#!/usr/bin/env python3
"""Word-level alignment for captions.

Transcribes each EN clip with mlx_whisper (word timestamps) and writes a JSON
consumed by the Remotion Subtitles component:

    <project>/src/captions.json
    { "<segment id>": { "duration": <s>, "words": [ {"w","s","e"}, ... ] } }

Times are seconds relative to the clip start — the component runs inside the
scene's Sequence, so no global offset is applied.

    uv run tts-align.py            # all scenes, en only

Re-run after EVERY tts-generate.py export. Do not "fix" whisper mishearing a
brand name here; the component's LCS + interpolation pass absorbs it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import mlx.core as mx
from mlx_whisper import transcribe

from tts_generate import SEGMENTS  # same directory

# Keep Metal behaviour consistent with tts-generate.py.
WIRED_LIMIT_GB = 36
CACHE_LIMIT_GB = 8

OUT = Path(__file__).resolve().parent.parent / "src" / "captions.json"
WHISPER_REPO = "mlx-community/whisper-large-v3-turbo"
EN_DIR = Path(__file__).resolve().parent / "en"


def main() -> None:
    gb = 1024**3
    if mx.metal.is_available():
        mx.set_wired_limit(int(WIRED_LIMIT_GB * gb))
        mx.set_cache_limit(int(CACHE_LIMIT_GB * gb))

    out: dict[str, dict] = {}
    for seg in SEGMENTS:
        wav = EN_DIR / f"{seg['id']}.wav"
        result = transcribe(
            str(wav),
            path_or_hf_repo=WHISPER_REPO,
            word_timestamps=True,
            language="en",
        )
        words = [
            {"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)}
            for chunk in result["segments"]
            for w in chunk.get("words", [])
        ]
        duration = result.get("duration", words[-1]["e"] if words else 0.0)
        out[seg["id"]] = {"duration": round(float(duration), 3), "words": words}
        print(f"{seg['id']}: {len(words)} words, {duration:.1f}s")

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
