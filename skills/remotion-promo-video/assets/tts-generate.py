#!/usr/bin/env python3
"""Per-scene bilingual TTS export (mlx_audio + Qwen3-TTS) + full reference mix.

Setup: put this file in <project>/tts/, edit SEGMENTS below, then:

    uv run tts-generate.py              # all scenes, zh + en
    uv run tts-generate.py 02_pain      # one scene (id or unique prefix)
    uv run tts-generate.py --list

Rules:
- SEGMENTS array order = playback order of the cut. `id` is the wav filename:
  when scenes are reordered, KEEP the ids and fix the comment (id != position).
- Never regenerate a scene whose text did not change — whisper alignment
  (tts-align.py) is tied to the exact audio.
- TTS text uses speakable spellings ("Qwen 3.8 Max", "times"); on-screen
  captions keep the written form. The aligner matches phonetically-close
  words and interpolates the rest.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import mlx.core as mx
import numpy as np
from mlx_audio.audio_io import read as audio_read
from mlx_audio.audio_io import write as audio_write
from mlx_audio.tts.generate import generate_audio
from mlx_audio.tts.utils import load_model

# ── edit these ──────────────────────────────────────────────
MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit"
# Faster draft (download once): mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit

# Pin the Metal working set (values for a 48GB machine; scale to yours).
WIRED_LIMIT_GB = 36
MEMORY_LIMIT_GB = 37
CACHE_LIMIT_GB = 8

# Chinese: Vivian / Serena / Dylan / Eric    English: Aiden / Ryan / Chelsie / Ethan
VOICE_ZH = "Vivian"
VOICE_EN = "Aiden"

INSTRUCT_ZH = "产品介绍，像对着镜头跟用户讲话。语速中等稍快。不要播音腔，不要卖货。"
INSTRUCT_EN = (
    "Calm product walkthrough, talking to another engineer on camera. "
    "Medium-fast. Not a radio host, not a sales pitch."
)

SPEED = 1.0
TEMPERATURE = 0.55
GAP_SECONDS = 0.5  # silence between scenes in the full mix
MAX_TOKENS = 4096
# ────────────────────────────────────────────────────────────

OUT_DIR = Path(__file__).resolve().parent
HF_CACHE = Path.home() / ".cache/huggingface/hub"

# Array order = playback order of the cut. ids are filenames only.
SEGMENTS: list[dict[str, str]] = [
    {
        "id": "01_intro",
        "zh": "（示例）品牌一句话口号。",
        "en": "(Example) One-line brand slogan.",
    },
    {
        "id": "02_feature",
        "zh": "（示例）这一幕讲什么，两三句。",
        "en": "(Example) What this scene covers, in two or three sentences.",
    },
]


def resolve_model(spec: str) -> str:
    """Use a local snapshot when the Hub repo is already cached (no network)."""
    local = Path(spec).expanduser()
    if local.exists():
        return str(local)
    cache = HF_CACHE / f"models--{spec.replace('/', '--')}"
    snaps = cache / "snapshots"
    if not snaps.is_dir():
        return spec
    ref = cache / "refs" / "main"
    if ref.is_file():
        dest = snaps / ref.read_text().strip()
        if dest.is_dir():
            return str(dest)
    found = sorted(p for p in snaps.iterdir() if p.is_dir())
    return str(found[-1]) if found else spec


def configure_mlx() -> None:
    if not mx.metal.is_available():
        print("Metal not available, using CPU")
        return
    gb = 1024**3
    if WIRED_LIMIT_GB:
        mx.set_wired_limit(int(WIRED_LIMIT_GB * gb))
    if MEMORY_LIMIT_GB:
        mx.set_memory_limit(int(MEMORY_LIMIT_GB * gb))
    if CACHE_LIMIT_GB:
        mx.set_cache_limit(int(CACHE_LIMIT_GB * gb))
    print(f"wired={WIRED_LIMIT_GB}GB memory={MEMORY_LIMIT_GB}GB cache={CACHE_LIMIT_GB}GB")


def _concat(paths: list[Path], dest: Path, gap_s: float) -> None:
    chunks: list[np.ndarray] = []
    sr = None
    for path in paths:
        audio, this_sr = audio_read(path, always_2d=True)
        if sr is None:
            sr = this_sr
        elif this_sr != sr:
            raise SystemExit(f"sample rate mismatch: {path} is {this_sr}, expected {sr}")
        chunks.append(audio)
        chunks.append(np.zeros((int(gap_s * sr), audio.shape[1]), dtype=audio.dtype))
    if not chunks:
        raise SystemExit("no clips to join")
    mixed = np.concatenate(chunks[:-1], axis=0)
    audio_write(dest, mixed, sr, format="wav")
    print(f"wrote {dest}  ({mixed.shape[0] / sr:.1f}s)")


def _gen_one(model, *, text: str, voice: str, instruct: str, lang: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    generate_audio(
        text=text,
        model=model,
        voice=voice,
        instruct=instruct,
        lang_code=lang,
        speed=SPEED,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        output_path=str(dest.parent),
        file_prefix=dest.stem,
        audio_format="wav",
        join_audio=True,
        play=False,
        verbose=True,
    )
    written = dest.parent / f"{dest.stem}.wav"
    if not written.exists():
        raise SystemExit(f"expected {written}")
    print(f"wrote {written}")


def parse_args() -> argparse.Namespace:
    ids = ", ".join(s["id"] for s in SEGMENTS)
    parser = argparse.ArgumentParser(description="Export scene TTS. Pass an id to rebuild one clip.")
    parser.add_argument("shot", nargs="?", help=f"id or unique prefix ({ids}). Omit for all.")
    parser.add_argument("--list", action="store_true", help="print scene ids and exit")
    return parser.parse_args()


def resolve_shots(shot: str | None) -> list[dict[str, str]]:
    if not shot:
        return list(SEGMENTS)
    key = shot.strip().lower()
    exact = [s for s in SEGMENTS if s["id"].lower() == key]
    if exact:
        return exact
    prefix = [s for s in SEGMENTS if s["id"].lower().startswith(key)]
    if len(prefix) == 1:
        return prefix
    contains = [s for s in SEGMENTS if key in s["id"].lower()]
    if len(contains) == 1:
        return contains
    ids = ", ".join(s["id"] for s in SEGMENTS)
    hits = ", ".join(s["id"] for s in (prefix or contains))
    if hits:
        raise SystemExit(f"ambiguous shot {shot!r}: {hits}")
    raise SystemExit(f"unknown shot {shot!r}. use --list or one of: {ids}")


def main() -> None:
    args = parse_args()
    if args.list:
        for s in SEGMENTS:
            print(s["id"])
        return

    selected = resolve_shots(args.shot)
    configure_mlx()
    model_path = resolve_model(MODEL)
    print(f"loading {model_path}")
    model = load_model(model_path)

    jobs = [
        ("zh", "Chinese", VOICE_ZH, INSTRUCT_ZH),
        ("en", "English", VOICE_EN, INSTRUCT_EN),
    ]
    for folder, lang, voice, instruct in jobs:
        out = OUT_DIR / folder
        out.mkdir(parents=True, exist_ok=True)
        for seg in selected:
            dest = out / f"{seg['id']}.wav"
            print(f"\n=== {folder}/{seg['id']}  voice={voice} ===")
            _gen_one(model, text=seg[folder], voice=voice, instruct=instruct, lang=lang, dest=dest)
        clips = [out / f"{s['id']}.wav" for s in SEGMENTS]
        missing = [p.name for p in clips if not p.exists()]
        if missing:
            print(f"skip {folder}/full.wav, missing: {', '.join(missing)}")
            continue
        _concat(clips, out / "full.wav", GAP_SECONDS)


if __name__ == "__main__":
    main()
