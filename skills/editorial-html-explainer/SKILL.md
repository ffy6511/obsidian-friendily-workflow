---
name: editorial-html-explainer
description: >
  Write a self-contained long-form visual HTML explainer (scrollable article,
  not slides): stone/slate editorial page, IKB accent, centered column, fixed
  right TOC, Maple Mono highlighted code, Mermaid + hand-built diagrams.
  Invoke with /editorial-html-explainer. Manual only — do not auto-run on
  generic "write HTML" or architecture-review requests.
disable-model-invocation: true
---

# Editorial HTML explainer

One self-contained `.html`. Visual first, prose sparse. Copy the scaffold; do not invent a new chrome.

## Workflow

1. Collect: topic, audience, language (match `html lang` to the user), output path. If the page teaches a codebase, gather the real files first — do not invent snippets.
2. Read [references/style.md](references/style.md) — tokens, layout, TOC, code, page spine.
3. Read [references/diagrams.md](references/diagrams.md) — which visual to use.
4. Copy [assets/scaffold.html](assets/scaffold.html) to the output path. Keep the `<head>` scripts and CSS unless the user names a different accent. Replace every `{{…}}`.
5. Fill `main`: header → optional opening map → numbered sections with `id`s → closing takeaway. Wire the same ids into **both** TOCs (header + rail).
6. Run the QA list below, then open the file (`open` on macOS) and give the user the absolute path.

Default output: a path the user named; else next to the topic files, not inside an unrelated repo.

## Hard rules

- Single HTML file. Tailwind CDN + Mermaid 11 ESM + highlight.js 11. No app framework.
- **Content stays centered** (`main.max-w-5xl.mx-auto`). TOC is `fixed` to the **viewport right**, shown only at `2xl+`. Never put TOC in the same flex/grid row as `main` — that shifts the article off-center.
- Code: local **Maple Mono CN** stack; every block is `<pre><code class="language-…">`. Highlight only those nodes (leave `pre.mermaid` alone).
- Diagrams: Mermaid for graphs/sequences; hand-built divs for mass, stacks, horizontal state rows. Mix them.
- Readable type. No `text-[10px] uppercase tracking-wider` on Chinese inside a narrow dark column.
- Horizontal sequences are a row (overflow-x if needed), not a vertical `stateDiagram-v2`.
- Open after write.

## Do not

- Produce a slide deck (different skill).
- Use architecture-review nouns unless the user asked for an architecture review — then follow [diagrams.md § Architecture review](references/diagrams.md#architecture-review).
- Put GitHub issue numbers (`#12`) on reader-facing pages.
- Reinvent tokens, TOC CSS, or highlight colors. Change them only if the user asks.

## After write

QA, then tell the user the absolute path. Fix failures in the same turn.

- Content column is centered; TOC is not in the same flex/grid as `main`.
- Every rail/header TOC href has an `id`. Highlight.js never touches `pre.mermaid`.
- Code blocks have `language-*`, a path figcaption, and escaped `>` / `<`.
- No mass / state row parked in a half-width column. No 10px uppercase Chinese.
- Opening map + numbered sections + a one-sentence close are all present unless the user asked for a different spine.
