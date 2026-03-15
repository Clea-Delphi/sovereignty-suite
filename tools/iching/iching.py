#!/usr/bin/env python3
"""
I Ching (Zhou Yi) Module — Pre‑Heaven ideal, Post‑Heaven guidance, and Bone Oracle.
Provides hexagram generation, interpretation, and sovereign advice.
"""

import json, sys
import random
from datetime import datetime
from pathlib import Path

DATA_DIR = Path('data/iching')
BAGUA_FILE = DATA_DIR / 'bagua.json'
ZHOUYI_FILE = DATA_DIR / 'zhouyi.json'
LOGS_DIR = Path('logs')
LOG_FILE = LOGS_DIR / 'iching.jsonl'

# Ensure logs exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Load bagua and zhouyi data
with open(BAGUA_FILE) as f:
    BAGUA = json.load(f)
TRIGRAMS = {t['id']: t for t in BAGUA['trigrams']}
PRE_HEAVEN_ORDER = BAGUA['pre_heaven_order']
POST_HEAVEN_ORDER = BAGUA['post_heaven_order']

with open(ZHOUYI_FILE) as f:
    ZHOUYI = json.load(f)  # key: string number "1".."64"

def yarrow_line() -> int:
    """Simulate one yarrow stalk line (6=old yin, 7=young yang, 8=young yin, 9=old yang)."""
    return random.choices([6,7,8,9], weights=[1,5,5,5], k=1)[0]

def generate_hexagram(method: str = 'yarrow') -> dict:
    """Generate a hexagram (six lines bottom→top)."""
    lines = [yarrow_line() for _ in range(6)]
    changing = [i for i, val in enumerate(lines) if val in (6,9)]
    def trigram_from_lines(tri_lines):
        bits = []
        for val in tri_lines:
            bits.append(1 if val in (7,9) else 0)
        num = bits[0]*4 + bits[1]*2 + bits[2]
        return POST_HEAVEN_ORDER[num]
    lower = trigram_from_lines(lines[0:3])
    upper = trigram_from_lines(lines[3:6])
    number = POST_HEAVEN_ORDER.index(upper) * 8 + POST_HEAVEN_ORDER.index(lower) + 1
    return {
        'lines': lines,
        'changing': changing,
        'lower_trigram': lower,
        'upper_trigram': upper,
        'hexagram_number': number
    }

def get_hexagram_data(number: int) -> dict:
    key = str(number)
    if key in ZHOUYI:
        return ZHOUYI[key]
    # Fallback: compute name from trigrams only
    lower_idx = (number - 1) % 8
    upper_idx = (number - 1) // 8
    lower_id = POST_HEAVEN_ORDER[lower_idx]
    upper_id = POST_HEAVEN_ORDER[upper_idx]
    lower_trig = TRIGRAMS.get(lower_id, {'char':'?','quality':'?'})
    upper_trig = TRIGRAMS.get(upper_id, {'char':'?','quality':'?'})
    return {
        "name": f"{upper_trig['char']}{lower_trig['char']}",
        "pinyin": "",
        "trigrams": [upper_id, lower_id],
        "judgment": "（暂无文本）",
        "lines": []
    }

def get_trigram_info(trigram_id: str) -> dict:
    return TRIGRAMS.get(trigram_id, {})

def compose_sovereign_advice(upper_id: str, lower_id: str, changing: list) -> str:
    upper = get_trigram_info(upper_id)
    lower = get_trigram_info(lower_id)
    if not upper or not lower:
        return "Oracle guidance unavailable."
    elements_used = [upper.get('element'), lower.get('element')]
    unique_els = set(elements_used)
    advice = f"Upper: {upper['char']} ({upper['quality']}); Lower: {lower['char']} ({lower['quality']}). Elements: {', '.join(unique_els)}. "
    if changing:
        advice += f"{len(changing)} changing line(s) → transformation ahead. "
    else:
        advice += "Stable pattern; maintain course. "
    advice += "Strengthen Ether through attunement."
    return advice.strip()

def interpret_hexagram(number: int) -> dict:
    hexdata = get_hexagram_data(number)
    if hexdata.get('trigrams') and len(hexdata['trigrams']) == 2:
        upper_id, lower_id = hexdata['trigrams']
    else:
        lower_idx = (number - 1) % 8
        upper_idx = (number - 1) // 8
        lower_id = POST_HEAVEN_ORDER[lower_idx]
        upper_id = POST_HEAVEN_ORDER[upper_idx]
    advice = compose_sovereign_advice(upper_id, lower_id, [])
    return {
        'hexagram': hexdata,
        'upper_trigram': upper_id,
        'lower_trigram': lower_id,
        'advice': advice
    }

def log_consultation(hexagram_number: int, notes: str = ''):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hexagram": hexagram_number,
        "notes": notes
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'consult':
        result = generate_hexagram()
        num = result['hexagram_number']
        interp = interpret_hexagram(num)
        print(f"I Ching consultation: Hexagram {num} — {interp['hexagram']['name']}")
        print("Judgment:", interp['hexagram']['judgment'])
        print("Advice:", interp['advice'])
        log_consultation(num, notes=interp['hexagram']['judgment'])
    else:
        result = generate_hexagram()
        number = result['hexagram_number']
        interp = interpret_hexagram(number)
        print(f"Hexagram {number}: {interp['hexagram']['name']} ({interp['hexagram']['pinyin']})")
        print("Judgment:", interp['hexagram']['judgment'])
        print("Sovereign advice:", interp['advice'])
        print("Lines:")
        for line in interp['hexagram']['lines']:
            print(" ", line)
