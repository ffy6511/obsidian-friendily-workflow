---
name: obsidian-vault
description: Define vault workspace architecture for Obsidian-based knowledge management. Use when initializing a domain workspace, creating navigation maps (project maps, domain maps, topic indexes), building roadmap canvases, or validating vault structure. Covers workspace bootstrap, directory conventions, canvas layout, and cross-note navigation patterns.
---

# Obsidian Vault Architecture

## Purpose

This skill defines the **structural architecture** for Obsidian vault workspaces used by domain skills (such as `paper-md-ingest` and `learning-unit-ingest`). It is the single source of truth for:

- How to bootstrap a new domain workspace (directory shape, `AGENTS.md`, global index)
- How to build roadmap canvases (colors, layout, node hierarchy)
- How navigation maps link to canonical notes (wikilinks, embeds, backlinks)
- How to validate vault structure (canvas JSON, link integrity)

## Scope boundary

| This skill owns | This skill does NOT own |
|---|---|
| Workspace directory shape and bootstrap | Obsidian markdown syntax (→ `obsidian-markdown`) |
| Roadmap canvas conventions (colors, layout) | Callout, footnote, or Mermaid rules (→ `obsidian-markdown`) |
| Navigation map structure (themes, embeds, backlinks) | Domain-specific content schemas (→ each domain skill) |
| Canvas JSON validation | Domain-specific validators (→ each domain skill) |

## When to use

- When initializing a new domain workspace (`papers/`, `learning/`, or any future domain)
- When creating or updating a roadmap `.canvas` file
- When creating navigation maps (project maps, domain maps, topic indexes)
- When validating canvas JSON integrity or edge references

## Dependencies

Read `obsidian-markdown` for Obsidian syntax conventions (wikilinks, embeds, block IDs, callouts, properties). This skill uses that syntax but does not re-document it.

## References

- [Workspace Bootstrap](references/workspace-bootstrap.md) — directory shape, `AGENTS.md` seed, global index pattern, initialization checklist
- [Roadmap Canvas](references/roadmap-canvas.md) — colors, layout, node hierarchy, edge rules, JSON validation
- [Navigation Maps](references/navigation-maps.md) — project maps, domain maps, topic indexes, wikilink + embed + backlink patterns
