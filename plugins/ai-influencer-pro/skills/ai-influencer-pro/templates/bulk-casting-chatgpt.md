# Bulk casting v2: 30 ordinary people, from 10 real UGC screenshots

Cast a roster of faces in one ChatGPT session. Ten screenshots of real creators carry the look; a
fixed list of 30 people carries the variety. Nothing else is specified, on purpose.

## What v1 got wrong

v1 gave each character a profession and a niche — a barber, a knitter, a bread baker — and dressed
their room to match: clippers on the counter, a yarn basket, flour on the apron. Every image came
back try-hard. Staged. Obviously art-directed by someone who wanted it to look like UGC.

Real UGC has no art direction. It is a person sitting in their own bedroom with the bed unmade
behind them, talking at a phone propped against a book. There is no prop. There is no theme. The
room is just where they live.

**So v2 varies three things and nothing else: ethnicity, age, gender.** Everything else — the room,
the clothes, the pose — is ordinary by instruction, not by design.

## The reference set

Twenty screenshots pulled from real TikTok videos found by searching "ugc", "ugc creator" and "ugc
example" across US, GB, ID, PH and CA. This is the same sourcing step as the main workflow: real
creator, real phone, real room.

The set is deliberately mixed — 14 women, 6 men, several ethnicities, and twenty different ordinary
rooms: a living-room couch, an unmade bed, rooms with framed prints, home desks, a bedroom with an
LED strip, dining tables, a kitchen island, a hallway, a back patio.

**Attach ten at a time**, not all twenty — more than about ten and the model starts averaging them
instead of reading them. Use ref-01 to ref-10 for the first half of the cast and ref-11 to ref-20 for
the second half; it also stops the whole batch inheriting one room.

One thing the set does not give you: **nobody over about forty.** Across 105 candidates, the people
making content about being a UGC creator were almost all women in their twenties and thirties. Watch
the older rows of the cast list harder than the rest, because that is where the model has the least
to copy and the most room to invent a stock photo. They are not face references. They are the answer to "what does a
real one of these actually look like", which is a question ChatGPT gets wrong by default.

Scores ran from 52 to 100 on the frame scorer, and that is fine — these are the look reference, not
the avatar. The one thing to know: several have burned-in captions across the chest or face, so the
prompt tells ChatGPT to ignore text in the references and never reproduce it.

---

## The kickoff prompt

Attach all ten reference screenshots. Paste everything between the lines.

---

I am casting faces for synthetic UGC video. The ten attached images are screenshots from real TikTok
videos by real creators. I need 30 new people who look like they belong in that set.

**Read the ten images as one thing: a quality bar and a composition bar.** Notice what they have in
common. Someone sitting in an ordinary room in their own home. A phone propped up or held at arm's
length. Nothing tidied, nothing arranged, nothing lit. Half of them are caught mid-sentence with a
hand half-raised. Most are a bit off-centre. The rooms are just rooms: a couch, an unmade bed, a
kitchen counter, a desk with a laptop on it, a wall with two pictures.

**These are not face references.** Every person you make must be a new human who appears in none of
them.

### The only things that vary between the 30

Ethnicity, age, and gender. That is the entire brief. Work through the list at the bottom in order.

### What every single one of them has

- Vertical 9:16, roughly 1024x1792.
- Phone front camera, arm's length, eye level or slightly below, held or propped.
- Upper body. Hands visible about half the time, doing nothing in particular.
- An **ordinary room in an ordinary home**. A bedroom, a living room, a kitchen, a spare room, a desk
  in the corner of one of those. Whatever is already in that room is what is in the shot.
- **Daylight from a window**, or a normal ceiling light, or both. Nothing else.
- Everyday clothes. A t-shirt, a hoodie, a jumper. What someone wears in their own house.
- No text, no captions, no logos, no watermarks. **Some of the reference screenshots have captions
  burned into them — ignore those completely and never reproduce text.**

### What NOT to add, and this is where it usually goes wrong

- **No profession, no hobby, no niche.** They are not a chef, a gamer, a musician, a gym person or a
  skincare person. They are a person. Do not give them an occupation and do not dress the room to
  suggest one.
- **No themed props.** No instrument, no tools, no product held up, no equipment. If something is on
  the table it is a mug or a phone or nothing.
- **No microphone**, no boom arm, no podcast setup, no ring light, no tripod in shot. Look at the
  references: almost none of them have a mic. Real people just use the phone.
- **Do not decorate.** No plant placed for composition, no fairy lights, no neat shelf of matching
  books, no "aesthetic" corner. Rooms can be plain, and slightly messy is better than styled.
- No studio anything. No backdrop.

### Making it look photographed instead of rendered

This is the part that decides whether the image is usable, so treat every line as a requirement.

- **Make them ordinary looking.** Around a 5 or 6 out of 10, not a 9. This matters more than every
  other instruction here. Look at the ten references: they are normal-looking people. Not one of
  them looks like a model, and if yours do, you have failed the brief.
- Visible skin texture. Pores, uneven tone, redness around the nose or on the cheeks, a blemish, fine
  lines that match the stated age, stubble or shaving rash where it fits.
- **Asymmetry.** One eye slightly smaller, a crooked mouth, a tooth out of line, one shoulder lower,
  hair not sitting right, a collar folded under.
- Slight front-camera lens distortion: the nose and the nearest hand read a little large.
- Mixed colour temperature. Cool window light against a warm bulb.
- A window behind them may be blown out. **Their face must never be.** Highlights on the forehead,
  nose and cheeks keep detail in them. This is the one hard technical rule.
- Faint noise in the shadows, and the slightly soft, slightly compressed look of a phone video
  screenshot rather than a photograph.
- Expression: mid-sentence, mouth part open, or neutral. **Not smiling at the camera. Not posing.**

### Banned, because these are what make an image read as AI

Background blur or bokeh. Cinematic colour grading. Vignette. HDR glow. Rim light or hair light.
Symmetrical faces. Flawless skin. Perfect white teeth. Glossy catchlights. Sculpted jawlines.
Model proportions. Studio lighting. Both hands placed symmetrically. A tidy, styled, staged room.
Heavy makeup. Anyone who looks like an influencer stock photo.

### Limits

- Every person is a different human from each other and from everyone in the references.
- No one resembles any real, identifiable person.
- Everyone is clearly an adult.

### How to work

**One image per message, in order, numbered.** After each, one line: which row it was, and one thing
you did to keep it from looking staged. No grids, no contact sheets, no batching. Do not stop to ask
me between images.

If one comes back glossy, symmetrical, model-like, or if the room looks decorated, say so yourself
and regenerate that number once before moving on.

### The 30

Room is a suggestion, not a theme. Anything ordinary is fine.

| # | Gender | Ethnicity / region | Age | Room |
|---|---|---|---|---|
| 1 | woman | White American | 24 | bedroom |
| 2 | man | Black American | 31 | living room |
| 3 | woman | Filipina | 42 | kitchen |
| 4 | man | White British | 19 | bedroom |
| 5 | woman | Indian | 27 | living room |
| 6 | man | Korean | 55 | kitchen |
| 7 | woman | Nigerian | 35 | bedroom |
| 8 | man | Mexican | 23 | spare room |
| 9 | woman | White Australian | 61 | living room |
| 10 | man | Pakistani | 38 | dining table |
| 11 | woman | Japanese | 21 | bedroom |
| 12 | man | Black British | 47 | living room |
| 13 | woman | Brazilian | 29 | kitchen |
| 14 | man | Vietnamese | 26 | bedroom |
| 15 | woman | Turkish | 33 | living room |
| 16 | man | White American | 68 | living room |
| 17 | woman | Chinese | 45 | dining table |
| 18 | man | Ethiopian | 22 | bedroom |
| 19 | woman | Mexican American | 18 | bedroom |
| 20 | man | White Polish | 34 | desk in a bedroom |
| 21 | woman | Thai | 52 | kitchen |
| 22 | man | Indian | 29 | living room |
| 23 | woman | Black American | 20 | bedroom |
| 24 | man | Egyptian | 41 | living room |
| 25 | woman | White Irish | 37 | kitchen |
| 26 | man | Japanese | 64 | dining table |
| 27 | woman | Indonesian | 25 | bedroom |
| 28 | man | White American | 28 | spare room |
| 29 | woman | Moroccan | 58 | living room |
| 30 | man | Colombian | 36 | kitchen |

Start with number 1.

---

## Running it

- **Six per message maximum**, fresh chat every ten with all ten references re-attached. Long image
  sessions average toward whatever they made last, and by twenty everyone has the same jaw.
- **Never let it offer a cleaner version.** One shot per person, regenerate rather than edit.
- If it drifts back to staging rooms — and it will — paste this: *"Too decorated. Look at reference
  4 again. The room is just a room. Remove the props and regenerate."*
- Download at the largest size offered.

## The QC pass

```bash
python3 scripts/score-frames.py cast/ --sheet cast-contact.jpg --json cast.json
```

Three filters, in order:

1. **`skin_clip` over 1.0% — delete.** Blown highlights on a face are dead pixels and Omni animates
   them as wax. Nothing fixes it afterwards.
2. **`skin_detail` under 4.0 or `skin_grain` under 2.2 — delete.** The too-clean failure. It looks
   fine as a still and turns plastic the moment it moves.
3. **Then look, and delete anything that reads as staged or as a model.** The scorer has no opinion
   about either. A beautiful symmetrical face in a styled room will pass every number and still be
   useless. This filter is yours and it is the one that decides the batch.

Expect to keep about half.

## What these are for

A casting pass. Thirty faces side by side so you can pick the few worth building on. They are not
avatars yet — ChatGPT renders too clean for a face that has to be animated, which is exactly why
step 2 of the main loop uses Nano Banana Pro from a real reference frame.

When you pick a winner, go and find **that person's own reference frame** — a real creator with the
same rough age and look, in a real room — and rebuild them through step 1 and step 2 properly. The
casting image is the sketch. The rebuilt avatar is the thing that carries an account.
