"""Layout engine for Apple-style kinetic type in Tesseract.

A card is a small stack of lines. Every word is its own Text layer, placed by
measuring the real font with PIL, so one line can mix weights and italics and
words can arrive one at a time without the rest of the line shifting.

Word markup (inside a line's "words"):
    word      default face for the line (small -> Medium, big -> ExtraBold)
    *word*    bold            (small lines)
    _word_    italic          (small -> Italic, big -> ExtraBold Italic)
    *_word_*  bold italic     (small lines)
    !word     accent colour   (combine freely: !_word_)

Use as a library from your own build script, or through kt.py.
"""
import os
from PIL import ImageFont

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "Inter")
FONT_DIR = os.path.normpath(FONT_DIR)

# role -> (file, (fontFamily, fontStyle) that Tesseract's strict resolver accepts)
# Found by fontprobe.py. For Inter the PostScript name + weight works; do not
# assume that generalises to other families (it does not for Montserrat).
FACES = {
    "reg":  ("Inter_28pt-Regular.ttf",         ("Inter28pt-Regular", "Regular")),
    "med":  ("Inter_28pt-Medium.ttf",          ("Inter28pt-Medium", "Medium")),
    "ital": ("Inter_28pt-Italic.ttf",          ("Inter28pt-Italic", "Italic")),
    "bold": ("Inter_28pt-Bold.ttf",            ("Inter28pt-Bold", "Bold")),
    "bi":   ("Inter_28pt-BoldItalic.ttf",      ("Inter28pt-BoldItalic", "BoldItalic")),
    "xb":   ("Inter_28pt-ExtraBold.ttf",       ("Inter28pt-ExtraBold", "ExtraBold")),
    "xbi":  ("Inter_28pt-ExtraBoldItalic.ttf", ("Inter28pt-ExtraBoldItalic", "ExtraBoldItalic")),
}
BIG = 80                     # a line at or above this size is a "big" line
MAX_W = 1000                 # widest a line may be on a 1080 canvas
WHITE = (1, 1, 1, 1)
ORANGE = (1.0, 0.624, 0.039, 1.0)   # systemOrange
SHADOW = (0, 0, 0, 0.55)

_cache = {}


def font_files():
    return [os.path.join(FONT_DIR, f) for f, _ in FACES.values()]


def width(face, size, s):
    key = (face, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, FACES[face][0]), size)
    return _cache[key].getlength(s)


def parse(token, size):
    """'!_word_' -> ('word', face, is_accent)"""
    acc = token.startswith("!")
    t = token[1:] if acc else token
    bold = ital = False
    if t.startswith("*") and t.endswith("*") and len(t) > 2:
        bold, t = True, t[1:-1]
    if t.startswith("_") and t.endswith("_") and len(t) > 2:
        ital, t = True, t[1:-1]
    if size >= BIG:
        face = "xbi" if ital else "xb"
    else:
        face = {(False, False): "med", (True, False): "bold",
                (False, True): "ital", (True, True): "bi"}[(bold, ital)]
    return t, face, acc


def split_times(t0, t1, words):
    """Spread word arrival across a spoken phrase, weighted by length."""
    wts = [len(w) + 2 for w in words]
    out, t = [], t0
    for w in wts:
        out.append(t)
        t += (t1 - t0) * w / sum(wts)
    return out


def card(next_id, t_in, t_out, lines, cx=540, y=40, color=WHITE, accent=ORANGE,
         shadow=SHADOW, name_prefix="kt:", align="center", x_left=None):
    """Build one card.

    lines: [{"size": 46, "t0": s, "t1": s, "words": ["this", "*lady*", ...]}, ...]
    Times are EDIT seconds. t0/t1 is the stretch of speech the line's words
    arrive across. Returns (layers, keys, next_id, warnings) where keys is
    [(layer_id, is_big)] for the motion pass.
    """
    layers, keys, warns = [], [], []
    yy = y
    for ln in lines:
        size = ln["size"]
        toks = [parse(t, size) for t in ln["words"]]
        ws = [width(f, size, w) for w, f, _ in toks]
        space = width(toks[0][1], size, " ")
        total = sum(ws) + space * (len(toks) - 1)
        if total > MAX_W:                       # shrink rather than overflow the frame
            k = MAX_W / total
            size = int(size * k)
            ws = [width(f, size, w) for w, f, _ in toks]
            space = width(toks[0][1], size, " ")
            total = sum(ws) + space * (len(toks) - 1)
            warns.append("line %r shrunk to %dpx to fit" % (" ".join(ln["words"]), size))
        x = (cx - total / 2) if align == "center" else x_left
        arrivals = split_times(ln.get("t0", t_in), ln.get("t1", t_in), [w for w, _, _ in toks])
        big = size >= BIG
        for (w, face, acc), wd, ta in zip(toks, ws, arrivals):
            ta = max(ta, t_in)
            fam = FACES[face][1]
            i = next_id; next_id += 1
            # anchor on the word's own centre so the scale-in grows in place
            ax, ay = x + wd / 2, yy + size * 0.55
            layers.append({
                "type": "Text", "id": i, "name": "%s%s" % (name_prefix, w), "blendMode": "normal",
                "activeRange": {"start": int(round(ta * 1000)), "duration": int(round((t_out - ta) * 1000))},
                "transform": {"anchorPoint": [ax, ay], "position": [ax, ay], "scale": [100, 100],
                              "rotation": 0, "opacity": 100},
                "sourceText": {"text": w, "fontFamily": fam[0], "fontStyle": fam[1], "fontSize": size,
                               "fillColor": list(accent if acc else color), "strokeWidth": 0.0,
                               "justification": "left", "boxText": True, "boxPosition": [x, yy],
                               "boxSize": [wd + 60, size * 1.5], "verticalAlign": "top",
                               "tracking": -0.5 if big else 0.0},
                "dropShadow": {"color": list(shadow), "blurRadius": 22.0 if big else 14.0,
                               "spreadRadius": 0.0, "blendMode": "normal", "offset": [0.0, 3.0]}})
            keys.append((i, big))
            x += wd + space
        yy += size * (1.08 if big else 1.25) + (8 if big else 0)
    return layers, keys, next_id, warns


def motion_actions(keys, tag="kt", composition="main"):
    """Small words fade in; big words fade and land with a scale-in."""
    EASE = {"type": "cubicBezier", "x1": 0.2, "y1": 0.0, "x2": 0.2, "y2": 1.0}
    LIN = {"type": "linear"}
    acts = []

    def k(lid, prop, pts):
        acts.append({"type": "setFxPropertyKeyframes", "compositionId": composition,
                     "property": {"layerId": lid, "propertyType": prop},
                     "keyframes": [{"id": "%s%d-%s-%d" % (tag, lid, prop, t), "layerTime": t,
                                    "value": {"type": "float", "value": float(v)}, "easing": e}
                                   for t, v, e in pts]})
    for lid, big in keys:
        k(lid, "opacity", [(0, 0, LIN), (120 if big else 90, 100, EASE)])
        if big:
            k(lid, "scaleX", [(0, 124, LIN), (280, 100, EASE)])
            k(lid, "scaleY", [(0, 124, LIN), (280, 100, EASE)])
    return acts


def build(spec, next_id):
    """A whole spec -> (layers, keys, warnings). See references/spec.md."""
    g = spec
    color = tuple(g.get("color", WHITE)); accent = tuple(g.get("accent", ORANGE))
    shadow = tuple(g.get("shadow", SHADOW))
    L, K, W = [], [], []
    for c in g["cards"]:
        off = c.get("offset", g.get("offset", 0.0))
        lines = [dict(l, t0=l.get("t0", c["t_in"]) + off, t1=l.get("t1", l.get("t0", c["t_in"])) + off)
                 for l in c["lines"]]
        ls, ks, next_id, ws = card(next_id, c["t_in"] + off, c["t_out"] + off, lines,
                                   cx=c.get("cx", g.get("cx", 540)), y=c.get("y", g.get("y", 40)),
                                   color=tuple(c.get("color", color)), accent=accent, shadow=shadow,
                                   align=c.get("align", "center"), x_left=c.get("x"))
        L += ls; K += ks; W += ws
    return L, K, W
