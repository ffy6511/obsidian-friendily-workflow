#!/usr/bin/env bash
# ffprobe duration for each file passed (or every media file in the cwd).
# Usage: measure.sh [file ...]
set -euo pipefail

files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  files=(*)
fi
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  printf "%-48s %8.2fs\n" "$f" "$d"
done
