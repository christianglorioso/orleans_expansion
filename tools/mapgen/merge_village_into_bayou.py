"""Seams review (user decision 2026-10-14): Old Water, Isle Marais and Route 1 share gTileset_OrleansBayou, so the Old Water huts in
Route 1's seam band draw correctly from Route 1 (and Route 1's cells from Old Water).  Copies what Old Water needs from the village
tileset into the bayou recipe / config (idempotent):  python tools/mapgen/merge_village_into_bayou.py
then:  python tools/mapgen/settle.py old_water route_1 isle_marais   (build / compose / build)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "tilesets")


def load(p):
    return json.load(open(os.path.join(T, p), encoding="utf-8"))


def save(p, o):
    with open(os.path.join(T, p), "w", encoding="utf-8", newline="\n") as f:
        json.dump(o, f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    b, v = load("orleans_bayou.json"), load("orleans_village.json")
    rb, rv = load("recipes/orleans_bayou.json"), load("recipes/orleans_village.json")
    for s in rv["sources"]:
        if s["name"].startswith("rk_") and not any(x["name"] == s["name"] for x in rb["sources"]):
            rb["sources"].append(s)
    ev = next(s for s in rv["sources"] if s["name"] == "ekat")
    eb = next(s for s in rb["sources"] if s["name"] == "ekat")
    have = {m["id"] for m in eb["metatiles"]}
    eb["metatiles"] += [m for m in ev["metatiles"] if m["id"] not in have]
    pb = {p.get("id") for p in rb["patches"]}
    rb["patches"] += [p for p in rv["patches"] if p.get("id") not in pb and p.get("id", "").startswith(("hut", "song", "rk", "walk", "wv"))]
    for k, x in v["prefabs"].items():
        if k in ("hut", "songhouse") and k not in b["prefabs"]:
            b["prefabs"][k] = x
        elif k.startswith("walk_"):                       # Old Water's rope walkways are not Isle Marais's boardwalks: own names (old_water.json "prefab_map")
            b["prefabs"]["ow_" + k] = x
    b["variants"].update({k: x for k, x in v.get("variants", {}).items() if k not in b["variants"]})
    save("orleans_bayou.json", b)
    save("recipes/orleans_bayou.json", rb)


if __name__ == "__main__":
    main()
