---
name: code-walkthrough-site
description: >
  Build a self-contained progressive code-walkthrough website: left-side teaching
  prose, right-side IDE that reveals code as the reader scrolls through checkpoints.
  Use when the user wants a pi-from-scratch-style lesson site, scroll-linked code
  reveal, progressive codebase explainer, left-text/right-code tutorial, or a
  one-command local preview of a topic (optionally with code references). Not for
  generic marketing landings or plain docs sites without progressive code.
---

# Code Walkthrough Site

## Goal

From a **topic** (and optional code references), produce a **self-contained** website:

- Left: scrollable markdown lesson
- Right: file-tree + editor; code **grows** at each `<!-- checkpoint: id -->`
- One command to preview locally; no dependency on the original repo at runtime

## When producing output

1. Read [references/content-schema.md](references/content-schema.md) for the JSON shape and checkpoint rules.
2. Read [references/writing-guide.md](references/writing-guide.md) for narrative + progressive-code technique.
3. Author `content.json` (all prose + full code snapshots inlined).
4. Validate, scaffold, launch.

## Workflow

### 1. Collect inputs

- Topic / learning goal
- Optional: paths, repos, snippets, or pasted final code
- Language preference (match the user)
- Output directory (default: `./walkthrough-<slug>/` under the current workspace)

If code is missing for a code-heavy topic, draft a **minimal complete** teaching codebase (small, correct, focused)—do not invent large fake systems.

### 2. Plan checkpoints

- Order by data flow or dependency, not filesystem order.
- 6–20 stages for a short lesson; each stage = one idea.
- Plan **monotonic** file snapshots (later stages only insert lines). See schema.

### 3. Write content JSON

Required structure (abbreviated):

```json
{
  "site": { "title": "...", "brand": "...", "brandMark": "◇", "lang": "zh-CN", "repoLabel": "demo /" },
  "lessons": [{
    "id": "main",
    "title": "...",
    "markdown": "<!-- checkpoint: overview -->\n\n...",
    "initialRepo": {},
    "checkpoints": [
      { "id": "overview", "label": "空仓库", "file": "src/a.ts", "repo": {} },
      { "id": "types", "label": "类型", "file": "src/a.ts", "repo": { "src/a.ts": "..." } }
    ]
  }]
}
```

Hard rules:

- Every checkpoint `id` ↔ exactly one `<!-- checkpoint: id -->` in markdown.
- `checkpoint.repo` is a **full** path→text map at that stage (not a diff).
- Prefer insert-only growth; use `focus: [start, end]` when a highlight must not rely on LCS.
- Bake figures into the site (`figures/`) if used.

### 4. Validate

```bash
SKILL_DIR="<path-to-code-walkthrough-site>"
python3 "$SKILL_DIR/scripts/validate_content.py" /path/to/content.json
```

Fix all errors before scaffold.

### 5. Scaffold

```bash
python3 "$SKILL_DIR/scripts/scaffold_site.py" \
  --content /path/to/content.json \
  --out /path/to/walkthrough-site \
  --force
```

Optional: `--figures /path/to/figures`.

The output is self-contained: `index.html`, `app.js`, `styles.css`, `content.js`, `vendor/`.

### 6. Launch (one command)

```bash
cd /path/to/walkthrough-site
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`. Same via `npm start` in the generated folder.

### 7. Scroll QA

Scroll top → bottom once: checkpoints fire, new lines animate, final stage complete, theme + lock work, mobile drawer works. See writing-guide checklist.

## Template

Runtime UI lives in [assets/template/](assets/template/) (static HTML/CSS/JS + vendored marked/hljs). Do not reimplement the reader unless the user asks for a different stack. Extend content via JSON only.

Example content: [assets/template/content.example.json](assets/template/content.example.json).

## Guardrails

- Self-contained content only — no runtime reads of the user’s monorepo.
- No secrets/API keys in snapshots.
- Do not pull in Next.js/TraceLab from pi-from-scratch; this skill’s default is the static progressive reader.
- Prefer one lesson unless the user asks for multi-chapter nav.
- After scaffold, tell the user the exact `cd` + server + URL commands.

## Scripts

| Script | Role |
| --- | --- |
| `scripts/validate_content.py` | Schema + anchor/repo consistency |
| `scripts/scaffold_site.py` | Copy template, embed `content.js`, write launch helpers |
