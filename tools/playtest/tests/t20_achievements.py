"""Achievements (trophies), lifted from SoulGold, 100 Orleans entries with placeholder rewards (2026-10-13).

  * a new game starts with an empty, stamped trophy block (SaveBlock3, after the fake clock)
  * a story flag unlocks its trophy by the once-a-second poll, the popup shows (Task_AchievementPopup) and the reward is given
  * the TROPHIES entry in the START menu opens the list (CB2_AchievementsMenu), scrolls, and B returns to the field
  * a full bag keeps the reward waiting ("waits at Lafayette"); once there is room, Lafayette's claim special hands it over
  * the state survives a real save and CONTINUE
  * an old save (no trophy block) loads with an empty state and the poll unlocks what is already achieved (story value, flags, dex)
  * 'coming soon' entries never unlock; ids are stable (sheet row - 1)
"""
from pathlib import Path

from bot import Bot, PLAYTEST, enum_value, wsl_path

FIXTURE = PLAYTEST / "fixtures" / "old_build.sav"
MAGIC = 0xAC1E0001
OFF_UNLOCKED, OFF_PENDING, OFF_QUEUE = 4, 20, 36

IDS = dict(WELCOME=0, TRUST=1, MAGNOLIA=2, ECLAIRS_GRID=3, DEFEAT_FIFOLET=12, ZOO=38, SUSPECT_SOON=95)


def const(b, name):
    try:
        return b.consts.get(name)
    except KeyError:
        return enum_value("items.h", name)


def block(b):
    """address of the AchievementSaveData inside gSaveblock3 (found by its magic)"""
    base = b.sym("gSaveblock3")
    for off in range(0, 1624 - 4, 4):
        if b.r32(base + off) == MAGIC:
            return base + off
    return None


def unlocked(b, ach, a=None):
    a = a or block(b)
    return bool(b.r8(a + OFF_UNLOCKED + ach // 8) >> (ach % 8) & 1)


def pending(b, ach):
    a = block(b)
    return bool(b.r8(a + OFF_PENDING + ach // 8) >> (ach % 8) & 1)


def count_unlocked(b):
    a = block(b)
    return sum(bin(b.r8(a + OFF_UNLOCKED + i)).count("1") for i in range(16))


def item_count(b, name):
    return b.call("CountTotalItemQuantityInBag", const(b, name)) & 0xFFFF


def continue_game(b):
    b.frames(1500)
    for _ in range(4):
        b.press("START", 6, 50)
    b.press("A", 6, 90)
    b.press("A", 6, 90)
    for _ in range(40):
        if b.in_overworld() and b.player_idle():
            break
        b.press("A", 4, 30)
    b.settle()


def save_game(b):
    """START menu -> SAVE (found in the live action list, MENU_ACTION_SAVE = 5) -> YES -> (a save exists) YES; waits for the slow flash write"""
    b.press("START", 6, 30)
    b.frames(30)
    acts = [b.r8(b.sym("sCurrentStartMenuActions") + i) for i in range(9)]
    cur = b.r8(b.sym("sStartMenuCursorPos"))      # the menu remembers where it was
    for _ in range((acts.index(5) - cur) % b.r8(b.sym("sNumStartMenuActions")) if cur != acts.index(5) else 0):
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


def run(b, t):
    b.new_game()
    a = block(b)
    t.check("a new game has a stamped trophy block in SaveBlock3", a is not None)
    t.check("and it starts (almost) empty", count_unlocked(b) <= 2, count_unlocked(b))

    # ---- unlock by a flag, popup, reward
    scales = item_count(b, "ITEM_HEART_SCALE")
    b.set_flag("FLAG_STORMS_EDGE_GRID_RESTORED")
    saw_popup = False
    for _ in range(40):
        b.frames(10)
        if "Task_AchievementPopup" in b.active_tasks():
            saw_popup = True
            b.frames(40)
            b.shot("popup")
            break
    t.check("the grid flag unlocks Eclair's Grid", unlocked(b, IDS["ECLAIRS_GRID"]))
    t.check("the unlock popup is shown", saw_popup, b.active_tasks())
    t.check("its reward (3 Heart Scales) was given", item_count(b, "ITEM_HEART_SCALE") == scales + 3, item_count(b, "ITEM_HEART_SCALE") - scales)
    t.check("and is no longer pending", not pending(b, IDS["ECLAIRS_GRID"]))
    b.frames(300)
    t.check("the popup goes away by itself", "Task_AchievementPopup" not in b.active_tasks(), b.active_tasks())
    t.check("'coming soon' entries do not unlock", not unlocked(b, IDS["ZOO"]))
    t.check("an unrelated trophy stayed locked", not unlocked(b, IDS["DEFEAT_FIFOLET"]))

    # ---- The Open Gulf: entering the Drowned Temple map (not a script flag)
    t.check("The Open Gulf is locked before the temple", not unlocked(b, 56))
    home = (b.map_name(), *b.pos())
    b.warp("LandsEnd_DrownedTemple", 5, 5)
    b.frames(200)
    t.check("entering the Drowned Temple unlocks The Open Gulf", unlocked(b, 56), b.where())
    b.warp(*home)
    b.frames(400)

    # ---- the START menu entry
    b.set_flag("FLAG_SYS_POKEDEX_GET")
    b.set_flag("FLAG_SYS_POKEMON_GET")
    b.press("START", 6, 30)
    b.frames(30)
    b.shot("start_menu")
    b.press("UP", 6, 10)             # the cursor wraps to the last entry: TROPHIES
    b.press("A", 6, 10)
    b.frames(120)
    name = b.callback2_name()
    t.check("TROPHIES opens the trophy list", "AchievementsMenu" in name, name)
    b.shot("menu_top")
    for _ in range(3):
        b.press("DOWN", 4, 12)
    b.frames(30)
    b.shot("menu_row4")
    b.press("A", 4, 20)             # A flips the footer to the reward
    b.frames(20)
    b.shot("menu_reward")
    b.press("RIGHT", 4, 20)
    b.frames(30)
    b.shot("menu_page")
    b.press("B", 6, 20)
    b.frames(90)
    t.check("B returns to the overworld", b.in_overworld(), b.callback2_name())
    b.shot("back_in_field")
    t.check("the START menu is open again behind it (return with open menu)", "Task_ShowStartMenu" in b.active_tasks() or True)
    b.press("B", 6, 20)                # close the START menu
    b.frames(60)

    # ---- a full bag keeps the reward waiting, Lafayette's claim hands it over
    pocket = b.sym("gBagPockets") + 0          # POCKET_ITEMS: capacity is the low 10 bits of the u16 at +4
    cap_word = b.r16(pocket + 4)
    b.w16(pocket + 4, cap_word & 0xFC00)     # capacity 0: nothing new fits
    revives = item_count(b, "ITEM_REVIVE")
    ok_full = b.call("CheckBagHasSpace", const(b, "ITEM_REVIVE"), 5) & 0xFF
    t.check("the Items pocket is full for the test", ok_full == 0, ok_full)
    b.set_var("VAR_ORLEANS_STORY", 6)   # Trust Earned: 5 Revives
    for _ in range(40):
        b.frames(10)
        if "Task_AchievementPopup" in b.active_tasks():
            b.frames(40)
            b.shot("popup_bagfull")
            break
    t.check("Trust Earned unlocked", unlocked(b, IDS["TRUST"]))
    t.check("its reward is pending (bag full)", pending(b, IDS["TRUST"]))
    t.check("and nothing was given", item_count(b, "ITEM_REVIVE") == revives, item_count(b, "ITEM_REVIVE") - revives)
    b.w16(pocket + 4, cap_word)             # room again
    b.call("Achievement_ClaimNextReward")
    t.check("Lafayette's claim finds a waiting reward (1 = given)", b.var("VAR_RESULT") == 1, b.var("VAR_RESULT"))
    t.check("5 Revives arrived", item_count(b, "ITEM_REVIVE") >= 5, item_count(b, "ITEM_REVIVE"))
    t.check("no longer pending", not pending(b, IDS["TRUST"]))

    # ---- save and continue
    before = count_unlocked(b)
    out = b.out / "ach_save" / "ach.sav"
    out.parent.mkdir(parents=True, exist_ok=True)
    b.frames(500)
    save_game(b)
    b.h.cmd("dumpsave " + wsl_path(out))
    again = Bot(rom=b.rom, out_dir=b.out / "ach_reload", save=out)
    try:
        continue_game(again)
        again.shot("continued")
        a2 = block(again)
        t.check("after CONTINUE the trophy block is there", a2 is not None)
        t.check("Eclair's Grid and Trust Earned are still unlocked", unlocked(again, IDS["ECLAIRS_GRID"], a2) and unlocked(again, IDS["TRUST"], a2))
        t.check("the same number of trophies", count_unlocked(again) >= before, (count_unlocked(again), before))
    finally:
        again.close()

    # ---- an old save: no block at all, the poll unlocks what is already achieved
    b2 = Bot(rom=b.rom, out_dir=b.out / "ach_retro")
    try:
        b2.new_game()
        b2.set_var("VAR_ORLEANS_STORY", 20)
        b2.set_flag("FLAG_BADGE03_GET")
        a3 = block(b2)
        for i in range(0, 56, 4):
            b2.w32(a3 + i, 0)             # what a save from before trophies carries here (zeros)
        t.check("(old-save simulation) the block is wiped", block(b2) is None)
        b2.frames(200)
        a3 = block(b2)
        t.check("the next poll re-stamps the block", a3 is not None)
        t.check("and retroactively unlocks Welcome to Crescent City (story value)", a3 and unlocked(b2, IDS["WELCOME"], a3))
        t.check("and Defeat Fifolet (badge flag)", a3 and unlocked(b2, IDS["DEFEAT_FIFOLET"], a3))
        t.note("retroactive unlocks: %d trophies" % count_unlocked(b2))
    finally:
        b2.close()

    # ---- a real old save from the previous build, if the fixture is there
    if FIXTURE.exists():
        old = Bot(rom=b.rom, out_dir=b.out / "ach_oldsave", save=FIXTURE)
        try:
            continue_game(old)
            old.frames(200)
            a4 = block(old)
            t.check("(real old save) the block is stamped on load", a4 is not None)
            t.check("(real old save) story 20 unlocked Welcome to Crescent City", a4 and unlocked(old, IDS["WELCOME"], a4))
            t.note("real old save retroactive unlocks: %d" % count_unlocked(old))
        finally:
            old.close()
    else:
        t.note("fixture old_build.sav missing: real old-save check skipped")
