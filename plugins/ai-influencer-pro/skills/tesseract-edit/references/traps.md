# Traps (tsrct 0.1.0)

Every one of these cost real time on the AI UGC promo. Several contradict Mirage's own docs or the
schema. Where this list and the vendor skill disagree, this list is what renders.

| # | Trap | What actually works |
|---|---|---|
| 1 | **Fonts don't resolve by the family the importer prints.** `SF Pro Display`/`Bold` fails; the importer even prints `fontStyle: Regular` for Montserrat ExtraBold, and `Regular` is what fails. | There is no single rule. Probe each face (`scripts/fontprobe.py`) and keep the pair that renders: `tsx.FONTS`. Inter and SF Pro take PostScript name + weight; Montserrat Bold takes `Montserrat`/`Bold`. A `missing_fonts` error is JSON on stdout, not a crash: check for the PNG. |
| 2 | **Nothing is auto-fitted.** `fit: "cover"` does not scale a source to the canvas. | Pre-scale every source to 1080x1920 (`prep.sh`) and use scale 100. |
| 3 | **Export resolution follows the sources**, not the canvas. One 720-wide clip makes the whole master 720, and every caption is downscaled with it. There is no resolution flag. | Same fix: pre-scale everything. `tsxi.py` refuses non-1080x1920 sources; `deliver.sh` asserts the master is 1080x1920. |
| 4 | **anchorPoint is layer-local.** The canvas centre (540,960) is not the centre of a 720x1280 source (360,640). Scaling about a point outside the source makes clips drift up and left — it looks like a fit bug and isn't. | Anchor at the source's own centre. With pre-scaled sources that is (540,960) again. |
| 5 | **A Rect's anchorPoint is its own space too.** A 720x104 pill anchored at (540,960) lands nowhere near its position. | `anchorPoint: [0,0]`, `rect.position: [-w/2,-h/2]`. Hang it at `[-w/2,-h]` so `scaleY` grows a bar from its baseline. |
| 6 | **`cornerRadius` is normalized 0..1**, not pixels. 16 is a capsule. | 0.10 is a card. |
| 7 | **Audio gain can't be animated on a Video layer.** `audioGainBoth` is in the schema and the action batch rejects it as read-only. | Split the clip into consecutive layers with static `volume` (`Edit.ducked`). A 200 ms middle step reads as a ramp. Gain is linear: 0.13 ≈ -17.7 dB. Audio layers *can* take a volume animator. |
| 8 | **No chroma key, and `personMatte` returns an empty mask.** | Green screen + external matte + luma track matte (`key.sh`, `Edit.keyed`). See keying.md. |
| 9 | **`commit` replaces the whole document.** Keyframes applied before it are gone. | Build layout and keyframes in one pass (`tsx.Edit.save` writes both), commit, then apply. `checkout` does keep existing keyframes, so injecting into someone else's project via checkout → edit → commit is safe. |
| 10 | **An action batch fails on the first bad id, after applying the ones before it.** | Generate actions from the same code that created the layers. Never hard-code ids; the old promo pass broke because a caption style owned one layer sometimes and two other times. |
| 11 | **A matte layer can't be exported solo** ("consumed as another layer's track matte"). | Inspect the matte file itself (`key.sh` output) or preview the composite. |
| 12 | **Tesseract does not normalise loudness.** Raw exports of generated clips sit around -21 LUFS. | `deliver.sh`: two-pass loudnorm to -14, then `aresample=48000` (loudnorm outputs 192 kHz and AAC silently falls back to 96 kHz, which breaks any later concat). |
| 13 | **Filmstrip tiles mislead.** A tile can catch an animating word or a mid-swipe frame and make it look wrong. | Judge placement from full-resolution previews (`verify.py frames`). |
| 14 | **zsh eats `$VAR:x`.** `$TH:linear` is parsed as a `:l` modifier. zsh arrays are 1-indexed. | Brace every variable in shell recipes: `${TH}`. |
