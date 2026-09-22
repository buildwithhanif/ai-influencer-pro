---
name: kinetic-type
description: Apple-style kinetic typography for a presenter talking to camera, built natively in Tesseract (tsrct) — a small context line with a big bold keyword stacked under it, mixed weights and italics in one line, words landing in sync with the speech, one accent word in orange. Use on "animasi teks", "text animation", "kinetic text", "kinetic typography", "teks kayak Apple", "Apple style text", "animated text for my part", "teks yang muncul pas gue ngomong", "bikin teks kayak video ini" with a reference video, or whenever a narrator or explainer shot should read as designed rather than subtitled. NOT for UGC creators or characters in a montage: they get ordinary subtitles in a different preset each, and kinetic type is what marks the narrator apart from them.
---

# Kinetic type

The look: a narrator explains something, and the key idea builds on screen as he says it.

```
      they are posting            <- small, Medium, arrives word by word
  10 times a day                  <- big, ExtraBold, lands with a scale-in
  ^^ orange                          one accent word, never two
```

It is **not** a subtitle. It can shorten the line ("10x a day"), it picks the one or two words
that carry the idea and makes them big, and it sits in the open space of the frame, never at the
bottom by default and never on the face.

Approved on the AI UGC promo (23 Sep 2026): "I LIKE THE TEXT ANIMATION". The worked spec from that
edit is `examples/promo-v4.json`.

## Rules

1. **Narrator only.** On a compilation of characters or UGC creators, they get normal captions —
   and each a different preset, so each reads as their own account. Kinetic type is the narrator's
   voice; spreading it to the cast erases the difference the edit is built on.
2. **Words land on speech.** Take the WORDS from a local whisper transcript and the TIMING from the
   waveform. Whisper's word starts drift up to ~0.8 s early and it snaps the first word to 0.0.
   `kt.py plan` does both.
3. **Place it by looking.** Render the card at two or three heights on a real frame
   (`kt.py proto`) and pick. White type needs a dark field: navy studio wall, a black t-shirt,
   a dim room. It never goes on a face, on hair, or on a light sweatshirt.
4. **One accent per card, and not on every card.** Orange (#FF9F0A) on the number or the claim.
5. **Check the settled frame at full resolution** (`kt.py check`). A filmstrip thumbnail can catch
   a big word mid-scale-in and make it look wrongly placed.

## The loop

```bash
KT=~/.claude/skills/kinetic-type/scripts/kt.py

# 1. draft cards from the clip's real speech (clip seconds)
python3 $KT plan clip.mp4 --out kt.json
#    edit kt.json: choose each big line, mark *bold* _italic_ !accent, set offset + y

# 2. decide placement on a real frame
python3 $KT proto clip.mp4 --at 2.0 --text "they are _posting_|!10 times a day" --y 40 1000 1300

# 3. inject into any Tesseract project (re-runnable; replaces its own kt: layers)
python3 $KT build kt.json --project edit.tsrct

# 4. look at every card, settled, full resolution
python3 $KT check kt.json --project edit.tsrct --out kt-check.png
```

`offset` in the spec maps clip seconds onto the edit: `offset = edit_start - source_in`.

**If the project is regenerated from a build script** (the doc is rebuilt and committed every
time), `kt.py build` output will be wiped by the next commit. Then use the library directly:

```python
sys.path.insert(0, os.path.expanduser("~/.claude/skills/kinetic-type/scripts"))
import kinetic
layers, keys, warns = kinetic.build(spec, next_id=3000)     # add layers to your doc
actions = kinetic.motion_actions(keys)                        # apply after your commit
```

and import `kinetic.font_files()` into the project with `tsrct project import-font`.

## Capability map

| I need to… | Go to |
|---|---|
| The design grammar: sizes, weights, italics, accent, what makes it read as Apple | `references/style.md` |
| Where it goes in the frame, per kind of shot | `references/placement.md` |
| Words from whisper, time from the waveform, when to rewrite the line | `references/timing.md` |
| The spec format and markup | `references/spec.md` |
| Tesseract traps that bite this (fonts, anchors, commit wipes motion) | `references/tesseract.md`; everything else about the edit: the `tesseract-edit` skill |
| Doing it with Omni 1.1 video editing instead, and why it lost | `references/omni.md` |
| Font addressing for a face that is not Inter | `scripts/fontprobe.py` |

## What it needs

- Tesseract 0.1.0+ at `~/Library/Application Support/Tesseract/bin/tsrct`
- ffmpeg, Python 3 with Pillow
- Node for `npx hyperframes transcribe` (local whisper, used by `plan` only)
- Inter is bundled in `assets/fonts/Inter` (OFL, see `OFL.txt`), so nothing else to install
