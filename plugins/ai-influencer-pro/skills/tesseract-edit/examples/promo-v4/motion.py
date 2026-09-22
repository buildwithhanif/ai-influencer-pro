#!/usr/bin/env python3
"""v4 motion pass. Reads the id manifest build.py writes; never guesses ids.

Captions on the creators stay still, like real subtitles. What moves:
  * the swipe: incoming and outgoing scroll together on ONE curve, so they stay
    exactly a frame-height apart and never gap or overlap
  * Hanif's kinetic words: small ones fade in, big ones land with a scale-in
  * his cut-in rising into the corner, and the outro arriving
"""
import json, sys
M = json.load(open(sys.argv[2]))
EASE = {"type": "cubicBezier", "x1": 0.2, "y1": 0.0, "x2": 0.2, "y2": 1.0}
FLICK = {"type": "cubicBezier", "x1": 0.3, "y1": 0.7, "x2": 0.25, "y2": 1.0}   # a thumb flick
LIN = {"type": "linear"}
SW = M["sw_ms"]
acts = []
def keys(lid, prop, pts, tag):
    acts.append({"type": "setFxPropertyKeyframes", "compositionId": "main",
                 "property": {"layerId": lid, "propertyType": prop},
                 "keyframes": [{"id": "%s-%s-%d" % (tag, prop, t), "layerTime": t,
                                "value": {"type": "float", "value": float(v)}, "easing": e}
                               for t, v, e in pts]})
for lid, y in M["swipe_in"]:
    keys(lid, "positionY", [(0, y + 1920, LIN), (SW, y, FLICK)], "in%d" % lid)
for lid, y in M["swipe_out"]:
    keys(lid, "positionY", [(0, y, LIN), (SW, y - 1920, FLICK)], "out%d" % lid)
for lid, big in M["kin"]:
    keys(lid, "opacity", [(0, 0, LIN), (120 if big else 90, 100, EASE)], "k%d" % lid)
    if big:
        for ax in ("scaleX", "scaleY"):
            keys(lid, ax, [(0, 124, LIN), (280, 100, EASE)], "k%d" % lid)
for pic, mat in M["overlay"]:
    for lid in (pic, mat):
        keys(lid, "opacity", [(0, 0, LIN), (220, 100, EASE)], "ovl%d" % lid)
        keys(lid, "positionY", [(0, M["ovl_y"] + 90, LIN), (280, M["ovl_y"], EASE)], "ovl%d" % lid)
for n, lid in enumerate(M["outro"]):
    keys(lid, "opacity", [(0, 0, LIN), (280, 100, EASE)], "outro%d" % n)
json.dump(acts, open(sys.argv[1], "w"), indent=1)
print("%d actions" % len(acts))
