#!/usr/bin/env python3
"""tsxi.py MANIFEST.json PROJECT.tsrct [--fonts]

Create a fresh document and package every asset listed in the manifest:

    {"video": {"luca": "../_hires/luca.mp4", ...},
     "image": {"freeze": "freeze.jpg"},
     "audio": {"swipe": "swipe.wav"}}

Writes assets.json beside the project: asset id -> intrinsic length in ms,
which Edit.clip() needs. Refuses any video or image that is not 1080x1920,
because one smaller source drags the whole export down to its size (run
prep.sh first). --fonts also imports every face tsx.FONTS knows.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tsx
TS = os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_type",
                        "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True)
    d = json.loads(r.stdout); v = [s for s in d["streams"] if s.get("codec_type") == "video"]
    return (v[0]["width"], v[0]["height"]) if v else None, float(d["format"].get("duration", 0) or 0)


def main():
    man, proj = sys.argv[1], sys.argv[2]
    base = os.path.dirname(os.path.abspath(man)); m = json.load(open(man))
    bad = []
    for kind in ("video", "image"):
        for k, p in m.get(kind, {}).items():
            wh, _ = probe(os.path.join(base, p))
            if wh != (1080, 1920): bad.append("%s %s is %s" % (kind, k, wh))
    if bad:
        sys.exit("not 1080x1920 (run prep.sh first):\n  " + "\n  ".join(bad))
    if os.path.exists(proj): os.remove(proj)
    subprocess.run([TS, "project", "create", "-p", proj], check=True, capture_output=True)
    out = {}
    for k, p in m.get("video", {}).items():
        r = subprocess.run([TS, "project", "import-video", "-p", proj, "--file", os.path.join(base, p),
                            "--asset-id", k], capture_output=True, text=True)
        if r.returncode: sys.exit("import %s failed: %s" % (k, r.stderr or r.stdout))
        out[k] = json.loads(r.stdout)["durationMs"]
    for kind in ("image", "audio"):
        for k, p in m.get(kind, {}).items():
            r = subprocess.run([TS, "project", "import-asset", "-p", proj, "--file", os.path.join(base, p),
                                "--asset-id", k, "--kind", kind], capture_output=True, text=True)
            if r.returncode: sys.exit("import %s failed: %s" % (k, r.stderr or r.stdout))
            out[k] = int(probe(os.path.join(base, p))[1] * 1000)
    if "--fonts" in sys.argv:
        for f in tsx.font_files():
            subprocess.run([TS, "project", "import-font", "-p", proj, "--file", f], capture_output=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(proj)), "assets.json"), "w"), indent=1)
    for k, v in out.items(): print("  %-16s %6d ms" % (k, v))
    print("wrote assets.json")


if __name__ == "__main__":
    main()
