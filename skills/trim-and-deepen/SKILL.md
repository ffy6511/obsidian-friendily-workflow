---
name: trim-and-deepen
description: >
  After a large batch of code changes, execute safe local trims (redundant
  code, unused helpers, extreme defensive programming) on the recently
  changed surface, and write proposed markdown notes for architecture
  deepening and implementation optimization. Invoke with /trim-and-deepen.
  Manual only — do not auto-run after edits or on generic "simplify",
  "refactor", or architecture-review requests.
disable-model-invocation: true
---

# Trim and deepen

Run only when the user invoked `/trim-and-deepen` or `$trim-and-deepen`. Do not start from nearby wording.

Two tracks on the **recently changed surface**. Do not mix them.

| Track      | Action       | Discriminant                                                                    |
| ---------- | ------------ | ------------------------------------------------------------------------------- |
| **TRIM**   | Edit now     | Behavior-preserving local delete/collapse. Public interface and ownership stay. |
| **DEEPEN** | Write a note | Structure, interface, ownership, or test strategy would change.                 |

Read [references/trim.md](references/trim.md) before executing trims.
Read [references/deepen.md](references/deepen.md) before writing notes.

## Scope

Default: the batch, not the whole repo.

1. User named files or a module — take that.
2. Else git: merge-base with `origin/main` or `origin/master` (uncommitted + commits on this branch). No remote — the feature commits / working tree of this change set.
3. If git is empty, files touched this session.
4. Whole-repo survey only when the user asks.

Read conventions in the scoped area first: `AGENTS.md` / `CLAUDE.md` / `CONTEXT.md` / ADRs / architecture docs. Do not re-litigate a recorded decision unless new evidence beats it.

## Workflow

1. Scope the batch.
2. Read the conventions and ADRs that own that area.
3. Survey the **diff** for cost: duplicated lifecycle, defensive copies, unused surface, shallow modules. An unused-symbol scan is not enough.
4. Classify every candidate against the table above. Reject thin guesses.
5. Execute every TRIM candidate. Do not implement DEEPEN.
6. Run the smallest tests that cover the trimmed paths.
7. Write DEEPEN notes. One durable proposal per file.
8. Report. Match the user's language.

Survey may fan out to subagents. Execute trims **serially in this session** so edits do not collide.

## Classify

Split consumers before deciding:

- **Production:** implementation sources, runtime config, shipped examples.
- **Non-production:** tests, docs, comments, snapshots, generated catalogs.
- A test-only consumer is not a reason to keep surface.

**TRIM now** when all of these hold:

- Lives in the scoped batch, or is dead only because of it.
- Removal or collapse preserves shipped behavior.
- Evidence: no production consumer, or the consumer only echoes a fact owned elsewhere.
- Public interface and ownership of the fact stay put.

**DEEPEN as a note** when any of these hold:

- Shallow module, leaking seam, missing locality, two representations of one fact, or speculative generality with no owner.
- Deletion test: deleting it would **concentrate** complexity, not just move it.
- Doing the work would change interfaces, package splits, or how the area is tested.

**SKIP** when:

- A production caller exists and the change is a product decision.
- An ADR or architecture note already justifies the surface.
- Two adapters already exist — that seam is real.
- Thin: typo, formatter, or "looks complex" with no call-site proof.
- The edit would churn unrelated files without shrinking required surface.

Tiny leftover that is still useful: a `TODO` / `FIXME` / `XXX` with a stable tag (`TODO(double-default)`), not a note.

## Execute TRIM

Follow [references/trim.md](references/trim.md).

- Prefer delete and collapse over rewrite.
- Do not rename for taste, restyle, or win "fewer lines" with denser code.
- Do not add features, dependencies, or new abstractions while trimming.
- Delete tests that existed only to pin the removed surface.
- Do not commit unless the user asks.

## Write DEEPEN notes

Follow [references/deepen.md](references/deepen.md).

Where to write, first match wins:

1. Path the user named.
2. `.agents/notes/` if that tree exists — follow **that repo's** lifecycle, class, and format (read its README). Do not invent a parallel scheme.
3. Otherwise one markdown file under `$TMPDIR` (`trim-and-deepen-<timestamp>.md`; split only when proposals are independent). Tell the user the absolute path.

Do not create a new in-repo notes tree unless the user asks.
If a note already owns the topic, amend it. Do not open a duplicate.

## Fold another branch

When the user asks to take findings from a sibling PR or branch: diff that branch against `origin/main` or `origin/master`, not against the current branch. Port only non-overlapping, evidence-backed notes or TODOs. Consolidate overlaps into the owner note. Do not close the other PR unless the user asked.

## Report

- **TRIM:** files changed, what was deleted or collapsed, tests run.
- **DEEPEN:** note paths, one line each.
- **SKIP:** what was left on purpose, and why.
- Do not claim architecture work was implemented.
