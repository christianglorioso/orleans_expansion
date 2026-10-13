"""Vertical slice (story 0-8): Mom's gifts, leaving the shelter, the Pokedex, Jayden at the landing."""

LAFAYETTE_TRIGGER = (13, 44)      # Route1_EventScript_LafayetteCallsOver, story 3
LANDING_TRIGGER = (20, 11)        # Route1_EventScript_LandingStandoff, story 4


def run(b, t):
    b.new_game()
    t.check("boot ok in shelter", b.map_name() == "IsleMarais_Shelter", b.where())

    # --- step 1: Mom's gifts (real talk through the player's own inputs)
    b.shot("shelter_start")
    done = b.interact("U")
    t.check("Mom's talk script finishes", done)
    t.check("story 0 -> 1 after Mom", b.var("VAR_ORLEANS_STORY") == 1, b.var("VAR_ORLEANS_STORY"))
    t.check("Running Shoes + PokeNav flags set", b.flag("FLAG_SYS_B_DASH") and b.flag("FLAG_SYS_POKENAV_GET"))
    b.shot("after_mom")

    # --- jump: starter given; the pick sets story 3 (the Wingull scene was cut)
    b.give_mon("SPECIES_TOTODILE", 100)
    b.set_var("VAR_STARTER_MON", 2)
    b.set_var("VAR_ORLEANS_STORY", 3)
    b.goto(10, 13)
    b.step("D")                       # onto the door cell
    b.step("D")                       # through it
    b.settle()
    t.check("walked out of the shelter to Isle Marais", b.map_name() == "IsleMarais", b.where())
    b.shot("outside")

    # --- the shelter steps are free: walking over the old Wingull cells starts nothing
    b.walk("D")
    b.frames(30)
    t.check("no battle or scene on the shelter steps", not b.in_battle() and b.script_status() == 2 and b.var("VAR_ORLEANS_STORY") == 3, b.where())
    b.shot("steps_free")

    # --- step 5: Pokedex from Lafayette on Route 1 (story 3)
    b.warp("Route1", LAFAYETTE_TRIGGER[0], LAFAYETTE_TRIGGER[1] + 2)
    b.set_var("VAR_ORLEANS_STORY", 3)
    b.step("U")
    b.step("U")                       # onto the trigger row
    b.frames(30)
    t.check("Lafayette trigger starts a script", b.script_status() != 2 or b.var("VAR_ORLEANS_STORY") != 3, b.where())
    b.shot("lafayette_scene")
    finished = b.advance_text(90)
    t.check("Lafayette scene finishes", finished)
    t.check("story 3 -> 4 and Pokedex given", b.var("VAR_ORLEANS_STORY") == 4 and b.flag("FLAG_SYS_POKEDEX_GET"),
            "story=%s" % b.var("VAR_ORLEANS_STORY"))
    b.shot("after_lafayette")

    # --- step 7: Jayden at the boat landing (story 4): scene + battle (lv100 mon) -> story 5
    b.warp("Route1", LANDING_TRIGGER[0], LANDING_TRIGGER[1] + 2)
    b.set_var("VAR_ORLEANS_STORY", 4)
    b.step("U")
    b.step("U")
    b.frames(30)
    t.check("landing trigger starts the scene", b.script_status() != 2 or b.in_battle(), b.where())
    b.shot("landing_scene")
    finished = b.advance_text(180)
    b.shot("landing_done")
    story = b.var("VAR_ORLEANS_STORY")
    t.check("landing scene + Jayden battle finish", finished, "cb2=%s map=%s" % (b.callback2_name(), b.where()))
    t.check("story 4 -> 5 (canoe to the Old Water)", story == 5, "story=%d" % story)
    if story == 5:
        t.check("canoe warps to the Old Water", b.map_name() == "OldWater", b.where())
