---
name: obsidian-format-validation
description: Validate Obsidian Markdown formatting in this vault, with deterministic checks for heading-fragment and block-ID wikilinks. Use when editing, renaming, numbering, or reorganizing Markdown notes; when a wikilink does not resolve; or when the user asks to audit or repair note-link integrity.
---

# Obsidian Format Validation

## Workflow

1. Read the nearest `AGENTS.md` before changing notes.
2. Run the validator from the vault root. It is read-only and exits with status `1` when it finds errors.

   ```bash
   python3 .agents/skills/obsidian-format-validation/scripts/check_wikilink_fragments.py
   ```

   Limit the report to a file or folder when iterating:

   ```bash
   python3 .agents/skills/obsidian-format-validation/scripts/check_wikilink_fragments.py inbox/csdiy
   ```

3. Inspect every finding, fix only the affected Markdown content, then rerun the same command. Do not edit `.obsidian/`.
4. Hand off only after the selected scope has zero findings, unless the user explicitly accepts outstanding links.

## Validator Coverage

Use `scripts/check_wikilink_fragments.py` to validate Markdown wikilinks with a heading or block target:

- `[[#Heading]]` resolves against headings in the current note.
- `[[path/to/note#Heading|label]]` resolves against a target note.
- `[[path/to/note#^block-id]]` resolves against an Obsidian block ID.

Ignore fenced code blocks and instructional placeholders. Scan the whole vault to resolve targets even when the requested reporting scope is smaller.

Links without a `#` fragment (e.g. `[[projects/foo/Index|label]]`) are intentionally **not** validated by the script — a bare note link is correct as long as the note resolves. Do not invent problems the script does not report.

## Valid Wikilink Path Forms

Obsidian accepts three path styles inside `[[…]]`, and the validator resolves all three. **All are equally valid; never convert a link from one form to another.**

- **Shortest path** (when the file name is unique in the vault): `[[Index|label]]`
- **Relative path** (resolved from the current note's folder): `[[../../projects/foo/Index|label]]`
- **Vault-absolute path** (resolved from the vault root, no leading `/`): `[[projects/foo/Index|label]]`

A link like `[[projects/nl-benchmark-platform/Index|自然语言驱动的 Benchmark 测评平台]]` is correct vault-absolute syntax. Do **not** prepend `../`, `../../`, or any other relative prefix to "fix" it. The validator's `resolve_note` already tries `source.parent / note` and `root / note`, so if the script reports zero findings for a link, its path style is correct — leave it alone.

## Repair Rules

- Only act on links the validator actually flags. If `check_wikilink_fragments.py` reports a link as fine, do not rewrite it.
- Never convert a working link between shortest-path, relative-path, and vault-absolute forms. Path style is not a defect.
- Match heading fragments to the actual heading text, including any persisted number. For example, a target `## 1 Micrograd` needs `[[#1 Micrograd|Micrograd]]`.
- Prefer a stable block ID when headings are expected to be renumbered: add `^micrograd` to the intended target block, then use `[[#^micrograd|Micrograd]]`.
- Treat suggested auto-numbered headings as hints. Confirm the target semantically before changing a link.
- Do not rewrite a link merely because a target is ambiguous or absent; report it and ask for direction when no intended target is evident.

## Scope

This skill currently checks heading-fragment and block-ID wikilinks. It does not validate external URLs, ordinary Markdown links, aliases, YAML properties, or rendered layout.
