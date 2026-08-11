# Content schema

Single source of truth for a walkthrough site: one JSON object, fully self-contained (all prose and code inlined). No runtime dependency on the original repository.

## Shape

```json
{
  "site": {
    "title": "Site tab title and default H1 brand context",
    "brand": "Header brand text",
    "brandMark": "π",
    "description": "Meta description",
    "lang": "zh-CN",
    "repoLabel": "demo /",
    "themeStorageKey": "cws-theme"
  },
  "lessons": [
    {
      "id": "main",
      "title": "Lesson title",
      "description": "Optional subtitle under the title",
      "readingTime": "10 min",
      "markdown": "Prose with checkpoint HTML comments",
      "initialRepo": {},
      "checkpoints": [
        {
          "id": "overview",
          "label": "Overview",
          "file": "src/index.ts",
          "repo": {},
          "focus": null
        }
      ]
    }
  ]
}
```

## Field rules

| Field | Required | Notes |
| --- | --- | --- |
| `site.title` | yes | Browser title |
| `site.brand` | yes | Header label |
| `site.brandMark` | no | Single glyph; default `◇` |
| `site.description` | no | Meta description |
| `site.lang` | no | Default `zh-CN` |
| `site.repoLabel` | no | Code panel heading; default `repo /` |
| `site.themeStorageKey` | no | localStorage key for theme |
| `lessons[]` | yes | At least one lesson |
| `lessons[].id` | yes | Unique; used in hash nav `#lesson-id` |
| `lessons[].title` | yes | Article H1 |
| `lessons[].markdown` | yes | Full lesson body |
| `lessons[].initialRepo` | no | Repo snapshot before first checkpoint; default `{}` |
| `lessons[].checkpoints[]` | yes | Ordered; at least one |
| `checkpoint.id` | yes | Must match a markdown anchor |
| `checkpoint.label` | yes | Short UI label |
| `checkpoint.file` | yes | File to focus when this checkpoint activates (must exist in `repo`, or `repo` empty) |
| `checkpoint.repo` | yes | Full file map at this stage: path → full file text |
| `checkpoint.focus` | no | `[startLine, endLine]` 1-based inclusive highlight override |

## Markdown anchors

Insert anchors **before** the prose that should unlock a code stage:

```markdown
<!-- checkpoint: overview -->

## 五个文件

...

<!-- checkpoint: llm -->

## llm.ts

...
```

Rules:

1. Every `checkpoint.id` must appear exactly once as `<!-- checkpoint: <id> -->`.
2. Anchors are ordered by document order; scrolling past an anchor activates that checkpoint.
3. Put the first checkpoint near the top of the article so the panel is not stuck empty for long.
4. Do not rely on heading text alone for coupling — anchors are the only link.

## Repo snapshots (progressive code)

Each checkpoint’s `repo` is the **complete visible workspace** at that moment, not a diff.

### Monotonic growth (default)

For each file path, later content should only **insert** lines relative to the previous checkpoint’s version of that file. Do not delete or rewrite earlier lines.

Why: the UI highlights “new” lines via LCS against the previous snapshot. Rewrites make the whole block look newly typed.

Allowed:

- empty → first lines
- append / insert new lines
- introduce a **new** file path

Forbidden (unless you set `focus`):

- renaming symbols that rewrites many lines
- reformatting large regions
- replacing a stub body with a different shape in place without keeping the old lines

### `focus` override

When a stage is conceptual (no code change) or a rewrite is unavoidable, set:

```json
"focus": [12, 28]
```

Then the panel still scrolls to that range and highlights it without depending on LCS.

### Empty workspace

Use `"repo": {}` (and optionally empty `initialRepo`) for overview stages. `file` may point at a path that appears later; when `repo` is empty the empty-state UI shows.

When first introducing a file, include it in `repo` with the partial content for that stage.

## Multi-lesson sites

- One lesson → single article + hash `#<id>`.
- Multiple lessons → header nav switches lessons; each has its own checkpoint sequence.
- Keep each lesson self-contained; do not share checkpoint ids across lessons.

## Optional assets

Figures referenced as markdown images (`![alt](figures/foo.png)`) must live under the generated site’s `figures/` (or any path relative to `index.html`). Copy them at scaffold time. Prefer local paths over remote URLs for offline viewing.

## Minimal valid example

See `assets/template/content.example.json`.
