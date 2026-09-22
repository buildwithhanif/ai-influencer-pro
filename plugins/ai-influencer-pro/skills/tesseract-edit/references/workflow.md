# Workflow

## Project root

```
promo/
  promo.tsrct             the editable document, all media packaged inside
  AI-UGC-promo-1080p.mp4  the delivered master of the CURRENT revision
  Previews/               a contact sheet of the delivered revision
  Versions/               every revision you might go back to (doc + master + build script)
  .tesseract-work/        manifest.json, assets.json, build.py, edit.json, motion.json
```

Save a version before any structural rebuild. On the promo, v2's graphics and v3's font set were
both wanted back later, and they were only recoverable because `Versions/` held them.

## The loop

```bash
T=~/.claude/skills/tesseract-edit/scripts
bash $T/prep.sh raw.mp4 _hires/clip.mp4              # every source to 1080x1920, once
python3 $T/tsxi.py manifest.json promo.tsrct --fonts  # fresh doc + assets.json (intrinsic ms)
python3 build.py                                      # tsx.Edit -> edit.json + motion.json
tsrct project commit -p promo.tsrct --file edit.json
tsrct project apply  -p promo.tsrct --actions motion.json
python3 $T/verify.py frames promo.tsrct 1.0 4.2 9.0   # look before exporting
bash $T/deliver.sh promo.tsrct promo.mp4              # export, loudness, A/V + size asserts
python3 $T/verify.py words promo.mp4                  # read the whole video back as text
```

`build.py` is the only file you edit. It is plain Python over `tsx.Edit`: see
`examples/demo_build.py` (minimal, every feature) and `examples/promo-v4/` (the real 50 s promo,
written before tsx existed, with the two-script manifest approach tsx replaced).

## Timing

Cuts are `sourceRange` (which moment of the source) + `activeRange` (where it sits in the edit),
both in ms. Nothing is pre-trimmed with ffmpeg, so every cut stays revisable. Write the timeline as
named constants and derive every later start from the durations before it: then lengthening one
clip moves everything downstream and nothing overlaps by accident.

Take cut points from the speech, not from guesses:
- **words** from a local transcript: `npx hyperframes transcribe clip.mp4 --language en --json`
- **timing** from the RMS envelope (`kinetic-type`'s `kt.py`, or `ai-influencer-pro`'s `beats.py`).
  Whisper's word starts drift up to ~0.8 s early on generated clips; the waveform is exact.
- A word the envelope splits into two bursts ("prob-lem") ends at the second burst: read the
  transcript before trusting a window's end.

## When Tesseract, when not

- **Tesseract**: anything with structure — promos, compilations, cut-ins, per-clip captions,
  motion graphics, anything you'll revise.
- **`ai-influencer-pro`'s `edit_hook.py`**: a single hook with burned-in captions, fast.
- **HyperFrames**: explainer videos built from HTML/CSS scenes.
