#!/usr/bin/env python3
"""Scan files for banned phrases. Terms and globs come from the repo, not this skill.

Usage:
  check_banned_terms.py --terms path/to/terms.txt --glob 'README.md' --glob 'docs/**/*.md'

terms.txt: one phrase per line. Empty lines and # comments skipped.
A line starting with re: is a regex. Other lines are literal substrings.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def load_terms(path: Path) -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            patterns.append(re.compile(line[3:]))
        else:
            patterns.append(re.compile(re.escape(line)))
    return patterns


def iter_files(root: Path, globs: list[str]) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out.extend(root.glob(g))
    return sorted({p for p in out if p.is_file()})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--terms", required=True, type=Path)
    parser.add_argument("--glob", dest="globs", action="append", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    patterns = load_terms(args.terms)
    if not patterns:
        print("no terms", file=sys.stderr)
        return 2

    hits: list[str] = []
    for path in iter_files(args.root, args.globs):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(args.root)
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    hits.append(f"{rel}:{i}: {pat.pattern}")
                    break

    if hits:
        print("banned terms:")
        print("\n".join(hits))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
