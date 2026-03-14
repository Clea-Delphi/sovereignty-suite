#!/usr/bin/env python3
"""
Low-level logging functions. Used by wrappers and analysis scripts.
"""

import json
from datetime import datetime
from pathlib import Path

def _ensure_log(path: Path):
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        path.write_text('')  # create empty

def log_memory_access(filepath, access_type='read', context=''):
    """Append a memory access event to logs/retrieval.jsonl."""
    log_path = Path('logs/retrieval.jsonl')
    _ensure_log(log_path)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'file': str(filepath),
        'type': access_type,
        'context': context[:100] if context else ''
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def log_tool_call(tool, command, context=''):
    """Append a tool usage event to logs/tool_calls.jsonl."""
    log_path = Path('logs/tool_calls.jsonl')
    _ensure_log(log_path)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'tool': tool,
        'command': str(command)[:200],
        'context': context[:100] if context else ''
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def log_my_response(text, token_estimate=None):
    """Append a message I sent to logs/my_responses.jsonl."""
    log_path = Path('logs/my_responses.jsonl')
    _ensure_log(log_path)
    if token_estimate is None:
        from utils.token_counter import estimate_tokens
        token_estimate = estimate_tokens(text)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'content': text[:500],
        'tokens': token_estimate
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def log_behavior_daily(metrics: dict):
    """Append daily behavioral metrics to logs/behavior.jsonl."""
    log_path = Path('logs/behavior.jsonl')
    _ensure_log(log_path)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        **metrics
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + '\n')
