#!/usr/bin/env python3
"""labels.py <outdir> --case "CASE #0041" --part "PART 1" --handle "@handle"
Renders the overlay PNGs assemble.sh burns in, with Pillow, so ffmpeg does not need drawtext/freetype:
  case.png   1080x1920 transparent, case label near the top
  part.png   1080x1920 transparent, PART label near the bottom
  outro1.png 1080x1920 black, "TO BE CONTINUED..."
  outro2.png 1080x1920 black, "FOLLOW <handle> FOR PART 2"
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def opt(n, d):
    return sys.argv[sys.argv.index('--'+n)+1] if '--'+n in sys.argv else d
CASE, PART, HANDLE = opt('case', 'CASE #0000'), opt('part', 'PART 1'), opt('handle', '@yourhandle')
W, H = 1080, 1920
def font(sz):
    for p in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, sz)
            except Exception: pass
    return ImageFont.load_default()
def pill(text, sz, y, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); f = font(sz)
    l, t, r, b = d.textbbox((0, 0), text, font=f); tw, th = r - l, b - t; pad = 22
    x0 = (W - tw) // 2 - pad; d.rounded_rectangle((x0, y - pad, x0 + tw + 2*pad, y + th + pad), radius=18, fill=(0, 0, 0, 150))
    d.text(((W - tw) // 2 - l, y - t), text, font=f, fill=(255, 255, 255, 255)); im.save(path)
def card(text, sz, path):
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im); f = font(sz)
    l, t, r, b = d.textbbox((0, 0), text, font=f); d.text(((W - (r - l)) // 2 - l, (H - (b - t)) // 2 - t), text, font=f, fill=(255, 255, 255)); im.save(path)
pill(CASE, 44, 150, os.path.join(out, 'case.png'))
pill(PART, 56, H - 320, os.path.join(out, 'part.png'))
card('TO BE CONTINUED...', 84, os.path.join(out, 'outro1.png'))
card(f'FOLLOW {HANDLE} FOR PART 2', 56, os.path.join(out, 'outro2.png'))
print('labels ->', out)
