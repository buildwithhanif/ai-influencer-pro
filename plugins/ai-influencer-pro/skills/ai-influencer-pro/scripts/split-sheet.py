#!/usr/bin/env python3
"""split-sheet.py <sheet.jpg> <outdir> [--cuts 0.235,0.47,0.70]
Cut a 4-panel Nano Banana character sheet into front / three-quarter / back / face crops.
Video models take single-subject references better than a strip, and the face crop is the one you
attach when a shot is a close-up. Panels on a generated sheet are never exactly equal width, so pass
--cuts after eyeballing the sheet once."""
import sys, os
from PIL import Image
if len(sys.argv) < 3: print(__doc__); sys.exit(1)
src, out = sys.argv[1], sys.argv[2]
cuts = [0.235, 0.47, 0.70]
if '--cuts' in sys.argv: cuts = [float(x) for x in sys.argv[sys.argv.index('--cuts')+1].split(',')]
os.makedirs(out, exist_ok=True)
im = Image.open(src); W, H = im.size
edges = [0.0] + cuts + [1.0]
for (a, b), n in zip(zip(edges, edges[1:]), ['front', 'threequarter', 'back', 'face']):
    c = im.crop((int(a*W), 0, int(b*W), H)); c.save(os.path.join(out, f'{n}.jpg'), quality=95); print(n, c.size)
