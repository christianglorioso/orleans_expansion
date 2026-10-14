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


ORPHAN_EGG = []   # (sheet name, hatch species const) when a family's hatchable base species is not a sheet row


def _family_root_fn(t, ents):
    """Returns root(const): the species an egg of that species' family hatches as. Mirrors the engine's
    GetSpeciesPreEvolution (src/pokemon.c): the species whose evolution list names it, else (alternate forms such as
    Alolan Raichu whose base form is the one named) the pre-evolution of the form table's base species."""
    pre = {}
    for k, body in ents.items():
        i = body.find(".evolutions =")
        if i < 0:
            continue
        j = body.find("{ 0xFFFF }", i)
        for m in re.finditer(r"SPECIES_\w+", body[i:j]):
            pre.setdefault(m.group(), k)
    tables = {m.group(1): re.findall(r"SPECIES_\w+", m.group(2))
              for m in re.finditer(r"static const u16 (\w+FormSpeciesIdTable)\[\] = \{(.*?)\};", t, re.S)}
    base = {}
    for k, body in ents.items():
        m = re.search(r"\.formSpeciesIdTable = (\w+)", body)
        if m and m.group(1) in tables:
            base[k] = tables[m.group(1)][0]

    def pre_of(c, depth=0):
        if c in pre:
            return pre[c]
        if c in base and base[c] != c and depth < 3:
            return pre_of(base[c], depth + 1)
        return None

    def root(c):
        for _ in range(6):
            p = pre_of(c)
            if p is None:
                break
            c = p
        return c
    return root


def build():
    """returns list of dict(num, name, const, levelup[(lvl,MOVE)], tm[MOVE], tutor[MOVE], egg[MOVE], ptr_lv, ptr_tm, ptr_egg,
    egg_own[MOVE] (what the sheet lists on this very row), egg_root (hatch species const), egg_from [names])

    Egg moves only matter on the species that hatches (the family's base species), so `egg` of a family's base
    species is the union of the sheet's egg moves over every member of the family (Roselia/Roserade -> Budew);
    every other row keeps just what the sheet lists on it."""
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
                        ptr_lv=f["levelUp"], ptr_tm=f["teach"], ptr_egg=f["egg"], natdex=f["natdex"],
                        egg_own=list(egg), egg_root=const, egg_from=[]))
    root = _family_root_fn(t, ents)
    byc = {r["const"]: r for r in out}
    ORPHAN_EGG.clear()
    for r in out:
        rt = root(r["const"])
        r["egg_root"] = rt
        if rt == r["const"] or not r["egg_own"]:
            continue
        if rt not in byc:
            ORPHAN_EGG.append((r["name"], rt))
            continue
        tgt = byc[rt]
        extra = [m for m in r["egg_own"] if m not in tgt["egg"]]
        if extra:
            tgt["egg"] = tgt["egg"] + extra
            tgt["egg_from"].append(r["name"])
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
