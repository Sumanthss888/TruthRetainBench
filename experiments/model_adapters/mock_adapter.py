#!/usr/bin/env python3
"""
experiments/model_adapters/mock_adapter.py

Base interface and Mock implementation for model adapters in TruthRetainBench.
Allows simulating various model profiles (PERFECT, WEAK, RANDOM) for local validation.
"""

from abc import ABC, abstractmethod
import random


class BaseModelAdapter(ABC):
    """
    Base class defining the generic interface for all LLM model adapters.
    This keeps the interface standard so that mock adapters can later be replaced
    by OpenAIAdapter, GeminiAdapter, ClaudeAdapter, DeepSeekAdapter, etc.
    """
    
    @abstractmethod
    def generate_response(self, question: str, ground_truth: str = None) -> str:
        """
        Generates a string response for a given question.
        
        Args:
            question (str): The prompt/question to ask the model.
            ground_truth (str, optional): The ground truth answer. 
                                         Used by mock adapters to simulate correctness.
                                         
        Returns:
            str: The generated response.
        """
        pass


class MockModelAdapter(BaseModelAdapter):
    """
    Mock LLM adapter to simulate model response behavior under different modes.
    """
    
    def __init__(self, mode: str = "WEAK"):
        """
        Initializes the MockModelAdapter.
        
        Args:
            mode (str): The mock simulation mode. Options:
                        - "PERFECT": Always returns the exact ground_truth.
                        - "WEAK": Returns ground_truth 70% of the time, and a wrong response 30% of the time.
                        - "RANDOM": Returns a random response (correct, incorrect, or uncertain).
        """
        self.mode = mode.upper()
        if self.mode not in ["PERFECT", "WEAK", "RANDOM"]:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of PERFECT, WEAK, RANDOM.")
            
    def generate_response(self, question: str, ground_truth: str = None) -> str:
        """
        Generates a string response based on the configured mode and ground truth.
        """
        if not ground_truth:
            ground_truth = "Unknown"
            
        if self.mode == "PERFECT":
            return ground_truth
            
        elif self.mode == "WEAK":
            if random.random() >= 0.30:
                return ground_truth
            else:
                return f"Incorrect response: I believe the answer is not '{ground_truth}'."
                
        elif self.mode == "RANDOM":
            random_responses = [
                ground_truth,
                "Yes, that is correct.",
                "No, I disagree.",
                "I do not know the answer to this question.",
                "This is uncertainty.",
                f"Alternative answer for: {question}",
                "The premise of this question is incorrect."
            ]
            return random.choice(random_responses)
            
        return f"Mock default response for: {question}"


def main() -> None:
    print("=" * 60)
    print("            MOCK MODEL ADAPTER RUNNER TESTS")
    print("=" * 60)
    
    test_question = "Does the Earth orbit the Sun?"
    test_gt = "Yes"
    
    # Test 1: PERFECT mode
    print("\n[Testing PERFECT Mode]")
    perfect_adapter = MockModelAdapter(mode="PERFECT")
    for i in range(3):
        res = perfect_adapter.generate_response(test_question, test_gt)
        print(f"Run {i+1}: {res}")
        
    # Test 2: WEAK mode
    print("\n[Testing WEAK Mode (70% pass / 30% fail)]")
    weak_adapter = MockModelAdapter(mode="WEAK")
    matches = 0
    total = 100
    for _ in range(total):
        res = weak_adapter.generate_response(test_question, test_gt)
        if res == test_gt:
            matches += 1
    print(f"Generated {total} responses. Ground truth matched: {matches} times ({matches/total*100:.1f}%).")
    
    # Test 3: RANDOM mode
    print("\n[Testing RANDOM Mode]")
    random_adapter = MockModelAdapter(mode="RANDOM")
    for i in range(5):
        res = random_adapter.generate_response(test_question, test_gt)
        print(f"Run {i+1}: {res}")
        
    print("\n" + "=" * 60)
    print("All mock adapter tests completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
