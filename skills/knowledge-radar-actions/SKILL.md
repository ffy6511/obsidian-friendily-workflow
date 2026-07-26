---
name: knowledge-radar-actions
description: Process manually checked actions in `inbox/知识科技雷达/` after the user reviews a radar digest. Use when the user asks to process the radar queue, execute checked deep reads, ingest checked papers, build a checked learning unit, or record checked ignores. Route paper ingestion to `paper-md-ingest` and learning-unit construction to `learning-unit-ingest`, preserve checkboxes and write idempotent linked receipts back to the source entry.
---

# Knowledge Radar Actions

Run this skill only after the user explicitly asks to process checked radar actions. Do not run it while generating a daily digest.

## Scope and queue

Scan `inbox/知识科技雷达/YYYY-MM-DD.md` from the most recent 14 days, ordered oldest to newest and then by entry order. Process only a checked action that lacks a matching `radar-processed` receipt.

Run the deterministic preflight first:

```bash
python3 .agents/skills/knowledge-radar-actions/scripts/list_pending.py \
  --radar-root inbox/知识科技雷达
```

Use its output to identify pending actions and conflicts; inspect the source entry before editing it.

Use the nearest entry's `%% radar-id: <canonical-id> %%` as its stable identity. Treat these as the supported actions:

| Checked label             | Receipt action        | Route                                                                           |
| ------------------------- | --------------------- | ------------------------------------------------------------------------------- |
| `深读`                    | `deep-read`           | Reuse an existing canonical paper note, or create a radar deep-read note.       |
| `深入调研`                | `deep-research`       | Create a radar deep-research note for an open-source project.                   |
| `收录到 papers/`          | `ingest-paper`        | Invoke `paper-md-ingest`.                                                       |
| `确认构建 learning/ unit` | `build-learning-unit` | Present an outline, then invoke `learning-unit-ingest` only after confirmation. |
| `忽略`                    | `ignore`              | Add the item to the radar ignore list.                                          |

Do not create or process a `生成 learning/ unit 大纲` action. The learning route presents its candidate outline in the conversation and waits for the user's confirmation.

If `忽略` and any productive action are both still pending in the same entry, do not execute either. Record the conflict under that entry and wait for the user to resolve it.

## Routing

### Deep read or deep research

For a paper already ingested into `papers/`, use its canonical reading note as the completed deep read. Otherwise, create a Chinese note under `inbox/知识科技雷达/深读/`.

For articles, record the source, positioning, problem, method or argument, evidence, limitations, and follow-up questions. For projects, verify the official repository, README or docs, architecture, code structure, installation or minimal run path, license, recent maintenance signals, use cases, risks, and alternatives. Distinguish project claims from independently verifiable evidence.

### Paper ingestion

Before ingesting, read `.agents/skills/paper-md-ingest/SKILL.md` and every reference it requires for the relevant workspace state. Only ingest a checked item with an arXiv ID or official paper URL. Run its validator and fix all failures before writing a receipt.

For every new radar paper, set the canonical reading-note filename to the paper's concise short title, for example `MetaGPT.md`, `Gorilla.md`, or `Fara-1.5.md`. Do not create `NOTES.md` for a radar ingestion. The receipt must point to that short-title file directly; an alias such as `[[.../NOTES|MetaGPT]]` is not sufficient. If the short title itself contains a dot, include the `.md` suffix in every vault-relative link so the validator does not parse the title's suffix as a file extension.

Do not create a new project map or roadmap merely because a paper is in the radar. Update an existing project map only when its project ownership is clear.

### Learning unit

Derive a proposed learning domain, unit name, source URLs, learning value, goals, and structure from the checked entry. Present that outline to the user and wait for an explicit confirmation. Do not modify `learning/` and do not write a processed receipt while awaiting that confirmation.

After confirmation, read `.agents/skills/learning-unit-ingest/SKILL.md` and its required references. Build the unit, maps, and roadmap through that skill, then run its validator. Write a receipt only after the validator passes.

### Ignore

Append the canonical id, title, canonical URL, and processing date to `inbox/知识科技雷达/忽略清单.md`. Create the list with a concise heading if it does not exist. Future radar discovery must exclude matching ids, normalized URLs, and normalized titles.

## Receipts and idempotency

Keep the checked box unchanged. Immediately below the completed action, add a visible result line and a hidden machine receipt:

```markdown
- [x] 收录到 papers/
  - 处理结果：2026-07-11 · [[papers/library/2607.08716/Remember When It Matters|Remember When It Matters]]
    %% radar-processed: ingest-paper 2026-07-11 %%
```

Use a vault-relative Obsidian wikilink to the actual target note. For an ignore, link to `[[inbox/知识科技雷达/忽略清单|忽略清单]]`. Insert the receipt only after the target exists and every required validator succeeds. A matching `radar-processed: <action>` receipt makes that action complete and must prevent duplicate work.

When an operation fails, keep the checkbox and omit the success receipt. Add a short visible failure reason under that action, then report the blocker without claiming completion.

## Completion check

Before reporting completion, verify that every written target exists, every added wikilink resolves, the relevant validator passed, and each successful action has exactly one matching receipt.

### `ingest-paper` short-title gate

Treat this as a hard release gate for every newly ingested radar paper. Before adding `radar-processed: ingest-paper`, verify all of the following:

- The sole canonical reading note under `papers/library/<paper-id>/` is named `<short-title>.md`; `NOTES.md` is a failure, not an acceptable fallback.
- `<short-title>` is the concise paper name used for human navigation, not the generic word `NOTES`; preserve meaningful punctuation such as `Fara-1.5`.
- The receipt links directly to that exact file path. A link whose display alias is the short title but whose target is `NOTES` fails this check.
- `PAPERS.md`, any topic/project indexes, and any source-digest or weekly-note links all target the same canonical short-title file. If the title contains a dot, these links include `.md` in the target path.
- Run `paper-md-ingest/scripts/validate_papers_workspace.py --papers-root papers` after the rename/link update. Any error, unresolved link, duplicate canonical note, or remaining `NOTES` target blocks the receipt.

Record a visible failure reason and leave the action pending if this gate fails. Report processed actions, deferred learning outlines, conflicts, failures, and the source digest paths.
