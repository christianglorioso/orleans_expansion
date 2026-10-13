"""Chapter 8: Land's End arrival (story 35), Heron's verse panels (a wrong order resets, the right order ends the rain), Heron (badge 8, TM Scald,
Gyaradosite, Diving Gear, story 36), Andrew named and Jayden battle 5 (37), Rayquaza wakes (38, the dust storms lift), the full telling at the Old Water
(39), the Kabuto revival at Lafayette's, and the route trainers."""
from bot import map_data

# panel -> (standing x, y, facing); verses in order 1..7 are B, D, F, A, G, C, E (story_data_ch8.PANELS)
STAND = {"A": (2, 8, "U"), "B": (5, 8, "U"), "C": (8, 8, "U"), "D": (11, 8, "U"), "E": (14, 8, "U"), "F": (17, 8, "U"), "G": (10, 11, "U")}
ORDER = "BDFAGCE"


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


def has_item(b, name):
    from bot import enum_value
    return bool(b.call("CheckBagHasItem", enum_value("items.h", name), 1) & 0xFF)


def press_panel(b, k):
    x, y, f = STAND[k]
    b.warp("LandsEnd_Gym", x, y)
    b.interact(f, 120)
    b.frames(20)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)
    for f in ("FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_RECEIVED_HM_SURF"):
        b.set_flag(f, True)

    # ---------------------------------------------------------------- sequence break: Land's End reached (by Surf) before the raid, story 33
    b.set_var("VAR_ORLEANS_STORY", 33)
    b.set_var("VAR_LANDS_END_ARRIVAL", 0)
    b.set_flag("FLAG_BADGE08_GET", False)
    b.warp("LandsEnd", 3, 20)
    b.frames(60)
    t.check("at story 33 the arrival changes nothing (story 33, still armed)", b.var("VAR_ORLEANS_STORY") == 33 and b.var("VAR_LANDS_END_ARRIVAL") == 0,
            "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_LANDS_END_ARRIVAL")))
    talk(b, "LandsEnd_Gym", "Heron0", "D", 300)
    t.check("Heron refuses at story 33 (no badge, story stays 33)", not b.flag("FLAG_BADGE08_GET") and b.var("VAR_ORLEANS_STORY") == 33)
    b.set_var("VAR_ORLEANS_STORY", 34)               # the raid is done later
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.warp("LandsEnd", 3, 20)
    b.frames(40)
    b.advance_text(120)
    t.check("the raid done later: Land's End's arrival still sets story 35", b.var("VAR_ORLEANS_STORY") == 35 and b.var("VAR_LANDS_END_ARRIVAL") == 1,
            "story=%d" % b.var("VAR_ORLEANS_STORY"))

    # ---------------------------------------------------------------- 8.1 arrival (story 34 -> 35)
    b.set_var("VAR_ORLEANS_STORY", 34)
    b.set_var("VAR_LANDS_END_ARRIVAL", 0)
    b.advance_text(60)
    b.frames(60)
    b.warp("LandsEnd_Pokecenter", 7, 5)                        # (a same-map warp can crash the harness helper)
    t.check("warp into Land's End", b.warp("LandsEnd", 3, 20), b.where())
    b.frames(40)
    b.shot("lands_end_arrival")
    b.advance_text(120)
    t.check("arrival: story 35, scene once (var)", b.var("VAR_ORLEANS_STORY") == 35 and b.var("VAR_LANDS_END_ARRIVAL") == 1,
            "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_LANDS_END_ARRIVAL")))

    # ---------------------------------------------------------------- 8.2 Heron's trial: the verse panels
    b.set_var("VAR_HERON_PANELS", 0)
    b.set_flag("FLAG_HERON_TRIAL_DONE", False)
    talk(b, "LandsEnd_Gym", "Heron0", "D", 300)
    t.check("Heron won't battle before the panels (no badge, story 35)", not b.flag("FLAG_BADGE08_GET") and b.var("VAR_ORLEANS_STORY") == 35)
    press_panel(b, "B")
    t.check("verse 1 first: the count is 1", b.var("VAR_HERON_PANELS") == 1, b.var("VAR_HERON_PANELS"))
    press_panel(b, "A")
    t.check("a wrong panel resets the count", b.var("VAR_HERON_PANELS") == 0 and not b.flag("FLAG_HERON_TRIAL_DONE"), b.var("VAR_HERON_PANELS"))
    for k in ORDER:
        press_panel(b, k)
    b.shot("panels_done")
    t.check("the seven panels in order end the rain", b.flag("FLAG_HERON_TRIAL_DONE") and b.var("VAR_HERON_PANELS") == 7,
            "done=%s count=%d" % (b.flag("FLAG_HERON_TRIAL_DONE"), b.var("VAR_HERON_PANELS")))

    # ---------------------------------------------------------------- 8.3 Heron (story 35 -> 36)
    b.set_flag("FLAG_BADGE08_GET", False)
    for f in ("FLAG_RECEIVED_TM082_SCALD", "FLAG_RECEIVED_GYARADOSITE", "FLAG_RECEIVED_DIVING_GEAR"):
        b.set_flag(f, False)
    talk(b, "LandsEnd_Gym", "Heron0", "D", 600)
    b.frames(30)
    t.check("Heron: badge 8, story 36", b.flag("FLAG_BADGE08_GET") and b.var("VAR_ORLEANS_STORY") == 36, "story=%d" % b.var("VAR_ORLEANS_STORY"))
    t.check("TM Scald, Gyaradosite and the Diving Gear (flags + bag)", b.flag("FLAG_RECEIVED_TM082_SCALD") and b.flag("FLAG_RECEIVED_GYARADOSITE")
            and b.flag("FLAG_RECEIVED_DIVING_GEAR") and has_item(b, "ITEM_GYARADOSITE") and has_item(b, "ITEM_DIVING_GEAR"))
    b.shot("heron_done")

    # ---------------------------------------------------------------- 8.4-8.6 Andrew, Jayden 5, Rayquaza, the telling
    b.set_var("VAR_LANDS_END_SCENE", 0)
    b.set_var("VAR_OLD_WATER_TELLING", 0)
    b.set_flag("FLAG_DUST_STORMS_LIFTED", False)
    b.warp("LandsEnd", 27, 36)                       # just outside the pavilion door: stepping onto the approach cell plays the scene
    b.frames(20)
    b.step("U")
    b.frames(40)
    b.advance_text(200)
    for _ in range(60):
        if b.var("VAR_ORLEANS_STORY") >= 39:
            break
        b.advance_text(120)
        b.frames(30)
    b.shot("telling_done")
    t.check("Andrew, Jayden 5, Rayquaza and the telling: story 39 back at Land's End", b.var("VAR_ORLEANS_STORY") == 39 and b.var("VAR_LANDS_END_SCENE") == 1
            and b.var("VAR_OLD_WATER_TELLING") == 2 and b.map_name() == "LandsEnd", "story=%d at %s" % (b.var("VAR_ORLEANS_STORY"), b.where()))
    t.check("the dust storms lifted (Rayquaza woke)", b.flag("FLAG_DUST_STORMS_LIFTED"))
    t.check("Andrew and Jayden are gone for good", b.flag("FLAG_HIDE_LANDS_END_ANDREW") and b.flag("FLAG_HIDE_LANDS_END_JAYDEN"))

    # ---------------------------------------------------------------- 8.1 the fossil revival
    b.give_item("ITEM_DOME_FOSSIL", 1)
    b.set_flag("FLAG_KABUTO_REVIVED", False)
    before = b.party_count()
    talk(b, "CrescentCity_Conservation", "Lafayette0", "D", 300)
    t.check("Lafayette revives the Dome Fossil: a Kabuto, the fossil used", b.flag("FLAG_KABUTO_REVIVED") and not has_item(b, "ITEM_DOME_FOSSIL"),
            "flag=%s" % b.flag("FLAG_KABUTO_REVIVED"))
    t.check("the Kabuto went to the party (room there), not the PC", b.party_count() == before + 1, "%d -> %d" % (before, b.party_count()))

    # ---------------------------------------------------------------- the route trainers
    for name, n in (("Route18", 4), ("Route19", 4), ("Route20", 4), ("Route21", 4), ("Route22", 3)):
        tr = [o for o in map_data(name)["objects"] if o.get("trainer_type") == "TRAINER_TYPE_NORMAL" and o.get("script", "").startswith(name + "_EventScript_Trainer")]
        t.check("%s has %d trainers with scripts" % (name, n), len(tr) == n, len(tr))
