"""Chapter 4: the riverboat arrival, the Pointe Rouge refinery gate and valves, Jayden and Camille, the Route 5 tournament, the gym's
tailwind puzzle and Kingfisher, the Old Water midpoint visit (verse 4, HM Surf, Rockruff), the Route 6 debris, the Surf unlock
and the Route 23 dust-storm gate. Story values: 17 (carving found) -> 18 -> 19 -> 20 -> 21 -> 22."""
from bot import map_data


def obj_by_script(mapname, suffix):
    for o in map_data(mapname)["objects"]:
        if o.get("script", "").endswith(suffix):
            return o
    return None


def go(b, x, y, tries=4):
    """goto, finishing any trainer spotting on the way"""
    for _ in range(tries):
        if b.goto(x, y):
            return True
        b.advance_text(120)
    return b.pos() == (x, y)


def talk(b, mapname, suffix, side="D"):
    """stand next to the person whose script ends with `suffix` (on `side` of them) and talk; returns advance_text's result"""
    o = obj_by_script(mapname, suffix)
    dx, dy = {"D": (0, 1), "U": (0, -1), "L": (-1, 0), "R": (1, 0)}[side]
    face = {"D": "U", "U": "D", "L": "R", "R": "L"}[side]
    b.warp(mapname, o["x"] + dx, o["y"] + dy)
    return b.interact(face, 240)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)

    # ---------------------------------------------------------------- 4.1 the ferry (clerk) and the arrival scene on Route 4
    b.set_flag("FLAG_BADGE03_GET", True)
    b.set_var("VAR_ORLEANS_STORY", 16)
    talk(b, "CrescentCity_RiverboatTerminal", "TicketClerk0")
    t.check("the clerk keeps the boat in port while the Ward is unfinished (story 16 stays)", b.var("VAR_ORLEANS_STORY") == 16 and b.map_name() == "CrescentCity_RiverboatTerminal", b.where())
    b.set_var("VAR_ORLEANS_STORY", 17)
    b.set_var("VAR_ROUTE4_ARRIVAL", 0)
    talk(b, "CrescentCity_RiverboatTerminal", "TicketClerk0")
    b.frames(30)
    t.check("the riverboat lands on Route 4, story 18", b.map_name() == "Route4" and b.var("VAR_ORLEANS_STORY") == 18, b.where())
    b.shot("route4_landing")
    b.advance_text(90)
    t.check("the arrival scene played (var set)", b.var("VAR_ROUTE4_ARRIVAL") == 1)
    b.shot("route4_after_arrival")

    # ---------------------------------------------------------------- 4.2 the refinery gate scene, the valves, Jayden and Camille
    b.set_flag("FLAG_POINTE_GATE_SCENE_SEEN", False)
    t.check("warp west of the refinery gate", b.warp("PointeRouge", 18, 33), b.where())
    b.step("R")
    b.frames(30)
    t.check("the gate scene starts at story 18", b.script_status() != 2, b.where())
    b.shot("refinery_gate_scene")
    t.check("gate scene finishes", b.advance_text(120))
    t.check("gate scene is once-only (flag)", b.flag("FLAG_POINTE_GATE_SCENE_SEEN"))

    for f in ("FLAG_POINTE_VALVE_1", "FLAG_POINTE_VALVE_2", "FLAG_POINTE_VALVE_3", "FLAG_POINTE_VALVE_4"):
        b.set_flag(f, False)
    talk(b, "PointeRouge_Refinery", "Camille2", "D")
    t.check("Camille only taunts while the valves are open (no story change)", b.var("VAR_ORLEANS_STORY") == 18, b.var("VAR_ORLEANS_STORY"))
    # stand under/over each valve and press A facing it
    for n, (vx, vy, sx, sy, face) in enumerate(((7, 4, 7, 5, "U"), (15, 4, 15, 5, "U"), (7, 9, 7, 10, "U"), (15, 9, 15, 10, "U")), 1):
        b.warp("PointeRouge_Refinery", sx, sy)
        b.interact(face, 60)
        t.check("valve %d shuts" % n, b.flag("FLAG_POINTE_VALVE_%d" % n))
    b.shot("valves_shut")
    # Jayden battle 3, then Camille (battles are forced wins), story 19
    talk(b, "PointeRouge_Refinery", "Camille2", "D")
    t.check("Jayden + Camille scene finishes: story 19", b.var("VAR_ORLEANS_STORY") == 19, "story=%d %s" % (b.var("VAR_ORLEANS_STORY"), b.where()))
    t.check("both are hidden afterwards", b.flag("FLAG_HIDE_POINTE_CAMILLE") and b.flag("FLAG_HIDE_POINTE_JAYDEN"))
    b.shot("refinery_done")

    # ---------------------------------------------------------------- 4.3 the Route 5 tournament
    talk(b, "Route5", "Npc2", "D")
    t.check("the angler enters the player: Good Rod + story 20", b.flag("FLAG_RECEIVED_GOOD_ROD") and b.var("VAR_ORLEANS_STORY") == 20,
            "rod=%s story=%d" % (b.flag("FLAG_RECEIVED_GOOD_ROD"), b.var("VAR_ORLEANS_STORY")))
    talk(b, "Route5", "Npc2", "D")
    t.check("weigh-in with no bites does not win", not b.flag("FLAG_POINTE_TOURNEY_WON"))
    for _ in range(5):
        b.call("IncrementGameStat", 12)                      # GAME_STAT_FISHING_ENCOUNTERS: one fishing bite
    talk(b, "Route5", "Npc2", "D")
    t.check("five bites win the tournament", b.flag("FLAG_POINTE_TOURNEY_WON"))
    b.shot("tournament_won")

    # ---------------------------------------------------------------- 4.4 the gym: the tailwind puzzle, then Kingfisher
    b.set_flag("FLAG_POINTE_GYM_TAILWIND", False)
    b.set_var("VAR_POINTE_FAN_STEP", 0)
    b.warp("PointeRouge_Gym", 14, 10)
    b.interact("D", 40)                                       # the east fan first: wrong
    t.check("a wrong fan resets the sequence", b.var("VAR_POINTE_FAN_STEP") == 0 and not b.flag("FLAG_POINTE_GYM_TAILWIND"))
    # (the count restarts on every visit, so walk between the fans instead of warping)
    t.check("walk to the west fan", go(b, 6, 10), b.where())
    b.interact("D", 40)
    t.check("west fan starts the tailwind", b.var("VAR_POINTE_FAN_STEP") == 1, b.var("VAR_POINTE_FAN_STEP"))
    t.check("walk to the centre fan", go(b, 10, 8), b.where())
    b.interact("U", 40)
    t.check("centre fan next", b.var("VAR_POINTE_FAN_STEP") == 2, b.var("VAR_POINTE_FAN_STEP"))
    t.check("walk to the east fan", go(b, 14, 10), b.where())
    b.interact("D", 60)
    t.check("east fan last: the tailwind is up", b.flag("FLAG_POINTE_GYM_TAILWIND"))
    b.shot("gym_tailwind")
    # the gap at (6, 7) is open now: walk through it
    b.warp("PointeRouge_Gym", 6, 8)
    b.walk("UU")
    t.check("the nets are gone: through the gap into the rafters", b.pos()[1] <= 6, b.where())
    b.set_flag("FLAG_BADGE04_GET", False)
    b.set_var("VAR_ORLEANS_STORY", 20)
    b.set_flag("FLAG_RECEIVED_SUPER_ROD", False)
    b.set_flag("FLAG_RECEIVED_TM_AERIAL_ACE", False)
    talk(b, "PointeRouge_Gym", "Kingfisher0", "D")
    t.check("Kingfisher: badge 4, story 21, TM and Super Rod",
            b.flag("FLAG_BADGE04_GET") and b.var("VAR_ORLEANS_STORY") == 21 and b.flag("FLAG_RECEIVED_TM_AERIAL_ACE") and b.flag("FLAG_RECEIVED_SUPER_ROD"),
            "badge=%s story=%d" % (b.flag("FLAG_BADGE04_GET"), b.var("VAR_ORLEANS_STORY")))
    b.shot("kingfisher_done")

    # ---------------------------------------------------------------- 4.6 the Old Water visit: verse 4, HM Surf, the Route 6 debris, Wren
    b.set_flag("FLAG_ROUTE6_DEBRIS_CLEARED", False)
    b.set_flag("FLAG_RECEIVED_HM_SURF", False)
    talk(b, "OldWater_SongHouse", "Tupelo0", "D")
    t.check("Tupelo: debris cleared, HM Surf given, story 22",
            b.flag("FLAG_ROUTE6_DEBRIS_CLEARED") and b.flag("FLAG_RECEIVED_HM_SURF") and b.var("VAR_ORLEANS_STORY") == 22,
            "debris=%s surf=%s story=%d" % (b.flag("FLAG_ROUTE6_DEBRIS_CLEARED"), b.flag("FLAG_RECEIVED_HM_SURF"), b.var("VAR_ORLEANS_STORY")))
    b.shot("old_water_visit")
    b.set_flag("FLAG_RECEIVED_ROCKRUFF", False)
    talk(b, "OldWater_SongHouse", "Wren1", "D")
    t.check("Wren: friendly battle, then the Rockruff", b.flag("FLAG_RECEIVED_ROCKRUFF"))

    # ---------------------------------------------------------------- the Route 6 debris opens with the verse flag
    b.set_flag("FLAG_ROUTE6_DEBRIS_CLEARED", False)
    b.warp("Route6", 28, 22)
    blocked = not b.step("R")
    t.check("the debris blocks the shore path before the verse", blocked, b.where())
    b.set_flag("FLAG_ROUTE6_DEBRIS_CLEARED", True)
    b.warp("Route6", 28, 22)
    t.check("after the verse flag the debris is gone", b.step("R") and b.pos() == (29, 22), b.where())
    b.shot("route6_open")

    # ---------------------------------------------------------------- Surf unlocks with the fourth badge (not the fifth)
    b.set_flag("FLAG_BADGE04_GET", True)
    b.set_flag("FLAG_BADGE05_GET", False)
    b.set_move(1, "MOVE_SURF", 0)
    b.warp("Route5", 14, 6)
    b.face("R")
    b.press("A", 4, 20)
    b.frames(30)
    t.check("facing the lake with badge 4 and Surf: the Surf prompt appears", b.script_status() != 2, b.where())
    b.shot("surf_prompt")
    b.press("B", 4, 30)
    b.advance_text(20)

    # ---------------------------------------------------------------- the dust-storm gate (Route 23 stays closed)
    b.set_flag("FLAG_DUST_STORMS_LIFTED", False)
    b.warp("PointeRouge", 64, 6)
    b.step("R")
    b.frames(20)
    t.check("the dust storm stops the player at the east edge", b.script_status() != 2, b.where())
    b.advance_text(60)
    t.check("and turns the player back west", b.map_name() == "PointeRouge" and b.pos()[0] < 65, b.where())
