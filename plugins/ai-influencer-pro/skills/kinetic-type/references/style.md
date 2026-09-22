# The grammar

Taken from the reference Hanif supplied (an Indonesian CapCut/Apple-style edit, 23 Sep 2026)
and the values he then approved on the AI UGC promo.

## What the reference actually does

- **A stack, not a sentence.** A small context line, and under it a big line carrying the idea:
  *yang gayanya kaya* / **Apple Style**; *dan ini bisa kepakai* / **banget**.
- **Weight and slant change inside one line**: *gua **ngedit** video ini*, *jadi **cepet** banget*.
  That is the single most recognisable thing about it, and it is why every word is its own layer.
- **Words build in as they are spoken.** The small line types on; the big word lands with a quick
  blur-and-scale. The card then clears all at once when the next thought starts.
- **It lives in open space beside the speaker**, never along the bottom like a subtitle.
- **Clean grotesque type**, white, a soft dark shadow, one word coloured.

## The values

| | |
|---|---|
| Face | Inter, 28pt optical cut (closest OFL match to SF Pro; SF Pro is not licensed for published video) |
| Small line | 44-46 px, Medium. *Italic* for the verb or the doing-word; **Bold** for the one that matters |
| Big line | 104-124 px, ExtraBold. ExtraBold Italic for emphasis (*client's*, *even*, *this*) |
| Hero number | 200-230 px on its own line (**30**) |
| Accent | systemOrange `#FF9F0A`, one word per card, and not on every card |
| Shadow | black 55%, blur 14 (small) / 22 (big), 3 px down |
| Line gap | small line 1.25 em, big line 1.08 em + 8 px |
| Arrival | small words fade 0 to 100 in 90 ms; big words fade in 120 ms and scale 124% to 100% over 280 ms, ease `cubic-bezier(.2,0,.2,1)` |
| Exit | the whole card cuts out when the next card starts. No exit animation: the reference doesn't have one and it would steal time from the next line |

## Writing the cards

- **One card per spoken phrase.** A phrase is a breath: `kt.py plan` finds them in the waveform.
- **The big line is the payoff, usually the end of the phrase**: *this lady is not* / **real.**
- **Numbers go huge and orange**: **30** / *AI influencers* / *running every day.*
- **It may compress what was said** ("10 times" can become "10x") because it is a title, not a
  transcript. It must never say something he didn't.
- **Lowercase the small line**, keep the big line as spoken. Keep punctuation on the big line; it
  is part of the rhythm ("real." lands harder than "real").
- **Three lines at most.** More than that and it's a paragraph.
- **The last card can outlive the clip.** On the promo, **AI-generated.** stayed up through the
  cut to black and white and the freeze, and that replaced a separate caption card.
