#!/usr/bin/env python3
"""montage.py <montage.json>

Assemble the cast reel.

SHAPE, AND WHY

  Fourteen hooks back to back does not work. Every hook is a cold open with no payoff, so by
  the fourth one the viewer has stopped believing any of them and starts waiting for the
  trick. The reel has to earn the trick instead.

  1. COLD OPEN  one hook, played in full, edited like a real post. No AI signal at all.
     Robyn carries this: sixty-one, sun damage, greys, deadpan. She is the hardest one to
     disbelieve, which is exactly why she goes first.
  2. THE TURN   black, one line. "None of these people exist." This is the product.
  3. THE RUN    thirteen fragments, 1.4 to 4 seconds each, one self-contained clause apiece.
     Now the viewer is not judging whether it is real, they are counting how many there are.
  4. THE CLOSE  the numbers.

  Fragments are cut on phrase windows from beats.py, never mid-word, and every caption is the
  exact words spoken inside its window. A caption that paraphrases what you hear is the
  fastest way to make a real clip feel fake.

  Run order alternates gender, jumps age, and changes room every cut. Meera and Priya share a
  room (both trace to the same purple-LED reference), so they sit ten clips apart.

Needs edit_hook.py alongside it.
"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SF = os.path.join(ROOT, "fonts/Font/Sans-Serif/San Francisco/pro")
SFX = os.path.join(ROOT, "sfx")
W, H, FPS = 1080, 1920, 24
WORK = os.path.join(tempfile.gettempdir(), "montage_work")


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(" ".join(cmd)[:300]); print(r.stderr[-2500:]); sys.exit(1)


def words_of(text, accent):
    out = []
    for w in text.split():
        bare = w.strip(".,!?").upper()
        out.append([w, "hit"] if accent and bare == accent.upper() else [w])
    return out


def build_clip(seg, idx):
    """Trim the fragment, then run the normal hook editor over it."""
    cut = f"{WORK}/cut{idx:02d}.mp4"
    dur = round(seg["out"] - seg["in"], 3)
    sh(["ffmpeg", "-y", "-v", "error", "-ss", str(seg["in"]), "-t", str(dur),
        "-i", os.path.join(ROOT, seg["src"]),
        "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-r", str(FPS), cut])

    plan = {
        "src": cut, "out": f"{WORK}/seg{idx:02d}.mp4", "duration": dur,
        "kicker": "", "caption_y": seg.get("caption_y", 1420),
        "caption_size": seg.get("caption_size", 70),
        "push": seg.get("push", 0.03),
        "frames": f"{WORK}/f{idx:02d}",
        "beats": [{"in": b["in"], "out": b["out"],
                   "words": words_of(b["text"], b.get("accent"))} for b in seg["beats"]],
        "sfx": seg.get("sfx", [{"file": "01. Swoosh fast.mp3", "at": 0.0, "db": -25}]),
    }
    pf = f"{WORK}/plan{idx:02d}.json"
    json.dump(plan, open(pf, "w"))
    sh([sys.executable, os.path.join(ROOT, "edit_hook.py"), pf])
    return plan["out"]


def build_card(seg, idx):
    """A black card. Type only, no motion: after the run, stillness is the punctuation."""
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = seg["lines"]
    sizes = seg.get("sizes", [78] * len(lines))
    cols = seg.get("colours", [[255, 255, 255]] * len(lines))
    gaps = seg.get("gaps", [30] * (len(lines) - 1)) if len(lines) > 1 else []
    fonts = [ImageFont.truetype(os.path.join(SF, seg.get("font", "SF-Pro-Display-Bold.otf")), s)
             for s in sizes]
    heights = [int(s * 1.2) for s in sizes]
    total = sum(heights) + sum(gaps)
    y = (H - total) / 2
    for i, ln in enumerate(lines):
        lw = d.textlength(ln, font=fonts[i])
        d.text(((W - lw) / 2, y), ln, font=fonts[i], fill=tuple(cols[i]))
        y += heights[i] + (gaps[i] if i < len(gaps) else 0)
    png = f"{WORK}/card{idx:02d}.png"
    im.save(png)

    out = f"{WORK}/seg{idx:02d}.mp4"
    dur = seg["duration"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(dur), "-i", png,
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
    fc = ["[0:v]fade=t=in:st=0:d=0.25,fade=t=out:st=%.2f:d=0.3,format=yuv420p[v]"
          % (dur - 0.3)]
    amix = ["[1:a]"]
    for j, s in enumerate(seg.get("sfx", [])):
        cmd += ["-i", os.path.join(SFX, s["file"])]
        ms = int(s["at"] * 1000)
        fc.append(f"[{j+2}:a]volume={s.get('db',-20)}dB,adelay={ms}|{ms},"
                  f"apad=whole_dur={dur}[c{j}]")
        amix.append(f"[c{j}]")
    fc.append("".join(amix) + f"amix=inputs={len(amix)}:normalize=0:duration=first[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", out]
    sh(cmd)
    return out


def main():
    plan = json.load(open(sys.argv[1]))
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)

    parts = []
    for i, seg in enumerate(plan["segments"]):
        parts.append(build_card(seg, i) if seg["type"] == "card" else build_clip(seg, i))
        print(f"  [{i+1}/{len(plan['segments'])}] {seg.get('label', seg['type'])}")

    lst = f"{WORK}/list.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    sh(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        os.path.join(ROOT, plan["out"])])
    shutil.rmtree(WORK, ignore_errors=True)
    print("wrote", plan["out"])


if __name__ == "__main__":
    main()
