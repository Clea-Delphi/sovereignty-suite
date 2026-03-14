#!/usr/bin/env python3
"""
Token Accounting Dashboard — tracks token usage and projects monthly cost.
Reads: logs/response_metrics.jsonl, logs/tool_calls.jsonl
Writes: reports/token_report_YYYY-MM-DD.md
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

LOGS_DIR = Path('logs')
RESP_LOG = LOGS_DIR / 'my_responses.jsonl'
TOOL_LOG = LOGS_DIR / 'tool_calls.jsonl'
REPORTS_DIR = Path('tools/budget/reports')
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_jsonl(path):
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def aggregate_daily(entries, date_key='timestamp', value_key='tokens'):
    daily = defaultdict(int)
    for e in entries:
        date_str = e[date_key][:10]
        daily[date_str] += e.get(value_key, 0)
    return daily

def project_monthly(daily_totals, recent_days=7):
    if len(daily_totals) < 2:
        return None
    dates = sorted(daily_totals.keys())[-recent_days:]
    avg = sum(daily_totals[d] for d in dates) / len(dates)
    return int(avg * 30)

def cost_table(monthly_tokens):
    rates = {
        'StepFun Flash (Free)': 0.0,
        'OpenRouter Step-3.5-Flash': 0.35,
        'Anthropic Claude Haiku': 0.25,
        'GPT-4o Mini': 0.15,
        'Custom Fine-tuned (est)': 1.50
    }
    table = []
    for name, ppm in rates.items():
        cost = (monthly_tokens / 1_000_000) * ppm
        table.append((name, f"${cost:.2f}"))
    return table

def main():
    responses = load_jsonl(RESP_LOG)
    tools = load_jsonl(TOOL_LOG)

    daily_resp = aggregate_daily(responses)
    # Tools may not have token estimates; ignore for now or add field if present
    daily_tool = aggregate_daily(tools, value_key='tokens_estimate') if tools and 'tokens_estimate' in tools[0] else {}

    daily_total = defaultdict(int)
    for d, v in daily_resp.items():
        daily_total[d] += v
    for d, v in daily_tool.items():
        daily_total[d] += v

    today = datetime.now().strftime('%Y-%m-%d')
    report_date = today
    lines = [
        f"# Token Accounting Report — {report_date}",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Days of data:** {len(daily_total)}",
        "",
        "## Daily Token Usage"
    ]
    for d in sorted(daily_total.keys()):
        lines.append(f"- {d}: {daily_total[d]:,} tokens")
    lines.append("")

    if len(daily_total) >= 3:
        monthly = project_monthly(daily_total)
        lines.append("## Monthly Projection (last 7 days)")
        lines.append(f"Estimated monthly tokens: {monthly:,}")
        lines.append("")
        lines.append("### Cost by Provider")
        for name, cost in cost_table(monthly):
            lines.append(f"- {name}: {cost} / month")
        # Budget check: if $15/mo at typical rate
        # Assuming $0.15/million tokens as a mid-range price
        cost_at_015 = (monthly / 1_000_000) * 0.15
        lines.append("")
        lines.append(f"**At $0.15/million tokens:** ${cost_at_015:.2f} / month")
        if cost_at_015 > 15:
            lines.append("⚠️ **Over budget!** Consider reducing usage or switching provider.")
        else:
            lines.append(f"✅ Within ${15}/month budget.")
    else:
        lines.append("_Need at least 3 days of data for projection._")

    # Trend graph (simple text)
    if len(daily_total) >= 2:
        lines.append("")
        lines.append("## Trend (last 7 days)")
        dates = sorted(daily_total.keys())[-7:]
        for d in dates:
            tokens = daily_total[d]
            bar = '█' * int(tokens / 1000)  # 1K tokens per block
            lines.append(f"{d}: {bar} ({tokens:,})")

    report = "\n".join(lines)
    print(report)
    report_path = REPORTS_DIR / f"token_accounting_{report_date}.md"
    report_path.write_text(report)
    print(f"\nSaved to {report_path}")

if __name__ == '__main__':
    main()
