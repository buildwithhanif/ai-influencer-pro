#!/usr/bin/env python3
"""carousel.py <slides.json> [--out slides/]

Turn generated character photos into a UGC-style carousel: 1080x1350, top scrim, a setup line,
a highlighted payoff line, and a detail line at the bottom. No design tool, no fonts to install.

slides.json:
{
  "out": "slides",
  "slides": [
    {"src": "shots/cover.jpg", "top": "my dad worked homicide for 26 years",
     "punch": "6 things he told me to NEVER do at night"},
    {"src": "shots/car.jpg",  "top": "1. if you think you're being followed",
     "punch": "do NOT drive home",
     "bottom": "drive to a gas station instead. lights, cameras, people."}
  ]
}

Rules that matter more than the code:
- The punch line is the slide. If it doesn't work alone in a screenshot, rewrite it.
- Lower case reads as a person, Title Case reads as a brand.
- One claim per slide, and no absolute claims you cannot support.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
FONTS = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf',
         '/System/Library/Fonts/Helvetica.ttc',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']

def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except Exception: pass
    return ImageFont.load_default()

def fit(im, focus=0.22):
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * focus)
    return im.crop((x, y, x + W, y + H))

def wrap(d, txt, f, maxw):
    lines, cur = [], ''
    for w in txt.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def scrim(im, top, h, strength):
    g = Image.new('L', (1, H), 0); px = g.load()
    for y in range(H):
        t = (1 - y / h) if top else (1 - (H - 1 - y) / h)
        px[0, y] = int(max(0, min(1, t)) * strength)
    return Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), im, g.resize((W, H)))

def render(s, out_path):
    im = fit(Image.open(s['src']).convert('RGB'), s.get('focus', 0.22))
    im = scrim(im, True, 620, 205)
    if s.get('bottom'):
        im = scrim(im, False, 430, s.get('bottom_strength', 180))
    d = ImageDraw.Draw(im); y = 96
    for text, sz, col in [(s.get('top'), 58, (255, 255, 255)),
                          (s.get('punch'), 84, (255, 214, 102))]:
        if not text: continue
        f = font(sz)
        for line in wrap(d, text, f, W - 140):
            d.text((70, y), line, font=f, fill=col); y += int(sz * 1.18)
        y += 14
    if s.get('bottom'):
        f = font(44); lines = wrap(d, s['bottom'], f, W - 140)
        yy = H - 70 - len(lines) * 55
        for line in lines:
            d.text((70, yy), line, font=f, fill=(255, 255, 255)); yy += 55
    im.save(out_path, quality=92)
    return out_path

def main():
    plan = json.load(open(sys.argv[1]))
    out = plan.get('out', 'slides')
    if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
    os.makedirs(out, exist_ok=True)
    for i, s in enumerate(plan['slides'], 1):
        print(render(s, os.path.join(out, f'slide-{i}.jpg')))

if __name__ == '__main__':
    main()
