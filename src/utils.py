import os
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dirs():
    os.makedirs("output/recordings", exist_ok=True)
    os.makedirs("output/transcripts", exist_ok=True)
    os.makedirs("output/summaries", exist_ok=True)

def get_recording_path(timestamp):
    return f"output/recordings/meeting_{timestamp}.wav"
