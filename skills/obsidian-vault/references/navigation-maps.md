# Navigation Maps

This reference defines the **abstract patterns** for how navigation maps link to canonical notes within a vault workspace. Domain skills provide their concrete content schemas; this reference covers the shared structure.

## Core principle

Navigation maps are **reading surfaces**, not content stores. They organize, synthesize, and guide — they never duplicate the canonical notes they link to. One canonical note (a paper reading note, a learning unit) lives in exactly one place; maps discover it through links and embeds.

## Wikilink + embed pattern

Every item listed in a navigation map should follow this shape:

```markdown
- [[<vault-relative-path-to-note>|<short display title>]] - <one-line reason>.![[<vault-relative-path-to-note>#<block-id>]]
```

- Use a wikilink with an alias for readability: `[[path/to/note|Short Title]]`.
- Append an inline block embed (`![[...#^block-id]]`) on the same bullet to surface a compact summary without duplicating text.
- Use a stable block id in the canonical note (e.g., `^summary`, `^guide`). The file path already identifies the item, so item-specific block ids are unnecessary.
- In group sections where inline embeds are required, every bullet must include `![[...#<block-id>]]` — it is not optional there.

## Ordinary Markdown links

Use `[](url)` links only for **external** URLs (arXiv, official docs, web pages). Use `[[wikilinks]]` for everything inside the vault. Mixing the two breaks Obsidian's rename tracking and backlinks.

## Backlinks

Backlinks are the reason to prefer wikilinks over plain Markdown links for internal notes. When a navigation map links to a canonical note, Obsidian automatically shows the map in that note's backlinks. This matters because one item may support multiple maps, projects, or research questions. Do not force these relationships into directory structure by copying notes into map folders.

## Map types

### Project maps (`projects/<project>.md`)

Project-specific reading maps for a group of related items. Should contain:

- Project goal.
- Paired roadmap canvas embedded near the top (see [Roadmap Canvas](roadmap-canvas.md)).
- Optional search framing (how items were discovered).
- Theme groups with inline block embeds for every listed item.
- A recommended reading path with ordered wikilinks and one-line reasons.
- Optional reading-focus notes for close-reading cues or open questions.

Project maps are created only when the request explicitly identifies that project. A topic or tag alone does not establish project ownership.

### Domain maps (`domains/<domain>/<title>.md`)

Domain-level entry points for a knowledge area (used by `learning-unit-ingest`). Should contain:

- Learning objectives.
- Paired roadmap canvas embedded near the top.
- A learning map with wikilinks + inline embeds for each unit.
- A recommended reading path.
- A concept index.

### Topic indexes (`topics/<topic>.md`)

Cross-project, long-lived groupings by shared concept — method families, benchmark categories, classics. Should contain:

- Lightweight `topic-index` frontmatter.
- A concise statement of the shared concept and selection boundary.
- Canonical note wikilinks grouped by concept or reading dependency.
- Optional inline `![[...#<block-id>]]` embeds for fast recall.
- A short reading path when order matters.

Topic indexes do **not** get a roadmap canvas. They are navigation and curation surfaces, not project maps.

## What navigation maps must NOT do

- Do not copy canonical note content or full-text into maps.
- Do not use ordinary Markdown links for internal notes.
- Do not embed long sections or full note bodies.
- Do not create a navigation map just to hold a project-independent topic index — use a topic index instead.
- Do not rename a canonical note without updating every wikilink, embed, and global-index entry that references it.
