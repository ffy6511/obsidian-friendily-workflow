# Quality subagent

Spawn **one** subagent after TRIM, before CI-equivalent and the PR. It reviews **and may edit** in-scope quality problems. `$review` is optional extra, not a substitute.

Skip only if the user said so, or the change is docs-only with no code path.

## Give it

- Worktree cwd
- Source `BASE` / `$START_REF` and nightly branch name
- Tonight's theme + slice list (user goal, issue URLs, or the discovery outline)
- `git log --oneline $START_REF..HEAD`
- `git diff $START_REF...HEAD` (and remaining uncommitted if any)
- Repo conventions actually read: `AGENTS.md`, architecture, issue Acceptance

Ask for:

1. Blocking vs follow-up findings (correctness, tests, unsafe shortcuts, missing fail-closed, docs drift vs claimed surface, scope creep).
2. Fixes **in this worktree** for blocking, in-scope items. Stay inside tonight's files/theme. No new features, no extra issues, no commit/push/PR.
3. A short pass/fail per slice. Name anything left for the PR.

It must not: merge, push, force-push, delete the worktree, touch the primary checkout, or expand into unrelated refactors.

## Executor after it returns

1. Inspect `git status` / diff in the worktree.
2. Phase-commit remaining or subagent-made fixes with `$staged-commit-message`. No `git add .`.
3. Re-run the subagent at most **once** more if the fix round was material (cap: two rounds total including the first).
4. Cheap follow-ups now; otherwise list them in the PR. Do not claim them done.

Blocking: broken smoke, wrong verdict / identity / cleanup, security or data-loss, clear defect in tonight's paths, CI-equivalent red.

Non-blocking: naming taste, extra comments, optional coverage. Fix if cheap.

If the subagent cannot start, the executor does one self-review of the same diff and records that the independent pass was skipped.
