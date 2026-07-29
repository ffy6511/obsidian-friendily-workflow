# Conversion Notes

Use this reference before converting HTML, debugging conversion quality, or promoting a figure from `paper.md` into a canonical reading note.

## Contents

- [HTML to Markdown](#html-to-markdown)
- [Promoting Figures into Reading Notes](#promoting-figures-into-reading-notes)
- [TeX Fallback](#tex-fallback)
- [PDF Fallback](#pdf-fallback)
  - [Output Contract](#output-contract)
  - [Check and Install LiteParse](#check-and-install-liteparse)
  - [Core `lit` Commands](#core-lit-commands)
  - [Route OCR with `is-complex`](#route-ocr-with-is-complex)
  - [Images and Structured PDF Data](#images-and-structured-pdf-data)
  - [PDF Figure Extraction with PicGo](#pdf-figure-extraction-with-picgo)
  - [Remote PDFs](#remote-pdfs)
  - [Quality Gate](#quality-gate)
  - [Last-resort Fallback](#last-resort-fallback)

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

For non-arXiv or PDF-only material, use [LiteParse](https://github.com/run-llama/liteparse) as the default local parser. Keep the official PDF URL in the reading note's `source` frontmatter field. Download the PDF into a temporary directory unless the user explicitly asks to archive it.

### Output Contract

- Generate the canonical full text as `paper.md`.
- Prefer Markdown output for reading. Use JSON only for diagnostics or structured follow-up work.
- Preserve headings, tables, lists, and links when the parser can reconstruct them.
- Do not silently replace an existing `paper.md` with empty, truncated, or obviously garbled output. Parse into a temporary file, validate it, then replace the destination atomically.
- Do not store the downloaded PDF, parser JSON, screenshots, or extracted image files in the papers workspace unless the user explicitly requests those assets. The extraction pipeline uploads figures to cloud storage and discards local copies.
- PDF-derived figures may enter the reading note when they are uploaded to a public HTTPS URL via PicGo (see [PDF Figure Extraction with PicGo](#pdf-figure-extraction-with-picgo)). Without PicGo, keep PDF-derived figures out — the reading note still requires a verified public `https://` image URL, and unresolved local paths are never acceptable.

### Check and Install LiteParse

Before a PDF conversion, check both command availability and version:

```bash
if command -v lit >/dev/null 2>&1; then
  command -v lit
  lit --version
else
  echo "lit is not available"
fi
```

Use LiteParse `2.9.0` for the command surface documented here. If `lit` is missing and local tool installation is allowed, install the pinned Python package with uv:

```bash
uv tool install --python 3.13 'liteparse==2.9.0'
```

If uv reports that the tool is installed but `lit` is still missing from `PATH`, expose uv's executable directory for the current shell and verify again:

```bash
export PATH="$(uv tool dir --bin):$PATH"
command -v lit
lit --version
```

If another `lit` binary is found or the version is incompatible, inspect its path before replacing it. Reinstall the pinned uv tool only when changing the user's tool environment is permitted:

```bash
uv tool install --python 3.13 --force 'liteparse==2.9.0'
export PATH="$(uv tool dir --bin):$PATH"
lit --version
```

Do not continue with a guessed command surface when `lit --version` or `lit parse --help` fails. Report the installation failure and preserve any existing `paper.md`.

### Core `lit` Commands

Basic parsing writes plain text to stdout:

```bash
lit parse document.pdf
```

Generate the Markdown used for `paper.md`:

```bash
lit parse document.pdf --format markdown --image-mode off -o output.md
```

`--image-mode off` is intentional for the default papers workspace. LiteParse otherwise emits image placeholders such as `![](img_pN_K.png)` even when image bytes were not extracted.

Generate structured JSON for inspection or downstream processing:

```bash
lit parse document.pdf --format json -o output.json
```

Parse selected 1-based page ranges:

```bash
lit parse document.pdf --target-pages "1-5,10,15-20"
```

Disable OCR for a confirmed born-digital PDF:

```bash
lit parse document.pdf --format markdown --no-ocr --image-mode off -o output.md
```

Keep OCR enabled for scanned, sparse, garbled, or mixed PDFs by omitting `--no-ocr`. The bundled OCR language defaults to English:

```bash
lit parse document.pdf --format markdown --ocr-language eng --image-mode off -o output.md
```

For a non-English scan, pass a Tesseract language code and a directory containing the corresponding `.traineddata` files:

```bash
lit parse document.pdf \
  --format markdown \
  --ocr-language eng+chi_sim \
  --tessdata-path /path/to/tessdata \
  --image-mode off \
  -o output.md
```

Useful JSON enrichments are opt-in:

```bash
# Include page-scoped vector shapes and merged horizontal/vertical lines
lit parse document.pdf --format json --extract-vector-graphics -o vectors.json

# Include rich per-item PDF text metadata
lit parse document.pdf --format json --extract-text-metadata -o text-metadata.json

# Include page annotations
lit parse document.pdf --format json --extract-annotations -o annotations.json

# Include AcroForm widget fields and values
lit parse document.pdf --format json --extract-form-fields -o form-fields.json

# Include the tagged-PDF logical structure tree
lit parse document.pdf --format json --extract-structure-tree -o structure.json
```

Use these structured outputs to debug reading order, tables, forms, annotations, or geometry. Do not treat them as required workspace artifacts or replace `paper.md` with JSON.

### Route OCR with `is-complex`

Run the cheap text-layer complexity pass before a full parse:

```bash
lit is-complex document.pdf
```

The command always writes per-page JSON to stdout and a human-readable verdict to stderr. Each page includes `needs_ocr` and reasons such as `scanned`, `no-text`, `sparse-text`, `embedded-images`, `garbled`, or `vector-text`.

The exit status is a routing signal:

- `0`: no page needs OCR; use `lit parse ... --no-ocr`.
- non-zero with valid per-page JSON: at least one page needs OCR; run `lit parse` without `--no-ocr`.
- non-zero without valid JSON: command failure; do not misclassify it as an OCR verdict.

For scripts, do not call `is-complex` with an unconditional `check=True`. Capture stdout and the exit status, validate that stdout is a JSON array, then route the parse:

```bash
COMPLEXITY_JSON="$(mktemp)"

if lit is-complex document.pdf --compact > "$COMPLEXITY_JSON"; then
  lit parse document.pdf \
    --format markdown \
    --no-ocr \
    --image-mode off \
    -o output.md
elif jq -e 'type == "array"' "$COMPLEXITY_JSON" >/dev/null 2>&1; then
  lit parse document.pdf \
    --format markdown \
    --image-mode off \
    -o output.md
else
  echo "LiteParse complexity detection failed" >&2
  exit 1
fi
```

Remove temporary diagnostics after the conversion. If `jq` is unavailable, parse and validate the JSON with the runtime already executing the ingest script.

### Images and Structured PDF Data

For canonical `paper.md` without figures, use `--image-mode off`. This is the right choice when the paper has official HTML (figures come from there) or when `[figures].extract_from_pdf` is disabled in `preferences.toml`.

LiteParse extracts embedded images with `--extract-images --image-output-dir`:

```bash
lit parse document.pdf \
  --format markdown \
  --image-mode placeholder \
  --extract-images \
  --image-output-dir ./assets \
  -o paper.md
```

The Markdown gets `![](img_pN_K.png)` references (N = page, K = image index on that page). Image files land in `--image-output-dir`. Valid source JPEGs keep their format; all others are PNG.

Use screenshots for temporary visual verification when text alone cannot validate formulas, tables, charts, or reading order:

```bash
lit screenshot document.pdf --target-pages "1,3,5" -o ./screenshots
```

Keep screenshots outside the papers workspace unless the user explicitly requests them as durable assets.

### PDF Figure Extraction with PicGo

When a paper has no official HTML (PDF-only), figures cannot be linked as remote URLs from the publisher's page. The `scripts/extract_pdf_figures.py` bridge closes this gap: it extracts images via LiteParse, filters out decorations and icons, uploads qualifying figures to the user's configured cloud image bed via PicGo CLI, and rewrites the Markdown references with public HTTPS URLs.

The pipeline runs automatically during `ingest_papers.py` for PDF-only papers when both `lit` and `picgo` are on `PATH` and `[figures].upload_via_picgo` is enabled in `preferences.toml`. When PicGo is absent or the preference is disabled, the pipeline skips upload gracefully and produces text-only `paper.md` (the previous default behavior).

**Install PicGo CLI** (Node.js required):

```bash
npm install -g picgo
```

**Configure the image bed** before first use. PicGo supports Alibaba Cloud OSS, Tencent Cloud COS, Qiniu, SM.MS, GitHub, and others:

```bash
picgo set  # interactive: choose uploader, enter credentials
picgo upload /path/to/test.png  # verify configuration returns an HTTPS URL
```

For OSS/COS, set the bucket, region, access key, secret key, and path prefix. After configuration, `picgo upload <file>` prints the uploaded URL to stdout.

**Run the bridge standalone** (useful for testing or manual PDF conversion):

```bash
python3 "$PAPER_MD_INGEST_DIR/scripts/extract_pdf_figures.py" paper.pdf \
  --output paper.md \
  --max-figures 8 \
  --json
```

The script:

1. Routes OCR via `lit is-complex` (skips OCR for born-digital PDFs).
2. Parses with `--extract-images --image-mode placeholder`.
3. Filters extracted images by file size (≥ 3 KB), pixel dimensions (≥ 50×50), and aspect ratio (≤ 12:1) to remove icons, logos, decorative lines, and math fragments.
4. Caps the figure count (default 12), preferring larger images by pixel area.
5. Uploads each figure via `picgo upload` and collects HTTPS URLs.
6. Rewrites Markdown: uploaded figures get cloud URLs; filtered or failed images have their `![](...)` references stripped to avoid broken paths.
7. Returns a JSON summary to stderr: `{uploaded, skipped, picgo_used, figures}`.

**Figure filtering heuristics** — LiteParse extracts *all* embedded images, including noise. The defaults (from `preferences.toml` `[figures]`) are conservative but may need tuning for specific papers:

| Filter | Default | Preference key | Rationale |
|--------|---------|----------------|-----------|
| Min file size | 3 KB | `min_file_size_kb` | Icons and tiny graphics are typically < 1 KB |
| Min dimensions | 50×50 px | `min_width` / `min_height` | Filters math symbol fragments and tiny UI elements |
| Max aspect ratio | 12:1 | `max_aspect_ratio` | Removes header/footer strips and decorative lines |
| Max figures | 12 | `max_figures` | Caps cloud upload volume; prefer largest by area |

Override via CLI flags (`--min-width`, `--min-height`, `--max-figures`) or by editing `preferences.toml` directly.

**Reading note integration** — `ingest_papers.py` auto-populates the `## 关键图示` section when the manifest provides no `figures` list, `[figures].extract_from_pdf` is enabled in `preferences.toml`, and PDF figures were successfully uploaded. Each auto-extracted figure gets a generic `图 N` alt label; add a caption and reading cue manually after reviewing `paper.md` and the PDF.

### Remote PDFs

LiteParse accepts PDF bytes on stdin:

```bash
curl -fsSL https://example.com/report.pdf | lit parse -
```

For canonical `paper.md`, specify Markdown and disable unresolved image placeholders:

```bash
curl -fsSL https://example.com/report.pdf |
  lit parse - --format markdown --image-mode off -o output.md
```

Prefer downloading to a temporary file first when the workflow needs to validate the HTTP status, `%PDF-` magic, page count, encrypted state, or complexity before parsing. Keep the official URL in note frontmatter even when redirects lead to a different download endpoint.

### Quality Gate

Before replacing `paper.md`:

1. Confirm the response is a PDF rather than an HTML login/error page.
2. Confirm LiteParse completed successfully and the output is non-empty.
3. Check that Markdown contains substantive paragraphs, not only page labels, headers, or image placeholders.
4. Reject output with obvious decoding corruption, extreme repeated headers/footers, or unusable multi-column ordering.
5. Inspect at least the abstract, one method page, one equation/table/figure page when present, and the conclusion or references against the PDF.
6. For OCR-routed documents, inspect every page reported as `needs_ocr` when the count is small; otherwise sample across all reported reason types.
7. Confirm every retained Markdown link or image reference resolves under the workspace asset policy.
8. Preserve the previous `paper.md` when validation fails and report the failing pages or parser limitation.

LiteParse is local, fast, and heuristic. Dense tables, complex multi-column layouts, handwriting, scans, and math-heavy pages may require a heavier parser or manual correction. State the limitation rather than silently normalizing uncertain formulas, symbols, citations, or numbers.

### Last-resort Fallback

If LiteParse is unavailable and its pinned uv installation cannot be completed, use Poppler only for a confirmed born-digital PDF where raw text is acceptable:

```bash
if ! command -v pdftotext >/dev/null 2>&1; then
  brew install poppler
fi

pdftotext -layout document.pdf output.txt
```

Treat `pdftotext`, `pdfplumber`, and `pypdf` as raw-text recovery tools. They do not satisfy the normal structured Markdown contract for scans, complex tables, equations, figures, or difficult multi-column reading order. Do not use them to produce a seemingly successful but empty or misleading `paper.md`; stop and report that structured PDF conversion remains unresolved.
