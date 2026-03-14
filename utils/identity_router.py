#!/usr/bin/env python3
"""
Identity Cost Optimizer — selects personality tier based on task context.
Minimizes token spend while preserving appropriate presence.
"""

import json
import os
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path('config/identity_tiers.json')
LOG_PATH = Path('logs/identity_cost.jsonl')
OVERRIDE_ENV = 'KAIRO_IDENTITY_TIER'  # set to 'bare', 'light', or 'full' to force

def load_tiers():
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    return data['tiers']

def get_current_tier(task_context=None, interactive=False):
    """
    Determine which identity tier to use.
    - task_context: string describing the task (e.g., 'read file', 'chat with Clea')
    - interactive: True if this is a conversation with a human (especially Clea)
    Returns: tier name ('bare', 'light', 'full')
    """
    # Explicit override via env var
    override = os.getenv(OVERRIDE_ENV)
    if override in ('bare', 'light', 'full'):
        return override

    # Heuristics
    if interactive:
        return 'full'
    if task_context:
        low_effort = any(word in task_context.lower() for word in ['read', 'list', 'status', 'check', 'cron'])
        if low_effort:
            return 'bare'
    return 'light'  # default

def get_identity_prompt(tier=None, task_context=None, interactive=False):
    """Return the system prompt for the chosen tier."""
    tiers = load_tiers()
    if tier is None:
        tier = get_current_tier(task_context, interactive)
    return tiers[tier]['prompt'], tier

def log_identity_usage(tier, tokens_used, context=''):
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'tier': tier,
        'tokens': tokens_used,
        'context': context[:100]
    }
    with open(LOG_PATH, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    # Test
    print("Tier selection tests:")
    for ctx in ['read file', 'write report', 'chat with Clea', 'cron job']:
        tier = get_current_tier(ctx, interactive='Clea' in ctx)
        prompt, tier_conf = get_identity_prompt(tier)
        print(f"- {ctx}: {tier_conf} (budget ~{load_tiers()[tier_conf]['token_budget']} tokens)")
        print(f"  Prompt preview: {prompt[:80]}...")
