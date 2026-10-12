"""Chapter 2: Jayden on the Route 3 bridge (story 11 -> 12). The five trigger rows at x 42: 0, 1, 8, 11, 12.

KNOWN CRASH (first run, ROM 8fdc7853): after winning the battle the game resets while printing the post-battle
message (Route3_Text_BridgeJaydenAfter). Shows up here as a CRASH result with screenshots."""

ROWS = (11, 12, 8, 1, 0)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    b.set_var("VAR_ORLEANS_STORY", 11)
    b.set_flag("FLAG_HIDE_ROUTE3_JAYDEN", True)
    t.check("warp to Route 3 west of the bridge", b.warp("Route3", 40, 11), b.where())
    b.shot("route3_before_bridge")
    b.walk("RR")                       # onto the trigger column at x 42
    b.frames(30)
    t.check("bridge trigger starts Jayden's scene", b.script_status() != 2 or b.in_battle(), b.where())
    b.shot("jayden_bridge_scene")
    b.last_where = b.where()
    finished = b.advance_text(240)     # raises GameCrash if the game resets
    b.shot("jayden_bridge_done")
    t.check("Jayden scene + battle finish (no freeze)", finished, "cb2=%s %s" % (b.callback2_name(), b.where()))
    t.check("story 11 -> 12", b.var("VAR_ORLEANS_STORY") == 12, b.var("VAR_ORLEANS_STORY"))
    t.check("Jayden hidden afterwards", b.flag("FLAG_HIDE_ROUTE3_JAYDEN"))

    # the other trigger rows must fire too (story reset to 11 each time)
    for row in ROWS[1:]:
        b.set_var("VAR_ORLEANS_STORY", 11)
        b.set_flag("FLAG_HIDE_ROUTE3_JAYDEN", True)
        if not b.warp("Route3", 41, row):
            t.check("warp to (41,%d)" % row, False, b.where())
            continue
        b.step("R")
        b.frames(30)
        t.check("trigger row %d starts the scene" % row, b.script_status() != 2 or b.in_battle(), b.where())
        b.advance_text(240)
        t.check("row %d scene completes, story 12" % row, b.var("VAR_ORLEANS_STORY") == 12, b.var("VAR_ORLEANS_STORY"))
