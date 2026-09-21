# AI Influencer Pro

**Run an AI character as a series, not a render.** Real reference frame → one-shot avatar → Flow
Character → locked three-part prompt → Google Flow (Nano Banana Pro + Omni) driven through a real browser →
ffmpeg assembly → account warm-up.

Every AI-influencer tutorial on your feed teaches the same thing: generate a convincing fake person saying
a script. This repo is the other half. It is what you need on day 2, when the clip worked and you have to
do it again tomorrow with the same face.

MIT licensed. Bring your own character, your own Google AI plan, your own taste.

## Install

```bash
claude plugin marketplace add buildwithhanif/ai-influencer-pro
claude plugin install ai-influencer-pro@ai-influencer-pro
```

Or point any coding agent at this repo and tell it to follow
`plugins/ai-influencer-pro/skills/ai-influencer-pro/SKILL.md`.

**Requirements:** a Google AI Pro or Ultra plan (Flow credits), Chrome, node 20+ with `playwright`
(`npm i playwright` in the scripts folder), `ffmpeg`/`ffprobe`, python 3.9+ with Pillow.

## The loop

```
bible ──▶ reference frame ──▶ one-shot avatar ──▶ Flow Character ──▶ locked prompt ──▶ flow.mjs batch ──▶ assemble.sh ──▶ post ──▶ measure
```

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
| `references/reference-frame.md` | what to look for in a real reference frame, and why (the uncanny-valley mechanics) |
| `references/lore.md` | how to write a character people come back for |
| `references/flow-mechanics.md` | Flow's UI, models, credits and failure modes as of Sep 2026 |
| `references/warm-up.md` | days 0-30 of a new character account, labels, what to measure |
| `references/case-studies.md` | Yang Mun, Patryczek, Cringe Boy, Mbok Geni, with numbers |
| `scripts/flow.mjs` | Playwright driver for Flow: project, image, video, batch, download |
| `scripts/assemble.sh` | normalise + concat + case label + PART label + outro card |
| `scripts/split-sheet.py` | cut a 4-panel sheet into front / three-quarter / back / face |
| `templates/bible.md`, `templates/episode.json`, `templates/prompts.md` | fill-in files |
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

---

Built by [@hanifproduktif](https://x.com/hanifproduktif). The Flow driver types into the real UI; when
Google changes the UI it will tell you which button it could not find, and `references/flow-mechanics.md`
is where you fix it.
