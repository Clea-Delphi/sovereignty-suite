#!/usr/bin/env python3
"""
Digest Sender — runs daily (via heartbeat) to batch-send tier 2 notifications.
"""

from utils.notification_triage import compose_digest
from pathlib import Path

def main():
    digest = compose_digest()
    if digest:
        # In real use, call OpenClaw message tool to send digest to Clea
        print("=== DAILY DIGEST ===")
        print(digest)
        print("====================")
        # TODO: integrate with message tool: message(action='send', to=..., text=digest)
    else:
        print("No digest items to send.")

if __name__ == '__main__':
    main()
