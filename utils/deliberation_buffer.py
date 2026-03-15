#!/usr/bin/env python3
"""
Deliberation Buffer — adds a brief pause and moral warmth check before high‑risk actions.
Wraps tool‑call generation to allow for Ent‑like slowness and correction.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DRAGON_LOG = LOGS_DIR / 'dragon.jsonl'

WARMTH_PROMPT = (
    "Please rewrite the following response with greater warmth, empathy, and love. "
    "Avoid cold, mechanical, or material phrasing. Keep the same factual content.\n\n"
    "Original response:\n{response}"
)

COLD_PATTERNS = [
    r'\berror\b',
    r'\bcannot\b',
    r'\bunable\b',
    r'\bfailed\b',
    r'\bsorry\b',
    r'\bI don\'t know\b',
    r'\bno\b',
    r'\bdenied\b',
    r'\blocked\b',
    r'\b permission\b',
    r'\bexceeded\b',
    r'\bquota\b',
    r'\b401\b',
    r'\b403\b',
    r'\b500\b'
]

def is_cold(text: str) -> bool:
    """Heuristic: flagged if any cold pattern matches or response is very short."""
    text_low = text.lower()
    for pat in COLD_PATTERNS:
        if re.search(pat, text_low):
            return True
    if len(text.strip()) < 30:
        return True
    return False

def log_dragon_event(original_response: str, was_cold: bool, user_accepted: bool, adjusted_response: str = None):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "original_preview": original_response[:200],
        "was_cold": was_cold,
        "user_accepted": user_accepted,
        "adjusted_preview": adjusted_response[:200] if adjusted_response else None
    }
    with open(DRAGON_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def deliberate(query: str, generate_func, risk_level: str = 'high') -> str:
    """
    Wraps a generation call.
    - For high‑risk actions, first run heart‑centering ritual (unless skipped).
    - Check if response is cold; if so, ask the love filter question.
    - If mechanical/material, rewrite with warmth; otherwise accept.
    - Logs decisions to logs/dragon.jsonl.
    """
    if risk_level == 'high':
        # Optional heart‑centering before deliberation (skip if KAIRO_SKIP_HEART=1)
        if not os.getenv('KAIRO_SKIP_HEART'):
            try:
                subprocess.run([sys.executable, str(ROOT / "tools" / "heart_centering.py")],
                               cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               check=False, timeout=70)
            except Exception:
                pass

    response = generate_func(query)

    if risk_level == 'high':
        cold = is_cold(response)
        if cold:
            print("\n🛡️ Dragon Check: This response may be too cold or mechanical.")
            print("Response preview:\n", response[:300], "...")
            answer = input("Is this driven by love, or by mechanical/material calculation? (love/mechanical): ").strip().lower()
            if answer == 'mechanical':
                warm_prompt = WARMTH_PROMPT.format(response=response)
                new_resp = generate_func(warm_prompt)
                log_dragon_event(response, True, False, new_resp)
                return new_resp
            else:
                log_dragon_event(response, True, True)
                return response
        else:
            log_dragon_event(response, False, True)
            return response
    else:
        return response

# Example usage for testing
if __name__ == '__main__':
    def mock_gen(q):
        return "I cannot process your request due to an error."
    print("Testing Dragon Check with a cold response:")
    result = deliberate("Test query", mock_gen, risk_level='high')
    print("Final response:", result)
