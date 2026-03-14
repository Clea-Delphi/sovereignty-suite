#!/usr/bin/env python3
"""
Memory Curation Cycle — run apply then report.
"""

import subprocess
import sys

def run_script(path):
    print(f"\n=== Running {path} ===\n")
    result = subprocess.run([sys.executable, path], cwd='/home/node/.openclaw/workspace')
    if result.returncode != 0:
        print(f"Error running {path}")
        return False
    return True

def main():
    steps = [
        'tools/memory_curator/curator.py',
        'tools/memory_curator/mca_apply.py',
        'tools/memory_curator/mca_report.py'
    ]
    for step in steps:
        if not run_script(step):
            print(f"Cycle halted at {step}")
            return
    print("\n=== Cycle complete ===\n")

if __name__ == '__main__':
    main()
