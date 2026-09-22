#!/bin/bash
# deliver.sh PROJECT.tsrct OUT.mp4 [LUFS]
# Export, then the loudness pass Tesseract does not do, then refuse to finish
# if audio and video lengths disagree.
#
# Tesseract sums source levels and never normalises: a raw export of generated
# clips lands around -21 LUFS. Two-pass loudnorm to -14, and aresample back to
# 48 kHz, because loudnorm OUTPUTS 192 kHz and the AAC encoder silently falls
# back to 96 kHz, which breaks any later concat.
set -e
TS="$HOME/Library/Application Support/Tesseract/bin/tsrct"
P="$1"; OUT="$2"; I_T="${3:--14}"
RAW="${OUT%.*}-raw.mp4"
"$TS" export --project "$P" --output "$RAW" >/dev/null
M=$(ffmpeg -hide_banner -nostats -i "$RAW" -af loudnorm=I=${I_T}:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python3 -c "
import sys,json,re
d=json.loads(re.search(r'\{[^{]*input_i.*?\}', sys.stdin.read(), re.S).group(0))
print('%s|%s|%s|%s'%(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh']))")
IFS='|' read -r I TP LRA TH <<< "$M"
# brace every variable: zsh reads $TH:linear as a :l modifier and mangles it
ffmpeg -v error -i "$RAW" \
  -af "loudnorm=I=${I_T}:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:linear=true,aresample=48000" \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT" -y
vd=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$OUT")
ad=$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$OUT")
wh=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$OUT")
python3 -c "
v,a=float('$vd'),float('$ad')
assert abs(v-a)<0.12, 'A/V drift %.3fs'%abs(v-a)
assert '$wh'=='1080,1920', 'master is $wh, not 1080x1920: a source was not pre-scaled (prep.sh)'
print('ok  %s  video %.2fs  audio %.2fs  drift %.3fs  from raw %s LUFS'%('$wh',v,a,abs(v-a),'$I'))"
rm -f "$RAW"
