# Spec format

Illustrative — strip the `//` comments, JSON has none. A real file is `examples/promo-v4.json`.

```json
{
  "offset": 19.87,          // added to every time below: edit_start - source_in
  "cx": 540, "y": 40,       // defaults for every card
  "accent": [1, 0.624, 0.039, 1],
  "cards": [
    {"t_in": 1.07, "t_out": 3.61,                // the card is on screen for this span
     "lines": [
       {"size": 44,  "t0": 1.07, "t1": 1.90, "words": ["they", "are", "_posting_"]},
       {"size": 112, "t0": 1.90, "t1": 3.03, "words": ["!10", "times", "a", "day"]}
     ]}
  ]
}
```

- `t0`/`t1` on a line: the stretch of speech its words arrive across.
- Per card you may also set `offset`, `cx`, `y`, `color`, and `align: "left"` with `x`.
- A line of `size` >= 80 is a big line (ExtraBold, scale-in); below that it is small (Medium, fade).

## Word markup

| Token | Face |
|---|---|
| `word` | small: Medium · big: ExtraBold |
| `*word*` | small: Bold |
| `_word_` | small: Italic · big: ExtraBold Italic |
| `*_word_*` | small: Bold Italic |
| `!word` | accent colour; combines with the others (`!_word_`) |
