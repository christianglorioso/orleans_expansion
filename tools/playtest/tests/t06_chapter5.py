"""Chapter 5: Camp Cocodrie arrival (story 23), Isaac (24), the four cook-off ingredients, the judging table (25), the brothers' double
battle (26: badge 5, TM Sludge Bomb), the Route 10 water gate opening with badge 5, and Route 7's Pry Bar stump."""
from bot import map_data


def obj_by_script(mapname, suffix):
    for o in map_data(mapname)["objects"]:
        if o.get("script", "").endswith(suffix):
            return o
    return None


def talk(b, mapname, suffix, side="D", timeout=240):
    o = obj_by_script(mapname, suffix)
    dx, dy = {"D": (0, 1), "U": (0, -1), "L": (-1, 0), "R": (1, 0)}[side]
    face = {"D": "U", "U": "D", "L": "R", "R": "L"}[side]
    b.warp(mapname, o["x"] + dx, o["y"] + dy)
    return b.interact(face, timeout)


def menu_choice(b, down):
    """a script's multichoice is open once a Multichoice task runs: mash A through the text until then, move `down` entries, pick"""
    for _ in range(60):
        if any("ultichoice" in str(x) for x in b.active_tasks()):
            break
        b.press("A", 4, 30)
    b.frames(20)
    for _ in range(down):
        b.press("DOWN", 6, 14)
        b.frames(6)
    b.press("A", 4, 30)
    b.frames(20)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)

    # ---------------------------------------------------------------- 5.2 the arrival scene
    b.set_var("VAR_ORLEANS_STORY", 22)
    b.set_var("VAR_CAMP_ARRIVAL", 0)
    t.check("warp to Camp Cocodrie's landing", b.warp("CampCocodrie", 47, 14), b.where())
    b.frames(40)
    b.shot("camp_arrival")
    b.advance_text(120)
    t.check("arrival: story 23, scene once (var)", b.var("VAR_ORLEANS_STORY") == 23 and b.var("VAR_CAMP_ARRIVAL") == 1,
            "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_CAMP_ARRIVAL")))

    # ---------------------------------------------------------------- 5.3 Isaac at the nurse cabin door
    b.set_flag("FLAG_HIDE_CAMP_ISAAC", False)
    b.warp("CampCocodrie", 7, 23)
    b.face("U")
    b.press("A", 4, 20)
    b.advance_text(240)
    t.check("Isaac beaten: story 24 and he leaves the door", b.var("VAR_ORLEANS_STORY") == 24 and b.flag("FLAG_HIDE_CAMP_ISAAC"),
            "story=%d" % b.var("VAR_ORLEANS_STORY"))
    b.shot("isaac_done")

    # ---------------------------------------------------------------- 5.4 the four ingredients
    for f in ("FLAG_CAMP_FIRE_STOKED", "FLAG_CAMP_ANDOUILLE", "FLAG_CAMP_SHRIMP", "FLAG_CAMP_OKRA_ASKED", "FLAG_CAMP_OKRA", "FLAG_CAMP_FILE"):
        b.set_flag(f, False)
    talk(b, "CampCocodrie", "Fisherman", "U")
    t.check("the dock fisherman's battle gives the shrimp", b.flag("FLAG_CAMP_SHRIMP"))
    # smokehouse: smoker first (no fire yet), then the fire door, then the smoker again
    talk(b, "CampCocodrie_Smokehouse", "Smoker0", "U")
    t.check("the smoker will not give andouille before the fire is stoked", not b.flag("FLAG_CAMP_ANDOUILLE"))
    b.warp("CampCocodrie_Smokehouse", 5, 6)
    b.interact("U", 60)
    t.check("the smoker's fire door gets stoked", b.flag("FLAG_CAMP_FIRE_STOKED"))
    talk(b, "CampCocodrie_Smokehouse", "Smoker0", "U")
    t.check("then the smoker gives the andouille", b.flag("FLAG_CAMP_ANDOUILLE"))
    # okra: the patch refuses before the gardener has been asked
    b.warp("CampCocodrie", 45, 7)
    b.interact("U", 60)
    t.check("the okra patch is not picked before the gardener is asked", not b.flag("FLAG_CAMP_OKRA"))
    talk(b, "CampCocodrie_Cabin4", "Gardener0", "U")
    t.check("the gardener says go ahead", b.flag("FLAG_CAMP_OKRA_ASKED"))
    b.warp("CampCocodrie", 45, 7)
    b.interact("U", 60)
    t.check("then the okra is picked", b.flag("FLAG_CAMP_OKRA"))
    # filé: the rude answer is scolded, the polite one is given it
    o = obj_by_script("CampCocodrie_Cabin1", "OldNeighbour0")
    b.warp("CampCocodrie_Cabin1", o["x"] - 1, o["y"])
    b.face("R")
    b.press("A", 4, 30)
    menu_choice(b, 0)                                    # "Gimme the filé!"
    b.advance_text(60)
    t.check("the rude request gets no filé", not b.flag("FLAG_CAMP_FILE"))
    b.warp("CampCocodrie_Cabin1", o["x"] - 1, o["y"])
    b.face("R")
    b.press("A", 4, 30)
    menu_choice(b, 1)                                    # "Could I please have some filé?"
    b.advance_text(60)
    t.check("the polite request gets the filé", b.flag("FLAG_CAMP_FILE"))
    b.shot("ingredients")

    # ---------------------------------------------------------------- the judging table: a wrong pot, then the tie (story 25)
    b.set_var("VAR_ORLEANS_STORY", 24)
    b.warp("CampCocodrie_Gym", 9, 4)
    b.face("U")
    b.press("A", 4, 30)
    menu_choice(b, 0)                                    # Boudreaux's pot: wrong
    b.advance_text(60)
    t.check("a wrong pot does not settle it (story stays 24)", b.var("VAR_ORLEANS_STORY") == 24, b.var("VAR_ORLEANS_STORY"))
    b.warp("CampCocodrie_Gym", 9, 4)
    b.face("U")
    b.press("A", 4, 30)
    menu_choice(b, 2)                                    # it's a tie
    b.advance_text(60)
    t.check("calling it a tie: story 25", b.var("VAR_ORLEANS_STORY") == 25, b.var("VAR_ORLEANS_STORY"))
    b.shot("tie")

    # ---------------------------------------------------------------- 5.5 the brothers: a double battle (two usable POKéMON needed)
    b.set_flag("FLAG_BADGE05_GET", False)
    b.set_flag("FLAG_RECEIVED_TM_SLUDGE_BOMB", False)
    talk(b, "CampCocodrie_Gym", "Boudreaux0", "D", 360)
    b.frames(30)
    t.check("the double battle: badge 5, story 26, TM Sludge Bomb",
            b.flag("FLAG_BADGE05_GET") and b.var("VAR_ORLEANS_STORY") == 26 and b.flag("FLAG_RECEIVED_TM_SLUDGE_BOMB"),
            "badge=%s story=%d tm=%s %s" % (b.flag("FLAG_BADGE05_GET"), b.var("VAR_ORLEANS_STORY"), b.flag("FLAG_RECEIVED_TM_SLUDGE_BOMB"), b.where()))
    b.shot("brothers_done")

    # ---------------------------------------------------------------- Route 10's log jam opens with badge 5
    b.set_flag("FLAG_BADGE05_GET", False)
    b.warp("Route10", 10, 15)
    b.step("R")
    b.frames(20)
    t.check("Route 10's gate stops the player before badge 5", b.script_status() != 2, b.where())
    b.advance_text(60)
    t.check("and turns them back west of the cut (the Crescent side)", b.pos()[0] <= 10, b.where())
    b.set_flag("FLAG_BADGE05_GET", True)
    b.warp("Route10", 10, 15)
    b.step("R")
    b.frames(20)
    t.check("with badge 5 the gate lets the player through", b.script_status() == 2 and b.pos()[0] == 11, b.where())

    # ---------------------------------------------------------------- Route 7's Pry Bar stump (optional cache: Kleavorite)
    b.give_item("ITEM_PRY_BAR")
    b.set_flag("FLAG_ROUTE7_STUMP_OPENED", False)
    talk(b, "Route7", "Stump", "D")
    t.check("the stump opens with the Pry Bar", b.flag("FLAG_ROUTE7_STUMP_OPENED"))
