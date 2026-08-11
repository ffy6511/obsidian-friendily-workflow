---
name: staged-commit-message
description: >
  Draft or create Conventional Commit(s) from git changes. Two operating modes:
  (1) Draft — message text only from currently staged (or agreed) diff;
  (2) Commit — create local commits. Prefer **phase-during-work**: when the user
  asks for multi-phase implementation with staged commits (分阶段提交 / process
  commits / commit as you go), finish one logical phase → commit that phase
  immediately → then start the next phase. Do NOT implement everything first
  and only then split a giant working tree into retrospective commits. Also
  used when the user asks to prepare commit text from staged files, split a
  messy stage into clean commits, or create local commits without rewriting
  history.
---

# Staged Commit Message

## Core rule: phase commits happen **during** the work

When the user wants multi-step delivery with commits (e.g. “分阶段提交”、
“过程中提交”、“commit each phase”、`/staged-commit-message` on a multi-slice
plan):

| Wrong                                                                     | Right                                                     |
| ------------------------------------------------------------------------- | --------------------------------------------------------- |
| Implement S0–S4 completely, then invent commit groups from the final tree | Finish **S0** → commit S0 → finish **S1** → commit S1 → … |
| One mega uncommitted WIP until “done”                                     | Each phase leaves a **reviewable, green-enough** commit   |
| Retrospective `git add -p` storytelling after the fact                    | Commit boundaries match real phase completion             |

**Phase boundary = commit boundary.** After each intentional slice
(design, core, CLI, examples, upload path, Hub UI, …):

1. Stage **only** that phase’s paths (never blind `git add .`).
2. Draft message from **that** staged diff + recent log style.
3. `git commit` (HEREDOC / non-interactive).
4. Continue the **next** phase on a clean tree (or only unrelated dirt left intentional).

Do **not** wait until the full epic is implemented to “split commits for
neatness.” Retrospective splitting is a recovery tool when the tree is already
messy—not the default workflow for multi-phase delivery.

Never invent changes. Prefer evidence from git over chat summary.

## Modes

| Mode                           | When                                                          | Deliverable                                                   |
| ------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------- |
| **Draft** (default if unclear) | User wants message text only                                  | Present message(s) in the reply; do not `git commit`          |
| **Commit**                     | User asks to commit / 提交 / 分阶段提交 / “commit each phase” | Create local commit(s)                                        |
| **Phase-during-work**          | Multi-slice implementation with staged commits requested      | After each phase completes: commit immediately, then continue |

If the user only says “staged-commit-message” without “commit”, **draft only**.  
If they said “分阶段提交” / “过程中提交” / “commit as you go” earlier in the
task, treat ongoing phase boundaries as **Commit** mode without re-asking.

## Workflow

### 1. Inspect

Run:

- `git status --short`
- `git diff --cached --name-status`
- `git diff --cached --stat`
- `git diff --cached`
- `git log -n 20 --no-merges --pretty=format:%s%n%b`

For **phase-during-work**: after finishing a phase, stage that phase’s paths
first, then inspect **cached** diff only for the message. Unrelated dirt stays
unstaged.

For **recovery split** of an already-mixed tree: also read unstaged/untracked as
candidates to group—do not treat them as in-scope unless drafting a multi-commit
plan or the user asked to include them.

Do **not** use `git reset --hard`, `git checkout --`, or other destructive
discard ops. Preserve unrelated user work.

### 2. Stop early

- **Draft + nothing staged**: if `git diff --cached --quiet`, stop with a short
  error; do not invent a message (unless phase-during-work still needs to
  `git add` the just-finished phase first).
- **Commit + empty**: same, unless user asked to stage a specific plan first.
- **Secrets / generated junk / unexplainable paths**: stop that part; report
  path and reason.

### 3. Infer language & style from history

- Prefer Chinese if recent subjects/bodies are mainly Chinese.
- Prefer English if mainly English.
- If mixed, follow the latest non-merge commit language.
- Match local conventions for type vocabulary and scope density.

### 4. Decide: one commit vs split

**Default for a single staged set → one commit.**

**Phase-during-work → one commit per completed phase** (even if the overall task
has more phases left). Do not batch several finished phases into one commit
unless the user asked for fewer commits.

**Recovery split** of one messy stage when:

- User asked to split / 拆分 / multiple commits for an existing tree
- Staged (or agreed) changes have **independent purposes**
- A single message would force a vague subject

**Do not split** only by folder layout. Group by **intent**.

If split is ambiguous, state the proposed groups first (paths + purpose), then
write messages / commit.

### 5. Draft message(s)

Each commit:

```text
<type>(<scope>): <description>

- <point 1>
- <point 2>
```

- `type`: `feat` | `fix` | `refactor` | `perf` | `docs` | `test` | `build` | `ci` | `chore` | `revert`
- `scope`: smallest meaningful module from paths (omit only if history rarely uses scope)
- `description`: one concise line, selected language, no trailing period
- `body`: ≤5 bullets; behavior/intent only—not file laundry lists
- `footer`: only with clear evidence (`BREAKING CHANGE:`, `Refs:`, migration note)

When co-changing UI / data contracts / release process, keep matching docs in
the **same logical commit**, or a dedicated `docs` commit **immediately after**
that phase—not deferred until epic end.

### 6. Present message(s)

- Output plain commit text in the reply (no extra commentary inside the message block).
- **Single** commit: one message only.
- **Multiple** commits (recovery split or multi-phase plan preview):

```text
## Commit 1
paths:
- path/a
- path/b

<type>(<scope>): <description>

- <point>

## Commit 2
paths:
- path/c

…
```

Order so later commits may depend on earlier ones.

Do **not** write a `COMMIT.md` (or other message file) unless the user explicitly
asks for a file.

### 7. Commit mode / phase-during-work

For each group (or the just-finished phase), in order:

1. Stage **only** that group’s paths (`git add -- path`); never blind `git add .`.
2. Optional: minimal check matching that phase’s risk (focused pytest / ruff on
   touched packages). Do not invent a full CI gate every phase unless the user
   asked or the phase is push-critical.
3. `git commit` with the drafted message (HEREDOC / `-F`). Prefer non-interactive.
4. Do **not** amend, rebase, tag, push, or force-push unless the user explicitly
   requires it.
5. **Phase-during-work:** after a successful commit, proceed to the next phase;
   do not accumulate more uncommitted work from later phases first.

After a multi-commit batch (recovery) or at epic end: show
`git log -n <N> --oneline` and `git status --short`. Confirm remaining unstaged
work is intentional.

## Quality rules

- Accuracy over cleverness; no fabricated file changes.
- One purpose per commit when splitting or phasing.
- Body bullets ≤5 each.
- Leave unrelated dirty files alone.
- Do not rewrite history to “clean up” unless the user orders it.
- **Process over packaging:** incremental phase commits beat one perfect
  end-of-epic rewrite.

## Tiny examples

**Phase-during-work** (preferred for multi-slice tasks):

```text
# After S1 code is done and green enough:
feat(config): merge Database profiles.yaml onto role slots

- Fail closed on missing binding; export job_overlay on lock

# …implement S2…
feat(cli): add --profiles and /bindings overrides

- Campaign matrix accepts binding axes
```

**Single (default)** — only staged harness fix:

```text
fix(sdk): reject completed harness terminal as PASS

- Keep evaluation authority on the independent evaluator path
```

**Recovery split** — feat + docs already mixed in one dirty tree:

```text
## Commit 1
paths:
- src/bora/agent/acp.py
- tests/agent/test_acp.py

feat(acp): map session updates into AgentResult

- Normalize stop reasons before evidence attach

## Commit 2
paths:
- docs/design/05-agent-service.md

docs(acp): note permission auto-approve evidence field
```
