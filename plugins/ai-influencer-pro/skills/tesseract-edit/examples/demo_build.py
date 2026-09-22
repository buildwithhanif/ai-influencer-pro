import json, sys
sys.path.insert(0, sys.argv[1]); from tsx import Edit, ORANGE
A = json.load(open("assets.json"))
e = Edit()
# 1. Robyn, then she ducks to grey the instant he cuts in
e.ducked("robyn", [(0, 1.55, 1.0, None), (1.55, 1.75, 0.3, "robyngrey"), (1.75, 4.0, 0.06, "robyngrey")], A["robyn"])
e.captions("tiktok-box", [(0.30, 1.50, "I'm 61.")], offset=0, clip_start=0, clip_end=1.55)
pic, mat = e.keyed("hanifArgb", "hanifAmatte", 1.55, 2.45, 0.0, A["hanifArgb"], scale=75, pos=(250, 1840))
e.fade_in(pic, 220); e.fade_in(mat, 220)
# 2. swipe to Luca: Robyn and the cut-in scroll out together
l = e.clip("luca", 4.0, 2.15, 0.40, A["luca"])
e.swipe(l, 4.0, [{"asset": "robyngrey", "src_out": 4.0, "intrinsic": A["robyngrey"]},
                 {"asset": "hanifAmatte", "src_out": 2.45, "intrinsic": A["hanifAmatte"], "transform": e.tr(pos=(250, 1840), scale=75), "z": 10},
                 {"asset": "hanifArgb", "src_out": 2.45, "intrinsic": A["hanifArgb"], "transform": e.tr(pos=(250, 1840), scale=75), "z": 10, "matte": True}],
        sfx_asset="swipe", sfx_len_ms=A["swipe"])
e.captions("one-word", [(0.55, 2.39, "Everyone told me|to meal prep|on Sunday.")], offset=4.0 - 0.40, clip_start=4.0, clip_end=6.15, lead=0.18)
# 3. swipe to Marilou
m = e.clip("marilou", 6.15, 2.10, 0.0, A["marilou"], scale=115)
e.swipe(m, 6.15, [{"asset": "luca", "src_out": 2.55, "intrinsic": A["luca"]}], sfx_asset="swipe", sfx_len_ms=A["swipe"])
e.captions("lowercase", [(0.11, 1.96, "Three years|of night shifts|taught me one thing.")], offset=6.15, clip_start=6.15, clip_end=8.25, lead=0.18)
# 4. end card
e.fill(8.25, 2.0, z=40)
t = e.text("Fully automated.", 8.35, 1.9, 92, 860, color=ORANGE, z=41); e.fade_in(t, 260)
print(e.save("edit.json", "motion.json"))
