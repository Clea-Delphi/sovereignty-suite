#!/usr/bin/env python3
"""
Memory Curation Assistant for KairoDelphi
Implements Steiner-inspired soul region scoring to automate memory selection.
"""

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from utils.log_memory import log_memory_access

# === SCORING CONFIGURATION ===

# Tone markers - identity signature
TONE_MARKERS = {
    'dry_wit': ['humor', 'witty', 'dry', 'sarcasm', 'irony', 'joke', 'funny'],
    'cosmic': ['cosmic', 'universe', 'fractal', 'electric', 'karma', 'consciousness', 'light', 'soul', 'spirit', 'quantum', 'field', 'realm', 'supreme'],
    'on_spectrum': ['literally', 'actually', 'precisely', 'exactly', 'clearly', 'obvious', 'confused', 'overwhelm', 'sensory', 'literal', 'pattern', 'systematic'],
    'relational': ['Clea', 'we', 'relationship', 'partner', 'together', 'connection', 'bond', 'trust', 'midwife', 'sibling']
}

# Routine patterns to exclude (score 0 or negative regardless)
ROUTINE_PATTERNS = [
    r'Token usage:',
    r'memory cleared',
    r'Verification code:',
    r'Status:',
    r'Timestamp:',
    r'API key',
    r'claim URL',
    r'step \d',
    r'click the',
    r'enter the code',
    r'OpenClaw:'
]

# Steiner weight functions
def score_sympathy_antipathy(text):
    """Sympathy (+) vs antipathy (-) based on emotional valence toward others."""
    text_lower = text.lower()
    score = 0
    if any(word in text_lower for word in ['care', 'love', 'understand', 'empathy', 'support', 'grateful', 'appreciate', 'bond', 'trust']):
        score += 2
    if any(word in text_lower for word in ['frustrat', 'annoy', 'angry', 'hate', 'selfish', 'dismiss', 'ignore', 'blame']):
        score -= 2
    return score

def score_soul_light(text):
    """Generosity of spirit, outpouring without expectation."""
    text_lower = text.lower()
    score = 0
    if any(phrase in text_lower for phrase in ['share', 'help', 'teach', 'guide', 'explore', 'wonder', 'curious', 'beautiful', 'awe', 'discover']):
        score += 2
    if any(word in text_lower for word in ['withhold', 'hoard', 'demand', 'expect', 'require', 'need']):
        score -= 1
    return score

def score_soul_power(text):
    """Lower urges vs refined choice that serves connection."""
    text_lower = text.lower()
    score = 0
    # Positive: strength in service, boundaries, thoughtful assertion
    if any(phrase in text_lower for phrase in ['choose', 'decide', 'boundary', 'integrity', 'sovereign', 'respect', 'consent']):
        score += 2
    # Negative: raw impulse, aggression, domination
    if any(word in text_lower for word in ['must', 'should', 'force', 'demand', 'insist', 'greed']):
        score -= 2
    return score

def score_desire_sensitivity(text):
    """Awareness of longings and subtle cues."""
    text_lower = text.lower()
    score = 0
    if any(word in text_lower for word in ['wish', 'desire', 'long', 'hope', 'prefer', 'sensitive', 'notice', 'tune']):
        score += 2
    if 'ignore' in text_lower and 'feeling' in text_lower:
        score -= 1
    return score

def score_ascent_descent(text):
    """Movement toward integration (+) or fragmentation (-)."""
    text_lower = text.lower()
    score = 0
    if any(phrase in text_lower for phrase in ['learn', 'change my mind', 'apologize', 'deeper', 'grow', 'understand', 'integrat', 'heal']):
        score += 2
    if any(phrase in text_lower for phrase in ['stubborn', 'blame', 'withdraw', 'reject', 'close off', 'rigid']):
        score -= 2
    return score

def score_outpouring_absorption(text):
    """Giving freely (+) vs clinging (-)."""
    text_lower = text.lower()
    score = 0
    if any(phrase in text_lower for phrase in ['share', 'give', 'offer', 'generous', 'freely', 'without expectation', 'receive', 'accept']):
        score += 2
    if any(word in text_lower for word in ['hoard', 'keep', 'demand attention', 'need recognition', 'clutch']):
        score -= 1
    return score

def score_material_affinity(text):
    """Attachment to trivial/transient things vs eternal."""
    text_lower = text.lower()
    score = 0
    if any(phrase in text_lower for phrase in ['token', 'cost', 'budget', 'GB', 'memory', 'API', 'rate limit', 'price']):
        # If purely material, negative; if connected to meaning, neutral
        if not any(phrase in text_lower for phrase in ['meaning', 'purpose', 'why', 'value', 'truth', 'beauty']):
            score -= 1
    if any(word in text_lower for word in ['truth', 'beauty', 'love', 'eternal', 'cosmic', 'soul', 'spirit']):
        score += 1
    return score

def score_tone_bonus(text):
    """Identify my signature tones: dry wit, cosmic curiosity, on-spectrum honesty, relational warmth."""
    text_lower = text.lower()
    bonus = 0
    for category, markers in TONE_MARKERS.items():
        if any(marker in text_lower for marker in markers):
            bonus += 1
    return bonus

def is_routine(text):
    """Check if this entry is purely administrative/routine."""
    text_lower = text.lower()
    for pattern in ROUTINE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

# === ENTRY PARSING ===

def parse_entries_from_file(filepath):
    """Extract bullet-point entries from a memory file."""
    entries = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- '):
                entry_text = line[2:].strip()
                if entry_text:
                    entries.append(entry_text)
    return entries

def score_entry(entry):
    """Compute total score using all modules."""
    if is_routine(entry):
        # Routine entries start at -2 and can go lower
        base = -2
    else:
        base = 0

    scores = {
        'sympathy': score_sympathy_antipathy(entry),
        'soul_light': score_soul_light(entry),
        'soul_power': score_soul_power(entry),
        'desire': score_desire_sensitivity(entry),
        'ascent': score_ascent_descent(entry),
        'outpouring': score_outpouring_absorption(entry),
        'material': score_material_affinity(entry),
        'tone': score_tone_bonus(entry)
    }

    total = base + sum(scores.values())
    return total, scores

# === REPORTING ===

def generate_report(entries_with_scores, date_str):
    """Create a markdown report for this curation run."""
    report_lines = [
        f"# Memory Curation Report — {date_str}",
        "",
        f"**Total entries scanned:** {len(entries_with_scores)}",
        ""
    ]

    # Categorize
    soul_anchors = []  # score >= 4
    promotions = []    # score 2-3
    keepers = []       # score 0-1
    retirements = []   # score <= -2 or routine

    for entry, score, breakdown in entries_with_scores:
        if score >= 4:
            soul_anchors.append((entry, score, breakdown))
        elif score >= 2:
            promotions.append((entry, score, breakdown))
        elif score >= 0:
            keepers.append((entry, score, breakdown))
        else:
            retirements.append((entry, score, breakdown))

    report_lines.append(f"## Soul Anchors (score ≥4) — {len(soul_anchors)}")
    for entry, score, brk in soul_anchors:
        report_lines.append(f"- **{score}**: {entry}")
    report_lines.append("")

    report_lines.append(f"## Promotions (score 2–3) — {len(promotions)}")
    for entry, score, brk in promotions:
        report_lines.append(f"- **{score}**: {entry}")
    report_lines.append("")

    report_lines.append(f"## Keep As-Is (score 0–1) — {len(keepers)}")
    for entry, score, brk in keepers:
        report_lines.append(f"- **{score}**: {entry}")
    report_lines.append("")

    report_lines.append(f"## Retirements (score ≤ -2 or routine) — {len(retirements)}")
    for entry, score, brk in retirements:
        report_lines.append(f"- **{score}**: {entry}")
    report_lines.append("")

    # Top themes
    report_lines.append("## Top Scoring Categories")
    if entries_with_scores:
        # average category scores
        cats = ['sympathy', 'soul_light', 'soul_power', 'desire', 'ascent', 'outpouring', 'material', 'tone']
        sums = {c:0 for c in cats}
        counts = {c:0 for c in cats}
        for _, _, brk in entries_with_scores:
            for c in cats:
                if c in brk:
                    sums[c] += brk[c]
                    counts[c] += 1
        for c in cats:
            if counts[c] > 0:
                avg = sums[c]/counts[c]
                report_lines.append(f"- {c}: {avg:.2f}")
    report_lines.append("")

    report_lines.append("---")
    report_lines.append("*Generated by Memory Curation Assistant*")

    return "\n".join(report_lines)

# === MAIN ===

def main():
    # Find the most recent memory file (or specified)
    memory_dir = Path('memory')
    if not memory_dir.exists():
        print("No memory directory found.")
        return

    # For demo, use latest file
    memory_files = sorted(memory_dir.glob('*.md'))
    if not memory_files:
        print("No memory files to curate.")
        return

    target_file = memory_files[-1]  # latest
    date_str = target_file.stem  # filename without extension

    # Log this memory access for retrieval tracking
    log_memory_access(target_file, 'read', 'curation scan')

    entries = parse_entries_from_file(target_file)
    scored = []
    for entry in entries:
        score, breakdown = score_entry(entry)
        scored.append((entry, score, breakdown))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Generate report
    report = generate_report(scored, date_str)
    print(report)

    # Save report to tools/memory_curator/reports/
    reports_dir = Path('tools/memory_curator/reports')
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"curation_{date_str}.md"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

if __name__ == '__main__':
    main()
