"""The legendary lairs' route entrance art (tilesets/lairs/entrances.png + entrances.json, made by make_entrances.py) on the route tilesets.

entrances.json carries the recipe source ("source": name `lent`, overlay-only: the pieces are drawn over whatever ground they stand on, magenta =
clear). A map asks for a piece by name ("lent:8_0" ...) from a spec "gates" cell (build.py gates(), story_data_lairs.py); the tilesets are
demand-driven, so a piece costs tiles only on the maps that place it. make_route_tilesets.py applies this to the shared route set (patch_base),
every variant copies it; `python tools/mapgen/lair_entrances_tileset.py` patches just the tilesets the entrances sit on, in place (idempotent).
Nothing here imports build.py.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "tilesets", "lairs", "entrances.json")
TS = os.path.join(HERE, "tilesets")
# the tilesets the six entrances stand on: Routes 7 and 11 (orleans_route), 14 (route_b), 16 (route_farm), 23 (route_dry); Route 2 uses primary pieces only
ON = ("orleans_route", "orleans_route_b", "orleans_route_dry", "orleans_route_farm")


def apply(r, c=None):
    """add (or refresh) the `lent` source in recipe r; True if it changed"""
    doc = json.load(open(ART, encoding="utf-8"))
    src = json.loads(json.dumps(doc["source"]))
    want = [src]
    if not any(s["name"] == "bd" for s in r["sources"]):
        # the swamp wall cells the entrances stand over (bd:swamp_W_marsh_0 ...) are pieces of the PRIMARY: this recipe needs their art to draw an overlay over
        # them, but must not place them as metatiles of its own (every map would pick the duplicates up, and seam bands allow primary pieces only): overlay_only
        gen = json.load(open(os.path.join(TS, "recipes", "orleans_general.json"), encoding="utf-8"))
        bd = [json.loads(json.dumps(x)) for x in gen["sources"] if x["name"] == "bd"][0]
        bd["overlay_only"] = True
        bd["_comment"] = "Border cells as overlay bases only (lair_entrances_tileset.py): never placed."
        want.insert(0, bd)
    have = {s["name"]: s for s in r["sources"]}
    if all(have.get(w["name"]) == w for w in want):
        return False
    r["sources"] = [s for s in r["sources"] if s["name"] not in {w["name"] for w in want}] + want
    return True


def main():
    for n in ON:
        p = os.path.join(TS, "recipes", n + ".json")
        r = json.load(open(p, encoding="utf-8"))
        if apply(r):
            with open(p + ".new", "w", encoding="utf-8", newline="\n") as f:
                json.dump(r, f, indent=1, ensure_ascii=False)
                f.write("\n")
            os.replace(p + ".new", p)
            print(n, ": lent source added")
        else:
            print(n, ": already has it")


if __name__ == "__main__":
    main()
