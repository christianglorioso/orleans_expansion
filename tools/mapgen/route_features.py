"""Route landmarks and natural details on top of the mockup's terrain (read by firstpass.py).

The generator keeps each mockup's terrain, roads and water; this table adds what the mockups mark on top of it:
structures, signs, labelled features, special spots, hidden items. Coordinates are mockup tiles (routes aren't
scaled, so they are map cells too; the x, y of a prop is its top-left cell).

PLANS      route -> [(label, prefab, (x, y, w, h) mockup rect)]  buildings with a door (closed: no interior), merged
           into town_plans.ROUTE_PLANS: centred on the rect, bottom-aligned, with a door path carved to them.
FEATURES   route -> dict with
  "terrain": painted over the normalised mockup before anything else: ("rect", x, y, w, h, char) or
             ("colour", (r, g, b), char[, (x0, y0, x1, y1)]) = the mockup tiles of that key colour (within a box).
  "props":   (prefab, x, y, label[, opts]) placed at the nearest free spot after the greenery. opts: on (grid
             chars the footprint may stand on; default plain ground and marsh), reach (search radius, default 2),
             ring (cells round it cleared to plain ground / painted with patch, default 0 / 1), patch (char painted
             under it and round it, e.g. '"' for a marsh tree).
  "lines":   (prefab, x0, y0, x1, y1, label) a run of 1x1 pieces along a row or column, skipping road and water.
  "signs":   (x, y, text) a signpost near that spot.
  "hidden":  (item const, label[, x, y[, opts]]) a hidden item at the mockup's n-th hidden-item marker (or at x, y).
             opts: water (the cell may be water: Surf), occ (the cell may be under a dock/prop).
PLACEHOLDERS  art that isn't drawn yet (tools/mapgen/art_requests/route_landmarks.md). The generator uses the real
           prefab of that name as soon as a tileset config has it, otherwise a stand-in of the same footprint:
           name: (stand-in prefab, pattern or None for the stand-in's own rows, walkable). pattern: one string per row,
           '#' = a tile of the stand-in (tiled over the pattern), '.' = leave the terrain.
"""

PLACEHOLDERS = {
    "power_tower": ("lamp", ["##", "##", "##", "##"], False),          # 2x4 transmission tower
    "fallen_line": ("boulder", ["##"], False),                               # 2x1 sparking fallen power line
    "lookout": ("cabin", None, False),                                 # 3x4 shore lookout hut on stilts
    "rail_h": ("boulder", ["#"], True), "rail_v": ("boulder", ["#"], True),    # 1x1 track pieces (walkable across)
    "rail_car": ("boulder", None, False),                              # 3x2 freight car
    "chimney": ("lamp", ["#", "#", "#", "#", "#"], False),             # 1x5 mill chimney
    "levee_gate": ("lamp", ["#..#", "#..#"], False),                   # 4x2 gate posts, the road passes between
    "channel_buoy": ("snag_water", None, False),                       # 1x2 buoy / piling in water
    "sunken_ruin": ("snag_water", None, False),                        # 1x2 broken pillar in water
    "nav_beacon": ("cypress_small_water", None, False),                # 2x3 navigation beacon on water
    "shipwreck": ("boat", None, False),                                # 4x3 half-sunk hull
    "bird_platform": ("dock_h", None, False),                          # 6x3 heron platform
    "offshore_platform": ("dock_h", None, False),                      # 6x3 abandoned platform
    "shrine_steps": ("dock_h", None, False),                           # 6x3 stone steps of the oldest shrine
    "temple_gate": ("cave_mouth", None, False),                        # 3x2 drowned-temple entrance
    "mine_mouth": ("cave_mouth", None, False),                         # 3x2 mine tunnel mouth
    "oyster_bed": ("boulder", None, False),                            # 3x2 shell heap
    "scorched_cypress": ("cypress_marsh", None, False),                # 3x3 lightning-struck cypress
    "cut_stump": ("boulder", ["#"], False),                            # 1x1 cut stump (art requested)
    "felled_log": ("boulder", ["###"], False),                         # 3x1 felled trunk (art requested)
    "great_oak": ("cypress_marsh", None, False),                       # 3x3 (art: bigger) great live oak
}

# routes whose road is drawn dead straight like their mockup (no natural.py bulges and drifts)
STRAIGHT = {"route_14"}

PLANS = {
    "route_2": [("Seaside lookout", "lookout", (37, 13, 5, 3))],
}


def tree_wall(prefab, x, y0, y1, gaps, step=3, lean=1):
    """A bank of trees down a column, a tree every `step` rows (leaning a column to one side every other row),
    except where a gap (a, b) covers it."""
    return [(prefab, x + (lean if (y // step) % 2 else 0), y, "Tree", {"patch": '"', "reach": 1})
            for y in range(y0, y1, step) if not any(a - 2 <= y <= b for a, b in gaps)]


FEATURES = {
    "route_2": {
        "spans": ("power_tower", "wire_span"),     # overhead wires along the towers' top row (wire_span_l / wire_span / wire_span_r)
        "terrain": [("colour", (242, 226, 180), "L")],                 # the sand beach (mud until sand is drawn)
        # world seams (phase 2): the west road is 2 wide (Grand Oak's rows 14-15), the lake keeps off the west edge (Grand Oak's lawn
        # runs to the border there), the east road is 2 wide (Storm's Edge's street rows 12-13)
        "terrain_edges": [("rect", 0, 8, 8, 1, "."), ("rect", 0, 20, 6, 6, "."), ("rect", 6, 21, 1, 5, "."), ("rect", 43, 10, 7, 1, "."), ("rect", 44, 20, 6, 3, "."), ("rect", 46, 23, 4, 1, ".")],   # + a grass spit at the east edge where Storm's quay (rows 21-23) lands
        "props": [("power_tower", 7, 3, "Transmission tower", {"reach": 4}),
                  ("power_tower", 19, 3, "Transmission tower", {"reach": 4}),
                  ("power_tower", 31, 3, "Transmission tower", {"reach": 4}),
                  ("power_tower", 43, 3, "Transmission tower", {"reach": 4}),
                  ("fallen_line", 23, 8, "Fallen power line"), ("fallen_line", 26, 9, "Fallen power line"),
                  ("fallen_line", 24, 10, "Fallen power line"),
                  ("pirogue", 15, 20, "Fishing boat", {"on": "~"})],
        "signs": [(22, 7, "DANGER\nLive wires down. Keep clear!"),
                  (20, 7, "HIGH-VOLTAGE LINE\nThe towers hum in a storm."),
                  (36, 13, "SEASIDE LOOKOUT\nThe boats are best from here.")],
        "hidden": [("ITEM_THUNDER_STONE", "Thunder Stone at the lookout")],
    },
    "route_3": {
        "terrain": [("rect", 22, 9, 6, 2, ":")],                       # the rest stop's yard, off the causeway
        "terrain_edges": [("rect", 0, 21, 4, 3, "~"), ("rect", 4, 22, 2, 2, "~")],   # Storm's Edge's bay (its east edge, rows 22+) carries on
        "props": [("bench", 23, 8, "Bench"), ("bench", 26, 8, "Bench"), ("lamp", 22, 6, "Lamp")],
        "signs": [(28, 8, "REST STOP\nWater and shade for travellers."),
                  (3, 9, "CAUSEWAY ROAD\nStorm's Edge west, Crescent City east.")],
        "hidden": [("ITEM_REVIVE", "under the bridge")],
    },
    "route_4": {
        # world seams: Pointe Rouge's south edge is lawn and paving over these columns (its river opens 21 cells further east), so the
        # river starts below a lawn headland and the road keeps 4 wide ground at the edge
        "terrain_edges": [("rect", 19, 0, 9, 6, "."), ("rect", 22, 6, 6, 1, "."), ("rect", 24, 7, 4, 1, ".")],
        "lines": [("rail_v", 4, 6, 4, 39, "Rail line"), ("rail_v", 6, 6, 6, 39, "Rail line")],
        "signs": [(17, 8, "POINTE ROUGE FREIGHT YARD\nAuthorized personnel only."),
                  (20, 38, "RIVERBOAT LANDING\nTickets at the office.")],
    },
    "route_5": {
        "terrain": [("rect", 30, 18, 8, 5, '"')],                      # the reed bed
        "props": [("reeds_marsh", 31, 19, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("reeds_marsh", 34, 19, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("reeds_marsh", 32, 21, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("reeds_marsh", 36, 21, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("channel_buoy", 21, 14, "Tournament float", {"on": "~", "reach": 3})],
        "signs": [(35, 9, "ANGLER'S SHACK\nGood Rod handed out to all comers."),
                  (30, 17, "REED BED\nSomething rare hides in the reeds.")],
        "hidden": [("ITEM_STARDUST", "in the reeds")],
    },
    "route_6": {
        "props": [("sunken_ruin", 19, 7, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin", 23, 12, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin_l", 32, 13, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin_l", 46, 7, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin", 43, 15, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin", 9, 15, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin", 16, 19, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("waterlog", 31, 19, "Floating debris", {"on": "~", "reach": 3}),
                  ("waterlog", 34, 20, "Floating debris", {"on": "~", "reach": 3}),
                  ("waterlog", 36, 18, "Floating debris", {"on": "~", "reach": 3})],
        "hidden": [("ITEM_PEARL", "on the island")],
    },
    "route_7": {
        "props": [("shrine", 16, 3, "Celebi shrine", {"patch": '"', "reach": 3}),
                  ("cut_stump", 24, 19, "Cut stump (Kleavorite)", {"reach": 3}),
                  ("felled_log", 22, 21, "Felled trunk"), ("felled_log", 26, 20, "Felled trunk"), ("felled_log", 27, 22, "Felled trunk")],
        "signs": [(18, 5, "THE OLDEST CYPRESS\nA shrine to the forest's keeper."),
                  (23, 18, "OLD LOGGING RUN\nThe trunks floated down from here.")],
        "hidden": [("ITEM_STAR_PIECE", "at the cypress landing")],
    },
    "route_8": {
        "terrain": [("rect", 25, 6, 6, 6, ".")],                       # the lightning-struck cypress's island, a little roomier
        "props": [("scorched_cypress", 27, 7, "Lightning-struck cypress", {"patch": '"', "reach": 3})],
        "signs": [(31, 10, "LIGHTNING-STRUCK CYPRESS\nThe air still hums with static.")],
        "hidden": [("ITEM_MAX_ETHER", "on the island")],
    },
    "route_9": {
        "signs": [(18, 9, "CAMP COCODRIE\nGator wranglers' trail leads north."),
                  (29, 12, "BOAT LANDING\nBoats leave for the open bayou lake.")],
        "hidden": [("ITEM_REVIVE", "under the boardwalk")],
    },
    "route_10": {
        "props": [("channel_buoy", 20, 12, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 30, 9, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 40, 6, "Channel marker", {"on": "~", "reach": 3}),
                  ("reeds_marsh", 16, 21, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("reeds_marsh", 19, 23, "Reeds", {"on": '"', "patch": '"', "ring": 0}),
                  ("reeds_marsh", 21, 21, "Reeds", {"on": '"', "patch": '"', "ring": 0})],
        "signs": [(13, 17, "CRESCENT CITY LAKEFRONT\nBoats for the big lake leave here.")],
        "hidden": [("ITEM_PEARL", "on a floating marker", 29, 7, {"water": True})],
    },
    "route_11": {
        "props": [("nav_beacon", 24, 13, "Navigation beacon", {"on": "~", "reach": 3}),
                  ("channel_buoy", 10, 22, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 38, 8, "Channel marker", {"on": "~", "reach": 3}),
                  ("cypress_marsh", 29, 21, "Hidden island's cypress", {"patch": '"', "reach": 2})],
        "hidden": [("ITEM_ETHER", "at the beacon", 26, 14, {"water": True})],
    },
    "route_12": {
        "props": [("cypress_marsh", 21, 17, "Tree", {"patch": '"'}), ("cypress_marsh", 24, 18, "Tree", {"patch": '"'}),
                  ("cypress_small_marsh", 26, 21, "Tree", {"patch": '"'}),
                  ("cypress_small_marsh", 22, 22, "Tree", {"patch": '"'}),
                  ("cypress_marsh", 25, 23, "Tree", {"patch": '"'}),
                  ("great_oak", 6, 31, "Great live oak", {"patch": '"', "reach": 3})],
        "signs": [(19, 22, "OVERGROWN GROVE\nSomething stirs among the trees."),
                  (10, 34, "GREAT LIVE OAK\nIts roots coil like a serpent.")],
        "hidden": [("ITEM_ELIXIR", "in the clearing")],
    },
    "route_13": {
        "props": [("shrine", 9, 21, "Meadow shrine", {"patch": '"', "reach": 3})],
        "signs": [(8, 19, "MEADOW SHRINE\nFlowers are left here for Flabébé."),
                  (19, 8, "THE MIST THICKENS\nStay on the path.")],
        "hidden": [("ITEM_MAX_ELIXIR", "by the shrine")],
    },
    "route_14": {
        "props": [("levee_gate", 12, 21, "Levee gate", {"reach": 1})],
        "signs": [(11, 23, "LEVEE GATE\nClosed to carts after dark.")],
        "hidden": [("ITEM_MAX_REPEL", "at the levee gate")],
    },
    "route_15": {
        "share": 0,        # encounter cane only in the mockup's clearings
        "walls": True,     # the rest is blocking cane wall (dry_finish), a dry verge along the roads
        "signs": [(6, 5, "SUNKEN CANE CO.\nHarvest burn at dusk. Mind smoke.")],
        "hidden": [("ITEM_NUGGET", "at the field's edge")],
    },
    "route_16": {
        "share": 0,        # encounter pepper only in the mockup's three green patches
        "base": "e",       # red-earth ground (the mockup is orange-dotted all over)
        "encounter": "g",  # the encounter patches are tall dry grass (walk-in pepper would look like the blocking beds)
        "beds": 0.5,       # blocking pepper beds over this share of the open ground (dry_finish)
        "signs": [(4, 11, "PEPPER FIELDS\nPickers wanted. Mind the heat.")],
        "hidden": [("ITEM_FIRE_STONE", "Fire Stone")],
    },
    "route_17": {
        "lines": [("rail_h", 0, 16, 45, 16, "Rail line")],   # row 16 = Redfield's rail (row 21) across the seam
        "props": [("rail_car", 6, 15, "Rail car"), ("rail_car", 10, 15, "Rail car"), ("rail_car", 36, 15, "Rail car"),
                  ("chimney", 37, 3, "Mill chimney", {"reach": 3})],
        "signs": [(24, 10, "SUGAR MILL ROAD\nMind the rail cars.")],
        "hidden": [("ITEM_ULTRA_BALL", "beside a furnace")],
    },
    "route_18": {
        "props": [("channel_buoy", 22, 10, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 8, 15, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 34, 12, "Channel marker", {"on": "~", "reach": 3}),
                  ("channel_buoy", 46, 14, "Channel marker", {"on": "~", "reach": 3}),
                  ("boat", 16, 17, "Shrimp boat", {"on": "~", "reach": 3}),
                  ("shipwreck", 26, 14, "Half-sunk barge", {"on": "~", "reach": 3})],
        "hidden": [("ITEM_NUGGET", "on the half-sunk barge")],
    },
    "route_19": {
        "trim_shore": True,   # the bridge approach's road runs along the shore: no road cell touches the water (a seam)
        "terrain": [("rect", 7, 3, 6, 4, "."), ("rect", 30, 2, 6, 4, ".")],       # oyster bed islets in the flats
        "props": [("oyster_bed", 7, 3, "Oyster bed", {"reach": 1}), ("oyster_bed", 10, 5, "Oyster bed", {"reach": 1}),
                  ("oyster_bed", 30, 2, "Oyster bed", {"reach": 1}), ("oyster_bed", 33, 4, "Oyster bed", {"reach": 1})],
        "signs": [(34, 18, "FOSSIL DIG SITE\nThe mud here hides old bones.")],
        "hidden": [("ITEM_PEARL", "on the oyster beds")],
    },
    "route_20": {
        "terrain": [("rect", 27, 10, 7, 3, "~")],                      # the heron platform's block was read as ground
        "props": [("bird_platform", 27, 10, "Heron platform", {"on": "~", "reach": 2}),
                  ("sunken_piling", 12, 13, "Barnacled piling", {"on": "~", "reach": 3}),
                  ("sunken_piling", 24, 14, "Barnacled piling", {"on": "~", "reach": 3}),
                  ("sunken_piling", 36, 12, "Barnacled piling", {"on": "~", "reach": 3})],
        "hidden": [("ITEM_WATER_STONE", "Water Stone")],
    },
    "route_21": {
        "terrain": [("rect", 22, 12, 7, 6, "~")],                      # the abandoned platform stands in open water
        "props": [("offshore_platform", 22, 12, "Offshore platform", {"on": "~", "reach": 1})],   # one 6x6 piece
        "hidden": [("ITEM_MAX_REVIVE", "beside the platform (its deck blocks)", 21, 14, {"water": True})],
    },
    "route_22": {
        "terrain": [("rect", 34, 13, 6, 3, "~"), ("rect", 20, 8, 3, 3, "~"), ("rect", 26, 6, 3, 3, "~")],
        "props": [("sunken_ruin", 21, 8, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("sunken_ruin_l", 27, 6, "Sunken ruin", {"on": "~", "reach": 3}),
                  ("shipwreck", 34, 13, "Shipwreck", {"on": "~", "reach": 2}),
                  ("temple_gate", 4, 21, "Drowned temple gate", {"reach": 3})],
        "signs": [(3, 23, "DROWNED TEMPLE\nDive at the door. Gear needed.")],
        "hidden": [("ITEM_BIG_PEARL", "in the shipwreck", 36, 16, {"water": True})],
    },
    "route_23": {
        "props": [("shrine", 25, 3, "Azelf's ridge shrine", {"patch": '"', "reach": 3}),
                  ("cypress_marsh", 42, 23, "Tree", {"patch": '"', "reach": 2}),
                  ("cypress_small_marsh", 45, 24, "Tree", {"patch": '"', "reach": 2}),
                  ("cypress_marsh", 43, 26, "Tree", {"patch": '"', "reach": 2})],
        "share": 0.18,                          # encounter patches (tall dry grass): the mockup's, grown a little
        "encounter": "g",
        "gully": (217, 199, 154),               # the mockup's "dry riverbed" band is a 2-wide gully, not a road
        "rock_wall": {"depth": (2, 4), "mix": True},   # the north bluff: a short stepped rock wall, then the rock / tree scatter
        "stones": [("rock", 0.008), ("rock_l", 0.002)],   # the dry hills' scatter (dry_finish; dry set only)
        "signs": [(26, 6, "AZELF'S RIDGE\nA shrine stands on the heights."),
                  (4, 13, "DUST STORM WARNING\nThe road closes when the wind rises."),
                  (41, 21, "FERTILE HOLLOW\nThe ground is green here, oddly.")],
        "hidden": [("ITEM_NUGGET", "on the ridge")],
    },
    "route_24": {
        "share": 0,                  # encounter patches only where the mockup draws them
        "encounter": "g",            # tall dry grass on dry ground at the flat's margins
        "salt": (247, 246, 241),     # the mockup's salt flats (the salt set)
        "rock_wall": {"mouths": [("Dry cave", "cave_mouth", (8, 8)), ("Salt-dome cavern", "cave_mouth", (40, 21)),
                                 ("Abandoned mine tunnels (Lantern)", "mine_mouth", (46, 6))],
                      "scree": 0.1},    # the dark east face and the dry cave's block are rock_wall (dry_cliffs)
        "signs": [(43, 6, "LANTERN MINE\nTunnels abandoned.\\pEnter at your own risk."),
                  (38, 7, "SALT-DOME CAVERN\nA deep shaft. Something sleeps.")],
        "hidden": [("ITEM_HARD_STONE", "in a mine tunnel")],
    },
    "route_25": {
        "props": tree_wall("cypress_small_marsh", 2, 0, 46, [(12, 17), (29, 35)], lean=-1)
                 + tree_wall("cypress_small_marsh", 25, 0, 46, [(9, 14), (25, 30), (38, 41)])
                 + [("shrine_steps", 12, 6, "Shrine steps", {"on": '~."', "reach": 2})],
        "signs": [(19, 9, "THE OLDEST SHRINE\nThe heart of the basin lies north.")],
        "hidden": [("ITEM_RARE_CANDY", "on the shrine steps", 14, 7, {"occ": True})],
    },
}

import os as _os
if _os.environ.get("ROUTE_FEATURES_OFF"):  # baseline runs: the generator without any of the above
    FEATURES, PLANS, STRAIGHT = {}, {}, set()
