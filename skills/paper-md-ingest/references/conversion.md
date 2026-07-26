# Conversion Notes

Use this reference before converting HTML, debugging conversion quality, or promoting a figure from `paper.md` into a canonical reading note.

## HTML to Markdown

The arXiv HTML endpoint usually contains LaTeXML output with many `ltx_*` classes. Do not store the raw HTML in the papers workspace. Extract readable structure:

- title: `h1`
- sections: `h2`/`h3`/`h4`
- paragraphs: `p`
- figures: Markdown image links using the HTML page as base URL
- captions: text after each image
- tables: plain text fallback

Remote figure links are acceptable because the workspace is optimized for agent reading and small git diffs, not offline archival. Reject `data:` payloads, local paths, logos, navigation icons, tracking pixels, and CSS backgrounds.

When arXiv HTML is unavailable for a legacy submission, try a public HTML rendering mirror such as ar5iv before falling back to TeX. Treat the mirror as a conversion resource only: keep the reading note's `source` pointed to the official arXiv abstract/PDF, and identify mirror-derived figure captions in the note.

## Promoting Figures into Reading Notes

After conversion, inspect `paper.md` and its captions. Select one to three figures only when they clarify a core mechanism, evaluation protocol, or result that the note discusses. Prefer the paper's architecture/pipeline figure over a title illustration, and do not add a figure merely to make a note visual.

For every selected URL:

1. Resolve it against the HTML page URL and require a direct `https://` image endpoint.
2. Fetch it once and confirm a successful response with `image/*` content type.
3. Preserve the original figure number or concise caption in the note.
4. Add one sentence in the user's working language that tells the reader what relationship to inspect.

Use this Markdown shape:

```markdown
## 关键图示

![图 3：自动 harness 优化循环](https://arxiv.org/html/<paper-id>v1/x3.png)

图 3：候选 harness 经 trajectory 执行、评估和 Pareto 筛选后回到 meta-agent。
阅读提示：关注训练、validation 与 test 如何隔离，避免把优化器看到的反馈误当作测试证据。
```

## TeX Fallback

When HTML is unavailable, download `https://arxiv.org/e-print/<id>`, extract the archive, locate `main.tex` or the most likely root TeX file, recursively inline `\input{}` and `\include{}` when possible, then strip common LaTeX commands into Markdown.

## PDF Fallback

For non-arXiv or PDF-only material, extract text into `paper.md`. Keep the official PDF URL in the `source` frontmatter field.
