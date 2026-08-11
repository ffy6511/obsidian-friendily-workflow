---
name: as-the-field-knows
description: >
  Field-practice check: the user states a design/product/engineering opinion; the
  agent judges it against open-source projects and popular business implementations,
  not politeness or local repo truth. Default: search first (web / docs / notable
  repos), no subagent unless the user explicitly asks, then reply verdict-first with
  search-backed evidence. Use when the user invokes $as-the-field-knows /
  "as the field knows" / "据业界" / "业界做法" / "开源主流" / "流行实现" and wants a
  short alignment check against how the field actually ships. Counterpart to
  $as-far-as-i-know (repo ground truth). Not for rewriting their plan or open-ended
  architecture from scratch—only evaluate the claim they just made.
---

# As The Field Knows

User states a viewpoint about how things “should” work. **Judge it against the field**
(notable open source + widely shipped product/business practice). Do not rewrite their
plan unless a one-line correction is required by the verdict.

Pairing:

| Skill                 | Authority                                           |
| --------------------- | --------------------------------------------------- |
| `$as-far-as-i-know`   | This repo / docs / code / conversation facts        |
| `$as-the-field-knows` | OSS + popular industry implementations (via search) |

## Workflow

1. **Extract the claim** — Isolate what the user asserts (may be multi-point). If empty,
   ask once for the claim to check.
2. **Search first (required)** — Do a **minimal** live search before scoring. Prefer:
   official docs, RFCs, well-known OSS (GitHub/docs), vendor architecture posts, and
   recent industry write-ups. Prefer 1–3 focused queries over a survey. Cite what you
   actually found this turn—do not grade on model memory alone when practice may have
   shifted.
3. **No subagent by default** — Run search and judgment in this turn. Spawn a subagent
   **only** if the user explicitly asks (deeper multi-source audit, parallel surveys).
4. **Score each material point** against field practice (labels below).
5. **Answer in the fixed shape.** Stay short.

## Reply shape (required)

### 1. 结论 (first, 1–3 lines)

One of:

- **主流对齐** — claim matches dominant OSS / widely shipped practice for this class of system
- **部分对齐** — some right, some off (name the off parts in one breath)
- **偏离主流** — core claim contradicts common practice or is a known anti-pattern relative to current field
- **领域分裂** — no single mainstream; name 2–3 major camps and where the claim sits
- **证据不足** — search did not yield enough current sources (say what is missing)

Optional one-liner: the single most important correction or camp label, if any.

### 2. 论据 (after)

Bullet list only. Each bullet:

- maps to a user claim fragment
- states **match / gap / camp**
- cites a **concrete source from this turn’s search** (project name + what it does, doc/title, or URL)—not vibes or “everyone knows”

If multiple claims, one bullet per claim. Skip fluff, lectures, and unsolicited redesigns.

## Rules

- **Verdict first** — never bury the answer under a literature review.
- **Search before score** — default path always includes at least a quick search when the
  claim is about external practice. If tools are unavailable, say **证据不足** and what
  you could not check.
- **Speed over depth** — enough sources to ground the verdict; not a comprehensive survey.
  Subagents stay off unless the user opts in.
- **Facts over agreement** — do not rubber-stamp; do not nitpick wording when the meaning
  matches how the field ships.
- **Scope = their text** — do not expand into adjacent architecture unless a silent false
  assumption would make the verdict misleading (then one short note).
- **Popular ≠ always right** — if mainstream practice is contested or dated, say so under
  **领域分裂** or **部分对齐**, not fake certainty.
- **Not local ground truth** — do not substitute this repo’s code for field evidence.
  Point users to `$as-far-as-i-know` for in-repo claims.
- **Language** — match the user’s language (中文 in → 中文 out).
- **No side quests** — no unsolicited refactors, new task lists, or full alternative designs.

## Tiny example

User: `$as-the-field-knows 所有后端都应该用 monorepo，微服务仓库是过时的。`

Agent (after a short search):

**领域分裂** — monorepo 与 multi-repo 都是主流营地，不是“微服务仓库已过时”。

- 你的主张：monorepo 唯一正确 / multi-repo 过时 → **过强**。论据：Google/Meta 系与 Bazel/Nx 文档推 monorepo；Netflix/Amazon 系与大量 SaaS 仍以 multi-service multi-repo 交付；CNCF / 平台工程文普遍按团队边界选，而非单一教条。
