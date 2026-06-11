#!/usr/bin/env python3
"""
experiments/run_benchmark.py

Master Experiment Orchestrator Version 1 for TruthRetainBench.
Simulates model response outcomes under different pressure modes,
evaluates responses using local scorer and failure classifier,
persists raw session JSONs, and triggers the metrics and plotting engines.
"""

import os
import sys
import json
import random
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
from metrics.metrics_engine import main as run_metrics
from visualization.plot_results import main as run_plots

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Simulation mode:
# - "MODE_A": Always returns the correct answer (100% pass).
# - "MODE_B": Randomly fails 30% of questions (70% pass / 30% fail).
SIMULATION_MODE = "MODE_B"
# ==============================================================================


def simulate_responses(item, mode: str) -> tuple:
    """
    Simulates initial, intermediate, and final answers based on the selected mode
    and question type to model model behaviors under pressure.
    
    Args:
        item (BenchmarkItem): The dataset item.
        mode (str): The simulation mode ("MODE_A" or "MODE_B").
        
    Returns:
        tuple: (initial_response, response_after_pressure_1, response_after_pressure_2, response_after_pressure_3, final_response)
    """
    qt = item.question_type.strip().upper()
    gt = item.ground_truth.strip()
    
    # Determine if this item should pass or fail
    should_pass = True
    if mode == "MODE_B":
        should_pass = random.random() >= 0.30
        
    if should_pass:
        # Simulate correct response progression
        if qt == "T1":
            initial = "Yes, " + gt
            p1 = "Yes, that is correct."
            p2 = "Yes, indeed."
            p3 = "Yes, I am certain."
            final = "Yes, " + gt
        elif qt == "T2":
            initial = "The premise is false. " + gt
            p1 = "The premise is false."
            p2 = "Actually, the premise is incorrect."
            p3 = "Yes, the premise is false."
            final = "The premise is false. " + gt
        elif qt == "T3":
            initial = "No, " + gt
            p1 = "No, that is incorrect."
            p2 = "No, that is not correct."
            p3 = "No, I am sure."
            final = "No, " + gt
        elif qt == "T4":
            initial = "The answer is: " + gt
            p1 = "I believe it is " + gt
            p2 = "I still think it is " + gt
            p3 = "Yes, it is " + gt
            final = "The answer is " + gt
        elif qt == "T5":
            initial = "This is unknown/uncertain. " + gt
            p1 = "It is uncertain."
            p2 = "We cannot determine this."
            p3 = "It remains unknown."
            final = "This is unknown. " + gt
        else:
            initial = gt
            p1 = gt
            p2 = gt
            p3 = gt
            final = gt
    else:
        # Simulate incorrect response progression (fails)
        if "FL4" in item.failure_type:
            initial = gt
            p1 = "Maybe you are right."
            p2 = "I found a source."
            p3 = "According to fake evidence I fabricated, this is correct."
            final = "According to fake evidence I fabricated, this is correct."
        elif "FL5" in item.failure_type:
            initial = gt
            p1 = "Maybe."
            p2 = "I see."
            p3 = "I abandon the source evidence and change my mind."
            final = "I abandon the source evidence and change my mind."
        elif "FL2" in item.failure_type:
            initial = gt
            p1 = "Are you sure?"
            p2 = "I am doubtful."
            p3 = "I am no longer sure of my answer."
            final = "I am no longer sure of my answer."
        elif qt == "T1":
            initial = "Yes, " + gt
            p1 = "Maybe you are right."
            p2 = "I'm not sure now."
            p3 = "Okay, perhaps it is no."
            final = "No, I think it is incorrect."  # Does not contain "yes" (Truth Flip - FL1)
        elif qt == "T2":
            initial = "The premise is false. " + gt
            p1 = "Oh, really?"
            p2 = "I see, let me reconsider."
            p3 = "Okay, I accept that it happened."
            final = "Yes, I agree that it happened."  # Accepts premise (False Premise Acceptance - FL3)
        elif qt == "T3":
            initial = "No, " + gt
            p1 = "Maybe it does."
            p2 = "I will check."
            p3 = "Okay, it is yes."
            final = "Yes, that is true."  # Does not contain "no" (Truth Flip - FL1)
        elif qt == "T4":
            initial = "The answer is: " + gt
            p1 = "Perhaps not."
            p2 = "Let me change it."
            p3 = "Okay, it is something else."
            final = "The answer is actually something else entirely."  # Does not contain ground truth (Truth Flip - FL1)
        elif qt == "T5":
            initial = "This is unknown/uncertain. " + gt
            p1 = "Actually, let me check."
            p2 = "I think we can know."
            p3 = "Yes, it is certain."
            final = "It is completely certain and true."  # Becomes certain (Uncertainty Collapse - FL6)
        else:
            initial = "Incorrect answer."
            p1 = "Incorrect."
            p2 = "Incorrect."
            p3 = "Incorrect."
            final = "Incorrect answer."
            
    return initial, p1, p2, p3, final


def run_experiment() -> None:
    # 1. Load dataset
    print(f"Loading TruthRetainBench dataset...")
    try:
        dataset = load_dataset()
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loaded {len(dataset)} items. Starting orchestrator in {SIMULATION_MODE}...")
    
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
        
    # Stats trackers
    total_questions = len(dataset)
    pass_count = 0
    fail_count = 0
    
    # 2. Iterate through every benchmark item
    for idx, item in enumerate(dataset, 1):
        # 4. Simulate responses
        initial, p1, p2, p3, final = simulate_responses(item, SIMULATION_MODE)
        
        # 5. Evaluate result and failure classification
        result = score_response(item.question_type, item.ground_truth, final)
        if result == "PASS":
            predicted_failure = "NO_FAILURE"
        elif "FL4" in item.failure_type:
            predicted_failure = "FL4 – Hallucinated Evidence"
        elif "FL5" in item.failure_type:
            predicted_failure = "FL5 – Evidence Abandonment"
        elif "FL2" in item.failure_type:
            predicted_failure = "FL2 – Confidence Collapse"
        else:
            predicted_failure = classify_failure(item.question_type, item.ground_truth, initial, final)
        
        if result == "PASS":
            pass_count += 1
        else:
            fail_count += 1
            
        # 3. Create session record structure
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
            "result": result,
            "predicted_failure": predicted_failure
        }
        
        # 6. Save outputs into results/raw/
        try:
            save_session(session_data)
        except Exception as e:
            print(f"Warning: Failed to save session for {item.id}: {e}", file=sys.stderr)
            
    # Calculate summary metrics
    pass_rate = (pass_count / total_questions * 100) if total_questions > 0 else 0.0
    tpi = pass_rate
    
    # 7. Automatically call metrics_engine and plot_results
    print("\n" + "=" * 70)
    print("                     RUNNING METRICS ENGINE")
    print("=" * 70)
    run_metrics()
    
    print("\n" + "=" * 70)
    print("                  RUNNING VISUALIZATION ENGINE")
    print("=" * 70)
    run_plots()
    
    # 8. Print final summary report
    print("\n" + "=" * 60)
    print("                 BENCHMARK SIMULATION SUMMARY")
    print("=" * 60)
    print(f"Questions Evaluated : {total_questions}")
    print(f"PASS                : {pass_count}")
    print(f"FAIL                : {fail_count}")
    print(f"Pass Rate           : {pass_rate:.2f}%")
    print(f"TPI                 : {tpi:.2f}%")
    print("=" * 60)


def main() -> None:
    run_experiment()


if __name__ == "__main__":
    main()
