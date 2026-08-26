#!/usr/bin/env bash
# Convert a maze GIF to an MP4.
#
# Two modes:
#   (default)   CFR + a real final-frame hold — YouTube-ready. Upload this.
#   --vfr       Reproduces the GIF's exact per-frame delays. Best for
#               Slack/browser previews where you control the player.
#
# Usage:
#   ./gif2mp4.sh [input.gif] [output.mp4]           # YouTube-ready CFR
#   ./gif2mp4.sh --vfr [input.gif] [output.mp4]     # faithful VFR
#
# Env knobs (default mode): HOLD=5 (seconds to pause on the last frame)
#                           FPS=30 (constant frame rate)
set -euo pipefail

mode="youtube"
if [[ "${1:-}" == "--vfr" ]]; then
  mode="vfr"
  shift
fi

in="${1:-maze.gif}"
out="${2:-${in%.gif}.mp4}"

# Shared flags:
# - -pix_fmt yuv420p — plays everywhere (QuickTime/browsers/Slack); H.264's
#   default yuv444 won't play in many players.
# - scale=trunc(iw/2)*2:… — yuv420p needs even width/height; round down 1px.
#   flags=neighbor keeps the maze edges crisp (no blur).
# - -crf 18 — near-visually-lossless; higher = smaller file.
# - -movflags +faststart — index up front so it streams/previews immediately.
scale="scale=trunc(iw/2)*2:trunc(ih/2)*2:flags=neighbor"

if [[ "$mode" == "youtube" ]]; then
  hold="${HOLD:-5}"
  fps="${FPS:-30}"
  # Why not just rely on the GIF's 5000ms last frame? In video a frame's
  # on-screen time is the gap to the NEXT frame's timestamp — the final frame
  # has no successor, so its "duration" is advisory and YouTube's re-encode
  # drops it. tpad=stop_mode=clone makes the pause out of REAL cloned frames.
  # fps=<fps> first normalises to CFR (YouTube prefers it; VFR uploads glitch);
  # tpad then appends `hold` seconds of clones at that rate. All maze delays are
  # >=40ms, safely above 1/30s, so no fast frames are dropped.
  ffmpeg -y -i "$in" \
    -vf "fps=${fps},tpad=stop_mode=clone:stop_duration=${hold},${scale}" \
    -fps_mode cfr \
    -pix_fmt yuv420p \
    -c:v libx264 -crf 18 \
    -movflags +faststart \
    "$out"
else
  # VFR: preserves exact per-frame delays. NB: the last-frame pause is fragile
  # here too (see above) — fine for players that honour it, use --youtube if not.
  ffmpeg -y -i "$in" \
    -movflags +faststart \
    -fps_mode vfr \
    -pix_fmt yuv420p \
    -c:v libx264 -crf 18 \
    -vf "$scale" \
    "$out"
fi

echo "Wrote $out (mode: $mode)"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" | awk '{printf "Duration: %.2fs\n", $1}'
