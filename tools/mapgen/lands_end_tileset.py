"""Land's End's own pieces on top of the orleans_harbor tileset variant (make_town_tilesets.py calls apply() for
VARIANTS["orleans_harbor"]["addon"]). The variant stays demand-driven (compose keeps only what lands_end.py places) with
the v2 palette packer (never v2_backdrop). Same hook as camp_tileset.py / hollow_tileset.py.

Adds:
    own art     sources/orleans_custom/lands_end_planks.png and lands_end_art.png (drawn by make_lands_end_art.py,
                indexed by lands_end.json): every piece in the json becomes a prefab of the same name.
                  planks (sheet "planks": h<edges> / v<edges>, opaque 16x16 cells) are plain metatiles `lep:<name>`
                    placed as prefab `plank_<name>` (walkable), the boardwalk's deck;
                  art (sheet "art": skirts, houses on pilings, pavilion, lookout, station, shop, heron pile, pile,
                    sign) are overlays `lea:<x>_<y>`, drawn over whatever terrain lies beneath (water, mud, planks);
                    a piece's door cell gets a door behaviour, its `passable` cells are walkable ground even over
                    water ("walk": the art decides the behaviour).
    boats       trawler_a / trawler_b (6x3, art) are Land's-End-only; the old trawler is no longer placed here.
    water       no random weeds or lily decor on open water (stilts and decks stand on it): the water set's own
                lily variation stays.
"""
import json
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "sources", "orleans_custom")
ART_DIR = "tools/mapgen/sources/orleans_custom/"
DOOR = "MB_NON_ANIMATED_DOOR"
KEY = (255, 0, 255)

# art pieces held back as stand-ins while the set is over its tile budget: name -> (house piece to cut from, columns,
# rows, door cell). Empty when everything fits.
HOLD = {}

# pieces lands_end.py wants that may still be art requests: name -> (w, h, walk cells)
BOATS = {"trawler_a": (6, 3), "trawler_b": (6, 3)}


def art_index():
    p = os.path.join(ART, "lands_end.json")
    return json.load(open(p, encoding="utf-8"))["pieces"] if os.path.exists(p) else {}


def apply(r, c):
    idx = art_index()
    P = c["prefabs"]
    c["terrain"]["~"].pop("decor", None)
    if idx:
        sheets = {s: Image.open(os.path.join(ART, f"lands_end_{s}.png")).convert("RGB") for s in {p["sheet"] for p in idx.values()}}
        for sheet, src_name, overlay in (("planks", "lep", False), ("art", "lea", True)):
            if sheet not in sheets:
                continue
            cells = []
            for name, p in idx.items():
                if p["sheet"] != sheet:
                    continue
                for j in range(p["h"]):
                    for i in range(p["w"]):
                        if [i, j] not in p.get("empty", []):
                            cells.append((p["x"] + i, p["y"] + j))
            cells = sorted(set(cells), key=lambda t: (t[1], t[0]))
            # plank cells keep the piece name (lep:hns); overlay cells are named by sheet position
            if sheet == "planks":
                meta = [{"id": n, "bottom": [p["x"], p["y"]]} for n, p in idx.items() if p["sheet"] == "planks"]
            else:
                meta = [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]
            r["sources"].append({"name": src_name, "type": "image", "image": ART_DIR + f"lands_end_{sheet}.png",
                                 "transparent": [list(KEY)], "overlay_only": overlay,
                                 "_comment": f"Land's End's own art, {sheet} sheet (make_lands_end_art.py).",
                                 "metatiles": meta})
        for name, p in idx.items():
            if p["sheet"] == "planks":
                P["plank_" + name] = {"_comment": f"Boardwalk plank {name}: edges {name[1:] or 'none'} open to water.",
                                      "rows": [[f"lep:{name}"]], "passable": [[0, 0]]}
                continue
            doors = [tuple(d) for d in p.get("doors", [])]
            walk = {tuple(w) for w in (p.get("passable") or (p["walk"] if isinstance(p.get("walk"), list) else []))}
            rows = []
            for j in range(p["h"]):
                row = []
                for i in range(p["w"]):
                    if [i, j] in p.get("empty", []):
                        row.append(None)
                        continue
                    o = {"overlay": f"lea:{p['x'] + i}_{p['y'] + j}"}
                    if (i, j) in doors:
                        o["behavior"] = DOOR
                    if (i, j) in walk or (i, j) in doors:
                        o["walk"] = True
                    row.append(o)
                rows.append(row)
            pf = {"_comment": p.get("comment", "Land's End own art."), "rows": rows,
                  "passable": [list(w) for w in sorted(walk)]}
            if doors:
                pf["door"] = list(doors[0]) if len(doors) == 1 else [list(d) for d in doors]
            P[name] = pf
    # ---- pieces held back for the 512-tile budget (HOLD) get same-footprint stand-ins cut from a house's cells
    # (no extra tiles): see art_requests/lands_end.md for what each piece costs as drawn
    for name, (src, cols, rws, door) in HOLD.items():
        if name not in idx or src not in P:
            continue
        base = P[src]["rows"]
        clean = lambda cell: None if cell is None else {k: v for k, v in cell.items() if k == "overlay"}
        rows = [[clean(base[j][i]) for i in cols] for j in rws]
        dx, dy = door
        rows[dy][dx] = dict(rows[dy][dx] or {}, behavior=DOOR, walk=True)
        P[name] = {"_comment": f"STAND-IN for the {name} art (held for the tile budget): cut from {src}.",
                   "rows": rows, "door": list(door), "passable": [], "stand_in": True}
    # ---- the Pokemon Center stands over water: the vanilla building's own ground (its grass) is cut away and the
    # tiles are redrawn over the water (compose "reseat"), the door cell keeps its door behaviour
    if "pokecenter" in P:
        grass = [[120, 160, 104], [104, 144, 96], [110, 146, 100], [136, 176, 128], [140, 178, 131], [122, 172, 130],
                 [149, 190, 157], [96, 128, 88]]
        rows = []
        for j, row in enumerate(P["pokecenter"]["rows"]):
            out = []
            for i, ref in enumerate(row):
                src = "vgen:061" if ref == "patch:pc_door" else ref
                pid = f"pcw_{j}{i}"
                pt = {"id": pid, "reseat": src, "base": "ekat:water_C", "colors": grass}
                if ref == "patch:pc_door":
                    pt["behavior"] = DOOR
                r["patches"].append(pt)
                out.append(f"patch:{pid}")
            rows.append(out)
        P["pokecenter"] = dict(P["pokecenter"], rows=rows, _comment="Vanilla Emerald Pokemon Center (4x4) reseated on water.")
    # the Center's footing: pc_skirt's right-hand cell alone (the stub's planks cover the other columns of the 4x1 row)
    if "pc_skirt" in idx:
        p = idx["pc_skirt"]
        P["pc_skirt_r"] = {"_comment": "Pilings under the Pokemon Center's south-east corner (cell 3 of pc_skirt).",
                           "rows": [[{"overlay": f"lea:{p['x'] + 3}_{p['y']}"}]], "passable": []}
    # the signpost keeps its primary tile when the art has no sign
    P.setdefault("sign", {"_comment": "Wooden signpost (primary 003).", "rows": [["003"]]})
    # ---- the trawlers (art delivered): blocking overlays on open water; the old trawler is no longer used here
    for name in BOATS:
        if name in idx:
            P[name]["elev"] = 1
