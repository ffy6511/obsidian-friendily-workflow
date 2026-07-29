---
name: learning-unit-ingest
description: Create and maintain an Obsidian `learning/` workspace made of domain learning maps, paired roadmap canvases, and small learning-unit notes from public HTML, YouTube, Bilibili, or other embeddable URLs. Use when the user wants to learn a domain, discover high-quality public materials, draft a learning outline for confirmation, initialize `learning/`, create iframe-first learning notes, update domain maps or roadmap canvas files, or validate learning-unit wikilinks and guide embeds.
---

# Learning Unit Ingest

## Goal

Build a personal domain-learning workspace. Public URLs are the source material. The vault stores learning maps, iframe-first unit notes, guide text, concept structure, and the user's own notes.

## Workflow

1. Identify the learning domain from the user's request, such as `agentic-rl`, `llm-evaluation`, or `deep-learning`.
2. If the user asks to learn a domain, discover public materials first. Search for a balanced set of high-quality HTML docs, official guides, high-signal blogs, YouTube videos, and Bilibili videos. Prefer official project documentation, canonical tutorials, technical blogs with concrete workflows, and talks that explain mechanisms.
3. Present a candidate learning outline before creating unit notes. Include resource title, type, URL, why it belongs in the domain, and the proposed unit it supports. A proposed unit may aggregate multiple complementary resources. Wait for user confirmation before building the learning workspace from discovered materials.
4. If the user already confirms the outline or provides exact URLs to ingest, inspect `learning/`. If it is missing or immature, read `references/workspace.md` and initialize it with `scripts/init_learning_workspace.py`.
5. Create or update one small unit note per learning unit under `learning/domains/<domain>/units/`. A unit may contain one iframe or several iframes. Put `学习资源` at the top, list each resource as `- <resource name>: <URL>`, place its iframe directly below the list item, then add `学习导引`, `知识总览`, optional `概念注释`, and a complete `我的笔记`.
6. Update `learning/LEARNING.md` and the domain map `learning/domains/<domain>/<domain-title>.md`. The domain map is the human and agent entry point for the domain.
7. Create or update the domain roadmap canvas at `learning/domains/<domain>/<Domain Title> roadmap.canvas`, then embed it near the top of the domain map with `![[learning/domains/<domain>/<Domain Title> roadmap.canvas]]`.
8. Keep optional batch metadata in `learning/domains/<domain>/manifests/units.json`. This is for automation and audit, not for reading.
9. Run `scripts/validate_learning_workspace.py --learning-root learning` and fix all reported issues before handing off. For roadmap canvas edits, also validate that the `.canvas` file is parseable JSON and every edge references an existing node.

## Workspace Shape

```text
learning/
  AGENTS.md
  LEARNING.md
  domains/
    <domain>/
      <Domain Title>.md
      <Domain Title> roadmap.canvas
      units/
        <unit-title>.md
      manifests/
        units.json
```

The local workspace stores maps and notes. Public webpages and videos stay referenced by URL and rendered through iframe embeds.

Read `references/workspace.md` before initializing or changing workspace shape. Read `references/obsidian.md` before creating unit notes, video embeds, or domain maps.

## Unit Notes

Use this order exactly:

1. Lightweight frontmatter.
2. `## 学习资源`, with each resource shown as a named URL line followed by its iframe.
3. `## 学习导引` with a stable `^guide` block id.
4. `## 知识总览`.
5. Optional `## 概念注释`, when the guide or overview contains terms that need short explanations.
6. `## 我的笔记`, pre-populated as the unit's complete, reusable learning note by default.

The `学习资源` section should make every iframe legible: name the resource, show the clickable source URL with angle-bracket autolinks, then place the matching iframe. The `学习导引` section should explain what the unit teaches, where it sits in the domain, how multiple resources complement each other, and what to focus on while reading or watching. The `知识总览` section should remain a compact conceptual map and distinction table. `我的笔记` is the default home for the substantive note: write the full explanation, mechanism, examples, boundary cases, comparisons, practical checklist, and source trail there. Leave it empty only when the user explicitly asks for an empty personal-notes area. When revising an existing unit, preserve user-authored material in `我的笔记`; extend or revise it only to the scope the user authorizes. Apply the terminology and callout rules below to every explanatory section the skill writes.

### 完整“我的笔记”默认规则

Treat `## 我的笔记` as the primary learning artifact, not a blank scratchpad. Follow the established style of `learning/domains/deep-learning/units/序列建模与 Seq2Seq：从 RNN 到 Transformer.md`:

1. Start with the central question the note resolves and a short learning map or reading key.
2. Explain the subject from first principles in a progressive numbered structure. For each mechanism, state its input/precondition, transformation or control decision, output/state change, and role in the whole system.
3. Use tables, diagrams, compact examples, equations, and adjacent callouts when they make a relationship inspectable. Keep `知识总览` concise; do not hide the real derivation or engineering reasoning there.
4. State important boundaries, failure modes, comparisons, and anti-patterns explicitly. For implementation topics, distinguish SDK convenience state from the system's source of truth, and describe the evidence or test that would validate the claim.
5. End with a small self-check, implementation checklist, or next-step exercise when it helps the learner apply the material. Keep source links or a `资料出处` subsection within `我的笔记` when the unit needs a traceable reading trail.

The only exception is an explicit user request to reserve `我的笔记` for their own blank writing. Do not fabricate personal experience or claim the prose was written by the user; write it as complete study notes prepared for the user.

### Mermaid Diagrams

Follow the Mermaid diagram rules in the `obsidian-markdown` skill. Prefer `stateDiagram-v2` for lifecycle and state-transition diagrams; use `flowchart` only for static topology.

### Terminology Footnotes

Follow the terminology footnote rules in the `obsidian-markdown` skill. Collect definitions in the optional `## 概念注释` section before `## 我的笔记`. Add markers at the first meaningful occurrence of each specialized term.

### Formula and Complex-Concept Callouts

Follow the formula callout rules in the `obsidian-markdown` skill. After equations or complex mechanisms in `知识总览` or `我的笔记`, choose the callout's default state by **relevance and length**: expand (`> [!NOTE]+ 公式解释`) when the unpacking is essential to the surrounding passage and is not long; collapse (`> [!NOTE]- 公式解释`) when it is long or supplementary. Do not collapse every formula callout by default.

## Domain Maps

Domain maps organize learning, not project implementation. Use sections such as:

- `学习目标`
- `学习地图`
- `推荐路径`
- `概念索引`
- optional `待补资源`

In `学习地图`, each unit bullet should use an Obsidian wikilink plus an inline guide embed:

```markdown
- [[learning/domains/<domain>/units/<unit-title>|<unit-title>]] - <why this unit matters>.![[learning/domains/<domain>/units/<unit-title>#^guide]]
```

Use the fixed block id `^guide`; do not invent per-unit guide ids.

## Domain Roadmap Canvas

Each learning domain should have a paired roadmap canvas named `learning/domains/<domain>/<Domain Title> roadmap.canvas`. Embed it near the top of the domain map, immediately after `学习目标` unless the note already has a more natural overview section:

```markdown
## Roadmap

![[learning/domains/<domain>/<Domain Title> roadmap.canvas]]
```

Use a roadmap.sh-inspired layout for domain roadmaps:

- Put the main learning path on a vertical center spine. Main path nodes should use orange, preferably `#f6a800`, and be wide enough for the full unit title or key phrase without clipping. Use at least 230-280px width for short labels and increase width for Chinese or mixed Chinese/English labels.
- Put supporting concepts, prerequisites, and subtopics as side branches. Branch nodes should use blue, preferably light blue `#b9dcff`, with blue branch lines such as `#2f7de1`. Use more branches when the topic is complex; avoid cramming too much text into one node.
- Add a third-level explanation node for every second-level concept node. The explanation node should give a one-sentence meaning or role of that concept. Use a pale blue fill such as `#eaf4ff`.
- Connect each second-level concept node to its third-level explanation node with a gray line such as `#9ca3af`, set `toEnd: "none"`, and align the two node centers vertically so the edge is horizontal and does not cross other edges.
- Use concise labels in branch nodes. Put explanation prose in the third-level node rather than shrinking the concept label.
- Keep top context blocks such as prerequisites and usage notes in neutral white nodes.
- Use vault-relative wikilinks in main nodes, such as `[[learning/domains/<domain>/units/<unit-title>|<unit-title>]]`. Do not use absolute paths.
- Prefer stable dimensions and aligned coordinates. Leave enough spacing for Obsidian's rendered text so nodes do not overlap or truncate. If text does not fit, widen the node first; do not reduce the label until the roadmap becomes visually noisy.

## Resource Embeds

For public HTML:

```markdown
- <resource name>: <https://example.com>

<iframe
  src="https://example.com"
  style="width:100%; height:300px; border:0;"
  allowfullscreen>
</iframe>
```

For YouTube:

```markdown
- <resource name>: <https://www.youtube.com/watch?v=<video-id>>

<iframe
  width="100%"
  height="480"
  src="https://www.youtube.com/embed/<video-id>?start=<seconds>"
  title="YouTube video player"
  frameborder="0"
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  allowfullscreen>
</iframe>
```

Use normal `watch?v=` URLs for the clickable resource line and `sources` metadata. Use `/embed/<video-id>` URLs for iframe `src` because they provide a cleaner embedded player experience. If a specific video blocks `/embed/` playback in Obsidian, handle that unit as an exception by keeping the `watch?v=` resource line and either using the watch URL in iframe `src` or replacing the iframe with a short note.

For Bilibili:

```markdown
- <resource name>: <https://www.bilibili.com/video/<bvid>/>

<iframe
  width="100%"
  height="480"
  src="https://player.bilibili.com/player.html?bvid=<bvid>&page=1&t=<seconds>&autoplay=0"
  frameborder="0"
  autoplay="0"
  allowfullscreen>
</iframe>
```

## Scripts

Initialize or repair the workspace skeleton:

```bash
python3 .agents/skills/learning-unit-ingest/scripts/init_learning_workspace.py --learning-root learning
```

Validate after every build, rename, map edit, or manifest edit:

```bash
python3 .agents/skills/learning-unit-ingest/scripts/validate_learning_workspace.py --learning-root learning
```

For roadmap canvas edits, also validate JSON parseability and edge integrity. At minimum, parse the `.canvas` file and check that every `fromNode` and `toNode` exists in `nodes`. When the canvas has third-level explanation nodes, verify their explanation edges are gray, use `toEnd: "none"`, and have matching vertical centers with their second-level concept nodes.
