# Style — tokens, layout, TOC, code

Copy [../assets/scaffold.html](../assets/scaffold.html) and keep these decisions. Do not restyle from scratch.

## Tokens

| Role | Value |
| --- | --- |
| Page | `bg-stone-50 text-slate-900` |
| Accent (IKB) | `#002FA7` · dark-bg lift `#5B7BFF` · ink `#071033` |
| Deep fill | solid `#0f172a` (`.deep`) — no gradient |
| Leak | `#dc2626` |
| Warn | amber-50 / amber-200 |
| Serif (h1/h2/h3) | Iowan Old Style, Palatino, Georgia |
| Sans (body) | Inter from Google Fonts |
| Mono (code + chrome labels) | `"Maple Mono CN", "Maple Mono", "Maple Mono NF", ui-monospace, monospace` |
| Label | `font-mono text-xs uppercase tracking-wider text-slate-500` — English/digits only if the line is all-caps |

Tailwind extend: `colors.ikb` + the three `fontFamily` keys. Body: `antialiased`.

## Layout

```
body
  main.mx-auto.max-w-5xl.px-6.py-12.space-y-16     ← article, always centered
  aside.fixed.right-0.hidden.2xl:block             ← TOC, viewport edge
```

- `main` width cap `max-w-5xl`. Do not wrap `main` + `aside` in a centering flex/grid.
- Sections: `space-y-10` (or `space-y-6` for short ones). Section number: `font-mono text-xs uppercase tracking-widest text-ikb`.
- `html lang` matches the page language (`zh-CN` / `en`).
- Header: product line (mono, slate-500) · serif title · one-line lede · date · optional legend chips · **in-header TOC** with `2xl:hidden` (fallback when the rail is off). Both TOCs list the same top-level ids.
- Cards: `rounded-lg border border-slate-200 bg-white`. Emphasis: `border-2 border-slate-900`. Deep: dark fill + stone-50 text.
- Duo compare: two columns; the one you are teaching gets `border-2 border-slate-900`.
- Dense grids: 2–3 columns for anything with a sentence of text. A 5–6 cell strip is for **labels only** (one line). Never five paragraph-cards in one row.
- `[id] { scroll-margin-top: 1.25rem }` · `html { scroll-behavior: smooth }`.

## Page spine (explainer)

1. **Header** — kicker / title / lede. No second introduction.
2. **Opening map** — one figure that names the whole, then 2–4 one-line role cards (owner / not-owner / red line).
3. **Numbered sections** (`01` `02` `03`) — each: one lede → visual → real code or table. Distinguish colliding terms the first time they appear.
4. **Close** — three takeaway cards, then a one-sentence close in the same page ink (no fill, no gradient), then a mono sources line (`事实来源：path · path`). No issue numbers.

## Right TOC

Show at `2xl` only (`~1536px`) so it sits in leftover margin and never overlaps `max-w-5xl`.

```html
<aside class="pointer-events-none fixed inset-y-0 right-0 z-20 hidden w-56 pr-6 pt-12 2xl:block">
  <nav class="toc-rail pointer-events-auto sticky top-8 ml-auto w-44 text-[13px]" aria-label="本页目录">
    <p class="mb-3 font-mono text-[11px] uppercase tracking-widest text-slate-400">本页</p>
    <a href="#sec-a">01 · …</a>
    <div class="toc-sub">
      <a href="#sec-a-sub">…</a>
    </div>
    <a href="#sec-b">02 · …</a>
  </nav>
</aside>
```

Rules:

- Every TOC `href` has a matching `id` on a heading or section wrapper.
- Top-level = `h2` sections. Sub = important `h3` / visual blocks only (≤4 per section).
- Active = last intersecting target (`rootMargin: -12% 0px -72% 0px`).
- Rail CSS + observer: keep the copies in the scaffold. Do not restyle the left bar.

## Code

```html
<figure class="overflow-hidden rounded-lg border border-slate-200 bg-slate-900">
  <figcaption class="border-b border-slate-700 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-slate-400">
    path/to/file.py · why this snippet
  </figcaption>
  <pre class="overflow-x-auto p-4"><code class="language-python">…</code></pre>
</figure>
```

- Languages: `python` / `yaml` / `bash` (load those highlight.js packs; add more only if the page needs them). CLI samples are `language-bash` too, even inside a numbered “how to use” list.
- Highlight: `pre code[class*='language-']` only. Never highlight `pre.mermaid`.
- Mermaid click-to-zoom: keep the lightbox CSS/JS from the scaffold. See [diagrams.md](diagrams.md).
- Real files only. Figcaption = `repo/relative/path · why this snippet`. Truncate with `...`; escape `<` `>` as `&lt;` `&gt;`.
- Pair related snippets in `lg:grid-cols-2`. A long function stays full width.
- Inline `code` also uses the Maple stack (scaffold `code, pre, .hljs` rule).
- Highlight colors stay on the IKB/slate dark pane (scaffold `.hljs-*`). Do not keep github-dark’s default green-on-black clash.

## Type scale (article)

| Element | Class |
| --- | --- |
| h1 | `font-serif text-4xl leading-tight tracking-tight` |
| h2 | `font-serif text-3xl` (or `text-2xl` for the opening map) |
| h3 | `font-serif text-xl` |
| Body | `text-slate-700 leading-relaxed` · `max-w-3xl` on long paragraphs |
| Figcaption / chrome | Maple, 11px, uppercase tracking |

## Colour use

One accent (IKB) + red leak + amber warn. No extra brand palette. No gradient fills. No dark hero / closing splash.
