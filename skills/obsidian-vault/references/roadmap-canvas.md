# Roadmap Canvas Conventions

This is the **single source of truth** for roadmap `.canvas` files in Obsidian vaults. Domain skills (`paper-md-ingest`, `learning-unit-ingest`) delegate to this reference instead of re-documenting canvas layout rules.

## Purpose

Each navigation map (project map, domain map) may have a paired `.canvas` roadmap that visualizes its themes and branches. Embed the canvas near the top of the map:

```markdown
## Roadmap

![[<vault-relative-path-to-canvas>]]
```

## Layout: roadmap.sh-inspired

Use a three-level vertical hierarchy:

### Level 1 — Center spine (themes)

- **Color**: orange, preferably `#f6a800`.
- **Content**: the main themes of the map. These should mirror the map's subsection headers — for project maps, the `主题聚合` themes; for domain maps, the main learning path.
- **Do not** put individual items (papers, units) on the spine unless the map has only one linear path with no meaningful themes.
- **Width**: at least 260-320px for theme nodes. Increase for long Chinese or mixed Chinese/English labels.

### Level 2 — Branches (concrete items)

- **Color**: light blue, preferably `#b9dcff`.
- **Lines**: blue, preferably `#2f7de1`.
- **Content**: concrete items under the theme they support. Each branch node should use a vault-relative wikilink to its canonical note, with a short alias.
- Use more branches when the topic is complex. Avoid cramming too much text into one node — split a long branch into multiple concise nodes instead.

### Level 3 — Explanation nodes

- **Color**: pale blue, preferably `#eaf4ff`.
- **Content**: one sentence stating the item's role in the map's context. For project maps, this is the project-specific reason; for domain maps, this is a one-sentence meaning or role of the concept.
- **Edges**: connect each Level-2 node to its Level-3 explanation node with a gray line (`#9ca3af`), set `toEnd: "none"` (no arrowhead), and align the two node centers vertically so the edge is horizontal and does not cross other edges.

### Top context blocks

- **Color**: neutral white.
- **Content**: prerequisites, usage notes, project goals, or scope notes. Place at the top of the canvas.

## Node sizing and text

- Make node widths large enough for the displayed title or alias. Increase width for Chinese or mixed Chinese/English labels; do not leave clipped text.
- If text does not fit, widen the node first. Do not reduce the label until the roadmap becomes visually noisy.
- Use concise labels in branch nodes. Put explanation prose in the Level-3 node rather than shrinking the concept label.
- Prefer stable dimensions and aligned coordinates. Leave enough spacing for Obsidian's rendered text so nodes do not overlap or truncate.

## Paths

- Use **vault-relative** wikilinks inside `.canvas` node text, such as `[[papers/library/<id>/<note>|<alias>]]` or `[[learning/domains/<domain>/units/<unit>|<alias>]]`.
- **Never** use absolute filesystem paths inside `.canvas` files or navigation maps.

## Canvas JSON validation

After any canvas edit, validate:

1. The `.canvas` file is parseable JSON.
2. Every edge's `fromNode` and `toNode` references an existing node `id` in `nodes`.
3. When the canvas has third-level explanation nodes, verify their explanation edges are gray (`#9ca3af`), use `toEnd: "none"`, and have matching vertical centers with their second-level parent nodes.
