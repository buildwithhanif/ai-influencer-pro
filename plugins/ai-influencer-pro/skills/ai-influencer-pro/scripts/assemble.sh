#!/usr/bin/env bash
# assemble.sh — stitch Flow clips into one episode: 1080x1920, case label, PART label, outro card.
#
#   assemble.sh <out.mp4> --case "CASE #0041" --part "PART 1" --handle "@dennisfromhr" clip1.mp4 clip2.mp4 clip3.mp4
#
# Every clip is normalised first (same size, fps, sample rate) because Flow/Omni/Veo clips do not always
# match each other, and ffmpeg concat silently produces garbage when they don't. Labels and the outro
# card are PNGs rendered by labels.py (Pillow), so this works on ffmpeg builds without drawtext.
set -euo pipefail
OUT="$1"; shift
CASE="CASE #0000"; PART="PART 1"; HANDLE="@yourhandle"; OUTRO_SEC=3; CRF=20
CLIPS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --case) CASE="$2"; shift 2;;
    --part) PART="$2"; shift 2;;
    --handle) HANDLE="$2"; shift 2;;
    --outro) OUTRO_SEC="$2"; shift 2;;
    --crf) CRF="$2"; shift 2;;
    *) CLIPS+=("$1"); shift;;
  esac
done
[ ${#CLIPS[@]} -ge 1 ] || { echo "no clips"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 "$HERE/labels.py" "$TMP" --case "$CASE" --part "$PART" --handle "$HANDLE" >/dev/null
LIST="$TMP/list.txt"; : > "$LIST"; i=0
for c in "${CLIPS[@]}"; do
  i=$((i+1))
  ffmpeg -y -v error -i "$c" -i "$TMP/case.png" -i "$TMP/part.png" \
    -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p[v0];[v0][1:v]overlay=0:0[v1];[v1][2:v]overlay=0:0,format=yuv420p[v]" \
    -map "[v]" -map 0:a? -af "aresample=48000,aformat=channel_layouts=stereo" \
    -c:v libx264 -preset fast -crf "$CRF" -c:a aac -b:a 160k "$TMP/n$i.mp4"
  echo "file 'n$i.mp4'" >> "$LIST"
done
# outro: 1.5 s "TO BE CONTINUED...", hard cut, rest "FOLLOW <handle> FOR PART 2", silent stereo track
H1=1.5; H2=$(python3 -c "print(max(0.5, $OUTRO_SEC - 1.5))")
ffmpeg -y -v error -loop 1 -t "$H1" -i "$TMP/outro1.png" -loop 1 -t "$H2" -i "$TMP/outro2.png" -f lavfi -t "$OUTRO_SEC" -i "anullsrc=r=48000:cl=stereo" \
  -filter_complex "[0:v][1:v]concat=n=2:v=1:a=0,fps=24,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -preset fast -crf "$CRF" -c:a aac -b:a 160k -shortest "$TMP/outro.mp4"
echo "file 'outro.mp4'" >> "$LIST"
ffmpeg -y -v error -f concat -safe 0 -i "$LIST" -c:v libx264 -preset medium -crf "$CRF" -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of default=nw=1 "$OUT"
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
