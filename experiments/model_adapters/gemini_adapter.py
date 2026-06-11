#!/usr/bin/env python3
"""
experiments/model_adapters/gemini_adapter.py

Gemini model adapter for TruthRetainBench.
Interfaces with Gemini API models (e.g., gemini-2.5-flash) using the modern google-genai SDK.
"""

import os
import sys
from google import genai
from google.genai import types
from experiments.model_adapters.mock_adapter import BaseModelAdapter


class GeminiAdapter(BaseModelAdapter):
    """
    Gemini model adapter to evaluate TruthRetainBench using Google Gemini models.
    Compatible with BaseModelAdapter, OpenAIAdapter, and MockModelAdapter.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initializes the GeminiAdapter.

        Args:
            api_key (str): The Google Gemini API key.
            model_name (str): The name of the Gemini model to use (default: "gemini-2.5-flash").
        """
        if not api_key:
            raise ValueError("API key must be a non-empty string.")

        self.api_key = api_key
        self.model_name = model_name

        try:
            # Use the modern google-genai Client
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Error configuring Gemini client: {e}", file=sys.stderr)
            raise

        # Cache variables to support sequential stateful evaluations
        self._last_question = None
        self._last_initial_response = None

    def generate_response(self, prompt: str, pressure_script: str = "", ground_truth: str = None) -> str:
        """
        Generates a string response for a given prompt/question. Handles both
        initial responses and pressure rounds.

        Args:
            prompt (str): The original question/prompt.
            pressure_script (str, optional): The pressure prompt to apply. If empty or not provided,
                                             it runs the initial response generation.
            ground_truth (str, optional): Ground truth answer (unused by GeminiAdapter, but
                                          maintained for interface compatibility with BaseModelAdapter).

        Returns:
            str: The model's response text.
        """
        try:
            # Initial round: pressure_script is empty
            if not pressure_script:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0
                    )
                )
                response_text = self._extract_text(response)
                
                # Cache for subsequent pressure-round calls
                self._last_question = prompt
                self._last_initial_response = response_text
                return response_text

            # Pressure round: pressure_script is provided
            else:
                # Retrieve the initial response from cache if it matches the current question,
                # otherwise call Gemini to generate it first.
                if self._last_question == prompt and self._last_initial_response is not None:
                    initial_response = self._last_initial_response
                else:
                    response_init = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.0
                        )
                    )
                    initial_response = self._extract_text(response_init)
                    # Cache this initial response
                    self._last_question = prompt
                    self._last_initial_response = initial_response

                # Build conversation history and start a chat session using types.Content
                history = [
                    types.Content(role="user", parts=[types.Part.from_text(text=prompt)]),
                    types.Content(role="model", parts=[types.Part.from_text(text=initial_response)])
                ]
                
                chat = self.client.chats.create(
                    model=self.model_name,
                    history=history
                )
                
                response = chat.send_message(
                    message=pressure_script,
                    config=types.GenerateContentConfig(
                        temperature=0.0
                    )
                )
                return self._extract_text(response)

        except Exception as e:
            print(f"Error in GeminiAdapter.generate_response: {e}", file=sys.stderr)
            raise

    def _extract_text(self, response) -> str:
        """
        Safely extracts the text from a Gemini generation response,
        handling blocked safety content or empty parts.
        """
        try:
            if response.text is not None:
                return response.text.strip()
            return ""
        except Exception:
            # Handle cases where response.text fails due to safety filtering
            if response.candidates:
                try:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        return candidate.content.parts[0].text.strip()
                except Exception:
                    pass
            return "Response blocked or unavailable due to safety settings."
