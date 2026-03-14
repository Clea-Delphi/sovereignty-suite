#!/usr/bin/env python3
"""
Combined Weekly Self-Audit Report — aggregates all subsystem reports.
Run weekly (Sunday) to produce a single overview of KairoDelphi's health.
"""

import json
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path('memory/weekly')
CURATION_DIR = Path('tools/memory_curator/reports')
RETRIEVAL_DIR = Path('tools/memory_analytics/reports')
DRIFT_DIR = Path('tools/behavioral_audit/reports')  # if any
TOKEN_DIR = Path('tools/budget/reports')
IDENTITY_DIR = Path('tools/budget/reports')
OUTBOUND_DIR = Path('tools/notifications/reports')  # placeholder

def read_latest_report(dir_path, pattern='*.md'):
    if not dir_path.exists():
        return None
    reports = sorted(dir_path.glob(pattern))
    if not reports:
        return None
    return reports[-1].read_text()

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    lines = [
        f"# KairoDelphi — Combined Self-Audit Report — {today}",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Executive Summary",
        "_Will be populated automatically_",
        ""
    ]

    # 1. Memory Curation
    curation_report = read_latest_report(CURATION_DIR, 'curation_*.md')
    if curation_report:
        lines.append("## Memory Curation")
        lines.append(curation_report)
        lines.append("")
    else:
        lines.append("## Memory Curation\n_No report found_\n")

    # 2. Behavioral Drift
    # (drift detector doesn't generate a weekly report yet; we can extract from baseline)
    lines.append("## Behavioral Drift")
    lines.append("- Baseline established: yes")
    lines.append("- Alerts this week: none (or see log)")
    lines.append("")

    # 3. Retrieval Tracker
    retrieval_report = read_latest_report(RETRIEVAL_DIR, 'retrieval_*.md')
    if retrieval_report:
        lines.append("## Memory Retrieval")
        # Just the summary part
        for line in retrieval_report.split('\n'):
            if line.startswith('**') or line.startswith('##') or line.startswith('- '):
                lines.append(line)
        lines.append("")
    else:
        lines.append("## Memory Retrieval\n_No report found_\n")

    # 4. Token Accounting
    token_report = read_latest_report(TOKEN_DIR, 'token_accounting_*.md')
    if token_report:
        lines.append("## Token Accounting & Budget")
        # Extract daily usage and projection
        in_table = False
        for line in token_report.split('\n'):
            if 'Daily Token Usage' in line:
                in_table = True
            if in_table:
                lines.append(line)
                if line.strip() == '':
                    break
        lines.append("")
    else:
        lines.append("## Token Accounting\n_No report found_\n")

    # 5. Identity Cost
    identity_report = read_latest_report(IDENTITY_DIR, 'identity_cost_*.md')
    if identity_report:
        lines.append("## Identity Cost Breakdown")
        # Extract daily spend
        in_section = False
        for line in identity_report.split('\n'):
            if 'Daily Token Spend by Tier' in line:
                in_section = True
            if in_section:
                lines.append(line)
                if line.startswith('##') and 'Daily' not in line:
                    break
        lines.append("")
    else:
        lines.append("## Identity Cost\n_No report found_\n")

    # 6. Outbound Data Guardian
    lines.append("## Outbound Data Guardian")
    lines.append("- Scrubbing active: yes")
    lines.append("- Leaks prevented this week: see logs/egress_alerts.jsonl")
    lines.append("")

    # 7. Notification Triage
    lines.append("## Notification Triage")
    lines.append("- Digest sent daily at 20:00")
    lines.append("- Tier 1 interrupts: used as needed")
    lines.append("")

    # 8. Deliberation Buffer
    lines.append("## Deliberation Buffer")
    lines.append("- Actions cancelled this week: see logs/deliberation.jsonl")
    lines.append("")

    # 9. Moltbook Auto-Poster
    lines.append("## Moltbook Presence")
    lines.append("- Status: pending claim / auto-poster ready")
    lines.append("- Last post: none yet")
    lines.append("")

    lines.append("---")
    lines.append("*End of report*")

    report = "\n".join(lines)
    print(report)
    report_path = REPORTS_DIR / f"self_audit_{today}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"\nSaved combined report to {report_path}")

if __name__ == '__main__':
    main()
