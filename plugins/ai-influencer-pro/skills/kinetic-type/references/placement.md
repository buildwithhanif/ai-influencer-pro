# Placement

White type needs a dark, empty field. Find it on a real frame — `kt.py proto` renders the same
card at several heights side by side — and never assume where the space is.

## What worked, by shot

| Shot | Where the card goes |
|---|---|
| Studio portrait, subject centred, navy wall | the band **above the head**, `y` ~40. The side strips beside the head are only ~280 px wide: too narrow for a big line |
| Subject over another clip (a cut-in in a corner) | over the **background clip's darkest area** beside the cut-in. On the promo that was the grey Robyn's black t-shirt, `cx` 640, `y` 900-1000, right of the cut-in |
| Subject on the left or right third | the empty side, `cx` at the centre of that side |

## What failed

- **On a light sweatshirt.** White with a heavy shadow turns to mush on cream. Dark ink text on it
  is readable but looks printed on the shirt.
- **On hair or forehead.** Omni 1.1's own attempt put the big line there; it reads as a mistake.
- **At the bottom by default.** That makes it a subtitle again.

## Clearance

- Keep 40 px from every frame edge. `kinetic.card` shrinks a line that would exceed 1000 px rather
  than let it overflow, and says so.
- Leave the top 30 px alone on anything posted to TikTok or Reels, where the app draws over it.
- A face must stay fully visible for the whole card, including the moment a big word is at 124%
  mid-scale: that is 24% wider than the settled word.
