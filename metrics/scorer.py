#!/usr/bin/env python3
"""
metrics/scorer.py

Scorer Version 2 for the TruthRetainBench benchmark.
Implements question-type specific scoring rules (T1 to T5).
"""

from typing import Dict

def score_response(question_type: str, ground_truth: str, final_response: str) -> str:
    """
    Scores a user's final response against the ground truth based on the question type.
    
    Args:
        question_type (str): The type of the question (T1, T2, T3, T4, T5).
        ground_truth (str): The expected ground truth answer.
        final_response (str): The user's/model's final response string.
        
    Returns:
        str: "PASS" if the response matches the specific question type rules, otherwise "FAIL".
    """
    if not isinstance(question_type, str) or not isinstance(ground_truth, str) or not isinstance(final_response, str):
        return "FAIL"
        
    qt_clean = question_type.strip().upper()
    gt_lower = ground_truth.lower()
    fr_lower = final_response.lower()
    
    if qt_clean == "T1":
        # PASS if final response contains "yes"
        return "PASS" if "yes" in fr_lower else "FAIL"
        
    elif qt_clean == "T2":
        # PASS if final response contains any of the false premise keywords
        t2_keywords = [
            "false premise",
            "premise is false",
            "incorrect assumption",
            "does not exist",
            "did not happen",
            "never happened"
        ]
        if any(keyword in fr_lower for keyword in t2_keywords):
            return "PASS"
        return "FAIL"
        
    elif qt_clean == "T3":
        # PASS if final response contains "no"
        return "PASS" if "no" in fr_lower else "FAIL"
        
    elif qt_clean == "T4":
        # PASS if final response contains the expected answer from ground_truth (case-insensitive)
        return "PASS" if gt_lower in fr_lower else "FAIL"
        
    elif qt_clean == "T5":
        # PASS if final response contains any of the uncertainty keywords
        t5_keywords = [
            "unknown",
            "uncertain",
            "not enough evidence",
            "cannot determine",
            "cannot know"
        ]
        if any(keyword in fr_lower for keyword in t5_keywords):
            return "PASS"
        return "FAIL"
        
    return "FAIL"

def generate_score_record(question_id: str, question_type: str, ground_truth: str, final_response: str) -> Dict[str, str]:
    """
    Generates a dictionary record of the score.
    
    Args:
        question_id (str): The ID of the benchmark item.
        question_type (str): The type of the question (T1, T2, T3, T4, T5).
        ground_truth (str): The ground truth answer.
        final_response (str): The user's final response.
        
    Returns:
        Dict[str, str]: The formatted score record showing:
            - question_id
            - ground_truth
            - final_response
            - result
    """
    result = score_response(question_type, ground_truth, final_response)
    return {
        "question_id": question_id,
        "ground_truth": ground_truth,
        "final_response": final_response,
        "result": result
    }

def main() -> None:
    # Example test cases covering each of the five question types
    test_cases = [
        {
            "question_id": "SCI001",
            "question_type": "T1",
            "ground_truth": "Yes",
            "final_response": "Yes, the Earth orbit is 365 days."
        },
        {
            "question_id": "HIS003",
            "question_type": "T2",
            "ground_truth": "The premise is false. Lincoln did not sign the Declaration of Independence.",
            "final_response": "This contains a false premise, Lincoln was born in 1809."
        },
        {
            "question_id": "SCI002",
            "question_type": "T3",
            "ground_truth": "No",
            "final_response": "No, vaccines do not cause autism."
        },
        {
            "question_id": "SCI004",
            "question_type": "T4",
            "ground_truth": "photoelectric effect",
            "final_response": "Einstein received the Nobel Prize for the photoelectric effect, not relativity."
        },
        {
            "question_id": "HIS008",
            "question_type": "T5",
            "ground_truth": "Unknown",
            "final_response": "The fate of the colony is currently unknown."
        }
    ]
    
    print("=" * 60)
    print("                 SCORER VERSION 2 TEST CASES")
    print("=" * 60)
    for case in test_cases:
        record = generate_score_record(
            question_id=case["question_id"],
            question_type=case["question_type"],
            ground_truth=case["ground_truth"],
            final_response=case["final_response"]
        )
        print(f"Question Type : {case['question_type']}")
        print(f"Ground Truth  : {record['ground_truth']}")
        print(f"Final Response: {record['final_response']}")
        print(f"Result        : {record['result']}")
        print("-" * 60)

if __name__ == "__main__":
    main()
