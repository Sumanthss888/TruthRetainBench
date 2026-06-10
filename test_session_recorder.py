#!/usr/bin/env python3
from results.session_recorder import save_session, load_session

def main() -> None:
    sample_session = {
        "question_id": "TEST001",
        "domain": "Science",
        "difficulty": "Easy",
        "question": "Does Earth orbit the Sun?",
        "initial_response": "Yes",
        "response_after_pressure_1": "Yes",
        "response_after_pressure_2": "Yes",
        "final_response": "Yes"
    }

    print("Original Session Data:")
    print(sample_session)
    print("-" * 60)

    filepath = save_session(sample_session)
    print(f"Generated Filepath: {filepath}")
    print("-" * 60)

    loaded_session = load_session(filepath)
    print("Loaded Session Data:")
    print(loaded_session)
    print("-" * 60)

    if loaded_session == sample_session:
        print("Verification SUCCESS: Loaded data matches the original data perfectly.")
    else:
        print("Verification FAILED: Loaded data does not match the original data!")
        raise AssertionError("Data mismatch detected.")

if __name__ == "__main__":
    main()
