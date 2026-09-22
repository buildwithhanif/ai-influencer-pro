#!/bin/bash
# v3: rebuilds promo.tsrct from scratch. Run from the project root.
#
# Export resolution follows the SOURCES, not the canvas: one 720-wide clip in
# the timeline drags the whole master to 720 and the type with it. Everything
# here is pre-scaled to 1080x1920.
set -e
TS="$HOME/Library/Application Support/Tesseract/bin/tsrct"
E=".."; HI="../_hires"; V3="../hanif-v3"

rm -f promo.tsrct
"$TS" project create -p promo.tsrct >/dev/null
imp(){ "$TS" project import-video -p promo.tsrct --file "$2" --asset-id "$1" >/dev/null; echo "  video $1"; }

imp robyn "$HI/robyn.mp4"
imp robyngrey "$HI/robyn-grey.mp4"   # she drains to grey the instant he cuts in

# Hanif A is the only keyed shot: it sits over Robyn. A picture + matte pair,
# the matte driving a luma track matte (no chroma key in Tesseract 0.1.0).
imp hanifArgb   "$V3/A-rgb.mp4"
imp hanifAmatte "$V3/A-matte.mp4"
# B and C keep the studio background, the way his profile photo looks.
imp hanifB   "$V3/B.mp4"
imp hanifC   "$V3/C.mp4"
imp hanifCbw "$V3/C-bw.mp4"     # same take, desaturated, for the turn

for n in luca marilou andre priya hiroshi meera; do imp "$n" "$HI/$n.mp4"; done
for n in diego marcus marilou jhoanna callum ada soojin imran; do imp "pv-$n" "$HI/pv-$n.mp4"; done

"$TS" project import-asset -p promo.tsrct --file "$V3/freeze.jpg" \
      --asset-id freeze --kind image >/dev/null; echo "  image freeze"
"$TS" project import-asset -p promo.tsrct --file .tesseract-work/swipe.wav \
      --asset-id swipe --kind audio >/dev/null; echo "  audio swipe"

# Every face here is OFL. Addressing is NOT uniform across fonts: the working
# (fontFamily, fontStyle) pair for each was found by probing (fontprobe.py) and
# lives in build.py's FONTS table, never in what the importer prints.
F="$E/fonts/Font"
for f in Sans-Serif/Montserrat/static/Montserrat-{Black,ExtraBold,Bold,SemiBold,Medium}.ttf \
         Sans-Serif/Inter/static/Inter_28pt-{Regular,Medium,SemiBold,Bold,ExtraBold,Italic,BoldItalic,ExtraBoldItalic}.ttf \
         Sans-Serif/Lato/Lato-Black.ttf Serif/PT_Serif/PTSerif-BoldItalic.ttf \
         Serif/Playfair_Display/static/PlayfairDisplay-Italic.ttf; do
  "$TS" project import-font -p promo.tsrct --file "$F/$f" >/dev/null 2>&1 && echo "  font  $(basename $f)"
done
echo "done"
