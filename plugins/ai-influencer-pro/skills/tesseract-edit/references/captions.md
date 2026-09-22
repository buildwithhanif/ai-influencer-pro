# Captions

## Standard

`PRESETS["capcut"]`: Montserrat ExtraBold 74, white, black outline 9 px drawn behind the fill,
centred at y 1170, two or three words a chunk, no animation. Chunks come from the transcript,
split with `|`, timed across the phrase by length.

## A compilation: every person is a different account

When the video's claim is "these are all different people", a shared caption style gives the game
away. Hanif, 23 Sep 2026: "its weird to see them have the same caption style... each character is
different. they have their own content/account." Give each person a different ORDINARY preset —
the kinds real creators actually pick — and keep the same person's preset if they appear twice:

`tiktok-box` · `one-word` · `lowercase` · `white-box` · `purple-box` · `serif-italic` · `lime` ·
`yellow-word` · `red-box` · `elegant` · `genz` · `yellow-box` · `top` · `glow`

The narrator does not get a caption preset at all: he gets kinetic type (`kinetic-type` skill).
That difference is the whole grammar of the edit.

## Mechanics that matter

- **Measure with the real font** (`tsx.measure`, PIL). A background box is sized to the words; a
  chunk wider than 940 px shrinks instead of wrapping.
- **Clamp in one unit.** `captions(..., offset, clip_start, clip_end)`: chunk times are source
  seconds, clip bounds are edit seconds. Mixing them let a caption tail bleed 0.25 s onto the next
  person's face.
- **Don't caption a voice you can't hear.** When a cut-in ducks the clip underneath, its captions
  stop.
- **`lead`**: don't start a caption while its clip is still swiping in (pass `lead=0.18`).
- **Contrast**: a thin serif on a light sweater needs a tight dark shadow (`elegant` uses
  black 90% at blur 10), not a soft wide one.
