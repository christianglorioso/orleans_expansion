"""DexNav: the START menu has no DEXNAV before Lafayette gives it (Crescent City Conservation office, story 13 briefing, or the next visit for a player past
it) and has it after; a species registered on Route 2 starts a search (R in the field), creeping onto the target tile starts the battle against that
species; the overworld speedup is forced to 1x while searching; the night table is used at night (Zubat), the day table by day; the search level var starts
at 0 and the DexNav vars survive a save and continue; an old save loads with the DexNav off. SaveBlock3 is not touched (search levels live in a var)."""
import importlib.util as _ilu
import re
from pathlib import Path as _Path

from bot import Bot, ROOT, enum_value

_here = _Path(__file__).parent


def _load(name):
    spec = _ilu.spec_from_file_location(name, _here / (name + ".py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


speed = _load("t16_speed")
fixc = _load("t_fixc")
oldsave = _load("t13b_oldsave")

DEXNAV_ACTION = None


def dexnav_action_id():
    s = (ROOT / "src/start_menu.c").read_text(encoding="utf-8")
    m = re.search(r"enum\s*\{(.*?)\};", s, re.S)
    names = [x.strip().split("=")[0].strip() for x in m.group(1).split(",") if x.strip() and not x.strip().startswith("//")]
    return names.index("MENU_ACTION_DEXNAV")


def start_menu_actions(b):
    """open the START menu, read the action list, close it"""
    b.press("START", 6, 30)
    b.frames(20)
    n = b.r8(b.sym("sNumStartMenuActions"))
    acts = [b.r8(b.sym("sCurrentStartMenuActions") + i) for i in range(n)]
    b.shot("start_menu_%d" % n)
    b.press("B", 6, 30)
    b.frames(20)
    return acts


def save_game(b):
    """START menu -> SAVE (wherever it is in the list now that DEXNAV is there) -> YES -> overwrite YES; waits for the flash write"""
    src = (ROOT / "src/start_menu.c").read_text(encoding="utf-8")
    m = re.search(r"enum\s*\{(.*?)\};", src, re.S)
    names = [x.strip().split("=")[0].strip() for x in m.group(1).split(",") if x.strip() and not x.strip().startswith("//")]
    save_id = names.index("MENU_ACTION_SAVE")
    b.press("START", 6, 30)
    b.frames(20)
    n = b.r8(b.sym("sNumStartMenuActions"))
    acts = [b.r8(b.sym("sCurrentStartMenuActions") + i) for i in range(n)]
    for _ in range(acts.index(save_id)):
        b.press("DOWN", 6, 10)
    b.press("A", 6, 40)
    b.frames(150)
    b.press("A", 6, 40)
    b.frames(200)
    b.press("A", 6, 40)
    b.frames(900)
    for _ in range(4):
        b.press("A", 4, 60)
    b.frames(120)


def register(b, species, env=0):
    b.set_var("VAR_DEXNAV_SPECIES", enum_value("species.h", species) | (env << 14))


def start_search(b):
    b.press("R", 6, 20)
    b.frames(30)
    return b.flag("FLAG_DEXNAV_SEARCHING")


def creep_onto_target(b):
    """point the search's target tile at the cell south of the player (the target is normally 5-20 tiles away) and creep onto it (A held)"""
    ptr = b.r32(b.sym("sDexNavSearchDataPtr"))
    if not ptr:
        return False
    px, py = b.pos()
    b.w16(ptr + 18, px + 7)               # DexNavSearch.tileX / tileY (map grid coordinates, +7)
    b.w16(ptr + 20, py + 8)
    b.hold("DOWN+A")
    for _ in range(200):
        b.frames(1)
        if b.in_battle():
            break
    b.release()
    for _ in range(400):
        if b.in_battle():
            break
        b.frames(1)
    b.frames(60)
    return b.in_battle()


def enemy_species(b):
    base = b.r32(b.sym("gEnemyPartyPtr"))
    return b.call("GetMonData2", base, fixc.md("MON_DATA_SPECIES")) & 0xFFFF


def leave_battle(b):
    b.fight()
    b.frames(60)


def run(b, t):
    cfg = (ROOT / "include/config/dexnav.h").read_text(encoding="utf-8")
    t.check("DEXNAV_ENABLED is TRUE, search levels in the registered-species (var) mode, no per-species array in SaveBlock3",
            re.search(r"#define DEXNAV_ENABLED\s+TRUE", cfg) and re.search(r"#define USE_DEXNAV_SEARCH_LEVELS\s+DEXNAV_SEARCH_LEVELS_REGISTERED_SPECIES", cfg))

    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 13)
    t.check("a new game: the DexNav flag is off, the species / level vars are 0",
            not b.flag("FLAG_DEXNAV_OBTAINED") and b.var("VAR_DEXNAV_SPECIES") == 0 and b.var("VAR_DEXNAV_SEARCH_LEVEL") == 0)
    want = dexnav_action_id()
    b.warp("CrescentCity_Conservation", 6, 8)
    b.frames(30)
    acts = start_menu_actions(b)
    t.check("the START menu has no DEXNAV before Lafayette", want not in acts, acts)

    # ---------------------------------------------------------------- Lafayette gives it
    t.check("walked up to Lafayette", fixc.talk(b, "CrescentCity_Conservation", "CrescentCity_Conservation_EventScript_Lafayette0"))
    ended = b.advance_text(60)
    b.shot("lafayette_gift")
    t.check("Lafayette's briefing (story 13) ended and gave the DexNav (FLAG_DEXNAV_OBTAINED), story 14",
            ended and b.flag("FLAG_DEXNAV_OBTAINED") and b.var("VAR_ORLEANS_STORY") == 14,
            "ended %s flag %s story %d" % (ended, b.flag("FLAG_DEXNAV_OBTAINED"), b.var("VAR_ORLEANS_STORY")))
    b.frames(30)
    acts = start_menu_actions(b)
    t.check("the START menu now has DEXNAV, and the menu still fits (<= 9 entries)", want in acts and len(acts) <= 9, acts)

    # ---------------------------------------------------------------- the search on Route 2 (day table)
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.set_flag("FLAG_DEXNAV_OBTAINED")
    b.warp("Route2", 12, 12)
    b.frames(40)
    b.set_clock(12, 0)
    speed.set_opts(b, ow=3)
    t.check("at 4x with no search the overworld speedup is on", speed.extra_loops(b) == 3, speed.extra_loops(b))
    register(b, "SPECIES_ZIGZAGOON")
    t.check("R with Zigzagoon registered starts a search", start_search(b))
    b.shot("search_route2")
    t.check("while searching the overworld speedup is forced to 1x", speed.extra_loops(b) == 0, speed.extra_loops(b))
    t.check("an encounter appears: creeping onto the target tile starts a battle", creep_onto_target(b))
    sp = enemy_species(b) if b.in_battle() else -1
    t.check("it is the registered species (Zigzagoon)", sp == enum_value("species.h", "SPECIES_ZIGZAGOON"), sp)
    b.shot("dexnav_battle")
    leave_battle(b)
    t.check("after the battle the search is over and 4x is back", not b.flag("FLAG_DEXNAV_SEARCHING") and speed.extra_loops(b) == 3,
            (b.flag("FLAG_DEXNAV_SEARCHING"), speed.extra_loops(b)))

    # ---------------------------------------------------------------- the clock: night and day tables
    b.warp("Route2", 12, 12)
    b.frames(40)
    b.set_clock(23, 0)
    b.frames(30)
    t.check("23:00 is night", b.time_of_day() == 3, b.time_of_day())
    register(b, "SPECIES_ZUBAT")
    night_ok = start_search(b)
    t.check("the night table: Zubat (night only) can be searched at night", night_ok)
    if night_ok:
        ok = creep_onto_target(b)
        t.check("and its encounter appears", ok and enemy_species(b) == enum_value("species.h", "SPECIES_ZUBAT"), enemy_species(b) if ok else "no battle")
        leave_battle(b)
    b.warp("Route2", 12, 12)
    b.frames(40)
    b.set_clock(12, 0)
    b.frames(30)
    register(b, "SPECIES_ZUBAT")
    day = start_search(b)
    if day:
        ok = creep_onto_target(b)
        day = ok and enemy_species(b) == enum_value("species.h", "SPECIES_ZUBAT")
        if ok:
            leave_battle(b)
    t.check("by day Zubat is not in Route 2's table: no Zubat encounter", not day)
    b.set_var("VAR_DEXNAV_SPECIES", 0)

    # ---------------------------------------------------------------- save and continue; old save
    if not oldsave.FIXTURE.exists():
        t.note("old_build.sav fixture missing: save/continue and old-save checks skipped")
        return
    old = Bot(rom=b.rom, out_dir=b.out / "oldsave", save=oldsave.FIXTURE)
    try:
        oldsave.continue_game(old)
        t.check("an old save loads with the DexNav off (flag, species, level, step vars all 0)",
                not old.flag("FLAG_DEXNAV_OBTAINED") and old.var("VAR_DEXNAV_SPECIES") == 0 and old.var("VAR_DEXNAV_SEARCH_LEVEL") == 0
                and old.var("VAR_DEXNAV_STEP_COUNTER") == 0 and not old.flag("FLAG_DEXNAV_SEARCHING"))
        d0 = old.clock()
        t.check("and its fake-RTC clock is intact (day 0, 08:xx)", d0[0] == 0 and d0[1] == 8, d0)
        old.set_flag("FLAG_DEXNAV_OBTAINED")
        old.set_var("VAR_DEXNAV_SPECIES", enum_value("species.h", "SPECIES_PIKACHU"))
        old.set_var("VAR_DEXNAV_SEARCH_LEVEL", 7)
        old.set_clock(15, 30, day=2)
        save_game(old)
        out = b.out / "oldsave" / "dexnav.sav"
        old.h.cmd("dumpsave " + oldsave._wsl(out))
    finally:
        old.close()
    again = Bot(rom=b.rom, out_dir=b.out / "oldsave2", save=out)
    try:
        oldsave.continue_game(again)
        again.shot("continued")
        t.check("saved and continued: the DexNav flag, the registered species and the search level survived",
                again.flag("FLAG_DEXNAV_OBTAINED") and again.var("VAR_DEXNAV_SPECIES") == enum_value("species.h", "SPECIES_PIKACHU")
                and again.var("VAR_DEXNAV_SEARCH_LEVEL") == 7,
                (again.flag("FLAG_DEXNAV_OBTAINED"), again.var("VAR_DEXNAV_SPECIES"), again.var("VAR_DEXNAV_SEARCH_LEVEL")))
        d = again.clock()
        t.check("and the fake-RTC clock (SaveBlock3 tail) still reads day 2, 15:30", (d[0], d[1]) == (2, 15) and 25 <= d[2] <= 45, d)
        acts = start_menu_actions(again)
        t.check("the START menu of the continued save has DEXNAV", want in acts, acts)
    finally:
        again.close()
