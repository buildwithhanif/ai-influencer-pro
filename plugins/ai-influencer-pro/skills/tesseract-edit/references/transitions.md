# Transitions and cuts

## Feed swipe (between creators)

`Edit.swipe(incoming_id, at, outgoing, sfx_asset=..., sfx_len_ms=...)`. The incoming clip rises
from below over 180 ms while everything on screen rises out of the top, with motion blur and a soft
swoosh. It reads as scrolling a TikTok feed, which is the point of a compilation. Cuts back to the
narrator stay hard cuts: he is not part of the feed.

Built from the **outgoing shot's muted tail**, not the incoming clip's pre-roll: half the creators
start speaking at 0.02 s and have no frames to spare before their cut. The tail is a separate Video
layer at volume 0, so it can never talk over the next person. Check each tail lands in silence
against the transcript. Incoming and outgoing are keyed on ONE easing curve (`FLICK`), so they stay
exactly a frame-height apart. A keyed cut-in on screen scrolls out with the rest: list its matte
tail first, then its picture with `matte: True`.

## Jump cut past a flubbed line

A generated take said "I have 30 AI influencers" twice. Two layers from the same source — the first
ending before the first "30", the second starting at the second — made one clean sentence and
saved a regeneration. Verify by re-transcribing the cut.

## Cut to grey

When the narrator cuts in over a clip, cut that clip to a desaturated copy at the same instant
(`Edit.ducked` with an alternate asset per segment) and drop its gain to ~0.06. It says "this
footage is the subject now" without a word. Make the grey copy with ffmpeg
`hue=s=0,eq=brightness=-0.04:contrast=1.04`.

## Colour drains on a word

For the reveal ("I'm also AI-generated"), cut from the colour take to a `hue=s=0` copy of the SAME
take at the same source time, exactly on the word. Hold the last frame as a still for 1.5-2 s.

## Punch-in

`Edit.punch(lid)`: a cut onto 108% that settles to 100% in 340 ms. Use on a burst of short clips;
don't stack it with a swipe on the same cut.
