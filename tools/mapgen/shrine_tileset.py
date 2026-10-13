"""The Oldest Shrine's own art (tilesets/arenas/shrine.png + shrine.json, made by make_shrine.py) on the route_b variant (orleans_route_b).
make_route_tilesets.py calls apply(r, c) after copying the route set (VARIANTS["orleans_route_b"]["addon"]); the variant stays demand-driven
(compose keeps only what Route 14 and the shrine place), palette v2.

shrine.json carries everything: "sources" (osh = opaque pieces, osho = overlays drawn over the ground under them), "autotile" (the corner
sets berm and mound) and "prefabs" (the overlay pieces, the mound steps and the landing). This module only wires it in:

    terrain   R the low ridges (blocking, grass-coloured berms, the dual-grid set `berm` on grass)
              U the platform mound (the set `mound`: its edges and south face block, its top is plain walkable grass)
              (the art's own letter for the mound is M, but build.py clears M, H, K and P to grass as mockup building marks)
    prefabs   mound_steps, landing, singing_stone, live_oak, cedar_post, cedar_post_bird, stone_tall, stone_small, egret_post, shell_scatter
              (from shrine.json) and shell_road_w / shell_road_e (the 1x1 road halves), marsh_plants_a / marsh_plants_b (the primary's
              marsh plant cells as one-cell props, for the seam band)
Nothing here imports build.py.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "tilesets", "arenas", "shrine.json")


def load():
    return json.load(open(ART, encoding="utf-8"))


def apply(r, c):
    doc = load()
    names = {s["name"] for s in doc["sources"]}
    r["sources"] = [s for s in r["sources"] if s["name"] not in names]
    r["sources"] += json.loads(json.dumps(doc["sources"]))
    T, A, P = c["terrain"], c["autotile"], c["prefabs"]
    for key in ("berm", "mound"):
        A[key] = json.loads(json.dumps(doc["autotile"][key]))
    A["mound"]["connects"], A["mound"]["apply_on"] = "U", "U."
    A["mound"]["open_center"] = True     # build.corners(): the C piece (the mound's top) does not block
    T["R"] = {"name": "ridge (blocking berm)", "tile": "osh:berm_C", "elev": 3, "collision": 1}
    T["U"] = {"name": "platform mound (edges and face block, the top walks)", "tile": "ekat:grass", "elev": 3}
    # the art's prefabs, minus the shell road (placed as 1x1 halves below)
    for name, pf in doc["prefabs"].items():
        P[name] = json.loads(json.dumps(pf))
    P["shell_road_w"] = {"_comment": "The shell road's west half (1 wide): walkable.", "rows": [["osh:shell_W"]], "door": None, "passable": [[0, 0]]}
    P["shell_road_e"] = {"_comment": "The shell road's east half (1 wide): walkable.", "rows": [["osh:shell_E"]], "door": None, "passable": [[0, 0]]}
    P["marsh_plants_a"] = {"_comment": "One marsh plant cell (primary), a prop on marsh.", "rows": [["ekat:marsh_plants1"]], "door": None, "passable": [[0, 0]]}
    P["marsh_plants_b"] = {"_comment": "One marsh plant cell (primary), a prop on marsh.", "rows": [["ekat:marsh_plants3"]], "door": None, "passable": [[0, 0]]}
    return True
