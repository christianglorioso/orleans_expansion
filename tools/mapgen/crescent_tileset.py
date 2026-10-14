"""Crescent City's own additions to the orleans_crescent tileset variant (called by make_town_tilesets.make()).

The variant starts from the harbour base with Brick City buildings, the church and the shared street props
(bench, lamp, planter, magnolia). This module trims what the city never uses (mud, the shrine stone, the
wooden road bridge) and adds our own art from sources/orleans_custom/crescent.png (make_crescent_art.py):
above-ground tombs and the Fifolet gym for the Old Cemetery, the iron fence, drowned-ward ruins, French
Quarter iron balconies, market stalls, a stone fountain, the riverboat, mailbox, bins and signs.

Every piece of own art is an overlay (drawn over whatever terrain or wall tile is underneath), so the
source image is "overlay_only": only the composites the map really uses cost tiles. Prefab names and cell
layouts come from crescent.json, written by the art script next to the image.

usage: python tools/mapgen/make_town_tilesets.py orleans_crescent
       python -W ignore tools/mapgen/compose.py tools/mapgen/tilesets/recipes/orleans_crescent.json --register
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "sources", "orleans_custom")
DOOR = "MB_NON_ANIMATED_DOOR"


def apply(r, c):
    # compose only the pieces the map places (compose.demand_only), with tile-level map-weighted palettes
    # ("palette v2"; never the v2 backdrop trick: the day/night tint leaves colour 0 untinted)
    r["demand"] = True
    r["palette"] = "v2"
    # ---- trims (tile budget): no mud, shrine stone, wooden road bridge, dirt-path corners, headstones, tall grass
    # on marsh, snags, floating logs, reeds or small cypresses
    r["sources"] = [s for s in r["sources"] if s["name"] != "brg"]
    gone = ("shrine_stone", "grave_grass")      # (Route 3 shares this tileset since the seams review: its small cypress, reeds, snags, logs, tall grass, dirt-road corners and pier stay in)
    r["patches"] = [p for p in r["patches"] if not p.get("id", "").startswith(gone)]
    for k in ("shrine",):
        c["prefabs"].pop(k, None)
    c["autotile"].pop("path", None)
    ekat = next(s for s in r["sources"] if s["name"] == "ekat")
    # marsh never meets water in the city (crescent.py keeps a grass bank between them), so no marsh-water set
    c["autotile"]["water"]["alt_land"] = [a for a in c["autotile"]["water"].get("alt_land", []) if a["chars"] != '"']
    drop = lambda i: i.startswith(("marshwater",))
    ekat["metatiles"] = [m for m in ekat["metatiles"] if not drop(m["id"])]
    # the cypress and reed art is only ever used re-seated on marsh or water: keep it out of the tileset as raw
    # pieces (an overlay-only copy of the sheet that patches can still read)
    patch_only = [m for m in ekat["metatiles"] if m["id"].startswith("cypress_")]
    ekat["metatiles"] = [m for m in ekat["metatiles"] if m not in patch_only]
    r["sources"].insert(1, dict({k: v for k, v in ekat.items() if k != "metatiles"}, name="ekx", overlay_only=True,
                                metatiles=patch_only, _comment="Ekat cypress and reeds, only drawn re-seated."))
    ids = {m["id"] for m in patch_only}
    for p in r["patches"]:
        for k in ("upper", "reseat", "lower"):
            if isinstance(p.get(k), str) and p[k].startswith("ekat:") and p[k][5:] in ids:
                p[k] = "ekx:" + p[k][5:]
    # the Olivine dock gives way to our own boardwalk planks (walk_* below)
    c["prefabs"].pop("dock_h", None)
    c["terrain"].pop("L", None)
    # (tall grass "G" stays: Route 3's encounter grass; the city's own is the soft long grass drawn as overlays, pgrass)
    # dry ground ('D'): the Johto sand patch in the primary (0D3-0E5), for the Frontier plaza (no inner corners:
    # rectangles only). It reuses the "path" autotile slot the city's dirt paths no longer need.
    c["autotile"]["path"] = {"_comment": "Johto sand on grass (primary 0D3-0E5): the Battle Frontier plaza.",
                             "connects": "D", "NW": "0D3", "N": "0D4", "NE": "0D5", "W": "0DB", "C": "0DC",
                             "E": "0DD", "SW": "0E3", "S": "0E4", "SE": "0E5"}
    c["terrain"]["D"] = {"name": "dry ground (sand)", "tile": "0DC", "elev": 3, "autotile": "path"}  # lily pads only: the weed tufts cost tiles
    # the far bank's lakefront walk ('r'): Johto dirt, the same pieces as Route 10's promenade it meets across the seam (primary
    # 0D0-0E2, no inner corners: rectangles only), so the walk costs no tiles
    c["autotile"]["path_g"] = {"_comment": "Johto dirt path patch on grass (primary 0D0-0E2): the far bank's lakefront walk.",
                               "connects": "r", "NW": "0D0", "N": "0D1", "NE": "0D2", "W": "0D8", "C": "0D9", "E": "0DA",
                               "SW": "0E0", "S": "0E1", "SE": "0E2"}
    c["terrain"]["r"] = {"name": "dirt shore walk", "tile": "0D9", "elev": 3, "autotile": "path_g"}
    c["autotile"].pop("mud", None)
    w = c["autotile"]["water"]
    w["alt_land"] = [a for a in w.get("alt_land", []) if a["chars"] != "L"]
    w["apply_on"] = w["apply_on"].replace("L", "")
    # ---- Route 3 shares this tileset (seams review 2026-10-14, user rule: routes accommodate towns): the route family's pieces it
    # needs, copied from orleans_route. Demand-driven, so Crescent City pays for none of them. Route 3's road is terrain 'R'
    # (the city's ':' is paving): the spec's "char_map" reads its ':' / '=' as 'R' and its '%' as '='.
    rr = json.load(open(os.path.join(HERE, "tilesets", "recipes", "orleans_route.json"), encoding="utf-8"))
    rc = json.load(open(os.path.join(HERE, "tilesets", "orleans_route.json"), encoding="utf-8"))
    have = {m["id"] for m in ekat["metatiles"]}
    for m in next(x for x in rr["sources"] if x["name"] == "ekat")["metatiles"]:
        if m["id"] not in have:
            ekat["metatiles"].append(m)
    for x in rr["sources"]:
        if x["name"] in ("r40",) and not any(y["name"] == x["name"] for y in r["sources"]):
            r["sources"].append(x)
    pid = {p_.get("id") for p_ in r["patches"]}
    for p_ in rr["patches"]:
        if p_.get("id") not in pid and p_.get("id", "").startswith(("pier_", "cypress_small", "reeds", "path_i", "tallgrass", "snag", "waterlog")):
            r["patches"].append(p_)
    for k, v in rc["prefabs"].items():
        if k in ("pier", "cypress_small", "cypress_small_marsh", "cypress_small_water", "reeds_marsh", "snag_water", "waterlog", "log", "stump", "cypress"):
            c["prefabs"][k] = v
    c["prefabs"]["sign_g"] = rc["prefabs"]["sign"]       # the route's plain primary sign (the city's "sign" is its own notice board)
    c["variants"].update({k: v for k, v in rc.get("variants", {}).items() if k.startswith("pier_")})
    c["terrain"]["G"] = rc["terrain"]["G"]
    c["terrain"]["R"] = {"name": "road (route dirt)", "tile": "0D9", "elev": 3, "autotile": "path_g"}
    c["autotile"]["path_g"] = dict(rc["autotile"]["path"], connects="rR")     # the far bank's walk 'r' and the route's road share the dirt-path autotile
    c["terrain"]["~"]["decor"] = rc["terrain"]["~"]["decor"]

    # Ekat pieces nothing refers to (alternative diagonals, unused plant variations) stay out of the tileset
    import re
    used = set(re.findall(r'ekat:(\w+)', json.dumps(c) + json.dumps(r["patches"])))
    ekat["metatiles"] = [m for m in ekat["metatiles"] if m["id"] in used or m["id"] == "grass"]

    # ---- Brick City townhouses for the French Quarter and the market: two storeys (arched upper windows over a
    # ground floor), cut from the row building, and a narrow three-wide house
    D = "patch:brick_door"
    b = lambda *ids: [i if i.startswith("patch:") else f"brick:{i}" for i in ids]
    roof = lambda n: [b("220", *["221"] * (n - 2), "223"), b("228", *["229"] * (n - 2), "237"),
                      b("22A", *["22B"] * (n - 2), "233")]
    c["prefabs"]["town5"] = {"_comment": "Two-storey Brick City townhouse, 5x6 (from the row building).", "door": [2, 5],
                             "rows": roof(5) + [b("238", "260", "23A", "23A", "216"), b("238", "250", "227", "23B", "216"),
                                                b("240", "230", D, "231", "243")]}
    c["prefabs"]["town6"] = {"_comment": "Two-storey Brick City townhouse, 6x6, two arched windows.", "door": [2, 5],
                             "rows": roof(6) + [b("238", "260", "23A", "23A", "260", "216"),
                                                b("238", "250", "227", "23B", "258", "216"),
                                                b("240", "230", D, "231", "241", "243")]}
    c["prefabs"]["brick_narrow"] = {"_comment": "Narrow Brick City house, 3x5, round attic window.", "door": [1, 4],
                                    "rows": roof(3) + [b("238", "2B1", "216"), b("240", D, "243")]}

    # ---- the shared props (bench, lamp) and the magnolia are recoloured to the city's colour families
    # (make_crescent_art.FAMILY: props to the wood family, the magnolia to the leaf family), so they share palettes
    # with our own art instead of squeezing them. The shared brick planter is not used here (it mixes families).
    import sys
    from PIL import Image
    sys.path.insert(0, ART)
    from make_crescent_art import FAMILY
    gba = lambda c: tuple((v >> 3) << 3 for v in c)
    swaps = {}
    for f, fam in (("props.png", "wood"), ("magnolia.png", "leaf")):
        targets = FAMILY[fam]
        near = lambda c: min(targets, key=lambda t: (t[0] - c[0]) ** 2 * 3 + (t[1] - c[1]) ** 2 * 4 + (t[2] - c[2]) ** 2 * 2)
        for _, col in Image.open(os.path.join(ART, f)).convert("RGB").getcolors(4096):
            g = gba(col)
            if col != (255, 0, 255) and g not in targets:
                swaps[g] = near(g)
    r["recolor"] = r.get("recolor", []) + [[list(a), list(b)] for a, b in sorted(swaps.items())]
    c["prefabs"].pop("planter", None)

    # ---- our own art: one overlay-only source per colour family sheet (crescent_<family>.png)
    idx_path = os.path.join(ART, "crescent.json")
    if not os.path.exists(idx_path):
        return
    idx = json.load(open(idx_path, encoding="utf-8"))
    src = lambda fam: "cc" + fam[0] + ("r" if fam.endswith("_raw") else "")
    # identical cells (a wall, a gallery, roof or ashlar repeated across buildings) share one name, so they cost
    # one metatile, not one per building
    canon = {}
    for fam in sorted({p["sheet"] for p in idx["pieces"].values()}):
        raw = fam.endswith("_raw")  # opaque pieces (planks, flower beds) are plain metatiles, not overlays
        sheet = Image.open(os.path.join(ART, f"crescent_{fam}.png")).convert("RGB")
        seen, cells = {}, []
        for name, p in idx["pieces"].items():
            if p["sheet"] != fam:
                continue
            doors = {tuple(d) for d in p.get("doors", [])}
            for j in range(p["h"]):
                for i in range(p["w"]):
                    if [i, j] in p.get("empty", []):
                        continue
                    x, y = p["x"] + i, p["y"] + j
                    # a door cell keeps its own name (its behaviour differs); everything else is shared by its pixels
                    key = sheet.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16)).tobytes() + (b"door" if (i, j) in doors else b"")
                    if key not in seen:
                        seen[key] = f"{name}_{i}{j}"
                        cells.append({"id": seen[key], "bottom": [x, y]})
                    canon[(name, i, j)] = f"{src(fam)}:{seen[key]}"
        r["sources"].append({"name": src(fam), "type": "image", "transparent": [[255, 0, 255]], "overlay_only": not raw,
                             "image": f"tools/mapgen/sources/orleans_custom/crescent_{fam}.png",
                             "_comment": f"Crescent City's own art, {fam} colours (make_crescent_art.py).",
                             "metatiles": cells})
    for name, p in idx["pieces"].items():
        doors = [tuple(d) for d in p.get("doors", [])]
        raw = p["sheet"].endswith("_raw")
        rows = [[None if [i, j] in p.get("empty", []) else canon[(name, i, j)] if raw else
                 dict({"overlay": canon[(name, i, j)]},
                      **({"behavior": DOOR} if (i, j) in doors else {"behavior": "MB_TALL_GRASS"} if name.startswith("pgrass")
                         else {}))
                 for i in range(p["w"])] for j in range(p["h"])]
        pf = {"_comment": p.get("comment", "Crescent City own art."), "rows": rows}
        if doors:
            pf["door"] = list(doors[0]) if len(doors) == 1 else [list(d) for d in doors]
        if p.get("passable"):
            pf["passable"] = p["passable"]
        c["prefabs"][name] = pf
    # the Battle Frontier's facilities (the post-game, Chapter 10): the hall's one door is the middle cell of the bottom row (the art's door), a
    # non-animated door like every other building's, so the plaza leads into each facility's lobby (crescent.py gives each its lobby as "interior")
    for name in [n for n in idx["pieces"] if n.startswith("fac_")]:
        pf = c["prefabs"][name]
        row = pf["rows"][-1]
        dx = len(row) // 2
        row[dx] = dict(row[dx], behavior=DOOR)
        pf["door"] = [dx, len(pf["rows"]) - 1]
    def stack(name, parts, comment=None):
        """A prefab of several row blocks stacked top to bottom (prefab names or literal rows), its door carried
        down by the rows above it."""
        rows, door = [], None
        for q in parts:
            block = c["prefabs"][q]["rows"] if isinstance(q, str) else q
            if isinstance(q, str) and c["prefabs"][q].get("door"):
                dx, dy = c["prefabs"][q]["door"]
                door = [dx, dy + len(rows)]
            rows += block
        pf = {"_comment": comment or " / ".join(c["prefabs"][q]["_comment"] for q in parts if isinstance(q, str)),
              "rows": rows}
        if door:
            pf["door"] = door
        c["prefabs"][name] = pf

    for name, parts in idx.get("combos", {}).items():  # pieces split across sheets, stacked back together
        stack(name, parts)
    # the French Quarter's townhouses: Brick City's slate roof over our Creole facades (Trade House: a lower roof)
    for name in [n for n in idx["pieces"] if n.startswith("creole_")]:
        w = idx["pieces"][name]["w"]
        r_rows = roof(w)
        if name in ("creole_trades", "creole_gamecorner", "creole_icecream", "creole_daycare", "creole_namerater",
                    "creole_tutor"):  # one storey lower under the roof (they stand in five-row plots)
            r_rows = [r_rows[0], r_rows[2]]
        stack("house_" + name[len("creole_"):], [r_rows, name], comment=f"Creole townhouse ({name[7:]}): slate roof over "
              "a stucco facade with an iron gallery (own art).")
