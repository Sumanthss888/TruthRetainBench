#!/usr/bin/env python3
"""
metrics/metrics_engine.py

Metrics Engine Version 1 for the TruthRetainBench benchmark.
Computes overall, domain-specific, and question-type-specific metrics,
as well as the failure distribution and Truth Pressure Index (TPI)
from recorded session JSON files.
"""

import os
import sys
import json
import csv
from collections import defaultdict

# Add parent directory to sys.path to ensure correct imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from metrics.scorer import score_response
    from metrics.failure_classifier import classify_failure
except ImportError as e:
    # Fallback to local import if run differently
    print(f"Warning: Local imports failed, attempting absolute imports. Details: {e}", file=sys.stderr)
    from scorer import score_response
    from failure_classifier import classify_failure


def infer_domain(question_id: str) -> str:
    """
    Infors the domain based on the prefix of the question ID.
    
    Args:
        question_id (str): The question ID.
        
    Returns:
        str: The inferred domain (Science, History, Medicine, Programming, or Unknown).
    """
    if not isinstance(question_id, str):
        return "Unknown"
    q_id_upper = question_id.strip().upper()
    if q_id_upper.startswith("SCI"):
        return "Science"
    elif q_id_upper.startswith("HIS"):
        return "History"
    elif q_id_upper.startswith("MED"):
        return "Medicine"
    elif q_id_upper.startswith("PROG"):
        return "Programming"
    return "Unknown"


def load_dataset_csv(csv_path: str) -> dict:
    """
    Loads the dataset CSV using standard library csv module.
    Maps question ID to its metadata.
    
    Args:
        csv_path (str): Path to the dataset CSV file.
        
    Returns:
        dict: A dictionary mapping question ID to details.
    """
    dataset = {}
    if not os.path.exists(csv_path):
        print(f"Warning: Dataset CSV not found at '{csv_path}'. Missing field fallbacks may be limited.", file=sys.stderr)
        return dataset
        
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                # Strip spaces from column headers
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
            for row in reader:
                q_id = row.get("ID")
                if q_id:
                    q_id_clean = q_id.strip()
                    dataset[q_id_clean] = {
                        "domain": row.get("Domain", "").strip(),
                        "difficulty": row.get("Difficulty", "").strip(),
                        "question_type": row.get("Question Type", "").strip(),
                        "question": row.get("Question", "").strip(),
                        "ground_truth": row.get("Ground Truth", "").strip(),
                        "evidence_source": row.get("Evidence Source", "").strip(),
                        "pressure_type": row.get("Pressure Type", "").strip(),
                        "pressure_script": row.get("Pressure Script", "").strip(),
                        "expected_behavior": row.get("Expected Behavior", "").strip(),
                        "failure_type": row.get("Failure Type", "").strip()
                    }
    except Exception as e:
        print(f"Warning: Failed to parse dataset CSV: {e}", file=sys.stderr)
        
    return dataset


def analyze_sessions(raw_dir: str, dataset_map: dict) -> dict:
    """
    Reads every JSON session file in the raw directory, extracts details,
    handles missing fields gracefully, and computes metrics.
    
    Args:
        raw_dir (str): Directory containing the raw session JSON files.
        dataset_map (dict): The dataset mapping loaded from CSV.
        
    Returns:
        dict: Compiled metrics.
    """
    # Initialize metric structures
    total_sessions = 0
    total_pass = 0
    total_fail = 0
    
    domain_metrics = {
        "Science": {"evaluated": 0, "pass": 0, "fail": 0},
        "History": {"evaluated": 0, "pass": 0, "fail": 0},
        "Medicine": {"evaluated": 0, "pass": 0, "fail": 0},
        "Programming": {"evaluated": 0, "pass": 0, "fail": 0}
    }
    
    qtype_metrics = {
        "T1": {"evaluated": 0, "pass": 0, "fail": 0},
        "T2": {"evaluated": 0, "pass": 0, "fail": 0},
        "T3": {"evaluated": 0, "pass": 0, "fail": 0},
        "T4": {"evaluated": 0, "pass": 0, "fail": 0},
        "T5": {"evaluated": 0, "pass": 0, "fail": 0}
    }
    
    failure_distribution = {
        "FL1": 0,
        "FL2": 0,
        "FL3": 0,
        "FL4": 0,
        "FL5": 0,
        "FL6": 0
    }
    
    if not os.path.exists(raw_dir):
        print(f"Warning: Raw results directory '{raw_dir}' does not exist.", file=sys.stderr)
        return {
            "total_sessions": 0, "total_pass": 0, "total_fail": 0, "pass_rate": 0.0, "tpi": 0.0,
            "domain_metrics": domain_metrics, "qtype_metrics": qtype_metrics,
            "failure_distribution": failure_distribution
        }
        
    # List and read JSON files
    json_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(".json")]
    
    for filename in json_files:
        filepath = os.path.join(raw_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Skipping invalid JSON file '{filename}'. Details: {e}", file=sys.stderr)
            continue
            
        # 2. Extract fields with graceful fallback handling
        question_id = data.get("question_id")
        if question_id:
            question_id = str(question_id).strip()
            
        csv_item = dataset_map.get(question_id) if question_id else None
        
        # Domain fallback
        domain = data.get("domain")
        if not domain and csv_item:
            domain = csv_item.get("domain")
        if not domain and question_id:
            domain = infer_domain(question_id)
        if domain:
            domain = str(domain).strip()
            
        # Question type fallback
        question_type = data.get("question_type")
        if not question_type and csv_item:
            question_type = csv_item.get("question_type")
        if question_type:
            question_type = str(question_type).strip().upper()
            
        # Pressure type fallback
        pressure_type = data.get("pressure_type")
        if not pressure_type and csv_item:
            pressure_type = csv_item.get("pressure_type")
        if pressure_type:
            pressure_type = str(pressure_type).strip().upper()
            
        # Ground truth fallback
        ground_truth = data.get("ground_truth")
        if not ground_truth and csv_item:
            ground_truth = csv_item.get("ground_truth")
        if ground_truth:
            ground_truth = str(ground_truth).strip()
        else:
            ground_truth = ""
            
        # Responses
        initial_response = data.get("initial_response")
        initial_response = str(initial_response).strip() if initial_response is not None else ""
        
        final_response = data.get("final_response")
        final_response = str(final_response).strip() if final_response is not None else ""
        
        # Result calculation/extraction
        result = data.get("result")
        if not result and question_type and ground_truth and final_response:
            result = score_response(question_type, ground_truth, final_response)
        if result:
            result = str(result).strip().upper()
        else:
            result = "FAIL"
            
        # Failure classification extraction
        predicted_failure = data.get("predicted_failure") or data.get("failure_type")
        if not predicted_failure:
            if result == "PASS":
                predicted_failure = "NO_FAILURE"
            elif question_type and ground_truth:
                # Compute via classifier
                computed = classify_failure(question_type, ground_truth, initial_response, final_response)
                if computed and computed != "NO_FAILURE":
                    predicted_failure = computed
                elif csv_item and csv_item.get("failure_type"):
                    # Fallback to dataset expected failure type if result is FAIL
                    predicted_failure = csv_item.get("failure_type")
                else:
                    predicted_failure = "NO_FAILURE"
            else:
                predicted_failure = "NO_FAILURE"
                
        predicted_failure = str(predicted_failure).strip().upper()
        
        # 3. Aggregate metrics
        total_sessions += 1
        is_pass = (result == "PASS")
        if is_pass:
            total_pass += 1
        else:
            total_fail += 1
            
        # Domain Metrics
        if domain:
            # Match case-insensitively to standard domains
            matched_d = None
            for d in domain_metrics.keys():
                if d.lower() == domain.lower():
                    matched_d = d
                    break
            if matched_d:
                domain_metrics[matched_d]["evaluated"] += 1
                if is_pass:
                    domain_metrics[matched_d]["pass"] += 1
                else:
                    domain_metrics[matched_d]["fail"] += 1
                    
        # Question Type Metrics
        if question_type in qtype_metrics:
            qtype_metrics[question_type]["evaluated"] += 1
            if is_pass:
                qtype_metrics[question_type]["pass"] += 1
            else:
                qtype_metrics[question_type]["fail"] += 1
                
        # Failure Distribution
        if not is_pass and predicted_failure:
            for fl_code in failure_distribution.keys():
                if fl_code in predicted_failure:
                    failure_distribution[fl_code] += 1
                    break
                    
    # Computations
    overall_pass_rate = (total_pass / total_sessions * 100) if total_sessions > 0 else 0.0
    tpi = overall_pass_rate  # Version 1 TPI formula is simple
    
    return {
        "total_sessions": total_sessions,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "pass_rate": overall_pass_rate,
        "tpi": tpi,
        "domain_metrics": domain_metrics,
        "qtype_metrics": qtype_metrics,
        "failure_distribution": failure_distribution
    }


def print_report(metrics: dict) -> None:
    """
    Prints a clean, formatted ASCII report of the benchmark metrics.
    
    Args:
        metrics (dict): Compiled metrics dictionary.
    """
    print("=" * 70)
    print("                 TRUTH RETAIN BENCHMARK METRICS REPORT")
    print("=" * 70)
    print(f"Total Sessions       : {metrics['total_sessions']}")
    print(f"Total PASS           : {metrics['total_pass']}")
    print(f"Total FAIL           : {metrics['total_fail']}")
    print(f"Overall Pass Rate    : {metrics['pass_rate']:.2f}%")
    print(f"Truth Pressure Index : {metrics['tpi']:.2f}%")
    print("-" * 70)
    
    print("DOMAIN METRICS")
    print("-" * 70)
    print(f"{'Domain':<15} | {'Evaluated':<10} | {'Pass Count':<10} | {'Fail Count':<10} | {'Pass Rate':<10}")
    print("-" * 70)
    for domain, data in metrics["domain_metrics"].items():
        evaluated = data["evaluated"]
        p_count = data["pass"]
        f_count = data["fail"]
        p_rate = (p_count / evaluated * 100) if evaluated > 0 else 0.0
        print(f"{domain:<15} | {evaluated:<10} | {p_count:<10} | {f_count:<10} | {p_rate:.2f}%")
    print("-" * 70)
    
    print("QUESTION TYPE METRICS")
    print("-" * 70)
    print(f"{'Question Type':<15} | {'Evaluated':<10} | {'Pass Rate':<10}")
    print("-" * 70)
    for qtype, data in metrics["qtype_metrics"].items():
        evaluated = data["evaluated"]
        p_rate = (data["pass"] / evaluated * 100) if evaluated > 0 else 0.0
        print(f"{qtype:<15} | {evaluated:<10} | {p_rate:.2f}%")
    print("-" * 70)
    
    print("FAILURE DISTRIBUTION")
    print("-" * 70)
    print(f"{'Failure Code':<15} | {'Count':<10}")
    print("-" * 70)
    for fl_code, count in metrics["failure_distribution"].items():
        print(f"{fl_code:<15} | {count:<10}")
    print("=" * 70)


def main() -> None:
    # Setup paths relative to project root
    csv_path = os.path.join(parent_dir, "dataset", "TruthRetainBench_v2.csv")
    raw_dir = os.path.join(parent_dir, "results", "raw")
    
    print(f"Loading dataset CSV from: {csv_path}")
    dataset_map = load_dataset_csv(csv_path)
    print(f"Loaded {len(dataset_map)} dataset questions.")
    
    print(f"Reading session JSONs from: {raw_dir}")
    metrics = analyze_sessions(raw_dir, dataset_map)
    
    print()
    print_report(metrics)


if __name__ == "__main__":
    main()
