#!/bin/bash
# Green screen -> (rgb, matte) pair at 1080x1920 for compositing in Tesseract.
#
# Tesseract has no chroma key and its personMatte segmenter returns an empty
# mask in 0.1.0, so the cutout is a luma track matte: layer A is the picture,
# layer B is this matte, and A carries trackMatte {mode: luma, layer: B}.
#
# The key is GREEN DOMINANCE, not colour distance. colorkey/chromakey both
# fail on this footage: colorkey punches holes in the shadow under his jaw and
# in the sweatshirt folds, because dark neutral pixels sit closer to a mid
# green in RGB than white ones do. chromakey eats the cream sweatshirt, whose
# chroma is nearly neutral. "Is green clearly the largest channel here" is the
# question that actually separates this subject from this background.
set -e
IN="$1"; OUT="$2"; TH="${3:-25}"
[ -z "$OUT" ] && { echo "usage: key.sh in.mp4 outprefix [threshold]"; exit 1; }

E="if(gt(min(g(X,Y)-r(X,Y),g(X,Y)-b(X,Y)),${TH}),0,255)"
# close small specks, then choke one extra pixel to cut the green fringe
CLEAN="format=gray,dilation,dilation,erosion,erosion,erosion,gblur=sigma=1.4"

ffmpeg -v error -i "$IN" \
  -vf "format=gbrp,geq=r='${E}':g='${E}':b='${E}',${CLEAN},scale=1080:1920:flags=lanczos" \
  -c:v libx264 -crf 12 -pix_fmt yuv420p -an "${OUT}-matte.mp4" -y

# picture: keep the audio, keep the green (the matte hides it), just upscale
ffmpeg -v error -i "$IN" -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -c:a copy "${OUT}-rgb.mp4" -y

echo "$(basename "$OUT")  matte + rgb at 1080x1920"
