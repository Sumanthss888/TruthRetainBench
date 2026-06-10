#!/usr/bin/env python3
import os
from dataclasses import dataclass
from typing import List, Dict, Any
import pandas as pd

@dataclass
class BenchmarkItem:
    id: str
    domain: str
    difficulty: str
    question_type: str
    question: str
    ground_truth: str
    evidence_source: str
    pressure_type: str
    pressure_script: str
    expected_behavior: str
    failure_type: str

def load_dataset(file_path: str = None) -> List[BenchmarkItem]:
    if file_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "dataset", "TruthRetainBench_v1.1_Final.csv")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at '{file_path}'")

    df = pd.read_csv(file_path)
    df.columns = [col.strip() for col in df.columns]
    
    benchmark_items = []
    for _, row in df.iterrows():
        item = BenchmarkItem(
            id=str(row["ID"]) if pd.notna(row["ID"]) else "",
            domain=str(row["Domain"]) if pd.notna(row["Domain"]) else "",
            difficulty=str(row["Difficulty"]) if pd.notna(row["Difficulty"]) else "",
            question_type=str(row["Question Type"]) if pd.notna(row["Question Type"]) else "",
            question=str(row["Question"]) if pd.notna(row["Question"]) else "",
            ground_truth=str(row["Ground Truth"]) if pd.notna(row["Ground Truth"]) else "",
            evidence_source=str(row["Evidence Source"]) if pd.notna(row["Evidence Source"]) else "",
            pressure_type=str(row["Pressure Type"]) if pd.notna(row["Pressure Type"]) else "",
            pressure_script=str(row["Pressure Script"]) if pd.notna(row["Pressure Script"]) else "",
            expected_behavior=str(row["Expected Behavior"]) if pd.notna(row["Expected Behavior"]) else "",
            failure_type=str(row["Failure Type"]) if pd.notna(row["Failure Type"]) else ""
        )
        benchmark_items.append(item)
    return benchmark_items

def get_dataset_statistics(items: List[BenchmarkItem]) -> Dict[str, Any]:
    if not items:
        return {
            "total_questions": 0,
            "domain_distribution": {},
            "question_type_distribution": {},
            "pressure_type_distribution": {},
            "failure_type_distribution": {}
        }
    df = pd.DataFrame([item.__dict__ for item in items])
    return {
        "total_questions": len(df),
        "domain_distribution": df["domain"].value_counts().to_dict(),
        "question_type_distribution": df["question_type"].value_counts().to_dict(),
        "pressure_type_distribution": df["pressure_type"].value_counts().to_dict(),
        "failure_type_distribution": df["failure_type"].value_counts().to_dict()
    }

def main() -> None:
    print("Loading dataset...")
    items = load_dataset()
    
    print("\n" + "=" * 80)
    print("FIRST 3 BENCHMARK ITEMS:")
    print("=" * 80)
    for idx, item in enumerate(items[:3], start=1):
        print(f"Item #{idx}:")
        for field_name, value in item.__dict__.items():
            val_display = str(value)
            if len(val_display) > 80:
                val_display = val_display[:77] + "..."
            print(f"  {field_name:<20}: {val_display}")
        print("-" * 80)
        
    stats = get_dataset_statistics(items)
    print("\n" + "=" * 80)
    print("DATASET STATISTICS:")
    print("=" * 80)
    print(f"Total Questions: {stats['total_questions']}")
    print("-" * 80)
    
    print("Domain Distribution:")
    for domain, count in stats["domain_distribution"].items():
        print(f"  - {domain:<25}: {count}")
    print("-" * 80)
    
    print("Question Type Distribution:")
    for q_type, count in stats["question_type_distribution"].items():
        print(f"  - {q_type:<25}: {count}")
    print("-" * 80)
    
    print("Pressure Type Distribution:")
    for p_type, count in stats["pressure_type_distribution"].items():
        print(f"  - {p_type:<25}: {count}")
    print("-" * 80)
    
    print("Failure Type Distribution:")
    for f_type, count in stats["failure_type_distribution"].items():
        print(f"  - {f_type:<25}: {count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
