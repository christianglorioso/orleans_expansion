"""Chapter 2: Storm's Edge arrival, Crescent arrival, the floodwater gate at Crescent's south exit.
(Jayden on the Route 3 bridge is t03_jayden_bridge.)"""


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)

    # --- 2.3 Storm's Edge arrival frame script (story 8 or 9 -> 10)
    b.set_var("VAR_ORLEANS_STORY", 9)
    arrived = b.warp("StormsEdge", 5, 20)
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

    # --- floodwater gate at the south exit (triggers on row 65 while FLAG_BADGE06_GET is clear)
    b.set_flag("FLAG_BADGE06_GET", False)
    t.check("warp next to the floodwater gate", b.warp("CrescentCity", 45, 63), b.where())
    b.walk("DD")                       # (45,64) then row 65: the trigger
    b.frames(20)
    b.shot("flood_message")
    t.check("gate shows a message (script running)", b.script_status() != 2, "status=%d at %s" % (b.script_status(), b.where()))
    finished = b.advance_text(40)
    b.frames(30)
    b.shot("flood_after")
    t.check("message dismisses (no freeze)", finished)
    t.check("player is turned back north (y < 65)", b.pos()[1] < 65 and b.map_name() == "CrescentCity", b.where())
    # walking there again must behave the same, not freeze
    b.step("D")
    b.frames(20)
    finished2 = b.advance_text(40)
    t.check("second approach also resolves", finished2 and b.pos()[1] < 65, b.where())
    # and from other columns of the gate row
    for x in (40, 55, 66):
        b.warp("CrescentCity", x, 63)
        b.walk("DD")
        b.frames(20)
        started = b.script_status() != 2
        ok = b.advance_text(40)
        t.check("gate at x=%d: message then turned back" % x, started and ok and b.pos()[1] < 65, b.where())
    b.shot("flood_last_column")
    # after the 6th badge the road is open
    b.set_flag("FLAG_BADGE06_GET", True)
    b.warp("CrescentCity", 45, 63)
    b.walk("DD")
    b.frames(10)
    t.check("with the badge flag the gate does not trigger", b.script_status() == 2 and b.pos()[1] == 65,
            "status=%d %s" % (b.script_status(), b.where()))
