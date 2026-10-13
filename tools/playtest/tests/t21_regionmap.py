"""Region map and Fly (tools/regionmap, region_map/01_wiring_plan.md): the Fly map shows Orleans; Fly from Crescent City to every visited town lands on a
walkable cell outside the Center; unvisited towns, routes and the hidden Frontier can't be chosen; arriving sets the visited flag; the old-save catch-up
(a real Continue on tools/playtest/fixtures/old_build.sav when present, plus a story-31 save simulated by clearing the flags); the player icon on a route follows
the route's own cells; the Pokedex area screen glows on Orleans routes and towns; Fly (Pokenav / Town Map, R) needs the badge and an outdoor map."""
import json
from pathlib import Path

from bot import ROOT, Bot, enum_value, map_data

SECTIONS = json.loads((ROOT / "src/data/region_map/region_map_sections.json").read_text(encoding="utf-8"))["map_sections"]
SECID = {s["id"]: i for i, s in enumerate(SECTIONS)}
NONE_ID = len(SECTIONS)
OUTLINE = json.loads((ROOT / "tools/regionmap/out/sections.json").read_text(encoding="utf-8"))["sections"]
CELLS = {s["id"]: [tuple(c) for c in s["cells"]] for s in OUTLINE}

MAPCURSOR_X_MIN, MAPCURSOR_Y_MIN = 1, 2
# MAPSECTYPE_NONE, ROUTE, CITY_CANFLY, CITY_CANTFLY, BATTLE_FRONTIER
T_NONE, T_ROUTE, T_CANFLY, T_CANTFLY, T_FRONTIER = 0, 1, 2, 3, 4

# town: (map dir, mapsec, flag, landing (x, y), the cell to put the cursor on)
TOWNS = [
    ("IsleMarais", "MAPSEC_ISLE_MARAIS", "FLAG_VISITED_ISLE_MARAIS", (22, 5)),
    ("OldWater", "MAPSEC_OLD_WATER", "FLAG_VISITED_OLD_WATER", (16, 8)),
    ("GrandOak", "MAPSEC_GRAND_OAK", "FLAG_VISITED_GRAND_OAK", (6, 12)),
    ("StormsEdge", "MAPSEC_STORMS_EDGE", "FLAG_VISITED_STORMS_EDGE", (15, 13)),
    ("CrescentCity", "MAPSEC_CRESCENT_CITY", "FLAG_VISITED_CRESCENT_CITY", (48, 20)),
    ("PointeRouge", "MAPSEC_POINTE_ROUGE", "FLAG_VISITED_POINTE_ROUGE", (40, 7)),
    ("CampCocodrie", "MAPSEC_CAMP_COCODRIE", "FLAG_VISITED_CAMP_COCODRIE", (7, 22)),
    ("LutinsHollow", "MAPSEC_LUTINS_HOLLOW", "FLAG_VISITED_LUTINS_HOLLOW", (8, 16)),
    ("Redfield", "MAPSEC_REDFIELD", "FLAG_VISITED_REDFIELD", (27, 28)),
    ("LandsEnd", "MAPSEC_LANDS_END", "FLAG_VISITED_LANDS_END", (17, 23)),
]


def continue_game(b):
    """boot to the title, CONTINUE, until the player has control (as t13b_oldsave)"""
    b.frames(1500)
    for _ in range(4):
        b.press("START", 6, 50)
    b.press("A", 6, 90)
    b.press("A", 6, 90)
    for _ in range(40):
        if b.in_overworld() and b.player_idle():
            break
        b.press("A", 4, 30)
    b.settle()


def region(b):
    return b.r32(b.sym("sRegionMap"))


def rm_state(b):
    base = region(b)
    return b.r16(base), b.r8(base + 2), b.r16(base + 0x54), b.r16(base + 0x56)   # mapSecId, mapSecType, cursorPosX, cursorPosY


def cell(b):
    s, ty, x, y = rm_state(b)
    return x - MAPCURSOR_X_MIN, y - MAPCURSOR_Y_MIN


def open_fly(b):
    b.w32(b.sym("gMain") + 4, b.sym("CB2_OpenFlyMap") | 1)
    for _ in range(80):
        b.frames(10)
        if b.callback2() & ~1 == b.sym("CB2_FlyMap") and region(b):
            b.frames(30)
            return True
    return False


def close_fly(b):
    """B out of the Fly map (it returns to the party menu), B out of that, until the field is back"""
    for _ in range(12):
        if b.in_overworld() and b.player_idle():
            return True
        b.press("B", 4, 40)
        b.frames(60)
    return b.in_overworld()


def move_cursor(b, cx, cy):
    for _ in range(120):
        x, y = cell(b)
        if (x, y) == (cx, cy):
            b.frames(20)
            return True
        key = "RIGHT" if x < cx else "LEFT" if x > cx else "DOWN" if y < cy else "UP"
        b.press(key, 4, 8)
        b.frames(6)
    return False


def fly_to(b, mapsec_cells, label):
    """open the Fly map, put the cursor on the town's first cell, press A; returns (section, type) read on the cell"""
    ok = open_fly(b)
    ok = ok and move_cursor(b, *mapsec_cells)
    return ok


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_TOTODILE", 50)
    ids = {n: SECID[n] for n in SECID}

    # ---- the table the rest of the test relies on
    t.check("sections: Orleans towns and routes have rectangles, the new arenas exist",
            all(SECTIONS[SECID[s]].get("width") for s in CELLS) and "MAPSEC_SALT_DOME" in SECID and "MAPSEC_DROWNED_TEMPLE" in SECID,
            [s for s in CELLS if not SECTIONS[SECID[s]].get("width")])
    t.check("Hoenn sections have no rectangle (retired)", not SECTIONS[SECID["MAPSEC_LITTLEROOT_TOWN"]].get("width"))

    # ---- arrival sets the flag (map load: warp, as with a connection the OnTransition runs the same way)
    for name, sec, flag, land in TOWNS:
        b.set_flag(flag, False)
    b.set_var("VAR_ORLEANS_STORY", 36)
    b.set_flag("FLAG_BADGE06_GET")
    for name, sec, flag, land in TOWNS:
        b.warp(name, *land)
        t.check(f"arriving in {name} sets {flag}", b.flag(flag), b.where())
    b.set_var("VAR_ORLEANS_STORY", 44)
    b.set_flag("FLAG_LANDMARK_BATTLE_FRONTIER", False)
    b.warp("CrescentCity", 48, 20)
    t.check("the Frontier landmark is not set before the post-game", not b.flag("FLAG_LANDMARK_BATTLE_FRONTIER"))
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.warp("CrescentCity", 48, 20)
    t.check("arriving in Crescent City at story 45 sets the Frontier landmark", b.flag("FLAG_LANDMARK_BATTLE_FRONTIER"))
    b.set_flag("FLAG_LANDMARK_BATTLE_FRONTIER", False)

    # ---- the Fly map: Orleans picture, cursor types
    b.set_var("VAR_ORLEANS_STORY", 36)
    b.warp("CrescentCity", 48, 20)
    t.check("the Fly map opens", open_fly(b), b.callback2_name())
    b.shot("fly_map_all_visited")
    mapsec, ty, cx, cy = rm_state(b)
    t.check("the cursor starts on Crescent City (the player's town)", mapsec == SECID["MAPSEC_CRESCENT_CITY"] and ty == T_CANFLY, (mapsec, ty, cx - 1, cy - 2))

    # unvisited town, route and the hidden Frontier
    b.set_flag("FLAG_VISITED_LANDS_END", False)
    move_cursor(b, *CELLS["MAPSEC_LANDS_END"][0])
    mapsec, ty, _, _ = rm_state(b)
    t.check("an unvisited town (Land's End) is shown but can't be chosen", mapsec == SECID["MAPSEC_LANDS_END"] and ty == T_CANTFLY, (mapsec, ty))
    b.press("A", 6, 20)
    b.frames(60)
    t.check("A on it leaves the Fly map open", b.callback2() & ~1 == b.sym("CB2_FlyMap"), b.callback2_name())
    move_cursor(b, *CELLS["MAPSEC_ROUTE_17"][0])
    mapsec, ty, _, _ = rm_state(b)
    t.check("a route (Route 17) shows its name and is no Fly target", mapsec == SECID["MAPSEC_ROUTE_17"] and ty == T_ROUTE, (mapsec, ty))
    b.press("A", 6, 20)
    b.frames(60)
    t.check("A on a route leaves the Fly map open", b.callback2() & ~1 == b.sym("CB2_FlyMap"), b.callback2_name())
    move_cursor(b, 15, 10)
    mapsec, ty, _, _ = rm_state(b)
    t.check("the hidden Frontier cell has no name before the post-game", mapsec == SECID["MAPSEC_BATTLE_FRONTIER"] and ty == T_NONE, (mapsec, ty))
    b.press("A", 6, 20)
    b.frames(60)
    t.check("A on the hidden Frontier does nothing", b.callback2() & ~1 == b.sym("CB2_FlyMap"), b.callback2_name())
    b.shot("fly_map_cursor_frontier_hidden")
    b.set_flag("FLAG_LANDMARK_BATTLE_FRONTIER")
    b.press("LEFT", 4, 8)
    b.press("RIGHT", 4, 8)
    b.frames(20)
    mapsec, ty, _, _ = rm_state(b)
    t.check("after the post-game opens it, the Frontier is a Fly target", ty == T_FRONTIER, (mapsec, ty))
    b.set_flag("FLAG_LANDMARK_BATTLE_FRONTIER", False)
    b.set_flag("FLAG_VISITED_LANDS_END")
    close_fly(b)

    # ---- Fly from Crescent City to every visited town
    for name, sec, flag, land in TOWNS:
        if name == "CrescentCity":
            continue
        b.warp("CrescentCity", 48, 20)
        if not open_fly(b):
            t.check(f"Fly map opens for {name}", False, b.callback2_name())
            continue
        move_cursor(b, *CELLS[sec][0])
        mapsec, ty, _, _ = rm_state(b)
        t.check(f"{name}: the cell is a flyable section", mapsec == SECID[sec] and ty == T_CANFLY, (mapsec, ty))
        if name == "Redfield":
            b.shot("fly_map_cursor_redfield")
        b.press("A", 6, 20)
        arrived = False
        for _ in range(60):
            b.frames(30)
            if b.in_overworld() and b.map_name() == name:
                arrived = True
                break
        b.settle()
        t.check(f"{name}: Fly arrives in the town", arrived, b.where())
        d = map_data(name)
        x, y = b.pos()
        t.check(f"{name}: lands at {land}", (x, y) == land, b.where())
        t.check(f"{name}: the landing cell is walkable", d["coll"][y][x] == 0)
        t.check(f"{name}: not on a warp (outside the Center)", not any(w["x"] == x and w["y"] == y for w in d["warps"]))
        # one step toward the door of the Center: the door is the warp next to the landing cell
        door = [w for w in d["warps"] if abs(w["x"] - x) + abs(w["y"] - y) == 1]
        t.check(f"{name}: the landing cell is in front of a door", bool(door), (x, y))
    b.warp("StormsEdge", 15, 13)
    b.step("U")
    b.settle()
    t.check("Storm's Edge: stepping up from the landing enters the Center", "Pokecenter" in b.map_name() or "Pokemon" in b.map_name(), b.where())

    # ---- player icon on routes follows the route's cells
    route_maps = {"Route2": "MAPSEC_ROUTE_2", "Route3": "MAPSEC_ROUTE_3", "Route5": "MAPSEC_ROUTE_5", "Route11": "MAPSEC_ROUTE_11", "Route6": "MAPSEC_ROUTE_6"}
    for rname, sec in route_maps.items():
        d = map_data(rname)
        for frac, label in ((0.05, "west end"), (0.95, "east end")):
            x = max(1, min(d["width"] - 2, int(d["width"] * frac)))
            ys = [yy for yy in range(d["height"]) if d["coll"][yy][x] == 0]
            if not ys:
                continue
            y = ys[len(ys) // 2]
            if not b.warp(rname, x, y):
                t.check(f"{rname}: warp {label}", False, b.where())
                continue
            if not open_fly(b):
                t.check(f"{rname}: Fly map opens", False, b.callback2_name())
                continue
            c = cell(b)
            mapsec, ty, _, _ = rm_state(b)
            t.check(f"{rname} {label} (x={x}): the map picture is Orleans and the icon is on a {sec} cell", mapsec == SECID[sec] and c in CELLS[sec], (mapsec, c, CELLS[sec]))
            if rname == "Route2" and frac < 0.5:
                b.shot("fly_map_player_on_route2")
            close_fly(b)

    # ---- Town Map key item: same picture, R flies
    b.warp("Redfield", 27, 28)
    b.set_flag("FLAG_BADGE06_GET")
    b.call("FieldInitRegionMap", b.sym("CB2_ReturnToField") | 1)
    b.frames(240)
    b.shot("town_map")
    close_fly(b)
    b.frames(30)
    b.warp("Redfield", 27, 28)   # leave the screen again

    # ---- Fly without the HM: needs the badge and an outdoor map
    CAN = "Orleans_CanFlyFromMapType"
    b.set_flag("FLAG_BADGE06_GET")
    b.warp("Redfield", 27, 28)
    t.check("Fly (Pokenav / Town Map R) is allowed outdoors with the badge", (b.call(CAN, T_CANFLY) & 0xFF) == 1)
    t.check("... on a Battle Frontier cell too", (b.call(CAN, T_FRONTIER) & 0xFF) == 1)
    t.check("... not on a route cell or a locked town", (b.call(CAN, T_ROUTE) & 0xFF) == 0 and (b.call(CAN, T_CANTFLY) & 0xFF) == 0)
    b.set_flag("FLAG_BADGE06_GET", False)
    t.check("Fly is unavailable without the badge", (b.call(CAN, T_CANFLY) & 0xFF) == 0)
    b.set_flag("FLAG_BADGE06_GET")
    indoor = next((n for n in ("Redfield_Pokecenter", "Redfield_PokemonCenter") if n in b.maps.by_name), None)
    if indoor:
        d = map_data(indoor)
        ys = [(xx, yy) for yy in range(d["height"]) for xx in range(d["width"]) if d["coll"][yy][xx] == 0]
        b.warp(indoor, *ys[len(ys) // 2])
        t.check("Fly is unavailable indoors", (b.call(CAN, T_CANFLY) & 0xFF) == 0, b.where())
    b.warp("OldestShrine", *next(((xx, yy) for yy in range(map_data("OldestShrine")["height"]) for xx in range(map_data("OldestShrine")["width"])
                                  if map_data("OldestShrine")["coll"][yy][xx] == 0), (10, 10)))
    t.check("Fly is unavailable at the Oldest Shrine (finale arena)", (b.call(CAN, T_CANFLY) & 0xFF) == 0, b.where())
    b.warp("Redfield", 27, 28)

    # ---- Pokedex area screen: Orleans encounters glow
    species = enum_value("species.h", "SPECIES_SPEAROW_ORLEANIAN")
    scratch = b.sym("gSpecialVar_0x8000")
    route1 = SECID["MAPSEC_ROUTE_1"]
    for where, args in (("a town (Redfield)", ("Redfield", 27, 28)), ("a route (Route 5)", ("Route5", 20, 8))):
        if not b.warp(*args):
            continue
        b.w8(scratch, 0)
        b.call("DisplayPokedexAreaScreen", species, scratch, 0, 0)
        b.frames(120)
        ptr = b.r32(b.sym("sPokedexAreaScreen"))
        n = b.r16(ptr + 0x110) if ptr else 0
        secs = [b.r16(ptr + 0x10 + 4 * i + 2) for i in range(min(n, 64))] if ptr else []
        t.check(f"Pokedex area from {where}: Orleans encounters are listed and Route 1 glows", n > 0 and route1 in secs, (n, secs))
        if where.startswith("a town"):
            b.shot("pokedex_area_from_town")
        b.warp("Redfield", 27, 28)

    # ---- old-save catch-up
    for name, sec, flag, land in TOWNS:
        b.set_flag(flag, False)
    b.set_flag("FLAG_LANDMARK_BATTLE_FRONTIER", False)
    b.set_var("VAR_ORLEANS_STORY", 31)
    b.set_flag("FLAG_BADGE04_GET")
    b.call("Orleans_CatchUpVisitedFlags")
    want = {"ISLE_MARAIS", "OLD_WATER", "GRAND_OAK", "STORMS_EDGE", "CRESCENT_CITY", "POINTE_ROUGE", "CAMP_COCODRIE", "LUTINS_HOLLOW", "REDFIELD"}
    got = {n for n, sec, f, l in TOWNS if b.flag(f)}
    t.check("catch-up at story 31: nine towns set, Land's End and the Frontier not",
            {f.replace("FLAG_VISITED_", "") for f in [x[2] for x in TOWNS if b.flag(x[2])]} == want and not b.flag("FLAG_LANDMARK_BATTLE_FRONTIER"), got)
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.call("Orleans_CatchUpVisitedFlags")
    t.check("catch-up at story 45: Land's End and the Frontier too", b.flag("FLAG_VISITED_LANDS_END") and b.flag("FLAG_LANDMARK_BATTLE_FRONTIER"))

    # a real Continue on the previous build's save (story 20, Redfield): the flags appear through CB2_ContinueSavedGame
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "old_build.sav"
    if fixture.exists():
        old = Bot(rom=b.rom, out_dir=b.out / "oldsave", save=fixture)
        try:
            continue_game(old)
            have = {n for n, sec, f, l in TOWNS if old.flag(f)}
            t.check("Continue on the old save (story 20): towns up to Pointe Rouge are visited, Camp Cocodrie and later are not",
                    have == {"IsleMarais", "OldWater", "GrandOak", "StormsEdge", "CrescentCity", "PointeRouge"}, sorted(have))
        finally:
            old.close()
    else:
        t.note("fixture old_build.sav missing: the real Continue was not tested")
