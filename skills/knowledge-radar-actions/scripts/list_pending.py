#!/usr/bin/env python3
"""List checked knowledge-radar actions that do not have a matching receipt."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path


ACTIONS = {
    "深读": "deep-read",
    "深入调研": "deep-research",
    "收录到 papers/": "ingest-paper",
    "确认构建 learning/ unit": "build-learning-unit",
    "忽略": "ignore",
}
PRODUCTIVE = set(ACTIONS.values()) - {"ignore"}


def entry_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    current: list[str] = []
    title: str | None = None

    def flush() -> None:
        if title is None:
            return
        body = "\n".join(current)
        radar_id = re.search(r"%% radar-id: ([^%]+) %%", body)
        if radar_id is None:
            return
        selected = [
            action
            for label, action in ACTIONS.items()
            if re.search(rf"(?m)^- \[x\] {re.escape(label)}(?:\s*:.*)?$", body)
        ]
        processed = set(
            re.findall(r"%% radar-processed: ([a-z-]+) \d{4}-\d{2}-\d{2} %%", body)
        )
        pending = [action for action in selected if action not in processed]
        if selected:
            records.append(
                {
                    "title": title,
                    "radar_id": radar_id.group(1).strip() if radar_id else None,
                    "selected_actions": selected,
                    "processed_actions": sorted(processed),
                    "pending_actions": pending,
                    "conflict": "ignore" in pending and bool(set(pending) & PRODUCTIVE),
                }
            )

    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(?:### \d+\. |#### )(.+)$", line)
        if match:
            flush()
            title = match.group(1)
            current = [line]
        elif title is not None:
            current.append(line)
    flush()
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radar-root", type=Path, default=Path("inbox/知识科技雷达"))
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    earliest = args.today - timedelta(days=args.days - 1)
    result: list[dict[str, object]] = []
    for path in sorted(args.radar_root.glob("????-??-??.md")):
        try:
            report_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if not earliest <= report_date <= args.today:
            continue
        for record in entry_records(path):
            record["date"] = report_date.isoformat()
            record["file"] = path.as_posix()
            result.append(record)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    for record in result:
        state = "冲突" if record["conflict"] else ", ".join(record["pending_actions"]) or "无待处理"
        print(f"{record['date']} | {record['title']} | {state}")


if __name__ == "__main__":
    main()
