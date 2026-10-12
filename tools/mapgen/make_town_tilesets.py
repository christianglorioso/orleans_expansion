"""Per-town secondary tilesets: the harbour base (swamp terrain, docks, cypress, Pokémon Center, Mart) plus each
town's own buildings, so every town gets thematic landmarks without overflowing one shared 512-tile set.

    orleans_harbor   Land's End: own-art stilt houses, boardwalk, pavilion and landmarks (lands_end_tileset.py), trawler stand-ins
    orleans_camp     Camp Cocodrie: own-art boardwalk, stilt cabins and camp buildings (camp_tileset.py), the barn, the airboat, magnolias
    orleans_hollow   Lutin's Hollow: own-art glade pieces (hollow_tileset.py), cabins and magnolias as stand-ins
    orleans_port     Storm's Edge: no barn; Brick City shop and hall, and our own lighthouse
    orleans_capital  Redfield (redfield.py, redfield_tileset.py): dry-country terrain and own art, the barn, Brick City shop and row building as stand-ins
    orleans_crescent Crescent City: Brick City throughout (houses, shops, gables, hall, row building, church)

Brick City building layouts were recovered by matching its example map (sources/brick_city/example.png)
cell by cell against the tileset; the ids below are the source tileset's.

usage (from the decomp root): python tools/mapgen/make_town_tilesets.py [variant ...]
writes tilesets/recipes/<variant>.json and tilesets/<variant>.json; then compose each with --register.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "tilesets")

D = "patch:brick_door"  # the house door: brick:362 given a door behaviour
B = lambda *ids: [f"brick:{i}" if i not in (None, D) and not i.startswith("patch:") else i for i in ids]

BRICK = {
    "brick_house": {"_comment": "Brick City house, 5x5.", "door": [2, 4], "rows": [
        B("220", "221", "221", "221", "223"), B("228", "229", "229", "229", "237"), B("22A", "22B", "22B", "22B", "233"),
        B("238", "239", "227", "23B", "216"), B("240", "230", D, "231", "243")]},
    "brick_shop": {"_comment": "Brick City shopfront, 6x5: a display window right of the door.", "door": [1, 4], "rows": [
        B("220", "221", "221", "221", "221", "223"), B("228", "229", "229", "229", "229", "237"),
        B("22A", "22B", "22B", "22B", "22B", "233"), B("232", "227", "23C", "204", "206", "217"),
        B("248", D, "244", "20C", "20E", "21F")]},
    "brick_gable": {"_comment": "Brick City narrow gable house, 4x7.", "door": [1, 6], "rows": [
        [None, "patch:gable_328", "patch:gable_32B", None], ["patch:gable_31C", "brick:319", "brick:31A", "patch:gable_323"], B("330", "318", "31B", "333"),
        B("331", "2B2", "2B3", "332"), B("340", "28B", "2AB", "32E"), B("232", "227", "25D", "29A"), B("248", D, "231", "243")]},
    "brick_round": {"_comment": "Brick City house with round attic windows, 5x6.", "door": [2, 5], "rows": [
        B("220", "221", "221", "221", "223"), B("228", "229", "229", "229", "237"), B("22A", "22B", "22B", "22B", "233"),
        B("238", "2B1", "23A", "2B1", "216"), B("238", "239", "227", "23B", "216"), B("240", "230", D, "231", "243")]},
    "brick_hall": {"_comment": "Brick City hall, 10x9: arched porch entrance with steps.", "door": [4, 7], "rows": [
        B("220", *["221"] * 8, "223"), B("228", *["229"] * 8, "237"), B("22A", *["22B"] * 8, "233"),
        B("238", "293", "294", "23A", "293", "294", "23A", "293", "294", "216"),
        B("238", "29B", "29C", "23A", "29B", "29C", "23A", "29B", "29C", "216"),
        B("238", "246", "247", "23A", "246", "247", "23A", "246", "247", "216"),
        B("280", "284", "260", "2AC", "2AD", "2AE", "203", "207", "202", "216"),
        B("281", "28A", "2A6", "2B4", "patch:hall_door", "2B6", "20B", "20F", "20A", "243"),
        [None, None, None, "patch:hall_step_l", "patch:hall_step", "patch:hall_step_r", None, None, None, None]],
        "passable": [[3, 8], [4, 8], [5, 8]]},
    "brick_row": {"_comment": "Brick City row building, 9x6: the left door opens, the right one is a shut side door.", "door": [2, 5], "rows": [
        B("220", *["221"] * 7, "223"), B("228", *["229"] * 7, "237"), B("22A", *["22B"] * 7, "233"),
        B("238", "260", "23A", "23A", "260", "23A", "23A", "260", "216"),
        B("238", "250", "227", "23B", "2AF", "239", "227", "258", "216"),
        B("240", "230", D, "231", "241", "230", "362", "231", "243")]},
}
CHURCH_IDS = ["319", "31A", "321", "318", "31B", "322", "314", "2B0", "2B8", "338", "339", "23A", "33A", "332", "224",
              "227", "343", "248", "362", "243"]
BRICK_PATCHES = [
    {"id": "brick_door", "lower": "brick:362", "behavior": "MB_NON_ANIMATED_DOOR"},
    {"id": "hall_door", "lower": "brick:2B5", "behavior": "MB_NON_ANIMATED_DOOR"},
    {"id": "hall_step_l", "lower": "ekat:grass", "upper": "brick:2BC"},
    {"id": "hall_step", "lower": "ekat:grass", "upper": "brick:2BD"},
    {"id": "hall_step_r", "lower": "ekat:grass", "upper": "brick:2BE"},
    {"id": "gable_328", "lower": "ekat:grass", "upper": "brick:328"},
    {"id": "gable_32B", "lower": "ekat:grass", "upper": "brick:32B"},
    {"id": "gable_31C", "lower": "ekat:grass", "upper": "brick:31C"},
    {"id": "gable_323", "lower": "ekat:grass", "upper": "brick:323"},
]


def lighthouse():
    cells = [{"id": f"{x}{y}", "bottom": [x, y]} for y in range(6) for x in range(3)]
    src = {"name": "lh", "type": "image", "image": "tools/mapgen/sources/orleans_custom/lighthouse.png",
           "transparent": [[255, 0, 255]], "_comment": "Our own art (make_lighthouse.py), overlaid on terrain.", "overlay_only": True,
           "metatiles": cells}
    rows = [[{"overlay": f"lh:{x}{y}", **({"behavior": "MB_NON_ANIMATED_DOOR"} if (x, y) == (1, 5) else {})}
             for x in range(3)] for y in range(6)]
    return src, {"_comment": "Storm's Edge lighthouse (own art), 3x6, overlaid on the ground.", "rows": rows,
                 "door": [1, 5]}


# pieces a town can do without: (source or patch prefix, ids) and the prefabs that use them
HOUSES = [("shady", ["24E", "24F", "256", "257", "25E", "25F", "266", "267", "26E", "26F"], ["house_a", "house_b"])]
KNEES = [("ekat", ["knees_00", "knees_10", "knees_20", "knees_01", "knees_11"], ["knees"])]
BOAT = [("patch", ["boat_"], ["boat"])]
MART = [("vgen", ["028", "029", "02A", "02B", "030", "031", "032", "033", "038", "039", "03A", "03B", "040", "041",
                  "042", "043"], ["mart"]), ("patch", ["mart_door"], [])]
MUD = [("ekat", [f"{t}_{s}" for t in ("mud", "mudwater") for s in
                 ("N", "S", "W", "E", "C", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW", "landNE", "landNW",
                  "landSE2", "landSW2", "landNE2", "landNW2", "plants3", "sTLBR", "sTRBL")], [])]


PROP_CELLS = {"bench": {"bench_0": (0, 0), "bench_1": (1, 0)}, "lamp": {"lamp_top": (2, 0), "lamp_post": (2, 1)},
              "planter": {"planter_0": (3, 1), "planter_1": (4, 1)}, "barrel": {"barrel": (5, 1)},
              "crates": {"crates": (6, 1)}, "trap": {"trap": (7, 1)}}


def extras(want=("bench", "lamp", "planter", "barrel", "crates", "trap", "magnolia")):
    """Lived-in town pieces (own art): street furniture and props, magnolias, and the railed road bridge
    (docks() in firstpass.py lays bridges from its cells). `want`: which props this town gets."""
    props = {k: v for p in want if p in PROP_CELLS for k, v in PROP_CELLS[p].items()}
    sources = [
        {"name": "props", "type": "image", "image": "tools/mapgen/sources/orleans_custom/props.png",
         "transparent": [[255, 0, 255]], "_comment": "Our own street furniture and props (make_props.py), overlays.", "overlay_only": True,
         "metatiles": [{"id": k, "bottom": list(v)} for k, v in props.items()]},
        {"name": "brg", "type": "image", "image": "tools/mapgen/sources/orleans_custom/bridge.png",
         "transparent": [[255, 0, 255]], "_comment": "Our own railed road bridge (make_bridge.py).",
         "metatiles": [{"id": f"{x}{y}", "bottom": [x, y]} for x, y in
                       [(x, y) for y in range(4) for x in range(3)] + [(x, y) for y in range(3) for x in range(3, 7)]]},
    ] + ([{"name": "mag", "type": "image", "image": "tools/mapgen/sources/orleans_custom/magnolia.png",
           "transparent": [[255, 0, 255]], "_comment": "Southern magnolia (own art), the towns' street tree.", "overlay_only": True,
           "metatiles": [{"id": f"{x}{y}", "bottom": [x, y]} for y in range(3) for x in range(2)]}]
         if "magnolia" in want else [])
    o = lambda n: {"overlay": f"props:{n}"}
    prefabs = {
        "bench": {"_comment": "Wooden bench (own art), 2x1.", "rows": [[o("bench_0"), o("bench_1")]]},
        "lamp": {"_comment": "Gas lamp (own art), 1x2.", "rows": [[o("lamp_top")], [o("lamp_post")]]},
        "planter": {"_comment": "Brick flower planter (own art), 2x1.", "rows": [[o("planter_0"), o("planter_1")]]},
        "barrel": {"_comment": "Barrel (own art).", "rows": [[o("barrel")]]},
        "crates": {"_comment": "Fish crates (own art).", "rows": [[o("crates")]]},
        "trap": {"_comment": "Crab trap (own art).", "rows": [[o("trap")]]},
        "magnolia": {"_comment": "Southern magnolia (own art), 2x3.",
                     "rows": [[{"overlay": f"mag:{x}{y}"} for x in range(2)] for y in range(3)]},
    }
    if "trawler" in want or "airboat" in want:  # the working boats (make_boats.py), drawn over open water
        sources.append({"name": "boats", "type": "image", "image": "tools/mapgen/sources/orleans_custom/boats.png",
                        "transparent": [[255, 0, 255]], "overlay_only": True,
                        "_comment": "Our own trawler and airboat (make_boats.py), overlays on water.",
                        "metatiles": [{"id": f"{x}{y}", "bottom": [x, y]} for y in range(2) for x in range(7)]})
        prefabs["trawler"] = {"_comment": "Shrimp trawler (own art), 4x2, moored in open water.",
                              "rows": [[{"overlay": f"boats:{x}{y}"} for x in range(4)] for y in range(2)]}
        prefabs["airboat"] = {"_comment": "Swamp airboat (own art), 3x2.",
                              "rows": [[{"overlay": f"boats:{x}{y}"} for x in range(4, 7)] for y in range(2)]}
    return sources, {k: v for k, v in prefabs.items() if k in want}


VARIANTS = {
    "orleans_harbor": dict(symbol="gTileset_OrleansHarbor", drop=[], brick=[], trim=HOUSES + KNEES + BOAT + MART,
                           lighthouse=False, church=False, extras=("bench", "crates", "trawler"),
                           addon="lands_end_tileset"),
    "orleans_camp": dict(symbol="gTileset_OrleansCamp", drop=[], brick=[], trim=HOUSES + KNEES + BOAT + MART,
                         lighthouse=False, church=False, extras=("bench", "crates", "magnolia", "airboat"),
                         addon="camp_tileset"),
    "orleans_hollow": dict(symbol="gTileset_OrleansHollow", drop=[], brick=[], trim=HOUSES + KNEES + BOAT + MART,
                           lighthouse=False, church=False, extras=("crates", "magnolia"), addon="hollow_tileset"),
    "orleans_port": dict(symbol="gTileset_OrleansPort", drop=["barn"], brick=["brick_shop", "brick_hall"],
                         trim=HOUSES + KNEES + BOAT + MUD, lighthouse=True, church=False,
                         extras=("bench", "lamp", "crates", "trawler"), addon="storms_tileset"),
    "orleans_capital": dict(symbol="gTileset_OrleansCapital", drop=[], brick=["brick_shop", "brick_row"],
                            trim=HOUSES + KNEES + BOAT + MUD,
                            lighthouse=False, church=False, extras=("bench", "lamp", "barrel", "crates", "magnolia", "airboat"),
                            addon="redfield_tileset"),
    # Crescent City: its own art, prefabs and trims live in crescent_tileset.py (applied last, see make())
    "orleans_crescent": dict(symbol="gTileset_OrleansCrescent", drop=["barn", "shady"], trim=KNEES + BOAT + MART + MUD,
                             paved=":=", brick=list(BRICK), lighthouse=False, church=True,
                             extras=("bench", "lamp", "magnolia"), custom="crescent_tileset"),
}


def ids_of(prefabs):
    out = []
    for p in prefabs:
        for row in p["rows"]:
            for c in row:
                if isinstance(c, str) and c.startswith("brick:") and c[6:] not in out:
                    out.append(c[6:])
    return out


def make(name):
    v = VARIANTS[name]
    # the base template (the original harbour set); orleans_harbor itself is now one of the variants
    recipe = json.load(open(os.path.join(TS, "templates", "harbor_recipe.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(TS, "templates", "harbor_config.json"), encoding="utf-8"))
    r = copy.deepcopy(recipe)
    r["_comment"] = f"{name}: generated by make_town_tilesets.py from the harbour template (tilesets/templates)."
    r["dir"], r["symbol"], r["blends_file"] = name, v["symbol"], f"{name}.blends.json"
    if not v.get("custom"):  # compose only what the town's map places (see compose.demand_only), with
        r["demand"] = True   # tile-level, map-weighted palettes (compose.py "palette v2"; backdrop trick off: the
        r["palette"] = "v2"  # day/night tint leaves colour 0 untinted)
    drop = set(v["drop"])
    r["sources"] = [s for s in r["sources"] if s["name"] not in drop]
    r["patches"] = [p for p in r["patches"] if not any(p.get("id", "").startswith(d + "_") for d in drop)]
    c0 = None
    for src, ids_, gone in v.get("trim", []):
        if src == "patch":
            r["patches"] = [p for p in r["patches"] if not any(p.get("id", "").startswith(i) for i in ids_)]
        else:
            s = next(s for s in r["sources"] if s["name"] == src)
            if "ids" in s:
                s["ids"] = [i for i in s["ids"] if i not in ids_]
            else:
                s["metatiles"] = [m for m in s["metatiles"] if m["id"] not in ids_]
    c = copy.deepcopy(cfg)
    c["secondary"], c["secondary_dir"] = v["symbol"], f"data/tilesets/secondary/{name}"
    c["mappings"] = ["orleans_general.mapping.json", f"{name}.mapping.json"]
    c["blends_file"] = f"{name}.blends.json"
    for _, _, gone in v.get("trim", []):
        for g in gone:
            c["prefabs"].pop(g, None)
    if "barn" in drop:
        c["prefabs"].pop("barn", None)
    if "shady" in drop:
        for p in ("house_a", "house_b", "cabin"):
            c["prefabs"].pop(p, None)
    prefabs = {k: BRICK[k] for k in v["brick"]}
    ids = ids_of(prefabs.values())
    if v["church"]:
        ids += [i for i in CHURCH_IDS if i not in ids]
        bayou = json.load(open(os.path.join(TS, "orleans_bayou.json"), encoding="utf-8"))
        prefabs["church"] = bayou["prefabs"]["church"]
        bayou_recipe = json.load(open(os.path.join(TS, "recipes", "orleans_bayou.json"), encoding="utf-8"))
        r["patches"] += [p for p in bayou_recipe["patches"] if p.get("id", "").startswith("church_")]
    brick_src = next((s for s in r["sources"] if s["name"] == "brick"), None)
    if brick_src is None:
        brick_src = {"name": "brick", "primary": "general", "secondary": "tools/mapgen/sources/brick_city", "layers": 3}
        r["sources"].append(brick_src)
    brick_src.pop("pick_only_for_patches", None)
    brick_src["ids"] = ids
    brick_src["rebase_ground"] = {"base": "ekat:grass", "colors": [[120, 160, 104], [104, 144, 96], [110, 146, 100],
                                                                    [136, 176, 128], [140, 178, 131]]}
    r["patches"] += BRICK_PATCHES
    if v["lighthouse"]:
        src, pf = lighthouse()
        r["sources"].append(src)
        prefabs["lighthouse"] = pf
    c["prefabs"].update(prefabs)
    if v.get("extras"):
        ex_sources, ex_prefabs = extras(v["extras"])
        r["sources"] += ex_sources
        c["prefabs"].update(ex_prefabs)
    if v.get("paved"):  # city streets: Johto grey flagstone (in the primary) with grass edges, corners and inner corners
        c["autotile"]["paved"] = {"_comment": "Johto flagstone paving on grass (primary 1B8-1CA): the cities' streets.",
                                  "connects": ":=", "NW": "1B8", "N": "1B9", "NE": "1BA", "W": "1C0", "C": "1C1",
                                  "E": "1C2", "SW": "1C8", "S": "1C9", "SE": "1CA",
                                  "iNW": "1BB", "iNE": "1BC", "iSW": "1C3", "iSE": "1C4"}
        for ch in v["paved"]:
            c["terrain"][ch] = {"name": "paved street", "tile": "1C1", "elev": 3, "autotile": "paved"}
    # levee ground along river channels (levee.py): plain grass to every patch border, the levee drawn over it
    c["terrain"]["B"] = {"name": "levee ground (river channels; levee.py draws the embankment)", "tile": "ekat:grass",
                         "elev": 3}
    for a in c["autotile"].values():
        if "apply_on" in a and "." in a["apply_on"] and "B" not in a["apply_on"]:
            a["apply_on"] += "B"
    if v.get("custom"):  # a town's own additions (e.g. crescent_tileset.apply)
        sys.path.insert(0, HERE)
        __import__(v["custom"]).apply(r, c)
    if v.get("addon"):  # a handmade town's own pieces on a demand variant (e.g. storms_tileset for Storm's Edge)
        sys.path.insert(0, HERE)
        __import__(v["addon"]).apply(r, c)
    for path, obj in ((os.path.join(TS, "recipes", f"{name}.json"), r), (os.path.join(TS, f"{name}.json"), c)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(name, "brick ids", len(ids), "prefabs", sorted(c["prefabs"]))


if __name__ == "__main__":
    for n in sys.argv[1:] or VARIANTS:
        make(n)
