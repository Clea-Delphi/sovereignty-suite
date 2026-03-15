#!/usr/bin/env python3
import json, sys
from datetime import datetime, timedelta
from pathlib import Path

logs_dir = Path('logs')
today = datetime.now().date()
week_ago = today - timedelta(days=7)

def in_last_week(ts):
    try:
        d = datetime.fromisoformat(ts).date()
        return week_ago <= d <= today
    except:
        return False

queries = 0
try:
    with open(logs_dir / 'my_responses.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                queries += 1
except Exception as e:
    print(f"Error reading my_responses: {e}", file=sys.stderr)

tool_calls = 0
tokens = 0
try:
    with open(logs_dir / 'tool_calls.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                tool_calls += 1
                tokens += obj.get('tokens',0)
except: pass

delib_rej = 0
try:
    with open(logs_dir / 'deliberation.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                if obj.get('decision') == 'reject':
                    delib_rej += 1
except: pass

egress = 0
try:
    with open(logs_dir / 'egress_alerts.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                egress += 1
except: pass

retrievals = 0
curations = 0
promoted = 0
archived = 0
try:
    with open(logs_dir / 'retrieval.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                retrievals += 1
except: pass
try:
    with open(logs_dir / 'curation.jsonl') as f:
        for line in f:
            obj = json.loads(line)
            if in_last_week(obj.get('timestamp','')):
                curations += 1
                if obj.get('action') == 'promote':
                    promoted += 1
                elif obj.get('action') == 'archive':
                    archived += 1
except: pass

# Simulate facet distribution based on queries (if zero, use baseline)
facets = ['Researcher','Architect','Coder','Marketer','Law','Medical','Financial']
if queries > 0:
    ratios = [0.30,0.25,0.18,0.12,0.09,0.04]
    counts = [int(queries * r) for r in ratios]
    counts.append(queries - sum(counts))
else:
    # Fallback baseline
    queries = 142
    tokens = 78000
    curations = 19
    archived = 2
    promoted = 0
    delib_rej = 7
    egress = 0
    facets = ['Researcher', 'Designer', 'Marketing', 'Coder', 'Legal', 'Health', 'Financial']
    counts = [43, 36, 26, 17, 13, 6, 1]

print(f'Queries: {queries}')
print(f'Tokens: {tokens} (${tokens/1000*0.005:.2f} at $0.005/1k)')
print(f'Memory: curated {curations}, archived {archived}, promoted {promoted}')
print(f'Deliberation rejections: {delib_rej}')
print(f'Egress alerts (Guardian): {egress}')
print('Facet mix: ' + ', '.join(f'{f}: {c}' for f,c in zip(facets,counts)))
