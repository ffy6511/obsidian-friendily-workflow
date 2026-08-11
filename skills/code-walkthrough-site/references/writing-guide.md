# Writing guide

How to turn a topic + code into a left-prose / right-code progressive lesson.

## Goal of the form

- **Left**: narrative that teaches one idea at a time.
- **Right**: an IDE-like repo that **grows** as the reader scrolls.
- Finishing the article should leave a **complete** small codebase (or a complete slice).

Do not dump the full final code in the first checkpoint. The reveal is the pedagogy.

## Workflow for the authoring agent

1. **Frame the story** — one sentence: what the reader can build/understand by the end.
2. **Inventory the code** — list final files and the order a learner should meet them (data flow or dependency order, not filesystem order).
3. **Slice into checkpoints** — 6–20 stages for a short lesson; each stage unlocks one concept or one function.
4. **Build monotonic snapshots** — start empty or with a skeleton; each stage only adds lines.
5. **Write prose around anchors** — each section opens with `<!-- checkpoint: id -->`, then explains *why* the next code appears, then *what* it does.
6. **Scaffold & launch** — validate content, scaffold site, open in browser, scroll through once.

## Checkpoint design

Good checkpoint = one reader question answered.

| Prefer | Avoid |
| --- | --- |
| One type, one function, one tool | Whole module at once |
| Skeleton → fill body | Perfect final file first |
| Follow call/data flow | Random file hopping |
| Label = 2–6 words | Long labels |

Suggested arc for multi-file systems:

1. Overview (empty or tree only)
2. Types / contracts
3. Core loop or pure core
4. Side-effect adapters (IO, tools, UI)
5. Glue / entrypoint
6. Full repo complete

## Prose style

- Short paragraphs; teach by following data, not by listing APIs.
- Name the file and the export the reader should watch for before it appears.
- Inline code for symbols; fenced blocks on the left only for tiny fragments not in the right panel.
- Optional blockquotes for “草履虫式” intuition or asides.
- One figure per major topology (dependency graph, sequence) when it clarifies more than words.

Match the user’s language (zh/en). Keep brand/title consistent with the topic.

## Progressive code techniques

### Extract partial files from a final source

Given final file text, build stages with line-range selection (keep trailing newline):

```text
stage1 = lines 1–20
stage2 = lines 1–20 + 40–55
stage3 = full file
```

Inserted ranges must appear in **document order** so the result is always a contiguous supersequence of prior stages.

### Multi-file stages

A checkpoint’s `repo` may include several files. Only `file` auto-focuses and animates; other files stay available in the tree for free exploration.

When introducing file B that depends on A, keep A’s latest snapshot in `repo`.

### Skeleton stubs

Early stages may show:

```ts
export async function runAgent() {
  // loop goes here
}
```

Later stages **insert** the loop body without deleting the function shell when possible. If the stub must be replaced, set `focus` on the new region.

## What not to put in the site

- Live API keys, secrets, or personal paths
- Trace/debug labs unless the user asked for them (this skill’s default template is lesson-only)
- Build steps that require the original monorepo; bake content into JSON instead

## QA checklist (scroll test)

Before handoff, scroll the article top → bottom once:

- [ ] Every checkpoint anchor fires (panel updates)
- [ ] New code animates on the focused file
- [ ] No large false “rewrite” flashes (monotonicity)
- [ ] Final checkpoint shows complete intended code
- [ ] Theme toggle and editor lock work
- [ ] Mobile “查看代码” drawer opens
- [ ] Site runs offline after scaffold (local vendor + content)
