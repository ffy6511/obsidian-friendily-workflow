#!/usr/bin/env python3
"""Copy selected Obsidian notes and their local dependencies into Quartz content."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXCLUDED_DIRS = {".git", ".obsidian", ".agents", "node_modules", ".trash"}
DOCUMENT_SUFFIXES = {".md", ".canvas"}
WIKILINK_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")
FENCED_CODE_RE = re.compile(r"(^|\n)```.*?```", re.DOTALL)


@dataclass(frozen=True)
class Reference:
    raw: str
    via: str
    document: bool


@dataclass(frozen=True)
class Unresolved:
    source: Path
    reference: Reference


def _load_pref_roots() -> tuple[Path | None, Path | None, str]:
    """Load source/public roots from preferences.toml when present."""
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        from preferences import resolve_roots
    except ImportError:
        return None, None, "content"
    return resolve_roots()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            yield path


def strip_code_blocks(markdown: str) -> str:
    return FENCED_CODE_RE.sub("\n", markdown)


def clean_reference(value: str, *, wiki: bool) -> str | None:
    value = value.strip()
    if wiki:
        value = value.split("|", 1)[0].strip()
    else:
        value = value.strip("<>")
    value = value.split("#", 1)[0].split("^", 1)[0].split("?", 1)[0].strip()
    if not value or value.startswith(("/", "#", "mailto:", "data:")) or "://" in value:
        return None
    return value


def markdown_references(path: Path) -> list[Reference]:
    text = strip_code_blocks(path.read_text(encoding="utf-8"))
    refs: list[Reference] = []
    for _embed, raw in WIKILINK_RE.findall(text):
        value = clean_reference(raw, wiki=True)
        if value:
            refs.append(Reference(value, "wikilink", Path(value).suffix.lower() in DOCUMENT_SUFFIXES or not Path(value).suffix))
    for raw in MARKDOWN_LINK_RE.findall(text):
        value = clean_reference(raw, wiki=False)
        if value:
            refs.append(Reference(value, "markdown", Path(value).suffix.lower() in DOCUMENT_SUFFIXES))
    return refs


def canvas_references(path: Path) -> list[Reference]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"Invalid Canvas JSON: {path}") from error

    refs: list[Reference] = []

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "file" and isinstance(child, str):
                    target = clean_reference(child, wiki=True)
                    if target:
                        refs.append(Reference(target, "canvas", Path(target).suffix.lower() in DOCUMENT_SUFFIXES or not Path(target).suffix))
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    return refs


def references_for(path: Path) -> list[Reference]:
    if path.suffix.lower() == ".md":
        return markdown_references(path)
    if path.suffix.lower() == ".canvas":
        return canvas_references(path)
    return []


class Resolver:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.index: dict[str, set[Path]] = defaultdict(set)
        for file in iter_files(self.root):
            relative = file.relative_to(self.root).as_posix()
            self.index[relative].add(file)
            self.index[file.name].add(file)
            self.index[file.stem].add(file)
            if file.suffix.lower() in DOCUMENT_SUFFIXES:
                self.index[str(file.relative_to(self.root).with_suffix("")).replace("\\", "/")].add(file)

    def resolve(self, reference: str, current: Path) -> Path | None:
        candidates: list[Path] = []
        raw = Path(reference)
        names = [raw]
        if not raw.suffix:
            names.extend([Path(f"{reference}.md"), Path(f"{reference}.canvas")])

        for name in names:
            for candidate in (current.parent / name, self.root / name):
                if candidate.is_file() and is_within(candidate, self.root):
                    candidates.append(candidate.resolve())
        if candidates:
            return candidates[0]

        matches = self.index.get(reference, set())
        if len(matches) == 1:
            return next(iter(matches)).resolve()
        return None


def source_paths(items: list[str], source_root: Path) -> list[Path]:
    files: list[Path] = []
    for item in items:
        raw = Path(item).expanduser()
        candidate = raw.resolve() if raw.is_absolute() else (source_root / raw).resolve()
        if not candidate.exists() or not is_within(candidate, source_root):
            raise ValueError(f"Source is missing or outside the vault: {item}")
        if candidate.is_dir():
            files.extend(iter_files(candidate))
        elif candidate.is_file():
            files.append(candidate)
    return sorted(set(files))


def public_metadata(path: Path) -> list[str]:
    if path.suffix.lower() != ".md":
        return []
    head = path.read_text(encoding="utf-8").split("---", 2)
    if len(head) < 3 or not head[0].strip() == "":
        return []
    frontmatter = head[1]
    flags = []
    if re.search(r"^visibility:\s*private\s*$", frontmatter, re.MULTILINE):
        flags.append("visibility: private")
    if re.search(r"^\s*include:\s*false\s*$", frontmatter, re.MULTILINE):
        flags.append("public.include: false")
    return flags


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", nargs="+", required=True, help="Vault-relative source file(s) or folder(s)")
    parser.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="Private vault root (default: preferences.toml source_root)",
    )
    parser.add_argument(
        "--public-root",
        type=Path,
        default=None,
        help="Public Quartz repo root (default: preferences.toml public_root)",
    )
    parser.add_argument(
        "--content-subdir",
        default=None,
        help="Content directory under public root (default: preferences.toml content_subdir or 'content')",
    )
    parser.add_argument("--no-wikilinks", action="store_true", help="Do not follow wikilinks to note files")
    parser.add_argument("--allow-homepage-overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail when a local reference cannot be resolved")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pref_source, pref_public, pref_content = _load_pref_roots()

    source_raw = args.source_root or pref_source
    public_raw = args.public_root or pref_public
    content_subdir = (args.content_subdir or pref_content or "content").strip() or "content"

    if source_raw is None:
        raise ValueError(
            "source root not set. Copy preferences.example.toml to preferences.toml "
            "and set source_root, or pass --source-root."
        )
    if public_raw is None:
        raise ValueError(
            "public root not set. Copy preferences.example.toml to preferences.toml "
            "and set public_root, or pass --public-root."
        )

    source_root = Path(source_raw).expanduser().resolve()
    public_root = Path(public_raw).expanduser().resolve()
    content_root = public_root / content_subdir
    if not source_root.is_dir():
        raise ValueError(f"Source vault root does not exist: {source_root}")
    if not public_root.is_dir():
        raise ValueError(f"Public repository root does not exist: {public_root}")
    if not content_root.is_dir() and not args.dry_run:
        # content/ may be created by first copy; only require public root to exist
        pass

    resolver = Resolver(source_root)
    roots = source_paths(args.source, source_root)
    queue = deque(roots)
    selected: set[Path] = set()
    unresolved: set[Unresolved] = set()
    skipped: set[tuple[Path, str]] = set()

    while queue:
        current = queue.popleft().resolve()
        if current in selected:
            continue
        selected.add(current)
        for reference in references_for(current):
            resolved = resolver.resolve(reference.raw, current)
            if not resolved:
                unresolved.add(Unresolved(current, reference))
                continue
            if reference.document and reference.via == "wikilink" and args.no_wikilinks:
                skipped.add((current, reference.raw))
                continue
            queue.append(resolved)

    copied = []
    flagged = []
    for source in sorted(selected):
        relative = source.relative_to(source_root)
        destination = content_root / relative
        if relative == Path("index.md") and destination.exists() and not args.allow_homepage_overwrite:
            raise ValueError("Refusing to overwrite content/index.md; pass --allow-homepage-overwrite explicitly")
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        copied.append(relative.as_posix())
        metadata = public_metadata(source)
        if metadata:
            flagged.append((relative.as_posix(), ", ".join(metadata)))

    mode = "Dry run" if args.dry_run else "Synced"
    print(f"{mode}: {len(copied)} file(s)")
    for relative in copied:
        print(f"  + {relative}")
    if flagged:
        print("Private-marked files included:")
        for relative, metadata in flagged:
            print(f"  ! {relative} ({metadata})")
    if skipped:
        print("Skipped wikilinked documents:")
        for source, raw in sorted(skipped, key=lambda item: (str(item[0]), item[1])):
            print(f"  - {source.relative_to(source_root)} -> [[{raw}]]")
    if unresolved:
        print("Unresolved local references:")
        for item in sorted(unresolved, key=lambda entry: (str(entry.source), entry.reference.raw)):
            print(f"  ? {item.source.relative_to(source_root)} -> {item.reference.raw} ({item.reference.via})")
    return 2 if args.strict and unresolved else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
