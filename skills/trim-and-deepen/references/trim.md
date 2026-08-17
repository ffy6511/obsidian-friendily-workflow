# TRIM — execute now

Behavior-preserving local delete and collapse on the scoped batch. If the public interface or the owner of a fact would move, stop and write a DEEPEN note instead.

## Strong TRIM

- A helper, field, param, branch, event, or config knob added in the batch has **no production consumer**.
- Tests or docs are the only callers, and they pin nothing load-bearing.
- Two functions or blocks in the batch do the same transform — keep one.
- A wrapper only forwards.
- A result field echoes something already on the call, the log, or the returned object.
- Comments narrate control flow the code already shows.
- Hand-rolled logic that an **already-used** language builtin or in-repo helper covers, and the swap deletes the implementation plus its dedicated tests.

## Extreme defensive programming

Name where the value came from and who owns it next. Then delete the extra machinery when it sits on the wrong side.

Same-process typed calls **borrow** values. Do not keep:

- Runtime re-validation of fields a typed caller already has to supply.
- `clone` / `freeze` / defensive copy of data this function does not own and the caller will not mutate.
- `try/catch` that swallows or rewraps with no new information (an empty `catch` that names what it swallows is still a smell if the `try` was speculative).
- Rollback, retry, or "just in case" paths for states this batch cannot produce.
- A second null/undefined check after a call that already throws or narrows.
- Hostile-input tests, fake typed objects, or post-handoff mutation tests used as the **only** reason to keep the check.
- Several sentinels, flags, timeouts, and promises that all track the same liveness or settlement fact — keep one owner.
- Public "for tests" methods whose only job is to let tests poke internals.

**Keep** checks at real trust edges: parsers, config loaders, queues, model/tool JSON, durable files, workers, processes, wire decoders. Keep authz, sandbox, path traversal, first-terminal-outcome arbitration, and dispose-to-quiescence.

## Do not TRIM

- Anything that changes observable behavior, even slightly, unless the new behavior is the same user-visible contract and easier to explain — when unsure, note it.
- Adding a **new** dependency (that is a DEEPEN note, even if the swap would delete code).
- Collapsing a seam that already has two adapters.
- Security, compatibility, or durable/wire format handling.
- Recorded architecture (ADR / `CONTEXT.md` / architecture note) you have not beaten with new evidence.
- Style-only edits, import sorting, or comment rewrites.

## After the edit

- Tests that only existed to protect the deleted surface go with it.
- Do not add coverage as part of TRIM.
- Run the smallest existing tests that exercise the trimmed paths. If they fail because they pinned the dead surface, update them to the remaining public contract; if they fail because behavior moved, revert the trim and reclassify as DEEPEN or SKIP.
