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

1. **A character sheet before a single video.** Four views on one image, then split. The face has to
   survive a cut before it has to survive an episode.
2. **Lore before episodes.** A one-page bible with a logo prop, speech tics, a taboo and a season goal.
   Behaviour is what people follow; the face is just how they find it again.
3. **An episode engine, not ideas.** One offender + one procedure + one cliffhanger, numbered, with an
   outro card. The audience learns the shape by episode three and comes back for the number.
4. **Flow driven like a person.** `flow.mjs` types into the real UI in a real Chrome profile. There is no
   Flow API; anything that claims otherwise is scraping the same UI with worse error messages.
5. **Assembly that survives mismatched clips.** `assemble.sh` normalises every clip before concat and
   burns the case number, the PART label and the outro card in one pass.

## Hard rules

| # | Rule |
|---|---|
| 1 | **Disclose.** "AI" in the bio, the platform's AI label on every post. The character can carry a product; the character never vouches for it. No "same person btw", no synthetic testimonials. |
| 2 | **The visual lock paragraph goes into every prompt**, and the character is attached as an ingredient on every video shot. Both. One without the other drifts. |
| 3 | **One line of dialogue per 8-second shot.** Two speakers or two lines in one shot produces mumbling on Omni and Veo alike. |
| 4 | **Never generate a group shot as a character reference.** One subject per reference image (from the Mbok Geni bible; it still holds). |
| 5 | **Screenshot after every submit in Flow.** Clicking a card while typing dumps your prompt into that asset's edit box. Count the cards. |
| 6 | **Post 20 episodes before judging the character.** Measure follows per 1,000 views, not views. |
| 7 | **Run one `flow.mjs` at a time** against one profile. Parallel runs trip Flow's "unusual activity" guard and the shots fail without charging you. When you see that card, wait a minute and use the card's retry. |

## The loop

```
bible ──▶ sheet ──▶ character in Flow ──▶ episode plan (json) ──▶ flow.mjs batch ──▶ assemble.sh ──▶ post ──▶ measure
```

1. **Bible.** Copy `templates/bible.md`, fill every line. `references/lore.md` explains each field.
2. **Sheet.** Nano Banana Pro, 16:9, x2, 0 credits on PRO. Prompt in `templates/prompts.md`. Pick one.
   Download 2K. `python3 scripts/split-sheet.py sheet.jpg refs/` gives front / three-quarter / back / face.
3. **Character in Flow.** Characters > New character > Add from project > the sheet. Name it, paste the
   bible into Character info. Now it appears in the "+" picker on every prompt.
4. **Episode plan.** Copy `templates/episode.json`. Three shots: the event, the procedure, the
   escalation. The last line of shot 3 is the cliffhanger. 8 s, 9:16, 720p, x2.
5. **Generate.** `node scripts/flow.mjs batch --project <url> episodes/s1e01.json`. It attaches the
   character, submits each shot, waits for the % badges to clear, downloads 1080p. ~72 credits per
   episode at x2. `references/flow-mechanics.md` has the UI as of today and the failure modes.
6. **Pick and assemble.** Watch both takes of each shot, keep one, then
   `scripts/assemble.sh out.mp4 --case "CASE #0041" --part "PART 1" --handle @handle s1.mp4 s2.mp4 s3.mp4`.
7. **Post.** `references/warm-up.md`: days 1-4 no posting, then one episode a day in the same slot,
   AI label on, PART number in the caption, reply in character for the first hour.
8. **Measure.** Follows per 1,000 views and 3-second completion. Nothing else for 30 days.

## Capability map

| I need to... | Go to |
|---|---|
| Write the character, the lore, the season | `references/lore.md`, `templates/bible.md` |
| Exact prompts that produced a usable sheet and shots | `templates/prompts.md` |
| Drive Flow from the terminal | `scripts/flow.mjs` |
| Understand the Flow UI, credits, models, download sizes | `references/flow-mechanics.md` |
| Split a sheet into references | `scripts/split-sheet.py` |
| Stitch shots, burn labels, add the outro | `scripts/assemble.sh` |
| Warm up the account, labels, what to measure | `references/warm-up.md` |
| Case studies with numbers (Yang Mun, Patryczek, Cringe Boy, Mbok Geni) | `references/case-studies.md` |

## What this skill refuses to do

- Generate a real person's face, or a character that reads as a specific real person.
- Write testimonials, before/after bodies, medical or financial claims in the character's voice.
- Run more than one Flow session per profile, or retry a failed shot in a loop.
