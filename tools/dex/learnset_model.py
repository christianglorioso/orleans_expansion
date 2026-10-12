"""Turns the learnsets sheet into per-species data keyed by engine species constant, and maps species to the
level-up / egg / teachable array names used by the species blocks (read from the preprocessed view)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ppdata
import sheet_data as sd
import species_map as sm

SNAKIFY = re.compile(r"(?!^)([A-Z]+)")


def snake_key(pointer):
    """sFooBarTeachableLearnset -> FOO_BAR (the key used in all_learnables.json)"""
    m = re.match(r"s(\w+?)TeachableLearnset$", pointer)
    return SNAKIFY.sub(r"_\1", m.group(1)).upper()


def build():
    """returns list of dict(num, name, const, levelup[(lvl,MOVE)], tm[MOVE], tutor[MOVE], egg[MOVE], ptr_lv, ptr_tm, ptr_egg)"""
    mv = sd.load_move_names()
    L = sd.load_learnsets()
    t, ents = ppdata.load()
    cons = sm.species_consts()
    out = []
    for num, d in sorted(L.items()):
        name = d["name"]
        if name in sm.ORLEANIAN:
            const = sm.orleanian_const(name)
        else:
            const = sm.base_const(name, cons)
        f = ppdata.fields(ents[const])
        lv = [(lvl, mv[sd.norm(m)]) for lvl, m, pre, star, tag in d["levelup"] if not pre]
        lv.sort(key=lambda x: x[0])
        tm = [mv[sd.norm(m)] for m, pre, star in d["tm"] if not pre]
        tu = [mv[sd.norm(m)] for m, pre, star in d["tutor"] if not pre]
        egg = [mv[sd.norm(m)] for m, pre, star in d["egg"]]
        out.append(dict(num=num, name=name, const=const, levelup=lv, tm=tm, tutor=tu, egg=egg,
                        ptr_lv=f["levelUp"], ptr_tm=f["teach"], ptr_egg=f["egg"], natdex=f["natdex"]))
    return out


if __name__ == "__main__":
    rows = build()
    import collections
    for key in ("ptr_lv", "ptr_tm", "ptr_egg"):
        g = collections.defaultdict(list)
        for r in rows:
            g[r[key]].append(r)
        for p, rs in g.items():
            if len(rs) > 1 and p and "None" not in p:
                sig = {tuple(r["levelup"]) if key == "ptr_lv" else tuple(sorted(r["tm"] + r["tutor"])) if key == "ptr_tm" else tuple(r["egg"]) for r in rs}
                print(key, p, [r["name"] for r in rs], "CONFLICT" if len(sig) > 1 else "same")
