#!/usr/bin/env python3
"""Detect banned Chinese jargon and overused contrast frames.

Usage:
  check_writing_style.py --text '以调研为抓手推进'
  check_writing_style.py path/to/note.md
  check_writing_style.py --stdin
  check_writing_style.py --json note.md
  check_writing_style.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEXICON = ROOT / "references" / "banned-terms.tsv"
DEFAULT_PATTERNS = ROOT / "references" / "sentence-patterns.tsv"

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"`[^`]+`")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
MD_LINK_RE = re.compile(r"\[[^\]\n]*\]\([^)]+\)")
FRONTMATTER_OPEN_RE = re.compile(r"^---\s*$")


@dataclass(frozen=True)
class Term:
    severity: str
    category: str
    raw: str
    replacements: tuple[str, ...]
    note: str
    keep_if: str
    literal: str | None
    pattern: re.Pattern[str] | None


@dataclass(frozen=True)
class PatternDef:
    id: str
    family: str
    severity: str
    regex: re.Pattern[str]
    x_group: str
    y_group: str
    soft_limit: int
    replacements: tuple[str, ...]
    note: str
    keep_if: str


@dataclass(frozen=True)
class Hit:
    path: str
    line: int
    col: int
    term: str
    matched: str
    severity: str
    category: str
    replacements: tuple[str, ...]
    note: str
    keep_if: str
    excerpt: str

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": "term",
            "path": self.path,
            "line": self.line,
            "col": self.col,
            "term": self.term,
            "matched": self.matched,
            "severity": self.severity,
            "category": self.category,
            "replacements": list(self.replacements),
            "note": self.note,
            "keep_if": self.keep_if,
            "excerpt": self.excerpt,
        }


@dataclass(frozen=True)
class PatternHit:
    path: str
    line: int
    col: int
    pattern_id: str
    family: str
    matched: str
    x: str
    y: str
    severity: str
    replacements: tuple[str, ...]
    note: str
    keep_if: str
    excerpt: str
    index: int
    count: int
    soft_limit: int
    over_limit: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": "pattern",
            "path": self.path,
            "line": self.line,
            "col": self.col,
            "id": self.pattern_id,
            "family": self.family,
            "matched": self.matched,
            "x": self.x,
            "y": self.y,
            "severity": self.severity,
            "replacements": list(self.replacements),
            "note": self.note,
            "keep_if": self.keep_if,
            "excerpt": self.excerpt,
            "index": self.index,
            "count": self.count,
            "soft_limit": self.soft_limit,
            "over_limit": self.over_limit,
        }


@dataclass(frozen=True)
class LineMap:
    offset: int
    line_no: int
    line: str
    skip: list[tuple[int, int]]


def load_terms(path: Path) -> list[Term]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"empty lexicon: {path}")
    header = lines[0].split("\t")
    expected = ["severity", "category", "term", "replacements", "note", "keep_if"]
    if header[:6] != expected:
        raise ValueError(f"unexpected header in {path}: {header[:6]!r}")

    terms: list[Term] = []
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        cols += [""] * (6 - len(cols))
        severity, category, term, replacements, note, keep_if = (c.strip() for c in cols[:6])
        if severity not in {"ban", "flag"}:
            raise ValueError(f"bad severity {severity!r} for {term!r}")
        if not term:
            raise ValueError("empty term")
        reps = tuple(part for part in replacements.split("|") if part)
        if term.startswith("re:"):
            terms.append(
                Term(severity, category, term, reps, note, keep_if, None, re.compile(term[3:]))
            )
        else:
            terms.append(Term(severity, category, term, reps, note, keep_if, term, None))
    if not terms:
        raise ValueError(f"no terms in {path}")
    return terms


def load_patterns(path: Path) -> list[PatternDef]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"empty patterns: {path}")
    header = lines[0].split("\t")
    expected = [
        "id",
        "family",
        "severity",
        "regex",
        "x_group",
        "y_group",
        "soft_limit",
        "replacements",
        "note",
        "keep_if",
    ]
    if header[:10] != expected:
        raise ValueError(f"unexpected header in {path}: {header[:10]!r}")

    patterns: list[PatternDef] = []
    for raw_line in lines[1:]:
        line = raw_line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        cols += [""] * (10 - len(cols))
        (
            pid,
            family,
            severity,
            regex,
            x_group,
            y_group,
            soft_limit,
            replacements,
            note,
            keep_if,
        ) = (c.strip() for c in cols[:10])
        if severity not in {"ban", "flag"}:
            raise ValueError(f"bad severity {severity!r} for {pid!r}")
        if not pid or not regex:
            raise ValueError("empty pattern id or regex")
        try:
            limit = int(soft_limit)
        except ValueError as exc:
            raise ValueError(f"bad soft_limit {soft_limit!r} for {pid!r}") from exc
        if limit < 1:
            raise ValueError(f"soft_limit must be >= 1 for {pid!r}")
        reps = tuple(part for part in replacements.split("|") if part)
        patterns.append(
            PatternDef(
                id=pid,
                family=family,
                severity=severity,
                regex=re.compile(regex),
                x_group=x_group or "x",
                y_group=y_group or "y",
                soft_limit=limit,
                replacements=reps,
                note=note,
                keep_if=keep_if,
            )
        )
    if not patterns:
        raise ValueError(f"no patterns in {path}")
    return patterns


def skip_spans(line: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for cre in (INLINE_CODE_RE, URL_RE, MD_LINK_RE):
        for match in cre.finditer(line):
            spans.append((match.start(), match.end()))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def in_spans(index: int, end: int, spans: Sequence[tuple[int, int]]) -> bool:
    for start, stop in spans:
        if index >= stop:
            continue
        if end <= start:
            return False
        return True
    return False


def collect_candidates(
    line: str, terms: Sequence[Term], spans: Sequence[tuple[int, int]]
) -> list[tuple[int, int, Term, str]]:
    found: list[tuple[int, int, Term, str]] = []
    for term in terms:
        if term.literal is not None:
            start = 0
            while True:
                index = line.find(term.literal, start)
                if index < 0:
                    break
                end = index + len(term.literal)
                if not in_spans(index, end, spans):
                    found.append((index, end, term, term.literal))
                start = index + 1
            continue
        assert term.pattern is not None
        for match in term.pattern.finditer(line):
            if not in_spans(match.start(), match.end(), spans):
                found.append((match.start(), match.end(), term, match.group(0)))
    return found


def pick_non_overlapping(
    candidates: Sequence[tuple[int, int, Term, str]],
) -> list[tuple[int, int, Term, str]]:
    ordered = sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]), -len(item[2].raw)))
    picked: list[tuple[int, int, Term, str]] = []
    cursor = -1
    for start, end, term, matched in ordered:
        if start < cursor:
            continue
        picked.append((start, end, term, matched))
        cursor = end
    return picked


def excerpt_around(line: str, start: int, end: int, width: int = 24) -> str:
    left = max(0, start - width)
    right = min(len(line), end + width)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(line) else ""
    return prefix + line[left:right].strip() + suffix


def visible_lines(text: str) -> Iterable[tuple[int, str]]:
    in_fence = False
    fence_marker = ""
    in_frontmatter = False
    lines = text.splitlines()
    for number, line in enumerate(lines, start=1):
        if number == 1 and FRONTMATTER_OPEN_RE.match(line):
            in_frontmatter = True
            continue
        if in_frontmatter:
            if FRONTMATTER_OPEN_RE.match(line):
                in_frontmatter = False
            continue
        fence = FENCE_RE.match(line)
        if fence:
            token = fence.group(1)
            if not in_fence:
                in_fence, fence_marker = True, token[0]
            elif token[0] == fence_marker:
                in_fence = False
            continue
        if not in_fence:
            yield number, line


def scan_terms(text: str, terms: Sequence[Term], path: str) -> list[Hit]:
    hits: list[Hit] = []
    for number, line in visible_lines(text):
        spans = skip_spans(line)
        picked = pick_non_overlapping(collect_candidates(line, terms, spans))
        for start, end, term, matched in picked:
            hits.append(
                Hit(
                    path=path,
                    line=number,
                    col=start + 1,
                    term=term.raw,
                    matched=matched,
                    severity=term.severity,
                    category=term.category,
                    replacements=term.replacements,
                    note=term.note,
                    keep_if=term.keep_if,
                    excerpt=excerpt_around(line, start, end),
                )
            )
    return hits


def join_visible(text: str) -> tuple[str, list[LineMap]]:
    mapping: list[LineMap] = []
    chunks: list[str] = []
    pos = 0
    for line_no, line in visible_lines(text):
        mapping.append(LineMap(pos, line_no, line, skip_spans(line)))
        chunks.append(line)
        pos += len(line) + 1
    return "\n".join(chunks), mapping


def map_offset(offset: int, mapping: Sequence[LineMap]) -> LineMap:
    chosen = mapping[0]
    for item in mapping:
        if offset >= item.offset:
            chosen = item
        else:
            break
    return chosen


def pattern_skipped(start: int, end: int, mapping: Sequence[LineMap]) -> bool:
    for item in mapping:
        line_end = item.offset + len(item.line)
        if end <= item.offset or start >= line_end:
            continue
        local_start = max(0, start - item.offset)
        local_end = min(len(item.line), end - item.offset)
        if in_spans(local_start, local_end, item.skip):
            return True
    return False


def collect_pattern_candidates(
    joined: str, patterns: Sequence[PatternDef], mapping: Sequence[LineMap]
) -> list[tuple[int, int, PatternDef, re.Match[str]]]:
    found: list[tuple[int, int, PatternDef, re.Match[str]]] = []
    for pattern in patterns:
        for match in pattern.regex.finditer(joined):
            start, end = match.start(), match.end()
            if pattern_skipped(start, end, mapping):
                continue
            found.append((start, end, pattern, match))
    return found


def pick_pattern_non_overlapping(
    candidates: Sequence[tuple[int, int, PatternDef, re.Match[str]]],
) -> list[tuple[int, int, PatternDef, re.Match[str]]]:
    ordered = sorted(
        candidates,
        key=lambda item: (item[0], -(item[1] - item[0]), -len(item[2].id)),
    )
    picked: list[tuple[int, int, PatternDef, re.Match[str]]] = []
    cursor = -1
    for start, end, pattern, match in ordered:
        if start < cursor:
            continue
        picked.append((start, end, pattern, match))
        cursor = end
    return picked


def scan_patterns(text: str, patterns: Sequence[PatternDef], path: str) -> list[PatternHit]:
    joined, mapping = join_visible(text)
    if not joined.strip() or not mapping:
        return []
    picked = pick_pattern_non_overlapping(collect_pattern_candidates(joined, patterns, mapping))
    raw_hits: list[tuple[int, int, PatternDef, re.Match[str], LineMap]] = []
    for start, end, pattern, match in picked:
        raw_hits.append((start, end, pattern, match, map_offset(start, mapping)))

    family_total: dict[str, int] = defaultdict(int)
    for _, _, pattern, _, _ in raw_hits:
        family_total[pattern.family] += 1
    family_index: dict[str, int] = defaultdict(int)

    hits: list[PatternHit] = []
    for start, end, pattern, match, loc in raw_hits:
        family_index[pattern.family] += 1
        index = family_index[pattern.family]
        count = family_total[pattern.family]
        x = (match.group(pattern.x_group) or "").strip()
        y = (match.group(pattern.y_group) or "").strip()
        matched = re.sub(r"\s+", "", match.group(0).strip())
        col = start - loc.offset + 1
        if col < 1:
            col = 1
        hits.append(
            PatternHit(
                path=path,
                line=loc.line_no,
                col=col,
                pattern_id=pattern.id,
                family=pattern.family,
                matched=matched,
                x=x,
                y=y,
                severity=pattern.severity,
                replacements=pattern.replacements,
                note=pattern.note,
                keep_if=pattern.keep_if,
                excerpt=excerpt_around(loc.line, max(0, start - loc.offset), max(0, end - loc.offset)),
                index=index,
                count=count,
                soft_limit=pattern.soft_limit,
                over_limit=index > pattern.soft_limit,
            )
        )
    return hits


def pattern_summary(hits: Sequence[PatternHit]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for hit in hits:
        item = grouped.setdefault(
            hit.family,
            {
                "family": hit.family,
                "count": hit.count,
                "soft_limit": hit.soft_limit,
                "over_limit": hit.count > hit.soft_limit,
            },
        )
        item["soft_limit"] = min(int(item["soft_limit"]), hit.soft_limit)
        item["over_limit"] = bool(item["over_limit"]) or hit.count > int(item["soft_limit"])
    return list(grouped.values())


def format_term_hits(hits: Sequence[Hit]) -> str:
    blocks: list[str] = []
    for hit in hits:
        reps = " / ".join(hit.replacements) if hit.replacements else "(删或改写成具体说法)"
        lines = [
            f"{hit.path}:{hit.line}:{hit.col}: {hit.matched}  [{hit.severity}/{hit.category}]",
            f"  词条: {hit.term}",
            f"  建议: {reps}",
        ]
        if hit.note:
            lines.append(f"  说明: {hit.note}")
        if hit.keep_if:
            lines.append(f"  可留: {hit.keep_if}")
        lines.append(f"  上下文: {hit.excerpt}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def format_pattern_hits(hits: Sequence[PatternHit]) -> str:
    if not hits:
        return ""
    header_bits: list[str] = []
    for item in pattern_summary(hits):
        mark = "  [超限]" if item["over_limit"] else ""
        header_bits.append(f"{item['family']} {item['count']} 次 / 软上限 {item['soft_limit']}{mark}")
    blocks = ["句式: " + "；".join(header_bits)]
    for hit in hits:
        reps = " / ".join(hit.replacements) if hit.replacements else "直接写 Y"
        over = "  [超限，默认再砍]" if hit.over_limit else ""
        lines = [
            f"{hit.path}:{hit.line}:{hit.col}: {hit.matched}  [{hit.severity}/{hit.family}]{over}",
            f"  反例 X: {hit.x}",
            f"  正句 Y: {hit.y}",
            f"  评估: X 是否是读者此刻真会以为的对立说法？若不是，或 X 与 Y 无必然对立，删掉「不是 X」，直接写 Y。",
            f"  建议: {reps}",
            f"  次数: {hit.index}/{hit.soft_limit}（本篇 {hit.family} 共 {hit.count} 次）",
        ]
        if hit.note:
            lines.append(f"  说明: {hit.note}")
        if hit.keep_if:
            lines.append(f"  可留: {hit.keep_if}")
        lines.append(f"  上下文: {hit.excerpt}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def format_human(term_hits: Sequence[Hit], pattern_hits: Sequence[PatternHit]) -> str:
    parts: list[str] = []
    if term_hits:
        parts.append(format_term_hits(term_hits))
    if pattern_hits:
        parts.append(format_pattern_hits(pattern_hits))
    return "\n\n".join(parts)


def read_input(path: Path | None, text_arg: str | None, use_stdin: bool) -> tuple[str, str]:
    if text_arg is not None:
        return text_arg, "-"
    if use_stdin:
        return sys.stdin.read(), "-"
    assert path is not None
    return path.read_text(encoding="utf-8"), str(path)


def self_test(terms: Sequence[Term], patterns: Sequence[PatternDef]) -> int:
    term_cases: list[tuple[str, list[str], str]] = [
        ("以用户调研为抓手推进产品", ["以用户调研为抓手"], "regex 抓手骨架"),
        ("把赋能写进方案", ["赋能"], "literal 赋能"),
        ("形成闭环之后再复盘", ["形成闭环", "复盘"], "长词优先于闭环"),
        ("这里有`抓手`这个词", [], "行内代码跳过"),
        ("见 https://example.com/抓手 说明", [], "URL 跳过"),
        ("```\n赋能\n```\n正文干净", [], "围栏代码跳过"),
        ("今天把笔记写完了。", [], "干净文本"),
        ("飞机落地了", ["落地"], "flag 落地"),
        ("对齐认知之后再做", ["对齐认知"], "对齐认知 优先于 对齐"),
    ]
    failed = 0
    for source, expected, label in term_cases:
        hits = scan_terms(source, terms, "-")
        got = [hit.matched for hit in hits]
        if got != expected:
            print(f"FAIL term {label}: expected {expected!r}, got {got!r}", file=sys.stderr)
            failed += 1
        else:
            print(f"ok   term {label}")

    pattern_cases: list[tuple[str, list[tuple[str, str, str]], str]] = [
        (
            "这不是技术问题，而是管理问题。",
            [("not-but", "技术问题", "管理问题")],
            "不是/而是",
        ),
        (
            "这里的「关闭」不是杀进程，而是断开连接。",
            [("not-but", "杀进程", "断开连接")],
            "可留的消歧也要标出",
        ),
        ("是不是技术问题", [], "是不是 不误伤"),
        (
            "文献不是一堆文件，而是工作材料。核心不是收藏，而是继续用。",
            [
                ("not-but", "一堆文件", "工作材料"),
                ("not-but", "收藏", "继续用"),
            ],
            "同篇两次，第二次超限",
        ),
        (
            "这不仅仅是产品，更是一种信念。",
            [("not-just", "产品", "一种信念")],
            "不仅仅是/更是",
        ),
        (
            "与其继续讨论，不如先写一版。",
            [("rather-than", "继续讨论", "先写一版")],
            "与其/不如",
        ),
        ("今天把笔记写完了。", [], "无句式"),
        (
            "正文有`不是x，而是y`这个例子",
            [],
            "行内代码跳过句式",
        ),
        (
            "不是技术问题，\n而是管理问题。",
            [("not-but", "技术问题", "管理问题")],
            "跨行不是/而是",
        ),
    ]
    for source, expected, label in pattern_cases:
        hits = scan_patterns(source, patterns, "-")
        got = [(hit.pattern_id, hit.x, hit.y) for hit in hits]
        if got != expected:
            print(f"FAIL pattern {label}: expected {expected!r}, got {got!r}", file=sys.stderr)
            failed += 1
            continue
        if label == "同篇两次，第二次超限":
            if not hits[-1].over_limit or hits[0].over_limit or hits[0].count != 2:
                print(
                    f"FAIL pattern {label}: over_limit flags {[(h.index, h.over_limit, h.count) for h in hits]!r}",
                    file=sys.stderr,
                )
                failed += 1
                continue
        print(f"ok   pattern {label}")

    if failed:
        print(f"{failed} failed", file=sys.stderr)
        return 1
    print("self-test ok")
    return 0


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="files to scan")
    parser.add_argument("--text", help="scan this string instead of files")
    parser.add_argument("--stdin", action="store_true", help="scan stdin")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON)
    parser.add_argument("--patterns", type=Path, default=DEFAULT_PATTERNS)
    parser.add_argument("--severity", choices=("ban", "flag"), help="only report this severity")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        terms = load_terms(args.lexicon)
        patterns = load_patterns(args.patterns)
    except (OSError, ValueError) as exc:
        print(f"data error: {exc}", file=sys.stderr)
        return 2

    if args.self_test:
        return self_test(terms, patterns)

    sources: list[tuple[str, str]] = []
    if args.text is not None:
        sources.append(read_input(None, args.text, False))
    elif args.stdin:
        sources.append(read_input(None, None, True))
    elif args.paths:
        for path in args.paths:
            if not path.is_file():
                print(f"not a file: {path}", file=sys.stderr)
                return 2
            sources.append(read_input(path, None, False))
    else:
        print("give --text, --stdin, --self-test, or file paths", file=sys.stderr)
        return 2

    term_hits: list[Hit] = []
    pattern_hits: list[PatternHit] = []
    for text, label in sources:
        term_hits.extend(scan_terms(text, terms, label))
        pattern_hits.extend(scan_patterns(text, patterns, label))
    if args.severity:
        term_hits = [hit for hit in term_hits if hit.severity == args.severity]
        pattern_hits = [hit for hit in pattern_hits if hit.severity == args.severity]

    payload = {
        "hits": [hit.as_dict() for hit in term_hits],
        "patterns": [hit.as_dict() for hit in pattern_hits],
        "pattern_summary": pattern_summary(pattern_hits),
    }

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif term_hits or pattern_hits:
        print(format_human(term_hits, pattern_hits))
        extra = []
        if term_hits:
            extra.append(f"{len(term_hits)} 词")
        if pattern_hits:
            extra.append(f"{len(pattern_hits)} 句式")
        print(f"\n{', '.join(extra)}")
    else:
        print("ok")

    return 1 if term_hits or pattern_hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
