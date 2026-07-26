---
name: obsidian-markdown
description: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts, properties, and other Obsidian-specific syntax. Use when working with .md files in Obsidian, or when the user mentions wikilinks, callouts, frontmatter, tags, embeds, or Obsidian notes.
---

# Obsidian Flavored Markdown Skill

Create and edit valid Obsidian Flavored Markdown. Obsidian extends CommonMark and GFM with wikilinks, embeds, callouts, properties, comments, and other syntax. This skill covers only Obsidian-specific extensions -- standard Markdown (headings, bold, italic, lists, quotes, code blocks, tables) is assumed knowledge.

## Workflow: Creating an Obsidian Note

1. **Add frontmatter** with properties (title, tags, aliases) at the top of the file. See [PROPERTIES.md](references/PROPERTIES.md) for all property types.
   - **`title`** and **`timestamp`** are required by the current project's content schema — the build will fail without them.
2. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below.
3. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections, or standard Markdown links for external URLs.
4. **Embed content** from other notes, images, or PDFs using the `![[embed]]` syntax. See [EMBEDS.md](references/EMBEDS.md) for all embed types.
5. **Add callouts** for highlighted information using `> [!type]` syntax. See [CALLOUTS.md](references/CALLOUTS.md) for all callout types.
6. **Verify** the note renders correctly in Obsidian's reading view.

> When choosing between wikilinks and Markdown links: use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only.

> [!important] Use `series` for sequential note groups
> When the note is part of a multi-part guide, tutorial, or any sequence
> the reader should follow in order, add `series: <SeriesName>` to the
> frontmatter. All notes sharing the same `series` value are listed
> together in the project's series navigation panel (ordered by
> `timestamp`). Do **not** use `series` for one-off notes or purely
> topical groupings — use `tags` for those. See
> [PROPERTIES.md](references/PROPERTIES.md#series) for details.

## Internal Links (Wikilinks)

```markdown
[[Note Name]] Link to note
[[Note Name|Display Text]] Custom display text
[[Note Name#Heading]] Link to heading
[[Note Name#^block-id]] Link to block
[[#Heading in same note]] Same-note heading link
```

Define a block ID by appending `^block-id` to any paragraph:

```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, place the block ID on a separate line after the block:

```markdown
> A quote block

^quote-id
```

## Embeds

Prefix any wikilink with `!` to embed its content inline:

```markdown
![[Note Name]]                         Embed full note
![[Note Name#Heading]]                 Embed section
![[image.png]]                         Embed image
![[image.png|300]]                     Embed image with width
![[document.pdf#page=3]]               Embed PDF page
```

See [EMBEDS.md](references/EMBEDS.md) for audio, video, search embeds, and external images.

## Callouts

```markdown
> [!note]
> Basic callout.

> [!warning] Custom Title
> Callout with a custom title.

> [!faq]- Collapsed by default
> Foldable callout (- collapsed, + expanded).
```

Common types: `note`, `tip`, `warning`, `info`, `example`, `quote`, `bug`, `danger`, `success`, `failure`, `question`, `abstract`, `todo`.

See [CALLOUTS.md](references/CALLOUTS.md) for the full list with aliases, nesting, and custom CSS callouts.

### Formula and Complex-Concept Callouts

Use an Obsidian-native `NOTE` callout immediately after a formula, special method, or complex concept when the explanation cannot fit in a one- or two-sentence footnote.

- Use `> [!NOTE] 公式解释` for a short explanation that should remain visible.
- Use `> [!NOTE]+ 公式解释` only when the block should be collapsible but initially expanded.
- Use `> [!NOTE]- 公式解释` for a content-heavy explanation that should be collapsed by default. Use equally literal titles such as `方法展开` or `概念展开` when the content is not an equation.
- Keep the surrounding paragraph understandable while the callout is collapsed: state the formula or method's basic purpose in the main narrative, then put the detailed unpacking in the callout.
- Explain a formula in plain language before enumerating symbols. Define every non-obvious parameter, variable, index, operator, normalization term, and constraint; state where each value comes from and whether it is fixed, observed, or learned when that distinction matters.
- Explain the overall relationship, not only the symbol table: identify the optimized or computed quantity, how the terms interact, which quantities increase or decrease together, and the trade-off, normalization, constraint, or stopping condition expressed by the equation.
- For a special method or concept, state its input or precondition, main transformation or decision steps, output or state change, and role in the note's end-to-end context. Add a small example or boundary case when it clarifies a branch.
- Preserve the source's notation and qualify any interpretation not stated by the source.

Example:

```markdown
$$
\pi^*(y\mid x)=\frac{1}{Z(x)}\pi_{\mathrm{ref}}(y\mid x)
\exp\left(\frac{r(x,y)}{\beta}\right)
$$

> [!NOTE]- 公式解释
> Plain-language explanation first, then symbol table.
>
> - $x$ is the input, $y$ is the output candidate.
> - $\pi_{\mathrm{ref}}$ is the fixed reference policy, $r(x,y)$ is the reward.
> - $\beta > 0$ controls the cost of deviating from the reference.
> - Overall: higher-reward outputs gain probability exponentially, but
>   $\pi_{\mathrm{ref}}$ and $\beta$ jointly limit the deviation.
```

## Properties (Frontmatter)

```yaml
---
title: My Note
date: 2024-01-15
tags:
  - project
  - active
aliases:
  - Alternative Name
cssclasses:
  - custom-class
---
```

Default properties: `tags` (searchable labels), `aliases` (alternative note names for link suggestions), `cssclasses` (CSS classes for styling).

Project-specific: `series` (groups sequential notes into a navigable series — see the workflow note above and [PROPERTIES.md](references/PROPERTIES.md#series)), `timestamp` (required publication date — see [PROPERTIES.md](references/PROPERTIES.md#timestamp)).

See [PROPERTIES.md](references/PROPERTIES.md) for all property types, tag syntax rules, and advanced usage.

## Tags

```markdown
#tag Inline tag
#nested/tag Nested tag with hierarchy
```

Tags can contain letters, numbers (not first character), underscores, hyphens, and forward slashes. Tags can also be defined in frontmatter under the `tags` property.

## Comments

```markdown
This is visible %%but this is hidden%% text.

%%
This entire block is hidden in reading view.
%%
```

## Obsidian-Specific Formatting

```markdown
==Highlighted text== Highlight syntax
```

## Math (LaTeX)

```markdown
Inline: $e^{i\pi} + 1 = 0$

Block:

$$
\frac{a}{b} = c
$$
```

## Diagrams (Mermaid)

For most diagrams that describe a lifecycle, event flow, or state transition, prefer `stateDiagram-v2`. Use `flowchart` only when static topology, branching, or component connectivity is the primary meaning. Apart from Mermaid syntax keywords and required code, protocol, or proper-name identifiers, write every state label, transition label, and annotation in the note's working language; Chinese notes default to Chinese.

For every `stateDiagram-v2`, count only named business states; do not count Mermaid `[*]` entry or exit markers. Set `direction LR` when the diagram has four or fewer business states, and `direction TB` when it has five or more. When a diagram would still be dense, split it into an overview and focused sub-diagrams instead of forcing a single large layout.

````markdown
```mermaid
stateDiagram-v2
    state "待处理" as 待处理
    state "执行中" as 执行中
    state "已完成" as 已完成

    [*] --> 待处理
    待处理 --> 执行中: 开始执行
    执行中 --> 已完成: 执行完成
```
````

To link Mermaid nodes to Obsidian notes, add `class NodeName internal-link;`.

## Footnotes

```markdown
Text with a footnote[^1].

[^1]: Footnote content.

Inline footnote.^[This is inline.]
```

### Terminology Footnotes

Use Obsidian-compatible Markdown footnotes to explain specialized terms that a technically capable reader may still need in order to follow the note. Add the marker at the term's first meaningful occurrence and collect definitions in a dedicated section (e.g. `## 概念注释` / `## Terminology Notes`) near the end of the note.

- Explain both **what the term means** and **what role it plays in this note**; prefer one or two sentences over a dictionary-style definition.
- Prioritize model families, algorithms, datasets, evaluation protocols, file formats, losses, and note-specific jargon that materially affect understanding.
- Do not annotate common terms, repeat the same definition, or overload every paragraph with footnotes. The goal is to preserve reading flow while removing likely comprehension blockers.
- Use stable, descriptive lowercase ids such as `[^deberta]`, `[^cross-encoder]`, or `[^teacher-forcing]`. Ensure every marker has exactly one definition and every definition is referenced.
- Keep equations in Obsidian-compatible dollar delimiters. Use the formula callout rules above for equations or mechanisms that require structured expansion rather than a short footnote.

Example:

```markdown
候选生成器使用 DeBERTa[^deberta] 对页面元素排序。

## 概念注释

[^deberta]: **DeBERTa**：一种 encoder-only 预训练语言模型。本文将它用作高效元素排序器。
```

## Complete Example

```markdown
---
title: Project Alpha
date: 2024-01-15
tags:
  - project
  - active
status: in-progress
---

# Project Alpha

This project aims to [[improve workflow]] using modern techniques.

> [!important] Key Deadline
> The first milestone is due on ==January 30th==.

## Tasks

- [x] Initial planning
- [ ] Development phase
  - [ ] Backend implementation
  - [ ] Frontend design

## Notes

The algorithm uses $O(n \log n)$ sorting. See [[Algorithm Notes#Sorting]] for details.

![[Architecture Diagram.png|600]]

Reviewed in [[Meeting Notes 2024-01-10#Decisions]].
```

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
