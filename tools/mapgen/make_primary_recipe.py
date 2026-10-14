"""(Re)write tilesets/recipes/orleans_general.json, the shared primary (edges pass, decisions 1 and 2).

usage (from the decomp root):  python tools/mapgen/make_primary_recipe.py [--prune-only]

The primary is the HnS Johto general set pruned to the pieces the Orleans maps use (tilesets/primary_keep.json, written by
primary_keep.py; every kept piece stays at its old metatile id) plus the SHARED TERRAIN that every route/town secondary used
to carry its own copy of:
  tier 1  grass, the marsh set (+ plants), the water set (+ lily, weeds), the marsh-water bank set, tall grass
  tier 2  the cypress canopy pieces on marsh and water, the mud set and the mud-water bank set
  plus    the four path inner corners, the tall grass on marsh patch
They fill the metatile slots the prune freed. The Ekat swamp sheet is cut exactly as the route tileset cuts it (same sheet,
same recolouring: "own_recolor") so a secondary finds its piece identical to the primary's and drops its own copy
(compose.py: drop_shared); any secondary whose copy differs keeps it.
--prune-only writes the pruned Johto set without the shared terrain (the decision-1 checkpoint).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECIPES = os.path.join(HERE, "tilesets", "recipes")

# metatile names (regexes over "source:name") that live in the primary
SHARED = [
    r"^patch:ovl_lmk_",        # the rail track and boxcar (route landmark art) over paving and grass: rails may run through a seam band
    r"^ekat:grass$",
    r"^ekat:marsh_",           # marsh set + plants (marsh_C, edges, corners, land*, saddles, marsh_plants*)
    r"^ekat:marshwater_",      # marsh-water bank
    r"^ekat:water_",           # water set + lily pad + weeds
    r"^ekat:tallgrass$",
    r"^ekat:mud_",             # mud set (+ plants)
    r"^ekat:mudwater_",        # mud-water bank
    r"^patch:cypress_",        # cypress canopy on marsh / water (big and small)
    r"^patch:path_i",          # Johto path inner corners
    r"^patch:tallgrass_marsh$",
    r"^patch:pier_",           # the Olivine/Route 40 plank dock over grass, water and banks (piers may stand in a band)
    r"^brg:",                  # the railed road bridge's own pieces ...
    r"^patch:ovl_brg_",        # ... and its overlays on water / grass / banks (tilesets/orleans_general.blends.json)
    r"^patch:ovl_mag_",        # the magnolia and the street furniture (lamp, bench ...) over grass / paving: props may stand in a band
    r"^patch:ovl_props_",
    r"^patch:bdg_",            # swamp border edge cells baked over grass (tilesets/orleans_general.blends.json)
    r"^bd:swamp_",             # border art, swamp style (make_borders.py): canopy block, wall-edge cells on marsh and water
    r"^dry:0_0$",              # the plain dry-country ground: the ONE dry fill a seam band may hold
    r"^pss:",                  # the art agent's primary seam-band art (rocks awash / cypress knee on water, Johto path on dry ground), tilesets/primary_seam_art
]
LMK_IDS = ("15_9", "8_11", "9_11", "10_11", "8_12", "9_12", "10_12")   # track, boxcar top row, boxcar bottom row
# patches taken over from the route tileset (the canonical green-route recipe): their sources are all in the primary
WANT_PATCH = ("cypress_", "path_i", "tallgrass_marsh", "pier_")


def main(args):
    route = json.load(open(os.path.join(RECIPES, "orleans_route.json"), encoding="utf-8"))
    path = os.path.join(RECIPES, "orleans_general.json")
    cur = json.load(open(path, encoding="utf-8"))
    for k in ("keep_file", "shared", "palette", "patches", "own"):
        cur.pop(k, None)
    cur["sources"] = [s for s in cur["sources"] if s["name"] == "johto"]
    cur["_comment"] = ("Orleans primary: HnS Johto general pruned to what the maps use (primary_keep.json; kept pieces keep their "
                       "old ids) + the shared terrain every secondary used to copy (make_primary_recipe.py). Written by "
                       "make_primary_recipe.py; edit that, not this.")
    cur["keep_file"] = "primary_keep.json"
    cur["palette"] = "v2"
    if "--prune-only" not in args:
        ekat = [s for s in route["sources"] if s["name"] == "ekat"][0]
        ekat = dict(ekat)
        # recoloured exactly the way a secondary recolours it: the primary's table + the route recipe's, with its tolerance
        ekat["own_recolor"] = {"table": route["recolor"], "tolerance": route.get("recolor_tolerance", 0)}
        cur["sources"].append(ekat)
        dry = [s for s in json.load(open(os.path.join(RECIPES, "orleans_route_dry.json"), encoding="utf-8"))["sources"]
               if s["name"] == "dry"][0]
        dry = {k: v for k, v in dry.items() if k != "metatiles"}
        dry["metatiles"] = [{"id": "0_0", "bottom": [0, 0]}]
        dry["own_recolor"] = ekat["own_recolor"]
        cur["sources"].append(dry)
        r40 = [s for s in route["sources"] if s["name"] == "r40"][0]
        port = json.load(open(os.path.join(RECIPES, "orleans_port.json"), encoding="utf-8"))
        brg = [s for s in port["sources"] if s["name"] == "brg"][0]
        cur["sources"] += [dict(r40), dict(brg)]
        bd = json.load(open(os.path.join(HERE, "sources", "orleans_custom", "borders.json"), encoding="utf-8"))
        cur["sources"].append({"name": "bd", "type": "image", "image": "tools/mapgen/sources/orleans_custom/borders.png",
                               "transparent": [[255, 0, 255]], "_comment": "Map border art (make_borders.py).",
                               "metatiles": [{"id": n, "bottom": list(xy)} for n, xy in sorted(bd["cells"].items())]})
        cur["blends_file"] = "orleans_general.blends.json"
        # magnolia + street furniture art (one copy of each sheet; the overlays over grass and paving live in the primary blends)
        for nm in ("mag", "props"):
            ids, src = {}, None
            for t in ("orleans_port", "orleans_crescent", "orleans_town", "orleans_camp", "orleans_harbor"):
                rr = json.load(open(os.path.join(RECIPES, t + ".json"), encoding="utf-8"))
                for x in rr["sources"]:
                    if x["name"] == nm and (src is None or x["image"] == src["image"]):
                        src = src or dict(x)
                        ids.update({m["id"]: m for m in x["metatiles"]})
            src["metatiles"] = [ids[k] for k in sorted(ids)]
            cur["sources"].append(src)
        # rail track + boxcar art (Pointe Rouge's rail yard runs through its seam bands): just the 7 landmark cells it uses
        lmk = json.load(open(os.path.join(HERE, "sources", "orleans_custom", "route_landmarks.json"), encoding="utf-8"))["source"]
        lmk["metatiles"] = [m for m in lmk["metatiles"] if m["id"] in LMK_IDS]
        cur["sources"].append(lmk)
        pss = json.load(open(os.path.join(HERE, "tilesets", "primary_seam_art", "sources", "orleans_general.pss.json"), encoding="utf-8"))
        pss["metatiles"] = [m for m in pss["metatiles"] if m["id"].startswith(("w_", "pd_"))]      # specs B and D; the scrub (A) lives in the dry secondaries' reserved window
        cur["sources"].append(pss)
        cur["keep_names"] = ["pss:", "patch:tallgrass_marsh", "ekat:grass", "ekat:tallgrass", "ekat:marsh_C", "ekat:water_C"]      # + the pieces gen_metatile_labels.py names for the engine
        cur["drop_names"] = json.load(open(os.path.join(HERE, "tilesets", "primary_drop_names.json"), encoding="utf-8"))["names"]      # compose.sparse_primary: unplaced shared pieces nobody reuses a tile of (seams review)
        cur["patches"] = [p for p in route["patches"] if p["id"].startswith(WANT_PATCH)]
        cur["shared"] = SHARED
        # grass and water must come out exact: keep the colours the route tileset keeps, plus the water the ekat sheet uses
        # (filled in by the caller via keep_colors once known)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, indent=1)
    print("wrote", path, "(prune only)" if "--prune-only" in args else "(pruned + shared terrain)")


if __name__ == "__main__":
    main(sys.argv[1:])
