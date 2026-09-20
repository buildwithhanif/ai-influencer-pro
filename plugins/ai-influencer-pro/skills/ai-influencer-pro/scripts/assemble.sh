#!/usr/bin/env bash
# assemble.sh — stitch Flow clips into one episode: 1080x1920, PART label, case number, outro card.
#
#   assemble.sh <out.mp4> --case "CASE #0041" --part "PART 1" --handle "@dennisfromhr" clip1.mp4 clip2.mp4 clip3.mp4
#
# Every clip is normalised first (same fps, size, sample rate) because Flow/Omni/Veo clips do not
# always match each other, and ffmpeg concat silently produces garbage when they don't.
set -euo pipefail
OUT="$1"; shift
CASE="CASE #0000"; PART="PART 1"; HANDLE="@yourhandle"; OUTRO_SEC=3
CLIPS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --case) CASE="$2"; shift 2;;
    --part) PART="$2"; shift 2;;
    --handle) HANDLE="$2"; shift 2;;
    --outro) OUTRO_SEC="$2"; shift 2;;
    *) CLIPS+=("$1"); shift;;
  esac
done
[ ${#CLIPS[@]} -ge 1 ] || { echo "no clips"; exit 1; }
FONT="${AIP_FONT:-/System/Library/Fonts/Supplemental/Arial Bold.ttf}"
[ -f "$FONT" ] || FONT="/System/Library/Fonts/Helvetica.ttc"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
LIST="$TMP/list.txt"; : > "$LIST"
i=0
for c in "${CLIPS[@]}"; do
  i=$((i+1))
  # normalise: 1080x1920, 24 fps, yuv420p, 48 kHz stereo. Pad if the clip is a different ratio.
  ffmpeg -y -v error -i "$c" \
    -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p" \
    -af "aresample=48000,aformat=channel_layouts=stereo" \
    -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 160k "$TMP/n$i.mp4"
  echo "file 'n$i.mp4'" >> "$LIST"
done
# outro card: black, "TO BE CONTINUED..." then "FOLLOW <handle> FOR PART 2"
ffmpeg -y -v error -f lavfi -i "color=c=black:s=1080x1920:r=24:d=$OUTRO_SEC" -f lavfi -i "anullsrc=r=48000:cl=stereo" -t "$OUTRO_SEC" \
  -vf "drawtext=fontfile='$FONT':text='TO BE CONTINUED...':fontcolor=white:fontsize=84:x=(w-text_w)/2:y=(h-text_h)/2:enable='lt(t,1.5)',drawtext=fontfile='$FONT':text='FOLLOW $HANDLE FOR PART 2':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:enable='gte(t,1.5)'" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "$TMP/outro.mp4"
echo "file 'outro.mp4'" >> "$LIST"
# concat, then burn the case label (top) and PART label (bottom) over the whole episode except the outro
TOTAL=$(for c in "$TMP"/n*.mp4; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$c"; done | awk '{s+=$1} END{print s}')
ffmpeg -y -v error -f concat -safe 0 -i "$LIST" \
  -vf "drawtext=fontfile='$FONT':text='$CASE':fontcolor=white:fontsize=44:box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=140:enable='lt(t,$TOTAL)',drawtext=fontfile='$FONT':text='$PART':fontcolor=white:fontsize=56:box=1:boxcolor=black@0.55:boxborderw=20:x=(w-text_w)/2:y=h-300:enable='lt(t,$TOTAL)'" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of default=nw=1 "$OUT"
echo "wrote $OUT"
