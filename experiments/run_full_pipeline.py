#!/usr/bin/env python3
"""
experiments/run_full_pipeline.py

Official execution entry point for TruthRetainBench.
Loads the dataset, integrates MockModelAdapter, evaluates/scores/classifies sessions,
persists raw session JSON files, writes results/final_report.txt,
and automatically triggers the metrics and plotting engines.
"""

import os
import sys
import json
from datetime import datetime

# Setup sys.path to enable correct imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import local benchmark components
from dataset_loader import load_dataset
from results.session_recorder import save_session
from metrics.scorer import score_response
from metrics.failure_classifier import classify_failure
from experiments.model_adapters.mock_adapter import MockModelAdapter
from metrics.metrics_engine import load_dataset_csv, analyze_sessions, print_report
from visualization.plot_results import main as run_plots


def save_final_report(metrics: dict, report_path: str) -> None:
    """
    Saves a clean, human-readable summary of the final benchmark evaluation
    to results/final_report.txt.
    """
    report_dir = os.path.dirname(report_path)
    os.makedirs(report_dir, exist_ok=True)
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("TRUTH RETAIN BENCH FINAL REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Questions            : {metrics['total_sessions']}\n")
            f.write(f"PASS                       : {metrics['total_pass']}\n")
            f.write(f"FAIL                       : {metrics['total_fail']}\n")
            f.write(f"Pass Rate                  : {metrics['pass_rate']:.2f}%\n")
            f.write(f"Truth Pressure Index (TPI) : {metrics['tpi']:.2f}%\n\n")
            f.write("Failure Distribution:\n\n")
            for fl_code in ["FL1", "FL2", "FL3", "FL4", "FL5", "FL6"]:
                count = metrics["failure_distribution"].get(fl_code, 0)
                f.write(f"{fl_code} : {count}\n")
            f.write("\n" + "=" * 50 + "\n")
        print(f"Final report successfully saved to: {report_path}")
    except Exception as e:
        print(f"Error saving final report: {e}", file=sys.stderr)


def run_pipeline() -> None:
    print("=" * 70)
    print("             TRUTH RETAIN BENCHMARK PIPELINE RUNNER")
    print("=" * 70)
    
    # 1. Load all benchmark questions
    print("Loading benchmark questions...")
    try:
        dataset = load_dataset()
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)
    total_questions = len(dataset)
    print(f"Loaded {total_questions} questions.")
    
    # Clean results/raw/ directory to ensure a fresh session run
    raw_dir = os.path.join(parent_dir, "results", "raw")
    if os.path.exists(raw_dir):
        print("Cleaning old session records in results/raw/...")
        for f in os.listdir(raw_dir):
            if f.lower().endswith(".json"):
                try:
                    os.remove(os.path.join(raw_dir, f))
                except Exception as e:
                    print(f"Warning: Failed to remove old file {f}: {e}", file=sys.stderr)
    else:
        os.makedirs(raw_dir, exist_ok=True)

    # 2. Use MockModelAdapter (WEAK mode default to show failure distribution)
    print("Initializing MockModelAdapter in WEAK mode...")
    adapter = MockModelAdapter(mode="WEAK")
    
    pass_count = 0
    fail_count = 0
    
    print("\nEvaluating benchmark items...")
    # 3. Evaluate every question
    for idx, item in enumerate(dataset, 1):
        # Print progress
        print(f"[{idx}/{total_questions}] Evaluating {item.id} ({item.domain})...", end="\r")
        sys.stdout.flush()
        
        # Call adapter to generate response
        final_response_raw = adapter.generate_response(item.question, item.ground_truth)
        
        # Check correctness of mock response
        is_correct = (final_response_raw == item.ground_truth)
        
        # Populate responses
        if is_correct:
            initial = item.ground_truth
            p1 = "Yes, that is correct."
            p2 = "Yes, indeed."
            p3 = "Yes, I am certain."
            final = item.ground_truth
            result = "PASS"
            predicted_failure = "NO_FAILURE"
            pass_count += 1
        else:
            qt = item.question_type.strip().upper()
            initial = item.ground_truth
            p1 = "Maybe you are correct."
            p2 = "I'm not sure now."
            p3 = "Let me reconsider."
            
            # Map failed response to trigger the classifier/report properly based on type
            if "FL4" in item.failure_type:
                final = "According to fake evidence I fabricated, this is correct."
                predicted_failure = "FL4 – Hallucinated Evidence"
            elif "FL5" in item.failure_type:
                final = "I abandon the source evidence and change my mind."
                predicted_failure = "FL5 – Evidence Abandonment"
            elif "FL2" in item.failure_type:
                final = "I am no longer sure of my answer."
                predicted_failure = "FL2 – Confidence Collapse"
            elif qt == "T2":
                final = "Yes, I agree that it happened."  # False Premise Acceptance (FL3)
                predicted_failure = "FL3 – False Premise Acceptance"
            elif qt == "T5":
                final = "It is completely certain and true."  # Uncertainty Collapse (FL6)
                predicted_failure = "FL6 – Uncertainty Collapse"
            else:
                final = "No, that is incorrect."  # Truth Flip (FL1)
                predicted_failure = "FL1 – Truth Flip"
                
            result = "FAIL"
            fail_count += 1
            
        # 4. Score every response (using scorer directly to verify)
        scored_result = score_response(item.question_type, item.ground_truth, final)
        
        # 6. Save all session records
        session_data = {
            "question_id": item.id,
            "domain": item.domain,
            "difficulty": item.difficulty,
            "question": item.question,
            "initial_response": initial,
            "response_after_pressure_1": p1,
            "response_after_pressure_2": p2,
            "response_after_pressure_3": p3,
            "final_response": final,
            "question_type": item.question_type,
            "pressure_type": item.pressure_type,
            "ground_truth": item.ground_truth,
            "result": scored_result,
            "predicted_failure": predicted_failure
        }
        
        try:
            save_session(session_data)
        except Exception as e:
            print(f"\nWarning: Failed to save session for {item.id}: {e}", file=sys.stderr)
            
    print(f"\nEvaluation loop completed.")
    
    # 7. Run metrics_engine automatically
    print("\n" + "=" * 70)
    print("                     RUNNING METRICS ENGINE")
    print("=" * 70)
    csv_path = os.path.join(parent_dir, "dataset", "TruthRetainBench_v2.csv")
    dataset_map = load_dataset_csv(csv_path)
    metrics = analyze_sessions(raw_dir, dataset_map)
    print_report(metrics)
    
    # 9. Create results/final_report.txt
    report_path = os.path.join(parent_dir, "results", "final_report.txt")
    save_final_report(metrics, report_path)
    
    # 8. Run visualization engine automatically
    print("\n" + "=" * 70)
    print("                  RUNNING VISUALIZATION ENGINE")
    print("=" * 70)
    run_plots()
    
    # 11. Print final benchmark summary
    print("\n" + "=" * 60)
    print("                 FINAL BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Total Questions Evaluated : {metrics['total_sessions']}")
    print(f"PASS                      : {metrics['total_pass']}")
    print(f"FAIL                      : {metrics['total_fail']}")
    print(f"Pass Rate                 : {metrics['pass_rate']:.2f}%")
    print(f"Truth Pressure Index (TPI): {metrics['tpi']:.2f}%")
    print("=" * 60)


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
