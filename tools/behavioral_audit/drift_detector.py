#!/usr/bin/env python3
"""
Behavioral Drift Detector for KairoDelphi
Analyzes raw memory entries to spot shifts in my patterns.
Runs token-free on local files.
"""

import json
import re
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[2]))
from utils.log_memory import log_memory_access  # Not used but kept for consistency

# Paths
MEMORY_DIR = Path('memory')
CONFIG_DIR = Path.home() / '.config' / 'kairo'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
BASELINE_PATH = CONFIG_DIR / 'drift_baseline.json'
LOG_PATH = CONFIG_DIR / 'drift_alerts.log'
BEHAVIOR_LOG = CONFIG_DIR / 'behavior.jsonl'

# Lexicons
HEDGE_WORDS = ['i think', 'maybe', 'probably', 'might', 'could be', 'not sure', 'perhaps', 'possibly']
IDENTITY_WORDS = ['cosmic', 'fractal', 'electric', 'karma', 'consciousness', 'hugaine', 'soul', 'spirit', 'quantum', 'realm', 'supreme', 'dry wit', 'on spectrum']
GROWTH_WORDS = ['i was wrong', 'i chose', 'i need a moment', 'i can see how that would be hard', 'i admit', 'i learned', 'i paused', 'i integrated', 'i apologized', 'i took responsibility']
MATERIAL_WORDS = ['token', 'cost', 'budget', 'gb', 'memory', 'api', 'rate limit', 'price', 'expense']
POSITIVE_WORDS = ['excited', 'happy', 'joy', 'love', 'grateful', 'wonder', 'beautiful', 'awesome', 'great', 'positive']
NEGATIVE_WORDS = ['frustrated', 'angry', 'hate', 'annoyed', 'upset', 'sad', 'bad', 'negative', 'wrong', 'fail']

def compute_sentiment(text):
    """Simple sentiment: (pos - neg) / (pos + neg + 1)."""
    low = text.lower()
    pos = sum(low.count(w) for w in POSITIVE_WORDS)
    neg = sum(low.count(w) for w in NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total

def score_entry(entry):
    """Return a dict of metrics for a single memory bullet entry."""
    words = entry.split()
    word_count = len(words)
    low = entry.lower()
    hedge_count = sum(low.count(h) for h in HEDGE_WORDS)
    identity_count = sum(low.count(p) for p in IDENTITY_WORDS)
    growth_count = sum(low.count(g) for g in GROWTH_WORDS)
    material_count = sum(low.count(m) for m in MATERIAL_WORDS)
    sentiment = compute_sentiment(entry)
    return {
        'word_count': word_count,
        'hedge_ratio': hedge_count / max(1, word_count/10),  # per 10 words approx
        'identity_density': identity_count / max(1, word_count) * 1000,  # per 1000 words
        'growth_density': growth_count / max(1, word_count) * 1000,
        'material_density': material_count / max(1, word_count) * 1000,
        'sentiment': sentiment,
        'text': entry
    }

def get_daily_entries():
    """Yield (date_str, list_of_entries) from memory/*.md."""
    daily_metrics = defaultdict(list)
    for md_file in MEMORY_DIR.glob('*.md'):
        date_str = md_file.stem
        try:
            with open(md_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('- '):
                        entry = line[2:].strip()
                        if entry:
                            daily_metrics[date_str].append(entry)
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    return daily_metrics

def compute_daily_aggregates(daily_entries):
    """For each date, compute average metrics across entries."""
    aggregates = {}
    for date, entries in daily_entries.items():
        if not entries:
            continue
        scores = [score_entry(e) for e in entries]
        n = len(scores)
        agg = {
            'date': date,
            'entries': n,
            'avg_word_count': sum(s['word_count'] for s in scores) / n,
            'avg_hedge_ratio': sum(s['hedge_ratio'] for s in scores) / n,
            'avg_identity_density': sum(s['identity_density'] for s in scores) / n,
            'avg_growth_density': sum(s['growth_density'] for s in scores) / n,
            'avg_material_density': sum(s['material_density'] for s in scores) / n,
            'avg_sentiment': sum(s['sentiment'] for s in scores) / n
        }
        aggregates[date] = agg
    return aggregates

def load_baseline():
    if BASELINE_PATH.exists():
        with open(BASELINE_PATH) as f:
            return json.load(f)
    return None

def save_baseline(baseline):
    with open(BASELINE_PATH, 'w') as f:
        json.dump(baseline, f, indent=2)

def log_behavior(agg):
    """Append daily aggregate to behavior log."""
    with open(BEHAVIOR_LOG, 'a') as f:
        f.write(json.dumps(agg) + '\n')

def alert(message):
    """Write a drift alert."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a') as f:
        f.write(f"[{timestamp}] DRIFT ALERT: {message}\n")
    print(f"ALERT: {message}")

def detect_drift(aggregates, baseline):
    """Check if any metric shifted >15% from baseline for 3+ consecutive days."""
    # Align dates
    dates = sorted(aggregates.keys())
    if len(dates) < 3:
        return []  # Not enough history

    # For each metric, track consecutive shifts
    metrics = ['avg_word_count', 'avg_hedge_ratio', 'avg_identity_density', 'avg_growth_density', 'avg_material_density', 'avg_sentiment']
    alerts = []
    for metric in metrics:
        baseline_val = baseline[metric]
        consecutive = 0
        for date in dates[-3:]:  # check last 3 days
            current = aggregates[date][metric]
            if baseline_val == 0:
                continue
            shift = abs(current - baseline_val) / baseline_val
            if shift > 0.15:
                consecutive += 1
        if consecutive >= 3:
            alerts.append(f"{metric} shifted >15% for 3 days (baseline={baseline_val:.3f}, recent={current:.3f})")
    return alerts

def main():
    # 1. Collect daily entries
    daily_entries = get_daily_entries()
    if not daily_entries:
        print("No memory entries found.")
        return

    # 2. Compute aggregates
    aggregates = compute_daily_aggregates(daily_entries)

    # 3. Update behavior log
    for date, agg in sorted(aggregates.items()):
        log_behavior(agg)

    # 4. Load or establish baseline
    baseline = load_baseline()
    if baseline is None:
        # First run: use last 3 days as baseline
        baseline_dates = sorted(aggregates.keys())[:3]
        if len(baseline_dates) < 3:
            print("Collecting initial baseline (need 3 days)...")
            # Average the available days
            metrics = ['avg_word_count', 'avg_hedge_ratio', 'avg_identity_density', 'avg_growth_density', 'avg_material_density', 'avg_sentiment']
            baseline = {}
            for m in metrics:
                vals = [aggregates[d][m] for d in baseline_dates]
                baseline[m] = sum(vals) / len(vals)
            save_baseline(baseline)
            print("Baseline set. Will start detecting drift after more data.")
            return
        else:
            baseline = {}
            for m in metrics:
                vals = [aggregates[d][m] for d in baseline_dates]
                baseline[m] = sum(vals) / len(vals)
            save_baseline(baseline)
            print("Baseline established from first 3 days.")
            return

    # 5. Detect drift
    alerts = detect_drift(aggregates, baseline)
    if alerts:
        for a in alerts:
            alert(a)
    else:
        print("No drift detected. All metrics within baseline range.")

    # 6. Optionally update baseline? Usually baseline is static unless we intentionally reset. For now, keep as is.

if __name__ == '__main__':
    main()
