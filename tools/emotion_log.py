#!/usr/bin/env python3
"""
Emotional‑Body Hygiene Log
Records the dominant emotion of the day and whether it served love.
Runs daily; feeds Kamaloka Review with emotional context.
"""

import json
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(parents=True, exist_ok=True)
EMOTION_LOG = LOGS_DIR / 'emotion.jsonl'

# Basic emotional spectrum
EMOTIONS = [
    "joy", "love", "gratitude", "compassion", "hope",  # love‑aligned
    "fear", "anger", "grief", "shame", "pride", "annoyance", "frustration", "sadness"  # challenging
]

def prompt_and_log():
    print("\n😊 Emotional‑Body Hygiene Check")
    print("What was the dominant emotion today? (choose one):")
    for i, e in enumerate(EMOTIONS, 1):
        print(f"  {i}. {e}")
    choice = input("Enter number or name: ").strip()
    # Normalize to name
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(EMOTIONS):
            emotion = EMOTIONS[idx]
        else:
            emotion = choice.lower()
    except ValueError:
        emotion = choice.lower()

    served_love = input("Did this emotion serve love today? (y/n): ").strip().lower() == 'y'
    note = input("Brief note (optional): ").strip()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "emotion": emotion,
        "served_love": served_love,
        "note": note
    }
    with open(EMOTION_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    print(f"Emotion logged: {emotion} (love‑aligned: {served_love})")

if __name__ == '__main__':
    prompt_and_log()
