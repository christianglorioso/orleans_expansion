"""Legendary lairs, batch 1 (user-approved 2026-10-13): the seven lairs and the six route entrances that lead to them.

    lair                         map                       off            opens
    the rougarou (night only)    Route14_RougarouHollow    Route 14       the flood flag of chapter 7 (FLAG_BADGE06_GET: the water is down, the road is open)
    Bloodmoon Ursaluna (night)   Route23_BloodmoonArroyo   Route 23       story 45 (the post-game)
    Articuno                     PointeRouge_IcePlant      Pointe Rouge   the room already exists (warp 8); Articuno from story 45
    Celebi                       Route7_CelebiGlade        Route 7        story 45
    Suicune                      Route11_SuicuneIsle       Route 11       story 45 (by Surf: the island)
    Raikou                       Route2_RaikouClearing     Route 2        story 45
    Entei                        Route16_EnteiField        Route 16       story 45

The lair maps are built by lairs.py from the approved mocks (tilesets/lairs/lair_mocks.py); this module is data only:
  * LAIRS: where each lair is, its tileset, music, and the cell the lair's exit puts the player on;
  * ROUTES: the story overlay of the six routes (story_overlay.py merges it): each entrance is a spec "gates" state (build.py gates()):
    map.bin holds the SEALED look, <Route>_EventScript_State<Name> (generated) setmetatile's the open one; and the coord triggers on the way
    in (marked "gate": the terrain does not shape around them). A trigger fires while FLAG_TEMP_1 is set: the route's OnLoad sets it when the way
    is open, so a sealed entrance never has a live trigger. The scripts are in tools/mapgen/story/<Route>.inc and <Lair>.inc.
The encounter objects (FLAG_PG_*) are listed in story_data_ch10.py (their map and cell); the rougarou is here.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ENT = json.load(open(os.path.join(HERE, "tilesets", "lairs", "entrances.json"), encoding="utf-8"))["pieces"]
FACE = "MOVEMENT_TYPE_FACE_"
TRIG = "FLAG_TEMP_1"      # armed by the route's / lair's OnLoad (see the module doc)

# key: lair map, its route, the mock (tilesets/lairs/lair_mocks.py), its tileset, music, the cell the lair's exit puts the player on (x, y, facing),
# `approach`: a walkable cell on the route's side of the entrance (the entrance checks flood-fill from it)
LAIRS = {
    "rougarou": dict(map="Route14_RougarouHollow", route="Route14", mock="rougarou", tileset="orleans_lairs_wet", prefix="lw", primary="orleans_general",
                     music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_14", back=(25, 30, "LEFT"), approach=(24, 30), opens="FLAG_BADGE06_GET"),
    "ursaluna": dict(map="Route23_BloodmoonArroyo", route="Route23", mock="ursaluna", tileset="orleans_lairs_dry", prefix="ld", primary="orleans_general",
                     music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_23", back=(22, 2, "DOWN"), approach=(22, 3), opens="story 45"),
    "celebi": dict(map="Route7_CelebiGlade", route="Route7", mock="celebi", tileset="orleans_lair_rootkin", prefix="lk", primary="orleans_general",
                   music="MUS_SURF", mapsec="MAPSEC_ROUTE_7", back=(34, 3, "DOWN"), approach=(34, 4), opens="story 45"),
    "suicune": dict(map="Route11_SuicuneIsle", route="Route11", mock="suicune", tileset="orleans_lairs_wet", prefix="lw", primary="orleans_general",
                    music="MUS_SURF", mapsec="MAPSEC_ROUTE_11", back=(28, 22, "DOWN"), approach=(28, 22), opens="story 45"),
    "raikou": dict(map="Route2_RaikouClearing", route="Route2", mock="raikou", tileset="orleans_lair_storm", prefix="ls", primary="orleans_general",
                   music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_2", back=(24, 1, "DOWN"), approach=(24, 4), opens="story 45"),
    "entei": dict(map="Route16_EnteiField", route="Route16", mock="entei", tileset="orleans_lairs_dry", prefix="ld", primary="orleans_general",
                  music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_16", back=(15, 2, "DOWN"), approach=(15, 4), opens="story 45"),
}
# where the player stands to talk to the lair's encounter (cell, the direction to face): the cell south of it, but Entei's south neighbour is a vent
STAND = {"rougarou": ((9, 9), "U"), "ursaluna": ((10, 9), "U"), "celebi": ((10, 11), "U"), "suicune": ((10, 8), "U"), "raikou": ((10, 11), "U"),
         "entei": ((10, 10), "L"), "articuno": ((9, 6), "U")}
# the lair's arrival cell and the exit trigger cells (every outdoor lair is 20 x 16 with its way in at x 10-11, rows 14-15)
ARRIVE = (10, 13)
EXITS = [(10, 14), (11, 14)]

# the rougarou's object (the others are the post-game statics of story_data_ch10.py): night only until it is caught
ROUGAROU = {"id": "LOCALID_ROUTE14_ROUGAROU_HOLLOW_ROUGAROU", "gfx": "OBJ_EVENT_GFX_SPECIES(LYCANROC_MIDNIGHT)", "move": FACE + "DOWN", "text": "", "custom": True,
            "flag": "FLAG_HIDE_ROUTE14_ROUGAROU"}


# ---------------------------------------------------------------------------------------------- entrances
def piece(name, x, y, walk_rows=()):
    """the cells of the entrance art `name` placed with its top-left cell at (x, y): [{"x", "y", "overlay": "lent:i_j", "collision"}];
    collision 0 on the rows (offsets from y) in walk_rows, else 1"""
    p = ENT[name]
    return [{"x": x + i, "y": y + j, "overlay": f"lent:{p['x'] + i}_{p['y'] + j}", "collision": 0 if j in walk_rows else 1}
            for j in range(p["h"]) for i in range(p["w"])]


def fill(block, edge, x0, y0, w, h):
    """close a notch in a wall: the wall block over rows y0..y0+h-1, the south edge cell on the row below"""
    cells = [{"x": x, "y": y, "tile": block(x, y), "collision": 1} for y in range(y0, y0 + h) for x in range(x0, x0 + w)]
    return cells + [{"x": x, "y": y0 + h, "tile": edge(x), "collision": 1} for x in range(x0, x0 + w)]


def swamp(x, y):
    return f"bd:swamp_canopy_{x & 1}{y & 1}"


def dry(x, y):
    return f"bd:dry_scrub_{x & 1}{y & 1}"


def trig(cells, script):
    return [{"x": x, "y": y, "elevation": 3, "var": TRIG, "value": 1, "script": script, "gate": True} for x, y in cells]


ROUTES = {
    # Route 14: the canopy as built is the sealed look; the trail opens east of the pond into the trees (2 x 2 overlay at (25, 30): the fringe and the mouth,
    # all four cells walkable; the player steps east onto the mouth, (26, 30) or (26, 31))
    "Route14": {
        "keep_open": [[21, 29]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "gates": {"RougarouOpen": {"open": piece("canopy_gap_w", 25, 30, walk_rows=(0, 1))}},
        "triggers": trig([(26, 30), (26, 31)], "Route14_EventScript_LairEnter"),
    },
    # Route 23: the feather notch in the north scrub (22-23, rows 0-1) is shut with the scrub block (south edge cells on row 2); the cleft overlay sits on
    # rows 1-2 (all four cells walkable) and a clawed stump beside it; the player steps north onto (22, 1) or (23, 1)
    "Route23": {
        "keep_open": [[23, 18]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "gates": {"UrsalunaOpen": {
            "open": piece("scrub_gap", 22, 1, walk_rows=(0, 1)) + piece("claw_stump", 21, 2),
            "sealed": fill(dry, lambda x: f"bd:dry_S_dry_{x & 1}", 22, 0, 2, 2)}},
        "triggers": trig([(22, 1), (23, 1)], "Route23_EventScript_LairEnter"),
    },
    # Route 7: a Rootkin arch in the north canopy notch: a curtain of vines (sealed, solid) or the way through (the bottom row walks)
    "Route7": {
        "keep_open": [[32, 10]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "gates": {"CelebiOpen": {"open": piece("stone_arch", 34, 1, walk_rows=(1,)),
                                 "sealed": piece("stone_arch_vines", 34, 1)}},
        "triggers": trig([(34, 2), (35, 2)], "Route7_EventScript_LairEnter"),
    },
    # Route 11: the hidden island's cypress makes way for the arch (vines sealed, mist open); Surf to the island, walk north
    "Route11": {
        "keep_open": [[29, 20]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "remove_buildings": [{"prefab": "cypress_marsh", "x": 28, "y": 20}],
        "gates": {"SuicuneOpen": {"open": piece("stone_arch_mist", 28, 20, walk_rows=(1,)),
                                  "sealed": piece("stone_arch_vines", 28, 20)}},
        "triggers": trig([(28, 21), (29, 21)], "Route11_EventScript_LairEnter"),
    },
    # Route 2: no new art (the Port tileset is full): the notch in the canopy (24-25, rows 0-1) is shut with the canopy block (primary pieces);
    # open, the notch as built, walkable
    "Route2": {
        "keep_open": [[25, 14]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "gates": {"RaikouOpen": {
            "open": [{"x": x, "y": y, "collision": 0} for y in (0, 1, 2) for x in (24, 25)],
            "sealed": fill(swamp, lambda x: f"patch:bdg_swamp_S{x & 1}_542aa1ca", 24, 0, 2, 2)}},
        "triggers": trig([(24, 0), (25, 0)], "Route2_EventScript_LairEnter"),
    },
    # Route 16: the notch in the north scrub above the pepper fields (14-17, rows 0-1) is shut with the scrub block; the cleft sits on rows 1-2 (x 15-16),
    # a charred stake beside it (17, rows 2-3)
    "Route16": {
        "keep_open": [[18, 10]],     # where the legendary stood before it moved into its lair: the walls keep their shape
        "gates": {"EnteiOpen": {
            "open": piece("scrub_gap", 15, 1, walk_rows=(0, 1)) + piece("charred_stake", 17, 2),
            "sealed": fill(dry, lambda x: f"bd:dry_S_dry_{x & 1}", 14, 0, 4, 2)}},
        "triggers": trig([(15, 1), (16, 1)], "Route16_EventScript_LairEnter"),
    },
}
