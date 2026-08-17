# DEEPEN — notes only

Propose structural improvement. Do not implement unless the user later asks to execute a specific note.

## Vocabulary

Use these words exactly. Domain names come from `CONTEXT.md` when it exists.

| Use                    | Do not substitute               |
| ---------------------- | ------------------------------- |
| module                 | component, service, unit        |
| interface              | API, signature                  |
| implementation         | —                               |
| depth / deep / shallow | "clean", "messy"                |
| seam                   | boundary, layer                 |
| adapter                | wrapper (when you mean adapter) |
| leverage               | "reuse"                         |
| locality               | "cohesion"                      |

**Shallow:** interface nearly as large as the implementation. **Deep:** small interface, large implementation.

**Deletion test:** if you deleted this module, would complexity concentrate in one place, or just move? "Concentrate" is the signal.

**Seam rule:** one adapter is a hypothetical seam; two adapters make it real. Do not propose deleting a real seam as a low-effort win.

**Locality:** a bug and its fix should live in one module. Pure helpers extracted only so tests can reach them, while the real failures sit in the caller, fail this test.

**Leverage:** one interface, many call sites. Deepening pays off on code that has been changing — that is why this skill defaults to the recent batch.

## Strong DEEPEN

- Understanding one concept requires bouncing across many small modules.
- A module is shallow — interface ≈ implementation.
- Tightly coupled modules leak across a seam.
- Two representations mirror the same fact (especially durable log vs transient event, or parallel state flags).
- A seam lists methods every implementation must support, and no consumer uses them.
- Speculative product generality (multi-session, live invalidation, mid-turn steering, …) with no product owner.
- An invariant, rollback path, or special-case test exists only to protect an unused interface.
- Implementation optimization that would change the owner of a fact, the interface, or how the area is tested (algorithm move, pipeline collapse, new dependency that deletes a hand-rolled body).

## Skip or downgrade

- Thin: one typo, one unused import, "this looks complex" with no call-site proof.
- Contradicts an ADR and the new friction is not strong enough to reopen it. If you still surface it, say which ADR and why the friction warrants a revisit.
- Correct but tiny — inline `TODO`/`FIXME`/`XXX`, not a note.
- A second note on a topic that already has an owner — amend the owner.

## Note file

Prefer this skeleton. One physical line per paragraph. Relative links.

```markdown
# <action-oriented title>

Status: proposed

## Problem

Name the current module/interface, cite files, state consumer evidence.
Separate production callers from tests/docs.

## Proposal

Exactly what to remove, fold, demote, or rehome.
Include tests, docs, and generated-file cleanup when they would otherwise pin the old surface.

## Alternatives considered

Each genuine alternative and why it lost.

## What we give up

The strongest case for keeping the current design.

## Acceptance criteria

Observable end state and which gates prove it.

## Risks

Public interface, behavior, future product wants — and why the tradeoff is still reasonable.
```

If the repo's `.agents/notes/` (or ADR) format differs, **that format wins**. Copy its required headings; do not dual-write.

Be concrete enough that a later implementing turn can follow the trail. No "simplify this package" notes.

Write in the user's language unless the repo's note tree is English-only.

## After writing

Do not start the implementation. Ask which note to execute only if the user is already in a "pick one" conversation; otherwise stop at the report in `SKILL.md`.
