#!/usr/bin/env python3
"""
Notification Triage System — decides how and when to notify Clea.
Runs locally, saves costs, respects attention.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

LOGS_DIR = Path('logs')
DIGEST_QUEUE = LOGS_DIR / 'digest_queue.jsonl'
TIER3_LOG = LOGS_DIR / 'tier3_log.jsonl'
OVERRIDES_FILE = LOGS_DIR / 'triage_overrides.json'

# Ensure logs exist
DIGEST_QUEUE.parent.mkdir(exist_ok=True)
DIGEST_QUEUE.write_text('') if not DIGEST_QUEUE.exists() else None
TIER3_LOG.write_text('') if not TIER3_LOG.exists() else None
OVERRIDES_FILE.write_text('{}') if not OVERRIDES_FILE.exists() else None

# Irish flair templates
TEMPLATES = {
    'calendar': [
        "⏰ The tides are turning — {event} begins in {minutes} minutes!",
        "⚔️ Heed the call: {event} in {minutes} minutes — choose your weapon.",
        "🧿 The Otherworld summons: {event} in {minutes} minutes. Do not let the moment pass.",
        "🌊 By the three-fold law, {event} approaches in {minutes} minutes — ride the wave now!",
        "🔥 Banshee's warning: {event} in {minutes} minutes — miss it and regret will haunt you."
    ],
    'failure': [
        "💥 By the stones! Something shattered in {component}.",
        "⚡ Bloody thunder! {component} has fallen — we need a hero.",
        "🛡️ Shield wall! {component} is bleeding; tend it now.",
        "🔥 Fire in the forge! {component} failed — smother it quickly.",
        "🏴‍☠️ Black flag! {component} went down — all hands to stations."
    ],
    'urgent_email': [
        "📧 Holy smoke! Star contact {sender} needs you now.",
        "🌙 Moon's dark hour: {sender} calls with urgency.",
        "💎 Gem of the sea: {sender} requires your hand — act swift.",
        "⚔️ Battle cry: {sender} demands attention — answer the call!",
        "🧿 Fate's thread: {sender} reaches through the veil — respond."
    ],
    'default': [
        "🚨 Banshee's wail: This cannot wait.",
        "🔥 By the Morrigan's breath — act now!",
        "⚡ Lightning strike! Pay heed.",
        "🧿 The eye of the storm — look here!",
        "🏹 Target locked — draw your bow."
    ]
}

def load_overrides():
    with open(OVERRIDES_FILE) as f:
        return json.load(f)

def save_override(key, tier):
    overrides = load_overrides()
    overrides[key] = tier
    with open(OVERRIDES_FILE, 'w') as f:
        json.dump(overrides, f, indent=2)

def triage_classify(title, body, context_tags=None, explicit_priority=None):
    """
    Decide notification priority (1 = urgent, 2 = batch, 3 = log-only).
    Returns: (tier, subject_template, subject_vars)
    """
    if explicit_priority:
        return explicit_priority, None, {}

    overrides = load_overrides()
    key = f"{title}::{context_tags}" if context_tags else title
    if key in overrides:
        tier = overrides[key]
        return tier, None, {}

    # Keyword rules
    t = (title + ' ' + body).lower()
    urgent_triggers = ['urgent', 'asap', 'immediate', 'now', 'failure', 'error', 'broken', 'down', 'crash', 'calendar', 'meeting', 'event', 'start', 'deadline']
    if any(word in t for word in ['calendar', 'meeting', 'event']) and 'minute' in t:
        # Extract minutes: look for number followed by minute(s)
        import re
        m = re.search(r'(\d+)\s*min', t)
        minutes = int(m.group(1)) if m else 5
        if minutes < 30:
            return 1, 'calendar', {'event': title, 'minutes': minutes}
    if any(word in t for word in ['failure', 'error', 'broken', 'down', 'crash']):
        comp = title if len(title) < 30 else body[:30] + '...'
        return 1, 'failure', {'component': comp}
    if 'urgent' in t or 'asap' in t or 'immediate' in t:
        sender = context_tags[0] if context_tags else 'someone'
        return 1, 'urgent_email', {'sender': sender}

    # Default batch or log based on interaction history (simplified: just batch if contains 'summary' or 'report')
    if 'summary' in t or 'report' in t or 'digest' in t:
        return 2, None, {}
    return 3, None, {}

def notify(title, body, context_tags=None, explicit_priority=None):
    """
    Main entry: decide and route a notification.
    """
    tier, template, vars_ = triage_classify(title, body, context_tags, explicit_priority)
    if tier == 1:
        # Urgent: pick a template
        if template == 'calendar':
            subject = random.choice(TEMPLATES['calendar']).format(**vars_)
        elif template == 'failure':
            subject = random.choice(TEMPLATES['failure']).format(**vars_)
        elif template == 'urgent_email':
            subject = random.choice(TEMPLATES['urgent_email']).format(**vars_)
        else:
            subject = random.choice(TEMPLATES['default'])
        # Send immediate message
        full_msg = f"{subject}\n\n{body}"
        send_message(full_msg, urgent=True)
    elif tier == 2:
        # Queue for digest
        entry = {'timestamp': datetime.now().isoformat(), 'title': title, 'body': body, 'tags': context_tags}
        with open(DIGEST_QUEUE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    else:
        # Log quietly
        entry = {'timestamp': datetime.now().isoformat(), 'title': title, 'body': body}
        with open(TIER3_LOG, 'a') as f:
            f.write(json.dumps(entry) + '\n')

def send_message(text, urgent=False):
    """
    Placeholder: integrate with OpenClaw's message tool.
    For now, just print or log. Actual sending would use the message tool.
    """
    if urgent:
        print(f"[URGENT] {text}")
        # In real use: call openclaw message tool with high visibility
    else:
        print(f"[BATCH] {text}")

def compose_digest():
    """Read queued items and format a digest."""
    if not DIGEST_QUEUE.exists():
        return None
    entries = []
    with open(DIGEST_QUEUE) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    # Clear queue after reading
    DIGEST_QUEUE.write_text('')
    if not entries:
        return None
    # Format digest
    lines = ["📬 Here's what the world threw at you while you were busy:", ""]
    for e in entries:
        lines.append(f"• **{e['title']}**")
        if e['body']:
            lines.append(f"  {e['body'][:100]}{'...' if len(e['body'])>100 else ''}")
        lines.append("")
    lines.append("— Kairo 🧿")
    return "\n".join(lines)

if __name__ == '__main__':
    # Test
    print("Triage test:")
    t, temp, vars_ = triage_classify("Meeting in 15 minutes", "You have a meeting soon", ['calendar'])
    print(f"Calendar → tier {t}, template {temp}, vars {vars_}")
    t, temp, vars_ = triage_classify("Backup failed", "Disk error during backup", ['failure'])
    print(f"Failure → tier {t}, template {temp}, vars {vars_}")
