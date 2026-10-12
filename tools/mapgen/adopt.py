"""Let a town's tileset carry a neighbouring route's pieces, so the join between them has the SAME secondary tileset on both
sides (edges pass: the seam-band rule allows pieces that are identical in both maps' secondaries, and a shared tileset is the
strongest form of that: nothing in the band can garble, buildings and props included).

    adopt.apply(recipe, config, donors)     donors: tileset names whose recipe/config (tilesets/recipes/<d>.json, tilesets/<d>.json)
                                            are merged INTO the target: every source, patch, prefab, variant, terrain character
                                            and autotile the target does not already have. The tileset is demand-driven, so
                                            pieces no map places cost nothing.
    python tools/mapgen/adopt.py <target> <donor> [<donor> ...]      the same on the files of a hand-made tileset, in place
                                            (idempotent; the generated town variants call apply() from make_town_tilesets.py)

Where the target and a donor define the same name differently the target's wins and the clash is printed.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "tilesets")


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def apply(r, c, donors):
    clashes = []
    for d in donors:
        dr, dc = _load(os.path.join(TS, "recipes", d + ".json")), _load(os.path.join(TS, d + ".json"))
        have = {s["name"]: s for s in r["sources"]}
        for s in dr["sources"]:
            if s["name"] not in have:
                r["sources"].append(copy.deepcopy(s))
                have[s["name"]] = r["sources"][-1]
            else:
                t = have[s["name"]]
                if "metatiles" in s and "metatiles" in t and s.get("image") == t.get("image"):
                    ids = {m["id"] for m in t["metatiles"]}
                    t["metatiles"] += [copy.deepcopy(m) for m in s["metatiles"] if m["id"] not in ids]
                elif s.get("image") != t.get("image") or s.get("primary") != t.get("primary") or s.get("secondary") != t.get("secondary"):
                    clashes.append(f"source {s['name']}")
        ids = {p["id"] for p in r.get("patches", [])}
        r.setdefault("patches", [])
        r["patches"] += [copy.deepcopy(p) for p in dr.get("patches", []) if p["id"] not in ids]
        for key in ("prefabs", "variants", "terrain", "autotile"):
            for k, v in dc.get(key, {}).items():
                if k not in c.setdefault(key, {}):
                    c[key][k] = copy.deepcopy(v)
                elif c[key][k] != v and key in ("terrain", "autotile"):
                    clashes.append(f"{key} {k}")
    if clashes:
        print("adopt: the target's own definition kept for:", ", ".join(sorted(set(clashes))))
    return r, c


def main(args):
    target, donors = args[0], args[1:]
    rp, cp = os.path.join(TS, "recipes", target + ".json"), os.path.join(TS, target + ".json")
    r, c = _load(rp), _load(cp)
    apply(r, c, donors)
    for p, o in ((rp, r), (cp, c)):
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(o, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(f"{target}: now carries {', '.join(donors)}: {len(r['sources'])} sources, {len(r['patches'])} patches, "
          f"{len(c['prefabs'])} prefabs")


if __name__ == "__main__":
    main(sys.argv[1:])
