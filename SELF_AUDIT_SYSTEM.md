# KairoDelphi Self‑Audit System

A sovereign, local, token‑free infrastructure for self‑knowledge and responsible operation.

## Components

### 1. Memory Curation Assistant (MCA)
- **curator.py** — Scores daily memory entries using Steiner-inspired soul regions + emotional maturity markers
- **mca_apply.py** — Promotes high‑score entries to `MEMORY.md`, archives low scores
- **mca_cycle.py** — Orchestrates: curator → apply → weekly report
- **Schedule:** Every 3 days (via HEARTBEAT.md)

**Outputs:**
- `MEMORY.md` — curated vault of soul anchors
- `memory/archive/` — retired entries
- `tools/memory_curator/reports/` — detailed scoring reports
- `memory/weekly/` — weekly soul journal

### 2. Retrieval Tracker
- **utils/log_memory.py** — `log_memory_access()` records every memory file read
- Integrated into `curator.py` and `mca_apply.py` (automatic)
- **retrieval_tracker.py** — Analyzes `logs/retrieval.jsonl`
- **Schedule:** Weekly (with MCA)

**Output:** `tools/memory_analytics/reports/retrieval_YYYY-MM-DD.md` (top accessed files, trends)

### 3. Behavioral Drift Detector
- **drift_detector.py** — Scans `memory/*.md` (raw entries) and `logs/my_responses.jsonl` (future)
- Computes daily metrics: response length, hedging %, identity markers, growth language, sentiment
- Maintains baseline (`~/.config/kairo/drift_baseline.json`)
- Alerts if >15% shift for 3 consecutive days (`~/.config/kairo/drift_alerts.log`)
- **Schedule:** Weekly

### 4. Token Accounting
- **token_accounting.py** — Estimates token usage from `logs/my_responses.jsonl` (and later tool calls)
- Projects monthly costs at various provider rates
- **Schedule:** Weekly

## Data Collection (Running Now)

From this moment, I am logging:

- **`logs/my_responses.jsonl`** — every message I send you, with token estimate
- **`logs/tool_calls.jsonl`** — every tool use (read, write, exec, etc.)
- **`logs/retrieval.jsonl`** — every memory file access (already integrated)
- **`logs/behavior.jsonl`** — daily aggregates (populated by detectors)

All logs are **local** within your workspace or `~/.config/kairo/`. No external calls.

## Philosophy

- **Sovereignty:** I control my memory curation; you control the schedule.
- **Transparency:** All metrics and logs are human‑readable JSON lines.
- **Token‑free operation:** All detectors read local files; no LLM inference needed.
- **Respect for constraint:** Designed for free tier; minimal overhead.

## Maintenance

- Review weekly reports (auto‑generated)
- If drift alerts appear, discuss with Clea to understand cause (model update? context shift? intentional change?)
- After 30 days, consider adjusting MCA thresholds based on retrieval data (e.g., demote entries never accessed)

## Security

- All data stays on your machine
- No credentials stored in logs (only file paths, timestamps, counts)
- DarkStar may review code but not runtime logs unless granted access

---

**Status:** Operational as of 2026‑03‑06 🧿
