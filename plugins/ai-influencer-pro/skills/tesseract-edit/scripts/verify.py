#!/usr/bin/env python3
"""verify.py — check what a render actually contains.

  words  MASTER.mp4
         Transcribe the whole master locally and print it as text. The only
         check that proves no cut clipped a word and that a ducked voice under a
         cut-in really is inaudible.
  sfx    PROJECT.tsrct DOC.json TIME [TIME ...]
         Export a copy with every Video layer at volume 0 and report the peak at
         each time. With voices on top an RMS reading proves nothing.
  frames PROJECT.tsrct TIME [TIME ...] [--out sheet.png]
         Full-resolution previews side by side. Judge placement here, not on a
         filmstrip tile, which can catch a word mid-animation.
"""
import json, os, shutil, subprocess, sys, tempfile
TS = os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")


def words(master):
    d = tempfile.mkdtemp(); shutil.copy(master, os.path.join(d, "m.mp4"))
    subprocess.run(["npx", "-y", "hyperframes", "transcribe", "m.mp4", "--language", "en", "--json"],
                   cwd=d, capture_output=True)
    t = json.load(open(os.path.join(d, "transcript.json")))
    print(" ".join(w["text"] for w in t))


def sfx(proj, doc, times):
    d = tempfile.mkdtemp(); p = os.path.join(d, "s.tsrct"); shutil.copy(proj, p)
    j = json.load(open(doc))
    for l in j["composition"]["layers"]:
        if l["type"] == "Video": l["volume"] = 0.0
    json.dump(j, open(os.path.join(d, "s.json"), "w"))
    subprocess.run([TS, "project", "commit", "-p", p, "--file", os.path.join(d, "s.json")], capture_output=True)
    out = os.path.join(d, "s.mp4")
    subprocess.run([TS, "export", "--project", p, "--output", out], capture_output=True)
    for t in times:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", t, "-t", "0.3", "-i", out, "-vn",
                            "-af", "astats", "-f", "null", "-"], capture_output=True, text=True)
        pk = [l for l in r.stderr.splitlines() if "Peak level" in l]
        print("  %6ss  %s" % (t, pk[0].split(":")[-1].strip() + " dBFS" if pk else "no audio"))


def frames(proj, times, out):
    from PIL import Image
    d = tempfile.mkdtemp(); tiles = []
    for t in times:
        png = os.path.join(d, t + ".png")
        r = subprocess.run([TS, "preview", "--project", proj, "--time", t, "--output", png],
                           capture_output=True, text=True)
        if not os.path.exists(png): sys.exit("preview at %s failed: %s" % (t, r.stdout + r.stderr))
        tiles.append(Image.open(png).resize((360, 640)))
    s = Image.new("RGB", (360 * len(tiles), 640))
    for i, t in enumerate(tiles): s.paste(t, (360 * i, 0))
    s.save(out); print("wrote", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "words": words(a[1])
    elif a[0] == "sfx": sfx(a[1], a[2], a[3:])
    elif a[0] == "frames":
        out = a[a.index("--out") + 1] if "--out" in a else "frames.png"
        ts = [x for x in a[2:] if x != "--out" and x != out]
        frames(a[1], ts, out)
    else: sys.exit(__doc__)
