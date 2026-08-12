---
name: paper-md-ingest
description: Convert research paper titles, arXiv IDs, official paper URLs, or research topics into an Obsidian-friendly `papers/` literature workspace. Use when adding papers, extracting verified public HTML figures into reading notes, fetching arXiv HTML/source/PDF, generating agent-readable `paper.md`, initializing reading notes with source links and expanded sections, updating `PAPERS.md`, and maintaining project maps or cross-project topic indexes with Obsidian links, embeds, and backlinks.
---

# Paper MD Ingest

## Goal

Add research papers to an Obsidian-friendly `papers/` workspace as Markdown that agents and humans can read efficiently. Store stable paper materials under `papers/library/<paper-id>/`, project-specific reading maps under `papers/projects/`, and project-independent aggregation indexes under `papers/topics/`. Store `paper.md` as the primary full-text material and one reading-note `.md` file as the canonical Obsidian note for each paper. Do not store raw HTML, browser `_files/` folders, source archives, or PDFs unless explicitly requested.

This skill assumes Obsidian by default. Use wikilinks, aliases, embeds, backlinks, and lightweight frontmatter as first-class parts of the literature workflow.

## User Preferences (`preferences.toml`)

Two files work together to keep the skill portable across users:

| File | Role | Git-tracked |
|------|------|-------------|
| `preferences.example.toml` | Fully documented template — every option with its default value and inline comments. | Yes |
| `preferences.toml` | Real user config — created by copying the example. | No (gitignored) |

When `preferences.toml` does not exist (or `initialized` is `false`), all scripts fall back to built-in defaults. The agent detects this and guides the user through first-time setup.

### First-time setup (agent-guided)

When `preferences.toml` is missing or `initialized` is `false`, the agent must guide the user through a one-time setup **before** running any ingest:

1. Copy the example file: `cp preferences.example.toml preferences.toml`.
2. Ask concise questions and fill in the answers.
3. Set `initialized = true` and save.

Questions to ask:

1. **PDF parser**: LiteParse (`lit`, recommended, supports figure extraction) or a text-only fallback (`pdfplumber` / `pypdf`)?
2. **Figure extraction from PDF**: Should the pipeline auto-extract figures from PDF-only papers? (default: yes)
3. **PicGo cloud upload**: Should extracted figures be uploaded to cloud storage via PicGo CLI? If yes, confirm `picgo` is installed (`npm install -g picgo`) and configured (`picgo set`) with an image bed such as OSS, COS, SM.MS, or GitHub.
4. **OCR language**: Default Tesseract language for scanned PDFs — `eng` (English), `chi_sim` (Simplified Chinese), or `eng+chi_sim` (both)?

After setup, read preferences silently and never re-ask. Users can also edit `preferences.toml` directly at any time; the agent re-reads without asking. See `preferences.example.toml` for the full schema with inline comments.

### How scripts use preferences

- `ingest_papers.py` reads `[pdf_parser].tool` to choose the parser and `[figures]` settings for figure extraction. It prints a notice to stderr when preferences are not yet initialized.
- `extract_pdf_figures.py` reads `[figures]` thresholds (min dimensions, max count, aspect ratio) and `[figures].upload_via_picgo` to gate cloud upload.
- CLI flags always override preferences — e.g., `--no-picgo` forces text-only even when `upload_via_picgo = true`.

## Workflow

1. **Check `preferences.toml`** next to `SKILL.md`. If it does not exist or `initialized` is `false`, guide the user through the one-time setup described in [User Preferences](#user-preferences-preferencestoml) — copy `preferences.example.toml` to `preferences.toml`, fill in answers, set `initialized = true`. If already initialized, use the stored preferences silently. Then inspect the target `papers/` workspace before ingesting. If it is missing or immature, read the `obsidian-vault` skill's [Workspace Bootstrap](../obsidian-vault/references/workspace-bootstrap.md) reference and initialize missing basics such as `AGENTS.md`, `PAPERS.md`, `library/`, `projects/`, `topics/`, and an optional project map or topic index.
2. If the user gives paper ids, titles, or official URLs, resolve each paper directly.
3. If the user only gives a topic, project goal, or research direction, first ask concise follow-up questions until the scope is clear enough to search. If the user already provided a concrete goal, infer reasonable search axes and proceed.
4. For topic-based discovery, search arXiv first. Unless the user specifies a count, curate 5-10 papers. Prefer a balanced set that covers core benchmarks, infrastructure/framework papers, methodology/survey papers, and project-specific risks.
5. Convert the selected papers into a manifest with concise summaries in the user's working language before ingesting. Add project relevance only when the user explicitly supplies a project or the paper's project ownership is already clear from the request.
6. Prefer official arXiv HTML. Convert it to `paper.md` and retain figure images as remote Markdown links. If a legacy paper has no official HTML, a public HTML rendering mirror may supply figures, but the canonical note source remains the official arXiv/PDF URL.
7. If HTML is unavailable, download the official arXiv PDF (`https://arxiv.org/pdf/<id>`), read `references/conversion.md`, check or install the pinned `lit` CLI (unless `[pdf_parser].tool` in `preferences.toml` specifies a different parser), route OCR with `lit is-complex`, and convert the PDF into a validated temporary Markdown file before replacing `paper.md`. PDF is preferred over the TeX source because it preserves structure (headings, tables, lists) and supports figure extraction. When `[figures].extract_from_pdf` and `[figures].upload_via_picgo` are enabled in `preferences.toml`, the extraction pipeline (`scripts/extract_pdf_figures.py`) automatically extracts figures from the PDF, uploads them to cloud storage, and rewrites the Markdown with public HTTPS URLs. See [PDF Figure Extraction with PicGo](references/conversion.md#pdf-figure-extraction-with-picgo) in the conversion reference.
8. If the PDF is also unavailable, use arXiv source and convert the TeX tree to `paper.md` as a last resort. The TeX fallback strips figure, table, equation, and list environments, so it produces only narrative text.
9. Create or update one reading-note `.md` file under `library/<paper-id>/` in the user's working language as the canonical Obsidian note for the paper. `NOTES.md` is the default; a short title filename is allowed when it improves human navigation. When `paper.md` exposes usable HTML figures, select the one to three that explain the paper's mechanism, protocol, or main result and add them to the note with a concise reading cue; omit decorative or redundant figures.
10. Add a `source` field in the reading note frontmatter pointing to the best human-readable official source, usually arXiv HTML or official PDF. New reading notes must also use the Boolean property `read: false` so Obsidian renders an unchecked checkbox. Never infer `read: true` from ingest completion, note depth, or agent-generated annotations; only the user marks a paper as read.
11. Update `PAPERS.md` manually after batch generation.
12. Update `projects/<project>.md` only when the request explicitly identifies that active project or establishes unambiguous project ownership. A radar action alone does not establish project ownership. When no project is named, keep the canonical note project-neutral and use an existing topic index only when the grouping is genuinely long-lived.
13. If the paper belongs in a project-independent long-term grouping, create or update the relevant `topics/<topic>.md` index instead of inventing a project map.
14. Run `scripts/validate_papers_workspace.py` and fix every broken Markdown link, Obsidian wikilink/embed, missing heading target, missing `paper.md`, missing reading note, missing `id/source` frontmatter field, legacy paper-note `status`, and non-Boolean `read` value. For roadmap canvas edits, also validate that the `.canvas` file is parseable JSON and every edge references an existing node.

## Directory Shape

```text
papers/
  AGENTS.md
  PAPERS.md
  library/
    <paper-id>/
      <reading-note>.md
      paper.md
  projects/
    <project>.md
    <project> roadmap.canvas
  topics/
    <topic>.md
```

Use bare arXiv ids without version suffix for directory names, such as `library/2509.16779`. Use a stable slug for non-arXiv papers, such as `library/webaccessbench`. The default note filename is `NOTES.md`; a concise paper-title filename is also acceptable when it improves browsing. Whenever the note filename changes, update every project map and `PAPERS.md`, then run the validator.

For new or partially formed workspaces, use the `obsidian-vault` skill's [Workspace Bootstrap](../obsidian-vault/references/workspace-bootstrap.md) reference before ingesting papers.

## Dependencies

This skill relies on two shared skills for Obsidian conventions:

- **`obsidian-markdown`** — for Obsidian syntax (wikilinks, embeds, callouts, footnotes, Mermaid diagrams, properties). Follow its rules for callout expand/collapse, formula explanations, terminology footnotes, and diagram conventions. Do not re-state those rules here.
- **`obsidian-vault`** — for vault workspace architecture (directory shape, `AGENTS.md` seed, project-map and topic-index navigation patterns, roadmap canvas conventions, workspace validation). Read its [Navigation Maps](../obsidian-vault/references/navigation-maps.md) reference before creating project maps or topic indexes. Read its [Roadmap Canvas](../obsidian-vault/references/roadmap-canvas.md) reference before creating `.canvas` files.

Treat the non-`paper.md` reading note under `library/<paper-id>/` as the canonical Obsidian note for a paper. Treat `projects/<project>.md` as the human and agent reading entry for a project; treat `topics/<topic>.md` as a cross-project navigation index, not a second paper store or a project map.

### Project association gate

`## 与当前项目的关系` / `## Relationship to Current Project`, the manifest `relevance` field, and a project-map update are all optional. Add them only when the request names a project, or when an existing project map is the paper's clearly established owner. Do not infer a project from the paper's topic, tags, or a `knowledge-radar-actions` receipt. When the condition is absent, omit the section entirely; backlinks and a topic index already provide discovery without inventing a project relationship.

## Script

Use `scripts/ingest_papers.py` for deterministic fetching and conversion. Resolve the script from the installed or loaded `paper-md-ingest` skill directory; do not assume any fixed install root.

```bash
PY="${PY:-python3}"
PAPER_MD_INGEST_DIR="<path-to-installed-paper-md-ingest>"
ROOT="papers"
"$PY" "$PAPER_MD_INGEST_DIR/scripts/ingest_papers.py" --manifest batch.json --papers-root "$ROOT"
```

After every ingest, rename, or project-map edit, run:

```bash
PY="${PY:-python3}"
PAPER_MD_INGEST_DIR="<path-to-installed-paper-md-ingest>"
ROOT="papers"
"$PY" "$PAPER_MD_INGEST_DIR/scripts/validate_papers_workspace.py" --papers-root "$ROOT"
```

When a run adds or changes reading-note figures, also run the network-backed check:

```bash
"$PY" "$PAPER_MD_INGEST_DIR/scripts/validate_papers_workspace.py" --papers-root "$ROOT" --check-remote-images
```

For fast incremental verification after editing only a few files (e.g. a reading note, a topic index, and `PAPERS.md`), pass `--files` so the per-file checks (markdown links, remote images, wikilinks) run only on those files. Structural checks (`library/` integrity, `PAPERS.md` inventory coverage) still run over the whole library, and wikilink targets resolve against the whole-library stem index, so cross-file integrity is preserved. This turns a full-library image sweep into a sub-second check:

```bash
"$PY" "$PAPER_MD_INGEST_DIR/scripts/validate_papers_workspace.py" --papers-root "$ROOT" --check-remote-images \
  --files "papers/library/<paper-id>/<note>.md" "papers/topics/<topic>.md" "papers/PAPERS.md"
```

Remote image checks run in parallel (`--image-workers`, default 16) and retry transient TLS errors, so full-library sweeps stay practical when you do need them.

Manifest schema:

```json
[
  {
    "id": "2509.16779",
    "title": "Improving User Interface Generation Models from Designer Feedback",
    "authors": "Wu et al.",
    "year": 2025,
    "read": false,
    "tags": ["feedback-learning", "designer-feedback", "ui-generation"],
    "source": "arxiv:2509.16779",
    "note_filename": "Improving UI Generation from Designer Feedback.md",
    "summary": [
      "核心贡献：用 1-2 句直白语言说明论文做成了什么。",
      "领域痛点：说明它处理的现实问题，以及为什么值得关注。"
    ],
    "figures": [
      {
        "url": "https://example.org/figure-1.png",
        "alt": "Figure 1: concise accessible description",
        "caption": "图 1：原图表达的机制或实验关系。",
        "takeaway": "阅读提示：这张图应如何帮助理解方法。"
      }
    ],
    "notes": {
      "problem_definition": "具体问题、重要性，以及既有方案的根本瓶颈。",
      "method": "逐模块解释方法；困难部分可在对应核心要点后用 QUESTION 类型 callout 补充简洁问答和具体例子。",
      "experiments": "实验支持哪些主张、关键图表如何阅读，以及证据是否充分。",
      "limitations_open_questions": "真实局限、部署风险和自然延伸出的开放问题。"
    },
    "relevance": "可选：仅在请求明确指定项目时，写该论文与项目的关系。"
  }
]
```

For non-arXiv papers, set `source` to an official PDF URL and set `id` to a stable slug. `note_filename` is optional; omit it to use `NOTES.md`, or provide a concise safe filename when a short title improves browsing.

## Topic Discovery Requirements

When starting from a topic or project goal instead of known papers:

- Ask follow-up questions only when the goal is too broad, ambiguous, or missing the target domain.
- If the user has provided a concrete project goal, proceed with best-judgment arXiv search instead of blocking on questions.
- Default to 5-10 papers when the user does not specify a count.
- Record the search framing in the project map so future readers know why these papers were selected.
- Favor official arXiv ids and links. Use non-arXiv official PDFs only when a key source is not on arXiv.
- Do not treat arXiv search ranking as enough; curate for coverage across benchmark design, execution environment, evaluation fairness, reproducibility, transparency, and domain-specific benchmark examples.

## Reading Note Requirements

Each `library/<paper-id>/<reading-note>.md` note must have frontmatter:

```yaml
---
id: <paper-id>
title: '<title>'
year: <year>
read: false
source: '<official html/pdf/source url>'
tags:
  - <tag>
---
```

`read` is an Obsidian Checkbox backed by an unquoted YAML Boolean. Every newly ingested note starts with `read: false`; the user changes it to `read: true` after personally reading the paper. Do not add `status` to paper reading notes. In an existing migrated workspace, an already-read note may omit `read`; the validator accepts that convention, while any present `read` value must be exactly `true` or `false`.

The body must use the user's working language, inferred from the request and manifest. Keep the section structure equivalent even when translating headings.

### Voice and plain-language style

Write like a sharp senior researcher teaching an intelligent newcomer who is busy, not like a paper abstract restated in Chinese. The target tone is the same as a clear hallway explanation: direct, concrete, and slightly conversational without slang or filler.

Hard rules:

- **Plain language first, jargon second.** Lead with what the system does in ordinary words; introduce the paper's term immediately after, with a footnote marker when the term is a real comprehension blocker. Prefer “把历史压进固定大小的矩阵，再轻轻扳一下 attention 方向” over stacking undefined English nouns.
- **One causal chain per paragraph.** Say what breaks, what the method changes, and what that enables. Do not pile background citations, acronym expansions, and results into the same sentence.
- **Prefer scenes and jobs over taxonomy dumps.** “长程助手不能只答当前这一句，还得记住以前发生过的事” beats “面向 long-horizon agentic scenarios 的 memory-augmented LLM systems”.
- **Keep technical teeth.** Notation, thresholds, component names, and benchmark numbers stay exact. Plain language explains them; it does not replace them with vague paraphrase.
- **Short sentences and active verbs.** Cut throat-clearing openers, symmetrical three-part slogans, and review-article cadence. If a sentence needs a second read, split it.
- **Tables may use plain column headers.** Headers such as `白话`, `主要卡点`, `缺了会怎样` are encouraged when they help scanning; keep the cell content concrete.
- **Reading cues stay operational.** Figure captions should tell the reader what to inspect, not restate the image title.

Anti-patterns to reject:

- Encyclopedia tone: definition lists with no “why it matters here”.
- Abstractese: “提出一种新颖框架以有效提升复杂场景下的综合表现”.
- Jargon carpet-bombing: a paragraph that only natives of the subfield can parse.
- Footnote-shaped body text: burying the only explanation of a key term in dense prose with no marker and no `## 概念注释` entry.

### Table-first comparisons

Use a compact Markdown table whenever the content compares three or more parallel items through repeated dimensions. Typical cases include task or capability levels, component responsibilities, method variants, benchmark settings, claim-to-evidence mappings, and systems compared by the same attributes. If a paragraph repeatedly expresses `<item> -> <scope> -> <requirement/result>`, convert it into rows and make those repeated fields the columns.

Keep prose before or after the table only for the causal conclusion, caveat, or reading guidance that the cells do not express. Do not restate every row in prose. Keep numbered lists for genuine execution sequences where order and dependency matter more than side-by-side comparison, and keep prose for a single causal chain without stable repeated fields.

```markdown
## 高层摘要

用 1-2 句直白语言说明核心贡献，让没有读过论文的人也能理解。
指出它处理的领域痛点，以及为什么值得关注。 ^summary

## 问题定义

论文具体解决什么问题？为什么重要？既有方法的根本瓶颈是什么？
能列表或表格时，用读者能扫懂的对比说明旧方案卡在哪里。

## 方法

先给出端到端总览，再按论文的实际模块逐一解释输入、处理、输出和控制信号。公式先解释物理意义，再给公式和符号。

当某个核心要点仅靠直接说明仍然难以理解时，可紧跟该要点补充简洁的 Q&A。Q&A 用 Obsidian 的 QUESTION 类型 callout 呈现：问题作为 callout 标题，答案作为正文。Q&A 是局部可选解释，不得单独设章，也不得集中收纳与不同要点相关的问题：

> [!QUESTION]- 这个步骤为什么需要？
> 先说明直觉，再用一个具体例子走完该步骤。

## 实验：证据如何支撑结论

说明每组实验要支持哪项主张、关键图表与数字应如何阅读、证据是否充分，以及缺少哪些 baseline 或 ablation。
主张列写成读者能直接反驳的判断句，不要写成空泛的“有效性”“优越性”。

## 局限与开放问题

直接说明真实局限、部署或实践风险，以及自然延伸出的后续研究方向。

## 概念注释

在术语首次出现处挂脚注标记，例如 `harness[^harness]`。这里集中放置定义；每条必须同时说明“是什么”和“在本文里干什么”：

[^harness]: **Inference harness（推理编排层）**：套在模型外面的运行时，负责多轮循环、工具调用和上下文管理。本文训练的是“模型 + 真实 harness”，不是裸 completion。
```

`## 与当前项目的关系` 是可选章节。只有 manifest 提供非空 `relevance`，且该关系来自请求中指定的项目时才写入；没有项目上下文时不要留下空标题、`TODO` 或泛泛的关联判断。

Keep the 30-second summary short and stable. It must contain both the core contribution and the domain pain point; end its final line with the fixed block id `^summary` so project maps can embed only the summary content via `![[...#^summary]]`. Use the expanded sections for single-paper reading and future agent handoff. If the paper has not been deeply read yet, write a conservative initial note and mark uncertain details in the user's working language rather than overclaiming.

Do not add separate `基本信息` / `Basic Info`, `论文定位` / `Paper Positioning`, or `主要贡献` / `Main Contributions` sections. Frontmatter already carries metadata, the high-level summary carries the core contribution, and Problem Definition carries only the prior-work context needed to understand the paper's problem.

### Terminology Footnotes

Follow the terminology footnote rules in the `obsidian-markdown` skill, and treat `## 概念注释` as a required quality surface rather than an optional appendix dump.

Requirements:

- Place the marker at the **first meaningful occurrence** in the body (`term[^id]`). Do not leave definitions only in the end section with zero markers, and do not mark the same term repeatedly.
- Collect definitions under `## 概念注释` / `## Terminology Notes` near the end. Every marker has exactly one definition; every definition is referenced at least once.
- Each entry must answer both: **what it is** and **what role it plays in this paper**. One or two plain sentences beat a dictionary gloss.
- Prioritize note-specific blockers: method jargon, training objectives, evaluation protocols, system components, and paper-coined names. Skip common terms the target reader already knows.
- Use stable lowercase ids such as `[^deberta]`, `[^grpo]`, `[^train-deploy-mismatch]`.
- When a Chinese plain gloss helps, put it in parentheses after the bold term: `**Delta-rule / 残差写入**` or `**pass@k / pass³**`.
- A reading note that introduces specialized machinery without a usable `## 概念注释` section is incomplete.

### Formula and Complex-Concept Callouts

Follow the formula callout rules in the `obsidian-markdown` skill. After equations in `方法`, `实验：证据如何支撑结论`, and any user-requested additions, choose the callout's default state by **relevance and length**: expand (`> [!NOTE]+ 公式解释`) when the unpacking is essential to the surrounding passage and is not long; collapse (`> [!NOTE]- 公式解释`) when it is long or supplementary. Do not collapse every formula callout by default. Explain the equation's physical meaning before presenting the formula. The formula callout requirement applies throughout the reading note whenever an equation carries part of the method.

### Method: blocking completeness requirement

`## 方法` / `## Method` is the main handoff surface. A one-sentence description, a list of component names, or a restatement of the abstract is incomplete and must not be handed off as a reading note.

Read the paper's method sections in `paper.md` before drafting this section. Start with one short end-to-end overview, then use `###` subheadings to make the mechanism executable in the reader's head. Each relevant subheading must state the concrete input or state, transformation steps, output or state change, and the signal that controls, validates, or terminates the step. Preserve original notation, equations, schemas, action names, and thresholds when they carry the mechanism; explain them in the user's working language instead of replacing them with generic prose.

Cover the applicable items below. Omit only items the paper truly does not define, and say what remains unspecified when that absence matters:

- **System / agent**: components, their visible state, data and control flow, tool or action semantics, memory writes, feedback loop, termination, and error or rollback path.
- **Algorithm / training method**: objective or reward, inputs and outputs, each iteration or decision step, learned versus fixed parts, and inference-time behavior.
- **Benchmark / dataset**: task contract, instance schema, source data, construction pipeline, splits, human or automatic validation, evaluator, metrics, hidden information, and contamination or leakage controls.
- **Cost / resource method**: budget definition, accounting units, expansion or stopping rule, and what qualifies as a successful low-cost run.

For complex methods, include a numbered lifecycle, a compact formula or schema when the paper gives one, and a small running example or failure case when it clarifies a branch. When a mechanism is hard to understand from a direct explanation alone, optionally place a QUESTION callout immediately after the relevant core point: the question goes in the callout title and the answer in the body (`> [!QUESTION] <question>` / `> <answer>`). Treat Q&A as a local explanation attached to that point: never create a standalone Q&A heading or section, and never collect questions about unrelated points in one place. Use plain questions and direct answers. Choose the callout's default state by the expand/collapse principle in the `obsidian-markdown` skill — since Q&A is supplementary, it leans collapsed (`> [!QUESTION]-`) unless the answer is short and essential. Do not force Q&A into simple points or papers.

Apply the formula-callout requirement whenever an equation carries part of the method: reproducing the equation without explaining its parameters and overall relationship is incomplete. Place benchmark-specific validation and evaluator details in this section or directly beside it, not only under experiments or limitations. Before handoff, check that a reader can answer: “what enters the method, what changes at each step, why it advances or stops, and what artifact is judged?”

### Key Figure Requirements

Use `## 关键图示` / `## Key Figures` when the paper exposes a figure that materially improves understanding — whether from public HTML or auto-extracted from a PDF-only paper and uploaded via PicGo. Insert the section after `方法` / `Method` and before `实验：证据如何支撑结论` / `Experiments (How They Prove It)`. Each selected figure must use a direct, public `https://` image URL from the paper's official HTML, a clearly identified public HTML rendering mirror, or a PicGo-uploaded cloud URL for PDF-only papers; never use `data:` URLs, local files, screenshots, logos, UI decoration, or unverified search thumbnails. Verify that the URL returns an image before writing it. Keep the original figure number or caption in a short sentence, then add one Chinese/working-language sentence explaining what to inspect. A paper may have no suitable figure; do not add a placeholder or force an image merely for visual variety.

For manifest-driven generation, pass selected figures through the optional `figures` list. `ingest_papers.py` writes them into the canonical note, but does not choose their semantic relevance: inspect `paper.md` and its captions first. The usual target is one figure; use two or three only when they explain distinct necessary mechanisms. For PDF-only papers without manifest figures, the ingest script auto-extracts and uploads figures via PicGo when `[figures].upload_via_picgo` is enabled in `preferences.toml`; review and caption them manually after the run.

## Project Map Requirements

When a batch is tied to a project, create or update `projects/<project>.md`. Project maps are the primary human/agent reading entry for project-specific literature. Follow the navigation-map conventions in the `obsidian-vault` skill's [Navigation Maps](../obsidian-vault/references/navigation-maps.md) reference for wikilink + embed + backlink patterns.

Paper-specific project-map content:

- A project title and short project goal.
- A paired roadmap canvas embedded near the top (see `obsidian-vault` [Roadmap Canvas](../obsidian-vault/references/roadmap-canvas.md)).
- A `主题聚合` section with project-specific groupings by problem, module, decision, or reading stage; every paper listed there must include an inline `![[...#^summary]]` block embed on the same bullet.
- A `推荐阅读路径` section after `主题聚合`, with ordered wikilinks and one-line reasons.
- Wikilinks to every referenced paper note using the `^summary` block id.

Strongly recommended:

- Lightweight frontmatter with `type: note`, `status`, `visibility`, and `literature-map` tags.
- A search framing section when papers were discovered from a topic or project goal.
- A `阅读关注点` section only when useful, for close-reading cues, open questions, or follow-up paper gaps. Do not add a generic `设计笔记` section by default.

Do not duplicate `paper.md` or reading notes in project folders.

## Topic Index Requirements

Use `papers/topics/<topic>.md` when the requested grouping is long-lived and independent of a specific project, such as classics, a method family, or a benchmark category. Follow the topic-index pattern in the `obsidian-vault` skill's [Navigation Maps](../obsidian-vault/references/navigation-maps.md) reference. Paper-specific requirements:

- Link only to canonical reading notes in `library/`; use `![[...#^summary]]` for compact recall when helpful.
- Do not create a roadmap canvas, duplicate paper note, or topic-specific raw-material directory.

## PAPERS.md Requirements

Keep `PAPERS.md` as a lightweight global inventory and audit list, not the primary reading interface. Project-specific reading belongs in `projects/<project>.md`, and cross-project curated paths belong in `topics/<topic>.md`; `PAPERS.md` exists for de-duplication, quick whole-library scanning, and checking that every library item is indexed. Each entry should include:

```markdown
- [<paper-id> <title>](library/<paper-id>/<reading-note>.md)
  - Tags: `<tag>`, `<tag>`
  - Summary: <two or three concise sentences in the user's working language>
  - Source: <official source URL>
```

Prefer concise entries in `PAPERS.md`. Put richer reading paths, rationale, and synthesis in project maps.

Do not create `papers.jsonl` unless the user explicitly asks for a later indexing phase.

## Validation Requirements

Run the validator after every ingest, note rename, `PAPERS.md` edit, or project-map edit:

```bash
PY="${PY:-python3}"
PAPER_MD_INGEST_DIR="<path-to-installed-paper-md-ingest>"
ROOT="papers"
"$PY" "$PAPER_MD_INGEST_DIR/scripts/validate_papers_workspace.py" --papers-root "$ROOT"
```

The validator must pass before handing off. It checks library structure, reading-note frontmatter, the absence of legacy paper-note `status`, Boolean syntax for `read` when present, `PAPERS.md` inventory coverage, Markdown links, Obsidian wikilinks/embeds, and embedded heading targets. `--check-remote-images` additionally fetches selected figures and requires `image/*`; use it whenever figures change.

For roadmap canvas edits, follow the canvas JSON validation rules in the `obsidian-vault` skill's [Roadmap Canvas](../obsidian-vault/references/roadmap-canvas.md) reference: parse the `.canvas` file, check that every `fromNode` and `toNode` exists, and verify explanation-edge colors and alignment.
