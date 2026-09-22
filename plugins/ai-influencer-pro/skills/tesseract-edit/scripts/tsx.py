"""tsx — a small layout library for building Tesseract (tsrct) edits in Python.

Everything here was learned the hard way on the AI UGC promo (Sep 2026) and is
correct for tsrct 0.1.0 where the vendor docs are not. The shape of a build:

    from tsx import Edit, PRESETS
    e = Edit()
    a = e.clip("luca", at=0.0, dur=2.15, src_in=0.40, intrinsic=10005)
    e.captions("capcut", [(0.55, 2.39, "Everyone told me|to meal prep")], offset=-0.40,
               clip_start=0.0, clip_end=2.15)
    e.save("edit.json", "motion.json")
    # tsrct project commit ... edit.json ; tsrct project apply ... motion.json

Layout and motion are produced in ONE pass: every method that needs keyframes
records them as it creates the layer, so the ids can never drift apart (the
old two-script split needed an id manifest and broke when a caption style owned
one layer sometimes and two other times).

Stacking is by `z` (higher is in front), resolved at save time, so you can add
things in any order. Defaults: footage 0, cut-ins 10, captions 20, graphics 30,
full-frame cards 40.
"""
import json, os
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "fonts"))

W, H = 1080, 1920
WHITE, BLACK = (1, 1, 1, 1), (0, 0, 0, 1)
INK = (0.07, 0.07, 0.09, 1)
ORANGE = (1.0, 0.624, 0.039, 1.0)

# (fontFamily, fontStyle) that the strict resolver ACCEPTS, with the file.
# Found by fontprobe.py; not uniform across families and not what the importer
# prints (it reports Montserrat ExtraBold as style "Regular", which fails).
FONTS = {
    "ms-black":   ("Montserrat-Black", "Black",         "Montserrat/Montserrat-Black.ttf"),
    "ms-xbold":   ("Montserrat-ExtraBold", "ExtraBold", "Montserrat/Montserrat-ExtraBold.ttf"),
    "ms-bold":    ("Montserrat", "Bold",                "Montserrat/Montserrat-Bold.ttf"),
    "ms-semi":    ("Montserrat-SemiBold", "SemiBold",   "Montserrat/Montserrat-SemiBold.ttf"),
    "in-med":     ("Inter28pt-Medium", "Medium",        "Inter/Inter_28pt-Medium.ttf"),
    "in-semi":    ("Inter28pt-SemiBold", "SemiBold",    "Inter/Inter_28pt-SemiBold.ttf"),
    "in-bold":    ("Inter28pt-Bold", "Bold",            "Inter/Inter_28pt-Bold.ttf"),
    "lato-black": ("Lato-Black", "Black",               "Lato/Lato-Black.ttf"),
    "pts-bi":     ("PTSerif-BoldItalic", "BoldItalic",  "PTSerif/PTSerif-BoldItalic.ttf"),
    "pf-ital":    ("PlayfairDisplay-Italic", "Italic",  "Playfair/PlayfairDisplay-Italic.ttf"),
}

# Caption presets. "capcut" is the standard auto-caption look. The rest are
# ordinary presets real creators pick; in a compilation give every person a
# DIFFERENT one so each reads as their own account.
#   face, size, color, case, stroke, box=(rgba, padx, pady, roundness),
#   shadow=(rgba, blur), y, align ("c" or a left x), word (one word at a time)
PRESETS = {
    "capcut":       dict(face="ms-xbold", size=74, color=WHITE, stroke=9, y=1170),
    "tiktok-box":   dict(face="ms-semi", size=56, color=WHITE, box=((0, 0, 0, .74), 26, 14, .35), y=1260),
    "one-word":     dict(face="ms-black", size=112, color=WHITE, case="upper", stroke=11, word=True, y=1070),
    "lowercase":    dict(face="in-med", size=50, color=WHITE, case="lower", shadow=((0, 0, 0, .65), 16), align=96, y=1500),
    "white-box":    dict(face="in-bold", size=54, color=INK, box=((1, 1, 1, 1), 24, 12, .30), y=1290),
    "purple-box":   dict(face="in-semi", size=52, color=WHITE, box=((.45, .33, .98, 1), 26, 13, .45), y=1330),
    "serif-italic": dict(face="pts-bi", size=66, color=WHITE, shadow=((0, 0, 0, .7), 18), y=1360),
    "lime":         dict(face="ms-xbold", size=76, color=(.72, 1, .2, 1), stroke=8, y=1160),
    "yellow-word":  dict(face="ms-black", size=100, color=(1, .85, .08, 1), case="upper", stroke=11, word=True, y=1090),
    "red-box":      dict(face="ms-xbold", size=58, color=WHITE, case="upper", box=((.88, .1, .14, 1), 24, 14, .12), y=1300),
    "elegant":      dict(face="pf-ital", size=84, color=WHITE, shadow=((0, 0, 0, .9), 10), y=1380),
    "genz":         dict(face="in-semi", size=58, color=WHITE, case="lower", stroke=5, y=1190),
    "yellow-box":   dict(face="lato-black", size=60, color=INK, box=((1, .83, .1, 1), 24, 12, .25), y=1300),
    "top":          dict(face="in-bold", size=54, color=WHITE, shadow=((0, 0, 0, .7), 16), y=300),
    "glow":         dict(face="ms-bold", size=66, color=WHITE, shadow=((0, .9, 1, .95), 26), y=1210),
}

EASE = {"type": "cubicBezier", "x1": 0.2, "y1": 0.0, "x2": 0.2, "y2": 1.0}
OUT = {"type": "cubicBezier", "x1": 0.4, "y1": 0.0, "x2": 1.0, "y2": 1.0}
FLICK = {"type": "cubicBezier", "x1": 0.3, "y1": 0.7, "x2": 0.25, "y2": 1.0}
LIN = {"type": "linear"}

ms = lambda s: int(round(s * 1000))
_fonts = {}


def font_files(keys=None):
    return [os.path.join(FONT_DIR, FONTS[k][2]) for k in (keys or FONTS)]


def measure(face, size, s):
    if (face, size) not in _fonts:
        _fonts[(face, size)] = ImageFont.truetype(os.path.join(FONT_DIR, FONTS[face][2]), size)
    return _fonts[(face, size)].getlength(s)


class Edit:
    def __init__(self, width=W, height=H, composition="main", first_id=1):
        self.W, self.H, self.cx, self.cy = width, height, width / 2, height / 2
        self.comp = composition
        self._id = first_id
        self.layers = []            # (z, seq, layer)
        self.actions = []
        self.end = 0.0

    # ------------------------------------------------------------ plumbing
    def nid(self):
        i = self._id; self._id += 1; return i

    def add(self, layer, z=0):
        self.layers.append((z, len(self.layers), layer))
        ar = layer["activeRange"]
        self.end = max(self.end, (ar["start"] + ar["duration"]) / 1000.0)
        return layer["id"]

    def keys(self, lid, prop, pts, tag=None):
        tag = tag or "k%d" % lid
        self.actions.append({"type": "setFxPropertyKeyframes", "compositionId": self.comp,
                             "property": {"layerId": lid, "propertyType": prop},
                             "keyframes": [{"id": "%s-%s-%d" % (tag, prop, t), "layerTime": int(t),
                                            "value": {"type": "float", "value": float(v)}, "easing": e}
                                           for t, v, e in pts]})

    def tr(self, pos=None, anchor=None, scale=100.0, opacity=100):
        # anchorPoint is LAYER-local: for a full-canvas source its centre is
        # (W/2, H/2) in the SOURCE's pixels, which matches only because every
        # source is pre-scaled to the canvas. Scale a 720-wide source and the
        # centre is (360, 640), and "cover" does not fit it for you.
        return {"anchorPoint": list(anchor or (self.cx, self.cy)),
                "position": list(pos or (self.cx, self.cy)),
                "scale": [scale, scale], "rotation": 0, "opacity": opacity}

    def bias_y(self, scale, bias=0.36):
        """A centre-anchored zoom that favours the eyes over the chin."""
        return self.cy + self.H * (scale / 100.0 - 1) * (0.5 - bias)

    # ------------------------------------------------------------ footage
    def clip(self, asset, at, dur, src_in, intrinsic, scale=100.0, vol=1.0, z=0,
             name=None, transform=None, matte=None, blur=False, id=None):
        """One cut of a video source. sourceRange = which moment of the source,
        activeRange = where it sits in the edit. intrinsic is the source's full
        length in ms. vol is LINEAR gain and is static: audio gain cannot be
        animated on a Video layer."""
        lid = id or self.nid()
        l = {"type": "Video", "id": lid, "name": name or asset, "blendMode": "normal",
             "activeRange": {"start": ms(at), "duration": ms(dur)},
             "sourceRange": {"start": ms(src_in), "duration": ms(dur)},
             "sourceIntrinsicDuration": int(intrinsic), "volume": float(vol),
             "transform": transform or self.tr(pos=(self.cx, self.bias_y(scale)), scale=scale),
             "source": {"assetId": asset, "fit": "cover"}}
        if matte is not None:
            l["trackMatte"] = {"mode": "luma", "layer": matte}
        if blur:
            l["motionBlur"] = True
        return self.add(l, z)

    def ducked(self, asset, segments, intrinsic, z=0, name=None):
        """One source split into consecutive layers of different static gain,
        [(start, end, gain, asset_or_None), ...] in edit seconds with source time
        equal to edit time. A 200 ms middle step reads as a ramp. Swap the asset
        per segment to cut to a graded copy (e.g. greyscale) at the same instant."""
        ids = []
        for a, b, g, alt in segments:
            ids.append(self.clip(alt or asset, a, b - a, a, intrinsic, vol=g, z=z,
                                 name="%s %.2f-%.2f" % (name or asset, a, b)))
        return ids

    def keyed(self, rgb_asset, matte_asset, at, dur, src_in, intrinsic, scale, pos,
              vol=1.0, z=10, name="cut-in", blur=True):
        """A green-screen subject cut out by a luma track matte (see key.sh).
        The matte layer is consumed by the picture and never paints itself; both
        need identical timing and transform or the cutout slides off the subject.
        Returns (picture_id, matte_id)."""
        t = self.tr(pos=pos, scale=scale)
        m = self.clip(matte_asset, at, dur, src_in, intrinsic, vol=0.0, z=z,
                      name=name + " matte", transform=dict(t), blur=blur)
        p = self.clip(rgb_asset, at, dur, src_in, intrinsic, vol=vol, z=z,
                      name=name, transform=dict(t), matte=m, blur=blur)
        # the matte sits directly IN FRONT of its picture in the stack
        self._pair(p, m)
        return p, m

    def _pair(self, pic, mat):
        zp = [e for e in self.layers if e[2]["id"] == pic][0]
        self.layers = [e for e in self.layers if e[2]["id"] != mat] + \
                      [(zp[0], zp[1] - 0.5, [e for e in self.layers if e[2]["id"] == mat][0][2])]

    def image(self, asset, at, dur, z=0, scale=100.0, name=None):
        return self.add({"type": "Image", "id": self.nid(), "name": name or asset,
                         "blendMode": "normal",
                         "activeRange": {"start": ms(at), "duration": ms(dur)},
                         "transform": self.tr(scale=scale),
                         "source": {"assetId": asset, "fit": "cover"}}, z)

    def sfx(self, asset, at, length_ms, vol=0.22, name="sfx"):
        """A sound effect as an Audio layer. Place it so its loudest point lands
        on the event: at = event - peak_offset."""
        return self.add({"type": "Audio", "id": self.nid(), "name": name, "windowMs": int(length_ms),
                         "activeRange": {"start": ms(at), "duration": int(length_ms)},
                         "sourceRange": {"start": 0, "duration": int(length_ms)},
                         "sourceIntrinsicDuration": int(length_ms), "source": {"assetId": asset},
                         "volume": float(vol), "captionsEnabled": False}, -5)

    # ------------------------------------------------------------- shapes
    def rect(self, at, dur, size, color, pos=None, roundness=0.0, z=30, grow_up=False, name="rect"):
        """A Rect's anchorPoint is ITS OWN space too. Anchor at the origin and
        hang the shape around it; grow_up hangs it above so scaleY rises from
        the baseline. roundness is normalized 0..1 (1 is a capsule)."""
        w, h = size
        org = [-w / 2.0, -h] if grow_up else [-w / 2.0, -h / 2.0]
        return self.add({"type": "Rect", "id": self.nid(), "name": name, "blendMode": "normal",
                         "activeRange": {"start": ms(at), "duration": ms(dur)},
                         "transform": self.tr(pos=pos or (self.cx, self.cy), anchor=(0, 0)),
                         "rect": {"size": [w, h], "fillColor": list(color),
                                  "position": org, "roundness": roundness}}, z)

    def fill(self, at, dur, color=BLACK, z=-10, name="background"):
        return self.rect(at, dur, (self.W, self.H), color, z=z, name=name)

    def text(self, body, at, dur, size, y, face="ms-bold", color=WHITE, z=40,
             align="center", x=None, box_w=940, stroke=0.0, shadow=None, tracking=0.0, name=None):
        fam = FONTS[face]
        st = {"text": body, "fontFamily": fam[0], "fontStyle": fam[1], "fontSize": size,
              "fillColor": list(color), "justification": align, "boxText": True,
              "boxPosition": [(self.cx - box_w / 2) if x is None else x, y],
              "boxSize": [box_w, size * 1.6], "verticalAlign": "top",
              "tracking": tracking, "strokeWidth": float(stroke)}
        if stroke:   # outline drawn BEHIND the fill so letterforms keep their weight
            st.update({"applyStroke": True, "strokeColor": list(BLACK), "strokeOverFill": False})
        l = {"type": "Text", "id": self.nid(), "name": name or "text " + body, "blendMode": "normal",
             "activeRange": {"start": ms(at), "duration": ms(dur)},
             "transform": self.tr(), "sourceText": st}
        if shadow:
            c, b = shadow
            l["dropShadow"] = {"color": list(c), "blurRadius": float(b), "spreadRadius": 0.0,
                               "blendMode": "normal", "offset": [0.0, 2.0]}
        return self.add(l, z)

    # ----------------------------------------------------------- captions
    def caption(self, preset, words, t0, t1, z=20):
        """One caption chunk in a preset. Measured with the real font so a box
        fits the words and a chunk never wraps (it shrinks instead)."""
        s = dict(PRESETS[preset]) if isinstance(preset, str) else dict(preset)
        face, size = s["face"], s["size"]
        if s.get("case") == "upper": words = words.upper()
        if s.get("case") == "lower": words = words.lower()
        tw = measure(face, size, words)
        if tw > self.W - 140:
            size = int(size * (self.W - 140) / tw); tw = measure(face, size, words)
        x0 = self.cx - tw / 2 if s.get("align", "c") == "c" else s["align"]
        ids = [self.text(words, t0, t1 - t0, size, s["y"], face=face, color=s["color"], z=z,
                         align="left", x=x0, box_w=tw + 80, stroke=s.get("stroke", 0),
                         shadow=s.get("shadow"), name="cap " + words)]
        if s.get("box"):
            c, px, py, rnd = s["box"]
            # the glyphs sit a little under the text box top; 0.62 em centres the box on them
            ids.append(self.rect(t0, t1 - t0, (tw + 2 * px, size * 1.18 + 2 * py), c,
                                 pos=(x0 + tw / 2, s["y"] + size * 0.62), roundness=rnd,
                                 z=z - 0.5, name="cap box"))
        return ids

    def captions(self, preset, phrases, offset, clip_start, clip_end, lead=0.0, z=20):
        """phrases: [(src_start, src_end, "chunk|chunk")] in SOURCE seconds, timed
        from the waveform, words from the transcript. offset = edit time of source 0.
        A chunk holds until the next unless the speaker pauses; it never starts
        before clip_start + lead (e.g. while a swipe is landing) and never runs
        past clip_end onto the next person."""
        s = PRESETS[preset] if isinstance(preset, str) else preset
        chunks = []
        for a, b, txt in phrases:
            parts = txt.split("|")
            if s.get("word"):
                parts = [w for p in parts for w in p.split()]
            wts = [len(p) + 2 for p in parts]; t = a
            for p, w in zip(parts, wts):
                d = (b - a) * w / sum(wts); chunks.append((t, t + d, p)); t += d
        ids = []
        for n, (a, b, p) in enumerate(chunks):
            nxt = chunks[n + 1][0] if n + 1 < len(chunks) else None
            end = nxt if (nxt is not None and nxt - b < 0.5) else b + 0.25
            # clamp in ONE unit: clip_end is edit time, chunk times are source time
            t0, t1 = max(offset + a, clip_start + lead), min(offset + end, clip_end)
            if t1 - t0 > 0.08:
                ids += self.caption(preset, p, t0, t1, z=z)
        return ids

    # --------------------------------------------------------- transitions
    def swipe(self, incoming_id, at, outgoing, sw=0.18, sfx_asset=None, sfx_len_ms=None,
              sfx_peak=0.21, sfx_vol=0.22):
        """A TikTok feed scroll: the incoming layer rises from below while what
        was on screen rises out of the top.

        The outgoing frames come from a MUTED TAIL, never from the incoming
        clip's pre-roll: many clips start speaking at 0.02 s and have none, and
        a tail with sound would run over the next person's first word. Check each
        tail lands in silence against the transcript.

        outgoing: list of dicts, one per layer that must leave the screen:
          {"asset", "src_out", "intrinsic", "scale"=100, "transform"=None, "matte"=False}
          List a keyed pair as its matte first, then its picture with matte=True.
        """
        base_in = self._layer(incoming_id)["transform"]["position"][1]
        self.keys(incoming_id, "positionY", [(0, base_in + self.H, LIN), (ms(sw), base_in, FLICK)], "in%d" % incoming_id)
        self._layer(incoming_id)["motionBlur"] = True
        last = None
        for o in outgoing:
            tid = self.clip(o["asset"], at, sw, o["src_out"], o["intrinsic"], scale=o.get("scale", 100.0),
                            vol=0.0, z=o.get("z", 0), transform=o.get("transform"),
                            matte=last if o.get("matte") else None, blur=True, name=o["asset"] + " tail")
            y = self._layer(tid)["transform"]["position"][1]
            # both on ONE curve, so they stay exactly a frame apart: no gap, no overlap
            self.keys(tid, "positionY", [(0, y, LIN), (ms(sw), y - self.H, FLICK)], "out%d" % tid)
            if o.get("matte"):
                self._pair(tid, last)
            last = tid
        if sfx_asset:
            # the Audio layer's sourceRange must not run past the file: pass the
            # real length from assets.json (tsxi.py writes it)
            if not sfx_len_ms:
                raise ValueError("swipe(): pass sfx_len_ms=assets[%r] from assets.json" % sfx_asset)
            self.sfx(sfx_asset, at + sw / 2 - sfx_peak, sfx_len_ms, sfx_vol, name="swipe")

    def _layer(self, lid):
        return [e for e in self.layers if e[2]["id"] == lid][0][2]

    # --------------------------------------------------------------- motion
    def fade_in(self, lid, ms_=150):
        self.keys(lid, "opacity", [(0, 0, LIN), (ms_, 100, EASE)], "fade%d" % lid)

    def punch(self, lid, start=108.0, ms_=340):
        """A cut onto a tighter frame that settles."""
        for ax in ("scaleX", "scaleY"):
            self.keys(lid, ax, [(0, start, LIN), (ms_, 100, EASE)], "punch%d" % lid)

    def rise(self, lid, dy=90.0, ms_=280):
        y = self._layer(lid)["transform"]["position"][1]
        self.keys(lid, "positionY", [(0, y + dy, LIN), (ms_, y, EASE)], "rise%d" % lid)

    # ----------------------------------------------------------------- save
    def document(self, duration=None):
        ordered = [l for _, _, l in sorted(self.layers, key=lambda e: (-e[0], e[1]))]
        return {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json",
                "composition": {"id": self.comp, "name": "Main", "layers": ordered},
                "dimensions": {"width": self.W, "height": self.H},
                "duration": round(duration or self.end, 3), "formatVersion": 1}

    def save(self, doc_path, actions_path, duration=None):
        json.dump(self.document(duration), open(doc_path, "w"), indent=1)
        json.dump(self.actions, open(actions_path, "w"), indent=1)
        n = len(self.layers)
        return "%d layers, %d keyframe actions, %.2fs" % (n, len(self.actions), duration or self.end)
