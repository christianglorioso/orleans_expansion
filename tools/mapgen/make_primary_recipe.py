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
]
# patches taken over from the route tileset (the canonical green-route recipe): their sources are all in the primary
WANT_PATCH = ("cypress_", "path_i", "tallgrass_marsh")


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
        cur["patches"] = [p for p in route["patches"] if p["id"].startswith(WANT_PATCH)]
        cur["shared"] = SHARED
        # grass and water must come out exact: keep the colours the route tileset keeps, plus the water the ekat sheet uses
        # (filled in by the caller via keep_colors once known)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, indent=1)
    print("wrote", path, "(prune only)" if "--prune-only" in args else "(pruned + shared terrain)")


if __name__ == "__main__":
    main(sys.argv[1:])
