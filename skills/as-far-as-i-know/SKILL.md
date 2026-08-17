---
name: as-far-as-i-know
description: >
  Consensus check against this repo: the user states a current-state claim or a
  proposed plan; the agent judges it against local ground truth (docs / code /
  design / conversation), not politeness. Fact mode asks "is this true now?"
  Plan mode asks "does this increment fit the existing contracts?" — never
  scores a plan as wrong because it is not implemented yet. Use when the user
  invokes $as-far-as-i-know / "as far as I know" / "据我所知" / "我的理解是"
  / "我们做成" / "要改进的话应该". Counterpart to $as-the-field-knows. Not for
  open-ended teaching or designing from scratch.
---

# As Far As I Know

User pastes an understanding **or** a planned increment. **Judge it.**
Do not rewrite their plan unless the delta needs a one-line correction.

## Classify first (required)

Decide **现状** vs **规划** from their wording, then stay in that mode.

| Mode | Signals (examples) | Question you answer |
| --- | --- | --- |
| **现状** | 现在是、已经、会、就是、我的理解是（陈述事实） | Is this true in the repo *now*? |
| **规划** | 要改进、应该做成、计划、预期、下一步、我们做成、打算 | Does this increment fit *existing* contracts / approach? |

- Mixed text: score each fragment in its own mode.
- Ambiguous: prefer **规划** when they are choosing what to build; prefer **现状** when they are checking a mental model of today's behavior.
- **Never** treat a 规划 as a missing-feature 现状 claim. "还没做" is not a gap for a plan.

## Workflow

1. **Extract** — Isolate material points. If empty, ask once.
2. **Ground** — Highest-relevant local authority: design/docs, Architecture, code, tests, git/state, prior turns. Prefer evidence over memory. Minimal lookup when a file/command is needed.
3. **Score** — Use the mode's labels. Stay short.

## Reply shape

### 1. 结论 (first, 1–3 lines)

**现状:**

- **共识** — material points match current ground truth
- **部分共识** — some right, some off (name the off parts in one breath)
- **未达成共识** — core claim is wrong or inverted
- **证据不足** — cannot judge (say what is missing)

**规划:**

- **规划对齐** — increment fits existing contracts and approach
- **规划部分对齐** — direction fits; mechanism / wording / a constraint is off (name it)
- **规划冲突** — core plan contradicts a binding contract
- **证据不足** — cannot judge (say what is missing)

Optional one-liner: the single most important correction (for 规划: the mechanism, not a rewrite).

### 2. 论据 (after)

Bullet list only. Each bullet: claim fragment → **match / gap** → a concrete local fact (path, API, design line). No fluff.

规划 bullets judge **fit**, not existence:

- **match** — reuses or extends an existing primitive / invariant
- **gap** — would break a contract, or picks the wrong existing knob
- Do **not** write "当前还没实现所以 gap"

## Rules

- **Verdict first.**
- **Facts over agreement** — do not rubber-stamp; do not nitpick wording when the meaning fits.
- **Scope = their text** — no adjacent architecture unless a silent false assumption would break the work.
- **Unknown is allowed.**
- **Language** — match the user (中文 in → 中文 out).
- **No side quests.**

## Tiny examples

**现状.** User: `$as-far-as-i-know PASS 可以由 harness 的 completed 终端直接给出。`

**未达成共识** — PASS 只能来自独立 evaluator；`HarnessTerminal.completed` ≠ PASS。

- 你的主张：harness completed → PASS → **错**。权威：trajectory/harness 完成态与 evaluation 是独立事实；PASS 仅 evaluator 形成。

**规划.** User: `$as-far-as-i-know 改进的话应该覆盖掉 ERROR 那次，但旧记录还能打开。`

**规划部分对齐** — 旧记录可查对；不要覆盖旧 Attempt，应追加新 identity 并改 suite 指针。

- 「旧记录可查」→ **match**。设计：重试是新 Attempt，不许改旧 identity/score。
- 「覆盖 ERROR 那次」→ **gap**。`--resume-suite` 把 ERROR 当 finished；契约是新 Attempt，不是改写旧槽。
