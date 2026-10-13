"""Chapter 6: Lutin's Hollow arrival (story 27), the gym usher, Jayden battle 4 and Wren's song (28), the trial (pools, a false Lutin, the real
one: badge 6, TM Dazzling Gleam, story 29), the riddler's Delphoxite, Tupelo's verse 6 and the carver's cypress charm (30), the zydeco band's
Exploudite (night only), and the Mega stone vendor's stock script."""
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


def has_item(b, name):
    from bot import enum_value
    return bool(b.call("CheckBagHasItem", enum_value("items.h", name), 1) & 0xFF)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)

    # ---------------------------------------------------------------- 6.3 arrival, the gym usher, Jayden and Wren
    b.set_var("VAR_ORLEANS_STORY", 26)
    b.set_var("VAR_HOLLOW_ARRIVAL", 0)
    t.check("warp into Lutin's Hollow", b.warp("LutinsHollow", 3, 28), b.where())
    b.frames(40)
    b.shot("hollow_arrival")
    b.advance_text(120)
    t.check("arrival: story 27, scene once", b.var("VAR_ORLEANS_STORY") == 27 and b.var("VAR_HOLLOW_ARRIVAL") == 1,
            "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_HOLLOW_ARRIVAL")))
    talk(b, "LutinsHollow", "GymUsher", "D")
    t.check("the gym's pupil keeps the door shut at story 27 (story unchanged)", b.var("VAR_ORLEANS_STORY") == 27)
    talk(b, "LutinsHollow", "Jayden", "L")
    t.check("Jayden battle 4 and the song: story 28, both leave", b.var("VAR_ORLEANS_STORY") == 28 and b.flag("FLAG_HIDE_HOLLOW_JAYDEN") and b.flag("FLAG_HIDE_HOLLOW_WREN"),
            "story=%d" % b.var("VAR_ORLEANS_STORY"))
    b.shot("jayden_done")
    t.check("the gym pupil leaves the door with the scene", b.flag("FLAG_HIDE_HOLLOW_GYM_USHER"))

    # ---------------------------------------------------------------- 6.4 the trial: pools, a false Lutin, the real one
    b.warp("LutinsHollow_Gym", 5, 8)
    b.interact("D", 60)
    t.check("a pool with no reflection can be read (script ends)", b.script_status() == 2)
    b.warp("LutinsHollow_Gym", 5, 5)
    b.face("U")
    b.press("A", 4, 30)
    b.advance_text(120)
    b.frames(40)
    t.check("a false Lutin sends the player back to the door", b.map_name() == "LutinsHollow_Gym" and b.pos() == (10, 14), b.where())
    b.set_flag("FLAG_BADGE06_GET", False)
    b.set_flag("FLAG_RECEIVED_TM_DAZZLING_GLEAM", False)
    talk(b, "LutinsHollow_Gym", "TheReal2", "D", 600)
    b.frames(30)
    t.check("the real Lutin: badge 6, story 29, TM Dazzling Gleam",
            b.flag("FLAG_BADGE06_GET") and b.var("VAR_ORLEANS_STORY") == 29 and b.flag("FLAG_RECEIVED_TM_DAZZLING_GLEAM"),
            "badge=%s story=%d" % (b.flag("FLAG_BADGE06_GET"), b.var("VAR_ORLEANS_STORY")))
    b.shot("lutin_done")

    # ---------------------------------------------------------------- the riddler's Delphoxite
    b.set_var("VAR_HOLLOW_RIDDLES", 0)
    b.set_flag("FLAG_RECEIVED_DELPHOXITE", False)
    for n, down in ((1, 0), (2, 1), (3, 2)):
        o = obj_by_script("LutinsHollow_MossHouseN", "Riddler0")
        b.warp("LutinsHollow_MossHouseN", o["x"], o["y"] - 1)
        b.face("D")
        b.press("A", 4, 30)
        if n < 3:
            menu_choice(b, down)
            b.advance_text(60)
        else:
            menu_choice(b, down)
            b.advance_text(120)
        t.check("riddle %d answered" % n, b.var("VAR_HOLLOW_RIDDLES") >= n, b.var("VAR_HOLLOW_RIDDLES"))
    t.check("three riddles: the Delphoxite", b.flag("FLAG_RECEIVED_DELPHOXITE") and has_item(b, "ITEM_DELPHOXITE"))

    # ---------------------------------------------------------------- 6.6 verse 6 at Tupelo, the charm from the carver (story 30)
    b.set_flag("FLAG_RECEIVED_HM_SURF", True)
    b.set_flag("FLAG_ROUTE6_DEBRIS_CLEARED", True)
    b.set_flag("FLAG_VERSE6_HEARD", False)
    b.set_flag("FLAG_RECEIVED_CYPRESS_CHARM", False)
    talk(b, "OldWater_SongHouse", "Tupelo0", "D")
    t.check("Tupelo hears the sixth verse (flag), story stays 29", b.flag("FLAG_VERSE6_HEARD") and b.var("VAR_ORLEANS_STORY") == 29)
    talk(b, "OldWater_Carver", "Carver0", "D")
    t.check("the carver gives the cypress charm: item, story 30", has_item(b, "ITEM_MEGA_RING") and b.flag("FLAG_RECEIVED_CYPRESS_CHARM") and b.var("VAR_ORLEANS_STORY") == 30,
            "story=%d" % b.var("VAR_ORLEANS_STORY"))
    b.shot("charm")

    # ---------------------------------------------------------------- the zydeco band: Exploudite at night only, after badge 6
    b.set_flag("FLAG_RECEIVED_EXPLOUDITE", False)
    talk(b, "CampCocodrie_DancePorch", "ZydecoBand0", "D")
    got = b.flag("FLAG_RECEIVED_EXPLOUDITE")
    t.check("the band either gives the stone (night) or says to come at night (day), never both", (got and has_item(b, "ITEM_EXPLOUDITE")) or not got, "got=%s" % got)

    # ---------------------------------------------------------------- the Mega stone vendor opens at story 30 (the shop menu appears)
    b.set_var("VAR_ORLEANS_STORY", 30)
    o = obj_by_script("CrescentCity_Dept3f", "Clerk0")
    b.warp("CrescentCity_Dept3f", o["x"], o["y"] + 1)
    b.face("U")
    b.press("A", 4, 30)
    for _ in range(30):
        if any("hopMenu" in str(x) or "Shop" in str(x) for x in b.active_tasks()):
            break
        b.press("A", 4, 30)
    b.shot("vendor")
    shop = any("hopMenu" in str(x) or "Shop" in str(x) for x in b.active_tasks())
    t.check("the vendor's shop menu opens with the charm", shop, str(b.active_tasks()))
    b.press("B", 4, 30)
    b.press("B", 4, 30)

    # ---------------------------------------------------------------- hotfix 2026-10-13: the charm is never lost after the telling (story 38+)
    from bot import enum_value

    def lose_charm():
        b.call("RemoveBagItem", enum_value("items.h", "ITEM_MEGA_RING"), 1)
        b.set_flag("FLAG_RECEIVED_CYPRESS_CHARM", False)
        b.set_flag("FLAG_VERSE6_HEARD", False)

    def shop_opens():
        o = obj_by_script("CrescentCity_Dept3f", "Clerk0")
        b.warp("CrescentCity_Dept3f", o["x"], o["y"] + 1)
        b.face("U")
        b.press("A", 4, 30)
        for _ in range(30):
            if any("hopMenu" in str(x) or "Shop" in str(x) for x in b.active_tasks()):
                break
            b.press("A", 4, 30)
        opened = any("hopMenu" in str(x) or "Shop" in str(x) for x in b.active_tasks())
        for _ in range(4):
            b.press("B", 4, 30)
        b.advance_text(30)
        return opened

    b.set_flag("FLAG_BADGE06_GET", True)
    lose_charm()
    b.set_var("VAR_ORLEANS_STORY", 37)
    talk(b, "OldWater_Carver", "Carver0", "D")
    t.check("story 37, verse 6 unsung: the carver still withholds the charm", not has_item(b, "ITEM_MEGA_RING") and not b.flag("FLAG_RECEIVED_CYPRESS_CHARM"))
    t.check("no charm: the vendor stays closed (stock opens on owning the charm, not on the story)", not shop_opens())

    b.set_var("VAR_ORLEANS_STORY", 38)
    talk(b, "OldWater_Carver", "Carver0", "D")
    t.check("story 38, verse 6 never sung: the carver gives the charm (badge 6); the story stays 38", has_item(b, "ITEM_MEGA_RING") and b.flag("FLAG_RECEIVED_CYPRESS_CHARM") and b.var("VAR_ORLEANS_STORY") == 38,
            "story=%d" % b.var("VAR_ORLEANS_STORY"))
    t.check("story 38 with the charm: the vendor opens", shop_opens())

    lose_charm()
    b.set_var("VAR_ORLEANS_STORY", 39)          # (entering the song house at 38 plays the telling and moves on to 39)
    talk(b, "OldWater_SongHouse", "Tupelo0", "D")
    t.check("story 39, never sang verse 6: Tupelo still sings it (flag set, story unchanged)", b.flag("FLAG_VERSE6_HEARD") and b.var("VAR_ORLEANS_STORY") == 39,
            "heard=%s story=%d" % (b.flag("FLAG_VERSE6_HEARD"), b.var("VAR_ORLEANS_STORY")))
    talk(b, "OldWater_Carver", "Carver0", "D")
    t.check("story 39: the carver gives the charm after Tupelo's verse", has_item(b, "ITEM_MEGA_RING") and b.flag("FLAG_RECEIVED_CYPRESS_CHARM"))

    lose_charm()
    b.set_var("VAR_ORLEANS_STORY", 45)
    talk(b, "OldWater_Carver", "Carver0", "D")
    t.check("story 45, verse 6 never heard: the carver alone gives the charm (badge 6 held)", has_item(b, "ITEM_MEGA_RING") and b.flag("FLAG_RECEIVED_CYPRESS_CHARM") and b.var("VAR_ORLEANS_STORY") == 45,
            "story=%d" % b.var("VAR_ORLEANS_STORY"))
    lose_charm()
    talk(b, "OldWater_SongHouse", "Tupelo0", "D")
    t.check("story 45: Tupelo sings verse 6 for a player without the charm", b.flag("FLAG_VERSE6_HEARD") and b.var("VAR_ORLEANS_STORY") == 45)
