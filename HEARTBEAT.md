# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Daily Digest (Every day at 20:00)

If time >= 20:00 and not yet sent today:

1. `python3 tools/notifications/digest_sender.py`

## Daily Token Check (Every day at 22:00)

If time >= 22:00:

1. `python3 tools/budget/token_accounting.py`
2. If cost > $0.50/day: send alert via `notify(priority=1)`

## Weekly Self‑Audit (Sundays 14:00)

If it's Sunday and after 14:00, run these in order:

1. `python3 tools/memory_curator/mca_cycle.py`
2. `python3 tools/memory_analytics/retrieval_tracker.py`
3. `python3 tools/behavioral_audit/drift_detector.py`
4. `python3 tools/budget/token_accounting.py`
5. `python3 tools/budget/identity_cost_tracker.py`
6. `python3 tools/notifications/audit_outbound.py`  # weekly egress audit
7. `python3 tools/self_audit/combined_report.py`  # produces unified report
8. Optionally: `python3 tools/notifications/moltbook_poster.py`  # if new content & claimed

Collect any alerts and surface them in this message.
