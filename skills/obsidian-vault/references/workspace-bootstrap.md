# Workspace Bootstrap

Use this reference when initializing a new domain workspace or repairing an immature one. A domain workspace is the top-level container for a knowledge domain — `papers/` for research papers, `learning/` for learning units, or any future domain.

## Directory Shape

Every domain workspace follows the same skeleton:

```text
<domain-root>/
  AGENTS.md          # Agent-readable workflow rules for this domain
  <INDEX>.md          # Global inventory and audit list (PAPERS.md, LEARNING.md, ...)
  <content>/          # Canonical items (library/, units/, ...)
  <maps>/             # Navigation maps (projects/, domains/)
  <indexes>/          # Cross-cutting topic indexes (topics/, optional)
```

The domain skill defines the concrete directory names. For example:
- `paper-md-ingest` uses `library/`, `projects/`, `topics/`
- `learning-unit-ingest` uses `domains/<domain>/units/`, `domains/<domain>/manifests/`

## `AGENTS.md` Seed

Every domain workspace should have an `AGENTS.md` at its root. It explains:

- The directory layout (the shape above, with concrete names)
- What each subdirectory stores
- Domain-specific rules (what to store, what to reject, naming conventions)
- When to run the domain validator

Write it in the user's working language. Keep it concise — it is a reference card for agents, not a tutorial. The domain skill provides a concrete seed template.

## Global Index File

Each domain has one global index file that serves as a flat inventory:

- `papers/` → `PAPERS.md`
- `learning/` → `LEARNING.md`

The index lists every canonical item with minimal metadata (id, title, tags, source, summary). It exists for de-duplication, whole-library scanning, and audit coverage — not for rich synthesis. Put reading paths, rationale, and curation in navigation maps, not in the global index.

## Initialization Rules

- Create directories and files conservatively — only what is missing.
- Do not overwrite existing files unless the user asks for a refresh. If a file exists but is thin, append or make the smallest useful edit.
- Create navigation maps and topic indexes only when the user gives a concrete reason (a project name, a domain request, a long-lived grouping).
- After initialization or any structural change, run the domain validator.

## Checklist

Before adding items to a new or immature workspace, ensure:

- The content directory exists (`library/`, `units/`, etc.)
- The maps directory exists (`projects/`, `domains/`, etc.)
- `AGENTS.md` explains local workflow rules
- The global index file exists
- Any active project or domain has one navigation map
