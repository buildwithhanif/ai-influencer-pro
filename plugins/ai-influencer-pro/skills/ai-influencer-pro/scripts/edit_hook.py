#!/usr/bin/env python3
"""edit_hook.py <plan.json>

Cut an AI UGC hook into a montage-ready clip: Apple-style typography, a name kicker,
a slow push-in, and SFX sitting under the voice.

The plan is a JSON file; see plans/ for examples. Everything is driven from it, so the
same script does all fourteen characters.

WHY IT WORKS THE WAY IT DOES

  Captions are placed on REAL speech boundaries, not guesses. Run `beats.py` on the clip
  first: it reads the RMS envelope and prints where the phrases actually start and stop.
  Typing timings by ear is how captions end up a third of a second late, which reads as
  cheap even when the viewer cannot say why.

  Every frame of the overlay is rendered in Pillow and composited once. That buys exact
  control of the fade and the 24px rise, which ffmpeg's drawtext cannot do, and it means
  the type is rendered at 1080 wide rather than scaled up from 720.

  SFX are mixed at -20 dB or below. The brief was "people might not notice, but their brain
  likes it" — the moment you can name the sound, it is too loud.

Needs: Pillow, ffmpeg, ffprobe. Fonts come from ./fonts, SFX from ./sfx.
"""
import importlib.util, json, math, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

_spec = importlib.util.spec_from_file_location(
    "beats", os.path.join(os.path.dirname(os.path.abspath(__file__)), "beats.py"))
beats_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(beats_mod)


def jump_cut(src, dur, cfg, workdir):
    """Cut the dead air out of a take.

    Omni leaves 0.5-1.3 s of room tone between clauses because it is pacing the line to fill a
    fixed slot. Nobody edits a real UGC video that way: they cut the breath out, and that tight
    rhythm is the most recognisable 'this was edited' signal there is.

    Returns (new_src, new_duration, map_time) where map_time converts a timestamp in the
    original take to its position in the tightened one, so every caption cue still lands on
    the word it belongs to.
    """
    keep_pad = cfg.get("keep", 0.12)
    min_gap = cfg.get("min_gap", 0.45)
    ph, _ = beats_mod.phrases(src)
    ph = [(a, b) for a, b in ph if a < dur]
    if not ph:
        return src, dur, (lambda t: t)

    # Grow each phrase by the pad, then merge anything that now overlaps. What is left between
    # the merged blocks is dead air longer than min_gap, and that is what gets removed.
    keeps = []
    for a, b in ph:
        a2, b2 = max(0.0, a - keep_pad), min(dur, b + keep_pad)
        if keeps and a2 - keeps[-1][1] < min_gap:
            keeps[-1] = (keeps[-1][0], b2)
        else:
            keeps.append((a2, b2))
    keeps[0] = (0.0, keeps[0][1])           # never clip the head
    keeps[-1] = (keeps[-1][0], dur)          # never clip the tail

    removed = dur - sum(b - a for a, b in keeps)
    if removed < 0.12:
        return src, dur, (lambda t: t)

    out = os.path.join(workdir, "tight.mp4")
    v = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];" for i, (a, b) in enumerate(keeps))
    a_ = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];" for i, (a, b) in enumerate(keeps))
    cc = "".join(f"[v{i}][a{i}]" for i in range(len(keeps)))
    fc = v + a_ + cc + f"concat=n={len(keeps)}:v=1:a=1[v][a]"
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter_complex", fc,
                        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16",
                        "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                        "-b:a", "192k", "-ar", "48000", "-ac", "2", out],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:]); sys.exit(1)

    starts, acc = [], 0.0
    for a, b in keeps:
        starts.append((a, b, acc)); acc += b - a

    def map_time(t):
        for a, b, base in starts:
            if t < a:
                return base                       # inside removed air: snap to the next keep
            if t <= b:
                return base + (t - a)
        return acc

    print(f"  jump cut: removed {removed:.2f}s of air across {len(keeps)-1} cuts "
          f"({dur:.2f}s -> {acc:.2f}s)")
    return out, round(acc, 3), map_time

W, H = 1080, 1920
FPS = 24
ROOT = os.path.dirname(os.path.abspath(__file__))
SF = os.path.join(ROOT, "fonts/Font/Sans-Serif/San Francisco/pro")
SFX = os.path.join(ROOT, "sfx")

# Apple system colours. The accent is used on exactly one word per clip.
WHITE = (255, 255, 255)
ACCENT = (255, 159, 10)      # systemOrange dark-mode


def font(name, size):
    return ImageFont.truetype(os.path.join(SF, name), size)


def ease_out(t):
    """Cubic ease-out. Apple motion decelerates; linear fades look like a slideshow."""
    return 1 - pow(1 - t, 3)


def track(draw, xy, text, f, fill, tracking=0):
    """Draw text with letter tracking, since Pillow has no tracking control."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def track_width(draw, text, f, tracking=0):
    return sum(draw.textlength(c, font=f) for c in text) + tracking * max(0, len(text) - 1)


def wrap(draw, words, f, maxw):
    """Balanced wrap. Greedy wrapping leaves orphans ("...until I / was 59."), which is the
    single most amateur-looking thing a caption can do. Find the minimum number of lines that
    fits, then choose the split that makes those lines as even as possible."""
    def width(ws):
        return draw.textlength(" ".join(x["t"] for x in ws), font=f)

    n = len(words)
    for k in range(1, n + 1):
        best, best_cost = None, None
        # every way to cut the word list into k contiguous runs
        def walk(start, left, acc):
            nonlocal best, best_cost
            if left == 1:
                run = words[start:]
                w = width(run)
                if w > maxw:
                    return
                widths = [width(r) for r in acc] + [w]
                cost = max(widths) - min(widths)
                if best_cost is None or cost < best_cost:
                    best_cost, best = cost, acc + [run]
                return
            for end in range(start + 1, n - left + 2):
                run = words[start:end]
                if width(run) > maxw:
                    break
                walk(end, left - 1, acc + [run])
        walk(0, k, [])
        if best:
            return best
    return [words]


def render_frame(i, plan, cap_font, kick_font):
    t = i / FPS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # --- kicker, top (optional; set "kicker": "" to drop it) -----------------
    k = plan.get("kicker", "")
    if not k:
        pass
    else:
        kin, kout = 0.35, plan["duration"] - 0.45
        a = 0.0
        if t >= kin:
            a = min(1.0, ease_out(min(1.0, (t - kin) / 0.5)))
        if t > kout:
            a *= max(0.0, 1 - (t - kout) / 0.35)
        if a > 0.01:
            kw = track_width(d, k, kick_font, 5)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            dl = ImageDraw.Draw(layer)
            track(dl, ((W - kw) / 2, 148), k, kick_font, (255, 255, 255, int(200 * a)), 5)
            im.alpha_composite(layer)

    # --- captions, lower third ----------------------------------------------
    for beat in plan["beats"]:
        s, e = beat["in"], beat["out"]
        if not (s - 0.3 <= t <= e + 0.3):
            continue
        fade_in, fade_out = 0.20, 0.14
        if t < s:
            continue
        if t < s + fade_in:
            p = ease_out((t - s) / fade_in); rise = (1 - p) * 26
        elif t > e - fade_out:
            p = max(0.0, (e - t) / fade_out); rise = 0
        else:
            p, rise = 1.0, 0
        if p <= 0.01:
            continue

        words = [{"t": w[0], "hit": len(w) > 1 and w[1] == "hit"} for w in beat["words"]]
        lines = wrap(d, words, cap_font, W - 200)
        lh = int(cap_font.size * 1.16)
        block_h = lh * len(lines)
        y0 = plan.get("caption_y", 1395) - block_h + rise

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        for li, line in enumerate(lines):
            txt = " ".join(x["t"] for x in line)
            lw = dl.textlength(txt, font=cap_font)
            x = (W - lw) / 2
            y = y0 + li * lh
            for wobj in line:
                col = ACCENT if wobj["hit"] else WHITE
                dl.text((x, y), wobj["t"], font=cap_font, fill=col + (255,))
                x += dl.textlength(wobj["t"] + " ", font=cap_font)

        # Soft shadow so white type survives a bright kitchen window. Built from the
        # type's own alpha rather than a stroke: a stroke reads as a meme caption.
        alpha = layer.split()[3].point(lambda v: int(v * 0.85))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow.putalpha(alpha)
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))

        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(shadow, (0, 6))
        out.alpha_composite(layer)
        if p < 1.0:
            oa = out.split()[3].point(lambda v: int(v * p))
            out.putalpha(oa)
        im.alpha_composite(out)

    return im


def verify(path, want):
    """Audio and video must agree, and the rate must be 48 kHz. A silent mismatch here is
    what breaks a concat later, and it is invisible until you play the reel."""
    def probe(sel, fields):
        # ffprobe prints stream and format sections on separate LINES, not comma-joined.
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", sel,
                              "-show_entries", fields, "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout
        return [x for x in out.replace(",", "\n").split() if x]
    a = probe("a:0", "stream=sample_rate:format=duration")
    v = probe("v:0", "format=duration")
    rate = int(a[0]); adur = float(a[1]); vdur = float(v[0])
    if rate != 48000:
        sys.exit(f"FAIL {path}: audio is {rate} Hz, expected 48000")
    if abs(adur - vdur) > 0.12:
        sys.exit(f"FAIL {path}: audio {adur:.2f}s vs video {vdur:.2f}s")
    if abs(vdur - want) > 0.15:
        print(f"  note: {path} is {vdur:.2f}s, plan asked for {want:.2f}s")


def main():
    plan = json.load(open(sys.argv[1]))
    src = plan["src"]
    outdir = plan.get("frames", "/tmp/hookframes")
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)

    if plan.get("jumpcut"):
        src, newdur, mt = jump_cut(src, plan["duration"], plan["jumpcut"], outdir)
        plan["duration"] = newdur
        for bt in plan["beats"]:
            bt["in"], bt["out"] = round(mt(bt["in"]), 3), round(mt(bt["out"]), 3)
        for c in plan.get("cuts", []):
            c["at"] = round(mt(c["at"]), 3)

    cap_font = font(plan.get("caption_font", "SF-Pro-Display-Bold.otf"),
                    plan.get("caption_size", 70))
    kick_font = font("SF-Pro-Text-Medium.otf", 30)

    n = int(plan["duration"] * FPS)
    for i in range(n):
        render_frame(i, plan, cap_font, kick_font).save(f"{outdir}/{i:04d}.png")
    print(f"rendered {n} overlay frames")

    # push-in: 1.00 -> 1.045 across the clip, then crop back to frame
    # BASE VIDEO
    # "cuts" turns the clip into hard punch-ins: a cut to a tighter crop on the word that
    # matters. This is the one editing move that works inside a hook, because it never leaves
    # the face. Cutting away to b-roll in the first seconds kills the thing the hook is for.
    # Each cut is a real cut, not a zoom: the jump is the point.
    cuts = plan.get("cuts", [])
    z = plan.get("push", 0.045)
    dur = plan["duration"]

    def crop_at(scale):
        """Scale up and crop back to frame, biased slightly high so the punch lands on eyes."""
        if scale <= 1.001:
            return f"scale={W}:{H}:flags=lanczos"
        sw, sh_ = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
        x, y = (sw - W) // 2, int((sh_ - H) * plan.get("punch_bias", 0.38))
        return f"scale={sw}:{sh_}:flags=lanczos,crop={W}:{H}:{x}:{y}"

    base_scale = plan.get("base_scale", 1.0)
    if cuts:
        bounds = [0.0] + [c["at"] for c in cuts] + [dur]
        scales = [base_scale] + [c["scale"] for c in cuts]
        parts, labs = [], []
        for i, sc in enumerate(scales):
            a, b = bounds[i], bounds[i + 1]
            lab = f"[p{i}]"
            parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,{crop_at(sc)},"
                         f"format=yuv420p{lab}")
            labs.append(lab)
        base_chain = ";".join(parts) + ";" + "".join(labs) + \
                     f"concat=n={len(labs)}:v=1:a=0[base]"
    elif base_scale > 1.001:
        # A fixed tighter frame. In a run of short fragments this is the rhythm: consecutive
        # clips must not share a focal length or the whole run reads as one long shot.
        base_chain = f"[0:v]{crop_at(base_scale)},format=yuv420p[base]"
    else:
        # Slow push-in. Oversample 2x before zoompan: zoompan rounds its crop to whole pixels,
        # and at 1x that rounding shows as a stutter on a locked-off shot.
        n_ = int(dur * FPS)
        if z:
            step = z / n_
            base_chain = (f"[0:v]scale={W*2}:{H*2}:flags=lanczos,"
                          f"zoompan=z='min(zoom+{step:.8f},{1+z})':d=1"
                          f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
                          f"format=yuv420p[base]")
        else:
            base_chain = f"[0:v]scale={W}:{H}:flags=lanczos,format=yuv420p[base]"

    cmd = ["ffmpeg", "-y", "-v", "error",
           "-t", str(plan["duration"]), "-i", src,
           "-framerate", str(FPS), "-i", f"{outdir}/%04d.png"]
    sfx = plan.get("sfx", [])
    for s in sfx:
        cmd += ["-i", os.path.join(SFX, s["file"])]

    # video: push-in then overlay the rendered type
    fc = [base_chain, "[base][1:v]overlay=0:0:format=auto[v]"]

    # audio: voice + every SFX delayed to its cue, all mixed
    # loudnorm runs at 192 kHz internally and OUTPUTS at 192 kHz. Without the aresample the
    # encoder lands on 96 kHz, every clip disagrees with every card, and the concat demuxer
    # (which needs identical stream parameters) produces an audio track shorter than the
    # video. Always pin the rate after loudnorm.
    fc.append(f"[0:a]atrim=0:{plan['duration']},asetpts=PTS-STARTPTS,"
              f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]")
    mix = ["[voice]"]
    for idx, s in enumerate(sfx):
        lab = f"[s{idx}]"
        ms = int(s["at"] * 1000)
        fc.append(f"[{idx+2}:a]aresample=48000,volume={s.get('db', -20)}dB,"
                  f"adelay={ms}|{ms},apad=whole_dur={plan['duration']}{lab}")
        mix.append(lab)
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first[a]")

    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-movflags", "+faststart", plan["out"]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); sys.exit(1)
    shutil.rmtree(outdir, ignore_errors=True)
    verify(plan["out"], plan["duration"])
    print("wrote", plan["out"])


if __name__ == "__main__":
    main()
