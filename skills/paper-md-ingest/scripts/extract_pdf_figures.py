#!/usr/bin/env python3
"""Extract figures from a PDF via LiteParse, upload to cloud storage via PicGo,
and rewrite Markdown image references with public HTTPS URLs.

This bridge closes the figure gap for PDF-only papers. HTML-sourced papers get
figures as remote URLs naturally; PDF-only papers previously had none because
LiteParse writes local file paths that the reading-note policy rejects. By
uploading extracted images to the user's configured image bed (OSS, COS, SM.MS,
etc.) via PicGo CLI, the reading note can carry real figures with verified
public URLs.

Pipeline:
    PDF → lit parse (--extract-images) → filter decorations → picgo upload → rewrite markdown

Usage as CLI::

    python3 extract_pdf_figures.py paper.pdf --output paper.md --json
    python3 extract_pdf_figures.py paper.pdf --min-width 100 --max-figures 8

Usage as library (importable from ingest_papers.py)::

    from extract_pdf_figures import extract_pdf_figures
    result = extract_pdf_figures("/tmp/paper.pdf")
    # result["markdown"]   — paper text with cloud URLs
    # result["figures"]    — list of uploaded figure dicts
    # result["uploaded"]   — count of successfully uploaded figures
"""

import argparse
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

# Enable sibling-module import for preferences.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
try:
    from preferences import load_preferences as _load_prefs
except Exception:  # pragma: no cover
    _load_prefs = None

LIT_BINARY = "lit"
PICGO_BINARY = "picgo"

DEFAULT_MIN_WIDTH = 50
DEFAULT_MIN_HEIGHT = 50
DEFAULT_MIN_FILE_SIZE_KB = 3
DEFAULT_MAX_ASPECT_RATIO = 12.0
DEFAULT_MAX_FIGURES = 12
PICGO_TIMEOUT = 90  # seconds per image upload


# ---------------------------------------------------------------------------
# Environment checks
# ---------------------------------------------------------------------------

def which(cmd):
    """Return True if a CLI tool is on PATH."""
    return shutil.which(cmd) is not None


def lit_available():
    return which(LIT_BINARY)


def picgo_available():
    return which(PICGO_BINARY)


# ---------------------------------------------------------------------------
# Image dimension reading (dependency-free)
# ---------------------------------------------------------------------------

def read_image_dimensions(path):
    """Read (width, height) from PNG or JPEG file headers without Pillow.

    Returns (None, None) for unsupported formats or read failures.
    """
    try:
        with open(path, "rb") as f:
            header = f.read(32)
    except OSError:
        return None, None

    # PNG: signature at bytes 0-7, IHDR width/height at bytes 16-23.
    if header[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", header[16:24])
        return width, height

    # JPEG: scan for a Start-Of-Frame marker.
    if header[:2] == b"\xff\xd8":
        return _read_jpeg_dimensions(path)

    return None, None


def _read_jpeg_dimensions(path):
    """Scan JPEG bytes for the SOF marker carrying width and height."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None, None

    i = 2  # skip the SOI marker
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # SOF0–SOF3, SOF5–SOF7, SOF9–SOF11, SOF13–SOF15.
        if marker in (
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        ):
            height = struct.unpack(">H", data[i + 5:i + 7])[0]
            width = struct.unpack(">H", data[i + 7:i + 9])[0]
            return width, height
        if marker in (0xD8, 0xD9):
            i += 2
        elif 0xD0 <= marker <= 0xD7:
            i += 2
        elif i + 4 <= len(data):
            seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg_len
        else:
            break
    return None, None


# ---------------------------------------------------------------------------
# Image name parsing and filtering
# ---------------------------------------------------------------------------

def parse_image_name(filename):
    """Extract (page, index) from LiteParse image names like ``img_p3_1.png``."""
    match = re.match(r"img_p(\d+)_(\d+)\.(?:png|jpg|jpeg)", filename, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def is_likely_figure(path, min_width, min_height, min_file_size_kb, max_aspect):
    """Decide whether an extracted image is a real figure or decoration.

    Heuristics (in order of cheapness):
    - File size below threshold: icons, logos, tiny graphics → skip.
    - Dimensions below threshold: too small to be a meaningful figure → skip.
    - Extreme aspect ratio: lines, bars, header/footer strips → skip.

    Returns (bool, reason_string).
    """
    file_size = path.stat().st_size
    if file_size < min_file_size_kb * 1024:
        return False, f"file too small ({file_size}B)"

    width, height = read_image_dimensions(path)
    if width is None or height is None:
        # Cannot inspect — keep it and let upload/validation decide.
        return True, "unknown format"

    if width < min_width or height < min_height:
        return False, f"too small ({width}x{height})"

    shorter = min(width, height)
    aspect = max(width, height) / shorter if shorter > 0 else 1.0
    if aspect > max_aspect:
        return False, f"extreme aspect ({aspect:.1f}:1)"

    return True, f"ok ({width}x{height}, {file_size // 1024}KB)"


# ---------------------------------------------------------------------------
# LiteParse parsing
# ---------------------------------------------------------------------------

def _route_ocr(pdf_path):
    """Run ``lit is-complex`` to decide whether OCR is needed.

    Returns True when at least one page needs OCR, False for born-digital PDFs.
    Defaults to True (OCR on) when the complexity check itself fails.
    """
    try:
        result = subprocess.run(
            [LIT_BINARY, "is-complex", str(pdf_path), "--compact"],
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return True

    # Exit 0 means no page needs OCR.
    if result.returncode == 0:
        return False

    # Non-zero exit with valid JSON array means some pages need OCR.
    stdout = (result.stdout or "").strip()
    if stdout.startswith("["):
        return True

    # Ambiguous failure — default to OCR to be safe.
    return True


def parse_pdf_with_images(pdf_path, output_dir, use_ocr=True):
    """Run LiteParse to produce markdown text and extract embedded images.

    Returns (markdown_text, assets_dir_path).
    Raises RuntimeError on parse failure.
    """
    assets_dir = output_dir / "assets"
    md_path = output_dir / "paper.md"

    cmd = [
        LIT_BINARY, "parse", str(pdf_path),
        "--format", "markdown",
        "--image-mode", "placeholder",
        "--extract-images",
        "--image-output-dir", str(assets_dir),
        "-o", str(md_path),
    ]
    if not use_ocr:
        cmd.append("--no-ocr")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(
            f"LiteParse parse failed (exit {result.returncode}):\n"
            f"{result.stderr.strip()}"
        )

    if not md_path.exists():
        raise RuntimeError("LiteParse did not produce paper.md")

    markdown = md_path.read_text(encoding="utf-8")
    return markdown, assets_dir


# ---------------------------------------------------------------------------
# PicGo upload
# ---------------------------------------------------------------------------

def upload_image_via_picgo(image_path):
    """Upload a single image via PicGo CLI and return the public HTTPS URL.

    Returns the URL string, or None on failure / timeout / missing binary.
    PicGo prints the uploaded URL to stdout after success. We extract the last
    ``https://`` match because some versions also print config URLs in logs.
    """
    try:
        result = subprocess.run(
            [PICGO_BINARY, "upload", str(image_path)],
            capture_output=True, text=True, timeout=PICGO_TIMEOUT,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    urls = re.findall(r"https?://[^\s\"'<>]+", combined)
    if not urls:
        return None

    url = urls[-1].rstrip(",.;")
    # Reject data URIs — only accept hosted URLs.
    if url.startswith("https://"):
        return url
    return None


# ---------------------------------------------------------------------------
# Markdown rewriting
# ---------------------------------------------------------------------------

# Matches ![alt](filename) or ![](filename) for known local image names.
_IMAGE_REF_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def rewrite_markdown_images(markdown, url_map, strip_names=None):
    """Replace local image filenames with cloud URLs in markdown text.

    ``url_map`` maps local filename → cloud HTTPS URL. References to filenames
    not in the map are left untouched — *unless* the basename appears in
    ``strip_names``, in which case the entire image reference line is removed.
    This prevents broken local-path references in the canonical paper.md.
    """
    strip_set = set()
    if strip_names:
        for name in strip_names:
            strip_set.add(Path(name).name)

    def replacer(match):
        alt, target = match.group(1), match.group(2)
        basename = Path(target).name
        if basename in url_map:
            return f"![{alt}]({url_map[basename]})"
        if basename in strip_set:
            return ""  # remove filtered/failed image reference
        return match.group(0)

    return _IMAGE_REF_RE.sub(replacer, markdown)


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def _prefs_defaults():
    """Return figure filtering defaults from preferences.toml (or built-in defaults)."""
    if _load_prefs is not None:
        prefs = _load_prefs()
        fig = prefs.get("figures", {})
        return {
            "min_width": fig.get("min_width", DEFAULT_MIN_WIDTH),
            "min_height": fig.get("min_height", DEFAULT_MIN_HEIGHT),
            "min_file_size_kb": fig.get("min_file_size_kb", DEFAULT_MIN_FILE_SIZE_KB),
            "max_aspect": fig.get("max_aspect_ratio", DEFAULT_MAX_ASPECT_RATIO),
            "max_figures": fig.get("max_figures", DEFAULT_MAX_FIGURES),
            "extract_from_pdf": fig.get("extract_from_pdf", True),
            "upload_via_picgo": fig.get("upload_via_picgo", False),
        }
    return {
        "min_width": DEFAULT_MIN_WIDTH,
        "min_height": DEFAULT_MIN_HEIGHT,
        "min_file_size_kb": DEFAULT_MIN_FILE_SIZE_KB,
        "max_aspect": DEFAULT_MAX_ASPECT_RATIO,
        "max_figures": DEFAULT_MAX_FIGURES,
        "extract_from_pdf": True,
        "upload_via_picgo": False,
    }


def extract_pdf_figures(
    pdf_path,
    work_dir=None,
    min_width=None,
    min_height=None,
    min_file_size_kb=None,
    max_aspect=None,
    max_figures=None,
    use_picgo=None,
):
    """Run the full extract → filter → upload → rewrite pipeline on a PDF.

    Parameters
    ----------
    pdf_path : str or Path
        Local path to the PDF file.
    work_dir : str or Path, optional
        Working directory for LiteParse output. Created if missing.
        If None, a temporary directory is used and cleaned up.
    min_width, min_height : int or None
        Minimum pixel dimensions for an image to qualify as a figure.
        None = read from preferences.toml (default: 50).
    min_file_size_kb : int or None
        Minimum file size in KB (filters tiny icons/logos).
    max_aspect : float or None
        Maximum width:height ratio (filters decorative strips).
    max_figures : int or None
        Cap on number of figures to upload.
    use_picgo : bool or None
        Override PicGo usage. None = read from preferences, then auto-detect
        PicGo availability on PATH.

    Returns
    -------
    dict with keys:
        - ``markdown``: paper text, image refs rewritten to cloud URLs
        - ``figures``: list of dicts for successfully uploaded figures, each with
          ``url``, ``alt``, ``caption``, ``page``, ``width``, ``height``
        - ``uploaded``: count of uploaded figures
        - ``skipped``: count filtered or failed images
        - ``picgo_used``: whether PicGo was available and used
    """
    # Resolve parameters from preferences when not explicitly given.
    pd = _prefs_defaults()
    min_width = pd["min_width"] if min_width is None else min_width
    min_height = pd["min_height"] if min_height is None else min_height
    min_file_size_kb = pd["min_file_size_kb"] if min_file_size_kb is None else min_file_size_kb
    max_aspect = pd["max_aspect"] if max_aspect is None else max_aspect
    max_figures = pd["max_figures"] if max_figures is None else max_figures

    # PicGo: preference flag gates the feature; availability check confirms it's installed.
    if use_picgo is None:
        use_picgo = pd["upload_via_picgo"] and picgo_available()

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Set up work directory.
    if work_dir is not None:
        work_dir = Path(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        cleanup_dir = None
    else:
        cleanup_dir = tempfile.TemporaryDirectory()
        work_dir = Path(cleanup_dir.name)

    try:
        # 1. Route OCR and parse.
        use_ocr = _route_ocr(pdf_path)
        markdown, assets_dir = parse_pdf_with_images(
            pdf_path, work_dir, use_ocr=use_ocr
        )

        # 2. Collect and filter candidate figures.
        all_local_names = set()
        candidates = []
        if assets_dir.exists():
            for img_path in sorted(assets_dir.iterdir()):
                if not img_path.is_file():
                    continue
                all_local_names.add(img_path.name)
                ok, _ = is_likely_figure(
                    img_path, min_width, min_height, min_file_size_kb, max_aspect
                )
                if not ok:
                    continue
                page, index = parse_image_name(img_path.name)
                w, h = read_image_dimensions(img_path)
                candidates.append({
                    "local_name": img_path.name,
                    "local_path": str(img_path),
                    "width": w,
                    "height": h,
                    "page": page,
                    "index": index,
                })

        # Names that will NOT get a cloud URL — strip their references.
        candidate_names = {c["local_name"] for c in candidates}
        strip_names = all_local_names - candidate_names

        # 3. Cap figure count: prefer largest images (by pixel area).
        candidates.sort(
            key=lambda c: (c["width"] or 0) * (c["height"] or 0),
            reverse=True,
        )
        capped = candidates[:max_figures]
        skipped = len(candidates) - len(capped)

        # 4. Upload via PicGo.
        figures = []
        url_map = {}
        uploaded = 0

        if use_picgo and capped:
            for fig in capped:
                url = upload_image_via_picgo(fig["local_path"])
                if url:
                    url_map[fig["local_name"]] = url
                    fig["url"] = url
                    uploaded += 1
                else:
                    skipped += 1
                    strip_names.add(fig["local_name"])
        else:
            skipped += len(capped)
            for fig in capped:
                strip_names.add(fig["local_name"])

        # 5. Rewrite markdown: upload URLs in, filtered/failed refs stripped out.
        markdown = rewrite_markdown_images(markdown, url_map, strip_names=strip_names)

        # 6. Build figure list for the reading note (uploaded only).
        # Sort by page order for natural reading flow.
        uploaded_figs = sorted(
            [f for f in capped if f.get("url")],
            key=lambda f: (f.get("page") or 999, f.get("index") or 999),
        )
        for i, fig in enumerate(uploaded_figs, start=1):
            fig["alt"] = f"图 {i}"
            fig["caption"] = ""
            fig["takeaway"] = ""

        return {
            "markdown": markdown,
            "figures": uploaded_figs,
            "uploaded": uploaded,
            "skipped": skipped,
            "picgo_used": use_picgo,
        }
    finally:
        if cleanup_dir:
            cleanup_dir.cleanup()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract PDF figures via LiteParse, upload via PicGo, "
                    "rewrite markdown with cloud URLs.",
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--output", "-o", default=None,
                        help="Write the rewritten markdown here (default: stdout)")
    parser.add_argument("--work-dir", default=None,
                        help="Working directory for LiteParse output")
    parser.add_argument("--min-width", type=int, default=None,
                        help="Minimum image width in px (default: from preferences.toml)")
    parser.add_argument("--min-height", type=int, default=None,
                        help="Minimum image height in px (default: from preferences.toml)")
    parser.add_argument("--max-figures", type=int, default=None,
                        help="Maximum figures to upload (default: from preferences.toml)")
    parser.add_argument("--json", action="store_true",
                        help="Output result summary as JSON to stderr")
    parser.add_argument("--no-picgo", action="store_true",
                        help="Skip PicGo upload (extract only)")
    args = parser.parse_args()

    if not lit_available():
        print(f"error: '{LIT_BINARY}' not found on PATH. Install LiteParse first.",
              file=sys.stderr)
        sys.exit(1)

    use_picgo = False if args.no_picgo else None

    try:
        result = extract_pdf_figures(
            args.pdf,
            work_dir=args.work_dir,
            min_width=args.min_width,
            min_height=args.min_height,
            max_figures=args.max_figures,
            use_picgo=use_picgo,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    markdown = result["markdown"]
    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
        print(f"wrote {len(markdown)} chars to {args.output}", file=sys.stderr)
    else:
        print(markdown)

    if args.json or not args.output:
        summary = {
            "uploaded": result["uploaded"],
            "skipped": result["skipped"],
            "picgo_used": result["picgo_used"],
            "figures": [
                {"url": f["url"], "alt": f["alt"], "page": f.get("page")}
                for f in result["figures"]
            ],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
