#!/usr/bin/env python3
"""Validate an Obsidian-friendly papers workspace."""

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


FENCE_RE = re.compile(r"(^|\n)```.*?(\n```|$)", re.S)
WIKILINK_RE = re.compile(r"(!?)\[\[([^\]\n]+)\]\]")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")
MD_IMAGE_RE = re.compile(r"!\[[^\]\n]*\]\(([^)\n]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


@dataclass
class Issue:
    severity: str
    path: Path
    message: str


def strip_fenced_code(text):
    return FENCE_RE.sub("\n", text)


def split_unescaped_pipe(value):
    value = value.replace("\\|", "|")
    escaped = False
    for i, char in enumerate(value):
        if char == "\\":
            escaped = not escaped
            continue
        if char == "|" and not escaped:
            return value[:i], value[i + 1 :]
        escaped = False
    return value, ""


def split_target_fragment(target):
    if "#" not in target:
        return target, ""
    base, fragment = target.split("#", 1)
    return base, urllib.parse.unquote(fragment).strip()


def is_external_target(target):
    lower = target.lower()
    return (
        "://" in lower
        or lower.startswith("mailto:")
        or lower.startswith("tel:")
        or lower.startswith("obsidian:")
        or lower.startswith("data:")
    )


def md_link_target(raw_target):
    target = raw_target.strip()
    if not target:
        return ""
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return urllib.parse.unquote(target)


def is_placeholder_target(target):
    return "..." in target or "<" in target or ">" in target


def candidate_paths(base_dir, vault_root, papers_root, target):
    target = target.strip()
    if not target:
        return []
    target = target.lstrip("/")
    raw = Path(target)
    candidates = []
    if target.startswith("papers/"):
        candidates.append(vault_root / raw)
    elif target.startswith(("library/", "projects/")):
        candidates.append(papers_root / raw)
    else:
        candidates.append(base_dir / raw)
        candidates.append(vault_root / raw)
        candidates.append(papers_root / raw)
    expanded = []
    for candidate in candidates:
        expanded.append(candidate)
        if candidate.suffix == "":
            expanded.append(candidate.with_suffix(".md"))
    return expanded


def build_stem_index(markdown_files):
    index = {}
    for path in markdown_files:
        index.setdefault(path.stem, []).append(path)
    return index


def resolve_target(source_file, vault_root, papers_root, stem_index, target):
    base, fragment = split_target_fragment(target)
    if not base:
        return source_file, fragment
    for candidate in candidate_paths(source_file.parent, vault_root, papers_root, base):
        if candidate.exists():
            return candidate.resolve(), fragment
    if "/" not in base and base in stem_index and len(stem_index[base]) == 1:
        return stem_index[base][0].resolve(), fragment
    return None, fragment


def frontmatter_fields(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def heading_set(text):
    return {match.group(2).strip() for match in HEADING_RE.finditer(text)}


def has_block_id(text, block_id):
    return re.search(rf"(?<!\S)\^{re.escape(block_id)}(?!\S)", text) is not None


def check_fragment(target_file, fragment, source_file, issues):
    if not fragment:
        return
    text = target_file.read_text(encoding="utf-8", errors="ignore")
    if fragment.startswith("^"):
        if not has_block_id(text, fragment[1:]):
            issues.append(Issue("error", source_file, f"missing block id #{fragment} in {target_file}"))
        return
    if fragment not in heading_set(text):
        issues.append(Issue("error", source_file, f"missing heading #{fragment} in {target_file}"))


def check_markdown_links(path, text, vault_root, papers_root, stem_index, issues):
    body = strip_fenced_code(text)
    for match in MD_LINK_RE.finditer(body):
        raw_target = md_link_target(match.group(1))
        if (
            not raw_target
            or raw_target.startswith("#")
            or is_external_target(raw_target)
            or is_placeholder_target(raw_target)
        ):
            continue
        base, fragment = split_target_fragment(raw_target)
        resolved, fragment = resolve_target(path, vault_root, papers_root, stem_index, raw_target)
        if resolved is None:
            issues.append(Issue("error", path, f"broken Markdown link: {raw_target}"))
        else:
            check_fragment(resolved, fragment, path, issues)


def check_markdown_images(path, text, check_remote_images, image_cache, issues):
    body = strip_fenced_code(text)
    for match in MD_IMAGE_RE.finditer(body):
        raw_target = md_link_target(match.group(1))
        if not raw_target.startswith("https://"):
            issues.append(Issue("error", path, f"reading-note image must use a public https URL: {raw_target}"))
            continue
        if not check_remote_images or raw_target in image_cache:
            continue
        try:
            request = urllib.request.Request(raw_target, headers={"User-Agent": "paper-md-ingest-validator/0.1"})
            with urllib.request.urlopen(request, timeout=20) as response:
                content_type = response.headers.get("content-type", "").lower()
                response.read(1)
            image_cache[raw_target] = content_type
            if not content_type.startswith("image/"):
                issues.append(Issue("error", path, f"remote image is not image/* ({content_type or 'missing content type'}): {raw_target}"))
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            issues.append(Issue("error", path, f"remote image check failed: {raw_target} ({error})"))


def check_wikilinks(path, text, vault_root, papers_root, stem_index, issues):
    body = strip_fenced_code(text)
    for match in WIKILINK_RE.finditer(body):
        raw_target, _alias = split_unescaped_pipe(match.group(2))
        target = raw_target.strip()
        if not target or is_external_target(target) or is_placeholder_target(target):
            continue
        resolved, fragment = resolve_target(path, vault_root, papers_root, stem_index, target)
        if resolved is None:
            issues.append(Issue("error", path, f"broken Obsidian link: [[{target}]]"))
        else:
            check_fragment(resolved, fragment, path, issues)


def check_library(papers_root, issues):
    library_root = papers_root / "library"
    if not library_root.exists():
        issues.append(Issue("error", papers_root, "missing library/ directory"))
        return
    for paper_dir in sorted(p for p in library_root.iterdir() if p.is_dir()):
        paper_md = paper_dir / "paper.md"
        if not paper_md.exists():
            issues.append(Issue("error", paper_dir, "missing paper.md"))
        note_files = sorted(p for p in paper_dir.glob("*.md") if p.name != "paper.md")
        if not note_files:
            issues.append(Issue("error", paper_dir, "missing reading note .md file"))
            continue
        for note_file in note_files:
            text = note_file.read_text(encoding="utf-8", errors="ignore")
            fields = frontmatter_fields(text)
            if not fields.get("id"):
                issues.append(Issue("error", note_file, "frontmatter missing id"))
            if not fields.get("source"):
                issues.append(Issue("error", note_file, "frontmatter missing source"))


def check_inventory(papers_root, issues):
    papers_md = papers_root / "PAPERS.md"
    if not papers_md.exists():
        issues.append(Issue("error", papers_root, "missing PAPERS.md"))
        return
    text = papers_md.read_text(encoding="utf-8", errors="ignore")
    library_root = papers_root / "library"
    if not library_root.exists():
        return
    for paper_dir in sorted(p for p in library_root.iterdir() if p.is_dir()):
        marker = f"library/{paper_dir.name}/"
        if marker not in text:
            issues.append(Issue("error", papers_md, f"library item not indexed: {paper_dir.name}"))


def validate(papers_root, check_remote_images=False):
    papers_root = papers_root.resolve()
    vault_root = papers_root.parent
    issues = []
    markdown_files = sorted(p.resolve() for p in papers_root.rglob("*.md"))
    stem_index = build_stem_index(markdown_files)
    image_cache = {}

    check_library(papers_root, issues)
    check_inventory(papers_root, issues)
    for path in markdown_files:
        if path.name == "paper.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        check_markdown_links(path, text, vault_root, papers_root, stem_index, issues)
        check_markdown_images(path, text, check_remote_images, image_cache, issues)
        check_wikilinks(path, text, vault_root, papers_root, stem_index, issues)
    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate papers workspace links and required files.")
    parser.add_argument("--papers-root", default="papers", help="Path to the papers workspace")
    parser.add_argument("--check-remote-images", action="store_true", help="Fetch reading-note images and require image/* responses")
    args = parser.parse_args()

    papers_root = Path(args.papers_root)
    issues = validate(papers_root, check_remote_images=args.check_remote_images)
    errors = [issue for issue in issues if issue.severity == "error"]
    for issue in issues:
        print(f"{issue.severity.upper()}: {issue.path}: {issue.message}", file=sys.stderr)
    if errors:
        print(f"\nValidation failed: {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validation passed: {papers_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
