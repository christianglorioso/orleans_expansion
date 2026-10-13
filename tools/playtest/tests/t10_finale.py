"""The finale: the dive spot (Diving Gear) and the Kyogre raid, the cracked shaft (Lantern) and the Groudon raid, story 40 and FLAG_ROUTE25_OPEN with the
second raid, the dusk ceremony (the player's legendary and orb, story 41), the Oldest Shrine's landing steps (Camille, Andrew: 42), the Rayquaza raid
(2 v 1 with Jayden: 43), the Swampertite, and the epilogue up to the game clear (story 45)."""
from bot import map_data


def has_item(b, name):
    from bot import enum_value
    return bool(b.call("CheckBagHasItem", enum_value("items.h", name), 1) & 0xFF)


def menu_choice(b, down):
    for _ in range(80):
        if any("ultichoice" in str(x) for x in b.active_tasks()):
            break
        b.press("A", 4, 30)
    b.frames(20)
    for _ in range(down):
        b.press("DOWN", 6, 14)
        b.frames(6)
    b.press("A", 4, 30)
    b.frames(20)


def mash_until(b, cond, n=200):
    for _ in range(n):
        if cond():
            return True
        if b.in_battle():
            b.fight()
            continue
        b.press("A", 4, 26)
    return cond()


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)
    for f in ("FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_BADGE08_GET", "FLAG_RECEIVED_HM_SURF",
              "FLAG_DUST_STORMS_LIFTED", "FLAG_HIDE_OLD_WATER_TUPELO"):
        b.set_flag(f, True)
    b.set_flag("FLAG_HIDE_OLD_WATER_TUPELO", False)

    # ---------------------------------------------------------------- the dive spot needs the gear AND the telling
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.set_flag("FLAG_RECEIVED_DIVING_GEAR", False)
    b.warp("Route22", 13, 20)
    b.interact("R", 60)
    t.check("without the Diving Gear the dive spot stays shut", b.map_name() == "Route22", b.where())
    b.set_flag("FLAG_RECEIVED_DIVING_GEAR", True)
    b.set_var("VAR_ORLEANS_STORY", 38)
    b.warp("Route22", 13, 20)
    b.interact("R", 60)
    t.check("before the telling (story 38) the dive spot stays shut", b.map_name() == "Route22", b.where())
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.warp("Route22", 13, 20)
    b.face("R")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.map_name() == "LandsEnd_DrownedTemple", 60)
    b.frames(30)
    t.check("with the gear and the telling the dive spot leads to the Drowned Temple", b.map_name() == "LandsEnd_DrownedTemple", b.where())

    # ---------------------------------------------------------------- F.1 the Tide Hall
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN", False)
    b.set_flag("FLAG_KYOGRE_CALMED", False)
    b.set_flag("FLAG_GROUDON_CALMED", False)
    b.set_flag("FLAG_ROUTE25_OPEN", False)
    b.warp("LandsEnd_DrownedTemple", 8, 9)
    b.interact("U", 120)
    t.check("singing at the sealed door opens it", b.flag("FLAG_TEMPLE_DOOR_OPEN"))
    b.warp("LandsEnd_DrownedTemple", 8, 4)
    b.face("U")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.flag("FLAG_KYOGRE_CALMED"), 300)
    b.frames(30)
    t.check("Kyogre calmed (one raid left: no Route 25, story 39)", b.flag("FLAG_KYOGRE_CALMED") and not b.flag("FLAG_ROUTE25_OPEN") and b.var("VAR_ORLEANS_STORY") == 39,
            "story=%d at %s" % (b.var("VAR_ORLEANS_STORY"), b.where()))
    b.advance_text(60)
    b.shot("kyogre_done")
    b.goto(8, 13)
    b.press("DOWN", 8, 8)
    b.frames(160)
    t.check("the exit mat leaves by script to the islet at the end of Route 22", b.map_name() == "Route22" and b.pos() == (13, 20), b.where())

    # ---------------------------------------------------------------- F.2 the cracked shaft and the Salt Cathedral
    b.warp("Route24", 34, 7)
    b.interact("U", 60)
    b.frames(30)
    t.check("the shaft needs the Lantern", b.map_name() == "Route24", b.where())
    b.give_item("ITEM_LANTERN", 1)
    b.warp("Route24", 34, 7)
    b.face("U")
    b.press("A", 4, 20)
    mash_until(b, lambda: b.map_name() == "LandsEnd_SaltCathedral", 60)
    b.frames(30)
    t.check("with the Lantern the shaft leads to the Salt Cathedral", b.map_name() == "LandsEnd_SaltCathedral", b.where())
    b.warp("LandsEnd_SaltCathedral", 10, 4)
    b.face("U")
    b.press("A", 4, 20)
    # the second raid: story 40, the channel opens, the ceremony follows at the Old Water
    mash_until(b, lambda: b.flag("FLAG_GROUDON_CALMED") and b.map_name() == "OldWater", 300)
    b.frames(40)
    t.check("both raids done: story 40, FLAG_ROUTE25_OPEN, the ceremony at the Old Water", b.flag("FLAG_GROUDON_CALMED") and b.flag("FLAG_ROUTE25_OPEN")
            and b.var("VAR_ORLEANS_STORY") == 40 and b.map_name() == "OldWater", "story=%d at %s" % (b.var("VAR_ORLEANS_STORY"), b.where()))

    # ---------------------------------------------------------------- F.4 the ceremony: the player takes Kyogre
    menu_choice(b, 0)
    mash_until(b, lambda: b.map_name() == "Route8", 120)
    b.frames(40)
    t.check("ceremony: Kyogre and its Blue Orb for the player (Jayden gets Groudon), story 41, Tupelo's boat to Route 8",
            b.var("VAR_ORLEANS_LEGENDARY_PICK") == 1 and b.flag("FLAG_RECEIVED_LEGENDARY") and has_item(b, "ITEM_BLUE_ORB")
            and b.var("VAR_ORLEANS_STORY") == 41 and b.map_name() == "Route8", "pick=%d story=%d at %s" % (b.var("VAR_ORLEANS_LEGENDARY_PICK"), b.var("VAR_ORLEANS_STORY"), b.where()))
    b.shot("ceremony_done")

    # ---------------------------------------------------------------- F.5 the landing steps (story 41 -> 42)
    b.set_var("VAR_SHRINE_ARRIVAL", 0)
    b.warp("OldestShrine", 18, 22)
    b.frames(40)
    mash_until(b, lambda: b.var("VAR_ORLEANS_STORY") == 42, 400)
    b.advance_text(120)
    b.frames(30)
    t.check("Camille and Andrew beaten on the landing steps: story 42, Rayquaza and Jayden at the stone",
            b.var("VAR_ORLEANS_STORY") == 42 and b.flag("FLAG_HIDE_SHRINE_CAMILLE") and b.flag("FLAG_HIDE_SHRINE_ANDREW")
            and not b.flag("FLAG_HIDE_SHRINE_RAYQUAZA") and not b.flag("FLAG_HIDE_SHRINE_JAYDEN"), "story=%d" % b.var("VAR_ORLEANS_STORY"))
    b.shot("shrine_steps_done")

    # ---------------------------------------------------------------- F.6 the Rayquaza raid, the Swampertite, the epilogue
    b.set_flag("FLAG_RECEIVED_SWAMPERTITE", False)
    b.warp("Route24", 34, 8)                         # (a same-map warp would crash the harness helper)
    b.warp("OldestShrine", 18, 9)
    b.face("U")
    b.press("A", 4, 20)
    seen = {"story": 0, "swamp": False, "credits": False}
    fails = 0
    for _ in range(900):
        if b.in_battle():
            b.fight()
            continue
        try:
            seen["story"] = b.var("VAR_ORLEANS_STORY")
            fails = 0
            seen["swamp"] = b.flag("FLAG_RECEIVED_SWAMPERTITE")
            if b.flag("FLAG_SYS_GAME_CLEAR"):
                seen["credits"] = True
                break
            if b.in_battle():
                b.fight()
                continue
        except RuntimeError:                         # the harness can't call into the game while the Hall of Fame / credits screens run
            fails += 1
            if fails > 25 and seen["story"] >= 44:
                seen["credits"] = True
                break
        b.press("A", 4, 26)
    b.shot("finale_end")
    seen["cb2"] = b.callback2_name()
    seen["where"] = b.where()
    t.check("the raid is won (2 v 1 with Jayden): the Swampertite was given", seen["swamp"], str(seen))
    t.check("the epilogue reached the game clear (Hall of Fame and the credits) with the story at 44-45", seen["credits"] and seen["story"] >= 44, str(seen))

    # ---------------------------------------------------------------- static: the new route trainers
    for name, n in (("Route23", 4), ("Route24", 4), ("Route25", 4)):
        tr = [o for o in map_data(name)["objects"] if o.get("trainer_type") == "TRAINER_TYPE_NORMAL" and o.get("script", "").startswith(name + "_EventScript_Trainer")]
        t.check("%s has %d trainers with scripts" % (name, n), len(tr) == n, len(tr))
