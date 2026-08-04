---
name: staged-commit-message
description: >
  Draft Conventional Commit message(s) from git changes (default: one commit from
  staged diff, language/style from recent history) and write COMMIT.md. When the
  change set has multiple independent purposes—or the user asks—split into several
  focused commits with explicit file groups for clarity. Use when the user asks to
  draft/update COMMIT.md, prepare commit text from staged files, split a messy
  stage into clean commits, or create local commits without rewriting history.
---

# Staged Commit Message

Default: **one** Conventional Commit, message style from repo history.  
When clarity needs it (or the user asks): **split** into multiple focused commits.

Never invent changes. Prefer evidence from git over chat summary.

## Modes

| Mode | When | Deliverable |
| --- | --- | --- |
| **Draft** (default) | User wants message / `COMMIT.md` | Write `COMMIT.md` only; do not `git commit` |
| **Commit** | User explicitly asks to commit / 提交 | Create local commit(s); still may write `COMMIT.md` if useful |

If unclear, **draft only**.

## Workflow

### 1. Inspect

Run:

- `git status --short`
- `git diff --cached --name-status`
- `git diff --cached --stat`
- `git diff --cached`
- `git log -n 20 --no-merges --pretty=format:%s%n%b`

For **split planning**, also read unstaged/untracked only as candidates to group—do not treat them as already-in-scope unless drafting a multi-commit plan or the user asked to include them.

Do **not** use `git reset --hard`, `git checkout --`, or other destructive discard ops. Preserve unrelated user work.

### 2. Stop early

- **Draft + nothing staged**: if `git diff --cached --quiet`, stop with a short error; do not invent a message.
- **Commit + empty**: same, unless user asked to stage a specific plan first.
- **Secrets / generated junk / unexplainable paths**: stop that part; report path and reason.

### 3. Infer language & style from history

- Prefer Chinese if recent subjects/bodies are mainly Chinese.
- Prefer English if mainly English.
- If mixed, follow the latest non-merge commit language.
- Match local conventions for type vocabulary and scope density (short vs descriptive subjects).

### 4. Decide: one commit vs split

**Default → one commit** covering the staged set.

**Split when** any of these hold:

- User asked to split / 拆分 / multiple commits
- Staged (or agreed working-tree) changes have **independent purposes** (e.g. feat code vs docs-only vs test-only vs chore/version vs unrelated fix)
- A single message would force a vague subject or hide a reviewable unit

**Do not split** only by folder layout. Group by **intent**.

If split is ambiguous, state the proposed groups first (paths + purpose), then write messages / commit.

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

When co-changing UI / data contracts / release process / vault semantics, keep matching docs in the **same logical commit**, or a dedicated `docs` commit next to it—do not leave docs orphaned without reason.

### 6. Write `COMMIT.md`

- Default path: cwd `COMMIT.md` (overwrite, never append).
- Plain commit text only for **single** commit (no fences, no commentary).
- For **multiple** commits, use this structure:

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

<type>(<scope>): <description>

- <point>
```

Order commits so later ones may depend on earlier (base/types before callers; code before pure docs only if docs describe that code).

### 7. Commit mode only (user asked to commit)

For each group, in order:

1. Stage **only** that group's paths (`git add -- path` or `git add -p`); never blind `git add .`.
2. Optional: run the **minimal** check matching that group's risk (if already known in repo). Do not invent a long CI pipeline.
3. `git commit` with the drafted message (HEREDOC / `-F` from a temp message file is fine). Prefer non-interactive.
4. Do **not** amend, rebase, tag, push, or force-push unless the user explicitly requires it.

After all groups: show `git log -n <N> --oneline` and `git status --short`. Confirm remaining unstaged work is intentional.

## Quality rules

- Accuracy over cleverness; no fabricated file changes.
- One purpose per commit when splitting.
- Body bullets ≤5 each.
- Leave unrelated dirty files alone.
- Do not rewrite existing history to “clean up” unless the user orders it.

## Tiny examples

**Single (default)** — only staged harness fix:

```text
fix(sdk): reject completed harness terminal as PASS

- Keep evaluation authority on the independent evaluator path
```

**Split** — feat + docs in one stage:

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
