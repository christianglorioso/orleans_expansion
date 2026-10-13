"""The three legendary arenas as built from the approved art (tools/mapgen/tilesets/arenas): the Drowned Temple (the dive arrival, the sealed door as a
map state, Kyogre's standing cell, the exit), the Salt Cathedral (the shaft arrival, Groudon's standing cell, the exit) and the Oldest Shrine (the landing,
the shell road, the mound steps, every stand cell). Takes the in-engine screenshots the layout review wants (out/<run>/t19_arenas/)."""
from bot import map_data


def mash_until(b, cond, n=200):
    for _ in range(n):
        if cond():
            return True
        if b.in_battle():
            b.fight()
            continue
        b.press("A", 4, 26)
    return cond()


def walkable(name, x, y):
    d = map_data(name)
    return d["coll"][y][x] == 0


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_ORLEANS_STORY", 39)
    for f in ("FLAG_RECEIVED_DIVING_GEAR", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET", "FLAG_RECEIVED_HM_SURF"):
        b.set_flag(f, True)
    b.give_item("ITEM_LANTERN", 1)

    # ---------------------------------------------------------------- the Drowned Temple
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN", False)
    b.warp("Route22", 5, 24)
    b.face("U")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.map_name() == "LandsEnd_DrownedTemple", 60)
    b.frames(60)
    t.check("the dive arrives on the dive pool's top step (9, 18)", b.map_name() == "LandsEnd_DrownedTemple" and b.pos() == (9, 18), b.where())
    b.frames(120)
    b.shot("temple_arrival_door_closed")
    t.check("the hall: the door cells (8-10, 9-10) block while it is sealed", not any(walkable("LandsEnd_DrownedTemple", x, y) for x in (8, 9, 10) for y in (9, 10)))
    t.check("the singing cell (9, 11) and Kyogre's stand cell (9, 6) are floor", walkable("LandsEnd_DrownedTemple", 9, 11) and walkable("LandsEnd_DrownedTemple", 9, 6))
    t.check("walk from the dive pool to the singing cell (9, 11)", b.goto(9, 11), b.where())
    b.face("U")
    b.shot("temple_before_singing")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.flag("FLAG_TEMPLE_DOOR_OPEN"), 120)
    b.advance_text(60)
    b.frames(40)
    t.check("singing opens the door (FLAG_TEMPLE_DOOR_OPEN)", b.flag("FLAG_TEMPLE_DOOR_OPEN"))
    b.shot("temple_door_open")
    b.walk("UUUUU")
    t.check("through the opened door and over the causeway to Kyogre's stand cell (9, 6)", b.pos() == (9, 6), b.where())
    b.face("U")
    b.frames(30)
    b.shot("temple_kyogre")
    b.walk("DDDDD")
    # leaving and coming back keeps the door open (the map's ON_LOAD re-applies the state)
    b.warp("Route22", 5, 24)
    b.warp("LandsEnd_DrownedTemple", 9, 11)
    b.frames(30)
    b.walk("UUUUU")
    t.check("the door is still open after leaving and re-entering (state applied on load)", b.pos() == (9, 6), b.where())
    b.walk("DDDDD")
    b.goto(9, 18)
    b.press("DOWN", 8, 8)
    b.frames(160)
    t.check("the dive pool's exit leaves by script to Route 22 (5, 24)", b.map_name() == "Route22" and b.pos() == (5, 24), b.where())

    # ---------------------------------------------------------------- the Salt Cathedral
    b.warp("Route24", 39, 7)
    b.face("U")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.map_name() == "LandsEnd_SaltCathedral", 60)
    b.frames(60)
    t.check("the shaft arrives at the adit's mouth (11, 20)", b.map_name() == "LandsEnd_SaltCathedral" and b.pos() == (11, 20), b.where())
    b.shot("cathedral_arrival")
    t.check("Groudon's stand cell (11, 5) is floor and reachable", walkable("LandsEnd_SaltCathedral", 11, 5) and b.goto(11, 5), b.where())
    b.face("U")
    b.frames(30)
    b.shot("cathedral_groudon")
    b.goto(11, 20)
    b.press("DOWN", 8, 8)
    b.frames(160)
    t.check("the adit's exit leaves by script to Route 24 (39, 7)", b.map_name() == "Route24" and b.pos() == (39, 7), b.where())

    # ---------------------------------------------------------------- the Oldest Shrine
    b.set_var("VAR_ORLEANS_STORY", 42)
    b.set_var("VAR_SHRINE_ARRIVAL", 1)
    b.warp("OldestShrine", 17, 24)
    b.frames(90)
    b.shot("shrine_landing")
    for name, (x, y) in (("the keeper's cell", (15, 14)), ("NPC_1's cell", (18, 14)), ("Andrew's cell (head of the steps)", (17, 20)),
                         ("Camille's cell (on the steps)", (16, 23)), ("Jayden's cell (top step)", (17, 10)), ("the player's raid cell (top step)", (16, 10)),
                         ("the Dragoninite cell (landing)", (17, 24))):
        t.check("%s is walkable" % name, walkable("OldestShrine", x, y))
    t.check("Rayquaza's cell (16, 9) on the mound top is walkable (an object stands there)", walkable("OldestShrine", 16, 9))
    t.check("walk from the landing up the shell road to the top step (16, 10)", b.goto(16, 10), b.where())
    b.face("U")
    b.frames(30)
    b.shot("shrine_mound_rayquaza")
    t.check("both raid objects are shown at story 42 and Rayquaza faces the player's cell",
            not b.flag("FLAG_HIDE_SHRINE_RAYQUAZA") and not b.flag("FLAG_HIDE_SHRINE_JAYDEN"))
    b.goto(17, 14)
    b.shot("shrine_road")
    t.check("the ridges block: the west bank (7, 13) is not floor", not walkable("OldestShrine", 7, 13) and not walkable("OldestShrine", 26, 13))
