# Papers Workspace Initialization

Use this reference when the user asks to create a literature workspace, when `papers/` does not exist, or when an existing `papers/` workspace is missing its basic files or directories.

The goal is to create a small, readable workspace that works for both humans and agents. Write the actual files in the user's working language.

## Directory Shape

```text
papers/
  AGENTS.md
  PAPERS.md
  library/
    <paper-id>/
      paper.md
      <reading-note>.md
  projects/
    <project>.md
    <project> roadmap.canvas
  topics/
    <topic>.md
```

Initialize missing pieces conservatively:

- Create `papers/library/` if missing.
- Create `papers/projects/` if missing.
- Create `papers/topics/` if missing.
- Create `papers/AGENTS.md` if missing.
- Create `papers/PAPERS.md` if missing.
- Create `papers/projects/<project>.md` only when the user gives a project, topic, or research goal.
- Create `papers/topics/<topic>.md` only when the user asks for a project-independent aggregation index.
- Do not overwrite existing files unless the user asks for a refresh. If a file exists but is thin, append or make the smallest useful edit.

## `papers/AGENTS.md` Seed

````markdown
# Papers Agent Workflow

This directory is an agent-readable literature workspace.

## Layout

```text
papers/
  library/
    <paper-id>/
      paper.md
      <reading-note>.md
  projects/
    <project>.md
    <project> roadmap.canvas
  topics/
    <topic>.md

  PAPERS.md
  AGENTS.md
```

- `library/` stores stable paper materials. Directory names use bare arXiv ids or stable slugs.
- `paper.md` is the converted paper body for agent reading and git diff.
- `<reading-note>.md` is the canonical Obsidian reading note for humans and agents.
- `projects/` stores Obsidian project maps that link to paper notes with wikilinks.
- A project map may have a paired `<project> roadmap.canvas` visualizing its `主题聚合` themes and paper branches.
- `topics/` stores project-independent aggregation indexes. Each index links to canonical notes by a long-lived theme and does not need a roadmap canvas.
- `PAPERS.md` is a lightweight global inventory and audit list.

## Rules

- Do not store raw HTML, browser `_files/` folders, source archives, or PDFs unless explicitly requested.
- Prefer official arXiv HTML or official PDF links in reading-note frontmatter.
- Keep all `paper.md` figures as public remote links. Promote only verified explanatory figures into the canonical note, with the original caption and a short reading cue; do not store raw assets by default.
- Use Obsidian wikilinks for internal paper-note relationships.
- Keep project maps focused on navigation, synthesis, and project relevance.
- Keep topic indexes focused on cross-project curation, concept dependencies, and reading order; do not copy single-paper analysis into them.
- Run the paper workspace validator after ingest, rename, inventory edits, or project-map edits.

```

```
````

## `papers/PAPERS.md` Seed

```markdown
# Papers

Global inventory for the paper library. Project-specific reading paths live in `projects/`; cross-project curated paths live in `topics/`.

## Index

<!-- Add entries like:
- [<paper-id> <title>](library/<paper-id>/<reading-note>.md)
  - Tags: `<tag>`, `<tag>`
  - Summary: <two or three concise sentences>
  - Source: <official source URL>
-->
```

Keep `PAPERS.md` compact. It is for de-duplication, whole-library scanning, and audit coverage, not for long synthesis.

## Project Map Seed

Use this when creating `papers/projects/<project>.md`:

```markdown
---
title: '<project title>'
type: note
status: seed
visibility: private
tags:
  - literature-map
---

# <Project Title>

## Project Goal

<What this project is trying to understand or build.>

## Roadmap

![[papers/projects/<project> roadmap.canvas]]

## Search Framing

<How papers were selected. Include topic axes, inclusion criteria, and known gaps when relevant.>

## Core Reading Path

1. [[papers/library/<paper-id>/<reading-note>|<short title>]] - <why to read first>

## Groups

### <Problem, Module, Decision, or Stage>

- [[papers/library/<paper-id>/<reading-note>|<short title>]] - <project-specific reason>

## Key Summaries

![[papers/library/<paper-id>/<reading-note>#<summary-heading>]]

## Project Notes

- <Design decision, open question, risk, or follow-up paper gap.>
```

Do not copy `paper.md` or single-paper reading notes into `projects/`.

## Topic Index Seed

Use this when creating `papers/topics/<topic>.md` for a long-lived, project-independent grouping:

```markdown
---
title: '<topic title>'
type: topic-index
status: active
visibility: private
tags:
  - papers
  - <topic-tag>
---

# <Topic Title>

<Explain the shared idea and why this is not a project map.>

## <Conceptual Group>

- [[papers/library/<paper-id>/<reading-note>|<short title>]] - <why it belongs here>.![[papers/library/<paper-id>/<reading-note>#^summary]]

## 阅读路径

1. [[papers/library/<paper-id>/<reading-note>|<short title>]] - <why to read first>.
```

Do not create a roadmap canvas or a second copy of any paper for a topic index.

## Minimal Initialization Checklist

Before ingesting papers into a new or immature workspace, make sure:

- `papers/library/` exists.
- `papers/projects/` exists.
- `papers/topics/` exists.
- `papers/AGENTS.md` explains local workflow rules.
- `papers/PAPERS.md` exists as the global inventory.
- Any active project has one `papers/projects/<project>.md` map.

After adding papers, run `scripts/validate_papers_workspace.py`.
