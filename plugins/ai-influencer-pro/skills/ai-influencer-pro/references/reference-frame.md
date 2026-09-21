# The reference frame (step 1, half the work)

Why: a video model animates what is in the image. A generated portrait has no sensor grain, no pores,
no under-eye lines, no micro-expression, so the animation has nothing real to move and the viewer's
face-reading circuit flags it as fake. A frame from a real phone video carries all of that for free.

## Where
- Younger character: TikTok. Millennial: Instagram. Older: Facebook.
- Search the niche + "talking" / "review" / "my setup". Skip aesthetic B-roll; you need a face talking to
  the phone. TikHub/Apify search endpoints return cover + play URLs; `curl` the mp4, then
  `ffmpeg -ss 1 -i v.mp4 -frames:v 1 -q:v 2 ref.jpg`. Grab 5-7 frames and pick.

## What to check (in this order)
1. Framing: seated or standing, lean in/back, table or not, phone height (eye level / looking up /
   looking down), both hands visible, no caption over the face if the creator ever leaves one clean.
2. Lighting: soft and directional. No blown-out white on forehead, nose or cheeks: blown = no data =
   wax when animated. Shine with detail in it is fine, right up to the line.
3. Background: not busy, but a life in it. A wall and a frame, a mirror, a plant, depth for the light to
   change. This room is where the character lives for a hundred videos.
4. Audio logic: is there a visible reason the sound will be clean (handheld mic, lav, desk mic, phone
   very close)? If not, add one in the avatar prompt.

## Legal and decency
- The reference is a real person. The avatar must be a genetically different human: different eyes,
  nose, skin tone, face shape, an added mole. Test: without surgery, could they be the same person?
- Blur the reference face in anything you publish. The transcript's agency shows before/afters; we do
  not show the stranger's face.
- Never a medical professional, never a public figure.

## When to throw it away
About 1 in 10 references will not animate cleanly whatever you prompt. Do not fight the video model.
Go back here and pick another frame; images are free and video is not.
