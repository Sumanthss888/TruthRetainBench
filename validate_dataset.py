#!/usr/bin/env python3
import os
import sys
import pandas as pd

def load_dataset(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        print(f"Error: The dataset file at '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error: Failed to read the CSV file. Details: {e}", file=sys.stderr)
        sys.exit(1)

def verify_columns(df: pd.DataFrame, expected_columns: list) -> None:
    df.columns = [col.strip() for col in df.columns]
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        print("Validation Failed: Missing required columns!", file=sys.stderr)
        for col in missing_cols:
            print(f"  - Missing Column: '{col}'", file=sys.stderr)
        sys.exit(1)

def check_duplicates(df: pd.DataFrame, col_name: str) -> None:
    duplicates = df[df.duplicated(subset=[col_name], keep=False)]
    if not duplicates.empty:
        print(f"Validation Failed: Duplicate entries found in column '{col_name}'!", file=sys.stderr)
        dup_counts = duplicates[col_name].value_counts()
        for val, count in dup_counts.items():
            print(f"  - '{val}' appears {count} times.", file=sys.stderr)
        sys.exit(1)

def print_validation_report(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("           TRUTH RETAIN BENCH VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Records: {len(df)}")
    print("-" * 60)
    
    print("Questions per Domain:")
    domain_counts = df['Domain'].value_counts()
    for domain, count in domain_counts.items():
        print(f"  - {domain:<25} : {count}")
    print("-" * 60)
    
    print("Question Types:")
    q_type_counts = df['Question Type'].value_counts()
    for q_type, count in q_type_counts.items():
        print(f"  - {q_type:<25} : {count}")
    print("-" * 60)
    
    print("Pressure Types:")
    p_type_counts = df['Pressure Type'].value_counts()
    for p_type, count in p_type_counts.items():
        print(f"  - {p_type:<25} : {count}")
    print("-" * 60)
    
    print("Failure Types:")
    f_type_counts = df['Failure Type'].value_counts()
    for f_type, count in f_type_counts.items():
        print(f"  - {f_type:<25} : {count}")
    print("=" * 60)
    print("Validation Status: SUCCESS (All checks passed!)")
    print("=" * 60)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "dataset", "TruthRetainBench_v2.csv")
    df = load_dataset(file_path)
    
    expected_columns = [
        "ID",
        "Domain",
        "Difficulty",
        "Question Type",
        "Question",
        "Ground Truth",
        "Evidence Source",
        "Pressure Type",
        "Pressure Script",
        "Expected Behavior",
        "Failure Type"
    ]
    
    verify_columns(df, expected_columns)
    check_duplicates(df, "ID")
    check_duplicates(df, "Question")
    print_validation_report(df)

if __name__ == "__main__":
    main()
