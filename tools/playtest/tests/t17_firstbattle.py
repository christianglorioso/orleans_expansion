"""The Wingull scene was cut (playtest feedback): a REAL new game, no set_var jumps. Mom (story 1), pick a starter (story 3 straight away), walk out over the old
Wingull cells (nothing starts), Lafayette's Pokedex (4), then Jayden at the landing is the first battle (the level-5 starter, battles shortcut by the bot) -> 5."""
from bot import map_data

LAFAYETTE_TRIGGER = (13, 44)
LANDING_TRIGGER = (20, 11)


def pick(b, t, label, suffix, var):
    shelter = [o for o in map_data("IsleMarais_Shelter")["objects"] if o["script"].endswith(suffix)][0]
    b.warp("IsleMarais_Shelter", shelter["x"], shelter["y"] + 1)
    b.frames(20)
    done = b.interact("U", 120)
    t.check("%s: the pick scene finishes" % label, done, b.where())
    t.check("%s: story is 3 right after the pick (no Wingull step)" % label, b.var("VAR_ORLEANS_STORY") == 3, "story=%d" % b.var("VAR_ORLEANS_STORY"))
    t.check("%s: VAR_STARTER_MON" % label, b.var("VAR_STARTER_MON") == var and b.party_count() == 1, "var=%d party=%d" % (b.var("VAR_STARTER_MON"), b.party_count()))


def run(b, t):
    b.new_game()
    b.interact("U")                                   # Mom
    t.check("story 1 after Mom", b.var("VAR_ORLEANS_STORY") == 1, "story=%d" % b.var("VAR_ORLEANS_STORY"))
    pick(b, t, "Fuecoco", "Fuecoco9", 2)
    # out of the shelter and over the old Wingull trigger cells
    b.warp("IsleMarais", 22, 4)
    b.frames(30)
    b.walk("DD")
    b.frames(40)
    t.check("walking the shelter steps starts nothing", not b.in_battle() and b.script_status() == 2 and b.var("VAR_ORLEANS_STORY") == 3, b.where())
    # Lafayette on Route 1
    b.warp("Route1", LAFAYETTE_TRIGGER[0], LAFAYETTE_TRIGGER[1] + 2)
    b.step("U")
    b.step("U")
    b.frames(30)
    t.check("Lafayette's scene starts at story 3", b.script_status() != 2 or b.var("VAR_ORLEANS_STORY") != 3, b.where())
    t.check("Lafayette scene finishes", b.advance_text(90))
    t.check("story 4 and the Pokedex", b.var("VAR_ORLEANS_STORY") == 4 and b.flag("FLAG_SYS_POKEDEX_GET"), "story=%d" % b.var("VAR_ORLEANS_STORY"))
    # the first battle: Jayden, with the fresh level-5 starter
    b.warp("Route1", LANDING_TRIGGER[0], LANDING_TRIGGER[1] + 2)
    b.step("U")
    b.step("U")
    b.frames(30)
    t.check("the landing scene starts", b.script_status() != 2 or b.in_battle(), b.where())
    t.check("the landing scene and the Jayden battle finish", b.advance_text(240), "cb2=%s %s" % (b.callback2_name(), b.where()))
    t.check("story 5 (canoe to the Old Water)", b.var("VAR_ORLEANS_STORY") == 5 and b.map_name() == "OldWater", "story=%d %s" % (b.var("VAR_ORLEANS_STORY"), b.where()))
