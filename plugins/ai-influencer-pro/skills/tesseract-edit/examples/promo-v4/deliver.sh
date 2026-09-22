#!/bin/bash
# Full rebuild -> export -> normalised delivery master. Run from the project root.
set -e
TS="$HOME/Library/Application Support/Tesseract/bin/tsrct"
python3 .tesseract-work/build.py .tesseract-work/editable.json
"$TS" project commit -p promo.tsrct --file .tesseract-work/editable.json >/dev/null
# motion.py reads the layer-id manifest build.py just wrote. commit replaces
# the document, so the motion pass has to be re-applied after every commit.
python3 .tesseract-work/motion.py .tesseract-work/motion.json \
        .tesseract-work/editable-manifest.json >/dev/null
"$TS" project apply -p promo.tsrct --actions .tesseract-work/motion.json >/dev/null
"$TS" export --project promo.tsrct --output promo.mp4

# Tesseract sums source levels and does not normalise; the raw export lands
# around -21 LUFS, far under anything else in a social feed.
M=$(ffmpeg -hide_banner -nostats -i promo.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "
import sys,json,re
d=json.loads(re.search(r'\{[^{]*input_i.*?\}', sys.stdin.read(), re.S).group(0))
print('%s|%s|%s|%s'%(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh']))")
IFS='|' read -r I TP LRA TH <<< "$M"
# brace every variable: zsh reads \$TH:linear as a :l modifier and mangles it
ffmpeg -v error -i promo.mp4 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:linear=true,aresample=48000" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart \
  "AI-UGC-promo-1080p.mp4" -y

vd=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "AI-UGC-promo-1080p.mp4")
ad=$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "AI-UGC-promo-1080p.mp4")
python3 -c "
v,a=float('$vd'),float('$ad')
assert abs(v-a)<0.12, 'A/V drift %.3fs'%abs(v-a)
print('ok  video %.3fs  audio %.3fs  drift %.3fs'%(v,a,abs(v-a)))"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "AI-UGC-promo-1080p.mp4"
