#!/usr/bin/env python3
"""score-frames.py <frame.jpg | dir> [...] [--sheet contact.jpg] [--json scores.json]
                   [--zone x0,y0,x1,y1] [--quiet]

Screen candidate reference frames mechanically instead of squinting at them.

Step 1 says: pick a real frame, choose the framing on purpose, make sure the highlights are not
blown, make sure the background has a life in it. Framing is a decision and this script will not
make it for you. The other two are measurements, and the one that matters most (blown highlights
on skin) is the one people get wrong by eye, because a laptop at 40% brightness hides clipping
that the video model will happily turn into wax.

Pure Pillow. No numpy, no OpenCV, nothing to install beyond what carousel.py already needs.

WHAT IT MEASURES
  skin_clip    % of the skin region at luma >= 250. Blown = no data = dead space when animated.
               The skin mask is DILATED before counting, because a blown cheek stops reading as
               skin (its Cb/Cr go neutral at white) and would otherwise be invisible to the test.
               Measured: real frames from one creator's video sit at 0.000-0.002%. Brightening
               one of those same frames by 1.3x takes it to 2.8%.
  skin_hot     Same, at luma >= 242. The early warning. Informational only.
  skin_detail  Fine-detail energy over skin, divided by the region's own contrast so the number
               survives a dark frame and a bright one. This is a FLOOR test: it catches beauty
               filters, heavy denoise and soft focus, the frames with nothing real to animate.
               Measured on real frames: 3.8 to 9.9.
  skin_grain   Same, restricted to skin that is also flat at medium scale, i.e. texture with the
               structure taken out. Measured on real frames: 2.1 to 6.7.
               NOT an AI detector. A Nano Banana avatar built off a good reference scored 6.4
               here, above most of the real frames. It tells you whether there is texture, not
               where the texture came from.
  sharp        The same normalised measure over the whole frame. Catches motion blur.
  face_fill    % of the face zone reading as skin. A sanity check on the zone, not a quality score.
  bg_entropy   Entropy outside the face zone. Low is a blank wall, very high is clutter.
  captions     Rows carrying both a lot of near-white pixels AND a lot of fine edge energy, i.e.
               white glyphs on a dark stroke. Reported as y% ranges. Validated: found a synthetic
               caption at y=30% and at y=80% exactly, and found the real 2-line overlay on the two
               frames of an 12-frame set that had one, with no false positives on the other ten.
               It will miss text that is small AND low contrast, e.g. grey-on-grey at 3% opacity.
               Look at the contact sheet as well; this is a filter, not a guarantee.

WHAT IT CANNOT DO
  No face detection. It assumes a talking-head frame and looks for skin inside a default zone
  (x 20-80%, y 5-65%). Off-centre or standing subject: pass --zone. If face_fill comes back under
  4% the zone is wrong and every skin number is meaningless.
  It does not judge framing, and it cannot tell you whether the person suits the product.

Exit code 0 when at least one frame is usable, 1 when none are.
"""
import json, math, os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

# Calibrated 21 Sep 2026 against 18 frames from a real TikTok talking-head video at 720x1280,
# plus a brightness sweep to find where clipping starts to bite. Re-measure on your own footage
# before trusting the WARN band; the REJECT lines are deliberately generous.
LIMITS = {
    'skin_clip':   {'reject': 1.00, 'warn': 0.25, 'dir': 'low'},    # percent
    'skin_detail': {'reject': 2.50, 'warn': 4.00, 'dir': 'high'},
    'skin_grain':  {'reject': 1.20, 'warn': 2.20, 'dir': 'high'},
    'sharp':       {'reject': 1.50, 'warn': 2.20, 'dir': 'high'},
    'bg_entropy':  {'reject': 3.20, 'warn': 4.20, 'dir': 'high'},
}
SCORE_TOP = {'skin_clip': 0.02, 'skin_detail': 8.0, 'skin_grain': 4.4, 'sharp': 4.4}

ZONE = (0.20, 0.05, 0.80, 0.65)     # face zone as fractions of w,h for a 9:16 talking head
MAXW = 900                          # analyse at this width: consistent numbers, and fast

FONTS = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf',
         '/System/Library/Fonts/Helvetica.ttc',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
         '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf']


def font(sz):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def skin_mask(im):
    """YCbCr skin gate. Crude, and it does pick up bare wood, which is why it is only ever
    applied inside the face zone."""
    y, cb, cr = im.convert('YCbCr').split()
    m = ImageChops.multiply(cb.point(lambda v: 255 if 77 <= v <= 127 else 0),
                            cr.point(lambda v: 255 if 133 <= v <= 173 else 0))
    return ImageChops.multiply(m, y.point(lambda v: 255 if v >= 45 else 0))


def dilate(mask, r=9):
    """A blown-out cheek stops reading as skin, so it burns a hole in the mask exactly where the
    problem is. Dilating puts the hole back inside the region before we count clipped pixels."""
    return mask.filter(ImageFilter.MaxFilter(r if r % 2 else r + 1))


def flat_mask(gray):
    """Pixels with no structure at medium scale: whatever fine detail is left there is texture."""
    d = ImageChops.difference(gray.filter(ImageFilter.GaussianBlur(2)),
                              gray.filter(ImageFilter.GaussianBlur(6)))
    return d.point(lambda v: 255 if v < 6 else 0)


def fine(gray):
    """Fine detail only: the image minus a 1.2 px blur of itself."""
    return ImageChops.difference(gray, gray.filter(ImageFilter.GaussianBlur(1.2)))


def texture(fine_im, gray, mask=None):
    """Fine-detail energy normalised by the region's own contrast, so it means roughly the same
    thing on a dim frame and a bright one. Raw Laplacian variance does not: brighten a photo and
    it triples without a single new pore appearing."""
    if mask is not None and ImageStat.Stat(mask).sum[0] < 255 * 200:
        return 0.0
    spread = math.sqrt(max(ImageStat.Stat(gray, mask).var[0], 1.0))
    return 100.0 * ImageStat.Stat(fine_im, mask).mean[0] / spread


def caption_bands(gray, fine_im, h):
    """Burned-in captions are white glyphs on a dark stroke: rows carrying both a lot of near-white
    pixels AND a lot of fine edge energy. Edge energy alone is not enough, it fires on a jawline
    or the edge of a table."""
    w = gray.width
    bright = [sum(gray.crop((0, y, w, y + 1)).histogram()[232:]) / w for y in range(h)]
    edge = [ImageStat.Stat(fine_im.crop((0, y, w, y + 1))).mean[0] for y in range(h)]
    bmed = sorted(bright)[h // 2]
    emed = sorted(edge)[h // 2] or 1.0
    hot = [bright[y] > max(0.03, bmed * 3.0) and edge[y] > emed * 1.8 for y in range(h)]
    bands, run = [], 0
    for y in range(h + 1):
        if y < h and hot[y]:
            run += 1
        else:
            if h * 0.012 <= run <= h * 0.16:
                bands.append((round(100 * (y - run) / h), round(100 * y / h)))
            run = 0
    return bands


def score_file(path, zone=ZONE):
    im = Image.open(path).convert('RGB')
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    w, h = im.size
    box = (int(zone[0] * w), int(zone[1] * h), int(zone[2] * w), int(zone[3] * h))

    gray = im.convert('L')
    fine_im = fine(gray)
    zone_im, zone_gray, zone_fine = im.crop(box), gray.crop(box), fine_im.crop(box)

    skin = skin_mask(zone_im)
    region = dilate(skin)
    flat = ImageChops.multiply(skin, flat_mask(zone_gray))

    zone_px = (box[2] - box[0]) * (box[3] - box[1])
    skin_px = ImageStat.Stat(skin).sum[0] / 255

    if skin_px >= 200:
        hist = zone_gray.histogram(mask=region)
        tot = max(1, sum(hist))
        clip, hot = 100 * sum(hist[250:]) / tot, 100 * sum(hist[242:]) / tot
    else:
        clip = hot = 0.0

    bg = im.copy()
    ImageDraw.Draw(bg).rectangle(box, fill=(0, 0, 0))

    m = {
        'skin_clip':   round(clip, 3),
        'skin_hot':    round(hot, 3),
        'skin_detail': round(texture(zone_fine, zone_gray, skin), 2),
        'skin_grain':  round(texture(zone_fine, zone_gray, flat), 2),
        'sharp':       round(texture(fine_im, gray), 2),
        'face_fill':   round(100 * skin_px / zone_px, 1),
        'bg_entropy':  round(bg.convert('L').entropy(), 2),
        'captions':    caption_bands(gray, fine_im, h),
    }

    notes, verdict = [], 'PASS'
    if m['face_fill'] < 4.0:
        notes.append('face zone has almost no skin in it: wrong zone, or the face is too small. '
                     'Every skin number below is meaningless. Re-run with --zone.')
        verdict = 'CHECK'
    else:
        for k, lim in LIMITS.items():
            v = m[k]
            worse = (lambda a, b: a > b) if lim['dir'] == 'low' else (lambda a, b: a < b)
            arrow = '<' if lim['dir'] == 'low' else '>'
            if worse(v, lim['reject']):
                verdict = 'REJECT'
                notes.append(f"{k} {v} past the reject line (want {arrow} {lim['reject']})")
            elif worse(v, lim['warn']):
                verdict = 'WARN' if verdict == 'PASS' else verdict
                notes.append(f"{k} {v} is marginal (want {arrow} {lim['warn']})")

    face_y = (100 * zone[1], 100 * zone[3])
    over = [b for b in m['captions'] if b[1] > face_y[0] and b[0] < face_y[1]]
    if over:
        notes.append(f'text band across the face at y {over[0][0]}-{over[0][1]}%. The avatar prompt '
                     'has to erase it, and erasing text off a face is where one-shot edits fail')
        verdict = 'WARN' if verdict == 'PASS' else verdict
    elif m['captions']:
        notes.append(f'captions clear of the face at y {m["captions"]}, fine')

    def band(v, lo, hi):
        return max(0.0, min(1.0, (v - lo) / (hi - lo)))
    m['score'] = round(100 * (
        0.40 * band(-m['skin_clip'], -LIMITS['skin_clip']['reject'], -SCORE_TOP['skin_clip']) +
        0.25 * band(m['skin_grain'], LIMITS['skin_grain']['reject'], SCORE_TOP['skin_grain']) +
        0.20 * band(m['skin_detail'], LIMITS['skin_detail']['reject'], SCORE_TOP['skin_detail']) +
        0.10 * band(m['bg_entropy'], 3.0, 5.2) +
        0.05 * band(m['sharp'], LIMITS['sharp']['reject'], SCORE_TOP['sharp'])), 1)
    if verdict == 'REJECT':
        m['score'] = round(m['score'] * 0.5, 1)

    m.update(file=path, verdict=verdict, notes=notes)
    return m


def sheet(results, out, cols=3, cell=360):
    rows = math.ceil(len(results) / cols)
    pad, bar = 12, 104
    sh = Image.new('RGB', (cols * (cell + pad) + pad, rows * (cell + bar + pad) + pad), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    f1, f2 = font(26), font(19)
    colour = {'PASS': (150, 220, 150), 'WARN': (255, 214, 102),
              'REJECT': (240, 120, 120), 'CHECK': (170, 170, 170)}
    for i, r in enumerate(results):
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + bar + pad)
        im = Image.open(r['file']).convert('RGB')
        s = cell / max(im.size)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        sh.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.text((x + 4, y + cell + 6), f"{r['verdict']}  {r['score']}", font=f1,
               fill=colour[r['verdict']])
        d.text((x + 4, y + cell + 38), os.path.basename(r['file'])[:34], font=f2, fill=(200,) * 3)
        d.text((x + 4, y + cell + 60), f"clip {r['skin_clip']}%  grain {r['skin_grain']}",
               font=f2, fill=(170,) * 3)
        d.text((x + 4, y + cell + 80), f"detail {r['skin_detail']}  bg {r['bg_entropy']}",
               font=f2, fill=(170,) * 3)
    sh.save(out, quality=90)
    return out


def main():
    args, opt, paths = sys.argv[1:], {}, []
    if not args:
        print(__doc__)
        sys.exit(2)
    i = 0
    while i < len(args):
        if args[i] in ('--sheet', '--json', '--zone'):
            opt[args[i]] = args[i + 1]; i += 2
        elif args[i] == '--quiet':
            opt[args[i]] = True; i += 1
        else:
            paths.append(args[i]); i += 1

    zone = tuple(float(v) for v in opt['--zone'].split(',')) if '--zone' in opt else ZONE

    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        else:
            files.append(p)
    if not files:
        print('no images found'); sys.exit(2)

    results = sorted((score_file(f, zone) for f in files), key=lambda r: -r['score'])

    if not opt.get('--quiet'):
        print(f"{'score':>6} {'verdict':<7} {'clip%':>6} {'detail':>7} {'grain':>6} {'sharp':>6} "
              f"{'face%':>6} {'bg':>5}  file")
        for r in results:
            print(f"{r['score']:>6} {r['verdict']:<7} {r['skin_clip']:>6} {r['skin_detail']:>7} "
                  f"{r['skin_grain']:>6} {r['sharp']:>6} {r['face_fill']:>6} {r['bg_entropy']:>5}  "
                  f"{os.path.basename(r['file'])}")
        print()
        for r in results:
            if r['notes']:
                print(os.path.basename(r['file']))
                for n in r['notes']:
                    print('   -', n)

    if '--json' in opt:
        json.dump(results, open(opt['--json'], 'w'), indent=1)
        print('\nwrote', opt['--json'])
    if '--sheet' in opt:
        print('wrote', sheet(results, opt['--sheet']))

    sys.exit(0 if any(r['verdict'] in ('PASS', 'WARN') for r in results) else 1)


if __name__ == '__main__':
    main()
