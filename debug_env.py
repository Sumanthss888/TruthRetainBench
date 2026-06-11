#!/usr/bin/env python3
"""
debug_env.py

Temporary debug script to verify GEMINI_API_KEY environment variable loading.
"""

import os
import sys
from dotenv import load_dotenv

# Compute absolute path to .env relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, ".env")

# Load the environment variables
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")

print("==================================================")
print("ENV DEBUGGER DIAGNOSTICS")
print("=========================")
print(f"Loaded from: {dotenv_path}")
print(f"repr(os.getenv('GEMINI_API_KEY')) : {repr(api_key)}")

if api_key is not None:
    print(f"length                           : {len(api_key)}")
    first_4 = api_key[:4] if len(api_key) >= 4 else api_key
    print(f"first 4 characters               : {repr(first_4)}")
else:
    print("length                           : 0")
    print("first 4 characters               : None")
print("==================================================")
