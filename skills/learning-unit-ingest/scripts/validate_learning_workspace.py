#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


REQUIRED_UNIT_HEADINGS = ["## 学习资源", "## 学习导引", "## 知识总览", "## 我的笔记"]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def resolve_wikilink(root: Path, target: str) -> Path:
    path = target.split("#", 1)[0].split("|", 1)[0]
    if not path:
        return root
    candidate = root.parent / path
    if candidate.suffix:
        return candidate
    md = candidate.with_suffix(".md")
    if md.exists():
        return md
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning-root", default="learning")
    args = parser.parse_args()

    root = Path(args.learning_root)
    errors = []

    if not root.exists():
        errors.append(f"missing learning root: {root}")
    for rel in ["AGENTS.md", "LEARNING.md", "domains"]:
        if not (root / rel).exists():
            errors.append(f"missing {root / rel}")

    if not errors:
        for unit in sorted((root / "domains").glob("*/units/*.md")):
            text = unit.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            domain = unit.parents[1].name
            for key in ["title", "type", "domain", "status", "resource_type"]:
                if key not in fm or not fm[key]:
                    errors.append(f"{unit}: missing frontmatter field `{key}`")
            if ("source" not in fm or not fm["source"]) and ("sources" not in fm or not fm["sources"]):
                errors.append(f"{unit}: missing frontmatter field `source` or `sources`")
            if fm.get("type") != "learning-unit":
                errors.append(f"{unit}: type must be learning-unit")
            if fm.get("domain") != domain:
                errors.append(f"{unit}: domain frontmatter must match directory `{domain}`")
            if "<iframe" not in text:
                errors.append(f"{unit}: missing iframe embed")
            for heading in REQUIRED_UNIT_HEADINGS:
                if heading not in text:
                    errors.append(f"{unit}: missing `{heading}`")
            if "^guide" not in text:
                errors.append(f"{unit}: missing ^guide block id")

        for md in sorted((root / "domains").glob("*/*.md")):
            if "/units/" in md.as_posix():
                continue
            text = md.read_text(encoding="utf-8")
            for embed in re.findall(r"!\[\[([^\]]+)#\^guide\]\]", text):
                target = resolve_wikilink(root, embed)
                if not target.exists():
                    errors.append(f"{md}: guide embed target missing: {embed}")
                    continue
                target_text = target.read_text(encoding="utf-8")
                if "^guide" not in target_text:
                    errors.append(f"{md}: guide embed target has no ^guide: {embed}")
            for link in re.findall(r"\[\[([^\]]+)\]\]", text):
                target = resolve_wikilink(root, link)
                if target == root:
                    continue
                if not target.exists():
                    errors.append(f"{md}: wikilink target missing: {link}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
