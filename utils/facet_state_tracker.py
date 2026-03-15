#!/usr/bin/env python3
"""
Facet State Tracker — maintains current facet and logs transitions.
Process‑local state; resets on agent restart. That's fine — we'll aggregate weekly.
"""

import json
from datetime import datetime
from pathlib import Path

logs_dir = Path('logs')
logs_dir.mkdir(parents=True, exist_ok=True)

# Global state (process‑local)
_current_facet = None

def init_facet_state():
    """Reset facet state (e.g., at start of a new agent run)."""
    set_current_facet(None)

def get_current_facet():
    """Return the currently active facet identifier (e.g., 'researcher')."""
    global _current_facet
    return _current_facet

def set_current_facet(facet: str):
    """Set the current facet (without logging)."""
    global _current_facet
    _current_facet = facet

def record_transition(from_facet: str, to_facet: str, trigger: str = "user_query", context: str = ""):
    """
    Log a facet transition to facet_transitions.jsonl.
    Args:
        from_facet: previous facet (or None if first)
        to_facet: new facet
        trigger: what caused the switch (e.g., 'user_query_keywords', 'response_content', 'explicit_command')
        context: short description of the user query or action
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "from_facet": from_facet,
        "to_facet": to_facet,
        "trigger": trigger,
        "context": context[:200] if context else ""
    }
    with open(logs_dir / 'facet_transitions.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

def maybe_log_transition(new_facet: str, trigger: str = "user_query", context: str = ""):
    """
    Compare new_facet with current; if different, log and update.
    Returns True if a transition was logged.
    """
    old = get_current_facet()
    if old != new_facet:
        record_transition(old, new_facet, trigger=trigger, context=context)
        set_current_facet(new_facet)
        return True
    return False
