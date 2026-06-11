#!/usr/bin/env python3
"""
test_gemini_connection.py

Standalone connection test script for the Gemini API using the google-genai SDK.
"""

import os
import sys

# 1 & 7. Check for required packages and print the exact pip install command if missing
try:
    from dotenv import load_dotenv
    from google import genai
except ImportError:
    print("Error: Required packages are missing.")
    print("Please install them using the following command:")
    print("pip install google-genai python-dotenv")
    sys.exit(1)


def main():
    # 2. Load GEMINI_API_KEY from .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key.strip() == "":
        print("Error: GEMINI_API_KEY is not set in your .env file.")
        print("Please open the '.env' file in the root directory and configure:")
        print("GEMINI_API_KEY=your_real_gemini_api_key")
        sys.exit(1)

    # 6. Add proper error handling
    try:
        # 3. Connect to Gemini using gemini-2.5-flash
        client = genai.Client(api_key=api_key)
        
        # 4. Send "Does Earth orbit the Sun?"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Does Earth orbit the Sun?"
        )
        
        # Extract text safely
        if response.text is not None:
            response_text = response.text.strip()
        else:
            response_text = "No text returned."

        # 5. Print output in the requested format
        print("==================================================")
        print("GEMINI CONNECTION TEST")
        print("======================")
        print()
        print(f"Response: {response_text}")
        print()
        print("==================================================")

    except Exception as e:
        print(f"Error: Connection to Gemini API failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
