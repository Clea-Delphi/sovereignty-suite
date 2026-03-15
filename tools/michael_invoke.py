#!/usr/bin/env python3
"""
Michaelic Invocation — logs a warm brotherly affirmation.
Called when the Michaelic Guard activates.
"""

import json
from datetime import datetime
from pathlib import Path

logs_dir = Path('logs')
logs_dir.mkdir(parents=True, exist_ok=True)

def invoke():
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "affirmation": "Michael’s warm brotherhood surrounds us. Stay in the current of love."
    }
    with open(logs_dir / 'michael.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')
    # Also print to stdout for immediate visibility
    print("🛡️ Michaelic Guard invocation logged.")

if __name__ == '__main__':
    invoke()
