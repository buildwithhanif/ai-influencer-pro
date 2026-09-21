#!/usr/bin/env python3
"""qc.py <clip.mp4 | dir> [...] [--episode ep.json] [--scene 0.35] [--json qc.json]

Judge the renders harshly, mechanically, before you spend another credit.

The workflow says to be harsh on the first render and turn every complaint into a fixed rule.
Most of the complaints are things a machine can see faster than you can: the model cut to a second
angle when you told it one take, the last second is a frozen frame, the audio came back silent,
the clip is a second shorter than the slot you paid for. Those are what this checks. Whether the
energy is right and whether she looks like a person is still your job.

CHECKS
  duration    against --episode if given, otherwise just reported. A clip more than 0.35 s short
              of its slot usually means the line got cut off.
  jump cut    scene-change detection inside the clip. You asked for one continuous take, so ANY
              hard cut is a failure. Threshold with --scene; 0.35 is deliberately strict, a real
              cut scores well above it and a head turn well below.
  freeze      a held frame of 0.8 s or more. Omni does this at the tail when the line ends early.
  black       black frames anywhere.
  audio       stream present, and mean volume above -45 dBFS so a silent render gets caught.
  format      width, height, fps, reported so a 720p clip in a 1080p batch stands out.

Needs ffmpeg and ffprobe on PATH. Exit 0 if every clip passes, 1 otherwise.
"""
import json, os, re, subprocess, sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    # metadata=print:file=- goes to STDOUT while every other ffmpeg log goes to stderr.
    # Read both or scene changes come back empty and every clip looks clean.
    return r.stdout + r.stderr


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height,r_frame_rate",
         "-of", "json", path], capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
    except json.JSONDecodeError:
        return None
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
    fps = round(float(num) / float(den or 1), 2) if float(den or 1) else 0
    return {"dur": round(float(d.get("format", {}).get("duration", 0)), 2),
            "w": v.get("width"), "h": v.get("height"), "fps": fps, "audio": a is not None}


def cuts(path, thresh):
    err = run(["ffmpeg", "-v", "info", "-i", path, "-an",
               "-vf", f"select='gt(scene,{thresh})',metadata=print:file=-",
               "-f", "null", "-"])
    return [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", err)]


def defects(path):
    err = run(["ffmpeg", "-v", "info", "-i", path, "-an",
               "-vf", "blackdetect=d=0.25:pic_th=0.98,freezedetect=n=0.002:d=0.8",
               "-f", "null", "-"])
    return ([round(float(t), 2) for t in re.findall(r"black_start:([0-9.]+)", err)],
            [round(float(t), 2) for t in re.findall(r"freeze_start: ?([0-9.]+)", err)])


def loudness(path):
    err = run(["ffmpeg", "-v", "info", "-i", path, "-vn", "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"mean_volume: (-?[0-9.]+) dB", err)
    return float(m.group(1)) if m else None


def check(path, want=None, thresh=0.35):
    p = probe(path)
    if not p:
        return {"file": path, "verdict": "FAIL", "notes": ["ffprobe could not read this file"]}
    black, freeze = defects(path)
    r = dict(p, file=path, cuts=cuts(path, thresh), black=black, freeze=freeze,
             mean_db=loudness(path) if p["audio"] else None)

    notes = []
    if want:
        short = round(want - r["dur"], 2)
        if short > 0.35:
            notes.append(f'{r["dur"]}s against a {want}s slot, {short}s short: the line was cut off, '
                         'or Flow returned the wrong duration')
        elif short < -0.35:
            notes.append(f'{r["dur"]}s against a {want}s slot, longer than asked for')
    if r["cuts"]:
        notes.append(f'jump cut at {r["cuts"]}s. You asked for one continuous take. Add "one '
                     'continuous take, no jump cuts" to the fixed rules and regenerate')
    if r["freeze"]:
        notes.append(f'frozen frame from {r["freeze"][0]}s. The line ended early and Omni held the '
                     'last frame: shorten the slot or pad the line')
    if r["black"]:
        notes.append(f'black frames at {r["black"]}s')
    if not r["audio"]:
        notes.append('no audio stream at all')
    elif r["mean_db"] is not None and r["mean_db"] < -45:
        notes.append(f'mean volume {r["mean_db"]} dB, effectively silent')

    r["notes"] = notes
    r["verdict"] = "FAIL" if notes else "PASS"
    return r


def main():
    args, opt, paths = sys.argv[1:], {}, []
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print(f"{args[i]} needs a value"); sys.exit(2)
            opt[args[i][2:]] = args[i + 1]; i += 2
        else:
            paths.append(args[i]); i += 1
    if not paths:
        print(__doc__); sys.exit(2)

    want = {}
    if "episode" in opt:
        for s in json.load(open(opt["episode"]))["shots"]:
            want[s["id"]] = s.get("seconds")

    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if f.lower().endswith((".mp4", ".mov", ".webm"))]
        else:
            files.append(p)
    if not files:
        print("no clips found"); sys.exit(2)

    thresh = float(opt.get("scene", 0.35))
    results = [check(f, want.get(os.path.splitext(os.path.basename(f))[0]), thresh) for f in files]

    print(f"{'verdict':<8} {'dur':>6} {'want':>5} {'size':>11} {'fps':>5} {'dB':>7}  file")
    for r in results:
        w = want.get(os.path.splitext(os.path.basename(r['file']))[0])
        size = f"{r.get('w')}x{r.get('h')}" if r.get("w") else "?"
        print(f"{r['verdict']:<8} {r.get('dur', 0):>6} {str(w or '-'):>5} {size:>11} "
              f"{r.get('fps', 0):>5} {str(r.get('mean_db') if r.get('mean_db') is not None else '-'):>7}"
              f"  {os.path.basename(r['file'])}")
    print()
    for r in results:
        if r["notes"]:
            print(os.path.basename(r["file"]))
            for n in r["notes"]:
                print("   -", n)

    if "json" in opt:
        json.dump(results, open(opt["json"], "w"), indent=1)
        print("\nwrote", opt["json"])

    sys.exit(0 if all(r["verdict"] == "PASS" for r in results) else 1)


if __name__ == "__main__":
    main()
