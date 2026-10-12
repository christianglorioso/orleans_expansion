"""Clean boot -> title -> New Game -> intro speech -> default name -> control in the shelter."""


def run(b, t):
    ok = b.new_game(shot_every=3)
    t.check("new game reaches the overworld with the player free", ok, b.callback2_name())
    t.check("no vanilla truck sequence at game start", not b.truck_seen)
    t.check("starts in IsleMarais_Shelter", b.map_name() == "IsleMarais_Shelter", b.where())
    t.check("story var is 0 at the start", b.var("VAR_ORLEANS_STORY") == 0, b.var("VAR_ORLEANS_STORY"))
    t.check("FLAG_ORLEANS_GAME_STARTED set by the shelter OnTransition", b.flag("FLAG_ORLEANS_GAME_STARTED"))
    b.shot("in_shelter")
    # the player can walk, and nothing is frozen
    moved = b.step("D") or b.step("R")
    t.check("player can take a step", moved, b.where())
    w = b.watch(4)
    t.check("no freeze / game loop alive", not w["frozen"] and w["frame_counter_advancing"], w)
    b.shot("after_step")
