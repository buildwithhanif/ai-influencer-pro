# Editing a hook, and cutting the cast reel

A raw Omni clip is a person talking in a room. What makes it read as a finished post is
typography, one accent, and sound you are not supposed to notice. This is that layer.

Scripts: `scripts/beats.py`, `scripts/edit_hook.py`, `scripts/montage.py`.

## Rule 1: cut on real speech, never on a guess

`silencedetect` is useless on these clips. Omni renders a continuous room tone, so nothing
ever crosses a silence threshold and ffmpeg reports no silence at all. Read the RMS envelope
instead:

```bash
python3 scripts/beats.py clips/hook-01.mp4
```

```
speaking level ~-32.6 dB, gate -42.6 dB, 6 phrases
  1.   0.19 ->  1.41   (1.22s)
  2.   1.96 ->  3.63   (1.66s)
  ...
gaps worth cutting on:
   1.41 ->  1.96   (0.55s of air)
```

Captions change on those boundaries and nowhere else. Typing timings by ear puts them a third
of a second late, which reads as cheap even when the viewer cannot say why.

**It also finds the trim.** The throwaway tail you padded the line with ("That is it") shows up
as a short run after the last big gap. Set the plan's `duration` just before it and the hook
ends on the real word.

## Rule 2: the type is Apple, and it is restrained

| | |
|---|---|
| Captions | SF Pro Display Bold, 70 px on a 1080-wide frame, centred, lower third at y≈1420 |
| Legibility | soft shadow built from the type's own alpha, blurred 16 px. **Not a stroke, not a box.** A stroke reads as a meme caption; a box covers the room you spent half the work choosing |
| Accent | systemOrange `#FF9F0A`, on **exactly one word per clip**, and only a word the voice already stresses. Two accents and neither means anything |
| Kicker | none. A name badge was tried and cut: it made the clip look like a corporate lower third |

**Balance the line breaks.** Greedy wrapping produced "Nobody told me this until I / was 59."
An orphan like that is the single most amateur thing a caption can do. `edit_hook.py` finds
the fewest lines that fit, then picks the split that makes them most even.

Everything renders at **1080x1920** even though the source is 720x1280. The video gets
upscaled, but the type is drawn at full size rather than scaled up with it, and that is most
of why the result looks finished.

## Rule 3: the sound sits under the floor

One swoosh on the open, a UI tick on each caption change, a softer one on the punch. Nothing
on the cut itself. Everything at **-22 dB or lower** against a voice normalised to -16 LUFS.

The test: if you can name the sound on a first watch, it is too loud.

## Rule 4: pin the sample rate after loudnorm, and verify it

`loudnorm` runs at 192 kHz internally **and outputs at 192 kHz**. The aac encoder cannot take
that, so it silently lands on 96 kHz. Nothing errors. The clip plays fine on its own.

Then you concat those clips with cards rendered at 48 kHz, and the concat demuxer — which does
not resample, it only concatenates — produces a reel whose audio track is **five seconds
shorter than its video**. Everything after the first card drifts. It looks like a mixing
mistake and it is a sample-rate mistake.

```
loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000
```

plus `-ar 48000 -ac 2` on every output, and `aresample=48000` on every SFX input.

Both scripts now assert it: `edit_hook.py` refuses to finish if the rate is not 48 kHz or if
audio and video lengths differ by more than 0.12 s, and `montage.py` checks every segment
before concat and the reel after. **Add the check to anything that concatenates** — this class
of bug is invisible until someone watches the whole thing.

## Rule 5: the push-in is oversampled

4.5% over the clip. Oversample 2x before `zoompan`, because zoompan rounds its crop to whole
pixels and on a locked-off talking head that rounding shows as a stutter.

```
scale=2160:3840,zoompan=z='min(zoom+0.00023,1.045)':d=1
  :x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=24
```

Note `zoom`, not `z`, inside the x/y expressions. `z` there is a syntax error that only shows
up at filter-configure time.

## The plan file

One JSON per clip; the script never changes.

```json
{ "src": "../<slug>/video/<slug>-hook-01.mp4",
  "out": "out/<slug>-edit.mp4",
  "duration": 8.15,
  "kicker": "",
  "caption_y": 1420, "caption_size": 70, "push": 0.045,
  "beats": [
    { "in": 0.30, "out": 1.50, "words": [["I'm"],["61."]] },
    { "in": 7.22, "out": 8.15, "words": [["is"],["not"],["your"],["MATTRESS.","hit"]] }
  ],
  "sfx": [ { "file": "01. Swoosh fast.mp3", "at": 0.15, "db": -24 } ] }
```

`["word","hit"]` is the accent. `"kicker": ""` drops the top label.

## The cast reel

Fourteen hooks back to back does not work. Every hook is a cold open with no payoff, so by the
fourth the viewer has stopped believing any of them and is waiting for the trick. The reel has
to earn the trick instead:

1. **Cold open.** One hook in full, edited like a real post, no AI signal. Use the *hardest to
   disbelieve* character, which is almost always the oldest one: weathered skin, greys and a
   deadpan delivery are what generators are worst at and what viewers scan for.
2. **The turn.** Black, one line: "None of these people exist."
3. **The run.** Every other character, 1.4 to 4 seconds each, one self-contained clause apiece,
   cut on phrase windows. The viewer stops judging whether it is real and starts counting how
   many there are.
4. **The close.** The numbers.

Run order alternates gender, jumps age, and changes room on every cut. **Two characters who
share a reference room must sit as far apart as possible** — a repeated room is the one thing
that breaks the illusion of a cast.

Every caption in the run is the exact words spoken inside its window. Paraphrasing what you
hear is the fastest way to make a real clip feel fake.

```bash
python3 scripts/montage.py plans/montage.json
```

## Assets

The font pack, SFX library and background kit live in the project's `_editing/` folder, not in
this skill: they are licensed material and too big to vendor. What the skill needs to know is
which ones to reach for — SF Pro Display for captions, SF Pro Text for small type, and the UI
and swoosh folders for sound.
