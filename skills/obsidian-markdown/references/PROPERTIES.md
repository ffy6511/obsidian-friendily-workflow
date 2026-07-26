# Properties (Frontmatter) Reference

Properties use YAML frontmatter at the start of a note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - important
aliases:
  - My Note
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
rating: 4.5
completed: false
due: 2024-02-01T14:30:00
---
```

## Property Types

| Type        | Example                         |
| ----------- | ------------------------------- |
| Text        | `title: My Title`               |
| Number      | `rating: 4.5`                   |
| Checkbox    | `completed: true`               |
| Date        | `date: 2024-01-15`              |
| Date & Time | `due: 2024-01-15T14:30:00`      |
| List        | `tags: [one, two]` or YAML list |
| Links       | `related: "[[Other Note]]"`     |

## Default Properties

- `tags` - Note tags (searchable, shown in graph view)
- `aliases` - Alternative names for the note (used in link suggestions)
- `cssclasses` - CSS classes applied to the note in reading/editing view

## Project-Specific Properties

These are not Obsidian-native. They are required or recognized by the
current project's theme (thought-lite) and its content collections.
When editing notes under `src/content/{note,jotting,preface,information}/`,
include them in frontmatter.

### `series`

Groups related notes into a navigable series. The value is a plain
string naming the series. All notes sharing the same `series` value
are listed together in a "series" navigation panel on each note's
table-of-contents sidebar, ordered by `timestamp` (oldest first).

```yaml
---
title: Configuration Guide
timestamp: 2026-03-21T00:00:00+08:00
series: Guide
---
```

**When to use:**

- A multi-part article, tutorial, or guide split across several notes
  (e.g. a "Guide" series covering configuration, content, i18n).
- Any set of notes meant to be read in sequence and surfaced as a
  connected group in the UI.

**When NOT to use:**

- One-off notes that don't belong to a sequence.
- Use `tags` instead when the relationship is topical rather than
  sequential — tags are many-to-many, `series` is one-to-one (a note
  belongs to at most one series).

> The `series` field is defined as `z.string().optional()` in
> `src/content.config.ts`. Notes that omit it simply don't appear in
> any series panel.

## Tags

```markdown
#tag
#nested/tag
#tag-with-dashes
#tag_with_underscores
```

Tags can contain: letters (any language), numbers (not first character), underscores `_`, hyphens `-`, forward slashes `/` (for nesting).

In frontmatter:

```yaml
---
tags:
  - tag1
  - nested/tag2
---
```
