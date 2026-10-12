"""Explicit building plans for the first-pass towns (read by firstpass.py and interior_rooms_world.py).

The mockups draw buildings smaller than the real prefabs (a 3x3 house box vs a 5x5 house), and extraction
merges or misses some of them, so each town lists its buildings by hand: the mockup rectangle (x, y, w, h in
mockup tiles), the prefab, and the interior room it leads to (None: no interior yet, e.g. the post-game
Battle Frontier). The town is scaled up by SCALE so the prefabs fit where the mockup put them; each prefab
sits centred on its scaled rectangle, bottom-aligned, nudged clear of its neighbours.

Each town has its own tileset (make_town_tilesets.py), chosen for its character:
    Storm's Edge   orleans_port      fishing port (storms_edge.py, storms_tileset.py): stilt houses, quay and pier, substation, lighthouse
    Crescent City  orleans_crescent  the old city: Brick City houses, shops, gables, halls, row buildings, church
    Pointe Rouge   orleans_pointe    the capital (pointe.py, pointe_tileset.py): own-art Capitol, refinery, boathouse gym, bridges
    Redfield       orleans_capital   sugar town: the mill barn, a brick bottling works and office, shotgun cabins
    Camp Cocodrie, Lutin's Hollow, Land's End  orleans_harbor: Shady houses and cabins, the Moomoo barn
"""

TOWN_CFG = {"storms_edge": "orleans_port", "crescent_city": "orleans_crescent", "pointe_rouge": "orleans_pointe",
            "redfield": "orleans_capital", "camp_cocodrie": "orleans_camp", "lutins_hollow": "orleans_hollow",
            "lands_end": "orleans_harbor",
            # routes with river levees (levee.py) get the route set under their own name (make_route_tilesets.py)
            "route_4": "orleans_river"}
# the later routes share a second copy of the route set (one set for all of them overflowed 512 tiles); the Gulf routes and the
# dry country then split off it (below)
TOWN_CFG.update({f"route_{n}": "orleans_route_b" for n in range(14, 26)})
# the Gulf routes (landmark art: offshore platform, temple gate, bird platform, shrine steps, wrecks, pilings) have their own set
TOWN_CFG.update({f"route_{n}": "orleans_gulf" for n in (18, 19, 20)})
TOWN_CFG.update({f"route_{n}": "orleans_offshore" for n in (21, 22, 25)})
TOWN_CFG["oldest_shrine"] = "orleans_route_b"
# Route 2 (power line, wire spans, lookout, beach) has its own set: with the landmark art orleans_route overflowed 512 tiles
TOWN_CFG["route_2"] = "orleans_coast"
# the dry country (Redfield's neighbours: dry farmland and hills) shares the dry-country art set (sources/orleans_custom/
# dry_country.*, art_requests/dry_country.md) on a third copy of the route set, orleans_route_dry (dry_route_tileset.py):
# the 107 tiles of the set would not fit in orleans_route_b
DRY_ROUTES = ["route_15", "route_16", "route_17", "route_23", "route_24"]
TOWN_CFG.update({k: "orleans_route_dry" for k in DRY_ROUTES})
# ... and the dry-country art (cane wall, red earth, rock wall, gully, salt) overflowed one set: the farm routes split off
TOWN_CFG.update({"route_15": "orleans_route_farm", "route_16": "orleans_route_farm", "route_17": "orleans_route_farm"})
# dry routes whose edge meets a green map: side -> cells over which the dry ground fades into green meadow
# (Route 15's west edge is Route 14's; Route 23's west edge is Pointe Rouge's)
DRY_FADE = {"route_15": {"W": 11, "N": 7}, "route_23": {"W": 11}}

# dry routes whose edge continues what the neighbour has at the border (firstpass.seam_adopt; the phase-2 world seams, Agent L):
# side = this map's edge, from = the neighbour, dy = neighbour's row (column) minus this map's, depth = how far a field's
# character (cane G, pepper q, wall w, red earth e) reaches in, clear = the plain-ground strip where the neighbour has plain ground
EDGE_PAINT = {   # (x, y, w, h, char) painted over a green route's grid after its greenery (firstpass.edge_clear), before the ground is built
    "route_2": [(0, 8, 4, 1, "."), (0, 19, 3, 7, "."), (44, 20, 6, 4, ".")],
    "route_3": [(0, 13, 3, 8, "."), (0, 0, 3, 6, ".")],
    "route_4": [(21, 0, 7, 4, ".")],
    "route_23": [(46, 12, 4, 1, ".")],   # the east road is 2 wide, rows 10-11 (Route 24's rows 13-14 at offset -3): its dip at row 12 goes
}
EDGE_CLEAR = {   # green routes: marsh/tall grass off the last cells of an edge (firstpass.edge_clear): side, span, depth (min, max)
    "route_14": [{"side": "S", "span": (4, 28), "depth": (3, 6)}],
    "route_4": [{"side": "N", "span": (0, 28), "depth": (3, 5)}],
    # Route 3 meets two towns' plain lawns: marsh and tall grass keep off both edges
    "route_3": [{"side": "W", "span": (0, 24), "depth": (3, 6)}, {"side": "E", "span": (0, 24), "depth": (3, 5)}],
}
ROCK_KEEPOFF = {"route_23": {"E": 8}}   # no rock wall within this many cells of an edge (firstpass.dry_cliffs): Route 24's west edge is salt and sand
SEAM_ADOPT = {
    "route_15": [{"side": "E", "from": "route_16", "dy": 4, "depth": (6, 9)}],
    "route_16": [{"side": "E", "from": "route_17", "dy": -5, "depth": (6, 9)}],
    "route_17": [{"side": "E", "from": "redfield", "dy": 5, "depth": (6, 9)}],
    "route_23": [{"side": "E", "from": "route_24", "dy": 3, "depth": (3, 5)}],
}

# routes made larger than their mockup, and exits the mockup doesn't draw: Route 23 grows south so Pointe Rouge's
# second (southern) river bridge has somewhere to go (its west edge meets Pointe's east edge 7 rows lower:
# Pointe's bridge deck rows 29-30 are Route 23's rows 36-37)
GROW = {"route_23": {"S": 12}}
EXTRA_EXITS = {"route_23": [{"side": "W", "pos": 36}], "route_15": [{"side": "N", "pos": 9}]}

SCALE = {"storms_edge": 1.25, "crescent_city": 1.5, "pointe_rouge": 1.5, "camp_cocodrie": 1.25,
         "lutins_hollow": 1.25, "redfield": 1.25, "lands_end": 1.25}

# town -> [(room key or None, label when no room, prefab, (x, y, w, h) in mockup tiles)]
# A building with no room (label set) is "closed": its door stays shut.
PLANS = {
    "storms_edge": [  # placed by hand in storms_edge.py (map positions there); rects are the mockup's
        ("storms_edge_pokecenter", None, "pokecenter", (3, 3, 6, 4)),
        ("storms_edge_mart", None, "mart", (10, 3, 5, 4)),
        ("storms_edge_gym", None, "substation", (29, 3, 6, 5)),
        ("storms_edge_house_w", None, "stilt_house", (3, 15, 3, 3)),
        ("storms_edge_house_c", None, "stilt_house", (8, 15, 3, 3)),
        ("storms_edge_seafood_market", None, "brick_shop", (12, 15, 5, 3)),
        ("storms_edge_house_e", None, "stilt_house", (26, 15, 3, 3)),
        ("storms_edge_lighthouse", None, "lighthouse", (34, 24, 3, 5)),
    ],
    "crescent_city": [  # placed by hand in crescent.py (map positions there); rects are the mockup's
        ("crescent_city_cathedral", None, "church", (14, 3, 4, 4)),
        ("crescent_city_cafe", None, "house_cafe", (18, 3, 3, 4)),
        ("crescent_city_apartment", None, "house_apartment", (22, 3, 4, 4)),
        ("crescent_city_salon", None, "house_salon", (13, 9, 3, 3)),
        ("crescent_city_laundry", None, "house_laundry", (17, 9, 4, 3)),
        ("crescent_city_pokecenter_quarter", None, "pokecenter", (21, 9, 4, 3)),
        ("crescent_city_trades", None, "house_trades", (13, 13, 5, 3)),
        ("crescent_city_gym", None, "gym", (4, 13, 5, 3)),
        ("crescent_city_blacksnake_base", None, "ruin_door", (32, 10, 3, 3)),
        ("crescent_city_dept_1f", None, "brick_hall", (13, 21, 6, 5)),
        ("crescent_city_game_corner", None, "house_gamecorner", (20, 21, 5, 2)),
        ("crescent_city_name_rater", None, "house_namerater", (20, 24, 2, 2)),
        ("crescent_city_tutor", None, "house_tutor", (23, 24, 2, 2)),
        ("crescent_city_day_care", None, "house_daycare", (7, 25, 3, 2)),
        ("crescent_city_conservation", None, "brick_hall", (27, 22, 7, 5)),
        ("crescent_city_pokecenter_waterfront", None, "pokecenter", (35, 22, 4, 3)),
        ("crescent_city_ice_cream", None, "house_icecream", (35, 25, 3, 2)),
        ("crescent_city_riverboat_terminal", None, "warehouse9", (27, 29, 6, 3)),
        ("crescent_city_pelipper_post", None, "warehouse6", (34, 29, 5, 3)),
        (None, "Battle Tower (post-game)", "fac_tower", (2, 31, 3, 3)),
        (None, "Battle Dome (post-game)", "fac_dome", (5, 31, 3, 3)),
        (None, "Battle Palace (post-game)", "fac_palace", (9, 31, 3, 3)),
        (None, "Battle Arena (post-game)", "fac_arena", (12, 31, 3, 3)),
        (None, "Battle Factory (post-game)", "fac_factory", (16, 31, 3, 3)),
        (None, "Battle Pike (post-game)", "fac_pike", (19, 31, 3, 3)),
        (None, "Battle Pyramid (post-game)", "fac_pyramid", (23, 31, 3, 3)),
    ],
    "pointe_rouge": [  # handmade by pointe.py at 1.5x on its own tileset (orleans_pointe); rects are the mockup's
        ("pointe_rouge_capitol_lobby", None, "capitol", (18, 2, 5, 7)),
        ("pointe_rouge_pokecenter", None, "pokecenter", (24, 2, 5, 3)),
        ("pointe_rouge_house_nw", None, "brick_round", (2, 3, 4, 3)),
        ("pointe_rouge_house_ne", None, "brick_round", (8, 3, 4, 3)),
        ("pointe_rouge_mart", None, "mart", (24, 6, 5, 3)),
        ("pointe_rouge_refinery", None, "refinery", (2, 13, 9, 10)),
        ("pointe_rouge_tackle_shop", None, "tackle_shop", (18, 14, 5, 3)),
        ("pointe_rouge_ice_plant", None, "ice_plant", (24, 14, 5, 4)),
        ("pointe_rouge_house_s", None, "brick_house", (19, 21, 4, 3)),
        ("pointe_rouge_gym", None, "boathouse", (27, 23, 5, 5)),
    ],
    "camp_cocodrie": [
        ("camp_cocodrie_gym", None, "barn", (13, 3, 8, 6)),
        ("camp_cocodrie_cabin_1", None, "cabin", (2, 8, 3, 3)),
        ("camp_cocodrie_cabin_2", None, "cabin", (6, 8, 4, 3)),
        ("camp_cocodrie_cabin_3", None, "cabin", (25, 8, 3, 3)),
        ("camp_cocodrie_cabin_4", None, "cabin", (33, 8, 3, 3)),
        ("camp_cocodrie_nurse_cabin", None, "cabin", (4, 14, 5, 3)),
        ("camp_cocodrie_bait_shack", None, "cabin", (13, 14, 4, 3)),
        ("camp_cocodrie_smokehouse", None, "cabin", (24, 14, 4, 3)),
        ("camp_cocodrie_dance_porch", None, "cabin", (30, 14, 4, 4)),
    ],
    "lutins_hollow": [
        ("lutins_hollow_gym", None, "barn", (17, 1, 6, 4)),
        ("lutins_hollow_moss_house_n", None, "cabin", (27, 6, 3, 2)),
        ("lutins_hollow_pokecenter", None, "pokecenter", (7, 9, 4, 4)),
        ("lutins_hollow_herbalist", None, "cabin", (29, 18, 4, 4)),
        ("lutins_hollow_moss_house_s", None, "cabin", (10, 20, 3, 3)),
    ],
    "redfield": [
        ("redfield_shotgun_house_1", None, "cabin", (11, 3, 2, 4)),
        ("redfield_shotgun_house_2", None, "cabin", (14, 3, 2, 4)),
        ("redfield_gym", None, "barn", (28, 5, 6, 6)),
        ("redfield_house_1", None, "cabin", (11, 8, 2, 4)),
        ("redfield_house_2", None, "cabin", (14, 8, 2, 4)),
        ("redfield_ritas_office", None, "brick_shop", (21, 9, 3, 2)),
        ("redfield_pokecenter", None, "pokecenter", (20, 19, 5, 3)),
        ("redfield_mart", None, "mart", (26, 19, 4, 3)),
        ("redfield_bottling_works", None, "brick_row", (20, 24, 6, 3)),
    ],
    "lands_end": [
        ("lands_end_house_1", None, "cabin", (3, 9, 3, 3)),
        ("lands_end_lookout", None, "cabin", (33, 9, 3, 3)),
        ("lands_end_house_2", None, "cabin", (13, 10, 3, 2)),
        ("lands_end_house_3", None, "cabin", (25, 10, 4, 2)),
        ("lands_end_house_4", None, "cabin", (6, 15, 3, 2)),
        ("lands_end_pokecenter", None, "pokecenter", (13, 15, 5, 3)),
        ("lands_end_house_5", None, "cabin", (33, 15, 3, 2)),
        ("lands_end_marine_supply", None, "cabin", (13, 19, 5, 3)),
        ("lands_end_weather_station", None, "cabin", (28, 21, 4, 3)),
        ("lands_end_gym", None, "barn", (18, 25, 9, 4)),
    ],
}

# Route landmarks (no interiors: their doors stay shut): route -> [(label, prefab, (x, y, w, h) mockup tiles)]
ROUTE_PLANS = {
    "route_4": [("Yard warehouse", "barn", (9, 10, 7, 5)), ("Warehouse", "barn", (9, 28, 5, 3)),
                ("Riverboat landing office", "cabin", (21, 39, 4, 2))],
    "route_5": [("Angler's shack", "cabin", (36, 5, 4, 3))],
    "route_9": [("Landing shack", "cabin", (30, 12, 3, 2))],
    "route_10": [("Boathouse", "cabin", (1, 18, 4, 3)), ("Boathouse", "cabin", (6, 19, 4, 3))],
    "route_16": [("Drying shed", "drying_shed", (8, 4, 4, 3)), ("Drying shed", "drying_shed", (40, 6, 4, 3)),
                 ("Drying shed", "drying_shed", (26, 18, 4, 3))],
    "route_17": [("Sugar mill", "route_mill", (4, 4, 7, 6)), ("Sugar mill", "route_mill", (16, 4, 7, 6)),
                 ("Sugar mill", "route_mill", (30, 4, 7, 6))],
    "route_19": [("Oyster shed", "cabin", (16, 6, 3, 3)), ("Oyster shed", "cabin", (36, 6, 3, 2))],
    # (Route 24's dry cave and salt-dome cavern are mouths in its rock wall: route_features "rock_wall", firstpass.dry_cliffs)
    "oldest_shrine": [("Singing stone", "shrine", (17, 11, 2, 2))],
}

# terrain painted over the extracted mockup before scaling: (x, y, w, h, char) in mockup tiles
TERRAIN_FIX = {
    # the Old Cemetery's tomb grid reads as a lattice of streets: open ground until the Brick City pass
    "crescent_city": [(1, 4, 10, 12, "."),
                      (0, 0, 40, 2, "~")],  # the basin canal along the top: the Route 6 boat exit
    # the Route 20 label hides the west end of the main boardwalk
    "lands_end": [(2, 12, 13, 2, "#")],
}


# towns built over water: every boardwalk is a plank dock, even where it brushes land
DOCK_ALL = {"lands_end"}


def door_label(key, title):
    """The label a planned building carries in the town spec; the room's door_label is the same string."""
    return f"{title} ({key})"


def room_keys():
    return {k for plan in PLANS.values() for k, *_ in plan if k}
