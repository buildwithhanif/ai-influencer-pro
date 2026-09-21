# Google Flow mechanics (as of 20 Sep 2026, PRO plan)

Read this when a Flow step fails. It is the UI as it exists today; Flow changes weekly.

## Plans and credits
- AI Pro ($19.99/mo): 1,000 credits/mo, plus "50 additional Flow credits daily" on the plan banner.
- AI Ultra: 10,000-25,000 credits, about half-price video generations, Nano Banana Pro as default.
- Image: Nano Banana Pro, Nano Banana 2, Nano Banana 2 Lite. In the composer these show "0 credits" on
  PRO for x2. Images are effectively free. Generate sheets in pairs and keep the better one.
- Video: Omni 1.1 Flash (4/6/8/10 s, 720p or 360p at half cost, Ingredients, Frames, Video-to-Video),
  Veo 3.1 Lite / Fast / Quality (4/6/8 s). Omni 1.1 Flash at 720p 8 s x2 shows "24 credits", so
  12 credits per 8-second clip. A 3-shot episode at x2 = 72 credits. PRO gives ~13 episodes a month at
  that rate, plus the daily 50.

## The composer (bottom of every project)
- Placeholder "What do you want to create?". The chip on the right shows kind, model, ratio, count.
  Click it to open: Image | Video, Frames | Ingredients, ratio, model dropdown, resolution, length, x1-x4,
  and the credit cost line.
- "Agent" pill toggles Agent mode. In Agent mode the model chip disappears and Flow's agent plans for you.
  For batch work stay in manual mode. If your script cannot find the chip, Agent mode is on.
- "+" opens the asset picker: All | Images | Videos | Voices | Characters | Avatars | Uploads. Pick,
  then "Add to prompt". The picked asset appears as a thumbnail above the prompt. Submit with Enter or
  the arrow.
- A submitted prompt clears the thumbnail. Re-attach the character for every shot.
- Clicking anywhere on a card while typing opens that asset's edit view, and your prompt lands in the
  image-edit box instead of the video composer. Screenshot after every submit; check the card count.

## Characters
- Left nav > Characters > New character. "Add from project" and pick the sheet. It becomes the
  Portrait. Name it (pencil next to the title), fill "Character info" with the bible, "Select a voice"
  is optional. Done.
- Once a character exists it shows up in the "+" picker under Characters and can be attached to any
  video prompt as an ingredient. That is the consistency lock.

## Download
- Hover a card > "⋮ More" > Download. Images: 1K original, 2K upscaled (free on PRO), 4K (Ultra).
  Videos: 270p / 720p / 1080p. Files land in the browser's download folder with the prompt's first
  words as the file name.

## Known failure modes
- The video card sits blank (no % badge, no thumbnail) for 1-3 minutes on Omni Flash. That is normal.
- A prompt with two speakers or two lines of dialogue in one 8 s shot produces mumbling. One line.
- Ratio and model settings persist per project, but the count resets to x2 for video after a page load.

## Uploading a reference image without the native file picker (21 Sep 2026)
"+" > Upload media creates an `<input type=file>` on the fly and calls `.click()`, which opens a native
picker no browser automation can drive. Patch the prototype first, then click Upload media, then push the
file into the captured input:

```js
window.__fi=null; const oc=HTMLInputElement.prototype.click;
HTMLInputElement.prototype.click=function(){ if(this.type==='file'){ window.__fi=this;
  this.setAttribute('aria-label','FLOWUPLOAD'); if(!this.isConnected) document.body.appendChild(this); return; }
  return oc.call(this); };
```
Then `find "FLOWUPLOAD"` -> `file_upload <ref> <path>`. The file appears under Uploads in the picker
within ~5 s. Synthetic drag-and-drop events on the page do nothing. In Playwright use
`page.waitForEvent('filechooser')` instead; `flow.mjs upload` does this.
