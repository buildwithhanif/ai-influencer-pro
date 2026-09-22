#!/usr/bin/env python3
"""kt.py — Apple-style kinetic type for Tesseract projects.

  plan   CLIP [--offset S] [--from S --to S] [--y 40] [--out spec.json]
         Transcribe the clip locally and read its speech envelope, then write a
         DRAFT card spec: one card per phrase, the last word(s) as the big line.
         Words come from whisper; timing comes from the waveform (whisper's
         word starts drift up to ~0.8 s and it snaps the first word to 0.0).

  proto  CLIP --at S --text "small line|BIG LINE" [--y 40 1000 1300] [--out proto.png]
         Render the same card at several heights on a real frame, side by side,
         so placement is decided by looking, not by guessing where the space is.

  build  SPEC --project P.tsrct
         Inject the cards into an existing project: import the bundled Inter
         faces, check out the document, drop any earlier kt: layers, append the
         new ones on top, commit, then apply their keyframes. Re-runnable.

  check  SPEC --project P.tsrct [--out check.png]
         Render every card at FULL resolution once its last word has landed.
         A filmstrip thumbnail can catch a big word mid-scale-in and make it
         look misplaced; the full-res frame is the truth.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinetic

TS = os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")


def run(*a, **kw):
    return subprocess.run(list(a), capture_output=True, text=True, **kw)


# ------------------------------------------------------------------ speech
def envelope(path, floor=-45.0, min_gap=0.25):
    """Speech windows [(start, end)] from the RMS envelope. silencedetect finds
    nothing on generated clips because they carry continuous room tone."""
    tmp = tempfile.mktemp(suffix=".txt")
    run("ffmpeg", "-v", "error", "-i", path, "-af",
        "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=" + tmp,
        "-f", "null", "-")
    pairs = re.findall(r"pts_time:([0-9.]+)\n[^\n]*RMS_level=(-?[0-9.]+|-inf)", open(tmp).read())
    os.remove(tmp)
    ser = [(float(t), -99.0 if v == "-inf" else float(v)) for t, v in pairs]
    if not ser:
        return []
    loud = [v for _, v in ser if v > floor]
    gate = max(floor, (sum(loud) / len(loud) if loud else -30) - 10)
    runs, cur, start = [], ser[0][1] > gate, ser[0][0]
    for t, v in ser[1:]:
        s = v > gate
        if s != cur:
            runs.append((start, t, cur)); cur, start = s, t
    runs.append((start, ser[-1][0], cur))
    out = []
    for a, b, s in runs:
        if not s or b - a < 0.18:
            continue
        if out and a - out[-1][1] < min_gap:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def transcribe(path):
    """Local whisper via the HyperFrames CLI. Nothing leaves the machine."""
    d = tempfile.mkdtemp()
    shutil.copy(path, os.path.join(d, "in" + os.path.splitext(path)[1]))
    r = run("npx", "-y", "hyperframes", "transcribe", "in" + os.path.splitext(path)[1],
            "--language", "en", "--json", cwd=d)
    p = os.path.join(d, "transcript.json")
    if not os.path.exists(p):
        sys.exit("transcribe failed:\n" + r.stdout[-800:] + r.stderr[-800:])
    return json.load(open(p))


def assign(words, phrases):
    """Give each phrase its words.

    Whisper's word TIMES are unreliable here but its ORDER and PUNCTUATION are
    not. Each boundary starts where a length-proportional split would put it,
    then moves up to three words to whichever gap scores best: a clause mark
    (, . ? !) is worth most, a real pause in whisper's timing next, distance
    from the proportional guess costs a little.
    """
    n, K = len(words), len(phrases)
    if K == 0 or n == 0:
        return [[] for _ in phrases]
    chars = [len(w["text"]) + 1 for w in words]
    cum = [0]
    for c in chars: cum.append(cum[-1] + c)
    dur = [b - a for a, b in phrases]
    cuts, prev, acc = [], 0, 0.0
    for k in range(K - 1):
        acc += dur[k]
        target = cum[-1] * acc / sum(dur)
        guess = min(range(prev + 1, n), key=lambda j: abs(cum[j] - target), default=prev + 1)
        best, best_s = guess, -1e9
        for j in range(max(prev + 1, guess - 3), min(n - (K - 1 - k), guess + 4)):
            w = words[j - 1]
            gap = max(0.0, words[j]["start"] - w.get("end", w["start"]))
            s = (3.0 if w["text"][-1:] in ",.?!;:" else 0.0) + 2.0 * min(gap, 1.0) - 0.4 * abs(j - guess)
            if s > best_s: best, best_s = j, s
        cuts.append(best); prev = best
    bounds = [0] + cuts + [n]
    return [[w["text"] for w in words[bounds[i]:bounds[i + 1]]] for i in range(K)]


def cmd_plan(a):
    ph = envelope(a.clip)
    if a.src_from is not None:
        ph = [(max(s, a.src_from), min(e, a.src_to)) for s, e in ph if e > a.src_from and s < a.src_to]
    words = transcribe(a.clip)
    if a.src_from is not None:                   # whisper drifts early; keep a margin
        words = [w for w in words if a.src_from - 0.9 <= w["start"] <= a.src_to]
    print("transcript:", " ".join(w["text"] for w in words))
    groups = assign(words, ph)
    cards = []
    for n, ((s, e), ws) in enumerate(zip(ph, groups)):
        if not ws:
            continue
        nxt = ph[n + 1][0] if n + 1 < len(ph) else e + 0.6
        k = 1 if len(ws[-1]) >= 6 or len(ws) <= 2 else 2
        small, big = ws[:-k], ws[-k:]
        split = s + (e - s) * (sum(len(w) + 1 for w in small) / max(1, sum(len(w) + 1 for w in ws)))
        lines = []
        if small:
            lines.append({"size": 46, "t0": round(s, 2), "t1": round(split, 2), "words": [w.lower() for w in small]})
        lines.append({"size": 112, "t0": round(split, 2), "t1": round(e, 2), "words": big})
        cards.append({"t_in": round(s, 2), "t_out": round(nxt, 2), "y": a.y, "lines": lines})
        print("  card %d  %5.2f-%5.2f  %-32s | %s" % (n + 1, s, e, " ".join(small), " ".join(big)))
    spec = {"_note": "DRAFT from kt.py plan. Check every card's words against the transcript "
                     "above, pick the keyword for each big line, mark italics/accents.",
            "offset": a.offset, "cx": 540, "cards": cards}
    json.dump(spec, open(a.out, "w"), indent=1)
    print("wrote", a.out, "- times are CLIP seconds; offset maps them onto the edit")


# --------------------------------------------------------------- scratch
def _probe(path):
    r = run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=width,height", "-of", "csv=p=0", path)
    w, h = [int(x) for x in r.stdout.strip().splitlines()[0].split(",")[:2]]
    return w, h


def _video_layer(asset, at, dur, src_in, w, h):
    s = 100.0 * 1080 / w                          # nothing is auto-fitted in Tesseract
    return {"type": "Video", "id": 1, "name": "clip", "blendMode": "normal",
            "activeRange": {"start": int(at * 1000), "duration": int(dur * 1000)},
            "sourceRange": {"start": int(src_in * 1000), "duration": int(dur * 1000)},
            "sourceIntrinsicDuration": int((src_in + dur) * 1000) + 1, "volume": 0.0,
            "transform": {"anchorPoint": [w / 2, h / 2], "position": [540, 960],
                          "scale": [s, s], "rotation": 0, "opacity": 100},
            "source": {"assetId": asset, "fit": "cover"}}


def _import_fonts(project):
    for f in kinetic.font_files():
        run(TS, "project", "import-font", "-p", project, "--file", f)


def cmd_proto(a):
    from PIL import Image
    d = tempfile.mkdtemp(); p = os.path.join(d, "p.tsrct")
    run(TS, "project", "create", "-p", p)
    run(TS, "project", "import-video", "-p", p, "--file", a.clip, "--asset-id", "clip")
    _import_fonts(p)
    w, h = _probe(a.clip)
    small, big = (a.text.split("|") + [""])[:2]
    tiles = []
    for y in a.y:
        lines = []
        if small.strip():
            lines.append({"size": 46, "t0": 0, "t1": 0, "words": small.split()})
        lines.append({"size": 112, "t0": 0, "t1": 0, "words": big.split()})
        L, _, _, warns = kinetic.card(100, 0, 2, lines, y=y)
        for x in warns: print("  note:", x)
        doc = {"$schema": "https://jerboa.dev/schemas/fx-composition/editable/v1/document.schema.json",
               "composition": {"id": "main", "name": "Main", "layers": L + [_video_layer("clip", 0, 2, a.at, w, h)]},
               "dimensions": {"width": 1080, "height": 1920}, "duration": 2.0, "formatVersion": 1}
        json.dump(doc, open(os.path.join(d, "e.json"), "w"))
        run(TS, "project", "commit", "-p", p, "--file", os.path.join(d, "e.json"))
        png = os.path.join(d, "y%d.png" % y)
        r = run(TS, "preview", "--project", p, "--time", "1.0", "--output", png)
        if not os.path.exists(png):
            sys.exit("preview failed: " + r.stdout + r.stderr)
        tiles.append(Image.open(png).resize((360, 640)))
    sheet = Image.new("RGB", (360 * len(tiles), 640))
    for i, t in enumerate(tiles): sheet.paste(t, (360 * i, 0))
    sheet.save(a.out); print("wrote", a.out, "  y =", a.y)


# ---------------------------------------------------------------- inject
def _max_id(layers):
    m = 0
    for l in layers:
        m = max(m, l.get("id", 0))
        if isinstance(l.get("layers"), list):
            m = max(m, _max_id(l["layers"]))
    return m


def cmd_build(a):
    spec = json.load(open(a.spec))
    _import_fonts(a.project)
    d = tempfile.mkdtemp(); co = os.path.join(d, "doc.json")
    r = run(TS, "project", "checkout", "-p", a.project, "--output", co)
    if not os.path.exists(co):
        sys.exit("checkout failed: " + r.stdout + r.stderr)
    doc = json.load(open(co))
    comp = doc["composition"]
    kept = [l for l in comp["layers"] if not str(l.get("name", "")).startswith("kt:")]
    dropped = len(comp["layers"]) - len(kept)
    start = max(_max_id(kept) + 1, 30000)
    L, K, W = kinetic.build(spec, start)
    for x in W: print("  note:", x)
    comp["layers"] = L + kept                     # layers[0] is frontmost: type on top
    end = max((l["activeRange"]["start"] + l["activeRange"]["duration"]) / 1000.0 for l in L)
    if end > doc["duration"]:
        print("  note: cards run to %.2fs, past the document's %.2fs; extending" % (end, doc["duration"]))
        doc["duration"] = round(end, 3)
    json.dump(doc, open(co, "w"))
    r = run(TS, "project", "commit", "-p", a.project, "--file", co)
    if r.returncode:
        sys.exit("commit failed: " + r.stdout + r.stderr)
    acts = os.path.join(d, "acts.json")
    json.dump(kinetic.motion_actions(K, composition=comp.get("id", "main")), open(acts, "w"))
    r = run(TS, "project", "apply", "-p", a.project, "--actions", acts)
    if r.returncode:
        sys.exit("apply failed: " + r.stdout + r.stderr)
    print("built %d words in %d cards (replaced %d earlier kt: layers)" % (len(L), len(spec["cards"]), dropped))


def cmd_check(a):
    from PIL import Image, ImageDraw
    spec = json.load(open(a.spec))
    d = tempfile.mkdtemp(); tiles = []
    for n, c in enumerate(spec["cards"]):
        off = c.get("offset", spec.get("offset", 0.0))
        last = max(l.get("t1", l.get("t0", c["t_in"])) for l in c["lines"]) + off
        t = min(last + 0.4, c["t_out"] + off - 0.05)
        png = os.path.join(d, "c%d.png" % n)
        r = run(TS, "preview", "--project", a.project, "--time", "%.3f" % t, "--output", png)
        if not os.path.exists(png):
            out = r.stdout + r.stderr
            sys.exit("preview failed at %.2fs: %s" % (t, out) +
                     ("\n(missing fonts: run build first, it imports them)" if "missing_fonts" in out else ""))
        im = Image.open(png).resize((360, 640)); ImageDraw.Draw(im).text((8, 8), "card %d  %.2fs" % (n + 1, t), fill="yellow")
        tiles.append(im)
    cols = min(4, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (360 * cols, 640 * rows))
    for i, t in enumerate(tiles): sheet.paste(t, (360 * (i % cols), 640 * (i // cols)))
    sheet.save(a.out); print("wrote", a.out, "- look at it: every big word clear of the face, nothing touching an edge")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("plan"); p.add_argument("clip"); p.add_argument("--offset", type=float, default=0.0)
    p.add_argument("--from", dest="src_from", type=float); p.add_argument("--to", dest="src_to", type=float)
    p.add_argument("--y", type=float, default=40); p.add_argument("--out", default="kinetic-spec.json")
    p = sp.add_parser("proto"); p.add_argument("clip"); p.add_argument("--at", type=float, default=1.0)
    p.add_argument("--text", required=True); p.add_argument("--y", type=float, nargs="+", default=[40, 1000, 1300])
    p.add_argument("--out", default="kinetic-proto.png")
    p = sp.add_parser("build"); p.add_argument("spec"); p.add_argument("--project", required=True)
    p = sp.add_parser("check"); p.add_argument("spec"); p.add_argument("--project", required=True)
    p.add_argument("--out", default="kinetic-check.png")
    a = ap.parse_args()
    {"plan": cmd_plan, "proto": cmd_proto, "build": cmd_build, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
