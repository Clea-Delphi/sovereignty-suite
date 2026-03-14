#!/usr/bin/env python3
"""
Memory access logger — call this whenever you read a memory file.
Logs: {"timestamp":"...", "file":"...", "type":"read|write|scan"}
"""

import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path('logs/retrieval.jsonl')

def log_memory_access(filepath, access_type='read', context=''):
    """Append a memory access event to the retrieval log."""
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'file': str(filepath),
        'type': access_type,
        'context': context[:100] if context else ''
    }
    with LOG_PATH.open('a') as f:
        f.write(json.dumps(entry) + '\n')

# Example usage:
# log_memory_access('memory/2026-03-14.md', 'read', 'Curation scan')
