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


def trig(cells, script, elevation=3, var=TRIG):
    return [{"x": x, "y": y, "elevation": elevation, "var": var, "value": 1, "script": script, "gate": True} for x, y in cells]


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


# ---------------------------------------------------------------------------------------------- batch 2 (user-approved 2026-10-14)
# Batch 2: thirteen lairs (tile_review/set_pieces/lairs/batch2/LAYOUT_HANDOFF_batch2.md). Same scheme as batch 1, generalised per lair:
#   * LAIRS[key] gains "arrive" (the cell the route's LairEnter warp lands on), "exits" (the coord-trigger cells that warp back), "enter" (the route's
#     LairEnter script suffix), "state" (the route's gate state), "json" (the batch-2 mock's json, generated by lair_mocks_b2.py) and "kind":
#     "outdoor" (20 x 16 on gTileset_OrleansGeneral, exits are triggers), "gallery" (Zapdos: the existing map redone, the hatch is a warp) or "interior"
#     (the sugarhouse, on the building primary, the mat is a trigger);
#   * the entrances use the overlay source `le2` (entrances_b2.json); the open look is every cell of the piece walkable.
ENT2 = json.load(open(os.path.join(HERE, "tilesets", "lairs", "entrances_b2.json"), encoding="utf-8"))["pieces"]


def piece2(name, x, y, collision=0):
    """the cells of batch-2 entrance art `name` with its top-left cell at (x, y); open pieces walk on every cell (the cells the art's posts stand on
    are ground the player crosses), sealed ones block"""
    p = ENT2[name]
    return [{"x": x + i, "y": y + j, "overlay": f"le2:{p['x'] + i}_{p['y'] + j}", "collision": collision} for j in range(p["h"]) for i in range(p["w"])]


LAIRS2 = {
    "uxie": dict(map="OldWater_KnowingPool", route="OldWater", json="uxie", tileset="orleans_lair_trio", prefix="lt", primary="orleans_general", kind="outdoor",
                 music="MUS_SURF", mapsec="MAPSEC_OLD_WATER", back=(4, 6, "UP"), back_map="MAP_OLD_WATER_CANOE_DOCKS", arrive=(10, 13), exits=[(10, 14)],
                 enter=None, opens="story 45 (the Canoe Docks boatman)", approach=None, stand=((10, 6), "U")),
    "mesprit": dict(map="Route1_HeartPool", route="Route1", json="mesprit", tileset="orleans_lair_trio", prefix="lt", primary="orleans_general", kind="outdoor",
                    music="MUS_SURF", mapsec="MAPSEC_ROUTE_1", back=(26, 27, "LEFT"), arrive=(2, 8), exits=[(1, 8), (1, 9)], enter="Mesprit",
                    state="HeartPoolOpen", opens="story 45", approach=(25, 27), stand=((10, 8), "U")),
    "azelf": dict(map="Route23_UnfailingSpring", route="Route23", json="azelf", tileset="orleans_lair_field", prefix="lh", primary="orleans_general", kind="outdoor",
                  music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_23", back=(33, 2, "DOWN"), arrive=(10, 13), exits=[(10, 14), (11, 14)], enter="Azelf",
                  state="AzelfOpen", opens="story 45", approach=(33, 3), stand=((10, 10), "U")),
    "zapdos": dict(map="StormsEdge_LighthouseGallery", route="StormsEdge_Lighthouse", json="zapdos", tileset="orleans_lair_storm", prefix="ls", primary="orleans_general", kind="gallery",
                   music="MUS_RG_VERMILLION", mapsec="MAPSEC_STORMS_EDGE", back=(4, 3, "DOWN"), back_map="MAP_STORMS_EDGE_LIGHTHOUSE", arrive=(10, 12), exits=[(10, 12)],
                   enter=None, opens="the lighthouse stair (always)", approach=None, stand=((10, 10), "U")),
    "thundurus": dict(map="Route12_LeveeCrown", route="Route12", json="thundurus", tileset="orleans_lair_storm", prefix="ls", primary="orleans_general", kind="outdoor",
                      music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_12", back=(24, 22, "LEFT"), arrive=(2, 10), exits=[(1, 10), (1, 11)], enter="Thundurus",
                      state="ThundurusOpen", opens="story 45", approach=(24, 21), stand=((10, 7), "U")),
    "zarude": dict(map="Route13_DeepWood", route="Route13", json="zarude", tileset="orleans_lair_woods", prefix="lj", primary="orleans_general", kind="outdoor",
                   music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_13", back=(26, 26, "LEFT"), arrive=(2, 8), exits=[(1, 8), (1, 9)], enter="Zarude",
                   state="ZarudeOpen", opens="story 45", approach=(25, 26), stand=((10, 8), "U")),
    "ogerpon": dict(map="Route13_CourirGlade", route="Route13", json="ogerpon", tileset="orleans_lair_woods", prefix="lj", primary="orleans_general", kind="outdoor",
                    music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_13", back=(2, 25, "RIGHT"), arrive=(17, 8), exits=[(18, 8), (18, 9)], enter="Ogerpon",
                    state="OgerponOpen", opens="story 45", approach=(3, 25), stand=((10, 10), "U")),
    "tornadus": dict(map="Route3_WindsEye", route="Route3", json="tornadus", tileset="orleans_lair_woods", prefix="lj", primary="orleans_general", kind="outdoor",
                     music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_3", back=(27, 2, "DOWN"), arrive=(10, 13), exits=[(10, 14), (11, 14)], enter="Tornadus",
                     state="TornadusOpen", opens="story 45", approach=(27, 3), stand=((10, 8), "U")),
    "galar_moltres": dict(map="Route14_SpanishFort", route="Route14", json="galar_moltres", tileset="orleans_lair_fort", prefix="lf", primary="orleans_general",
                          kind="outdoor", music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_14", back=(2, 7, "RIGHT"), arrive=(17, 8), exits=[(18, 8), (18, 9)],
                          enter="SpanishFort", state="SpanishFortOpen", opens="story 45", approach=(3, 7), stand=((10, 7), "U")),
    "galar_zapdos": dict(map="Route14_BushTrack", route="Route14", json="galar_zapdos", tileset="orleans_lair_fort", prefix="lf", primary="orleans_general",
                         kind="outdoor", music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_14", back=(25, 19, "LEFT"), arrive=(2, 8), exits=[(1, 8), (1, 9)],
                         enter="BushTrack", state="BushTrackOpen", opens="story 45", approach=(24, 19), stand=((12, 9), "U")),
    "galar_articuno": dict(map="Route10_MilneburgPavilion", route="Route10", json="galar_articuno", tileset="orleans_lair_fort", prefix="lf", primary="orleans_general",
                           kind="outdoor", music="MUS_SURF", mapsec="MAPSEC_ROUTE_10", back=(30, 13, "DOWN"), arrive=(10, 13), exits=[(10, 14), (11, 14)],
                           enter="Pavilion", state="PavilionOpen", opens="story 45 (by Surf)", approach=(30, 14), stand=((10, 8), "U")),
    "moltres": dict(map="Route17_Sugarhouse", route="Route17", json="moltres", tileset="orleans_lair_sugarhouse", prefix="lm", primary="orleans_building",
                    kind="interior", music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_17", back=(33, 10, "DOWN"), arrive=(9, 12), exits=[(9, 13)], enter="Sugarhouse",
                    state="SugarhouseOpen", opens="story 45", approach=(33, 11), stand=((3, 7), "U")),
    "landorus": dict(map="Route23_BountifulField", route="Route23", json="landorus", tileset="orleans_lair_field", prefix="lh", primary="orleans_general", kind="outdoor",
                     music="MUS_RG_ROUTE24", mapsec="MAPSEC_ROUTE_23", back=(27, 37, "UP"), arrive=(10, 2), exits=[(10, 1), (11, 1)], enter="Landorus",
                     state="LandorusOpen", opens="story 45", approach=(27, 36), stand=((10, 5), "D")),
}
LAIRS.update(LAIRS2)
for _k, _v in LAIRS2.items():
    STAND[_k] = _v["stand"]


def arrive(key):
    return LAIRS[key].get("arrive", ARRIVE)


def exits(key):
    return LAIRS[key].get("exits", EXITS)


# the old encounter spots (kept shaped: the generator re-flows a wall the moment nothing stands there)
_OLD = {"Route1": [[15, 24]], "OldWater": [[24, 29]], "Route3": [[25, 13]], "Route12": [[14, 23]], "Route13": [[14, 19], [12, 25]], "Route17": [[23, 14]],
        "Route23": [[27, 19], [24, 16]], "StormsEdge": [[22, 20]], "CrescentCity": [[57, 22], [65, 35], [54, 25]]}

ROUTES2 = {
    "Route1": {"gates": {"HeartPoolOpen": {"open": piece2("spirit_gate_e", 26, 27), "sealed": piece2("spirit_gate_e_moss", 26, 27, 1)}},
               "triggers": trig([(27, 27), (27, 28)], "Route1_EventScript_LairEnterMesprit")},
    # Azelf: the notch in the north scrub (x 33-34) is shut with the scrub block over x 32-35, rows 0-1 and the south edge on row 2;
    # Landorus: the field gate at the south end of the notch (x 27-28, rows 37-38)
    "Route23": {"gates": {"AzelfOpen": {"open": piece2("grove_gap", 33, 1) + [{"x": x, "y": 0} for x in range(32, 36)] + [{"x": 32, "y": 1}, {"x": 35, "y": 1},
                                                                                {"x": 32, "y": 2}, {"x": 35, "y": 2}],
                                        "sealed": fill(dry, lambda x: f"bd:dry_S_dry_{x & 1}", 32, 0, 4, 2)},
                          "LandorusOpen": {"open": piece2("field_gate", 27, 38), "sealed": piece2("field_gate_shut", 27, 38, 1)}},
                "triggers": trig([(33, 1), (34, 1)], "Route23_EventScript_LairEnterAzelf", var="FLAG_TEMP_2") + trig([(27, 39), (28, 39)], "Route23_EventScript_LairEnterLandorus", var="FLAG_TEMP_3")},
    "Route12": {"gates": {"ThundurusOpen": {"open": piece2("levee_steps_e", 25, 22), "sealed": piece2("levee_steps_e_log", 25, 22, 1)}},
                "triggers": trig([(26, 22), (26, 23)], "Route12_EventScript_LairEnterThundurus")},
    "Route13": {"gates": {"ZarudeOpen": {"open": piece2("liana_gap_e", 26, 25), "sealed": piece2("liana_curtain_e", 26, 25, 1)},
                          "OgerponOpen": {"open": piece2("courir_gap_w_bright", 0, 25), "sealed": piece2("liana_curtain_w", 0, 25, 1)}},
                "triggers": trig([(27, 25), (27, 26)], "Route13_EventScript_LairEnterZarude") + trig([(0, 25), (0, 26)], "Route13_EventScript_LairEnterOgerpon", var="FLAG_TEMP_2")},
    "Route14": {"gates": {"SpanishFortOpen": {"open": piece2("sally_port_w", 0, 7), "sealed": piece2("sally_port_w_bricked", 0, 7, 1)},
                          "BushTrackOpen": {"open": piece2("bush_gate_e", 26, 19), "sealed": piece2("bush_gate_e_shut", 26, 19, 1)}},
                "triggers": trig([(0, 7), (0, 8)], "Route14_EventScript_LairEnterSpanishFort", var="FLAG_TEMP_2") + trig([(27, 19), (27, 20)], "Route14_EventScript_LairEnterBushTrack", var="FLAG_TEMP_3")},
    # Route 10: the pier stub stands in open water; open, its four plank cells are walkable ground (behaviour from the art), sealed it is only the pilings
    "Route10": {"gates": {"PavilionOpen": {"open": [dict(c, walk=True) for c in piece2("pier_stub", 30, 12)], "sealed": piece2("pier_pilings", 30, 12, 1)}},
                "triggers": trig([(30, 12), (31, 12)], "Route10_EventScript_LairEnterPavilion", elevation=0)},   # elevation 0 = any: the plank cells sit on the lake's elevation 1
    # Route 3: no new art (Crescent's set is full): the marsh notch (x 27-28, rows 0-2) is shut with the canopy block, open as built
    "Route3": {"gates": {"TornadusOpen": {"open": [{"x": x, "y": y, "collision": 0} for y in (0, 1, 2) for x in (27, 28)],
                                          "sealed": fill(swamp, lambda x: f"bd:swamp_S_marsh_{x & 1}", 27, 0, 2, 2)}},
               "triggers": trig([(27, 1), (28, 1)], "Route3_EventScript_LairEnterTornadus")},
    # Route 17: the mill door (33, 9): sealed as built (blocked, a sign says it is barred); open, collision 0 and the trigger
    "Route17": {"gates": {"SugarhouseOpen": {"open": [{"x": 33, "y": 9, "collision": 0}]}},
                "signs": [{"id": "MillDoor", "x": 33, "y": 9, "text": "", "custom": True}],
                "triggers": trig([(33, 9)], "Route17_EventScript_LairEnterSugarhouse")},
}
for _r, _c in _OLD.items():
    ROUTES2.setdefault(_r, {})["keep_open"] = _c
for _r, _d in ROUTES2.items():
    _into = ROUTES.setdefault(_r, {})
    for _k, _v in _d.items():
        if isinstance(_v, dict):
            _into.setdefault(_k, {}).update(_v)
        else:
            _into.setdefault(_k, []).extend(_v)


# ---------------------------------------------------------------------------------------------- the unlock gates (lair_gates.py, map_pass/lair_unlocks_spec.md)
# Every lair opens only when its trophy (src/data/achievements.h, tools/achievements/achievements_data.py) is complete AND the post-game has begun (story 45);
# the rougarou keeps its flood condition (FLAG_BADGE06_GET) and Bloodmoon Ursaluna its night-only encounter. The route OnLoad re-evaluates on every map load.
# key: (trophy constant, the armed-flag the route sets for this lair, the seal sign's cell (the blocked cell in front of the entrance) or None, the hint's requirement text)
GATES = {
    "suicune": ("ACH_WATER_COLLECTOR", "FLAG_TEMP_1", (28, 21), "Capture every Water Pokémon."),
    "entei": ("ACH_FIRE_COLLECTOR", "FLAG_TEMP_1", (15, 2), "Capture every Fire Pokémon."),
    "raikou": ("ACH_ELECTRIC_COLLECTOR", "FLAG_TEMP_1", (24, 2), "Capture every Electric Pokémon."),
    "zapdos": ("ACH_PARALYSIS_PRO", None, None, "Paralyze 25 Pokémon in the\nBattle Frontier."),
    "articuno": ("ACH_SNOW_SETTER", None, None, "Set Snow 25 times in the\nBattle Frontier."),
    "moltres": ("ACH_SUN_SETTER", "FLAG_TEMP_1", (33, 9), "Set Sun 25 times in the\nBattle Frontier."),
    "galar_zapdos": ("ACH_FIGHTERS_AND_FLIERS", "FLAG_TEMP_3", (26, 19), "Capture every Fighting and\nFlying Pokémon."),
    "galar_articuno": ("ACH_MIND_AND_WING", "FLAG_TEMP_1", (30, 13), "Capture every Psychic and\nFlying Pokémon."),
    "galar_moltres": ("ACH_NIGHT_WINGS", "FLAG_TEMP_2", (1, 7), "Capture every Dark and Flying\nPokémon."),
    "tornadus": ("ACH_TAILWIND_RIDER", "FLAG_TEMP_1", (27, 2), "Set Tailwind 25 times in the\nBattle Frontier."),
    "thundurus": ("ACH_RAIN_DANCER", "FLAG_TEMP_1", (25, 22), "Set Rain 25 times in the\nBattle Frontier."),
    "landorus": ("ACH_SANDSTORM_CALLER", "FLAG_TEMP_3", (27, 38), "Set Sandstorm 25 times in the\nBattle Frontier."),
    "zarude": ("ACH_MOSS_AND_SHADOW", "FLAG_TEMP_1", (26, 25), "Capture every Grass and Dark\nPokémon."),
    "ogerpon": ("ACH_MASK_COLLECTOR", "FLAG_TEMP_2", (1, 25), "Collect all of Ogerpon's\nmasks."),
    "uxie": ("ACH_MIST_WEAVER", None, None, "Set Misty Terrain 10 times in\nthe Battle Frontier."),
    "mesprit": ("ACH_MIST_WEAVER", "FLAG_TEMP_1", (26, 27), "Set Misty Terrain 10 times in\nthe Battle Frontier."),
    "azelf": ("ACH_MIST_WEAVER", "FLAG_TEMP_2", (33, 2), "Set Misty Terrain 10 times in\nthe Battle Frontier."),
    "celebi": ("ACH_ROOM_WARPER", "FLAG_TEMP_1", (34, 2), "Set Trick Room 10 times in the\nBattle Frontier."),
    "rougarou": ("ACH_HUNTERS_JAWS", "FLAG_TEMP_1", (25, 30), "Deal 10,000 damage with biting\nmoves."),
    "ursaluna": ("ACH_PSYCHIC_FURY", "FLAG_TEMP_1", (23, 2), "Deal 10,000 super-effective\ndamage with Psychic moves."),
}
# the route lairs with a sealed entrance in the route's map.bin: key -> the CamelCase name its scripts use
CAMEL = {k: "".join(p.title() for p in k.split("_")) for k in GATES}


# the seal signs: a custom sign (the script is generated into the route's story file by lair_gates.py) on the blocked cell in front of each sealed entrance;
# Moltres' mill door already has its MillDoor sign (hand-written, it checks the same gate)
for _k, (_ach, _arm, _cell, _req) in GATES.items():
    if _cell is None or _k == "moltres":
        continue
    ROUTES.setdefault(LAIRS[_k]["route"], {}).setdefault("signs", []).append(
        {"id": "LairSeal" + CAMEL[_k], "x": _cell[0], "y": _cell[1], "text": "", "custom": True, "gate": True})

# Rayquaza's arena (the Oldest Shrine's inner chamber, post-game): a seal sign on the cell in front of its dais names what opens it (story/OldestShrine.inc)
ROUTES.setdefault("OldestShrine", {}).setdefault("signs", []).append({"id": "ArenaSeal", "x": 16, "y": 10, "text": "", "custom": True, "gate": True})
