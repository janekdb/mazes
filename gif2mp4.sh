#!/usr/bin/env bash
# Convert a maze GIF to an MP4, preserving the GIF's per-frame timing.
#
# GIF frame delays are variable (intro pause, fast build, slow solve), so we
# keep variable frame rate (-fps_mode vfr) rather than resampling to a fixed
# fps — that reproduces the timing you see in the GIF exactly.
#
# Usage: ./gif2mp4.sh [input.gif] [output.mp4]
set -euo pipefail

in="${1:-maze.gif}"
out="${2:-${in%.gif}.mp4}"

#Key flags:
#- -fps_mode vfr — the important one. Your GIF is intentionally variable-rate (5 s intro, 20 ms build frames, 120 ms solve). VFR preserves those exact per-frame delays. If you forced a fixed -r 25 instead, ffmpeg would resample and either drop the fast frames or stretch the pauses.
#- -pix_fmt yuv420p — makes the mp4 playable everywhere (QuickTime, browsers, Slack). H.264's default yuv444 won't play in many players.
#- scale=trunc(iw/2)*2:trunc(ih/2)*2 — yuv420p requires even width/height; this rounds odd dimensions down by one pixel. flags=neighbor keeps the crisp maze edges (no blurring on the upscale-free path).
#- -crf 18 — near-visually-lossless; lower = bigger/better, higher = smaller. Bump to 23 for a smaller file.
#- -movflags +faststart — moves the index to the front so it streams/previews without downloading fully.

ffmpeg -y -i "$in" \
  -movflags +faststart \
  -fps_mode vfr \
  -pix_fmt yuv420p \
  -c:v libx264 -crf 18 \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=neighbor" \
  "$out"

echo "Wrote $out"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" | awk '{printf "Duration: %.2fs\n", $1}'
