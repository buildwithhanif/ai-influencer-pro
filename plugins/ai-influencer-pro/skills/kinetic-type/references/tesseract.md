# Tesseract traps that bite kinetic type

Full list and the editing library: the `tesseract-edit` skill (`references/traps.md`). The ones that matter here:

- **Font addressing is per face.** Inter works as PostScript name + weight (`Inter28pt-ExtraBold`
  / `ExtraBold`), which `kinetic.FACES` already holds. That rule does NOT hold for every family
  (Montserrat Bold wants `Montserrat` / `Bold`). For any new face run `scripts/fontprobe.py` and use
  what renders. A `missing_fonts` error is JSON on stdout, not a crash: check for the PNG.
- **anchorPoint is layer-local.** For a text layer that means canvas coordinates, since the box is
  placed by `boxPosition`. Each word anchors on its own centre so the scale-in grows in place.
- **`commit` replaces the document.** `kt.py build` checks out, appends, commits, then applies its
  keyframes; `checkout` keeps every existing keyframe, so the rest of the edit survives. But if
  another script rebuilds the doc from scratch and commits, the kinetic layers are gone: use the
  library from inside that script instead.
- **Filmstrip thumbnails lie about big words.** A tile can catch a word at 124% mid-landing, which
  looks like it is on the hairline. Judge placement from `kt.py check`, which renders each card's
  settled frame at full resolution.
- **Export resolution follows the sources**, not the canvas. With a 720-wide clip in the timeline
  the master encodes at 720 and every word is downscaled with it. Pre-scale sources to 1080x1920.
