---
name: as-far-as-i-know
description: >
  Consensus check: the user states their current understanding; the agent judges it
  against actual ground truth (repo, docs, code, conversation facts), not politeness.
  Reply with a short verdict first, then evidence. Use when the user invokes
  $as-far-as-i-know / "as far as I know" / "据我所知" / "我的理解是" and wants a
  yes/partial/no alignment check, to verify shared mental model before continuing,
  or to catch silent drift between human and agent. Not for open-ended teaching or
  design from scratch—only evaluate the claim the user just made.
---

# As Far As I Know

User pastes their understanding. **Judge it.** Do not rewrite their plan unless the delta requires a one-line correction.

## Workflow

1. **Extract the claim** — Isolate what the user asserts (may be multi-point). If empty, ask once for the understanding to check.
2. **Ground it** — Check against the highest-relevant authority available now: design/docs, Architecture, Specs, code, tests, git/state, and prior turns. Prefer evidence over memory. If a claim needs a file/command check, do the minimal lookup.
3. **Score each material point** — Correct / Partial / Wrong / Unknown (not enough evidence).
4. **Answer in the fixed shape below.** Stay short.

## Reply shape (required)

### 1. 结论 (first, 1–3 lines)

One of:

- **共识** — material points match ground truth
- **部分共识** — some right, some off (list the off parts in one breath)
- **未达成共识** — core claim is wrong or inverted
- **证据不足** — cannot judge without more facts (say what is missing)

Optional one-liner: the single most important correction, if any.

### 2. 论据 (after)

Bullet list only. Each bullet:

- maps to a user claim fragment
- states **match / gap**
- cites a concrete fact (path, Spec line idea, API name, observed behavior)—not vibes

If multiple claims, one bullet per claim. Skip fluff and lecture.

## Rules

- **Verdict first** — never bury the answer under explanation.
- **Facts over agreement** — do not rubber-stamp to be nice; do not nitpick wording when meaning is right.
- **Scope = their text** — do not expand into adjacent topics unless a silent false assumption would break the work.
- **Unknown is allowed** — say 证据不足 instead of guessing.
- **Language** — match the user's language (中文 in → 中文 out).
- **No side quests** — no unsolicited refactors, new tasks, or long recaps of the whole project.

## Tiny example

User: `$as-far-as-i-know PASS 可以由 harness 的 completed 终端直接给出。`

Agent:

**未达成共识** — PASS 只能来自独立 evaluator；`HarnessTerminal.completed` ≠ PASS。

- 你的主张：harness completed → PASS → **错**。权威：trajectory/harness 完成态与 evaluation 是独立事实；PASS 仅 evaluator 形成。
