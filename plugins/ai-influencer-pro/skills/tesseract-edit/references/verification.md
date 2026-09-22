# Verification

A render exiting 0 proves nothing. On the promo each of these caught something the others missed.

| Check | Command | Caught |
|---|---|---|
| Full-res frames | `verify.py frames P t1 t2 …` | a cut-in rendered as a pill (cornerRadius), clips drifting off-centre (anchor), a payoff caption unreadable on a cream sweater, a chart rising under "buy once, cry once" |
| Transcript of each take | `npx hyperframes transcribe take.mp4` | a take that said its key line twice |
| Transcript of the master | `verify.py words master.mp4` | two cuts ending a word early ("23-tab prop", "Optimum Nutrition cream"), and proof a ducked voice was inaudible |
| SFX-only mix | `verify.py sfx P doc.json t1 t2 …` | whether the swipe sounds were actually in the mix |
| Master spec | `deliver.sh` asserts | a master encoded at 720 because one source wasn't pre-scaled; A/V drift |
| Caption bleed | frames sampled just after each cut | caption tails landing on the next person's face |

Sample frames just AFTER cuts, not in the middle of clips: that is where bleed, tails and
mistimed captions show.
