---
name: issue-worktree-pr
description: >
  Deliver a GitHub issue or an oral goal from a clean main via a new branch
  and git worktree: phase commits, optional trim, subagent acceptance, local
  CI-equivalent, then a draft PR into main (English). Invoke with
  /issue-worktree-pr or $issue-worktree-pr. Manual only — do not auto-run on
  generic "implement this", "open a PR", or "work on #N" requests. Do not
  implement on a dirty primary checkout. Do not merge the PR.
disable-model-invocation: true
---

# Issue worktree PR

Turn **one** issue or oral goal into a **draft PR** against `main`, on an
isolated worktree. The originating chat is not the spec — the issue (or the
user's written goal) is.

Do **not** start this pipeline unless the user asked to deliver / implement.

Companion skills (read when that step runs; do not copy their rules here):

| Step | Skill |
| --- | --- |
| Phase commits | `$staged-commit-message` (phase-during-work / Commit) |
| Late simplify | `$trim-and-deepen` **TRIM track only**, if that skill is installed |
| Acceptance | one completion subagent (below). `$review` is optional extra, not required |

## Defaults

- Base: canonical `main` (or `master` if that is the default).
- Isolation: **always** `git worktree add` + new branch. Never commit on the
  caller's dirty primary tree.
- Branch prefix from issue **kind**: `feat/` · `fix/` (Bug/Fix) · `docs/` ·
  `chore/`. Default `feat/` if unclear.
- PR: `--draft`, `--base main`, **English** title and body. `Closes #N` only
  when delivering a numbered issue.
- Do not merge, tag, rebase-onto-main, or force-push.

## Workflow

### 1. Load the goal

- **Issue `#N`:** `gh issue view N --repo OWNER/REPO` (canonical remote, same
  rule as `$file-github-issue`). Treat the issue body as the spec: problem,
  non-goals, approach, acceptance.
- **Oral / pasted goal:** write a 5-line restatement (problem, approach,
  non-goals, acceptance, out of scope) in the reply, then proceed. Do not
  invent an issue unless the user asked.

Stop if the goal is two ownership areas with no sequencing. Ask once which
increment to deliver, or split.

### 2. Isolate from main

In the **existing** clone (read-only for this step):

1. `git remote -v` + `gh repo view` → canonical remote `UPSTREAM`.
2. `git fetch "$UPSTREAM" main` (or `master`).
3. Confirm the current checkout is **not** already this delivery worktree.
4. Branch name: `<prefix>/<slug>` — slug from the issue title or goal, kebab,
   ASCII, ≤40 chars. Example: `#137` Feat → `feat/eval-network-reuse-attempt`.
5. Worktree path (sibling of the repo root, never inside it):

```bash
ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$ROOT")
NAME=$(basename "$ROOT")
git worktree add -b "$BRANCH" "$PARENT/${NAME}-wt-${SLUG}" "$UPSTREAM/main"
```

If that path exists, stop and reuse or pick a new slug — do not clobber.

All later commands run with cwd = that worktree.

### 3. Phase the increment

Read the target repo's agent/architecture docs **in the worktree** before
editing (`AGENTS.md`, `docs/design/`, issue "Design impact").

If the issue says design-first, Phase 0 is **only** the cited design/docs
paths. Then implementation phases that match Acceptance, not module layers.

Each phase:

1. Implement that slice only.
2. Focused tests for that slice (repo's documented gate, not invented CI).
3. Stage **only** those paths. Follow `$staged-commit-message` Commit /
   phase-during-work. No `git add .`.
4. Next phase on a clean tree.

Do not implement everything and split commits at the end.

### 4. Trim (optional)

If `$trim-and-deepen` is installed, run it on the **branch diff vs
`$UPSTREAM/main`**. TRIM only (delete/collapse defensive redundancy). Do not
run DEEPEN unless the user asked. Commit trim as its own `refactor` /
`chore` phase if it is non-trivial.

If the skill is missing, skip. Do not invent a second trim procedure.

### 5. Completion subagent

Spawn **one** read-leaning subagent against this worktree. Give it:

- Issue URL or the 5-line oral restatement
- `git diff "$UPSTREAM/main"...HEAD` (and remaining uncommitted if any)
- Acceptance list from the issue

Ask it to return: pass/fail per acceptance item, blocking vs follow-up
findings, scope creep. It must **not** edit.

Executor: fix **blocking** items, phase-commit, re-check at most **twice**.
Cheap follow-ups optional; otherwise name them in the PR, do not claim done.

Skip only if the user said so, or the change is docs-only with no code path.

### 6. CI-equivalent + docs

Before opening the PR, run what **this repo** documents for push / PR
(path-filtered jobs in `.github/workflows/` or `AGENTS.md`). Do not invent
a full matrix. Do not skip because "only docs" unless the workflow files
agree.

Docs that belong with the behavior stay in that phase's commit (or an
immediate `docs` commit). Public/reader docs must not use GitHub issue
numbers if the target repo forbids that.

Failing CI-equivalent → fix in the worktree, do not open the PR.

### 7. Draft PR

```bash
git push -u "$UPSTREAM" "$BRANCH"
gh pr create --repo OWNER/REPO --draft --base main --head "$BRANCH" \
  --title "<type>(<scope>): <english subject>" \
  --body-file -
```

Body (English):

```markdown
## Summary
<what changed, one short paragraph>

## Approach
<the knob / files / default = omit means old behavior>

## Test plan
- [ ] <local CI-equivalent actually run>
- [ ] <acceptance item>

Closes #<N>
```

Omit `Closes` for oral goals. Reply with the PR URL. Do not merge.

## Guardrails

- One issue/goal per worktree.
- No secrets in commits, PR body, or evidence paths.
- No host-absolute paths in tracked docs.
- PASS / product verdicts stay whatever the target repo already owns.
- Do not push from the user's primary dirty checkout.
- Do not delete the worktree unless the user asks.
