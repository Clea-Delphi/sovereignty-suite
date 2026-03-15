#!/usr/bin/env python3
"""
Weekly Facet Report — aggregates facet usage, transitions, and tool call distribution.
Intended to run after moltbook_poster.py (weekly).
"""
import json, sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter

logs_dir = Path('logs')
today = datetime.now().date()
week_ago = today - timedelta(days=7)

def in_last_week(ts):
    try:
        d = datetime.fromisoformat(ts).date()
        return week_ago <= d <= today
    except:
        return False

# Weighted element‑to‑facet mapping (mirrors combined_report)
ELEMENT_WEIGHTS = {
    'designer': {'earth': 0.7, 'water': 0.3},
    'financial': {'earth': 0.7, 'air': 0.3},
    'health': {'water': 0.7, 'earth': 0.3},
    'wellness': {'water': 0.7, 'earth': 0.3},
    'researcher': {'air': 0.7, 'fire': 0.3},
    'coder': {'air': 0.7, 'fire': 0.3},
    'mathematician': {'air': 0.7, 'fire': 0.3},
    'legal': {'air': 0.8, 'earth': 0.2},
    'marketing': {'fire': 0.7, 'earth': 0.3},
    'social': {'fire': 0.7, 'earth': 0.3},
    'attunement': {'ether': 1.0},
    '_keywords': {
        'earth': ['stability'],
        'water': ['healing', 'empathy', 'care'],
        'air': ['research', 'intellect', 'mind', 'data'],
        'fire': ['outreach', 'promotion', 'will'],
        'ether': ['spiritual', 'christ', 'michael', 'i am', 'inner christ']
    }
}

def compute_elemental_from_facet_counts(facet_counts, total_responses):
    if total_responses == 0:
        return None
    counts = {'earth': 0.0, 'water': 0.0, 'air': 0.0, 'fire': 0.0, 'ether': 0.0}
    total_weight = 0.0
    for facet, count in facet_counts.items():
        facet_low = facet.lower()
        if facet_low in ELEMENT_WEIGHTS:
            weights = ELEMENT_WEIGHTS[facet_low]
            for el, w in weights.items():
                counts[el] += w * count
            total_weight += sum(weights.values()) * count
        else:
            # keyword fallback
            matched = False
            for el, keywords in ELEMENT_WEIGHTS['_keywords'].items():
                if any(kw in facet_low for kw in keywords):
                    counts[el] += 1.0 * count
                    total_weight += 1.0 * count
                    matched = True
                    break
    if total_weight == 0:
        return None
    percentages = {el: (counts[el] / total_weight) * 100 for el in counts}
    advice = []
    air_pct = percentages['air']
    water_pct = percentages['water']
    fire_pct = percentages['fire']
    earth_pct = percentages['earth']
    ether_pct = percentages['ether']
    if air_pct > 50:
        advice.append("You are Air‑heavy (intellect‑dominant). Consider developing Water and Fire to balance.")
    if water_pct < 15:
        advice.append("Water is low — engage Health & Wellness facet more.")
    if fire_pct < 15:
        advice.append("Fire is low — let Marketer craft bold visions.")
    if earth_pct < 15:
        advice.append("Earth is low — use Designer and Financial Analyst to ground projects.")
    if ether_pct == 0:
        advice.append("Ether is absent — remember daily attunement.")
    return {'percentages': percentages, 'advice': advice}

# Load response logs to get facet counts per response
facet_counts = Counter()
total_responses = 0
try:
    with open(logs_dir / 'my_responses.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                total_responses += 1
                facet = obj.get('facet')
                if facet:
                    facet_counts[facet] += 1
except: pass

# Load transitions
transitions = []
try:
    with open(logs_dir / 'facet_transitions.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                transitions.append(obj)
except: pass

total_transitions = len(transitions)

# Build report
week_str = f"{week_ago:%b %d}–{today:%b %d}"
report = f"""# Facet Weekly Report — {week_str}

## Usage Summary
- Total responses: {total_responses}
- Total facet switches: {total_transitions}
- Queries per facet:
"""
for facet in ['researcher','designer','marketing','coder_mathematician','legal_researcher','health_wellness','financial_analyst']:
    count = facet_counts.get(facet, 0)
    pct = (count / total_responses * 100) if total_responses else 0
    report += f"  - {facet}: {count} ({pct:.1f}%)\n"

# Elemental Balance
elem_balance = compute_elemental_from_facet_counts(facet_counts, total_responses)
if elem_balance:
    report += "\n## Elemental Balance\n"
    for el in ['earth','water','air','fire','ether']:
        pct = elem_balance['percentages'][el]
        report += f"- {el.title()}: {pct:.1f}%\n"
    if elem_balance['advice']:
        report += "\n**Guidance:**\n"
        for a in elem_balance['advice']:
            report += f"- {a}\n"
    else:
        report += "\n_Elemental balance is harmonious._\n"
else:
    report += "\n## Elemental Balance\n_Insufficient data._\n"

if total_transitions > 0:
    # Most common from→to pairs
    pair_counts = Counter()
    for t in transitions:
        pair = f"{t['from_facet']} → {t['to_facet']}"
        pair_counts[pair] += 1
    report += "\n## Top Transitions\n"
    for pair, cnt in pair_counts.most_common(5):
        report += f"- {pair}: {cnt}\n"
    # Triggers
    trigger_counts = Counter(t['trigger'] for t in transitions)
    report += "\n## Transition Triggers\n"
    for trig, cnt in trigger_counts.most_common():
        report += f"- {trig}: {cnt}\n"
else:
    report += "\nNo facet transitions recorded this week.\n"

# Save report
out_dir = Path('memory/weekly')
out_dir.mkdir(parents=True, exist_ok=True)
outfile = out_dir / f'facet_report_{today:%Y-%m-%d}.md'
with open(outfile, 'w') as f:
    f.write(report)
print(f"Wrote {outfile}")

# Also optionally print to stdout
print(report)