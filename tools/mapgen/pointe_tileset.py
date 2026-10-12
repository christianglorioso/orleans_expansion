"""gTileset_OrleansPointe: Pointe Rouge's own secondary tileset (the state capital).

Built from the harbour base template (tilesets/templates/harbor_recipe.json + harbor_config.json, read-only) with what a bayou capital
needs and nothing else:
    terrain    Ekat swamp grass, the river (water corner set, open water with lily pads: no trees, logs or snags in it); streets are the primary's Johto flagstone ("="); tall grass ("G", Ekat's tile on plain grass, the east bank). No marsh or mud.
    services   vanilla Pokemon Center and Mart
    brick      Brick City houses: plain and round-window
    own art    the art-deco Capitol, the refinery (process house, crude tanks, distillation columns, flare stack),
               the rail yard (buffer stops; the boxcar `rail_car` and its track `rail_h` come from the approved route landmark art, source `lmk`), Kingfisher's boathouse gym and its dock, the bait and
               tackle shop, the old ice plant, the stone quay (edge, bollard, crates, barrels), the stone arch
               bridge (both river crossings), a dockside crane, a park bench, a formal flower bed and the region's magnolia recoloured
               (sources/orleans_custom/make_pointe_art.py), all in colours the tileset already has
    primary    Johto street lamps and the grey post-and-rail fence (free: they live in the primary)

usage (from the decomp root): python tools/mapgen/pointe_tileset.py
writes tilesets/recipes/orleans_pointe.json and tilesets/orleans_pointe.json; then
    python -W ignore tools/mapgen/compose.py tools/mapgen/tilesets/recipes/orleans_pointe.json --register
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TS = os.path.join(HERE, "tilesets")
from make_town_tilesets import BRICK, BRICK_PATCHES  # noqa: E402

NAME, SYMBOL = "orleans_pointe", "gTileset_OrleansPointe"
ART = "tools/mapgen/sources/orleans_custom/"
DOOR = "MB_NON_ANIMATED_DOOR"

# Brick City buildings this town uses
BRICK_USED = ["brick_round", "brick_house"]  # the gabled house would cost 32 tiles: out of budget

# Ekat pieces the capital does without (no mud, no tall grass, no knees; marsh never meets the river)
EKAT_DROP = {f"{t}_{s}" for t in ("mud", "mudwater", "marshwater") for s in
             ("N", "S", "W", "E", "C", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW", "landNE", "landNW",
              "landSE2", "landSW2", "landNE2", "landNW2", "plants3", "sTLBR", "sTRBL")}
EKAT_DROP |= {"knees_00", "knees_10", "knees_20", "knees_01", "knees_11", "marsh_landSE2",
              "marsh_landSW2", "marsh_landNE2", "marsh_landNW2", "water_landSE2", "water_landSW2", "water_landNE2",
              "water_landNW2", "log_0", "log_1", "stump", "stump_top", "water_weeds2", "reeds", "reeds_top"}
# no marsh in the capital: its trees are magnolias on the lawns (none stand in the river)
EKAT_DROP |= {f"marsh_{s}" for s in ("N", "S", "W", "E", "C", "inNW", "inNE", "inSW", "inSE", "landSE", "landSW",
                                     "landNE", "landNW", "sTLBR", "sTRBL", "plants1", "plants3")}
EKAT_DROP |= {f"cypress_small_{x}{y}" for x in range(2) for y in range(3)}
# the river runs straight off the map's top and bottom with one bulge on its west bank: these bank pieces,
# the floating logs and snags and the second water plant never appear (tools/mapgen/usage.py orleans_pointe)
EKAT_DROP |= {"marsh", "water_N", "water_S", "water_inNE", "water_inSE", "water_landNW", "water_landSW", "water_sTLBR",
              "water_sTRBL", "water_weeds1", "waterlog_0", "waterlog_1", "snag_top_water", "waterstump"}
VGEN_DROP = {"02A", "040", "041", "061"}  # the doors are patches; 02A (an empty roof tile) is unused
PATCH_DROP = ("boat_", "grave_", "shrine_", "tallgrass_", "path_i", "shady_", "barn_", "pier_", "reeds_",
              "cypress_small_")
PREFAB_DROP = ("knees", "log", "stump", "boat", "shrine", "house_a", "house_b", "cabin", "barn", "dock_h", "pier",
               "waterlog", "snag_water",
               "cypress", "cypress_small", "cypress_marsh", "cypress_small_marsh", "cypress_small_water", "reeds_marsh")


def image(name, png, cells, overlay_only=True):
    return {"name": name, "type": "image", "image": ART + png, "transparent": [[255, 0, 255]],
            "overlay_only": overlay_only, "metatiles": [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]}


def grid_cells(w, h):
    return [(x, y) for y in range(h) for x in range(w)]


def ov(src, x, y, **kw):
    return dict({"overlay": f"{src}:{x}_{y}"}, **kw)


def own_art():
    """Image sources and prefabs for the own-art pieces (all overlays: drawn over whatever terrain lies beneath)."""
    srcs, pf = [], {}
    # Capitol 10x14: double bronze doors, a grand staircase (walkable), the rest blocks
    srcs.append(image("cap", "pointe_capitol.png", grid_cells(10, 14)))
    rows = []
    for y in range(14):
        row = []
        for x in range(10):
            if y == 13 and not 3 <= x <= 6:
                row.append(None)  # ground before the terrace
            elif (x, y) in ((4, 11), (5, 11)):
                row.append(ov("cap", x, y, behavior=DOOR))
            elif y < 2 and not 4 <= x <= 5 or y == 2 and not 3 <= x <= 6:
                row.append(None)  # sky round the lantern: nothing drawn there
            else:
                row.append(ov("cap", x, y))
        rows.append(row)
    pf["capitol"] = {"_comment": "The art-deco Capitol (own art), 10x14: tower, chamber wings, grand staircase.",
                     "rows": rows, "door": [[4, 11], [5, 11]],
                     "passable": [[x, y] for y in (12, 13) for x in range(3, 7)]}
    # the refinery's process house 6x6, door (2, 5)
    srcs.append(image("ref", "pointe_refinery.png", grid_cells(6, 6)))
    pf["refinery"] = {"_comment": "Refinery process house (own art), 6x6.", "door": [2, 5],
                      "rows": [[ov("ref", x, y, **({"behavior": DOOR} if (x, y) == (2, 5) else {})) for x in range(6)]
                               for y in range(6)]}
    srcs.append(image("tank", "pointe_tank.png", grid_cells(3, 3)))
    pf["tank"] = {"_comment": "Crude oil tank (own art), 3x3.", "rows": [[ov("tank", x, y) for x in range(3)] for y in range(3)]}
    srcs.append(image("col", "pointe_column.png", grid_cells(1, 7)))
    pf["column"] = {"_comment": "Distillation column (own art), 1x7.", "rows": [[ov("col", 0, y)] for y in range(7)]}
    srcs.append(image("flare", "pointe_flare.png", grid_cells(1, 7)))
    pf["flare"] = {"_comment": "Flare stack (own art), 1x7.", "rows": [[ov("flare", 0, y)] for y in range(7)]}
    srcs.append(image("pipe", "pointe_pipes.png", grid_cells(2, 1)))
    pf["pipes"] = {"_comment": "Pipe rack (own art), 1x1, repeats east-west.", "rows": [[ov("pipe", 0, 0)]]}
    pf["pipes_end"] = {"_comment": "Pipe rack's east end, the pipes turning down.", "rows": [[ov("pipe", 1, 0)]]}
    # rail yard: track cells are walkable (step over the rails); buffers and the tank car block
    srcs.append(image("rail", "pointe_rails.png", grid_cells(6, 1)))
    pf["track"] = {"_comment": "Rail track on ballast (own art), 1x1, walkable.", "rows": [[ov("rail", 0, 0)]],
                   "passable": [[0, 0]]}
    pf["buffer_w"] = {"_comment": "Buffer stop, west end of a track.", "rows": [[ov("rail", 1, 0)]]}
    pf["buffer_e"] = {"_comment": "Buffer stop, east end of a track.", "rows": [[ov("rail", 2, 0)]]}
    pf["tank_car"] = {"_comment": "Black tank car standing on the track, 3x1.", "rows": [[ov("rail", x, 0) for x in (3, 4, 5)]]}
    # Kingfisher's boathouse gym 7x6, door (3, 5)
    srcs.append(image("gym", "pointe_gym.png", grid_cells(7, 6)))
    pf["boathouse"] = {"_comment": "Riverfront boathouse gym (own art), 7x6.", "door": [3, 5],
                       "rows": [[None if (y == 0 and x != 3) else
                                 ov("gym", x, y, **({"behavior": DOOR} if (x, y) == (3, 5) else {})) for x in range(7)]
                                for y in range(6)]}
    # bridges: pieces are overlays; the deck is the primary's paving (1C1)
    bridge_cells = grid_cells(3, 3) + [(3, 0), (3, 1), (3, 2)]
    srcs.append(image("sbr", "pointe_stonebridge.png", bridge_cells))
    # the bait and tackle shop 6x5 (door 1,4) and the old ice plant 9x6 (door 4,5)
    srcs.append(image("tackle", "pointe_tackle.png", grid_cells(6, 5)))
    pf["tackle_shop"] = {"_comment": "Bait and tackle shop (own art), 6x5.", "door": [1, 4],
                         "rows": [[None if (y == 0 and not 1 <= x <= 4) else
                                   ov("tackle", x, y, **({"behavior": DOOR} if (x, y) == (1, 4) else {}))
                                   for x in range(6)] for y in range(5)]}
    srcs.append(image("ice", "pointe_iceplant.png", grid_cells(9, 6)))
    pf["ice_plant"] = {"_comment": "The old ice plant (own art), 9x6.", "door": [4, 5],
                       "rows": [[ov("ice", x, y, **({"behavior": DOOR} if (x, y) == (4, 5) else {})) for x in range(9)]
                                for y in range(6)]}
    # the stone quay along the city bank: the edge (walkable), with a bollard (blocks), crates, barrels
    srcs.append(image("quay", "pointe_quay.png", grid_cells(5, 1)))
    pf["quay"] = {"_comment": "Quayside edge (own art), the coping over the paving's kerb; walkable.",
                  "rows": [[ov("quay", 0, 0)]], "passable": [[0, 0]]}
    pf["quay_bollard"] = {"_comment": "Quayside edge with an iron bollard.", "rows": [[ov("quay", 1, 0)]]}
    pf["quay_wall"] = {"_comment": "The quay wall's face over the river's bank piece (blocks).", "rows": [[ov("quay", 4, 0)]]}
    srcs.append(image("crane", "pointe_crane.png", grid_cells(2, 3)))
    pf["crane"] = {"_comment": "Dockside jib crane (own art), 2x3.",
                   "rows": [[ov("crane", x, y) for x in range(2)] for y in range(3)]}
    pf["crates"] = {"_comment": "Stacked crates (own art).", "rows": [[ov("quay", 2, 0)]]}
    pf["barrels"] = {"_comment": "Two barrels (own art).", "rows": [[ov("quay", 3, 0)]]}
    # free street furniture from the primary (Johto general, recoloured to the swamp greens)
    pf["lamp"] = {"_comment": "Johto street lamp (primary 02A/03A), 1x2.", "rows": [["02A"], ["03A"]]}
    pf["shrub"] = {"_comment": "Round shrub (primary 00E).", "rows": [["00E"]]}
    pf["roses"] = {"_comment": "Red rose bush (primary 005).", "rows": [["005"]]}
    pf["sign"] = {"_comment": "Wooden sign (primary 003).", "rows": [["003"]]}
    pf["fence"] = {"_comment": "Grey post-and-rail fence piece (primary 0EC-0FD, 136): rows come from the spec.", "rows": [["0ED"]]}
    pf["bridge"] = {"_comment": "River bridge: its rows come from the spec (pointe_tileset.bridge_rows).", "rows": [[None]]}
    # street furniture and planting drawn in the town's own colours (a bench, a formal flower bed, the magnolia)
    srcs.append(image("bench", "pointe_bench.png", grid_cells(2, 1)))
    pf["bench"] = {"_comment": "Park bench (own art), 2x1.", "rows": [[ov("bench", 0, 0), ov("bench", 1, 0)]]}
    srcs.append(image("dock", "pointe_dock.png", grid_cells(3, 2)))
    pf["dock"] = {"_comment": "The gym's boat dock (own art), 3x2, walkable over the water.",
                  "rows": [[ov("dock", x, y, walk=True) for x in range(3)] for y in range(2)],
                  "passable": [[x, y] for y in range(2) for x in range(3)]}
    srcs.append(image("bed", "pointe_flowerbed.png", grid_cells(3, 1)))
    pf["flowerbed"] = {"_comment": "Formal flower bed (own art), 3x1: every flower its own colour.",
                       "rows": [[ov("bed", x, 0) for x in range(3)]]}
    srcs.append(image("mag", "pointe_magnolia.png", grid_cells(2, 3)))
    pf["magnolia"] = {"_comment": "Southern magnolia (the region's own art, colours snapped to this tileset's), 2x3.",
                      "rows": [[ov("mag", x, y) for x in range(2)] for y in range(3)]}
    return srcs, pf


def bridge_rows(kind, length):
    """Rows of an east-west river bridge `length` cells long (including the abutment end piers):
    north rail, deck, deck, south rail, then the face under the deck (truss bays with piers, or stone arches)."""
    src = {"truss": "truss", "stone": "sbr"}[kind]
    L = length
    def rail(row):
        return [ov(src, 1, row)] + [ov(src, 0, row)] * (L - 2) + [ov(src, 3, row)]
    deck = ["1C1"] * L
    # the face under the deck: two cells of solid abutment at each end (they stand over the river banks), and
    # between them truss bays with two piers placed symmetrically, or round arches two cells each
    n = L - 4
    if kind == "truss":
        k = n // 3
        mid = [ov(src, 1, 2) if i in (k, n - 1 - k) else ov(src, 0, 2) for i in range(n)]
    else:
        if n % 2:
            raise SystemExit(f"stone bridge of length {L}: the arches need an even span between the abutments")
        mid = [ov(src, i % 2, 2) for i in range(n)]
    face = [ov(src, 2, 2)] * 2 + mid + [ov(src, 3, 2)] * 2
    return [rail(0), deck, deck, rail(1), face]


def landmarks(r, c):
    """The approved route landmarks' boxcar (rail_car 3x2, its bottom row carries the track) and its matching
    track (rail_h): source `lmk` (sources/orleans_custom/route_landmarks.*) and just those two prefabs."""
    doc = json.load(open(os.path.join(HERE, "sources", "orleans_custom", "route_landmarks.json"), encoding="utf-8"))
    r["sources"] = [s for s in r["sources"] if s["name"] != doc["source"]["name"]]
    r["sources"].append(json.loads(json.dumps(doc["source"])))
    for name in ("rail_car", "rail_h"):
        c["prefabs"][name] = json.loads(json.dumps(doc["prefabs"][name]))


def riverboat(r, c):
    """Crescent City's riverboat (the white sternwheeler moored north-south, 3x7: `steamboat_ns`, own art in
    sources/orleans_custom/crescent_stone.png): just its 17 metatiles as source `ccs`, and its prefab, taken from
    Crescent's own recipe and builder config so the two cities' boats are the same piece."""
    cr = json.load(open(os.path.join(TS, "recipes", "orleans_crescent.json"), encoding="utf-8"))
    cc = json.load(open(os.path.join(TS, "orleans_crescent.json"), encoding="utf-8"))
    src = json.loads(json.dumps(next(s for s in cr["sources"] if s["name"] == "ccs")))
    src["metatiles"] = [m for m in src["metatiles"] if m["id"].startswith("steamboat_ns_")]
    r["sources"] = [s for s in r["sources"] if s["name"] != "ccs"]
    r["sources"].append(src)
    boat = json.loads(json.dumps(cc["prefabs"]["steamboat_ns"]))
    c["prefabs"]["steamboat_ns"] = boat
    # Pointe's boat points the other way (south): the same piece upside down, rows reversed, every cell vertically
    # flipped (compose.py's overlay "vflip"), so bow and stern swap ends and the paddle wheel is at the north
    south = json.loads(json.dumps(boat))
    south["_comment"] = "Crescent's riverboat turned bow-south (rows reversed, each cell vflipped), 3x7."
    south["rows"] = [[dict(cell, vflip=True) for cell in row] for row in reversed(boat["rows"])]
    c["prefabs"]["steamboat_ns_s"] = south


def make():
    recipe = json.load(open(os.path.join(TS, "templates", "harbor_recipe.json"), encoding="utf-8"))
    cfg = json.load(open(os.path.join(TS, "templates", "harbor_config.json"), encoding="utf-8"))
    r = copy.deepcopy(recipe)
    r["_comment"] = "Pointe Rouge (the capital): generated by pointe_tileset.py. " + __doc__.split("\n\n")[1].strip().split("\n")[0]
    r["dir"], r["symbol"], r["blends_file"] = NAME, SYMBOL, f"{NAME}.blends.json"
    r["demand"] = True  # keep only the pieces the map places (compose.demand_only)
    r["sources"] = [s for s in r["sources"] if s["name"] not in ("barn", "shady")]
    for s in r["sources"]:
        if s["name"] == "ekat":
            s["metatiles"] = [m for m in s["metatiles"] if m["id"] not in EKAT_DROP]
    vg = next(s for s in r["sources"] if s["name"] == "vgen")
    vg["ids"] = [i for i in vg["ids"] if i not in VGEN_DROP]
    r["patches"] = [p for p in r["patches"] if not p.get("id", "").startswith(PATCH_DROP)
                    and not p.get("id", "").endswith("_marsh")]
    # Brick City
    brick = next(s for s in r["sources"] if s["name"] == "brick")
    brick.pop("pick_only_for_patches", None)
    ids = []
    for k in BRICK_USED:
        for row in BRICK[k]["rows"]:
            for c in row:
                if isinstance(c, str) and c.startswith("brick:") and c[6:] not in ids:
                    ids.append(c[6:])
    brick["ids"] = ids
    brick["rebase_ground"] = {"base": "ekat:grass", "colors": [[120, 160, 104], [104, 144, 96], [110, 146, 100],
                                                                [136, 176, 128], [140, 178, 131]]}
    # four of Brick City's 18 colours folded into near neighbours, so the brick set (and the own art drawn in its
    # colours) fits one 15-colour palette
    brick["recolor"] = [[[80, 80, 80], [88, 72, 80]], [[72, 72, 80], [64, 72, 104]], [[96, 96, 120], [96, 96, 104]],
                        [[128, 104, 104], [144, 88, 80]]]
    # the vanilla Center and Mart: cut away all of Emerald's grass greens (tufts too), not just the main three
    vgen = next(s for s in r["sources"] if s["name"] == "vgen")
    vgen["rebase_ground"]["colors"] += [[180, 255, 131], [131, 197, 98], [57, 139, 49], [24, 164, 106], [57, 82, 0]]
    used_patches = {c[6:] for k in BRICK_USED for row in BRICK[k]["rows"] for c in row
                    if isinstance(c, str) and c.startswith("patch:")}
    r["patches"] += [p for p in BRICK_PATCHES if p["id"] in used_patches]
    # our own art (the shared props sheet is left out: its colours would squeeze the 7 palettes)
    art_src, art_pf = own_art()
    r["sources"] += art_src
    # --- builder config
    c = copy.deepcopy(cfg)
    c["_comment"] = "Pointe Rouge: gTileset_OrleansGeneral + gTileset_OrleansPointe (generated by pointe_tileset.py)."
    c["secondary"], c["secondary_dir"] = SYMBOL, f"data/tilesets/secondary/{NAME}"
    c["mappings"] = ["orleans_general.mapping.json", f"{NAME}.mapping.json"]
    c["blends_file"] = f"{NAME}.blends.json"
    c["border"] = ["ekat:grass"] * 4
    for p in PREFAB_DROP:
        c["prefabs"].pop(p, None)
    for k in BRICK_USED:
        c["prefabs"][k] = copy.deepcopy(BRICK[k])
    c["prefabs"].update(art_pf)
    landmarks(r, c)
    riverboat(r, c)  # Crescent's riverboat (+25 tiles; the buffer stops and flower beds were dropped to pay for it)
    c["variants"] = {}
    # terrain: no dirt roads, mud, churchyards or tall grass in the capital; streets are flagstone
    for ch in (":", "L", "S", "G", "#", "I"):
        c["terrain"].pop(ch, None)
    c["terrain"]["G"] = {"name": "tall grass (wild encounters)", "tile": "ekat:tallgrass", "elev": 3,
                         "_comment": "Tall grass on plain grass (the east bank): the same piece as the routes."}
    c["terrain"]["="] = {"name": "paved street", "tile": "1C1", "elev": 3, "autotile": "paved"}
    c["autotile"].pop("path", None)
    c["autotile"].pop("mud", None)
    c["autotile"]["paved"] = {"_comment": "Johto flagstone paving on grass (primary 1B8-1CA).", "connects": "=",
                              "NW": "1B8", "N": "1B9", "NE": "1BA", "W": "1C0", "C": "1C1", "E": "1C2",
                              "SW": "1C8", "S": "1C9", "SE": "1CA", "iNW": "1BB", "iNE": "1BC", "iSW": "1C3",
                              "iSE": "1C4"}
    # "w": river water with no lily pads or weeds (under and beside the bridges)
    c["terrain"]["w"] = {"name": "water (no decor)", "tile": "ekat:water_C", "elev": 1}
    c["prefabs"].pop("cypress_water", None)  # no trees in the river
    c["terrain"]["~"]["decor"]["tiles"] = ["ekat:water_lily"]
    w = c["autotile"]["water"]
    for k in [k for k, v in w.items() if isinstance(v, str) and v.split(":")[-1] in EKAT_DROP]:
        del w[k]  # pieces this river never needs; the builder stops loudly if a new shape asks for one
    w["connects"] = "~w"
    w["apply_on"] = "~.w"
    w.pop("alt_land", None)
    w["neutral"] = ""
    c["autotile"].pop("marsh", None)
    c["terrain"].pop('"', None)
    for path, obj in ((os.path.join(TS, "recipes", f"{NAME}.json"), r), (os.path.join(TS, f"{NAME}.json"), c)):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, indent=1, ensure_ascii=False)
            f.write("\n")
    print(f"{NAME}: {len(r['sources'])} sources, {len(r['patches'])} patches, prefabs {sorted(c['prefabs'])}")


if __name__ == "__main__":
    make()
