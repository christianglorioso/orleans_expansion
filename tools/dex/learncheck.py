import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ppdata, learnset_model as lm
t, ents = ppdata.load()
lv = ppdata.levelup_sets(t)
tc = ppdata.move_sets(t, "TeachableLearnset")
eg = ppdata.move_sets(t, "EggMoveLearnset")
rows = lm.build()
bad = 0
for r in rows:
    p = r["ptr_lv"]
    if lv.get(p) is None:
        print("no array", r["name"], p); bad += 1; continue
    want = [(m, l) for l, m in r["levelup"]]
    if sorted(lv[p]) != sorted(want):
        bad += 1; print("LV mismatch", r["name"], len(lv[p]), len(want))
    tp = r["ptr_tm"]
    got = set(tc.get(tp, []))
    want_t = set(r["tm"]) | set(r["tutor"])
    # teachable should be sheet moves that are TM/HM/tutor in the build (all of them now)
    if got != want_t:
        bad += 1; print("TEACH mismatch", r["name"], len(got), len(want_t), sorted(want_t - got)[:5], sorted(got - want_t)[:5])
print("bad", bad, "of", len(rows))
