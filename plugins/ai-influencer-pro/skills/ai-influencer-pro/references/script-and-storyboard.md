# Step 0: the script, the storyboard, and who the character is

The step before the reference frame. Skipping it is why most AI character accounts have beautiful
avatars and no audience.

## Format cannot save a bad script

The most realistic synthetic person in the world still loses with a weak message. If the account is
not working, the script is the first thing to change and the avatar is the last. People who are new
to this get it backwards and spend a week on the face.

Two consequences worth holding on to:

- A character that is working is a **script engine**, not a face. The face is how people find it
  again. The lines are why they stay.
- Before you touch the models, you should be able to say the promise of the video out loud in one
  sentence. If you cannot, generating it will not help.

## Choose the character with intent

Every decision should have a reason behind it. Not a clever reason, just a reason.

- **Match the character to the thing they will eventually sell.** A burly man on a Harley does not
  sell a feminine health product. This is obvious right up until you pick a face because it looked
  good.
- **They should have SOLVED the problem, not be living inside it.** Someone who fixed the thing has
  built-in authority. Someone still struggling with it is relatable and sells nothing. This single
  choice changes the whole register of the writing.
- **Borrowed authority beats claimed authority.** A character who *is* a homicide detective is a
  claim you cannot support and an impersonation risk. A character whose *dad* was one carries the
  same weight with none of that. Put the expertise one relationship away from the character.
- **Never a real person, never a medical professional.** Not a lookalike, not "inspired by". The
  avatar has to be a genuinely different human, and it must not present itself as licensed.

## Storyboard before you open anything

Private notes. They do not need to be pretty. What they need to do is settle the message before you
spend credits on it.

1. **Write the rules for this video first.** Iterating on something that already worked? Take its
   pace, its structure, whether it is calm or fast, and write those down as constraints. New idea?
   Find two references of what you want it to feel like.
2. **Keep it simple.** Hyper-cut, brain-rot editing can work, but it is not what wins by default.
   Deliver the message clearly and the format stops mattering.
3. **Two columns.** What is said on the left, what is on screen on the right. Where the character's
   face is on screen, just write "AI UGC". That is the whole storyboard.
4. **All the hooks first, then the body.** Hooks are a separate writing job from the body; writing
   them in a block stops the body's rhythm leaking into them.

`scripts/script-plan.py` produces the two-column table for you from a plain script file, along with
every line's duration, so the storyboard is a by-product of the timing pass rather than a chore.

## The script file format

```markdown
# TIP 01 do not drive home

## hook
My dad worked homicide for twenty-six years.
First thing he taught me: if someone follows you, do NOT drive *home*.

## body
Drive to a gas station instead.
Lights, cameras, people, and someone behind a counter.

## scene: same kitchen, later that night
The second one is your car door.
```

- One line per shot. **Never two lines in one shot** — both models mumble the moment two sentences
  share a clip.
- `## scene:` starts a scene change: the same character in a new position or setting. One per video
  is normal and it is the cheapest way to stop a talking head feeling static.
- `*stars*` force which word the delivery leans on. Without them the planner picks the longest
  content word in the back half of the line, which is right most of the time and wrong often enough
  that you should read what it chose.

```bash
python3 scripts/script-plan.py tip01.md \
  --storyboard tip01-storyboard.md \
  --episode episodes/tip01.json \
  --trims episodes/tip01-trim.sh \
  --character "Maddie Cole" --project https://flow.google.com/project/xxxx \
  --scene scene.txt --rules rules.txt
```

`--scene` and `--rules` are files holding part 1 and part 3 of the locked prompt. Once the prompt is
locked they never change again, which is the point: the planner drops them into every shot
unchanged, and only the line moves.

## Where the video topic comes from

Not from a blank page. A character that posts every day needs a supply, and the supply should be
things that already proved people want them:

- A carousel or a post of yours that already performed. Same tip, new format.
- The niche's own comment sections. The question people keep asking is the next fourteen videos.
- What the reference creator you sourced from is posting about. They are in the feed you want to be
  in.

One tip per video. A video with three tips in it gets saved by nobody, because there is nothing to
come back for.
