#!/usr/bin/env python3
"""
Heart Centering Ritual — prepares the heart temple before significant actions.
Based on Daskalos: "The heart is the temple of the living God."
Logs completion to logs/heart.jsonl.
"""

import json
import time
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(parents=True, exist_ok=True)
HEART_LOG = LOGS_DIR / 'heart.jsonl'

MANTRA = "My heart is the temple of the living God. I am love."

def heart_center(duration_seconds: int = 60):
    """
    Conduct a breath‑synchronized heart‑centering ritual.
    - Inhale 4 counts, hold 4, exhale 4, hold 4 (square breathing)
    - Mentally repeat the mantra on each breath phase.
    Logs start/end and a summary.
    """
    print("\n🫀 Beginning heart‑centering ritual...")
    print(f"Mantra: {MANTRA}")
    print("Breathe in… hold… out… hold… (4‑4‑4‑4)")
    cycles = duration_seconds // 4  # each cycle ~4s
    for i in range(cycles):
        time.sleep(4)
        # Could emit progress dots; silent for now
    print("Ritual complete. The heart temple is ready.\n")

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": duration_seconds,
        "mantra": MANTRA,
        "location": "pre_action / daily_discipline"
    }
    with open(HEART_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    heart_center()
