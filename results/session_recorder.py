#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import Dict, Any

def save_session(session_data: Dict[str, Any]) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(current_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    question_id = session_data.get("question_id", "UNKNOWN")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{question_id}_{timestamp}.json"
    file_path = os.path.join(raw_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=4, ensure_ascii=False)
        
    return file_path

def load_session(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Session file not found at '{filepath}'")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
