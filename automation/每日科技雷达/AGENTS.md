# Agent Instructions

This is a private Obsidian vault and working-memory repository.

## Safety

- Treat all content as private unless a note explicitly says otherwise.
- Do not create a `publish/` directory.
- Do not commit or edit `.obsidian/` unless the user explicitly asks.
- Do not move large groups of files without preserving relative asset links.
- Do not delete migrated source material from any external archive (e.g. a former Typst tree) unless explicitly asked.

## Organization

- New quick captures go to `inbox/`.
- Daily process notes go to `daily/weekly/` through the user's `ob daily` command.
- Reusable knowledge goes to `notes/`.
- Project context goes to `projects/<project>/`.
- Course material goes to `courses/<term>/<course>/`.
- Career and interview material goes to `career/`.
- Reviews and decisions go to `reviews/`.
- Reusable templates go to `_templates/`.

## Frontmatter

Use lightweight frontmatter when useful:

```yaml
title:
created:
updated:
type: note
status: seed
visibility: private
public:
  include: false
  slug:
tags: []
```

Publishing eligibility should be represented with metadata, not by moving files into a publish folder.

## Markdown Writing

- Organize notes with nested headings that reflect topic hierarchy.
- Use subheadings to group related details under the same theme.
- Avoid writing long notes as a flat sequence of same-level headings.
- Keep heading levels meaningful: `##` for major sections, `###` for subtopics, `####` only when the extra nesting improves scanning.
- Prefer concise section titles that describe the content below them.
- When referencing images in Markdown notes, prefer publicly accessible image URLs by default. Store images locally only when the user explicitly asks or when the source is private, unstable, or unavailable via a durable public URL.
- When the user requests to add a small concept, write it to the appropriate location in the form of a callout (closed by default). If the user explicitly requests to add a chapter to describe in detail, then use the title organization.
