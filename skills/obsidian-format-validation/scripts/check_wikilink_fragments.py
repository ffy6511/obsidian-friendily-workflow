#!/usr/bin/env python3
# This script is bundled with the obsidian-format-validation skill.
"""Report Obsidian wikilinks whose heading fragment cannot be resolved.

Examples:
  python3 .agents/skills/obsidian-format-validation/scripts/check_wikilink_fragments.py
  python3 .agents/skills/obsidian-format-validation/scripts/check_wikilink_fragments.py inbox/csdiy

The scan is read-only.  It checks links such as ``[[#Heading]]`` and
``[[some/note#Heading|label]]`` while ignoring fenced code blocks.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Iterable, List, Optional, Sequence, Set, Tuple


WIKILINK_RE = re.compile(r"!?\[\[([^\]\n]+)\]\]")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
BLOCK_ID_RE = re.compile(r"(?:^|\s)\^([A-Za-z0-9-]+)[ \t]*$")
NUMBER_PREFIX_RE = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?)[ \t]+")
SKIP_DIRS = {".agents", ".git", ".obsidian", "node_modules", ".trash"}


@dataclass(frozen=True)
class Finding:
    source: Path
    line: int
    link: str
    target: str
    fragment: str
    reason: str
    candidates: Tuple[str, ...]


def visible_lines(path: Path) -> Iterable[Tuple[int, str]]:
    """Yield Markdown lines outside fenced code blocks."""
    in_fence = False
    fence_marker = ""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if not in_fence:
                in_fence, fence_marker = True, token[0]
            elif token[0] == fence_marker:
                in_fence = False
            continue
        if not in_fence:
            yield number, line


def headings(path: Path) -> Set[str]:
    result: Set[str] = set()
    for _, line in visible_lines(path):
        match = HEADING_RE.match(line)
        if match:
            result.add(normalize(match.group(1)))
    return result


def block_ids(path: Path) -> Set[str]:
    """Return Obsidian block IDs, such as ``^summary`` at a block's end."""
    result: Set[str] = set()
    for _, line in visible_lines(path):
        match = BLOCK_ID_RE.search(line)
        if match:
            result.add(match.group(1).casefold())
    return result


def normalize(value: str) -> str:
    """Approximate Obsidian's case-insensitive heading comparison."""
    return " ".join(value.replace("\\", "").split()).casefold()


def split_alias(value: str) -> str:
    return re.split(r"(?<!\\)\|", value, maxsplit=1)[0].strip()


def is_template_link(value: str) -> bool:
    """Do not treat instructional placeholders as links to validate."""
    return "..." in value or "<" in value or ">" in value


def markdown_files(root: Path, scopes: Sequence[Path]) -> List[Path]:
    files: List[Path] = []
    for scope in scopes:
        absolute = (root / scope).resolve() if not scope.is_absolute() else scope.resolve()
        if not absolute.exists():
            raise FileNotFoundError(scope)
        candidates = [absolute] if absolute.is_file() else absolute.rglob("*.md")
        for candidate in candidates:
            if candidate.suffix != ".md" or any(part in SKIP_DIRS for part in candidate.parts):
                continue
            files.append(candidate)
    return sorted(set(files))


def resolve_note(
    note: str, source: Path, root: Path, by_stem: DefaultDict[str, List[Path]]
) -> Optional[Path]:
    """Resolve a wikilink target to a Markdown file.

    Obsidian accepts three equally-valid path styles, and we resolve all of
    them here without preference for repair: shortest unique name
    (``[[Index]]``), relative (``[[../projects/foo/Index]]``), and vault-absolute
    (``[[projects/foo/Index]]``). The validator must accept all three; do not
    rewrite a working link between forms.
    """
    note = note.strip().removesuffix(".md")
    if not note:
        return source

    candidates = [source.parent / note, root / note]
    for candidate in candidates:
        markdown = candidate.with_suffix(".md")
        if markdown.is_file():
            return markdown

    matches = by_stem.get(note.casefold(), [])
    return matches[0] if len(matches) == 1 else None


def numbered_variants(fragment: str, target_headings: Set[str]) -> Tuple[str, ...]:
    fragment_key = normalize(fragment)
    candidates = [
        heading
        for heading in target_headings
        if normalize(NUMBER_PREFIX_RE.sub("", heading)) == fragment_key
    ]
    return tuple(sorted(candidates))


def check(root: Path, files: Sequence[Path]) -> List[Finding]:
    all_files = markdown_files(root, [Path(".")])
    by_stem: DefaultDict[str, List[Path]] = defaultdict(list)
    for path in all_files:
        by_stem[path.stem.casefold()].append(path)

    heading_cache = {path: headings(path) for path in all_files}
    block_cache = {path: block_ids(path) for path in all_files}
    findings: List[Finding] = []
    for source in files:
        for line_number, line in visible_lines(source):
            for match in WIKILINK_RE.finditer(line):
                link = match.group(1)
                destination = split_alias(link)
                if is_template_link(destination):
                    continue
                if "#" not in destination:
                    continue
                note, fragment = destination.split("#", maxsplit=1)
                fragment = fragment.strip()
                if not fragment:
                    continue  # A link to a note's top is valid.

                target = resolve_note(note, source, root, by_stem)
                if target is None:
                    findings.append(
                        Finding(source, line_number, link, note or str(source), fragment,
                                "目标笔记不存在或名称不唯一", ())
                    )
                    continue

                if fragment.startswith("^"):
                    if fragment[1:].casefold() in block_cache[target]:
                        continue
                    findings.append(
                        Finding(source, line_number, link, str(target.relative_to(root)), fragment,
                                "目标块 ID 不存在", ())
                    )
                    continue

                target_headings = heading_cache[target]
                if normalize(fragment) in target_headings:
                    continue
                readable_headings = headings_display(target)
                findings.append(
                    Finding(
                        source, line_number, link, str(target.relative_to(root)), fragment,
                        "目标标题不存在",
                        numbered_variants(fragment, readable_headings),
                    )
                )
    return findings


def headings_display(path: Path) -> Set[str]:
    result: Set[str] = set()
    for _, line in visible_lines(path):
        match = HEADING_RE.match(line)
        if match:
            result.add(match.group(1))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*", type=Path, default=[Path(".")],
        help="要扫描的文件或目录，默认整个 vault",
    )
    args = parser.parse_args()
    root = Path.cwd().resolve()
    try:
        files = markdown_files(root, args.paths)
    except FileNotFoundError as error:
        print(f"找不到扫描路径: {error}", file=sys.stderr)
        return 2

    findings = check(root, files)
    for finding in findings:
        source = finding.source.relative_to(root)
        print(f"{source}:{finding.line}: [[{finding.link}]]")
        print(f"  {finding.reason}: {finding.target}#{finding.fragment}")
        if finding.candidates:
            print(f"  可能是自动编号后的标题: {', '.join(finding.candidates)}")

    print(f"检查 {len(files)} 个 Markdown 文件；发现 {len(findings)} 个失效标题双链。")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
