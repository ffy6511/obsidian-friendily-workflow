#!/usr/bin/env python3
"""Load user preferences for paper-md-ingest from ``preferences.toml``.

This module lets a single skill installation serve users with different
configurations. Two files work together:

- ``preferences.example.toml`` — ships with the skill, fully documented with
  every option and its default value. Tracked in git.
- ``preferences.toml`` — the real user file, created by copying the example
  (either manually or during agent-guided setup). Gitignored.

When ``preferences.toml`` does not exist, all scripts fall back to built-in
defaults (``initialized = false``). The agent detects this and guides the
user through a one-time setup.

TOML parsing uses ``tomllib`` (Python 3.11+), then ``tomli`` if installed,
then a small built-in fallback parser that covers the subset of TOML this
skill needs (sections, booleans, integers, floats, strings). This ensures
the scripts work on any Python 3.9+ runtime without third-party dependencies.
"""

from pathlib import Path

PREFERENCES_FILENAME = "preferences.toml"
EXAMPLE_FILENAME = "preferences.example.toml"

# Built-in defaults applied when preferences.toml is missing or a section is
# absent. These mirror the values in preferences.example.toml.
DEFAULTS = {
    "initialized": False,
    "pdf_parser": {
        "tool": "lit",  # "lit" | "pdfplumber" | "pypdf"
    },
    "figures": {
        "extract_from_pdf": True,
        "upload_via_picgo": False,
        "max_figures": 12,
        "min_width": 50,
        "min_height": 50,
        "max_aspect_ratio": 12.0,
        "min_file_size_kb": 3,
    },
    "ocr": {
        "language": "eng",  # Tesseract language code(s)
    },
}


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def skill_dir():
    """Return the paper-md-ingest skill directory (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def find_preferences_path():
    """Return the expected path to ``preferences.toml`` next to ``SKILL.md``."""
    return skill_dir() / PREFERENCES_FILENAME


def find_example_path():
    """Return the path to ``preferences.example.toml`` (the documented template)."""
    return skill_dir() / EXAMPLE_FILENAME


# ---------------------------------------------------------------------------
# Minimal TOML parser (fallback for Python < 3.11 without tomli)
# ---------------------------------------------------------------------------

def _parse_toml_minimal(text):
    """Parse a restricted TOML subset into a dict.

    Supports: comments, blank lines, top-level key-value pairs, ``[section]``
    headers, and values of type bool / int / float / string.  This is not a
    full TOML implementation — it covers exactly the keys this skill uses.
    """
    result = {}
    current = result

    for line in text.splitlines():
        stripped = line.strip()

        # Skip blank lines and comments.
        if not stripped or stripped.startswith("#"):
            continue

        # Section header: [name]
        if stripped.startswith("[") and stripped.endswith("]"):
            section_name = stripped[1:-1].strip()
            current = result.setdefault(section_name, {})
            continue

        # Key = value
        if "=" not in stripped:
            continue

        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        value = _parse_toml_value(raw_value.strip())
        current[key] = value

    return result


def _parse_toml_value(raw):
    """Convert a raw TOML value string to a Python value."""
    # Boolean
    if raw == "true":
        return True
    if raw == "false":
        return False

    # String (double or single quoted)
    if len(raw) >= 2 and raw[0] in '"\'' and raw[-1] == raw[0]:
        return raw[1:-1]

    # Integer
    try:
        return int(raw)
    except ValueError:
        pass

    # Float
    try:
        return float(raw)
    except ValueError:
        pass

    # Fallback: treat as string without quotes
    return raw


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_preferences(path=None):
    """Load preferences from ``preferences.toml``, merged over defaults.

    Returns a dict with the same structure as :data:`DEFAULTS`.  User values
    override defaults; missing keys fall back to defaults.  If the file does
    not exist, the full defaults are returned (``initialized = false``).
    """
    if path is None:
        path = find_preferences_path()
    else:
        path = Path(path)

    if not path.exists():
        return _deep_merge(DEFAULTS, {})

    text = path.read_text(encoding="utf-8")

    # Try stdlib tomllib (Python 3.11+).
    try:
        import tomllib
        user_prefs = tomllib.loads(text)
    except ImportError:
        # Try third-party tomli.
        try:
            import tomli
            user_prefs = tomli.loads(text)
        except ImportError:
            # Fall back to the minimal parser.
            user_prefs = _parse_toml_minimal(text)
    except Exception:
        # Malformed TOML — use defaults.
        user_prefs = {}

    return _deep_merge(DEFAULTS, user_prefs)


def is_initialized(path=None):
    """Return True when the user has completed first-time setup."""
    return bool(load_preferences(path).get("initialized", False))


def preferences_path_str(path=None):
    """Return the preferences file path as a string (for logging)."""
    return str(find_preferences_path() if path is None else path)


def _deep_merge(base, override):
    """Recursively merge ``override`` over ``base``, returning a new dict."""
    result = {}
    for key, value in base.items():
        if isinstance(value, dict):
            result[key] = _deep_merge(value, override.get(key, {}))
        else:
            result[key] = override.get(key, value)
    # Also carry any user-only keys not in defaults.
    for key, value in override.items():
        if key not in result:
            result[key] = value
    return result
