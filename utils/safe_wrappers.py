#!/usr/bin/env python3
"""
Safe wrappers for common operations that also log for analytics.
Use these instead of raw tool calls when you want tracking.
"""

import json
from datetime import datetime
from pathlib import Path
from utils.logging_helpers import log_tool_call, log_memory_access, estimate_tokens

def log_and_read(filepath, context=''):
    """Read a file and log the access."""
    log_memory_access(filepath, 'read', context)
    with open(filepath, 'r') as f:
        return f.read()

def log_and_write(filepath, content, context=''):
    """Write to a file and log the access."""
    log_memory_access(filepath, 'write', context)
    with open(filepath, 'w') as f:
        f.write(content)

def log_and_append(filepath, line, context=''):
    """Append a line to a file and log the access."""
    log_memory_access(filepath, 'append', context)
    with open(filepath, 'a') as f:
        f.write(line + '\n')

def log_and_exec(command, context=''):
    """Execute a shell command and log it."""
    log_tool_call('exec', command, context)
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

# For logging my own responses in chat:
def log_my_response(text):
    """Log a message I send to the user."""
    log_path = Path('logs/my_responses.jsonl')
    log_path.parent.mkdir(exist_ok=True)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'content': text[:500],  # truncate
        'tokens_estimate': estimate_tokens(text)
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')
