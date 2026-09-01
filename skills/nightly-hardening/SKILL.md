---
name: nightly-hardening
description: >
  Night pass from a given branch (default: current) via a new branch and git
  worktree: autonomously improve the repo, phase-commit, subagent quality
  review with fixes, then a draft PR into the source branch. Default: pick
  tractable open issues, or apply improve-codebase-architecture and
  trim-and-deepen heuristics — start immediately unless the user asked for a
  plan to review first. Invoke with /nightly-hardening or $nightly-hardening,
  or when the user asks for a nightly / evening pass, 晚上自己改, 从当前分支
  开工作树自主改进. Manual only — do not auto-run on generic "improve the
  codebase", "open a PR", "work on #N", or /issue-worktree-pr. Do not
  implement on a dirty primary checkout. Do not merge the PR.
---

# Nightly hardening

One evening increment: isolate from the **source branch**, improve, phase-commit,
quality-fix, draft PR. Not `$issue-worktree-pr` (that delivers **one** issue
from `main`).

Companion skills (read when that step runs; do not copy their rules here):

| Step | Skill |
| --- | --- |
| Phase commits | `$staged-commit-message` (phase-during-work / Commit) |
| Default discovery | [references/discover.md](references/discover.md); `$improve-codebase-architecture` explore heuristics if installed |
| Late simplify | `$trim-and-deepen` **TRIM track only**, if installed |
| Quality | one completion subagent ([references/review.md](references/review.md)) that **reviews and may edit** |
| Draft PR | [references/pr.md](references/pr.md) — match this repo's existing PRs to the source branch |

## Modes

| Mode | When | Action |
| --- | --- | --- |
| **Execute** (default) | `/nightly-hardening`, 晚上自己改, no plan-first phrase | Isolate → implement → commit → review → draft PR |
| **Plan-first** | 先列出大纲 / 改进计划 / 供我审阅 / plan first / don't start yet / 先别动手 | Discover, present the plan, **stop**. No worktree, no edits, no PR |

Default is **run**. A short "tonight I will…" line in the first reply is fine; do not wait for approval.

If the user named concrete work, that is the whole scope. Do not add unrelated issues.

## Defaults

- **Base:** the branch the user named; else the primary clone's current branch. Start from `$UPSTREAM/$BASE` after fetch when that ref exists — do not fold local-only commits or uncommitted dirt into the nightly PR.
- **Isolation:** always `git worktree add` + new branch. Never commit on the caller's dirty primary tree.
- **Branch:** `feat/nightly-<slug>` — slug from the named theme, else `<base>-<YYYYMMDD>`. ASCII kebab, ≤40 chars. Collision → append `-2`.
- **PR:** `--draft`, `--base <source-branch>`, head = the nightly branch. Do not merge, tag, rebase-onto-base, or force-push.
- **Reply language:** match the user. PR title/body: match recent PRs to that base (see [references/pr.md](references/pr.md)).
- One coherent PR per worktree. Several small related slices are OK; two ownership areas with no sequencing → pick one tonight.

## Workflow

### 1. Resolve base and remote

In the **existing** clone (read-only for this step):

1. `git remote -v` + `gh repo view` → canonical remote `UPSTREAM` (same rule as `$file-github-issue`).
2. Source branch `BASE`: user-named, else `git branch --show-current`.
3. `git fetch "$UPSTREAM" "$BASE"` when that remote branch exists.
4. `START_REF` = `$UPSTREAM/$BASE` if fetched, else local `$BASE`. If local HEAD has extra commits vs `START_REF`, say so and **leave them out**.
5. Confirm this checkout is **not** already a nightly worktree for the same slug.

Stop if `BASE` is missing or remotes disagree with no write access.

### 2. Discover tonight's work

Read [references/discover.md](references/discover.md).

Order:

1. **User-named work** — that is the spec. Restate problem / approach / non-goals / acceptance in the reply, then proceed (or stop if plan-first).
2. **Else tractable issues** — small, unblocked, one ownership area. Prefer Hub/GUI for an already-shipped CLI or API, leftover rename residue, fail-closed bugs with a test, docs drift vs the real surface.
3. **Else (or fill remaining room)** — `$improve-codebase-architecture` **explore** heuristics and `$trim-and-deepen` TRIM-sized work. Skip that skill's HTML report and grilling loop. Do not land interface/ownership moves.

Cap: one night, one PR. Name what you deferred.

Plan-first: present the outline (base, branch name, slices, non-goals, checks) and **stop**.

### 3. Isolate

Worktree path is a **sibling** of the repo root, never inside it:

```bash
ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$ROOT")
NAME=$(basename "$ROOT")
git worktree add -b "$BRANCH" "$PARENT/${NAME}-wt-nightly-${SLUG}" "$START_REF"
```

`$START_REF` is `$UPSTREAM/$BASE` when fetched, else the local base HEAD.

If that path exists, stop and reuse or pick a new slug — do not clobber.

All later commands run with cwd = that worktree.

### 4. Phase the increment

Read the target repo's agent/architecture docs **in the worktree** before editing (`AGENTS.md`, `ARCHITECTURE.md`, `docs/design/`, issue Acceptance).

Each phase:

1. Implement that slice only.
2. Focused tests for that slice (repo's documented gate, not invented CI).
3. Stage **only** those paths. Follow `$staged-commit-message` Commit / phase-during-work. No `git add .`.
4. Next phase on a clean tree.

Do not implement everything and split commits at the end.

If an issue says design-first, Phase 0 is **only** the cited design/docs paths.

Preserve unrelated dirt in the **primary** checkout. Never `git reset --hard` there.

### 5. Trim

If `$trim-and-deepen` is installed, run it on the **branch diff vs `$START_REF`**. TRIM only. Do not run DEEPEN (notes or implementation) unless the user asked. Commit trim as its own `refactor` / `chore` phase if it is non-trivial.

If the skill is missing, skip. Do not invent a second trim procedure.

### 6. Quality subagent

Spawn **one** subagent against this worktree. Prompt from [references/review.md](references/review.md). It **may edit** for blocking quality issues in-scope.

Then the executor phase-commits those fixes (`$staged-commit-message`) and follows the round cap in [references/review.md](references/review.md). Cheap follow-ups now; otherwise name them in the PR and do not claim done.

Skip only if the user said so, or the change is docs-only with no code path.

### 7. CI-equivalent

Before opening the PR, run what **this repo** documents for push / PR (path-filtered jobs in `.github/workflows/` or `AGENTS.md`). Do not invent a full matrix. Do not skip because "only docs" unless the workflow files agree.

Failing CI-equivalent → fix in the worktree, do not open the PR.

### 8. Draft PR + report

Read [references/pr.md](references/pr.md). Push the nightly branch, open `--draft` against `BASE`, reply with the PR URL and a change summary in the user's language.

Do not merge. Do not delete the worktree unless the user asks.

## Guardrails

- No secrets in commits, PR body, or evidence paths.
- No host-absolute paths in tracked docs.
- PASS / product verdicts stay whatever the target repo already owns.
- Do not push from the user's primary dirty checkout.
- Do not take irreversible, credential, or product-security semantic work without the user asking.
- Do not claim evidence grades, full-suite green, or "done" for paths the repo's CI skipped.
- Public/reader docs must not use GitHub issue numbers if the target repo forbids that.

## Tiny examples

**Default execute** — user: `/nightly-hardening`

```text
Base = current branch (e.g. canary). Discover issues or small hardenings.
Worktree + feat/nightly-canary-YYYYMMDD. Implement, phase-commit, review, draft PR → canary.
```

**Named work** — user: `/nightly-hardening` Hub 补上 CLI 已有的组织创建

```text
Scope = that GUI gap only. Same isolation and PR path. Do not wander into unrelated issues.
```

**Plan-first** — user: `/nightly-hardening` 先列出大纲供我审阅

```text
Discover, print slices / non-goals / checks, stop. Isolate only after they say go.
```
