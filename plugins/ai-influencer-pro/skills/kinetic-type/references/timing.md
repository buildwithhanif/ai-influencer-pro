# Timing

**Words from whisper, time from the waveform.**

`npx hyperframes transcribe clip.mp4 --language en --json` runs whisper locally (nothing is
uploaded) and returns words with times. On generated clips those times are not trustworthy: they
drift up to ~0.8 s early, and the first word is snapped to 0.0 even when speech starts at 1.07 s.
The words and their order are right; the punctuation is right.

The RMS envelope is the opposite: exact about when sound starts and stops, blind to what is said.
`silencedetect` is useless on these clips because they carry continuous room tone, so `kt.py`
reads RMS directly and gates 10 dB under the speaking level.

`kt.py plan` joins them: phrases from the envelope, words from whisper, dealt into phrases in order
with each boundary nudged to the nearest clause mark or pause. Then, inside a phrase, words arrive
spread by length across its duration, so a word never appears before it is said.

## Before building, check the take

A waveform shows that someone spoke; only the transcript shows **what**. On the promo a take said
*"I have 30 AI influencers"* twice. Reading the transcript found it, and a jump cut from the first
"30" to the second saved a regeneration. Read every take's transcript before cutting cards for it.

## After building, check the master

Transcribe the finished video too. It is the only check that proves no cut clipped a word
("23-tab prop", "Optimum Nutrition cream" were both caught this way) and that the cards are sitting
on the words they describe.
