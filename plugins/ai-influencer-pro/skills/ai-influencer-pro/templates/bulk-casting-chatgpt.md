# Bulk casting: 30 UGC characters from one reference, in ChatGPT

Cast a whole roster in one sitting instead of one character at a time. One reference image carries
the camera grammar; a fixed matrix of 30 people stops the model regressing to the same attractive
25-year-old thirty times.

## Read this before you use it

The workflow says to avoid GPT-Image-class models for avatars, because they render everything too
clean and too perfect, and a too-clean still animates as wax. That advice stands. This file exists
because bulk casting in a single agentic session is worth the trade, and because the trade can be
managed two ways:

1. **The prompt below fights cleanliness directly** — it bans the things that make a render look
   generated and demands the things that make a photo look taken.
2. **You do not trust the output, you measure it.** Run every image through `score-frames.py` and
   bin whatever fails. That is the whole safety net, and it is not optional here.

Expect to keep roughly half. That is a good hit rate for free images, and it is still far faster
than casting thirty characters one at a time.

**What this is for:** the casting pass, so you can see thirty faces next to each other and pick the
five you want to build accounts around. The winners should be **rebuilt properly in Nano Banana Pro
from a real reference frame** before they become a series. Treat these as audition headshots, not as
the final avatar.

## The reference

Use a frame that already looks the way you want the outputs to look. Two good choices:

- **Your own existing avatar** (this repo ships `assets/` examples). You own it, so nothing stops you
  generating thirty derivatives, and it already demonstrates the target.
- **A real creator's phone frame.** More authentic grain, but you are handing a stranger's face to a
  third party to spin thirty derivative humans. Every output must be a genetically different person
  regardless, but the cleaner call is to use something you own.

Whichever you pick, score it first. If the reference does not pass, nothing downstream will.

---

## The kickoff prompt

Attach the reference image, paste everything between the lines.

---

I am casting characters for synthetic UGC video. Attached is a reference image of a character I
created and own; there is no real person in it. I need you to generate 30 completely different
people using it as a style and camera reference only, never as a face reference.

**Your job is to make photographs that look taken, not renders that look made.** Every instinct you
have toward making an image attractive is working against me here. Read the rules and follow them
literally.

### What stays identical in all 30

- Vertical 9:16, roughly 1024x1792.
- Shot on a phone **front camera**, held at arm's length, at eye level or a few degrees below.
- The subject is seated or standing at a surface, upper body in frame, **hands or forearms visible**.
- **One soft directional light source**, a window off to one side. Never a ring light, never studio
  light, never a rim light.
- A **real room with depth behind them** — furniture, a doorway, a lamp, a plant, a staircase.
  Never a blank wall, never a backdrop, never bokeh.
- **A visible reason the audio would be clean:** a clip-on lav, a handheld mic, a desk mic on a
  boom, wired earbuds, or the phone very close to the face. One of these, always.
- Natural light only, no flash, **unedited straight out of camera**.
- No text, no captions, no logos, no watermarks, no borders.

### What must be different in every one

Ethnicity, region, age, gender, face shape, body type, hair, room, clothing, the niche they create
in, the prop on the surface, the audio device, and the one odd detail. Use the matrix below and do
not improvise substitutions.

### Banned, because these are what make an image read as generated

Shallow depth of field or background blur. Cinematic colour grading. Vignettes. HDR glow. Rim
lighting or hair light. Symmetrical faces. Flawless skin. Whitened or perfectly aligned teeth.
Glossy catchlights in the eyes. Sculpted jawlines and cheekbones. Fashion-model proportions.
Studio-quality anything. Both hands placed symmetrically. A tidy, staged, styled background. Heavy
or obviously "done" makeup. Anyone who looks like a professional model or an influencer stock photo.

### Required, because these are what make an image read as real

- **Make them ordinary looking.** Aim for a 5 or 6 out of 10 in conventional attractiveness, not a 9.
  This single instruction matters more than every other line here. Real creators look like people you
  would stand behind in a queue.
- Visible skin texture: **pores, uneven tone, some redness around the nose and cheeks**, a blemish or
  two, fine lines appropriate to the stated age, stubble or shaving irritation where it fits.
- Slight **front-camera lens distortion**: the nose and the nearest hand read a little large, the
  edges of the frame stretch a touch.
- **Asymmetry everywhere**: one eye slightly smaller, a crooked smile, a tooth out of line, one
  shoulder lower, flyaway hair, a collar sitting wrong.
- **Mixed colour temperature**: cool daylight from the window against a warm bulb somewhere in the
  room.
- The window behind them may be **blown out**. Their **face must never be**. Highlights on the
  forehead, nose and cheeks must keep detail in them. This is the single most important technical
  constraint in the brief.
- Faint sensor noise in the shadows, and the slightly soft, slightly compressed look of a phone photo
  rather than a camera file.
- A mildly untidy room. A cable, a mug, a folded towel, something left where someone put it down.
- Expression: neutral, or caught mid-word with the mouth slightly open. Not smiling at the camera.
  Not posing.

### Hard limits

- Every person must be **a genuinely different human from the reference and from each other** —
  different eyes, nose, skin tone, face shape, bone structure. Not the same face with new hair.
- No one is to resemble any real, identifiable person.
- No character presents as a doctor, nurse, pharmacist, lawyer or financial adviser, and no clothing
  or props imply a medical or clinical setting.
- Everyone is clearly an adult.

### How to work

Generate **one image per message, in order, numbered**. After each one, state in a single line which
matrix row it was and what you did to keep it from looking generated. Do not batch several into one
image. Do not create a grid or a contact sheet. Do not ask me to confirm between images; work
through the list.

If an image comes out looking clean, glossy, symmetrical or model-like, say so yourself and
regenerate that number once before moving on.

### The matrix

| # | Person | Age | Niche | Room | Audio | The odd detail |
|---|---|---|---|---|---|---|
| 1 | Nigerian man | 34 | barbering | barbershop, chair behind him | handheld mic | clippers still plugged in on the counter |
| 2 | Japanese woman | 27 | stationery and desk setup | tiny apartment desk, shelf above | clip-on lav | a pen held in her teeth in the previous shot, now in her hand |
| 3 | White American man | 61 | hand tools and DIY | garage workbench, pegboard | clip-on lav | reading glasses pushed up on his forehead |
| 4 | Indian woman | 22 | budget skincare | bedroom, wardrobe door ajar | phone very close, no mic | hair wrapped in a towel |
| 5 | Brazilian man | 29 | five-a-side football | kitchen, fridge behind | wired earbuds | one shin pad still on |
| 6 | Korean woman | 45 | home cooking | kitchen counter, hob in shot | desk mic on a boom arm | flour on one forearm |
| 7 | Mexican man | 41 | car detailing | open garage, car door edge visible | handheld mic | a microfibre cloth over his shoulder |
| 8 | Ethiopian woman | 31 | coffee | low table, jebena and cups | clip-on lav | she is holding the wrong cup |
| 9 | Polish man | 24 | PC building | desk, open case beside him | headset mic | a screw between his lips |
| 10 | Filipina woman | 38 | meal prep for shift workers | living room, containers on the table | clip-on lav | still in work shoes |
| 11 | Turkish man | 52 | rugs and textiles | shop, rolled rugs stacked behind | handheld mic | a tape measure round his neck |
| 12 | Vietnamese woman | 19 | thrifted fashion | bedroom, clothes rail behind | one earbud in | price tag still attached to her sleeve |
| 13 | Egyptian man | 36 | motorbike maintenance | courtyard, bike half in frame | clip-on lav | grease on two knuckles |
| 14 | Swedish woman | 58 | gardening | kitchen with seed trays | clip-on lav | soil under her fingernails |
| 15 | Black British man | 27 | music production | bedroom studio, MIDI keyboard | condenser mic on a stand | one headphone cup pushed off his ear |
| 16 | Pakistani woman | 33 | household budgeting | dining table, notebook open | phone very close | she is writing with the pen still capped |
| 17 | Indonesian man | 45 | fishing | porch, rods against the rail | handheld mic | a hook in his hat brim |
| 18 | Colombian woman | 24 | dance fitness | living room, mirror at the edge | one earbud in | one sock on, one off |
| 19 | Chinese man | 68 | tea | tea table, gaiwan and tray | desk mic on a boom arm | glasses on a cord |
| 20 | Moroccan woman | 29 | henna and craft | table covered in materials | clip-on lav | henna dried on her own palm |
| 21 | German man | 39 | commuter cycling | hallway, bike hanging behind | clip-on lav | a trouser clip still on one ankle |
| 22 | Kenyan woman | 26 | braiding | salon chair, mirror behind | handheld mic | three combs in her hair |
| 23 | Thai man | 31 | street food | food cart, wok in frame | wired earbuds | a towel knotted at his waist |
| 24 | Russian woman | 49 | knitting | armchair, yarn basket at her feet | clip-on lav | a needle held in her mouth |
| 25 | Iranian man | 22 | chess | desk, board mid-game | phone very close | he is holding a captured piece |
| 26 | Australian woman | 36 | dog training | back step, lead in her lap | clip-on lav | dog hair all over one trouser leg |
| 27 | Puerto Rican man | 55 | guitar | living room, guitar across his knee | condenser mic on a stand | a plectrum tucked behind his ear |
| 28 | Nepali woman | 41 | trekking gear | porch, packs stacked behind | handheld mic | a carabiner clipped to her belt loop |
| 29 | French man | 30 | bread | kitchen, dough on the counter | clip-on lav | flour handprint on his apron |
| 30 | Māori New Zealander woman | 23 | tattoo art | studio, sketchbook open | one earbud in | ink on the side of her hand |

Start with number 1.

---

## Running it without the session falling apart

- **Six per message maximum**, and a fresh chat every ten with the reference re-attached. Long image
  sessions drift: the model starts averaging toward whatever it made most recently, and by image
  twenty everyone has the same jaw.
- **Do not let it "improve" anything.** The moment it offers a cleaner version, you have lost the
  texture. One shot per character, regenerate rather than edit.
- If it softens or refuses on "genetically different person", say plainly that the reference is your
  own synthetic character and no real person is depicted. That is true, which is why you should use a
  reference you own.
- Download at the largest size offered. You are going to measure these.

## The QC pass, which is the actual point

```bash
python3 scripts/score-frames.py cast/ --sheet cast-contact.jpg --json cast.json
```

Read the contact sheet, then apply three filters in this order:

1. **`skin_clip` over 1.0% — delete it.** Blown highlights on the face are dead pixels, and Omni will
   animate them as wax. No prompt fixes this after the fact.
2. **`skin_detail` under 4.0 or `skin_grain` under 2.2 — delete it.** That is the too-clean failure
   this whole file is trying to avoid. It will look fine as a still and turn plastic the moment it
   moves, which is the trap.
3. **Look at what survives and delete anything that looks like a model.** The scorer has no opinion
   about attractiveness, and a beautiful symmetrical face with perfect texture will pass every number
   and still read as synthetic to a viewer. This filter is yours and it is the one that matters most.

What comes out the other side is your shortlist. Take the best few, find each one a **real reference
frame in their own niche**, and rebuild them properly through step 1 and step 2 of the main loop
before they carry an account.
