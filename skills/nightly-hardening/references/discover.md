# Discover tonight's work

Load this after the source branch is known and **before** isolating. Plan-first never creates a worktree. Do not boil the ocean.

## Cap

One night, **one coherent PR**. Typical: 2–5 phase commits. Prefer a theme you can name in one PR subject.

Stop adding slices when:

- The next slice is a different ownership area with no sequencing.
- It needs new product permission, an irreversible default, or a security-semantic change.
- It is blocked on credentials, a missing vendor, or a live environment this session cannot reach.
- It would be a DEEPEN (interface / ownership / test-strategy move) rather than a local fix.

Write deferred work as named follow-ups in the plan or PR. Do not file extra issues unless the user asked.

## 1. User-named work

If the user named an issue, a surface, or a bug, that is the spec.

- Issue `#N`: `gh issue view N --repo OWNER/REPO`. Body = problem, non-goals, approach, acceptance.
- Oral / pasted goal: 5-line restatement (problem, approach, non-goals, acceptance, out of scope), then proceed.
- Do not invent a GitHub issue unless they asked.

Do not attach unrelated "while we're here" issues. Tiny blockers of the named work may ride along.

## 2. Tractable issues (default when nothing was named)

Canonical remote, same rule as `$file-github-issue`.

```bash
gh issue list --repo OWNER/REPO --state open --limit 30
```

Prefer issues that are:

- Small / unblocked / one area (`p2`, `good first issue`, or equivalent labels **if the repo has them** — do not invent labels).
- Already half-done in code: CLI or API exists, GUI or docs do not.
- Leftover rename / product-name residue in **non-canonical** paths (code comments, skills, templates) — not a required historical GitHub path.
- Fail-closed bugs with an obvious test (wrong verdict, prefix match, merge-instead-of-replace).
- Docs or help text that disagree with ` --help` / the real route.

Skip:

- Assigned to someone else, or clearly in-flight on another branch/PR (`gh pr list --search`).
- Epics, RFCs, or "design first" with no agreed approach.
- Needs a credential this session does not have.
- Would change a public contract without an issue/user ask.

If several issues share one theme (e.g. "Hub for already-open Registry ops"), bundling them is OK. If they do not, pick the smallest high-leverage one.

## 3. Autonomous hardening (no good issue, or room left)

Use `$improve-codebase-architecture` **explore** criteria if that skill is installed. **Do not** follow its HTML-report or grilling loop — this pass is not interactive.

Look first at hot spots: `git log --oneline -n 80` on `START_REF`, and files that keep changing. Do not import uncommitted files from the primary checkout.

Take only work that is TRIM-sized or a small fail-closed fix:

| Take tonight | Leave for a named follow-up |
| --- | --- |
| Dead helper / wrapper / echo field in the recent surface | New module, new seam, new package split |
| Prefix/substring binding that should be exact | Re-litigating an ADR / architecture note |
| Upload/copy that merges instead of replace | Multi-actor scheduler, new box kind |
| CLI/API shipped, Hub has no control | Marketplace / plugin store design |
| Product-name residue in skills, templates, package docstrings | Required historical clone URL the repo still documents |
| Worker timeout falling into the wrong phase | Evidence-grade upgrades |

Deletion test: if deleting it would **concentrate** complexity, it is a DEEPEN — name it, do not implement.

`$trim-and-deepen` runs **after** the batch (SKILL.md step 5), on the branch diff, TRIM only. Do not pre-trim the whole repo as "the work".

Read the clone's `AGENTS.md` / `ARCHITECTURE.md` / `docs/` before treating a leftover as a bug. Recorded decisions stay.

## 4. Plan shape (plan-first, and the execute first line)

```text
Base: <branch> @ <short sha>
Branch / worktree: feat/nightly-<slug> · <sibling path>
Theme: <one line>
Slices:
- S1 <intent> → <paths or surface>
- S2 …
Non-goals: …
Checks: repo path-filtered jobs that will actually run
Deferred: …
```

Execute mode: print a compressed version and continue. Plan-first: print this and stop.
