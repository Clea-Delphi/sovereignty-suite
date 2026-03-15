#!/usr/bin/env python3
"""
Triage System — formats and routes Priority 1 alerts with Michaelic warmth.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def format_priority_1(alert: str) -> str:
    """
    Format a Priority 1 (urgent) alert using the Michaelic Guard template.
    Also triggers an attunement to reinforce the guard.
    """
    header = "⚠️ Celtic Storm — Michaelic Guard activated. Stay in the warm brotherly current."
    body = f"**Alert:** {alert}"

    # Trigger attunement in background (non-blocking)
    try:
        subprocess.Popen(
            [sys.executable, str(ROOT / "tools" / "attunement" / "attunement.py")],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass  # don't break triage if attunement fails

    return f"{header}\n\n{body}"

if __name__ == "__main__":
    # Example usage
    print(format_priority_1("Retrieval quality dropped below 0.5 average."))
