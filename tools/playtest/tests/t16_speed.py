"""OW SPEED (1x-4x), BATTLE SPEED (1x-3x), FAST INTRO and SLEEP CLAUSE: the Options menu rows and what they save (SaveBlock2 bits), overworld
movement taking about 1/N of the frames at N x, the 1x overrides (controls locked, the prevent flag, R held, link), a battle that finishes in far fewer
frames at 3 x with the same outcome, the in-game clock not running faster, the old-save defaults, the skipped intro slide and Sleep Clause blocking a
second sleep. Battle speed is held to 1x with SELECT (documented in GetBattleSpeedScale)."""
from bot import Bot, enum_value, map_data, PLAYTEST

import importlib.util as _ilu
from pathlib import Path as _Path
_spec = _ilu.spec_from_file_location("t13b_oldsave", _Path(__file__).with_name("t13b_oldsave.py"))
oldsave = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(oldsave)

OPT_A = 0x14           # SaveBlock2: u16 text speed 0-2, frame 3-7, sound 8, style 9, scene off 10, zoom 11, OW speed 12-13, battle speed 14-15
OPT_B = 0x16           # u16: fast intro bit 0, sleep clause bit 1
ROW = {"TEXTSPEED": 0, "BATTLESCENE": 1, "BATTLESPEED": 2, "OWSPEED": 3, "FASTINTRO": 4, "SLEEPCLAUSE": 5, "BATTLESTYLE": 6, "SOUND": 7,
       "BUTTONMODE": 8, "FRAME": 9, "CANCEL": 10}


def sb2(b):
    return b.r32(b.sym("gSaveBlock2Ptr"))


def get_opts(b):
    a, c = b.r16(sb2(b) + OPT_A), b.r16(sb2(b) + OPT_B)
    return {"text": a & 7, "ow": (a >> 12) & 3, "battle": (a >> 14) & 3, "fast": c & 1, "sleep": (c >> 1) & 1, "raw": (a, c)}


def set_opts(b, ow=None, battle=None, fast=None, sleep=None):
    a, c = b.r16(sb2(b) + OPT_A), b.r16(sb2(b) + OPT_B)
    if ow is not None:
        a = (a & ~(3 << 12)) | (ow << 12)
    if battle is not None:
        a = (a & ~(3 << 14)) | (battle << 14)
    if fast is not None:
        c = (c & ~1) | fast
    if sleep is not None:
        c = (c & ~2) | (sleep << 1)
    b.w16(sb2(b) + OPT_A, a)
    b.w16(sb2(b) + OPT_B, c)


def open_options(b):
    b.w32(b.sym("gMain") + 8, b.syms.call_addr("CB2_ReturnToField"))      # savedCallback
    b.call("SetMainCallback2", b.syms.call_addr("CB2_InitOptionMenu"))
    b.frames(90)


def tap(b, key, n=1):
    for _ in range(n):
        b.press(key, 4, 8)
        b.frames(4)


def extra_loops(b):
    return b.call("OverworldSpeedup_AdditionalIterations") & 0xFF


def straight_runs(name, n):
    """left ends of horizontal runs of n free cells (no objects or warps on them), nearest to the middle of the map first"""
    d = map_data(name)
    busy = {(o["x"], o["y"]) for o in d["objects"]} | {(o["x"], o["y"]) for o in d["warps"]}
    out = []
    for y in range(2, d["height"] - 2):
        for x in range(2, d["width"] - n - 2):
            if all(d["coll"][y][x + i] == 0 and (x + i, y) not in busy for i in range(n)):
                out.append((abs(x - d["width"] // 2) + abs(y - d["height"] // 2), x, y))
    out.sort()
    return [(x, y) for _, x, y in out]


def working_run(b, name, n):
    """the first run the player really can walk along (a few tiles in 90 frames at 1x)"""
    set_opts(b, ow=0)
    for x, y in straight_runs(name, n)[:40]:
        b.warp(name, x, y)
        b.frames(20)
        b.face("R")
        b.frames(6)
        b.hold("RIGHT")
        b.frames(90)
        for _ in range(12):               # the whole 10 tiles must be walkable (water cells have collision 0 too, but only Surf crosses them)
            if b.pos()[0] - x >= 10:
                break
            b.frames(20)
        b.release()
        moved = b.pos()[0] - x
        if moved < 10:
            continue
        for _ in range(40):
            if b.player_idle():
                break
            b.frames(1)
        if moved >= 4 and b.map_name() == name and b.script_status() == 2 and not b.call("ArePlayerFieldControlsLocked") & 0xFF:
            return x, y
    return None


def walk_frames(b, x0, y0, tiles, keys="RIGHT", prevent=False):
    """warp to (x0, y0), face right, hold RIGHT until `tiles` tiles are walked; frames used (best of 3 tries: a try can stall on the turn)"""
    best = 600
    for _ in range(3):
        b.warp(b.map_name(), x0, y0)
        b.frames(20)
        if prevent:
            b.set_flag("FLAG_PREVENT_OVERWORLD_SPEEDUP")      # after the warp: a map load clears it
        b.face("R")
        b.frames(10)
        n = 0
        b.hold(keys)
        while b.pos()[0] < x0 + tiles and n < 600:
            b.frames(1)
            n += 1
        b.release()
        for _ in range(60):
            if b.player_idle():
                break
            b.frames(1)
        best = min(best, n)
        if best < 600:
            break
    if prevent:
        b.set_flag("FLAG_PREVENT_OVERWORLD_SPEEDUP", False)
    return best


def start_wild(b, species, level):
    b.call("CreateScriptedWildMon", enum_value("species.h", species), level, 0)
    b.call("BattleSetup_StartScriptedWildBattle")
    for _ in range(400):                        # the transition runs first
        if b.in_battle():
            break
        b.frames(1)


def menu_reached(b):
    return (b.r32(b.sym("gBattleMainFunc")) & ~1) == (b.syms.call_addr("HandleTurnActionSelectionState") & ~1)


STUCK = []


def mash(b, until, cap):
    """tap A (2 frames down, 2 up) until until() is true; frames used"""
    n = 0
    while n < cap and not until():
        b.hold("A") if (n // 2) % 2 == 0 else b.release()
        b.frames(1)
        n += 1
    b.release()
    return n


def battle_frames(b, clock=False, species="SPECIES_MAGIKARP", level=2, to_menu=False):
    """a wild battle that Mew wins with its first move. Stage 1: tap A through the intro to the move menu; stage 2: FIGHT, Psychic, tap A to the
    end of the battle. Returns (frames, outcome, Mew HP, clock seconds spent); with to_menu only stage 1 runs"""
    start_wild(b, species, level)
    c0 = b.clock_seconds() if clock else 0
    n = mash(b, lambda: menu_reached(b) or not b.in_battle(), 3000)
    if not to_menu and b.in_battle():
        b.frames(20)
        tap(b, "A")                             # FIGHT
        b.frames(20)
        tap(b, "A")                             # the first move
        n += 44
        n += mash(b, lambda: not b.in_battle(), 3000)
    if n >= 3000:
        b.shot("battle_stuck")
        inv = {v | 1: k for k, v in b.syms.addr.items()}
        STUCK.append("stuck: gBattleMainFunc %s, callback2 %s, held opts %s" % (inv.get(b.r32(b.sym("gBattleMainFunc"))), b.callback2_name(), get_opts(b)))
    out = b.r8(b.sym("gBattleOutcome"))
    mon = b.r32(b.sym("gPlayerPartyPtr"))
    hp = b.r16(mon + 0x56)
    return n, out, hp, (b.clock_seconds() - c0) if clock else 0


def prep_party(b):
    """Mew (level 8: a higher level would disobey without badges) leads the party: slot 1 is copied over slot 0"""
    b.give_mon("SPECIES_MEW", 8)
    for slot in range(4):                       # Tackle alone: whatever slot a mashed A lands on is Tackle
        b.set_move(slot, "MOVE_TACKLE" if slot == 0 else "MOVE_NONE", b.party_count() - 1)
    base = b.r32(b.sym("gPlayerPartyPtr"))
    src = base + (b.party_count() - 1) * 100
    for i in range(0, 100, 4):
        b.w32(base + i, b.r32(src + i))
    b.call("HealPlayerParty")


def run(b, t):
    # ---------------------------------------------------------------- defaults and the Options menu rows
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 30)          # no early story triggers on the walking routes
    o = get_opts(b)
    t.check("a new game starts with OW SPEED 1x, BATTLE SPEED 1x, FAST INTRO off, SLEEP CLAUSE off (text speed untouched: MID)",
            o["ow"] == 0 and o["battle"] == 0 and o["fast"] == 0 and o["sleep"] == 0 and o["text"] == 1, o)
    b.warp("Route3", 20, 30)
    b.frames(30)
    open_options(b)
    b.shot("options_top")
    t.check("the Options menu opened (callback2 is not the field)", not b.in_overworld(), b.callback2_name())
    tap(b, "DOWN", ROW["BATTLESPEED"])
    tap(b, "RIGHT", 2)                          # 1x -> 2x -> 3x
    b.shot("options_battle_speed_3x")
    tap(b, "DOWN")                              # OW SPEED
    tap(b, "RIGHT", 3)                          # 4x
    tap(b, "DOWN")                              # FAST INTRO
    tap(b, "RIGHT")
    tap(b, "DOWN")                              # SLEEP CLAUSE
    tap(b, "RIGHT")
    b.shot("options_all_set")                   # the list has scrolled: TEXT SPEED and BATTLE SCENE are above the view
    tap(b, "DOWN", 5)                           # BATTLE STYLE ... FRAME, CANCEL
    b.shot("options_bottom")
    tap(b, "UP", 5)
    tap(b, "UP")                                # SLEEP CLAUSE again: prove the list scrolls both ways and keeps values
    tap(b, "LEFT")                              # sleep clause back off
    tap(b, "RIGHT")                             # and on again
    b.press("B", 4, 8)
    b.frames(120)
    o = get_opts(b)
    t.check("the rows saved: BATTLE SPEED 3x, OW SPEED 4x, FAST INTRO on, SLEEP CLAUSE on", (o["battle"], o["ow"], o["fast"], o["sleep"]) == (2, 3, 1, 1), o)
    t.check("the other option bits are untouched (text speed MID)", o["text"] == 1, o)
    t.check("the menu returned to the field", b.in_overworld(), b.callback2_name())
    b.call("UnlockPlayerFieldControls")         # the bot opens the menu directly, not through the START menu that unlocks on return
    # wrap-around: BATTLE SPEED 1x with LEFT goes to 3x, OW SPEED 4x with RIGHT goes to 1x
    open_options(b)
    tap(b, "DOWN", ROW["BATTLESPEED"])
    tap(b, "LEFT")
    tap(b, "RIGHT")
    tap(b, "DOWN")
    tap(b, "RIGHT")
    b.press("B", 4, 8)
    b.frames(120)
    o = get_opts(b)
    t.check("RIGHT past 4x wraps OW SPEED to 1x; LEFT then RIGHT leaves BATTLE SPEED at 3x", (o["battle"], o["ow"]) == (2, 0), o)
    b.call("UnlockPlayerFieldControls")

    # ---------------------------------------------------------------- overworld: frames per tile, the 1x overrides
    run_at = working_run(b, "Route3", 14)
    t.check("found a free straight run to walk", run_at is not None, run_at)
    frames_at = {}
    if run_at:
        x0, y0 = run_at
        mapname = b.map_name()
        for n in (1, 2, 3, 4):
            set_opts(b, ow=n - 1)
            frames_at[n] = walk_frames(b, x0, y0, 10)
        t.note("frames for 10 tiles at 1x/2x/3x/4x: %s" % frames_at)
        base = frames_at[1]
        t.check("1x walks 10 tiles in 60-260 frames (the player runs: about 8 per tile)", 60 <= base <= 260, frames_at)
        for n in (2, 3, 4):
            ratio = frames_at[n] * n / base
            t.check("%dx walks 10 tiles in about 1/%d of the 1x frames" % (n, n), 0.7 <= ratio <= 1.45, "%d frames, ratio x N = %.2f" % (frames_at[n], ratio))
        # R held: 1x again at 4x
        set_opts(b, ow=3)
        held = walk_frames(b, x0, y0, 10, keys="RIGHT+R")
        t.check("holding R at OW SPEED 4x is clearly slower than the 4x walk (the function check above shows 0 extra iterations)", held > 2 * frames_at[4], "%d vs 4x %d, 1x %d" % (held, frames_at[4], base))
        # the prevent flag
        prevented = walk_frames(b, x0, y0, 10, prevent=True)
        t.check("FLAG_PREVENT_OVERWORLD_SPEEDUP forces 1x at OW SPEED 4x", abs(prevented - base) <= 0.2 * base, "%d vs %d" % (prevented, base))

    set_opts(b, ow=3)
    b.frames(5)
    t.check("free roaming at 4x: 3 extra iterations", extra_loops(b) == 3, extra_loops(b))
    set_opts(b, ow=1)
    t.check("2x: 1 extra iteration", extra_loops(b) == 1, extra_loops(b))
    set_opts(b, ow=0)
    t.check("1x: no extra iteration", extra_loops(b) == 0, extra_loops(b))
    set_opts(b, ow=3)
    b.call("LockPlayerFieldControls")
    t.check("controls locked (scripts, text, menus): 1x", extra_loops(b) == 0, extra_loops(b))
    b.call("UnlockPlayerFieldControls")
    t.check("controls unlocked again: 4x", extra_loops(b) == 3, extra_loops(b))
    b.set_flag("FLAG_PREVENT_OVERWORLD_SPEEDUP")
    t.check("prevent flag set: 1x", extra_loops(b) == 0, extra_loops(b))
    b.warp("Route3", 20, 30)
    b.frames(30)
    t.check("a map load clears the prevent flag", not b.flag("FLAG_PREVENT_OVERWORLD_SPEEDUP") and extra_loops(b) == 3,
            (b.flag("FLAG_PREVENT_OVERWORLD_SPEEDUP"), extra_loops(b)))
    link = b.sym("gReceivedRemoteLinkPlayers")
    b.w8(link, 1)
    t.check("link active: 1x", extra_loops(b) == 0, extra_loops(b))
    b.w8(link, 0)
    b.hold("R")
    b.frames(2)
    t.check("R held: 1x", extra_loops(b) == 0, extra_loops(b))
    b.release()
    b.frames(2)
    # the scripted cinematics that set the flag: the Rayquaza arrival and the storm
    import re
    from bot import ROOT
    for f, label in (("tools/mapgen/story/OldestShrine.inc", "OldestShrine_EventScript_Arrival"),
                     ("tools/mapgen/story/LandsEnd.inc", "LandsEnd_EventScript_RayquazaWakes")):
        txt = (ROOT / f).read_text(encoding="utf-8")
        body = txt[txt.index(label + ":"):][:700]
        t.check("%s sets FLAG_PREVENT_OVERWORLD_SPEEDUP" % label, "FLAG_PREVENT_OVERWORLD_SPEEDUP" in body)

    # ---------------------------------------------------------------- the clock does not run faster with the speed loops
    set_opts(b, ow=3, battle=2)
    b.warp("Route3", 20, 30)
    b.frames(30)
    b.set_clock(12, 0)
    c0 = b.clock_seconds()
    if run_at:
        for _ in range(8):                      # ~20 s of real walking at 4x
            walk_frames(b, x0, y0, 10)
            b.frames(30)
    else:
        b.frames(60 * 20)
    c1 = b.clock_seconds()
    # the loop above took N frames: measure them with the frame counter instead of guessing
    f_before = b.frame_counter()
    c2 = b.clock_seconds()
    b.hold("RIGHT")
    b.frames(60 * 10)
    b.release()
    c3 = b.clock_seconds()
    f_after = b.frame_counter()
    secs = (f_after - f_before) / 60.0
    t.check("10 s of walking at OW SPEED 4x = about 200 game seconds (20 per second of play)", abs((c3 - c2) - secs * 20) <= 40 + secs * 2,
            "%d game s in %.1f s of play" % (c3 - c2, secs))

    # ---------------------------------------------------------------- battle speed
    prep_party(b)
    b.warp("Route3", 20, 30)
    b.frames(30)
    clock_ok = []
    res = {}
    for spd in (0, 2):
        set_opts(b, ow=0, battle=spd, fast=0)
        b.set_clock(12, 0)
        start_frames = b.frame_counter()
        n, out, hp, dc = battle_frames(b, clock=True)
        real = (b.frame_counter() - start_frames) / 60.0
        res[spd] = (n, out, hp, dc, real)
        b.frames(60)
        b.call("HealPlayerParty")
        b.warp("Route3", 20, 30)
        b.frames(30)
    for x in STUCK:
        t.note(x)
    t.note("battle (frames, outcome, mew hp, clock s, real s): 1x %s, 3x %s" % (res[0], res[2]))
    t.check("both battles ended in a win (outcome 1)", res[0][1] == 1 and res[2][1] == 1, (res[0][1], res[2][1]))
    t.check("same outcome: Mew unhurt at 1x and 3x", res[0][2] == res[2][2], (res[0][2], res[2][2]))
    t.check("3x finishes the battle in fewer frames (< 80% of 1x)", res[2][0] < 0.8 * res[0][0], "%d vs %d frames" % (res[2][0], res[0][0]))
    for spd, name in ((0, "1x"), (2, "3x")):
        n, out, hp, dc, real = res[spd]
        t.check("battle at %s: the clock advanced 20 game seconds per second of play" % name, abs(dc - real * 20) <= 60 + real * 3,
                "%d game s in %.1f s" % (dc, real))

    # scale: 1 at the move menu and with SELECT held, 3 during the intro; link battles stay 1x
    set_opts(b, battle=2)
    start_wild(b, "SPECIES_MAGIKARP", 2)
    b.frames(20)
    t.check("3x during the battle intro: scale 3", b.call("GetBattleSpeedScale") == 3, b.call("GetBattleSpeedScale"))
    b.hold("SELECT")
    b.frames(2)
    t.check("SELECT held: scale 1", b.call("GetBattleSpeedScale") == 1, b.call("GetBattleSpeedScale"))
    b.release()
    b.frames(2)
    mash(b, lambda: menu_reached(b), 3000)
    t.check("the move menu is reached", menu_reached(b))
    b.frames(10)
    t.check("choosing a move: scale 1 even at 3x", b.call("GetBattleSpeedScale") == 1, b.call("GetBattleSpeedScale"))
    b.shot("battle_menu_3x")
    flags = b.sym("gBattleTypeFlags")            # last: a frame runs inside call(), so the fake LINK bit wrecks this battle
    f = b.r32(flags)
    b.w32(flags, f | 2)                         # BATTLE_TYPE_LINK
    t.check("link battle: scale 1", b.call("GetBattleSpeedScale") == 1, b.call("GetBattleSpeedScale"))
    b.w32(flags, f)
    b.fight()
    b.frames(60)
    b.warp("Route3", 20, 30)
    b.frames(60)

    # ---------------------------------------------------------------- FAST INTRO: the slide is skipped
    prep_party(b)
    b.warp("Route3", 20, 30)
    b.frames(30)
    intro = {}
    for fast in (0, 1):
        set_opts(b, battle=0, fast=fast)
        n, _, _, _, = battle_frames(b, to_menu=True)[:4]
        intro[fast] = n
        b.fight()
        b.frames(60)
        b.call("HealPlayerParty")
        b.warp("Route3", 20, 30)
        b.frames(30)
    t.note("frames to the move menu: slide %s, skipped %s" % (intro[0], intro[1]))
    t.check("FAST INTRO on reaches the move menu sooner than the sliding intro", intro[1] < intro[0] - 10, intro)

    # ---------------------------------------------------------------- SLEEP CLAUSE
    sleepers = {}
    t.check("IsSleepClauseEnabled follows the option",
            (set_opts(b, sleep=0), b.call("IsSleepClauseEnabled") & 0xFF)[1] == 0 and (set_opts(b, sleep=1), b.call("IsSleepClauseEnabled") & 0xFF)[1] == 1)

    def one_run(sleep, aim):
        set_opts(b, sleep=sleep, battle=0, fast=1)
        if b.party_count() < 2:
            b.give_mon("SPECIES_BRELOOM", 8)
        n = double_spore(b, aim)
        b.shot("sleep_clause_%s_%s" % ("on" if sleep else "off", aim or "none"))
        b.fight()
        b.warp("Route3", 20, 30)
        b.frames(30)
        return n

    aim_used = None
    for aim in ("LEFT", "RIGHT", "UP", "DOWN", None):       # find the key that sends the second Spore to the other enemy (clause off: both sleep)
        n = one_run(0, aim)
        sleepers["off_" + str(aim)] = n
        if n == 2:
            aim_used = aim
            break
    t.note("enemies asleep after two Spores in one turn, clause off, by aim key: %s" % sleepers)
    if aim_used is not None or sleepers.get("off_None") == 2:
        n_on = one_run(1, aim_used)
        t.note("clause on, aim %s: %d asleep" % (aim_used, n_on))
        t.check("SLEEP CLAUSE off: both Spores put an enemy to sleep; on: only one does", n_on == 1, (sleepers, n_on))
    else:
        t.note("could not aim the second Spore at the other enemy")
        t.check("SLEEP CLAUSE: found a way to aim the second Spore at the other enemy", False, sleepers)

    # ---------------------------------------------------------------- old saves load at 1x / off
    if not oldsave.FIXTURE.exists():
        t.note("old_build.sav fixture missing: old-save defaults not tested")
        return
    old = Bot(rom=b.rom, out_dir=b.out / "oldsave", save=oldsave.FIXTURE)
    try:
        oldsave.continue_game(old)
        o = get_opts(old)
        old.shot("old_save_loaded")
        t.check("an old save loads with OW SPEED 1x, BATTLE SPEED 1x, FAST INTRO off, SLEEP CLAUSE off", (o["ow"], o["battle"], o["fast"], o["sleep"]) == (0, 0, 0, 0), o)
        t.check("and extra iterations 0, battle scale 1", extra_loops(old) == 0, extra_loops(old))
        old.release()
        open_options(old)
        old.shot("old_save_options")
        old.press("B", 4, 8)
        old.frames(100)
        t.check("opening and closing the menu on an old save keeps them at 1x", get_opts(old)["raw"][0] >> 12 == get_opts(old)["raw"][0] >> 12 and (get_opts(old)["ow"], get_opts(old)["battle"]) == (0, 0), get_opts(old))
    finally:
        old.close()


def double_spore(b, aim="LEFT"):
    """a double wild battle: the two lead mons both use Spore, the second aimed at the other enemy; (enemies asleep after the turn, clause active for the enemy side)"""
    b.set_move(0, "MOVE_SPORE", 0)
    b.set_move(0, "MOVE_SPORE", 1)
    b.call("HealPlayerParty")
    b.call("CreateScriptedDoubleWildMon", enum_value("species.h", "SPECIES_MAGIKARP"), 3, 0, enum_value("species.h", "SPECIES_MAGIKARP"), 3, 0)
    b.call("BattleSetup_StartScriptedDoubleWildBattle")
    for _ in range(1500):
        if menu_reached(b):
            break
        b.press("A", 3, 5)
    b.frames(30)
    tap(b, "A")                      # mon 1: FIGHT
    b.frames(20)
    tap(b, "A")                      # Spore
    b.frames(20)
    tap(b, "A")                      # the default target
    b.frames(40)
    tap(b, "A")                      # mon 2: FIGHT
    b.frames(20)
    tap(b, "A")                      # Spore
    b.frames(20)
    if aim:
        tap(b, aim)                  # the other enemy
    tap(b, "A")
    for _ in range(300):             # let the turn play until the next menu
        b.press("A", 3, 8)
        b.frames(4)
        if menu_reached(b) or not b.in_battle():
            break
    b.frames(20)
    asleep = 0
    enemy = b.r32(b.sym("gEnemyPartyPtr"))
    for i in range(2):
        if b.r32(enemy + i * 100 + 0x50) & 7:
            asleep += 1
    return asleep
