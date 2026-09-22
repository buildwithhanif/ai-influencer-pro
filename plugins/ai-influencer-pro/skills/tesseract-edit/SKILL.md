---
name: tesseract-edit
description: Edit real footage into a finished vertical video with Tesseract (tsrct, Mirage's local renderer) through a Python layout library — cuts from sourceRange/activeRange, per-creator caption presets, TikTok feed-swipe transitions with sound, green-screen cut-ins driven by a luma track matte, voice ducking by layer splits, cut-to-grey and colour-drain reveals, loudness delivery, and transcript-based verification. Use on "edit in tesseract", "tsrct", "pake tesseract", "bikin promo", "montage", "compilation", "bikin video dari clip-clip ini", "cut these clips together", "swipe transition", "caption beda tiap orang", "green screen", "keyed cut-in", "duck the audio", "render the promo", or any multi-beat edit that will be revised. Holds the fourteen tsrct 0.1.0 traps where Mirage's own docs are wrong. For the narrator's animated text use the `kinetic-type` skill alongside; for a single burned-in hook `ai-influencer-pro`'s edit_hook.py is faster.
---

# Tesseract edit

Tesseract renders an editable document locally: native video, image, text and shape layers,
keyframes with easing, luma track mattes, MP4 export. No GPU, no key, nothing uploaded. Free for
commercial use under US$1M revenue. `~/Library/Application Support/Tesseract/bin/tsrct`.

This skill is what building the AI UGC promo (v1-v4, 22-23 Sep 2026) taught, turned into a
library: `scripts/tsx.py`. You write one `build.py` against it; everything else is scripts.

## Before anything: the four rules that save the most time

1. **Pre-scale every source to 1080x1920** (`prep.sh`). Nothing is auto-fitted, and the export
   takes its resolution from the sources: one 720 clip makes the master 720.
2. **Probe fonts, don't trust the importer.** `tsx.FONTS` holds pairs that render; for a new face
   run `fontprobe.py`.
3. **Layout and keyframes in one pass, commit, then apply.** `commit` replaces the document and
   takes every earlier keyframe with it. `tsx.Edit.save` writes both files from the same code, so
   ids can't drift.
4. **Verify three ways**: full-res frames, a transcript of the master, an SFX-only mix. A render
   that exits 0 has proved nothing.

The full list is `references/traps.md` (fourteen, each with the fix).

## The loop

```bash
T=~/.claude/skills/tesseract-edit/scripts
bash $T/prep.sh raw.mp4 _hires/clip.mp4                 # 1080x1920, once per source
python3 $T/tsxi.py manifest.json edit.tsrct --fonts     # fresh doc + assets.json
python3 build.py                                         # tsx.Edit -> edit.json + motion.json
tsrct project commit -p edit.tsrct --file edit.json
tsrct project apply  -p edit.tsrct --actions motion.json
python3 $T/verify.py frames edit.tsrct 1.0 4.1 9.0      # look first
bash $T/deliver.sh edit.tsrct master.mp4                # export + -14 LUFS + asserts
python3 $T/verify.py words master.mp4                   # read the video back as text
```

A whole build is short. From `examples/demo_build.py`:

```python
from tsx import Edit, ORANGE
e = Edit(); A = json.load(open("assets.json"))
e.ducked("robyn", [(0, 1.55, 1.0, None), (1.55, 1.75, 0.3, "robyngrey"), (1.75, 4.0, 0.06, "robyngrey")], A["robyn"])
e.captions("tiktok-box", [(0.30, 1.50, "I'm 61.")], offset=0, clip_start=0, clip_end=1.55)
e.keyed("hanifArgb", "hanifAmatte", 1.55, 2.45, 0.0, A["hanifArgb"], scale=75, pos=(250, 1840))
l = e.clip("luca", 4.0, 2.15, 0.40, A["luca"])
e.swipe(l, 4.0, [{"asset": "robyngrey", "src_out": 4.0, "intrinsic": A["robyngrey"]}],
        sfx_asset="swipe", sfx_len_ms=A["swipe"])
e.captions("one-word", [(0.55, 2.39, "Everyone told me|to meal prep")], offset=3.6,
           clip_start=4.0, clip_end=6.15, lead=0.18)
e.save("edit.json", "motion.json")
```

## Capability map

| I need to… | Go to |
|---|---|
| Project layout, the loop, timing from speech, when to use something else | `references/workflow.md` |
| Everything that goes wrong in tsrct 0.1.0 and the fix | `references/traps.md` |
| Standard CapCut captions; a different preset per creator in a compilation | `references/captions.md` |
| Feed swipe, jump cut past a flubbed line, cut to grey, colour drain, punch-in | `references/transitions.md` |
| Cut a presenter out of a green screen | `references/keying.md`, `scripts/key.sh` |
| Ducking, SFX layers, loudness, proving a sound is in the mix | `references/audio.md` |
| What to check before calling it done | `references/verification.md` |
| The narrator's Apple-style animated text | the `kinetic-type` skill |
| A worked, real 50 s promo | `examples/promo-v4/` |
| Mirage's own docs (read, but trust traps.md where they differ) | github.com/mirage-hq/Tesseract `skills/tesseract-video` |

## Scripts

| | |
|---|---|
| `tsx.py` | the library: `Edit.clip / ducked / keyed / image / sfx / rect / fill / text / caption / captions / swipe / fade_in / punch / rise / save`, `PRESETS`, `FONTS` |
| `tsxi.py` | create the document from a manifest, refuse non-1080x1920 sources, write `assets.json` |
| `prep.sh` | scale any video or still to 1080x1920 |
| `key.sh` | green screen -> picture + luma matte |
| `deliver.sh` | export, two-pass loudnorm, 48 kHz, assert A/V sync and 1080x1920 |
| `verify.py` | `words` / `sfx` / `frames` |
| `fontprobe.py` | find the fontFamily/fontStyle pair a face actually resolves by |

Fonts in `assets/fonts` are all OFL (licences beside each). No SFX is bundled: bring your own and
check its licence.
