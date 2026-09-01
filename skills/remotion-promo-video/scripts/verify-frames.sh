#!/usr/bin/env bash
# Extract one still per timestamp for render QA. Pick timestamps where you
# KNOW what should be on screen (mid-line of a caption, duo swap point, ...).
# Usage: verify-frames.sh video.mp4 12.5[:label] [30[:label2] ...]
# Output: verify-frames/<label>.png next to the video.
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: $0 video.mp4 12.5[:label] [30[:label2] ...]" >&2; exit 1; }
video=$1
shift
outdir="$(dirname "$video")/verify-frames"
mkdir -p "$outdir"

for spec in "$@"; do
  ts=${spec%%:*}
  label=${spec#*:}
  [ "$label" = "$ts" ] && label="t${ts}"
  ffmpeg -y -v error -ss "$ts" -i "$video" -frames:v 1 "$outdir/${label}.png"
  echo "wrote $outdir/${label}.png"
done
