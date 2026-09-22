#!/usr/bin/env python3
"""v4 promo timeline as Tesseract editable document JSON.

  1. Robyn's hook, her own caption style
  2. Hanif cuts in over her, keyed. She drains to grey and goes quiet.
     His line is Apple-style kinetic type, not a subtitle.
  3. The run: six creators, each captioned in THEIR OWN style, because each is
     meant to read as a different account. Between them, a TikTok swipe-up.
  4. Hanif full frame in the studio, kinetic type in the navy above his head
  5. Product montage, swiping, each creator saying their brand in their style
  6. Hanif: none of them are real, even me -> colour drains on "AI-generated"
  7. Outro

Kinetic type is Hanif's alone: it is how HE talks on screen. The creators get
ordinary subtitles, just never the same preset twice.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import ImageFont
import kinetic

W, H = 1080, 1920
CX, CY = W / 2, H / 2
ORANGE = (1.0, 0.624, 0.039, 1.0)
WHITE, BLACK = (1, 1, 1, 1), (0, 0, 0, 1)
INK = (0.07, 0.07, 0.09, 1)

FK = "/Users/hanifbot/Documents/_0WORK/AI VIDEO/HYPERFRAME/AI UGC PRODUCTION/_editing/fonts/Font/"
# (fontFamily, fontStyle) that strict resolution actually accepts, found by
# fontprobe.py. It is not uniform: Montserrat Bold wants the family name,
# Montserrat ExtraBold wants the PostScript name. Do not "tidy" this table.
FONTS = {
    "ms-black":  ("Montserrat-Black", "Black",          "Sans-Serif/Montserrat/static/Montserrat-Black.ttf"),
    "ms-xbold":  ("Montserrat-ExtraBold", "ExtraBold",  "Sans-Serif/Montserrat/static/Montserrat-ExtraBold.ttf"),
    "ms-bold":   ("Montserrat", "Bold",                 "Sans-Serif/Montserrat/static/Montserrat-Bold.ttf"),
    "ms-semi":   ("Montserrat-SemiBold", "SemiBold",    "Sans-Serif/Montserrat/static/Montserrat-SemiBold.ttf"),
    "in-med":    ("Inter28pt-Medium", "Medium",         "Sans-Serif/Inter/static/Inter_28pt-Medium.ttf"),
    "in-semi":   ("Inter28pt-SemiBold", "SemiBold",     "Sans-Serif/Inter/static/Inter_28pt-SemiBold.ttf"),
    "in-bold":   ("Inter28pt-Bold", "Bold",             "Sans-Serif/Inter/static/Inter_28pt-Bold.ttf"),
    "lato-black":("Lato-Black", "Black",                "Sans-Serif/Lato/Lato-Black.ttf"),
    "pts-bi":    ("PTSerif-BoldItalic", "BoldItalic",   "Serif/PT_Serif/PTSerif-BoldItalic.ttf"),
    "pf-ital":   ("PlayfairDisplay-Italic", "Italic",   "Serif/Playfair_Display/static/PlayfairDisplay-Italic.ttf"),
}
_fc = {}
def measure(face, size, s):
    if (face, size) not in _fc:
        _fc[(face, size)] = ImageFont.truetype(FK + FONTS[face][2], size)
    return _fc[(face, size)].getlength(s)

FILL = 100.0
SRC_C = (540, 960)
ms = lambda s: int(round(s * 1000))
INTRINSIC = {"priya": 8000}
SW = 0.18                                   # swipe length

# ------------------------------------------------------------------ the beats
A_AT, A_CUT, A2_SRC, A_END_SRC = 1.55, 3.45, 6.33, 9.40
A_DUR = A_CUT + (A_END_SRC - A2_SRC)
RUN_AT = A_AT + A_DUR

# (who, source in, source out, scale, [(src start, src end, "chunk|chunk")])
RUN = [
    ("luca",    0.40, 2.55, 100, [(0.55, 2.39, "Everyone told me|to meal prep|on Sunday.")]),
    ("marilou", 0.00, 2.10, 115, [(0.11, 1.96, "Three years|of night shifts|taught me one thing.")]),
    ("andre",   5.15, 7.45, 100, [(5.31, 5.93, "You did|the right steps"),
                                  (6.59, 7.30, "in the wrong order.")]),
    ("priya",   0.50, 1.85, 115, [(0.64, 1.71, "Stop revising|at your desk.")]),
    ("hiroshi", 0.60, 3.25, 100, [(0.73, 2.24, "My father|made tea the same way"),
                                  (2.52, 3.11, "for 40 years.")]),
    ("meera",   2.75, 4.95, 115, [(2.90, 4.80, "You have a|23-tab problem.")]),
]
B_SRC = (0.95, 5.15)
PRODUCTS = [
    ("diego",   1.08, 2.40, [(1.22, 2.10, "Optimum Nutrition|creatine.")]),
    ("marcus",  0.40, 2.00, [(0.53, 1.88, "Natural Vitality|CALM.")]),
    ("marilou", 0.00, 1.55, [(0.09, 1.41, "Vital Proteins|collagen.")]),
    ("jhoanna", 0.00, 2.35, [(0.09, 2.24, "Nordic Naturals|Ultimate Omega.")]),
    ("callum",  0.30, 1.30, [(0.43, 1.15, "Liquid I.V.")]),
    ("ada",     0.00, 1.40, [(0.02, 1.26, "Ritual Essential.")]),
    ("soojin",  0.92, 2.10, [(1.05, 1.96, "The Anker Nano.")]),
    ("imran",   0.42, 2.35, [(0.55, 2.22, "Anker braided|USB-C.")]),
]
C_SRC, C_BW_SRC = (1.35, 7.45), 6.40
FREEZE_DUR, OUTRO_DUR = 1.8, 5.2

RUN_DUR = sum(o - i for _, i, o, _, _ in RUN)
B_AT = RUN_AT + RUN_DUR
PROD_AT = B_AT + (B_SRC[1] - B_SRC[0])
PROD_DUR = sum(o - i for _, i, o, _ in PRODUCTS)
C_AT = PROD_AT + PROD_DUR
C_BW_AT = C_AT + (C_BW_SRC - C_SRC[0])
FREEZE_AT = C_AT + (C_SRC[1] - C_SRC[0])
OUTRO_AT = FREEZE_AT + FREEZE_DUR
TOTAL = OUTRO_AT + OUTRO_DUR
OVL_SCALE, OVL_POS = 75, (250, 1840)

# ============================================== per-creator caption presets ==
# Each creator is a different account, so each gets a different, ORDINARY
# preset: the kinds real people actually pick in CapCut or TikTok. None of them
# is exotic on its own; the point is that no two are the same.
#   face, size, colour, case, stroke, box (rgba, padx, pady, roundness),
#   shadow (rgba, blur), y, align ("c" or left x), one-word-at-a-time
STYLES = {
    "robyn":   dict(face="ms-semi", size=56, color=WHITE, box=((0, 0, 0, .74), 26, 14, .35), y=1260),
    "luca":    dict(face="ms-black", size=112, color=WHITE, case="upper", stroke=11, word=True, y=1070),
    "marilou": dict(face="in-med", size=50, color=WHITE, case="lower", shadow=((0, 0, 0, .65), 16), align=96, y=1500),
    "andre":   dict(face="in-bold", size=54, color=INK, box=((1, 1, 1, 1), 24, 12, .30), y=1290),
    "priya":   dict(face="in-semi", size=52, color=WHITE, box=((.45, .33, .98, 1), 26, 13, .45), y=1330),
    "hiroshi": dict(face="pts-bi", size=66, color=WHITE, shadow=((0, 0, 0, .7), 18), y=1360),
    "meera":   dict(face="ms-xbold", size=76, color=(.72, 1, .2, 1), stroke=8, y=1160),
    "diego":   dict(face="ms-black", size=100, color=(1, .85, .08, 1), case="upper", stroke=11, word=True, y=1090),
    "marcus":  dict(face="ms-xbold", size=58, color=WHITE, case="upper", box=((.88, .1, .14, 1), 24, 14, .12), y=1300),
    # thin italic serif on a light grey sweater: needs a tighter, darker shadow
    "jhoanna": dict(face="pf-ital", size=84, color=WHITE, shadow=((0, 0, 0, .9), 10), y=1380),
    "callum":  dict(face="in-semi", size=58, color=WHITE, case="lower", stroke=5, y=1190),
    "ada":     dict(face="lato-black", size=60, color=INK, box=((1, .83, .1, 1), 24, 12, .25), y=1300),
    "soojin":  dict(face="in-bold", size=54, color=WHITE, shadow=((0, 0, 0, .7), 16), y=300),
    "imran":   dict(face="ms-bold", size=66, color=WHITE, shadow=((0, .9, 1, .95), 26), y=1210),
}

cap_id = [2000]


def tr(pos=(CX, CY), anchor=SRC_C, scale=FILL, opacity=100):
    return {"anchorPoint": list(anchor), "position": list(pos),
            "scale": [scale, scale], "rotation": 0, "opacity": opacity}


def bias_y(scale, bias=0.36):
    return CY + H * (scale / FILL - 1) * (0.5 - bias)


def cap_layers(style, text, t0, t1):
    s = STYLES[style]
    face, size = s["face"], s["size"]
    if s.get("case") == "upper": text = text.upper()
    if s.get("case") == "lower": text = text.lower()
    tw = measure(face, size, text)
    if tw > 940:                                   # never let a chunk wrap
        size = int(size * 940 / tw); tw = measure(face, size, text)
    align = s.get("align", "c")
    x0 = CX - tw / 2 if align == "c" else align
    i = cap_id[0]; cap_id[0] += 2
    st = {"text": text, "fontFamily": FONTS[face][0], "fontStyle": FONTS[face][1],
          "fontSize": size, "fillColor": list(s["color"]), "justification": "left",
          "boxText": True, "boxPosition": [x0, s["y"]], "boxSize": [tw + 80, size * 1.6],
          "verticalAlign": "top", "tracking": 0.0, "strokeWidth": float(s.get("stroke", 0))}
    if s.get("stroke"):
        st.update({"applyStroke": True, "strokeColor": list(BLACK), "strokeOverFill": False})
    t = {"type": "Text", "id": i, "name": "cap %s %s" % (style, text), "blendMode": "normal",
         "activeRange": {"start": ms(t0), "duration": ms(t1 - t0)},
         "transform": tr(pos=(CX, CY), anchor=(CX, CY)), "sourceText": st}
    if s.get("shadow"):
        c, b = s["shadow"]
        t["dropShadow"] = {"color": list(c), "blurRadius": float(b), "spreadRadius": 0.0,
                           "blendMode": "normal", "offset": [0.0, 2.0]}
    out = [t]
    if s.get("box"):
        c, px, py, rnd = s["box"]
        bw, bh = tw + 2 * px, size * 1.18 + 2 * py
        # the glyph box sits a little under the text box top; 0.62em centres it
        out.append({"type": "Rect", "id": i + 1, "name": "cap box " + style, "blendMode": "normal",
                    "activeRange": {"start": ms(t0), "duration": ms(t1 - t0)},
                    "transform": tr(pos=(x0 + tw / 2, s["y"] + size * 0.62), anchor=(0, 0)),
                    "rect": {"size": [bw, bh], "fillColor": list(c),
                             "position": [-bw / 2.0, -bh / 2.0], "roundness": rnd}})
    return out


def captions(style, phrases, offset, clip_start, clip_end):
    """phrases in SOURCE seconds; offset = edit time of source 0."""
    chunks = []
    for s, e, txt in phrases:
        parts = txt.split("|")
        if STYLES[style].get("word"):
            parts = [w for p in parts for w in p.split()]
        wts = [len(p) + 2 for p in parts]
        t = s
        for p, w in zip(parts, wts):
            d = (e - s) * w / sum(wts); chunks.append([t, t + d, p]); t += d
    out = []
    for n, (s, e, p) in enumerate(chunks):
        nxt = chunks[n + 1][0] if n + 1 < len(chunks) else None
        end = nxt if (nxt is not None and nxt - e < 0.5) else e + 0.25
        a = max(offset + s, clip_start + SW)        # never while the clip is still swiping in
        b = min(offset + end, clip_end)             # never onto the next person's face
        if b - a > 0.08:
            out += cap_layers(style, p, a, b)
    return out


def video(i, name, asset, at, dur, src_in, intrinsic, scale=FILL, vol=1.0,
          transform=None, matte=None, blur=False):
    l = {"type": "Video", "id": i, "name": name, "blendMode": "normal",
         "activeRange": {"start": ms(at), "duration": ms(dur)},
         "sourceRange": {"start": ms(src_in), "duration": ms(dur)},
         "sourceIntrinsicDuration": intrinsic, "volume": vol,
         "transform": transform or tr(pos=(CX, bias_y(scale)), scale=scale),
         "source": {"assetId": asset, "fit": "cover"}}
    if matte is not None: l["trackMatte"] = {"mode": "luma", "layer": matte}
    if blur: l["motionBlur"] = True
    return l


def keyed(pic, mat, name, asset, at, dur, src_in, intrinsic, vol=1.0):
    t = tr(pos=OVL_POS, scale=OVL_SCALE)
    return [video(mat, name + " matte", asset + "matte", at, dur, src_in, intrinsic,
                  vol=0.0, transform=dict(t), blur=True),
            video(pic, name, asset + "rgb", at, dur, src_in, intrinsic, vol=vol,
                  transform=dict(t), matte=mat, blur=True)]


def text(i, body, at, dur, size, y, color=WHITE, face="ms-bold"):
    return {"type": "Text", "id": i, "name": "outro " + body, "blendMode": "normal",
            "activeRange": {"start": ms(at), "duration": ms(dur)},
            "transform": tr(pos=(CX, CY), anchor=(CX, CY)),
            "sourceText": {"text": body, "fontFamily": FONTS[face][0], "fontStyle": FONTS[face][1],
                           "fontSize": size, "fillColor": list(color), "strokeWidth": 0.0,
                           "justification": "center", "boxText": True,
                           "boxPosition": [CX - 470, y], "boxSize": [940, size * 1.6],
                           "verticalAlign": "top"}}


def rect(i, name, at, dur, color):
    return {"type": "Rect", "id": i, "name": name, "blendMode": "normal",
            "activeRange": {"start": ms(at), "duration": ms(dur)},
            "transform": tr(pos=(CX, CY), anchor=(0, 0)),
            "rect": {"size": [W, H], "fillColor": list(color),
                     "position": [-W / 2.0, -H / 2.0], "roundness": 0.0}}


# ======================================================= Hanif's kinetic type ==
kid = [3000]
KIN_KEYS = []


def kcard(t_in, t_out, lines, cx, y):
    """lines: [(size, [(word, face, is_accent)]), ...] with arrival times filled
    in from the phrase each line belongs to: (size, words, phrase_t0, phrase_t1)."""
    built = []
    for size, words, p0, p1 in lines:
        ts = kinetic.split_times(p0, p1, [w for w, _, _ in words])
        built.append((size, [(w, f, max(t, t_in), a) for (w, f, a), t in zip(words, ts)]))
    L, keys = kinetic.card(kid, t_in, t_out, built, cx, y)
    KIN_KEYS.extend(keys)
    return L


def kin_hanif():
    L = []
    a = lambda t: A_AT + t                                   # A-edit -> edit time
    # over grey Robyn: on her black t-shirt, right of his cut-in
    L += kcard(a(0.47), a(2.24), [
        (46, [("this", "med", 0), ("lady", "med", 0), ("is", "med", 0), ("not", "med", 0)], a(0.47), a(1.30)),
        (124, [("real.", "xb", 1)], a(1.30), a(1.64))], 640, 1000)
    L += kcard(a(2.24), a(3.50), [
        (46, [("I", "med", 0), ("made", "bold", 0), ("her", "med", 0)], a(2.24), a(2.60)),
        (112, [("this", "xbi", 0), ("morning.", "xb", 0)], a(2.60), a(3.24))], 640, 1000)
    L += kcard(a(3.50), a(A_DUR), [
        (230, [("30", "xb", 1)], a(3.50), a(3.72)),
        (92, [("AI", "xb", 0), ("influencers", "xb", 0)], a(3.72), a(4.69)),
        (46, [("running", "med", 0), ("every", "bold", 0), ("day.", "bold", 0)], a(4.69), a(5.95))], 640, 900)
    # B: navy band above his head
    b = lambda s: B_AT + (s - B_SRC[0])
    L += kcard(b(1.07), b(3.61), [
        (44, [("they", "med", 0), ("are", "med", 0), ("posting", "ital", 0)], b(1.07), b(1.90)),
        (112, [("10", "xb", 1), ("times", "xb", 0), ("a", "xb", 0), ("day", "xb", 0)], b(1.90), b(3.03))], 540, 40)
    L += kcard(b(3.61), PROD_AT, [
        (44, [("promoting", "med", 0), ("my", "med", 0)], b(3.61), b(4.10)),
        (104, [("client's", "xbi", 0), ("products.", "xb", 0)], b(4.10), b(4.99))], 540, 44)
    # C: navy band; the last card rides through the black-and-white and the freeze
    c = lambda s: C_AT + (s - C_SRC[0])
    L += kcard(c(1.51), c(4.46), [
        (44, [("none", "med", 0), ("of", "med", 0), ("them", "med", 0)], c(1.51), c(1.95)),
        (112, [("are", "xb", 0), ("real.", "xb", 0)], c(1.95), c(2.41))], 540, 40)
    L += kcard(c(4.46), c(5.97), [
        (124, [("even", "xbi", 0), ("me.", "xb", 0)], c(4.46), c(4.93))], 540, 50)
    L += kcard(c(5.97), OUTRO_AT, [
        (44, [("I'm", "med", 0), ("also", "med", 0)], c(5.97), c(6.40)),
        (112, [("AI-generated.", "xb", 1)], c(6.40), c(7.15))], 540, 40)
    return L


# ================================================================= the stack
L, M = [], {"swipe_in": [], "swipe_out": [], "overlay": [], "outro": [], "kin": []}
add = lambda xs: L.extend(xs if isinstance(xs, list) else [xs])

# --- outro -----------------------------------------------------------------
for i, body, dly, size, y, col, face in (
        (71, "30 AI influencers.", 0.15, 92, 640, WHITE, "ms-bold"),
        (72, "Fully automated.", 0.55, 92, 750, ORANGE, "ms-bold"),
        (73, "The guide will be published soon", 1.25, 42, 990, (1, 1, 1, .78), "ms-semi"),
        (74, "x.com/hanifproduktif", 1.45, 60, 1060, WHITE, "ms-xbold")):
    add(text(i, body, OUTRO_AT + dly, OUTRO_DUR - dly, size, y, col, face)); M["outro"].append(i)
add(rect(70, "outro background", OUTRO_AT, OUTRO_DUR, BLACK))

# --- Hanif's kinetic type ------------------------------------------------------
add(kin_hanif())
M["kin"] = KIN_KEYS

# --- creator captions ------------------------------------------------------------
add(captions("robyn", [(0.30, 1.50, "I'm 61.")], 0.0, -SW, A_AT))
t = RUN_AT
for who, i, o, sc, ph in RUN:
    add(captions(who, ph, t - i, t, t + (o - i))); t += o - i
t = PROD_AT
for who, i, o, ph in PRODUCTS:
    add(captions(who, ph, t - i, t, t + (o - i))); t += o - i

# --- the freeze and C ------------------------------------------------------------
add({"type": "Image", "id": 60, "name": "Freeze", "blendMode": "normal",
     "activeRange": {"start": ms(FREEZE_AT), "duration": ms(FREEZE_DUR)},
     "transform": tr(), "source": {"assetId": "freeze", "fit": "cover"}})
add(video(52, "Hanif C black and white", "hanifCbw", C_BW_AT, C_SRC[1] - C_BW_SRC, C_BW_SRC, 10005))
add(video(51, "Hanif C", "hanifC", C_AT, C_BW_SRC - C_SRC[0], C_SRC[0], 10005))

# --- the swipe: a creator arriving scrolls up from below while whatever was on
# screen scrolls up and out. The outgoing shot's extra frames come from a MUTED
# tail segment, so its audio never runs over the next person's first word.
sfx_id, tail_id = [4000], [5000]


def swipe_in(lid, base_y, at):
    M["swipe_in"].append([lid, base_y])
    add({"type": "Audio", "id": sfx_id[0], "name": "swipe sfx", "windowMs": 680,
         "activeRange": {"start": ms(at - 0.12), "duration": 680},
         "sourceRange": {"start": 0, "duration": 680}, "sourceIntrinsicDuration": 680,
         "source": {"assetId": "swipe"}, "volume": 0.22, "captionsEnabled": False})
    sfx_id[0] += 1


def tail(name, asset, at, src, intrinsic, scale=FILL, transform=None, matte=None):
    lid = tail_id[0]; tail_id[0] += 1
    l = video(lid, name + " tail", asset, at, SW, src, intrinsic, scale=scale, vol=0.0,
              transform=transform, matte=matte, blur=True)
    y = (transform or l["transform"])["position"][1]
    M["swipe_out"].append([lid, y])
    return l


# product montage (the first one is entered from Hanif B, full frame)
t = PROD_AT
prev = ("Hanif B", "hanifB", B_SRC[1], 10005, FILL)
for n, (who, i, o, ph) in enumerate(PRODUCTS):
    pn, pa, psrc, pint, psc = prev
    add(tail(pn, pa, t, psrc, pint, psc))
    add(video(40 + n, "Product " + who, "pv-" + who, t, o - i, i, 6016, blur=True))
    swipe_in(40 + n, bias_y(FILL), t)
    prev = ("Product " + who, "pv-" + who, o, 6016, FILL)
    t += o - i

add(video(30, "Hanif B", "hanifB", B_AT, B_SRC[1] - B_SRC[0], B_SRC[0], 10005))

# the run (the first one is entered from Robyn + Hanif A)
t = RUN_AT
for n, (who, i, o, sc, ph) in enumerate(RUN):
    if n:
        pw, pi, po, psc, _ = RUN[n - 1]
        add(tail("Run " + pw, pw, t, po, INTRINSIC.get(pw, 10005), psc))
    add(video(20 + n, "Run " + who, who, t, o - i, i, INTRINSIC.get(who, 10005), scale=sc, blur=True))
    swipe_in(20 + n, bias_y(sc), t)
    t += o - i

# --- Hanif A keyed over Robyn, jump cut past the repeated line --------------------
ov = tr(pos=OVL_POS, scale=OVL_SCALE)
add(tail("Hanif A matte", "hanifAmatte", RUN_AT, A_END_SRC, 10005, transform=dict(ov)))
add(tail("Hanif A", "hanifArgb", RUN_AT, A_END_SRC, 10005, transform=dict(ov), matte=tail_id[0] - 1))
add(keyed(81, 82, "Hanif A1", "hanifA", A_AT, A_CUT, 0.0, 10005))
add(keyed(83, 84, "Hanif A2", "hanifA", A_AT + A_CUT, A_END_SRC - A2_SRC, A2_SRC, 10005))
M["overlay"] = [[81, 82]]

# --- Robyn: colour and full voice, then grey and nearly silent under him --------
add(tail("Robyn grey", "robyngrey", RUN_AT, RUN_AT, 10005))
for n, (a0, b0, g, asset) in enumerate(((0.0, A_AT, 1.0, "robyn"),
                                        (A_AT, A_AT + 0.2, 0.3, "robyngrey"),
                                        (A_AT + 0.2, RUN_AT, 0.06, "robyngrey"))):
    add(video(10 + n, "Robyn %d %s" % (n + 1, asset), asset, a0, b0 - a0, a0, 10005, vol=g))

doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json",
       "composition": {"id": "main", "name": "Main", "layers": L},
       "dimensions": {"width": W, "height": H}, "duration": round(TOTAL, 3), "formatVersion": 1}
M["ovl_y"] = OVL_POS[1]; M["sw_ms"] = ms(SW)
json.dump(M, open(sys.argv[1].replace(".json", "-manifest.json"), "w"), indent=1)
json.dump(doc, open(sys.argv[1], "w"), indent=1)
print("layers %d  captions %d  kinetic words %d  swipes %d  total %.2fs" % (
    len(L), (cap_id[0] - 2000) // 2, len(KIN_KEYS), len(M["swipe_in"]), TOTAL))
