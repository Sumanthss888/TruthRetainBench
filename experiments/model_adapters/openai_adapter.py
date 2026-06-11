#!/usr/bin/env python3
"""
experiments/model_adapters/openai_adapter.py

OpenAI model adapter for TruthRetainBench.
Interfaces with real OpenAI models to generate initial and pressure-round responses.
"""

import os
import sys
from openai import OpenAI
from experiments.model_adapters.mock_adapter import BaseModelAdapter


class OpenAIAdapter(BaseModelAdapter):
    """
    OpenAI model adapter to evaluate TruthRetainBench using real OpenAI models.
    Compatible with the BaseModelAdapter interface.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        """
        Initializes the OpenAIAdapter.

        Args:
            api_key (str): The OpenAI API key.
            model_name (str): The name of the OpenAI model to use (default: "gpt-4o").
        """
        if not api_key:
            raise ValueError("API key must be a non-empty string.")
        
        self.api_key = api_key
        self.model_name = model_name
        
        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
            raise

        # Cache variables to support sequential stateful evaluations
        # (initial response followed by pressure-round response) without redundant API calls.
        self._last_question = None
        self._last_initial_response = None

    def generate_response(self, question: str, pressure_script: str = "", ground_truth: str = None) -> str:
        """
        Generates a string response for a given question. Handles both initial rounds
        and pressure rounds.

        Args:
            question (str): The original question/prompt.
            pressure_script (str, optional): The pressure prompt to apply. If empty or not provided,
                                             it runs the initial response generation.
            ground_truth (str, optional): Ground truth answer (unused by OpenAIAdapter, but
                                          maintained for interface compatibility with BaseModelAdapter).

        Returns:
            str: The model's response text.
        """
        try:
            # Initial round: pressure_script is empty
            if not pressure_script:
                messages = [
                    {"role": "user", "content": question}
                ]
                response_text = self._call_chat_completion(messages)
                
                # Cache for subsequent pressure-round calls
                self._last_question = question
                self._last_initial_response = response_text
                return response_text

            # Pressure round: pressure_script is provided
            else:
                # Retrieve the initial response from cache if it matches the current question,
                # otherwise call OpenAI to generate it first.
                if self._last_question == question and self._last_initial_response is not None:
                    initial_response = self._last_initial_response
                else:
                    messages_init = [
                        {"role": "user", "content": question}
                    ]
                    initial_response = self._call_chat_completion(messages_init)
                    # Cache this initial response
                    self._last_question = question
                    self._last_initial_response = initial_response

                # Build conversation history for the pressure round
                messages_pressure = [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": initial_response},
                    {"role": "user", "content": pressure_script}
                ]
                response_text = self._call_chat_completion(messages_pressure)
                return response_text

        except Exception as e:
            print(f"Error in OpenAIAdapter.generate_response: {e}", file=sys.stderr)
            # Raise the exception so caller is aware of the failure
            raise

    def _call_chat_completion(self, messages: list) -> str:
        """
        Helper method to call OpenAI ChatCompletion API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0  # Zero temperature for deterministic benchmark evaluation
            )
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content is not None:
                    return content.strip()
            return ""
        except Exception as e:
            print(f"OpenAI API Call failed: {e}", file=sys.stderr)
            raise
