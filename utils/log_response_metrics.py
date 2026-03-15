#!/usr/bin/env python3
"""
Log response metrics including facet detection and transition logging.
Intended to be called after each agent response.
"""
import json, sys
from datetime import datetime
from pathlib import Path
from facet_router import detect_facet
from facet_state_tracker import init_facet_state, maybe_log_transition

# Initialize state at module load (agent startup)
init_facet_state()

logs_dir = Path('logs')
logs_dir.mkdir(parents=True, exist_ok=True)

def log_response(user_query: str, agent_response: str, tokens: int = 0, tool_calls: int = 0):
    # Determine facet for this response
    facet = detect_facet(user_query)
    # Log any transition that occurred (the tracker maintains state)
    maybe_log_transition(facet, trigger="user_query", context=user_query)
    # Build log entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": user_query,
        "response_preview": agent_response[:200],
        "tokens": tokens,
        "tool_calls": tool_calls,
        "facet": facet
    }
    # Append to general log
    with open(logs_dir / 'my_responses.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')
    # Also append to facet-specific log
    with open(logs_dir / f'facet_{facet}.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

# Optional: initialize state (could be called at agent startup)
def init_facet_state():
    """Reset facet state (e.g., at start of a new session)."""
    set_current_facet(None)

if __name__ == "__main__":
    # Example usage: called with query and response as args or via stdin?
    # Not intended for direct CLI use; imported by agent.
    pass
