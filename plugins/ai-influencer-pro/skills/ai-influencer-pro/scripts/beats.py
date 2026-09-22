#!/usr/bin/env python3
"""beats.py <clip.mp4> [--floor -45] [--gap 0.25]

Print where the phrases actually start and stop, so captions can be cut on real speech
instead of on a guess.

ffmpeg's `silencedetect` is no use on these clips: Omni renders a continuous room tone, so
nothing ever crosses a silence threshold. This reads the RMS envelope instead and calls a
gap wherever the level drops well below the speaking level for long enough to be a breath.

Output is the beat list you paste into a plan's `beats`, plus the point where the throwaway
tail starts, which is where `duration` should end.
"""
import re, subprocess, sys, tempfile, os

def main():
    path = sys.argv[1]
    floor = float(sys.argv[sys.argv.index("--floor") + 1]) if "--floor" in sys.argv else -45.0
    min_gap = float(sys.argv[sys.argv.index("--gap") + 1]) if "--gap" in sys.argv else 0.25

    tmp = tempfile.mktemp(suffix=".txt")
    subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af",
                    f"astats=metadata=1:reset=1,ametadata=print:"
                    f"key=lavfi.astats.Overall.RMS_level:file={tmp}",
                    "-f", "null", "-"], capture_output=True)
    pairs = re.findall(r"pts_time:([0-9.]+)\n[^\n]*RMS_level=(-?[0-9.]+|-inf)",
                       open(tmp).read())
    os.remove(tmp)
    ser = [(float(t), -99.0 if v == "-inf" else float(v)) for t, v in pairs]
    if not ser:
        print("no audio"); sys.exit(1)

    loud = [v for _, v in ser if v > floor]
    speak = sum(loud) / len(loud) if loud else -30
    gate = max(floor, speak - 10)

    on = [(t, v > gate) for t, v in ser]
    runs, cur, start = [], on[0][1], on[0][0]
    for t, state in on[1:]:
        if state != cur:
            runs.append((start, t, cur)); cur, start = state, t
    runs.append((start, ser[-1][0], cur))

    phrases = [(a, b) for a, b, s in runs if s and b - a >= 0.18]
    merged = []
    for a, b in phrases:
        if merged and a - merged[-1][1] < min_gap:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))

    print(f"speaking level ~{speak:.1f} dB, gate {gate:.1f} dB, {len(merged)} phrases\n")
    for i, (a, b) in enumerate(merged, 1):
        print(f"  {i}.  {a:5.2f} -> {b:5.2f}   ({b-a:.2f}s)")
    gaps = [(merged[i][1], merged[i + 1][0]) for i in range(len(merged) - 1)]
    big = [(a, b) for a, b in gaps if b - a >= 0.35]
    if big:
        print("\ngaps worth cutting on:")
        for a, b in big:
            print(f"  {a:5.2f} -> {b:5.2f}   ({b-a:.2f}s of air)")
    # The throwaway tail sits after the LAST big gap, not after the last phrase: the tail
    # itself often breaks into two short runs and picking the last one cuts it in half.
    if big:
        cut = big[-1][0]
        print(f"\nif the audio after {big[-1][1]:.2f} is the throwaway tail, set duration to "
              f"about {cut + 0.13:.2f} so the hook ends on the real line.")


if __name__ == "__main__":
    main()
