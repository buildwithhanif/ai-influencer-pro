#!/usr/bin/env python3
"""script-plan.py <script.md> [--storyboard sb.md] [--episode ep.json] [--trims trim.sh]
                  [--scene scene.txt] [--rules rules.txt] [--character NAME]
                  [--project URL] [--wps 2.9] [--out DIR]

Turn a written script into shots that are already the right length.

Omni renders 4, 6, 8 or 10 seconds and nothing in between, so every line lands in one of three
states: it fits, it gets cut off, or it gets drawled out to fill the slot. The fix from the
workflow is to pad the line with throwaway words, render at the longer duration, and cut the
padding off in the edit. That is arithmetic, so it should not be done by feel at 1am.

This does the arithmetic, picks the stressed word, writes the storyboard, writes the episode JSON
that flow.mjs consumes, and writes a shell script of the exact ffmpeg trims for the padded clips.

SCRIPT FORMAT
  # Title                     ignored, used as the episode name
  ## hook                     a section. Sections are only labels, except:
  ## scene: kitchen, later    a scene change. Everything after it gets scene index 2, 3, ...
  One line of dialogue.       one line = one shot. Never two lines in one shot.
  Put *stars* around a word   to force the stressed word. Otherwise it is picked for you.
  > note to self              ignored

TIMING
  Default 2.9 words/sec, which is high-energy UGC delivery. Slow it to 2.4 for a calm character.
  Syllables are counted, not just words, so "authorisation" costs what it should. Commas and full
  stops add a beat, because a real person breathes.

  Verify it once against your own character: render one line, time the result, adjust --wps. The
  number is a starting point, not physics.
"""
import json, os, re, sys

DURATIONS = [4, 6, 8, 10]
STOP = set("""a an and are as at be been but by can could did do does for from get got had has have
he her him his how i if in is it its just like me my no not of on or our out said say she so some
than that the their them then there these they this to too up us was we were what when which who
will with would you your it's i'm don't that's""".split())
# Cut-me-first words. They carry no information, so losing them in the edit costs nothing.
PADDING = ["anyway", "you know", "seriously", "okay so", "right", "that's it", "trust me",
           "for real", "every time", "honestly"]


def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    return max(1, n)


def estimate(line, wps):
    """Seconds this line takes to say. Syllable-driven, with a beat for each piece of punctuation."""
    words = re.findall(r"[A-Za-z']+", line)
    syl = sum(syllables(w) for w in words)
    sps = wps * 1.45                       # ~1.45 syllables per word in spoken English
    beats = len(re.findall(r"[,;:]", line)) * 0.18 + len(re.findall(r"[.!?]", line)) * 0.30
    return round(syl / sps + beats + 0.25, 2)   # 0.25 s of lead-in before the first word


def pick_stress(line):
    """The word the delivery should lean on. Explicit *stars* win; otherwise the longest content
    word in the second half of the line, because that is usually where the new information is."""
    m = re.search(r"\*([A-Za-z'-]+)\*", line)
    if m:
        return m.group(1)
    words = re.findall(r"[A-Za-z'-]+", line)
    if not words:
        return None
    tail = words[len(words) // 2:] or words
    content = [w for w in tail if w.lower() not in STOP and len(w) > 3]
    return max(content or tail, key=len)


def apply_stress(line, word):
    line = line.replace(f"*{word}*", word)
    if not word:
        return line
    return re.sub(rf"\b{re.escape(word)}\b", word.upper(), line, count=1)


def pad_for(gap, wps, start=0):
    """Enough throwaway words to fill `gap` seconds. `start` rotates the bank so every shot in a
    season does not end with the same word."""
    out, got, i = [], 0.0, 0
    while got < gap - 0.15 and i < len(PADDING):
        out.append(PADDING[(start + i) % len(PADDING)])
        got = estimate(" ".join(out), wps) - 0.25
        i += 1
    return " ".join(out), round(got, 2)


def parse(path):
    section, scene, shots = "body", 1, []
    title = os.path.splitext(os.path.basename(path))[0]
    for raw in open(path):
        line = raw.strip()
        if not line or line.startswith(">"):
            continue
        if line.startswith("# "):
            title = line[2:].strip(); continue
        if line.startswith("## "):
            head = line[3:].strip()
            if head.lower().startswith("scene"):
                scene += 1
                section = head.split(":", 1)[1].strip() if ":" in head else f"scene {scene}"
            else:
                section = head
            continue
        if line.startswith("#"):
            continue
        shots.append({"section": section, "scene": scene, "line": line})
    return title, shots


def plan(shots, wps):
    for i, s in enumerate(shots, 1):
        est = estimate(s["line"], wps)
        stress = pick_stress(s["line"])
        spoken = apply_stress(s["line"], stress)

        if est > DURATIONS[-1]:
            s.update(id=f"{i:02d}", est=est, seconds=DURATIONS[-1], stress=stress, spoken=spoken,
                     pad="", trim=None,
                     warn=f"{est}s is longer than the {DURATIONS[-1]}s ceiling. Split this line.")
            continue

        upper = next(d for d in DURATIONS if d >= est)
        lower = max([d for d in DURATIONS if d <= est], default=None)
        gap = round(upper - est, 2)
        pad, trim = "", None
        # Padding is only for a line that sits BETWEEN two slots, which is the case the workflow
        # describes. A line shorter than the 4 s floor has no lower slot to be cut off by: it just
        # gets a beat of silence at the end, and that is fine.
        if lower is not None and gap >= 0.6:
            pad, _ = pad_for(gap, wps, start=i)
            trim = round(est + 0.15, 2)
        s.update(id=f"{i:02d}", est=est, seconds=upper, stress=stress, spoken=spoken,
                 pad=pad, trim=trim, warn=None)
        if pad:
            # Drop the line's final stop so the model reads the padding as part of the same
            # breath. A full stop makes it pause, and the pause is what eats the slot.
            s["spoken_padded"] = f"{spoken.rstrip('.').rstrip()}, {pad}."
    return shots


def storyboard(title, shots):
    out = [f"# {title}", "",
           "Left is what is said, right is what is on screen. Where the character's face is on "
           "screen it just says AI UGC, same as the source workflow. THE CAPITALISED WORD is the "
           "one the delivery leans on; change it in the script with *stars*.", ""]
    sect = None
    for s in shots:
        if s["section"] != sect:
            sect = s["section"]
            out += ["", f"## {sect}", "",
                    "| # | line | on screen | len |", "|---|---|---|---|"]
        visual = "AI UGC" if s["scene"] == 1 else f"AI UGC, scene {s['scene']}"
        pad = " +pad" if s["pad"] else ""
        out.append(f"| {s['id']} | {s['spoken']} | {visual} | {s['seconds']}s{pad} |")
    out += ["", "Total spoken: %.1fs across %d shots."
            % (sum(x["est"] for x in shots), len(shots)), ""]
    return "\n".join(out)


def episode(title, shots, opt):
    scene = opt.get("scene", "[SCENE PARAGRAPH: camera movement stated, camera/shot type, where the "
                             "character is, what they are doing, energy. Same room as the reference.]")
    rules = opt.get("rules", "One continuous take, no jump cuts, no camera movement, no text on "
                             "screen, confident pace, natural pauses.")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:24]
    ep = {
        "project": opt.get("project", "https://flow.google.com/project/<your-project-id>"),
        "character": opt.get("character", "<Character name as registered in Flow>"),
        "model": "Omni 1.1 Flash", "ratio": "9:16", "resolution": "720p",
        "count": 2, "quality": "1080p",
        "out": opt.get("out", f"./episodes/{slug}/clips"),
        "shots": [],
    }
    for s in shots:
        said = s.get("spoken_padded", s["spoken"])
        ep["shots"].append({
            "id": f"{slug}-{s['id']}",
            "seconds": s["seconds"],
            "scene": s["scene"],
            "trim": s["trim"],
            "prompt": f"{scene}\n\nShe says: \"{said}\"\n\n{rules}",
        })
    return ep


def trims(ep):
    out = ["#!/bin/sh", "# Cut the throwaway padding off the tail of each padded clip.",
           "# Written by script-plan.py. Re-encodes, because cutting on a keyframe would drift.", "set -e", ""]
    n = 0
    for s in ep["shots"]:
        if s["trim"]:
            n += 1
            out.append(f'ffmpeg -y -v error -i "{s["id"]}.mp4" -t {s["trim"]} '
                       f'-c:v libx264 -crf 18 -preset veryfast -c:a aac "{s["id"]}-trim.mp4"')
    out.append("" if n else "# nothing needed trimming")
    return "\n".join(out) + "\n"


def main():
    args, opt, pos = sys.argv[1:], {}, []
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                print(f"{args[i]} needs a value"); sys.exit(2)
            opt[args[i][2:]] = args[i + 1]; i += 2
        else:
            pos.append(args[i]); i += 1
    if not pos:
        print(__doc__); sys.exit(2)

    wps = float(opt.get("wps", 2.9))
    for k in ("scene", "rules"):
        if k in opt and os.path.exists(opt[k]):
            opt[k] = open(opt[k]).read().strip()

    title, shots = parse(pos[0])
    if not shots:
        print("no dialogue lines found"); sys.exit(2)
    shots = plan(shots, wps)

    print(f"{title}   {len(shots)} shots, {wps} words/sec\n")
    print(f"{'#':>3} {'est':>5} {'->':>3} {'pad':>4} {'trim':>5}  stress        line")
    credits = 0
    for s in shots:
        credits += 12 * (s["seconds"] / 8)
        print(f"{s['id']:>3} {s['est']:>5} {s['seconds']:>3} "
              f"{'yes' if s['pad'] else '-':>4} {str(s['trim'] or '-'):>5}  "
              f"{(s['stress'] or '-')[:12]:<12}  {s['line'][:58]}")
        if s["warn"]:
            print(f"      !! {s['warn']}")
        if s["pad"]:
            print(f"      +  \"{s['pad']}\"  then cut at {s['trim']}s")
    total = sum(s["est"] for s in shots)
    print(f"\nspoken {total:.1f}s, rendered {sum(s['seconds'] for s in shots)}s, "
          f"about {round(credits)} credits on Pro at 12 per 8s clip")

    ep = episode(title, shots, opt)
    if "storyboard" in opt:
        open(opt["storyboard"], "w").write(storyboard(title, shots))
        print("wrote", opt["storyboard"])
    if "episode" in opt:
        json.dump(ep, open(opt["episode"], "w"), indent=1)
        print("wrote", opt["episode"])
    if "trims" in opt:
        open(opt["trims"], "w").write(trims(ep))
        os.chmod(opt["trims"], 0o755)
        print("wrote", opt["trims"])


if __name__ == "__main__":
    main()
