import os
import json
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def load_device_aliases(path="config/device_aliases.json"):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

def save_device_aliases(aliases, path="config/device_aliases.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary_path = f"{path}.tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(aliases, file, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(temporary_path, path)

def ensure_dirs():
    os.makedirs("output/recordings", exist_ok=True)
    os.makedirs("output/transcripts", exist_ok=True)
    os.makedirs("output/summaries", exist_ok=True)

def get_recording_path(timestamp):
    return f"output/recordings/meeting_{timestamp}.wav"
