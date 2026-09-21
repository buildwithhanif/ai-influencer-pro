# The locked video prompt, and everything that goes wrong inside it

Step 3. The prompt is not written, it is *found*, by generating one line over and over and turning
every complaint into a rule. Then it is frozen and only the dialogue moves.

## The three parts, in order, always

**Part 1, the scene.**
- **State the camera movement even when there is none.** "Static, locked-off shot." Leave it out and
  you get drift and hallucinated camera moves. Handheld is a choice you make on purpose:
  "Handheld UGC iPhone shot."
- **Name the camera or shot type.** "UGC iPhone front-camera footage." The model matches the whole
  look to the equipment you name, so naming a Canon body gets you a podcast look and naming a phone
  gets you a feed look. This is the cheapest lever in the prompt.
- **Where they are and what is around them.** The same room as the reference frame. Describe it even
  though the character ingredient is attached; the ingredient locks the face, the paragraph locks
  the room.
- **What the body is doing.** Body still, mouth moving naturally, eye contact held with the camera,
  small natural head movements, the other hand resting.
- **Energy, explicitly.** Left out, the delivery comes back flat. "High energy, expressive, like a
  creator who has done this a hundred times" is the default. For a calm character say calm and blunt
  instead, but say something.

**Part 2, the line.** In quotes, one line, one shot.

**Part 3, the fixed rules.** A stacked list you build by being harsh. Generate, watch it, and for
every single thing that annoyed you add a rule:

| What you saw | What you add |
|---|---|
| flat, low energy | high energy, expressive |
| unsure of herself | confident |
| dragging | faster pace |
| stone-faced | a small smile at the end |
| it cut to another angle | **one continuous take, no jump cuts** |
| text appeared on screen | no text on screen, no captions |
| the camera drifted | no camera movement |

"One continuous take, no jump cuts" belongs in almost every prompt, and it belongs there before you
have seen a jump cut, especially when there is any movement in the scene.

## Lock it, then stop touching it

1. Generate one line. Judge it harshly.
2. Regenerate the SAME line, adding a rule each time, until energy, framing, pace and feel are where
   you want them.
3. From then on, change nothing but the dialogue.

This is the whole answer to the inconsistency everybody complains about. The people whose AI
characters drift are changing the scene paragraph between shots without realising it.

## Durations: 4, 6, 8, 10 and nothing else

A line that lands at 7 seconds has two bad options. Render it at 6 and the character either paces it
properly and gets cut off mid-word, or rushes and it turns to mush. Render it at 8 and the character
slows down and sounds simple.

The fix is to **pad the line with throwaway words, render at the longer duration, and cut the
padding off in the edit**. The character then paces the real line correctly because, as far as it
knows, the line really is 8 seconds long.

`scripts/script-plan.py` does the arithmetic: it estimates each line from its syllable count, picks
the slot, writes the padded version into the episode JSON, and emits a shell script of the exact
ffmpeg trims. Padding is only applied to a line that genuinely sits *between* two slots. A line
under 4 seconds has no lower slot to be cut off by, so it just gets a beat of silence at the end,
and that is fine.

The estimator defaults to 2.9 words per second, which is high-energy delivery. Calibrate it once:
render one line, time the result, pass `--wps`. It is a starting point, not physics.

A line that needs more than 10 seconds is not a long line, it is two lines. The planner says so.

## Intonation is capitalisation

Capitalise the word you want stressed, then regenerate.

- "So weak follicles wake back up" — the stress lands on "weak" and "wake".
- "So weak FOLLICLES wake back up" — it moves to "follicles".

It changes how the claim lands, and it is free. The planner picks a word for you and prints it, so
read what it chose before you generate; the longest content word is usually right and occasionally
very wrong.

## Scene changes

One per video, roughly. The same character in a new position or a new setting partway through.
It resets attention without resetting recognition. Mark it with `## scene:` in the script and the
planner carries the index through to the episode JSON so you know which shots need the new scene
paragraph.

## Throw the reference away at three strikes

About one reference frame in ten simply will not animate cleanly, whatever you write. Do not fight
it. Images are free on the Pro plan and video is not, so going back to step 1 and building a new
reference is cheaper than three more rounds of video that look great for two seconds and then break.

Three failed renders on the same reference is the line. Stop, re-score some new candidate frames,
start again.

## Judging the render

Do the mechanical half with `scripts/qc.py` before you watch anything:

```bash
python3 scripts/qc.py episodes/tip01/clips --episode episodes/tip01.json
```

It catches jump cuts, frozen tails, black frames, silent audio and clips that came back short of
their slot. What it cannot judge is whether the energy is right and whether she reads as a person.
That part is still yours, and it is the part worth your attention.

## The quality ceiling on Flow

Flow's Omni is the Flash variant. The full Gemini Omni, through an API, is better on teeth and hand
motion. Flash is what a $19.99 plan buys, and it holds up for a talking head at phone distance. It
is not there yet for a walking shot.

Every Omni avatar shares the same set of teeth. Not a joke, and not fixable. Keep the mouth small in
frame and it does not matter.
