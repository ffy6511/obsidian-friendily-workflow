# public/

Everything referenced via `staticFile(...)` lives here. Symlinks work for
plain directory links (`tts -> ../tts`), but a link-to-a-link 404s in the
bundle — use real copies for single files.

| Path        | Contents                                                        |
| ----------- | --------------------------------------------------------------- |
| `tts/`      | generated VO (`en/0N_*.wav`), from `tts/tts-generate.py`        |
| `cuts/`     | ffmpeg-preprocessed footage, tail-frozen to scene length        |
| `bgm/`      | background track (see references/bgm.md)                        |
| `fonts/`    | optional self-hosted woff2 (see references/render-troubleshooting.md) |
| `media/`    | images used directly by scenes (hero, outro art, ...)           |
