"""Grand Oak's tileset (orleans_town) brought up to the current pipeline: demand-driven (compose keeps only what
maps/grand_oak.json places), palette v2 (never "v2_backdrop"), plus the pieces the polish pass added.

    flowers  the town's red flower (HnS Johto primary 004, the old `flowers` prefab) in five more colours: the same tile
             recoloured per source (pink, violet, blue, white, yellow: each flower's two reds, its highlight and its
             centre are swapped), so the loose flowers can be beds and borders of every colour in one style. One prefab
             each (bloom_<colour>, walkable). Hand-drawn replacements: art_requests/grand_oak.md.
    sign     a wooden signpost (primary 003, blocking) so the town sign can be read from the street.

usage (from the decomp root): python tools/mapgen/grand_oak_tileset.py     (rewrites tilesets/orleans_town.json and
tilesets/recipes/orleans_town.json; idempotent; grand_oak.py calls it too)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "tilesets")

# the red flower's colours in the Johto source: two reds, two highlights, the yellow centre
RED = [[192, 48, 64], [200, 56, 72]]
HIGH = [[232, 128, 104], [232, 136, 104]]
CENTRE = [248, 192, 112]
# colour -> (dark, light, highlight, centre)
COLOURS = {
    "pink": ([208, 80, 136], [224, 96, 152], [248, 176, 208], [248, 192, 112]),
    "violet": ([96, 64, 160], [112, 80, 176], [176, 152, 232], [248, 216, 120]),
    "blue": ([48, 88, 184], [64, 104, 200], [136, 184, 248], [248, 200, 112]),
    "white": ([208, 208, 200], [232, 232, 224], [248, 248, 240], [232, 160, 56]),
    "yellow": ([216, 152, 24], [240, 184, 40], [248, 232, 136], [232, 112, 40]),
}
GROUND = [[120, 160, 104], [104, 144, 96], [110, 146, 100], [136, 176, 128], [140, 178, 131], [122, 172, 130],
          [149, 190, 157], [96, 128, 88]]


def apply(r, c):
    r["demand"] = True
    r["palette"] = "v2"
    r.pop("v2_backdrop", None)
    for s in r["sources"]:     # art that is only ever drawn over terrain: never composed as raw metatiles
        if s["name"] in ("gh", "mag", "pl"):
            s["overlay_only"] = True
    r["sources"] = [s for s in r["sources"] if s["name"] not in ("blm",) and not s["name"].startswith("jfl_")]
    r["patches"] = [p for p in r["patches"] if not p.get("id", "").startswith("fl_")]
    P = c["prefabs"]
    for k in [k for k in P if k.startswith("bloom_")]:
        del P[k]
    for name, (dark, light, high, centre) in COLOURS.items():
        r["sources"].append({"name": f"jfl_{name}", "primary": "johto_general_hns", "secondary": "azalea_town_hns",
                             "layout": "frlg", "pick_only_for_patches": True,
                             "recolor": [[RED[0], dark], [RED[1], light], [HIGH[0], high], [HIGH[1], high],
                                         [CENTRE, centre]]})
        r["patches"].append({"id": f"fl_{name}", "reseat": f"jfl_{name}:004", "base": "ekat:grass", "colors": GROUND,
                             "behavior": "MB_NORMAL"})
        P[f"bloom_{name}"] = {"_comment": f"The red flower in {name} (same tile, recoloured), 1x1, walkable.",
                              "rows": [[f"patch:fl_{name}"]], "passable": [[0, 0]]}
    P["sign"] = {"_comment": "Wooden signpost (primary 003), blocking.", "rows": [["003"]]}
    # flowers in the fountain's top row, behind its spray (user, 2026-10-12: tiles (29,9) and (30,9)): the fountain's top
    # tiles with their grass cut away, drawn over a red and a violet flower (mirroring the violet/red pair below it)
    r["patches"] = [p for p in r["patches"] if not p.get("id", "").startswith("fnt_fl")]
    r["patches"] += [{"id": "fnt_fl_l", "reseat": "np:2A0", "base": "patch:peppers", "colors": GROUND, "merge_base": True},
                     {"id": "fnt_fl_r", "reseat": "np:2A1", "base": "patch:fl_violet", "colors": GROUND, "merge_base": True}]
    if "fountain" in P:
        P["fountain"]["rows"][0] = ["patch:fnt_fl_l", "patch:fnt_fl_r"]


def main():
    rp, cp = os.path.join(TS, "recipes", "orleans_town.json"), os.path.join(TS, "orleans_town.json")
    r, c = (json.load(open(p, encoding="utf-8")) for p in (rp, cp))
    apply(r, c)
    for p, o in ((rp, r), (cp, c)):
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            json.dump(o, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print("orleans_town: demand + palette v2; prefabs", sorted(c["prefabs"]))


if __name__ == "__main__":
    main()
