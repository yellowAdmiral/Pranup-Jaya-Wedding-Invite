#!/usr/bin/env bash
# Turns your recording into a small, web-friendly looping clip for the site.
# Usage:  ./tools/make-video.sh my-recording.mov
# Needs ffmpeg (https://ffmpeg.org). Writes hero.mp4 and poster.jpg next to index.html.
set -euo pipefail
in="${1:?Give the path to your video, e.g. ./tools/make-video.sh recording.mov}"
out_dir="$(cd "$(dirname "$0")/.." && pwd)"
# Silent, max 1280 px wide, H.264, fast-start so it plays before it has fully downloaded.
ffmpeg -y -i "$in" -an \
  -vf "scale='min(1280,iw)':-2,fps=30" \
  -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 27 -preset slow \
  -movflags +faststart "$out_dir/hero.mp4"
# A still frame, handy for link previews or if you later add a poster.
ffmpeg -y -ss 1 -i "$out_dir/hero.mp4" -frames:v 1 -q:v 3 "$out_dir/poster.jpg"
ls -lh "$out_dir/hero.mp4"
