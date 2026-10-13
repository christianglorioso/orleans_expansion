"""Chapter 2: Storm's Edge arrival, Crescent arrival, the floodwater gate at Crescent's south exit.
(Jayden on the Route 3 bridge is t03_jayden_bridge.)"""


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)

    # --- 2.3 Storm's Edge arrival frame script (story 8 or 9 -> 10)
    b.set_var("VAR_ORLEANS_STORY", 9)
    arrived = b.warp("StormsEdge", 5, 24)
    t.check("warp into Storm's Edge", arrived, b.where())
    b.frames(30)
    b.shot("storms_edge_arrival")
    finished = b.advance_text(60)
    t.check("Storm's Edge arrival scene finishes", finished)
    t.check("story 9 -> 10 on arrival", b.var("VAR_ORLEANS_STORY") == 10, b.var("VAR_ORLEANS_STORY"))

    # --- 2.13 Crescent arrival frame script (story 12 -> 13)
    b.set_var("VAR_ORLEANS_STORY", 12)
    t.check("warp to Crescent City", b.warp("CrescentCity", 45, 58), b.where())
    b.frames(30)
    b.shot("crescent_arrival")
    finished = b.advance_text(90)
    t.check("Crescent arrival scene finishes", finished)
    t.check("story 12 -> 13 on arrival", b.var("VAR_ORLEANS_STORY") == 13, b.var("VAR_ORLEANS_STORY"))

    # --- floodwater at the south exit (fix B: a water state over rows 64-65 of the Route 14 connection until badge 6, trigger row y=63)
    from mapwalk import Grid
    b.set_flag("FLAG_BADGE06_GET", False)
    t.check("warp next to the floodwater gate", b.warp("CrescentCity", 45, 61), b.where())
    b.frames(20)
    g = Grid(b)
    t.check("the flood is drawn: the cells below the bank are water the player cannot enter (rows 64-65 collide)",
            all(g.cells[(x, y)][1] != 0 for x in (39, 45, 52, 60, 66) for y in (64, 65)), [g.cells[(x, 64)] for x in (39, 45, 66)])
    t.check("the bank row 63 stays walkable (the trigger row)", all(g.cells[(x, 63)][1] == 0 for x in (39, 45, 52, 66)))
    b.shot("flood_visible")
    b.walk("DD")                       # (45,62) then row 63: the trigger
    b.frames(20)
    b.shot("flood_message")
    t.check("gate shows a message (script running)", b.script_status() != 2, "status=%d at %s" % (b.script_status(), b.where()))
    finished = b.advance_text(40)
    b.frames(30)
    b.shot("flood_after")
    t.check("message dismisses (no freeze)", finished)
    t.check("player is turned back north (y < 63)", b.pos()[1] < 63 and b.map_name() == "CrescentCity", b.where())
    b.step("D")
    b.frames(20)
    finished2 = b.advance_text(40)
    t.check("second approach also resolves", finished2 and b.pos()[1] < 63, b.where())
    for x in (39, 40, 55, 66):
        b.warp("CrescentCity", x, 62)
        b.walk("D")
        b.frames(20)
        started = b.script_status() != 2
        ok = b.advance_text(40)
        t.check("gate at x=%d: message then turned back" % x, started and ok and b.pos()[1] < 63, b.where())
    for x in (38, 67):                 # the lawn beside the connection leads nowhere: still cannot reach Route 14 around the water
        b.warp("CrescentCity", x, 62)
        b.walk("DDD")
        t.check("beside the connection (x=%d) the player never gets onto Route 14" % x, b.map_name() == "CrescentCity", b.where())
    b.shot("flood_last_column")
    # after the 6th badge the road is dry again (the load reads the flag) and open
    b.set_flag("FLAG_BADGE06_GET", True)
    b.warp("CrescentCity", 45, 61)
    b.frames(20)
    g2 = Grid(b)
    t.check("with the badge the water is gone (rows 64-65 walkable)", all(g2.cells[(x, y)][1] == 0 for x in (39, 45, 66) for y in (64, 65)))
    b.shot("flood_gone")
    b.walk("DDD")
    b.frames(10)
    t.check("with the badge flag the gate does not trigger", b.script_status() == 2 and b.pos()[1] == 64,
            "status=%d %s" % (b.script_status(), b.where()))
