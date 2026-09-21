---
name: ai-influencer-pro
description: >
  Build and run a recurring AI character (an "AI influencer") as a series on TikTok, Reels and Shorts:
  write the script and the bible first, source a real reference frame and score it, make the avatar in
  one shot, lock a three-part video prompt, plan every line to Omni's 4/6/8/10 second slots, generate
  in Google Flow through a real browser, QC the renders, stitch with ffmpeg, and warm the account up so
  the platform lets people see it. Use on "make an AI influencer", "AI character account", "bikin AI
  influencer", "AI UGC", "realistic UGC ad", "virtual creator", "faceless character series", "run
  Google Flow for me", "score these reference frames", "stitch these clips", or whenever someone wants
  a synthetic person that posts every day instead of a one-off AI video.
---

# AI Influencer Pro

**Everyone teaches you how to generate a convincing fake person saying a script. Nobody teaches you how
to run that person as a series.** This skill is the second half. It assumes you can already get a good
image out of a model; it tells you what to lock, what to write down, in what order to generate, and how
to post so the account survives its first month.

Six things a generic "make an AI influencer" prompt will not give you:

1. **The script before the face.** Format cannot save a weak message, and the character is a script
   engine, not a portrait. Who they are is a decision with a reason: someone who has *solved* the
   problem, with the expertise one relationship away from them (her dad worked homicide, not she is a
   detective). `references/script-and-storyboard.md`.
2. **A real reference frame, scored, before any generation.** A still from a real creator's phone
   video, chosen on framing, on lighting with no blown highlights, and on a background with a life in
   it. Generated portraits go waxy when animated because there is nothing real in them to animate.
   This is 50% of the work, and `scripts/score-frames.py` does the half of it that is measurable.
3. **A one-shot avatar.** Nano Banana Pro, one prompt with every change in it (a genetically different
   person, one accessory, a visible reason the audio is clean, the logo prop), spam-generate until one
   is right. Never edit in rounds: each round feathers seams that are invisible in the still and
   obvious the moment it moves.
4. **A hook written before the character, and a locked three-part prompt.** The first eight seconds
   are the product; the rest of the clip only justifies them. Test a new character on a hook alone.
   Then: scene (camera movement stated, camera, action, energy), the line in quotes, fixed rules
   stacked from what went wrong. Lock it on one line, then only swap the line.
5. **Lines planned to the slot.** Omni renders 4, 6, 8 or 10 seconds and nothing between, so a
   7-second line is either cut off or drawled. `scripts/script-plan.py` estimates every line, pads the
   ones that fall between slots, and emits the ffmpeg trims.
6. **A bible, a number, and a QC pass.** Niche, one tip a day, logo prop, three lines, a taboo; DAY n
   on every post. `scripts/qc.py` catches the jump cuts, frozen tails and silent audio before you look
   at anything.

## Hard rules

| # | Rule |
|---|---|
| 1 | **Disclose.** "AI" in the bio, the platform's AI label on every post. The character can carry a product; the character never vouches for it as a person who used it. No synthetic testimonials. |
| 2 | **Start from a real reference frame**, never from a text prompt. The avatar is attached as a Character ingredient on every clip AND the scene paragraph describes the same room. Both. |
| 3 | **One line of dialogue per shot.** Two lines in one clip produces mumbling on Omni and Veo alike. |
| 4 | **The avatar must be genetically different from the reference** (eyes, nose, skin, face shape), not just hair and clothes. Never deepfake a real person. Never a medical professional, and never let a character claim a credential it would need a licence for. |
| 5 | **Screenshot after every submit in Flow.** Clicking a card while typing dumps your prompt into that asset's edit box. Count the cards. |
| 6 | **Post 20 episodes before judging the character.** Measure follows per 1,000 views, not views. |
| 7 | **Run one `flow.mjs` at a time** against one profile. Parallel runs trip Flow's "unusual activity" guard and the shots fail without charging you. When you see that card, wait a minute and use the card's retry. |
| 8 | **Three failed renders on one reference means a new reference**, not a fourth prompt. About 1 in 10 frames will not animate whatever you write. Images are free on Pro; video is not. |

## The loop

```
script ─▶ reference frames ─▶ score ─▶ one-shot avatar ─▶ Flow Character ─▶ lock the prompt
       ─▶ plan the lines ─▶ flow.mjs batch ─▶ qc ─▶ trim ─▶ assemble ─▶ post ─▶ measure
```

Time split: 50% reference, 25% locking the prompt, 25% generating everything else. Rushing the first
half produces the too-perfect, fake-looking AI UGC everyone else ships, and whatever you accept early
becomes the standard the whole series is locked into.

0. **Bible and script.** `templates/bible.md`, `templates/script.md`. Niche with an affiliate from
   post 1, one tip per video, logo prop, three lines, a taboo, DAY numbering.
   `references/script-and-storyboard.md`, `references/lore.md`.
1. **Reference.** Find a talking-head creator in the niche (younger: TikTok, millennial: Instagram,
   older: Facebook). Pull a spread of candidates, then score them:
   ```bash
   ffmpeg -v error -i creator.mp4 -vf "fps=1/6,scale=720:-2" -frames:v 12 cand/%02d.jpg
   python3 scripts/score-frames.py cand/ --sheet contact.jpg
   ```
   Open the contact sheet. The ranking is a filter, not a decision — framing is still yours.
   `references/reference-frame.md`. Blur the face before it goes anywhere public.
2. **Avatar.** Upload the reference to Flow (upload trick in `references/flow-mechanics.md`), Nano
   Banana Pro, 9:16, x2, the one-shot prompt in `templates/prompts.md`. Genetically different person
   or it is a deepfake. Download 2K.
3. **Character in Flow.** Characters > New character > Add from project > the avatar. Name it, paste
   the bible into Character info.
4. **Lock the prompt.** Video, Ingredients (the character), Omni 1.1 Flash, 9:16, 720p, 8 s. Three
   parts. Be harsh on the first renders; every complaint becomes a fixed rule. Save part 1 as
   `scene.txt` and part 3 as `rules.txt` and never edit them again. `references/prompt-craft.md`.
5. **Plan the lines.**
   ```bash
   python3 scripts/script-plan.py tip01.md --scene scene.txt --rules rules.txt \
     --character "NAME" --project <flow-url> \
     --storyboard tip01-sb.md --episode episodes/tip01.json --trims episodes/tip01-trim.sh
   ```
   Read the stressed word it picked for each line before you generate. It is right most of the time.
6. **Generate.** `node scripts/flow.mjs batch --project <url> episodes/tip01.json`, one run at a time,
   a pause between clips. ~12 credits per 8 s clip on Pro.
7. **QC, then trim.**
   ```bash
   python3 scripts/qc.py episodes/tip01/clips --episode episodes/tip01.json
   sh episodes/tip01-trim.sh
   ```
8. **Assemble.** Video: `scripts/assemble.sh out.mp4 --case "TIP 01" --part "@handle" --handle @handle c1.mp4 c2.mp4 c3.mp4`.
   Carousel: generate 4 more scenes with the character attached (free on Pro), then
   `python3 scripts/carousel.py tip01.json --out slides/`. Same tip, two formats, two slots in the
   calendar.
9. **Post.** `references/warm-up.md`: four days of no posting, then one a day, AI label on, twenty
   before judging. Measure follows per 1,000 views.

## Capability map

| I need to... | Go to |
|---|---|
| Decide who the character is, write the script, storyboard it | `references/script-and-storyboard.md`, `templates/script.md` |
| Write the character, the lore, the season | `references/lore.md`, `templates/bible.md` |
| Pick a reference frame, and know why it will fail | `references/reference-frame.md` |
| Score candidate frames, contact sheet, clipping check | `scripts/score-frames.py` |
| Exact prompts that produced a usable avatar and clips | `templates/prompts.md`, `templates/scene.txt`, `templates/rules.txt` |
| Build the locked prompt, durations, stress, scene changes | `references/prompt-craft.md` |
| Time the lines, pad them, emit the episode JSON and the trims | `scripts/script-plan.py` |
| Drive Flow from the terminal | `scripts/flow.mjs` |
| Understand the Flow UI, credits, models, download sizes | `references/flow-mechanics.md` |
| Check the renders before watching them | `scripts/qc.py` |
| Split a 4-view sheet into references (non-talking-head characters) | `scripts/split-sheet.py` |
| Turn generated scenes into a UGC carousel | `scripts/carousel.py`, `templates/carousel.json` |
| Stitch shots, burn labels, add the outro | `scripts/assemble.sh` |
| Warm up the account, labels, what to measure | `references/warm-up.md` |
| Case studies with numbers (Yang Mun, Patryczek, Cringe Boy, Mbok Geni) | `references/case-studies.md` |

## What this skill refuses to do

- Generate a real person's face, or a character that reads as a specific real person.
- Write testimonials, before/after bodies, medical or financial claims in the character's voice, or
  let a character claim a credential a real one would need a licence for.
- Run more than one Flow session per profile, or retry a failed shot in a loop.

## Credit

The reference-frame-first method (real frame → genetically different avatar → locked three-part
prompt, and the 50/25/25 split) comes from Kristian Jennings' AI UGC walkthrough, which credits Ad
Creators Lab for the reference-image idea. What is added here is everything about running the thing
as a series instead of as one ad, Google Flow in place of a pay-as-you-go API, and the scripts that
turn the manual checks into measurements.
