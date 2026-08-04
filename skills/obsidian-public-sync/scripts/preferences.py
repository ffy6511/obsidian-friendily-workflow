#!/usr/bin/env python3
"""Load user preferences for obsidian-public-sync from ``preferences.toml``.

Same pattern as paper-md-ingest:

- ``preferences.example.toml`` — tracked template with docs
- ``preferences.toml`` — local real config (gitignored)

When the real file is missing, defaults are returned with ``initialized = false``.
"""

from __future__ import annotations

from pathlib import Path

PREFERENCES_FILENAME = "preferences.toml"
EXAMPLE_FILENAME = "preferences.example.toml"

DEFAULTS = {
    "initialized": False,
    "source_root": "",
    "public_root": "",
    "content_subdir": "content",
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def find_preferences_path() -> Path:
    return skill_dir() / PREFERENCES_FILENAME


def find_example_path() -> Path:
    return skill_dir() / EXAMPLE_FILENAME


def _parse_toml_minimal(text: str) -> dict:
    result: dict = {}
    current = result
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section_name = stripped[1:-1].strip()
            current = result.setdefault(section_name, {})
            continue
        if "=" not in stripped:
            continue
        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        current[key] = _parse_toml_value(raw_value.strip())
    return result


def _parse_toml_value(raw: str):
    if raw == "true":
        return True
    if raw == "false":
        return False
    if len(raw) >= 2 and raw[0] in "\"'" and raw[-1] == raw[0]:
        return raw[1:-1]
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw


def load_preferences(path: Path | None = None) -> dict:
    path = find_preferences_path() if path is None else Path(path)
    if not path.exists():
        return dict(DEFAULTS)

    text = path.read_text(encoding="utf-8")
    try:
        import tomllib

        user_prefs = tomllib.loads(text)
    except ImportError:
        try:
            import tomli

            user_prefs = tomli.loads(text)
        except ImportError:
            user_prefs = _parse_toml_minimal(text)
    except Exception:
        user_prefs = {}

    merged = dict(DEFAULTS)
    for key, value in user_prefs.items():
        if not isinstance(value, dict):
            merged[key] = value
    return merged


def is_initialized(path: Path | None = None) -> bool:
    return bool(load_preferences(path).get("initialized", False))


def resolve_roots(path: Path | None = None) -> tuple[Path | None, Path | None, str]:
    """Return (source_root, public_root, content_subdir) with ``~`` expanded.

    Roots that are empty strings become ``None``.
    """
    prefs = load_preferences(path)
    source = str(prefs.get("source_root") or "").strip()
    public = str(prefs.get("public_root") or "").strip()
    content_subdir = str(prefs.get("content_subdir") or "content").strip() or "content"
    source_root = Path(source).expanduser() if source else None
    public_root = Path(public).expanduser() if public else None
    return source_root, public_root, content_subdir
