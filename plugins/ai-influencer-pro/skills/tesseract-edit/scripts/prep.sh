#!/bin/bash
# prep.sh IN OUT   Scale a video or still to 1080x1920 before it enters Tesseract.
#
# Tesseract's export resolution follows the SOURCES, not the canvas: a single
# 720-wide clip in the timeline makes the whole master encode at 720 and every
# caption is downscaled with it. So everything is pre-scaled here, once.
# Audio is copied untouched.
set -e
IN="$1"; OUT="$2"
[ -z "$OUT" ] && { echo "usage: prep.sh in.(mp4|mov|jpg|png) out"; exit 1; }
case "${IN##*.}" in
  jpg|jpeg|png|webp|JPG|PNG)
    ffmpeg -v error -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -q:v 2 "$OUT" -y ;;
  *)
    ffmpeg -v error -i "$IN" -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920" \
      -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -c:a copy "$OUT" -y ;;
esac
echo "$OUT"
