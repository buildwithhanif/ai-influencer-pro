# Cut-out presenter (green screen)

Tesseract has no chroma key and `personMatte` returns an empty mask, so:

1. Generate the presenter on a green screen. Omni 1.1 prompt that keyed cleanly: "stands in front
   of a plain, evenly lit bright chroma key green screen. The background is pure flat green,
   completely empty, no props, no shadows falling on the green, clean separation". "Medium shot
   from the waist up… both of his hands are visible inside the frame" gets the hands in.
2. `bash key.sh raw.mp4 out` → `out-rgb.mp4` + `out-matte.mp4`, both 1080x1920.
3. `Edit.keyed(rgb, matte, at, dur, src_in, intrinsic, scale, pos)`.

## Why green DOMINANCE, not colour distance

`key.sh` keys where green is clearly the largest channel:
`if(gt(min(g-r, g-b), 25), 0, 255)`. Both obvious keys failed on this footage:
- `colorkey` punched holes in the shadow under the jaw and in clothing folds — a dark neutral pixel
  is closer to a mid green in RGB than a white one is.
- `chromakey` ate a cream sweatshirt, whose chroma is nearly neutral.

Then close specks (`dilation,dilation,erosion,erosion,erosion`); the extra erosion chokes a pixel
off the edge and takes the green fringe with it.

## Placement

Size from the source, not the canvas: the subject is ~40% of a green frame. Scale ~75 with the
head landing at y ~1420 (`pos=(250, 1840)` for a bottom-left corner cut-in) sits under the face of
whatever is behind. ~62 in mid-frame reads as a sticker and covers faces. On full-frame narrator
shots Hanif preferred his studio background kept ("background yg pas ini ga usah dihilangin karena
aneh"): key only when he is over someone else's footage.
