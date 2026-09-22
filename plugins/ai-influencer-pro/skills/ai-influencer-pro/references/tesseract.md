# Cutting in Tesseract

Tesseract (`tsrct`, Mirage) is a local rendering engine with an editable project
document: native video/image/text/shape layers, keyframes with easing, masks, filmstrip
review, MP4 export. No GPU, no API key, nothing leaves the machine.

It replaces the ffmpeg assembly for anything with structure. It does **not** replace
`score-frames.py`, `beats.py` or the Flow work — it has no generation and no transcription.

```
~/Library/Application Support/Tesseract/bin/tsrct
```

Free for commercial use below US$1M annual revenue. Closed source. The output is yours.

## Why bother

The ffmpeg pipeline renders a whole MP4 before you can look at anything, captions hard-cut
on and off, and "move that caption 200 ms" means re-rendering from scratch. Tesseract gives
you `filmstrip` (a labeled PNG grid at chosen timestamps, no encode), keyframes with real
easing, and a document you revise instead of regenerate.

```bash
tsrct filmstrip --project promo.tsrct \
  --timestamps-ms 19130,19220,19350,19500,19900,20130 \
  --tile-width 168 --tile-height 298 --items-per-row 8 \
  --output Previews/burst.png
```

Sample **entrance, mid-motion, settled hold, exit** around anything that moves, then open
the PNG and look. A command that exits 0 is not review.

## The four things that cost an hour

### 1. Fonts resolve by PostScript name, not family

`import-font` prints `fontFamily`, `fontStyle` and `font`. The docs say to use the first
two. That fails: strict resolution scores it `FamilyOnly` or `FamilyStyleNearest` and
rejects anything approximate, so the render errors with `missing_fonts` or
`strict font resolution failed`.

Use the **`font` value** (the PostScript name) as `fontFamily`:

```json
{"fontFamily": "SFProDisplay-Bold",     "fontStyle": "Bold"}
{"fontFamily": "SFProDisplay-Semibold", "fontStyle": "Semibold"}
```

`"SF Pro Display"` + `"Bold"` does not render. Two weights coexist fine once addressed
this way.

**But there is no rule that survives every font — probe each face.** On Montserrat the
importer prints `fontStyle: "Regular"` for ExtraBold, and `Regular` is what fails;
`Montserrat-ExtraBold` + `ExtraBold` renders. Meanwhile `Montserrat-Bold` + `Bold` fails
and `Montserrat` + `Bold` renders. Before building, drop each face into a scratch
document and try the combinations; keep whichever produces a PNG. Check for the file,
not the exit code: a `missing_fonts` error is JSON on stdout, not a crash. The resolver also carries a catalogue baked into the binary, so an error naming
a font file you never imported is it matching its own bundled copy.

### 2. anchorPoint is layer-local, and nothing is auto-fitted

A source draws at its own pixel size. `fit: "cover"` does not scale it to the canvas.
A 720x1280 hook on a 1080x1920 canvas needs `scale: 150`; a 768x1376 still needs `140.625`.

Worse, `anchorPoint` is in the **source's** coordinates. The centre of a 720x1280 layer is
`[360, 640]`, not `[540, 960]`. Using the canvas centre pins the scale to a point outside
the source and every clip drifts up and left as it grows — which looks like a fit bug and
is not one.

```python
SRC_720, FILL_720 = (720, 1280), 150.0
transform = {"anchorPoint": [360, 640], "position": [540, bias_y(scale)],
             "scale": [scale, scale], "rotation": 0, "opacity": 100}
```

Keep the eye-height bias from the hook editor. With centre anchoring:

```python
def bias_y(scale, fill, bias=0.36):
    return 960 + 1920 * (scale / fill - 1) * (0.5 - bias)
```

### 2b. There is no chroma key, and personMatte does not work

`personMatte` is in the schema and reads like the answer to cutting a presenter
out of a background. In 0.1.0 the segmenter returns an **empty mask**: with
`emptyFallback: "hide"` the layer vanishes, with `"white"` nothing is cut. Test
it before planning around it — the vendor docs say to, and they are right.

There is no chroma key either. So a cut-out presenter means: generate on a green
screen, build a matte outside, and drive the picture with a **luma track matte**
(the matte layer is consumed and never paints itself).

Key on **green dominance**, not colour distance:

```
format=gbrp,geq=r='if(gt(min(g(X,Y)-r(X,Y),g(X,Y)-b(X,Y)),25),0,255)':g='...':b='...'
```

`colorkey` punches holes in the shadow under a jaw and in clothing folds, because
a dark neutral pixel sits closer to a mid green in RGB than a white one does.
`chromakey` eats a cream sweatshirt, whose chroma is nearly neutral. "Is green
clearly the largest channel here" separates subject from background cleanly and
survives both. Close small specks with `dilation,dilation,erosion,erosion,erosion`
— the extra erosion chokes a pixel off the edge and takes the green fringe with it.

Size the cut-out from the **source**, not the canvas. The subject occupies maybe
40% of a green frame, so a 62% layer scale gives a small floating figure in the
middle of shot that reads as a sticker and covers the face behind it. Around 75%
with the anchor maths putting the head low in frame gives a corner cut-in.

### 3. `cornerRadius` is normalized 0..1

Not pixels. `1` is a full capsule, `16` is a capsule, `0.10` is a card. A picture-in-picture
overlay that renders as a pill is this.

### 3b. A Rect's anchorPoint is its own space too

Same trap as Video, easy to miss because a rect has no obvious "natural size".
`anchorPoint: [540, 960]` on a 720x104 pill parks the anchor far outside the
shape and the pill lands nowhere near its `position`. Anchor at `[0, 0]` and
centre the shape on that origin with `rect.position: [-w/2, -h/2]`. Hanging it
above the origin instead (`[-w/2, -h]`) makes `scaleY` animate a bar rising from
its baseline rather than swelling from its middle.

### 4. Audio gain cannot be animated on a Video layer

`audioGainBoth` is keyframable in the schema but **read-only on Video** — the action batch
is rejected. There is no gain envelope for footage audio.

To duck a clip under a voiceover, split it into consecutive layers with static `volume`.
A stair of short segments across 400 ms is indistinguishable from a ramp:

```python
DUCK = [(0, 1300, 1.00), (1300, 1500, 0.45), (1500, 6800, 0.13), (6800, 7125, 0.50)]
```

Gain is **linear**, not dB. 0.13 is about -17.7 dB.

## Shape of a build

Keep layout and motion in two scripts so either can be re-run alone.

```bash
bash .tesseract-work/import.sh              # fresh doc, package all media
python3 .tesseract-work/build.py e.json     # layers, cuts, type
tsrct project commit -p promo.tsrct --file e.json
python3 .tesseract-work/motion.py m.json    # keyframes
tsrct project apply -p promo.tsrct --actions m.json
tsrct export --project promo.tsrct --output promo.mp4
```

`commit` replaces the document, so **motion must be re-applied after every commit.** The
action batch is idempotent: keyframes upsert by stable id.

**Have the layout emit a manifest of the ids it used.** A caption style that
sometimes adds a background slab and sometimes does not means the ids are not a
fixed stride, and a motion pass that guesses them fails on
`property.layer_id does not target an existing layer` — after a partial apply.
`build.py` writes `editable-manifest.json`; `motion.py` reads it.

Cuts are `sourceRange` (which moment of the source) plus `activeRange` (where it sits in
the edit), both in ms, both parent-local. Nothing is pre-trimmed with ffmpeg, so every cut
stays revisable. Document `duration` is in **seconds**.

`layers[0]` is frontmost. `volume: 1.0` enables a Video layer's embedded audio; omitting it
leaves the clip silent.

## Verify with a transcript, not only a filmstrip

`npx hyperframes transcribe file.mp4 --language en --json` runs whisper locally and
returns word timings. Use it twice:

1. **On every generated take, before editing.** A waveform shows speech; it cannot show
   that the model said "I have 30 AI influencers" twice. The transcript can, and a jump
   cut from the first "30" to the second fixed that take without another generation.
2. **On the finished master.** Read the whole video back as text. It caught two cuts that
   ended a word early ("23-tab prop", "Optimum Nutrition cream") that no filmstrip could
   show, and confirmed a ducked voice underneath really was inaudible.

Take the **words** from whisper and the **timing** from `beats.py`: whisper's starts drift
up to ~0.8 s early on these clips, and it snaps the first word to 0.0. It also misspells
brands ("Anchor" for Anker), so captions are typed, not pasted.

## What still belongs to ffmpeg

Preparing a source, not assembling. On the promo that was exactly one thing: pulling the
freeze frame for the turn and desaturating it, because a held frame with a colour change is
cheaper as a still than as a layer effect.

```bash
ffmpeg -ss 6.7 -i hanif-C.mp4 -frames:v 1 \
  -vf "scale=1080:1920:flags=lanczos,hue=s=0.25" freeze.jpg
```

Import it as an image and place it where the clip ends.
