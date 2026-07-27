# Obsidian Literature Notes

Use this reference when creating or updating `papers/projects/*.md` or `papers/topics/*.md`, writing Obsidian links to paper notes, or deciding how a paper reading-note `.md` file should be referenced from a map or index.

This workspace treats Obsidian features as part of the literature workflow, not as decoration. Use wikilinks to express relationships, embeds to surface short summaries, and backlinks to let a paper reveal which projects cite it.

## Wikilinks

Use wikilinks for files inside the vault:

```markdown
[[papers/library/<paper-id>/NOTES]]
[[papers/library/<paper-id>/<Short Title>]]
[[papers/library/<paper-id>/NOTES|<short human title>]]
[[papers/library/<paper-id>/<Short Title>#<heading>]]
```

Use aliases for readability. The file can remain `NOTES.md`, or it can use a concise short title filename. The project map should display a paper title or short name:

```markdown
[[papers/library/2408.04682/ToolSandbox|ToolSandbox]]
```

Use ordinary Markdown links only for external URLs:

```markdown
[arXiv HTML](https://arxiv.org/html/2408.04682)
```

## Embeds

Prefix a wikilink with `!` to embed note content inline:

```markdown
![[papers/library/<paper-id>/<reading-note>#^summary]]
```

Embed only compact sections in project maps. The normal target is the summary block of the reading note.

Use a fixed `^summary` block id at the end of the last sentence in the summary section. The project map already includes the file path and paper title, so paper-specific block ids are unnecessary.

```markdown
指出论文处理的领域痛点，以及为什么值得关注。 ^summary

- [[papers/library/2507.02825/Best Practices for Agentic Benchmarks|Agentic Benchmark Checklist]] - Use this first to define evaluation rigor![[papers/library/2507.02825/Best Practices for Agentic Benchmarks#^summary]]
```

Do not embed full `paper.md` into a project map.

## Paper Note Pattern

Each paper directory has one canonical Obsidian reading note:

```text
papers/library/<paper-id>/<reading-note>.md
papers/library/<paper-id>/paper.md
```

The reading note is for human and agent orientation. `paper.md` is the fuller converted paper body. `NOTES.md` is the default filename, but a concise paper-title filename is acceptable when it helps browsing. After renaming a note, update project maps and `PAPERS.md`, then run the validator.

Recommended frontmatter:

```yaml
---
id: <paper-id>
title: '<paper title>'
year: <year>
status: inbox|to-read|reading|key|done
source: '<official html/pdf/source url>'
tags:
  - <tag>
---
```

`source` should point to the best official human-readable source, usually arXiv HTML when available. This makes it easy to open the original source for browser annotation and close reading.

## Key Figure Pattern

`paper.md` keeps the full converted text and any usable public HTML figure links. The canonical reading note should promote only the one to three figures that make its explanation easier to follow; it is not a gallery or a second copy of the paper.

Place selected figures after `## 方法` / `## Method` and before `## 实验：证据如何支撑结论` / `## Experiments (How They Prove It)`:

```markdown
## 关键图示

![图 2：失败模式到 harness 适配的映射](https://arxiv.org/html/<paper-id>v1/x2.png)

图 2：作者把轨迹中的能力缺口连到 context、tool、agent-loop 三类改造。
阅读提示：先按“失败信号 → 适配层 → 可测结果”核对这张图与正文是否一致。
```

Use a direct public `https://` image URL from official HTML whenever possible. If an older paper has no official HTML, a stable public HTML rendering mirror is acceptable only when its image response has been checked and the caption identifies it as a mirror. Do not use base64/data URLs, local paths, screenshots, logos, search thumbnails, or decorative images. Keep the original figure number/caption and add one sentence that tells the reader why the figure belongs in the note. If no figure is both available and explanatory, omit this section.

## Project Map Pattern

Each project map lives under:

```text
papers/projects/<project>.md
```

Project maps are reading maps, not duplicate paper notes. They should contain:

- project goal
- paired roadmap canvas embedded near the top
- search framing when papers were discovered from a topic
- `主题聚合`: paper groups by problem, module, decision, or reading stage
- `推荐阅读路径`: ordered wikilinks with one-line reasons, placed after `主题聚合`
- inline block embeds for every paper listed under `主题聚合`
- `阅读关注点` only when useful, for close-reading cues, open questions, or follow-up paper gaps

Example:

```markdown
# <Project Title>

## Project Goal

...

## Roadmap

![[papers/projects/<project> roadmap.canvas]]

## 主题聚合

### Evaluation Rigor

- [[papers/library/2507.02825/Best Practices for Agentic Benchmarks|Agentic Benchmark Checklist]] - Use this first to define evaluation rigor![[papers/library/2507.02825/Best Practices for Agentic Benchmarks#^summary]]

### Stateful Sandboxes

- [[papers/library/2408.04682/ToolSandbox|ToolSandbox]] - Read next for stateful sandbox design![[papers/library/2408.04682/ToolSandbox#^summary]]

## 推荐阅读路径

1. [[papers/library/2507.02825/Best Practices for Agentic Benchmarks|Agentic Benchmark Checklist]] - Use this first to define evaluation rigor.
2. [[papers/library/2408.04682/ToolSandbox|ToolSandbox]] - Read next for stateful sandbox design.
```

## Project Roadmap Canvas

Create one paired `.canvas` roadmap for each project map:

```text
papers/projects/<project> roadmap.canvas
```

Use this visual convention:

- Center spine: orange `#f6a800` nodes for the `主题聚合` themes, not individual papers.
- Side branches: blue `#b9dcff` nodes for concrete papers, linked with vault-relative wikilinks to canonical reading notes.
- Branch lines: blue `#2f7de1`.
- Third level: every paper node should have a one-sentence project-role explanation node, pale blue `#eaf4ff`.
- Explanation edges: connect paper nodes to explanation nodes with gray `#9ca3af`, no arrow (`toEnd: "none"`), and horizontal center alignment.
- Neutral top blocks: project goal, reading instructions, or scope notes.
- Node width: keep text legible. Increase width for long Chinese or mixed Chinese/English labels; do not leave clipped text.

## Backlinks

Backlinks are the reason to prefer wikilinks over plain Markdown links for internal notes. When a project map links to a paper note, Obsidian can show that project in the paper note's backlinks.

This matters because one paper may support multiple projects or research questions. Do not force this relationship into directory structure by copying paper notes into project folders.

## Topic Index Pattern

Use `papers/topics/<topic>.md` for a stable grouping that does not belong to one project, such as classics, a method family, or a benchmark category. A topic index is a navigation and curation surface, not a second library or a disguised project map.

Topic indexes should include:

- lightweight `topic-index` frontmatter;
- a concise statement of the shared concept and the selection boundary;
- canonical note wikilinks grouped by concept or reading dependency;
- optional inline `![[...#^summary]]` embeds for fast recall;
- a short reading path when order matters.

Do not create a roadmap canvas for a topic index, duplicate `paper.md`, or use ordinary Markdown links for canonical notes.

## Do Not

- Do not copy `paper.md` into project folders.
- Do not use ordinary Markdown links for internal paper notes.
- Do not embed long sections or full paper bodies in project maps.
- Do not create a project map just to hold a project-independent topic index.
- Do not turn a canonical note into a figure dump; include only figures that explain a method, protocol, or result, and retain their public source URL.
- Do not hard-code one language for headings; use the user's working language and link to the actual heading present in the note.
- Do not rename a note without updating every wikilink, embed, and `PAPERS.md` entry, then running `scripts/validate_papers_workspace.py`.
