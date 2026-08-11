#!/usr/bin/env python3
"""Validate a code-walkthrough-site content JSON file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CHECKPOINT_RE = re.compile(r"<!--\s*checkpoint:\s*([a-zA-Z0-9_-]+)\s*-->")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate(data: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["root must be an object"]

    site = data.get("site")
    if not isinstance(site, dict):
        errors.append("site must be an object")
    else:
        for key in ("title", "brand"):
            if not isinstance(site.get(key), str) or not site.get(key).strip():
                errors.append(f"site.{key} must be a non-empty string")

    lessons = data.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        errors.append("lessons must be a non-empty array")
        return errors

    seen_lesson_ids: set[str] = set()
    for li, lesson in enumerate(lessons):
        prefix = f"lessons[{li}]"
        if not isinstance(lesson, dict):
            errors.append(f"{prefix} must be an object")
            continue

        lesson_id = lesson.get("id")
        if not isinstance(lesson_id, str) or not lesson_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif lesson_id in seen_lesson_ids:
            errors.append(f"{prefix}.id duplicate: {lesson_id}")
        else:
            seen_lesson_ids.add(lesson_id)

        if not isinstance(lesson.get("title"), str) or not lesson.get("title").strip():
            errors.append(f"{prefix}.title must be a non-empty string")

        markdown = lesson.get("markdown")
        if not isinstance(markdown, str) or not markdown.strip():
            errors.append(f"{prefix}.markdown must be a non-empty string")
            markdown = ""

        initial_repo = lesson.get("initialRepo", {})
        if initial_repo is None:
            initial_repo = {}
        if not isinstance(initial_repo, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in initial_repo.items()
        ):
            errors.append(f"{prefix}.initialRepo must be an object of string→string")

        checkpoints = lesson.get("checkpoints")
        if not isinstance(checkpoints, list) or not checkpoints:
            errors.append(f"{prefix}.checkpoints must be a non-empty array")
            continue

        anchors = CHECKPOINT_RE.findall(markdown)
        anchor_set = set(anchors)
        if len(anchors) != len(anchor_set):
            errors.append(f"{prefix}.markdown has duplicate checkpoint anchors")

        seen_cp: set[str] = set()
        for ci, cp in enumerate(checkpoints):
            cpx = f"{prefix}.checkpoints[{ci}]"
            if not isinstance(cp, dict):
                errors.append(f"{cpx} must be an object")
                continue

            cp_id = cp.get("id")
            if not isinstance(cp_id, str) or not cp_id.strip():
                errors.append(f"{cpx}.id must be a non-empty string")
            elif cp_id in seen_cp:
                errors.append(f"{cpx}.id duplicate: {cp_id}")
            else:
                seen_cp.add(cp_id)
                if cp_id not in anchor_set:
                    errors.append(
                        f"{cpx}.id '{cp_id}' missing matching <!-- checkpoint: {cp_id} --> in markdown"
                    )

            if not isinstance(cp.get("label"), str) or not cp.get("label").strip():
                errors.append(f"{cpx}.label must be a non-empty string")

            file_path = cp.get("file")
            if not isinstance(file_path, str) or not file_path.strip():
                errors.append(f"{cpx}.file must be a non-empty string")

            repo = cp.get("repo")
            if not isinstance(repo, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in repo.items()
            ):
                errors.append(f"{cpx}.repo must be an object of string→string")
                repo = {}

            if repo and isinstance(file_path, str) and file_path and file_path not in repo:
                errors.append(
                    f"{cpx}.file '{file_path}' is not present in repo (keys: {sorted(repo)})"
                )

            focus = cp.get("focus")
            if focus is not None:
                if (
                    not isinstance(focus, list)
                    or len(focus) != 2
                    or not all(isinstance(n, int) and n >= 1 for n in focus)
                    or focus[0] > focus[1]
                ):
                    errors.append(
                        f"{cpx}.focus must be [startLine, endLine] with 1-based inclusive ints"
                    )

        for anchor in sorted(anchor_set - seen_cp):
            errors.append(
                f"{prefix}.markdown anchor '{anchor}' has no matching checkpoint entry"
            )

        # Soft monotonicity warnings as errors? Keep as warnings via stderr style — include as errors only when clearly broken empty→content is fine.
        # Optional: detect total rewrite (no shared lines) when both non-empty — warn only.
        prev_repo: dict[str, str] = dict(initial_repo) if isinstance(initial_repo, dict) else {}
        for ci, cp in enumerate(checkpoints):
            if not isinstance(cp, dict):
                continue
            repo = cp.get("repo") if isinstance(cp.get("repo"), dict) else {}
            for path, text in repo.items():
                if path in prev_repo and prev_repo[path] and text:
                    prev_lines = set(prev_repo[path].splitlines())
                    next_lines = set(text.splitlines())
                    if prev_lines and not (prev_lines & next_lines):
                        errors.append(
                            f"{prefix}.checkpoints[{ci}].repo['{path}'] shares no lines with previous snapshot; "
                            "prefer monotonic inserts or set focus"
                        )
            prev_repo = {**prev_repo, **repo}

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("content", type=Path, help="Path to content JSON")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result")
    args = parser.parse_args()

    if not args.content.is_file():
        print(f"error: file not found: {args.content}", file=sys.stderr)
        return 2

    try:
        data = load_json(args.content)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        if errors:
            print(f"FAIL {args.content} ({len(errors)} issue(s))")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"OK {args.content}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
