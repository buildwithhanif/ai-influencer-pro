---
name: ai-influencer-pro
description: >
  Build and run a recurring AI character (an "AI influencer") as a series on TikTok, Reels and Shorts:
  lock the face with a character sheet, write the lore, plan numbered episodes, generate every shot in
  Google Flow (Nano Banana for images, Omni / Veo for video) through a real browser, stitch the shots
  with ffmpeg, and warm the account up so the platform lets people see it. Use on "make an AI
  influencer", "AI character account", "bikin AI influencer", "virtual creator", "faceless character
  series", "run Google Flow for me", "stitch these clips", or whenever someone wants a synthetic person
  that posts every day instead of a one-off AI video.
---

# AI Influencer Pro

**Everyone teaches you how to generate a convincing fake person saying a script. Nobody teaches you how
to run that person as a series.** This skill is the second half. It assumes you can already get a good
image out of a model; it tells you what to lock, what to write down, in what order to generate, and how
to post so the account survives its first month.

Five things a generic "make an AI influencer" prompt will not give you:

1. **A real reference frame before any generation.** A still from a real creator's phone video, chosen
   for framing, lighting (no blown highlights) and a background with a life in it. Generated portraits go
   waxy when animated because there is nothing real in them to animate. This is 50% of the work.
2. **A one-shot avatar.** Nano Banana Pro, one prompt with every change in it (a genetically different
   person, one accessory, a visible reason the audio is clean, the logo prop), spam-generate until one is
   right. Never edit in rounds.
3. **A hook written before the character, and a locked three-part video prompt.** The first eight seconds
   are the product; the rest of the clip only justifies them. Test a new character on a hook alone.
   Then: Scene (camera movement stated, camera, action, energy), the line
   in quotes, fixed rules stacked from what went wrong. Lock it on one line, then only swap the line.
4. **A bible and a number.** Niche, one product a day, logo prop, three lines, a taboo; DAY n on every
   post and an outro card. Behaviour is what people follow; the face is how they find it again.
5. **Flow driven like a person, and ffmpeg for the rest.** `flow.mjs` types into the real UI in a Chrome
   profile you log into once (there is no Flow API). `assemble.sh` stitches, labels, numbers.

## Hard rules

| # | Rule |
|---|---|
| 1 | **Disclose.** "AI" in the bio, the platform's AI label on every post. The character can carry a product; the character never vouches for it. No "same person btw", no synthetic testimonials. |
| 2 | **Start from a real reference frame**, never from a text prompt. The avatar is attached as a Character ingredient on every clip AND the scene paragraph of the locked prompt describes the same room. Both. |
| 3 | **One line of dialogue per 8-second shot.** Two speakers or two lines in one shot produces mumbling on Omni and Veo alike. |
| 4 | **The avatar must be genetically different from the reference** (eyes, nose, skin, face shape), not just hair and clothes. Never deepfake a real person or a medical professional. |
| 5 | **Screenshot after every submit in Flow.** Clicking a card while typing dumps your prompt into that asset's edit box. Count the cards. |
| 6 | **Post 20 episodes before judging the character.** Measure follows per 1,000 views, not views. |
| 7 | **Run one `flow.mjs` at a time** against one profile. Parallel runs trip Flow's "unusual activity" guard and the shots fail without charging you. When you see that card, wait a minute and use the card's retry. |

## The loop

```
bible ──▶ reference frame ──▶ one-shot avatar ──▶ Flow Character ──▶ locked prompt ──▶ flow.mjs batch ──▶ assemble.sh ──▶ post ──▶ measure
```

Time split: 50% reference, 25% locking the prompt, 25% generating everything else.

1. **Bible.** `templates/bible.md`. Niche with an affiliate from post 1, one product per video, logo prop,
   three lines, a taboo, DAY numbering. `references/lore.md`.
2. **Reference.** Find a talking-head creator in the niche (younger: TikTok, millennial: Instagram, older:
   Facebook). Download the video, `ffmpeg -ss <t> -i v.mp4 -frames:v 1 ref.jpg`. Checklist in
   `references/reference-frame.md`. Blur the face before it goes anywhere public.
3. **Avatar.** Upload the reference to Flow (see flow-mechanics for the upload trick), Nano Banana Pro,
   9:16, x2, the one-shot prompt in `templates/prompts.md`. Genetically different person or it is a
   deepfake. Download 2K.
4. **Character in Flow.** Characters > New character > Add from project > the avatar. Name, bible in
   Character info.
5. **Lock the prompt.** Video, Ingredients (the character), Omni 1.1 Flash, 9:16, 720p, 8 s. Three-part
   prompt. Be harsh on the first renders; every complaint becomes a fixed rule. Capitalise the stressed
   word. Pad a 7-second line to 8 with a throwaway word and trim.
6. **Generate the season.** `node scripts/flow.mjs batch --project <url> episodes/day01.json`, one run at a
   time, a pause between clips. ~12 credits per 8 s clip on Pro.
7. **Assemble.** Video: `scripts/assemble.sh out.mp4 --case "TIP 01" --part "@handle" --handle @handle c1.mp4 c2.mp4 c3.mp4`.
   Carousel: generate 4 more scenes with the character attached (free on Pro), then
   `python3 scripts/carousel.py tip01.json --out slides/`. Same tip, two formats, two slots in the calendar.
8. **Post.** `references/warm-up.md`: four days of no posting, then one a day, AI label on, twenty before
   judging. Measure follows per 1,000 views.

## Capability map

| I need to... | Go to |
|---|---|
| Write the character, the lore, the season | `references/lore.md`, `templates/bible.md` |
| Exact prompts that produced a usable avatar and clips | `templates/prompts.md` |
| What to look for in a reference frame | `references/reference-frame.md` |
| Drive Flow from the terminal | `scripts/flow.mjs` |
| Understand the Flow UI, credits, models, download sizes | `references/flow-mechanics.md` |
| Split a 4-view sheet into references (optional, non-talking-head characters) | `scripts/split-sheet.py` |
| Turn generated scenes into a UGC carousel | `scripts/carousel.py`, `templates/carousel.json` |
| Stitch shots, burn labels, add the outro | `scripts/assemble.sh` |
| Warm up the account, labels, what to measure | `references/warm-up.md` |
| Case studies with numbers (Yang Mun, Patryczek, Cringe Boy, Mbok Geni) | `references/case-studies.md` |

## What this skill refuses to do

- Generate a real person's face, or a character that reads as a specific real person.
- Write testimonials, before/after bodies, medical or financial claims in the character's voice.
- Run more than one Flow session per profile, or retry a failed shot in a loop.
