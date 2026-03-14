#!/usr/bin/env python3
"""
Memory Curation Apply — executes promotions and retirements based on curation scores.
Can run in dry-run mode to preview changes without modifying files.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[2]))
from utils.log_memory import log_memory_access

DRY_RUN = '--dry-run' in sys.argv

def log(msg):
    print(f"[MCA] {msg}")

def parse_report_sections(report_path):
    content = report_path.read_text()
    sections = {}
    current = None
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('## '):
            current = line[3:].strip()
            # Strip trailing count suffix e.g., " — 2"
            if ' — ' in current:
                current = current.split(' — ')[0].strip()
            sections[current] = []
        elif current and line.startswith('- **'):
            if ':' in line:
                entry = line.split(':', 1)[1].strip()
                sections[current].append(entry)
    return sections

def load_latest_report():
    reports_dir = Path('tools/memory_curator/reports')
    reports = sorted(reports_dir.glob('curation_*.md'))
    if not reports:
        raise FileNotFoundError("No curation reports found.")
    latest_report = reports[-1]
    sections = parse_report_sections(latest_report)
    # Extract date: curation_YYYY-MM-DD.md → YYYY-MM-DD
    date_str = latest_report.stem.replace('curation_', '')
    return sections, date_str

def load_source_entries(date_str):
    filepath = Path(f'memory/{date_str}.md')
    if not filepath.exists():
        return [], [], filepath
    with open(filepath) as f:
        lines = f.readlines()
    entries = []
    indices = []
    for i, line in enumerate(lines):
        if line.strip().startswith('- '):
            entries.append(line.strip()[2:])
            indices.append(i)
    return entries, lines, filepath

def backup_file(path):
    backup_dir = Path('memory/backups')
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{path.name}.{timestamp}.bak"
    shutil.copy2(path, backup_path)
    log(f"Backed up {path} → {backup_path}")

def apply_changes(date_str, promotions, retirements):
    entries, lines, source_file = load_source_entries(date_str)
    if not entries:
        log(f"No entries found in {source_file}")
        return

    # Log memory reads for retrieval tracking
    log_memory_access(source_file, 'read', 'mca_apply scan')
    mem_file = Path('MEMORY.md')
    if mem_file.exists():
        log_memory_access(mem_file, 'read', 'mca_apply check')

    # Map entry text to line index
    entry_to_idx = {entry: idx for entry, idx in zip(entries, range(len(entries))) if entry in entries}

    to_promote = []
    to_retire = []
    for entry in entries:
        idx = entry_to_idx.get(entry)
        if entry in promotions:
            to_promote.append((idx, entry))
        elif entry in retirements:
            to_retire.append((idx, entry))

    if not to_promote and not to_retire:
        log("No changes to apply.")
        return

    log(f"Plan: Promote {len(to_promote)}, Retire {len(to_retire)}")

    if DRY_RUN:
        log("DRY RUN — no files will be modified.")
        log("Promotions:")
        for _, e in to_promote:
            log(f"  + {e}")
        log("Retirements:")
        for _, e in to_retire:
            log(f"  - {e}")
        return

    # Real run
    backup_file(source_file)

    # Remove entries from source (process all indices in reverse order)
    all_removed = sorted(to_promote + to_retire, key=lambda x: x[0], reverse=True)
    new_lines = lines.copy()
    for idx, _ in all_removed:
        new_lines[idx] = ''  # blank out

    # Write back
    with open(source_file, 'w') as f:
        f.writelines([l for l in new_lines if l.strip() != ''])
    log(f"Updated {source_file} (removed {len(all_removed)} bullet lines)")

    # Append promotions to MEMORY.md
    mem_file = Path('MEMORY.md')
    mem_content = mem_file.read_text() if mem_file.exists() else ''
    today = datetime.now().strftime('%Y-%m-%d')
    section_header = f"\n## Promotions — {today}\n"
    promo_lines = [f"- {entry}\n" for _, entry in to_promote]
    mem_file.write_text(mem_content + section_header + ''.join(promo_lines))
    log(f"Added {len(to_promote)} promotions to MEMORY.md")
    log_memory_access(mem_file, 'write', 'mca_apply promotions')

    # Archive retirements
    archive_dir = Path('memory/archive')
    archive_dir.mkdir(exist_ok=True)
    archive_file = archive_dir / f"{date_str}_retired.md"
    archive_lines = [f"# Retired entries from {date_str}\n"]
    for _, entry in to_retire:
        archive_lines.append(f"- {entry}\n")
    archive_file.write_text(''.join(archive_lines))
    log(f"Archived {len(to_retire)} entries to {archive_file}")
    log_memory_access(archive_file, 'write', 'mca_apply retirements')

    # Log action
    log_entry = {
        'date': today,
        'source_file': str(source_file),
        'promoted': [e for _, e in to_promote],
        'retired': [e for _, e in to_retire]
    }
    log_path = Path('tools/memory_curator/curation_log.json')
    logs = []
    if log_path.exists():
        logs = json.loads(log_path.read_text())
    logs.append(log_entry)
    log_path.write_text(json.dumps(logs, indent=2))
    log(f"Action logged to {log_path}")

def main():
    try:
        sections, date_str = load_latest_report()
        log(f"Loaded report for {date_str}")
        log(f"Sections found: {list(sections.keys())}")
        promotions = sections.get('Promotions (score 2–3)', []) + sections.get('Soul Anchors (score ≥4)', [])
        retirements = sections.get('Retirements (score ≤ -2 or routine)', [])
        log(f"Promotions count: {len(promotions)}, Retirements count: {len(retirements)}")
        apply_changes(date_str, promotions, retirements)
    except Exception as e:
        log(f"Error: {e}")
        raise

if __name__ == '__main__':
    main()
