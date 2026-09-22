"""Apple-style kinetic typography for Tesseract.

A card is a small stack of lines. Each word is its own Text layer, placed by
measuring the real font with PIL, so one line can mix weights and italics
("gua *ngedit* video ini") and words can arrive one at a time without the
rest of the line shifting under them. Big words land with a scale-in; small
words just appear. Everything on a card clears together when the next card
comes in, like the reference.
"""
from PIL import ImageFont

K = "/Users/hanifbot/Documents/_0WORK/AI VIDEO/HYPERFRAME/AI UGC PRODUCTION/_editing/fonts/Font/Sans-Serif/Inter/static/"
# role -> (ttf for measuring, (fontFamily, fontStyle) that the resolver accepts)
FACES = {
    "reg":  (K + "Inter_28pt-Regular.ttf",         ("Inter28pt-Regular", "Regular")),
    "med":  (K + "Inter_28pt-Medium.ttf",          ("Inter28pt-Medium", "Medium")),
    "ital": (K + "Inter_28pt-Italic.ttf",          ("Inter28pt-Italic", "Italic")),
    "bold": (K + "Inter_28pt-Bold.ttf",            ("Inter28pt-Bold", "Bold")),
    "xb":   (K + "Inter_28pt-ExtraBold.ttf",       ("Inter28pt-ExtraBold", "ExtraBold")),
    "xbi":  (K + "Inter_28pt-ExtraBoldItalic.ttf", ("Inter28pt-ExtraBoldItalic", "ExtraBoldItalic")),
    "bi":   (K + "Inter_28pt-BoldItalic.ttf",      ("Inter28pt-BoldItalic", "BoldItalic")),
}
_cache = {}


def width(face, size, s):
    key = (face, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FACES[face][0], size)
    return _cache[key].getlength(s)


def card(ids, t_in, t_out, lines, cx, y_top, color=(1, 1, 1, 1), accent=(1, .624, .039, 1),
         shadow=(0, 0, 0, .55), gap=0.18):
    """lines: [(size, [(word, face, t_appear, is_accent), ...]), ...]
    Times are EDIT seconds. Returns (layers, keyframe_specs)."""
    layers, keys = [], []
    y = y_top
    for size, words in lines:
        space = width(words[0][1], size, " ")
        ws = [width(f, size, w) for w, f, _, _ in words]
        total = sum(ws) + space * (len(words) - 1)
        x = cx - total / 2
        for (w, face, ta, acc), wd in zip(words, ws):
            i = ids[0]; ids[0] += 1
            big = size >= 80
            fam = FACES[face][1]
            box_w = wd + 60
            l = {"type": "Text", "id": i, "name": "k " + w, "blendMode": "normal",
                 "activeRange": {"start": int(ta * 1000), "duration": int((t_out - ta) * 1000)},
                 # anchor on the word's own centre so the scale-in grows in place
                 "transform": {"anchorPoint": [x + wd / 2, y + size * 0.55],
                               "position": [x + wd / 2, y + size * 0.55],
                               "scale": [100, 100], "rotation": 0, "opacity": 100},
                 "sourceText": {"text": w, "fontFamily": fam[0], "fontStyle": fam[1],
                                "fontSize": size, "fillColor": list(accent if acc else color),
                                "strokeWidth": 0.0, "justification": "left", "boxText": True,
                                "boxPosition": [x, y], "boxSize": [box_w, size * 1.5],
                                "verticalAlign": "top", "tracking": -0.5 if big else 0.0},
                 "dropShadow": {"color": list(shadow), "blurRadius": 22.0 if big else 14.0,
                                "spreadRadius": 0.0, "blendMode": "normal", "offset": [0.0, 3.0]}}
            layers.append(l)
            keys.append((i, big))
            x += wd + space
        y += size * (1.08 if size >= 80 else 1.25) + (8 if size >= 80 else 0)
    return layers, keys


def split_times(t0, t1, words):
    """Spread word arrival across a spoken phrase, weighted by length."""
    wts = [len(w) + 2 for w in words]
    out, t = [], t0
    for w in wts:
        out.append(t)
        t += (t1 - t0) * w / sum(wts)
    return out
