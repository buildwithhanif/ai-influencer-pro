# The reference frame (step 1, half the work)

Why: a video model animates what is in the image. A generated portrait has no sensor grain, no pores,
no under-eye lines, no micro-expression, so the animation has nothing real to move and the viewer's
face-reading circuit flags it as fake. A frame from a real phone video carries all of that for free.

Budget half the total effort here. Whatever quality you accept at this step becomes the ceiling for
every video the character ever makes.

## Where

- Younger character: TikTok. Millennial: Instagram. Older: Facebook.
- **Not Pinterest.** It used to be the standard move and it is now full of AI images, which puts you
  back where you started.
- Search the niche plus "talking" / "review" / "storytime" / "my setup". Skip aesthetic B-roll; you
  need a face talking to a phone.
- Download the video, then pull a spread of candidates rather than hunting for one:

```bash
ffmpeg -v error -i creator.mp4 -vf "fps=1/6,scale=720:-2" -frames:v 12 cand/%02d.jpg
```

## Score them instead of squinting

```bash
python3 scripts/score-frames.py cand/ --sheet contact.jpg --json scores.json
```

It ranks the candidates and writes a contact sheet with the numbers burned under each thumbnail.
Open the sheet. The ranking is a filter, not a decision.

| Number | What it is | Where real frames sit |
|---|---|---|
| `skin_clip` | % of skin at luma ≥ 250, i.e. blown to pure white | 0.000 - 0.002 |
| `skin_detail` | fine texture over skin, contrast-normalised | 3.8 - 9.9 |
| `skin_grain` | the same, restricted to flat skin: noise with the structure removed | 2.1 - 6.7 |
| `sharp` | the same over the whole frame; catches motion blur | 2.2 - 4.2 |
| `bg_entropy` | how much is going on outside the face zone | 5.4 - 5.8 |
| `captions` | rows of white-on-dark glyphs, as y% ranges | — |

Measured on 18 frames from one creator's video at 720x1280. Re-measure on your own footage before
trusting the WARN band.

**`skin_clip` is the one to care about.** Blown highlights have no data in them, so the video model
has nothing to animate there and the skin goes glossy and waxy. It is also the failure you cannot
see by eye on a dim laptop: brightening one of those real frames by 1.3x takes it from 0.001% to
2.8% clipped, and it still looks fine on screen.

Three ways the scorer will mislead you if you let it:

- It does **not** detect faces. It assumes a talking head and looks for skin in a default zone
  (x 20-80%, y 5-65%). If `face_fill` comes back under 4%, the zone is wrong and every skin number
  is meaningless: pass `--zone x0,y0,x1,y1`.
- `skin_grain` is **not an AI detector**. A Nano Banana avatar built off a good reference scored 6.4,
  above most of the real frames. It tells you there is texture, not where the texture came from.
- It does not judge framing, and it has no opinion about whether the person suits the product.

## What you are actually choosing (in this order)

1. **Framing.** Seated or standing, leaning in or back, table or no table, phone at eye level or
   looking up or down, both hands visible. This is a decision, not a measurement, and it does not
   have to be clever. It has to be deliberate, because it is fixed for the next hundred videos.
2. **Lighting.** Soft and directional. Shine on the forehead with detail still in it is fine, right
   up to the line. Past the line is dead pixels. This is what `skin_clip` measures.
3. **Background.** Not busy, but with a life in it: a frame on the wall, a mirror, a plant, depth
   for the light to change across. A blank wall gives the character nowhere to live.
4. **Audio logic.** Is there a visible reason the sound will be clean — a handheld mic, a lav, a desk
   mic, the phone very close? Generated audio comes back clean and the scene has to earn it. If
   there is nothing, add one in the avatar prompt.

## Blend in, then stick out

Copy what real creators in the niche actually do, so the video does not read as the odd one out in
the feed. Then add one thing that is slightly wrong on purpose — a mic clipped somewhere strange,
one earbud in, an odd mug — because a small unexplained detail makes a thumb stop. Native enough to
belong, odd enough to be looked at.

Burned-in captions are a nuisance rather than a disqualifier. The scorer reports where they are and
flags one that crosses the face, because erasing text off a face is exactly where a one-shot avatar
edit falls apart. If every frame of the video has captions, use it anyway and write the removal into
the prompt.

## Legal and decency

- The reference is a real person. The avatar must be a genetically different human: different eyes,
  nose, skin tone, face shape, an added mole. The test is whether, without surgery, they could be
  the same individual. Hair and clothes are not enough.
- Blur the reference face in anything you publish. We do not show the stranger's face.
- Never a medical professional, never a public figure.

## When to throw it away

About 1 in 10 references will not animate cleanly whatever you prompt. Three failed renders on one
reference is the line: stop, score some new candidates, start again. Images are free on Pro and
video is not.
