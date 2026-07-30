#!/usr/bin/env python3
import argparse
import gzip
import html as html_std
import json
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from lxml import html as lxml_html
except Exception:  # pragma: no cover
    lxml_html = None

# Enable sibling-module import for the PDF figure extraction bridge and preferences.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
try:
    from extract_pdf_figures import (
        extract_pdf_figures as _run_figure_extraction,
        lit_available as _lit_available,
    )
except Exception:  # pragma: no cover
    _run_figure_extraction = None
    _lit_available = lambda: False
try:
    from preferences import load_preferences as _load_prefs, is_initialized as _prefs_initialized
except Exception:  # pragma: no cover
    _load_prefs = None
    _prefs_initialized = lambda path=None: False

USER_AGENT = "paper-md-ingest/0.1"


def request_bytes(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.geturl(), resp.headers.get("content-type", "")


def maybe_fetch(url, timeout=30):
    try:
        data, final_url, content_type = request_bytes(url, timeout=timeout)
        return {"ok": True, "data": data, "url": final_url, "content_type": content_type}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}", "url": url}
    except Exception as e:
        return {"ok": False, "error": repr(e), "url": url}


def strip_version(arxiv_id):
    return re.sub(r"v\d+$", "", arxiv_id.strip())


def arxiv_atom(arxiv_id):
    bare = strip_version(arxiv_id)
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(bare)}"
    data, _, _ = request_bytes(url)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(data)
    entry = root.find("atom:entry", ns)
    if entry is None:
        return {}
    title = " ".join((entry.findtext("atom:title", default="", namespaces=ns)).split())
    authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
    published = entry.findtext("atom:published", default="", namespaces=ns)
    entry_id = entry.findtext("atom:id", default="", namespaces=ns)
    versioned = entry_id.rstrip("/").split("/")[-1] if entry_id else arxiv_id
    return {
        "title": title,
        "authors": authors,
        "authors_short": (authors[0].split()[-1] + " et al.") if authors else "",
        "year": int(published[:4]) if published[:4].isdigit() else None,
        "versioned_id": versioned,
        "abs_url": f"https://arxiv.org/abs/{versioned}",
    }


def clean_text(node):
    return " ".join(" ".join(node.itertext()).split())


def md_escape_alt(text):
    return text.replace("[", "(").replace("]", ")").replace("\n", " ")[:140]


def normalize_note_figures(record):
    figures = record.get("figures") or []
    if not isinstance(figures, list):
        raise ValueError("figures must be a list when provided")
    normalized = []
    for index, figure in enumerate(figures, start=1):
        if not isinstance(figure, dict):
            raise ValueError(f"figures[{index}] must be an object")
        url = str(figure.get("url", "")).strip()
        if not url.startswith("https://") or url.startswith("https://data:"):
            raise ValueError(f"figures[{index}].url must be a public https URL")
        alt = " ".join(str(figure.get("alt", "")).split()) or f"Figure {index}"
        caption = " ".join(str(figure.get("caption", "")).split())
        takeaway = " ".join(str(figure.get("takeaway", "")).split())
        normalized.append({"url": url, "alt": alt, "caption": caption, "takeaway": takeaway})
    return normalized


def convert_html_to_markdown(data, page_url):
    if lxml_html is None:
        raise RuntimeError("lxml is required for HTML conversion; use a Python runtime with lxml installed.")
    doc = lxml_html.fromstring(data)
    base_href = doc.xpath("//base/@href")
    base_url = urllib.parse.urljoin(page_url, base_href[0] if base_href else page_url)
    for bad in doc.xpath("//script|//style|//nav|//header|//footer"):
        parent = bad.getparent()
        if parent is not None:
            parent.remove(bad)
    root = (doc.xpath("//article") or doc.xpath("//main") or [doc])[0]
    lines = []
    seen = set()

    def add(line=""):
        if line:
            lines.append(line)
        elif lines and lines[-1] != "":
            lines.append("")

    h1 = root.xpath(".//h1") or doc.xpath("//h1")
    if h1:
        add("# " + clean_text(h1[0]))
        add()

    for node in root.iter():
        if not isinstance(node.tag, str) or node in seen:
            continue
        tag = node.tag.lower()
        if tag in {"h2", "h3", "h4"}:
            text = clean_text(node)
            if text:
                add("#" * min(int(tag[1]), 4) + " " + text)
                add()
            seen.add(node)
        elif tag == "figure":
            imgs = node.xpath(".//img/@src")
            captions = node.xpath('.//*[contains(concat(" ", normalize-space(@class), " "), " ltx_caption ")]') or node.xpath(".//figcaption")
            caption = clean_text(captions[0]) if captions else clean_text(node)
            for src in imgs[:4]:
                url = urllib.parse.urljoin(base_url, src)
                add(f"![{md_escape_alt(caption or 'figure')}]({url})")
            if caption:
                add(f"Figure: {caption}")
            add()
            for sub in node.iter():
                seen.add(sub)
        elif tag == "p":
            text = clean_text(node)
            if len(text) > 20:
                add(text)
                add()
            seen.add(node)
        elif tag == "table":
            text = clean_text(node)
            if text:
                add("[Table] " + text[:2400])
                add()
            for sub in node.iter():
                seen.add(sub)
    return "\n".join(lines).replace("\n\n\n", "\n\n").strip() + "\n"


def strip_tex_comments(text):
    out = []
    for line in text.splitlines():
        escaped = False
        cut = len(line)
        for i, ch in enumerate(line):
            if ch == "\\":
                escaped = not escaped
                continue
            if ch == "%" and not escaped:
                cut = i
                break
            escaped = False
        out.append(line[:cut])
    return "\n".join(out)


def read_tex_tree(path, root_dir, seen=None):
    seen = seen or set()
    path = path.resolve()
    if path in seen or not path.exists():
        return ""
    seen.add(path)
    text = path.read_text(errors="ignore")

    def repl(match):
        name = match.group(1).strip()
        candidate = (root_dir / name)
        if candidate.suffix != ".tex":
            candidate = candidate.with_suffix(".tex")
        return "\n" + read_tex_tree(candidate, root_dir, seen) + "\n"

    return re.sub(r"\\(?:input|include)\{([^}]+)\}", repl, text)


def tex_to_markdown(tex):
    tex = strip_tex_comments(tex)
    doc_match = re.search(r"\\begin\{document\}(.*)\\end\{document\}", tex, flags=re.S)
    if doc_match:
        tex = doc_match.group(1)
    replacements = [
        (r"\\title\{([^}]*)\}", r"# \1\n"),
        (r"\\section\*?\{([^}]*)\}", r"\n## \1\n"),
        (r"\\subsection\*?\{([^}]*)\}", r"\n### \1\n"),
        (r"\\subsubsection\*?\{([^}]*)\}", r"\n#### \1\n"),
        (r"\\paragraph\*?\{([^}]*)\}", r"\n**\1.** "),
        (r"\\caption\{([^}]*)\}", r"\nFigure/Table: \1\n"),
    ]
    for pat, repl in replacements:
        tex = re.sub(pat, repl, tex, flags=re.S)
    tex = re.sub(r"\\begin\{(?:figure|table|equation|align|itemize|enumerate)[^}]*\}", "\n", tex)
    tex = re.sub(r"\\end\{(?:figure|table|equation|align|itemize|enumerate)[^}]*\}", "\n", tex)
    tex = re.sub(r"\\(?:cite|citep|citet|ref|label)\{([^}]*)\}", r"[\1]", tex)
    tex = re.sub(r"\\(?:textbf|emph|textit)\{([^}]*)\}", r"\1", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) or "", tex)
    tex = tex.replace("~", " ")
    tex = html_std.unescape(tex)
    tex = re.sub(r"[ \t]+", " ", tex)
    tex = re.sub(r"\n{3,}", "\n\n", tex)
    return tex.strip() + "\n"


def source_to_markdown(arxiv_id):
    bare = strip_version(arxiv_id)
    url = f"https://arxiv.org/e-print/{bare}"
    data, final_url, _ = request_bytes(url, timeout=60)
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        archive = temp / "source"
        archive.write_bytes(data)
        extract_dir = temp / "extract"
        extract_dir.mkdir()
        try:
            with tarfile.open(archive, mode="r:*") as tar:
                tar.extractall(extract_dir)
        except tarfile.ReadError:
            try:
                raw = gzip.decompress(data)
                single = extract_dir / "paper.tex"
                single.write_bytes(raw)
            except Exception:
                shutil.copyfile(archive, extract_dir / "paper.tex")
        tex_files = list(extract_dir.rglob("*.tex"))
        if not tex_files:
            raise RuntimeError(f"No .tex files found in arXiv source {bare}")
        main = next((p for p in tex_files if p.name.lower() == "main.tex"), None)
        if main is None:
            main = max(tex_files, key=lambda p: p.stat().st_size)
        tex = read_tex_tree(main, main.parent)
        return tex_to_markdown(tex), final_url


def pdf_to_markdown(url):
    data, final_url, _ = request_bytes(url, timeout=60)

    # Read parser preference (lit / pdfplumber / pypdf).
    prefs = _load_prefs() if _load_prefs else {}
    parser_tool = prefs.get("pdf_parser", {}).get("tool", "lit")
    fig_prefs = prefs.get("figures", {})
    extract_figs = fig_prefs.get("extract_from_pdf", True)

    with tempfile.TemporaryDirectory() as td:
        pdf = Path(td) / "paper.pdf"
        pdf.write_bytes(data)

        # LiteParse path: structured Markdown + optional figure extraction.
        if parser_tool == "lit" and _lit_available() and _run_figure_extraction:
            try:
                result = _run_figure_extraction(pdf)
                print(
                    f"info: LiteParse parsed PDF "
                    f"({result['uploaded']} figures uploaded, "
                    f"{result['skipped']} skipped, "
                    f"picgo={'on' if result['picgo_used'] else 'off'})",
                    file=sys.stderr,
                )
                return result["markdown"], final_url, result["figures"]
            except RuntimeError as exc:
                print(f"warning: LiteParse failed ({exc}); falling back to pdfplumber", file=sys.stderr)
        elif parser_tool == "lit" and not _lit_available():
            print("warning: preferences request 'lit' but it is not on PATH; using pdfplumber", file=sys.stderr)

        # Fallback: pdfplumber or pypdf for text-only extraction (no figures).
        try:
            import pdfplumber
            parts = []
            with pdfplumber.open(str(pdf)) as doc:
                for i, page in enumerate(doc.pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        parts.append(f"\n\n## Page {i}\n\n{text.strip()}")
            return "\n".join(parts).strip() + "\n", final_url, []
        except Exception:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf))
            parts = []
            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(f"\n\n## Page {i}\n\n{text.strip()}")
            return "\n".join(parts).strip() + "\n", final_url, []


def yaml_scalar(value):
    return json.dumps(str(value), ensure_ascii=False)


NOTE_LABELS = {
    "zh": {
        "high_level_summary": "高层摘要",
        "summary_fallback": [
            "核心贡献尚未从论文正文核验。",
            "需要进一步阅读论文以确认它处理的领域痛点。",
        ],
        "problem_definition": "问题定义",
        "method": "方法",
        "key_figures": "关键图示",
        "experiments": "实验：证据如何支撑结论",
        "limitations_open_questions": "局限与开放问题",
        "relevance": "与当前项目的关系",
        "missing_problem_definition": "尚未提供经过论文正文核验的问题定义。",
        "missing_method": "尚未提供经过论文正文核验的方法说明。",
        "missing_experiments": "尚未提供经过论文正文核验的实验证据说明。",
        "missing_limitations": "尚未提供经过论文正文核验的局限与开放问题。",
    },
    "en": {
        "high_level_summary": "30-second High-Level Summary",
        "summary_fallback": [
            "The core contribution has not yet been verified against the paper body.",
            "Further reading is required to confirm the domain pain point it addresses.",
        ],
        "problem_definition": "Problem Definition",
        "method": "Method",
        "key_figures": "Key Figures",
        "experiments": "Experiments (How They Prove It)",
        "limitations_open_questions": "Limitations and Open Questions",
        "relevance": "Relationship to Current Project",
        "missing_problem_definition": "No paper-verified problem definition has been provided yet.",
        "missing_method": "No paper-verified method explanation has been provided yet.",
        "missing_experiments": "No paper-verified experimental evidence explanation has been provided yet.",
        "missing_limitations": "No paper-verified limitations or open questions have been provided yet.",
    },
}


def contains_cjk(value):
    if isinstance(value, dict):
        return any(contains_cjk(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_cjk(v) for v in value)
    return bool(re.search(r"[\u3400-\u9fff]", str(value)))


def infer_note_language(record):
    explicit = str(record.get("language", "")).strip().lower()
    if explicit in {"zh", "cn", "zh-cn", "chinese", "中文"}:
        return "zh"
    if explicit in {"en", "eng", "english"}:
        return "en"
    language_inputs = [
        record.get("summary", ""),
        record.get("notes", ""),
        record.get("relevance", ""),
    ]
    return "zh" if any(contains_cjk(item) for item in language_inputs) else "en"


def write_notes(path, record, final_source):
    labels = NOTE_LABELS[infer_note_language(record)]
    tags = record.get("tags") or []
    read = record.get("read", False)
    if not isinstance(read, bool):
        raise ValueError(f"read must be a JSON Boolean for {record.get('id', path.parent.name)}")
    summary = record.get("summary") or []
    if isinstance(summary, str):
        summary = [summary]
    summary = list(summary or labels["summary_fallback"])
    if summary:
        summary[-1] = ensure_summary_block_id(summary[-1])
    notes = record.get("notes") or {}
    if not isinstance(notes, dict):
        notes = {}
    relevance = str(record.get("relevance") or "").strip()
    figures = normalize_note_figures(record)

    def note_text(keys, default):
        values = []
        for key in keys:
            value = notes.get(key, "")
            if isinstance(value, list):
                value = "\n".join(f"- {item}" for item in value)
            value = str(value or "").strip()
            if value and value not in values:
                values.append(value)
        return "\n\n".join(values) or default

    body = [
        "---",
        f"id: {record['id']}",
        f"title: {yaml_scalar(record.get('title', record['id']))}",
        f"year: {record.get('year', '')}",
        f"read: {'true' if read else 'false'}",
        f"source: {yaml_scalar(final_source)}",
        "tags:",
    ]
    body.extend([f"  - {tag}" for tag in tags])
    body.extend([
        "---",
        "",
        f"# {record.get('title', record['id'])}",
        "",
        f"## {labels['high_level_summary']}",
        "",
    ])
    body.extend(summary)
    body.extend([
        "",
        f"## {labels['problem_definition']}",
        "",
        note_text(
            ["problem_definition", "problem", "background", "positioning"],
            labels["missing_problem_definition"],
        ),
        "",
        f"## {labels['method']}",
        "",
        note_text(["method"], labels["missing_method"]),
    ])
    if figures:
        body.extend(["", f"## {labels['key_figures']}", ""])
        for figure in figures:
            body.extend([
                f"![{md_escape_alt(figure['alt'])}]({figure['url']})",
                "",
            ])
            if figure["caption"]:
                body.extend([figure["caption"], ""])
            if figure["takeaway"]:
                body.extend([figure["takeaway"], ""])
    body.extend([
        "",
        f"## {labels['experiments']}",
        "",
        note_text(["experiments", "results"], labels["missing_experiments"]),
        "",
        f"## {labels['limitations_open_questions']}",
        "",
        note_text(
            ["limitations_open_questions", "limitations"],
            labels["missing_limitations"],
        ),
    ])
    if relevance:
        body.extend([
            "",
            f"## {labels['relevance']}",
            "",
            relevance,
        ])
    body.append("")
    path.write_text("\n".join(body), encoding="utf-8")


def safe_note_filename(value):
    filename = str(value or "NOTES.md").strip() or "NOTES.md"
    if "/" in filename or "\\" in filename:
        raise ValueError(f"note_filename must be a filename, not a path: {filename}")
    if filename in {".", ".."}:
        raise ValueError(f"invalid note_filename: {filename}")
    path = Path(filename)
    if path.suffix == "":
        path = path.with_suffix(".md")
    if path.suffix != ".md":
        raise ValueError(f"note_filename must use .md: {filename}")
    return path.name


def ensure_summary_block_id(line):
    text = re.sub(r"\s\^[A-Za-z0-9-]+$", "", str(line).rstrip())
    return f"{text} ^summary"


def reading_note_path(paper_dir, record):
    if record.get("note_filename"):
        return paper_dir / safe_note_filename(record["note_filename"])
    existing_notes = sorted(p for p in paper_dir.glob("*.md") if p.name != "paper.md")
    if len(existing_notes) == 1:
        return existing_notes[0]
    return paper_dir / "NOTES.md"


def ingest_one(record, library_root):
    record = dict(record)
    source = record.get("source", "")
    pdf_figures = []
    arxiv_id = None
    if source.startswith("arxiv:"):
        arxiv_id = source.split(":", 1)[1].strip()
    elif re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", record.get("id", "")):
        arxiv_id = record["id"]
    if arxiv_id:
        try:
            meta = arxiv_atom(arxiv_id)
        except Exception as e:
            print(f"warning: arXiv metadata lookup failed for {arxiv_id}: {e}", file=sys.stderr)
            meta = {}
        record.setdefault("title", meta.get("title") or strip_version(arxiv_id))
        record.setdefault("authors", meta.get("authors_short", ""))
        if not record.get("year") and meta.get("year"):
            record["year"] = meta["year"]
        record["id"] = strip_version(record.get("id") or arxiv_id)
        versioned = meta.get("versioned_id") or arxiv_id
        html_candidates = [
            (f"https://arxiv.org/html/{versioned}", None),
            (f"https://arxiv.org/html/{strip_version(arxiv_id)}", None),
            # Older arXiv submissions may not have first-party HTML. This mirror
            # is only a rendering fallback; the canonical note still points at arXiv.
            (f"https://ar5iv.labs.arxiv.org/html/{strip_version(arxiv_id)}", meta.get("abs_url")),
        ]
        for html_url, canonical_source in html_candidates:
            result = maybe_fetch(html_url)
            if result["ok"]:
                try:
                    md = convert_html_to_markdown(result["data"], result["url"])
                    if len(md) > 2000:
                        final_source = canonical_source or result["url"]
                        break
                except Exception:
                    md = ""
        else:
            # HTML unavailable: prefer the official arXiv PDF over the TeX
            # source. PDF preserves structure (headings, tables, lists) and
            # supports figure extraction; the TeX fallback strips figure,
            # table, equation, and list environments.
            pdf_url = f"https://arxiv.org/pdf/{strip_version(arxiv_id)}"
            md = ""
            try:
                md, final_source, pdf_figures = pdf_to_markdown(pdf_url)
            except Exception as e:
                print(f"warning: arXiv PDF conversion failed for {arxiv_id}: {e}", file=sys.stderr)
            if not md.strip():
                print(f"info: falling back to TeX source for {arxiv_id}", file=sys.stderr)
                md, final_source = source_to_markdown(arxiv_id)
    else:
        record["id"] = record["id"].strip()
        final_source = source
        md, final_source, pdf_figures = pdf_to_markdown(source)

    # Auto-extracted PDF figures fill in when the manifest provides none.
    if pdf_figures and not record.get("figures"):
        record["figures"] = pdf_figures

    paper_dir = library_root / record["id"]
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "paper.md").write_text(md, encoding="utf-8")
    notes_path = reading_note_path(paper_dir, record)
    if not notes_path.exists() or record.get("replace_notes"):
        write_notes(notes_path, record, final_source)
    return {"id": record["id"], "title": record.get("title"), "source": final_source, "chars": len(md)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="JSON list of paper records")
    parser.add_argument("--papers-root", required=True, help="Path to papers workspace")
    parser.add_argument("--library-dir", default="library", help="Paper material subdirectory under --papers-root")
    args = parser.parse_args()

    # Notify when preferences haven't been initialized yet.
    if not _prefs_initialized():
        print(
            "notice: preferences.toml is not initialized — using built-in defaults.\n"
            "       Run the skill workflow or edit preferences.toml to customize "
            "parser, figure extraction, and PicGo settings.",
            file=sys.stderr,
        )

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    papers_root = Path(args.papers_root)
    library_root = papers_root / args.library_dir
    library_root.mkdir(parents=True, exist_ok=True)
    results = [ingest_one(record, library_root) for record in manifest]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
