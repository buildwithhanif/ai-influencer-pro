# AI Influencer Pro

**Run an AI character as a series, not a render.** Script first → real reference frame, scored → one-shot
avatar → Flow Character → locked three-part prompt → lines planned to Omni's 4/6/8/10 second slots →
Google Flow (Nano Banana Pro + Omni) driven through a real browser → mechanical QC → ffmpeg assembly →
account warm-up.

Every AI-influencer tutorial on your feed teaches the same thing: generate a convincing fake person saying
a script. This repo is the other half. It is what you need on day 2, when the clip worked and you have to
do it again tomorrow with the same face.

MIT licensed. Bring your own character, your own Google AI plan, your own taste.

## Install

```bash
claude plugin marketplace add buildwithhanif/ai-influencer-pro
claude plugin install ai-influencer-pro@ai-influencer-pro
```

Or install it straight into `~/.claude/skills` without the marketplace:

```bash
git clone https://github.com/buildwithhanif/ai-influencer-pro
cd ai-influencer-pro && ./install-skill.sh          # --copy if your loader won't follow symlinks
```

Or point any coding agent at this repo and tell it to follow
`plugins/ai-influencer-pro/skills/ai-influencer-pro/SKILL.md`.

**Requirements:** a Google AI Pro or Ultra plan (Flow credits), Chrome, node 20+ with `playwright`
(`npm i playwright` in the scripts folder), `ffmpeg`/`ffprobe`, python 3.9+ with Pillow.

## The loop

```
script ─▶ reference frames ─▶ score ─▶ one-shot avatar ─▶ Flow Character ─▶ lock the prompt
       ─▶ plan the lines ─▶ flow.mjs batch ─▶ qc ─▶ trim ─▶ assemble ─▶ post ─▶ measure
```

Three of those steps used to be judgement calls made at 1am. They are now measurements:

| Instead of | Run |
|---|---|
| squinting at a frame to see if the highlights are blown | `score-frames.py cand/ --sheet contact.jpg` |
| guessing whether a line is 6 or 8 seconds long | `script-plan.py tip01.md --episode ep.json --trims trim.sh` |
| watching every render twice looking for a jump cut | `qc.py clips/ --episode ep.json` |

`score-frames.py` measures clipped highlights on skin specifically, which is the failure you cannot
see on a dim laptop: brightening a real frame by 1.3x takes it from 0.001% clipped to 2.8% and it
still looks fine on screen. It also finds burned-in captions and tells you when one crosses the face.

| Step | Tool | Cost |
|---|---|---|
| reference frame | a real creator's video + one ffmpeg command | free |
| avatar, 2 variants | Nano Banana Pro in Flow, reference attached | 0 credits on PRO |
| 3 clips x 2 takes, 8 s, 720p | Omni 1.1 Flash in Flow | 72 credits (~$1.44 at PRO's $19.99 / 1,000) |
| assembly, labels, outro | `assemble.sh` (ffmpeg) | free |

## Files

| Path | Does |
|---|---|
| `skills/ai-influencer-pro/SKILL.md` | the loop, the hard rules, the capability map |
| `references/script-and-storyboard.md` | step 0: who the character is, the script, the two-column storyboard |
| `references/reference-frame.md` | what to look for in a real reference frame, and why (the uncanny-valley mechanics) |
| `references/prompt-craft.md` | the three-part prompt, duration slots, intonation, scene changes, when to bin the reference |
| `references/lore.md` | how to write a character people come back for |
| `references/flow-mechanics.md` | Flow's UI, models, credits and failure modes as of Sep 2026 |
| `references/warm-up.md` | days 0-30 of a new character account, labels, what to measure |
| `references/case-studies.md` | Yang Mun, Patryczek, Cringe Boy, Mbok Geni, with numbers |
| `scripts/score-frames.py` | score and rank candidate reference frames, write a contact sheet |
| `scripts/script-plan.py` | script → timed shots, padding, stress words, storyboard, episode JSON, ffmpeg trims |
| `scripts/qc.py` | jump cuts, frozen tails, black frames, silent audio, short clips |
| `scripts/flow.mjs` | Playwright driver for Flow: project, image, video, batch, download |
| `scripts/assemble.sh` | normalise + concat + case label + PART label + outro card |
| `scripts/split-sheet.py` | cut a 4-panel sheet into front / three-quarter / back / face |
| `templates/bulk-casting-chatgpt.md` | cast 30 varied characters from one reference in a single ChatGPT session, then bin the ones that fail the scorer |
| `templates/bible.md`, `templates/script.md`, `templates/scene.txt`, `templates/rules.txt`, `templates/episode.json`, `templates/prompts.md` | fill-in files |
| `example/ayu-day01.json` | a real DAY 1 plan: one scene, one rules block, three lines |

## Three opinions this repo will not compromise on

**Disclose, always.** "AI" in the bio and the platform label on every post. The character carries the
product as a prop or a running joke; the character never vouches for it. No "same person btw".

**Real frame before any prompt.** Generated portraits animate as wax; a phone frame carries the grain,
pores and micro-expression the video model needs. Half the work is choosing that frame.

**Behaviour over face.** A locked face gets you recognised. A logo prop, four speech tics and a taboo get
you followed. Write the bible before episode one.

**Numbered parts.** The follower curve belongs to the accounts that end every episode with a number and an
outro card. A one-off clip cannot ask anyone to come back.

**Measure what can be measured.** "Check the highlights aren't blown" is advice. A number that says
2.8% of the skin is clipped is a decision. Everything in this repo that could be turned into a number
has been, and everything that could not is clearly marked as your call.

---

The reference-frame-first method (real frame, genetically different avatar, locked three-part prompt,
50/25/25) comes from [Kristian Jennings' AI UGC walkthrough](https://youtu.be/kvf2lRSGixg), which
credits Ad Creators Lab for the reference-image idea. What this repo adds is running it as a series
rather than as one ad, Google Flow in place of a pay-as-you-go API, and the measurements.

Built by [@hanifproduktif](https://x.com/hanifproduktif). The Flow driver types into the real UI; when
Google changes the UI it will tell you which button it could not find, and `references/flow-mechanics.md`
is where you fix it.
