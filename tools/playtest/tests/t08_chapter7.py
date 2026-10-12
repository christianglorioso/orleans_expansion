"""Chapter 7: Redfield arrival (story 31), Rita's Mega Chandelure at the yard gate (32), the mill yard trial (mirrors by day only, three dials in
order, locked mirrors, the shutter), Cayenne (badge 7, TM Overheat, Charizardite Y, story 33), Wren's call and Isaac's raid at the Old Water
(a partner battle, story 34), the rougarou (night only) and its Lycanrocite, and static checks of the route trainers."""
from bot import map_data

DAY = 1760000000            # 08:53: morning (not night)
NIGHT = DAY + 14 * 3600     # 22:53: night
MIRRORS = {"A": (30, 4, 31, 4, "L"), "B": (32, 4, 31, 4, "R"), "C": (32, 8, 31, 8, "R"), "D": (30, 10, 31, 10, "L"),
           "E": (29, 10, 28, 10, "R"), "F": (26, 10, 27, 10, "L")}   # sign x, y, standing x, y, facing
SOLUTION = {"A": 3, "B": 1, "C": 0, "D": 1, "E": 3, "F": 2}   # OrleansSvc in src/orleans_services.c


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


def set_time(b, secs):
    b.h.cmd("rtc %d" % secs)
    b.frames(30)


def press_mirror(b, k):
    sx, sy, px, py, face = MIRRORS[k]
    b.warp("Redfield", px, py)
    b.interact(face, 120)
    b.frames(20)


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


def lose_battle(b, max_s=60):
    """force a LOSS (the autopilot only wins): at the action selection point jump to the lost end-of-turn"""
    main_func = b.sym("gBattleMainFunc")
    for i in range(max_s * 2):
        if not b.in_battle():
            return True
        if (b.r32(main_func) & ~1) == b.sym("HandleTurnActionSelectionState"):
            b.w8(b.sym("gBattleOutcome"), 2)                                       # B_OUTCOME_LOST
            b.w32(main_func, b.syms.call_addr("HandleEndTurn_BattleLost"))
        b.press("A", 4, 26)
    return not b.in_battle()


def mirror_bits(b):
    return b.var("VAR_REDFIELD_MIRRORS")


def set_mirrors(b, **facing):
    v = 0
    for i, k in enumerate("ABCDEF"):
        v |= (facing.get(k, 0) & 3) << (i * 2)
    b.set_var("VAR_REDFIELD_MIRRORS", v)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)
    for f in ("FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_RECEIVED_HM_SURF"):
        b.set_flag(f, True)
    set_time(b, DAY)

    # ---------------------------------------------------------------- 7.1 arrival (from story 30; the charm is optional so 29 works too)
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.set_var("VAR_REDFIELD_ARRIVAL", 0)
    t.check("warp into Redfield", b.warp("Redfield", 2, 17), b.where())
    b.frames(40)
    b.shot("redfield_arrival")
    b.advance_text(120)
    t.check("arrival: story 31, scene once (var), Rita at the gate", b.var("VAR_ORLEANS_STORY") == 31 and b.var("VAR_REDFIELD_ARRIVAL") == 1
            and not b.flag("FLAG_HIDE_REDFIELD_RITA"), "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_REDFIELD_ARRIVAL")))

    # ---------------------------------------------------------------- 7.3 Rita at the yard gate (story 31 -> 32)
    b.warp("Redfield", 29, 15)
    b.step("U")                                   # onto the trigger row (29, 14)
    b.frames(30)
    b.advance_text(300)
    b.frames(30)
    t.check("Rita beaten at the gate: story 32, she leaves", b.var("VAR_ORLEANS_STORY") == 32 and b.flag("FLAG_HIDE_REDFIELD_RITA")
            and b.flag("FLAG_REDFIELD_RITA_BEATEN"), "story=%d" % b.var("VAR_ORLEANS_STORY"))
    b.shot("rita_done")
    b.warp("Redfield", 29, 15)
    b.step("U")
    b.frames(20)
    t.check("the gate trigger is quiet once the story is 32", b.script_status() == 2 and b.pos() == (29, 14), b.where())

    # ---------------------------------------------------------------- 7.4 the mill yard trial
    set_time(b, NIGHT)
    b.set_var("VAR_REDFIELD_MIRRORS", 0)
    press_mirror(b, "D")
    t.check("at night the mirrors do nothing", mirror_bits(b) == 0, mirror_bits(b))
    set_time(b, DAY)
    # out of order: dial 3's pair is right but dial 2 isn't lit
    set_mirrors(b, A=2, F=2)
    press_mirror(b, "A")
    t.check("a right pair out of order lights nothing", not b.flag("FLAG_REDFIELD_SUN3") and not b.flag("FLAG_REDFIELD_SUN1")
            and (mirror_bits(b) & 3) == 3, "flags %s %s bits %d" % (b.flag("FLAG_REDFIELD_SUN1"), b.flag("FLAG_REDFIELD_SUN3"), mirror_bits(b)))
    # dial 1: D and E
    set_mirrors(b, A=3, F=2, D=0, E=3)
    press_mirror(b, "D")
    t.check("dial 1 (D and E) lights", b.flag("FLAG_REDFIELD_SUN1") and not b.flag("FLAG_REDFIELD_SUN2"),
            "sun1=%s sun2=%s" % (b.flag("FLAG_REDFIELD_SUN1"), b.flag("FLAG_REDFIELD_SUN2")))
    before = mirror_bits(b)
    press_mirror(b, "D")
    t.check("a lit dial's mirror is fixed in place", mirror_bits(b) == before, "%d -> %d" % (before, mirror_bits(b)))
    # dial 2 completes and cascades into dial 3 (its pair is already right): the mill opens
    set_mirrors(b, A=3, F=2, D=1, E=3, B=0, C=0)
    press_mirror(b, "B")
    t.check("dials 2 and 3 light together, the shutter goes up", b.flag("FLAG_REDFIELD_SUN2") and b.flag("FLAG_REDFIELD_SUN3")
            and b.flag("FLAG_REDFIELD_MILL_OPEN"), "sun2=%s sun3=%s open=%s" % (b.flag("FLAG_REDFIELD_SUN2"), b.flag("FLAG_REDFIELD_SUN3"), b.flag("FLAG_REDFIELD_MILL_OPEN")))
    b.shot("mill_open")
    # a middle sundial reads lit
    b.warp("Redfield", 31, 6)
    b.interact("R", 60)
    t.check("a lit sundial can be read (script ends)", b.script_status() == 2)

    # ---------------------------------------------------------------- 7.5 Cayenne (story 32 -> 33)
    b.set_var("VAR_ORLEANS_STORY", 31)
    talk(b, "Redfield_Gym", "Cayenne0", "D", 300)
    t.check("Cayenne won't battle before Rita (no badge, story stays 31)", not b.flag("FLAG_BADGE07_GET") and b.var("VAR_ORLEANS_STORY") == 31)
    b.set_var("VAR_ORLEANS_STORY", 32)
    b.set_flag("FLAG_BADGE07_GET", False)
    b.set_flag("FLAG_RECEIVED_TM050_OVERHEAT", False)
    b.set_flag("FLAG_RECEIVED_CHARIZARDITE_Y", False)
    talk(b, "Redfield_Gym", "Cayenne0", "D", 600)
    b.frames(30)
    t.check("Cayenne: badge 7, story 33", b.flag("FLAG_BADGE07_GET") and b.var("VAR_ORLEANS_STORY") == 33, "story=%d" % b.var("VAR_ORLEANS_STORY"))
    t.check("TM Overheat and the Charizardite Y (flags + bag)", b.flag("FLAG_RECEIVED_TM050_OVERHEAT") and b.flag("FLAG_RECEIVED_CHARIZARDITE_Y")
            and has_item(b, "ITEM_CHARIZARDITE_Y"))
    b.shot("cayenne_done")

    # ---------------------------------------------------------------- 7.6 Wren's call and Isaac's raid (story 33 -> 34)
    b.set_var("VAR_REDFIELD_RAID_CALL", 0)
    b.set_var("VAR_OLD_WATER_RAID", 0)
    b.set_flag("FLAG_HIDE_RAID_ISAAC", False)       # (a load must hide the raid actors again: OldWater_OnTransition)
    b.warp("Redfield", 37, 14)
    b.frames(40)
    b.advance_text(120)
    for _ in range(40):
        if b.var("VAR_ORLEANS_STORY") == 34:
            break
        b.advance_text(120)
        b.frames(30)
    b.shot("raid_done")
    t.check("the raid is defended: story 34, var 2, back in Redfield by the mill", b.var("VAR_ORLEANS_STORY") == 34 and b.var("VAR_OLD_WATER_RAID") == 2
            and b.map_name() == "Redfield", "story=%d var=%d at %s" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_OLD_WATER_RAID"), b.where()))
    t.check("Isaac and the grunts are gone for good, Wren too", b.flag("FLAG_HIDE_RAID_ISAAC") and b.flag("FLAG_HIDE_RAID_GRUNT1")
            and b.flag("FLAG_HIDE_RAID_GRUNT2") and b.flag("FLAG_HIDE_REDFIELD_WREN"))

    # a LOSS in the raid, then NOT YET: back in Redfield, the raid reset, Wren waiting outside the mill
    b.set_var("VAR_ORLEANS_STORY", 33)
    b.set_var("VAR_REDFIELD_RAID_CALL", 1)
    b.set_var("VAR_OLD_WATER_RAID", 1)
    b.warp("OldWater", 22, 32)
    for _ in range(80):
        if b.in_battle():
            break
        b.press("A", 4, 30)
    lose_battle(b)
    menu_choice(b, 1)                              # TRY AGAIN / NOT YET: NOT YET
    for _ in range(30):
        if b.map_name() == "Redfield":
            break
        b.advance_text(60)
        b.frames(30)
    b.frames(40)
    b.advance_text(60)
    t.check("a loss then NOT YET: back in Redfield, story 33, raid var 0, Wren waits outside the mill",
            b.map_name() == "Redfield" and b.var("VAR_ORLEANS_STORY") == 33 and b.var("VAR_OLD_WATER_RAID") == 0
            and not b.flag("FLAG_HIDE_REDFIELD_WREN"), "%s story=%d var=%d" % (b.where(), b.var("VAR_ORLEANS_STORY"), b.var("VAR_OLD_WATER_RAID")))
    b.shot("raid_not_yet")
    b.warp("Redfield", 37, 14)
    b.interact("R", 400)                           # Wren (38, 14): the retry path after NOT YET
    for _ in range(40):
        if b.var("VAR_ORLEANS_STORY") == 34:
            break
        b.advance_text(120)
        b.frames(30)
    t.check("after NOT YET, talking to Wren retries the raid and it can be won (story 34)", b.var("VAR_ORLEANS_STORY") == 34 and b.var("VAR_OLD_WATER_RAID") == 2,
            "story=%d var=%d" % (b.var("VAR_ORLEANS_STORY"), b.var("VAR_OLD_WATER_RAID")))
    b.warp("OldWater", 22, 32)
    b.frames(30)
    t.check("outside the raid the Old Water has no raiders (hidden on load)", b.flag("FLAG_HIDE_RAID_ISAAC") and b.flag("FLAG_HIDE_RAID_GRUNT1")
            and b.flag("FLAG_HIDE_RAID_GRUNT2") and b.flag("FLAG_HIDE_RAID_WREN"))

    # ---------------------------------------------------------------- 7.1 the rougarou (night only), then Lycanrocite
    b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
    b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
    set_time(b, DAY)
    b.warp("Route14", 12, 12)
    b.frames(30)
    t.check("by day the rougarou is not on the crest", b.flag("FLAG_HIDE_ROUTE14_ROUGAROU"))
    set_time(b, NIGHT)
    b.warp("Route14", 12, 12)
    b.frames(30)
    t.check("at night the rougarou is on the crest", not b.flag("FLAG_HIDE_ROUTE14_ROUGAROU"))
    b.warp("Route14", 21, 30)
    b.interact("U", 300)
    b.frames(30)
    t.check("rougarou beaten: Lycanrocite in the bag, one-off flags set", b.flag("FLAG_ROUTE14_ROUGAROU_DONE") and b.flag("FLAG_RECEIVED_LYCANROCITE")
            and has_item(b, "ITEM_LYCANROCITE"), "done=%s got=%s" % (b.flag("FLAG_ROUTE14_ROUGAROU_DONE"), b.flag("FLAG_RECEIVED_LYCANROCITE")))
    set_time(b, DAY)

    # ---------------------------------------------------------------- static checks: the route trainers
    for name, n in (("Route14", 6), ("Route15", 5), ("Route16", 5), ("Route17", 4)):
        tr = [o for o in map_data(name)["objects"] if o.get("trainer_type") == "TRAINER_TYPE_NORMAL" and o.get("script", "").startswith(name + "_EventScript_Trainer")]
        t.check("%s has %d trainers with scripts" % (name, n), len(tr) == n, len(tr))
