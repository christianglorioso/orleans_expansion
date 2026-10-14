"""Boss battles (src/battle_boss.c, SoulGold's system by Eemeliri; `setbossbattle` in the story scripts), 2026-10-14.

  * the finale: the Kyogre raid (a trainer battle, 3 health bars, no orb): the barrier icons on the healthbox, Kyogre, then Primal Kyogre on the first
    break (form AND moveset from BOSS_PHASE_PROFILE_KYOGRE, the HP refilled, Primordial Sea), the last stand on the second break, a win on the third
    (a trainer's Pokemon is not caught); the Groudon raid (3 bars, Primal Groudon); the Rayquaza raid (2 v 1 with Jayden, 4 bars): Rayquaza, then Mega
    Rayquaza (Dragon Ascent) from the third bar
  * the lairs: Celebi (2 bars, no form change): the bar count, the last stand, the victory catch (a real Master Ball throw), the caught Celebi; the rougarou
    (2 bars, Lycanroc Midnight -> Mega Lycanroc on the break); the Drowned Temple's Kyogre (2 bars, Primal on the break, caught as plain Kyogre with its own
    moves back), the wild intro (gender, nature) and a boss that is beaten but not caught stays standing
  * the soft reset: from one save, boots with different timing roll a different nature / gender / shiny in the boss encounter (Celebi)
  * the bars never leak into the next battle (a plain scripted wild battle after a boss has no bars, no boss flag)
Screenshots for the user: tile_review/boss_*.png.
"""
import re
import shutil
import sys
from pathlib import Path

from bot import Bot, ROOT, enum_value, map_data, wsl_path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(Path(ROOT) / "tools" / "mapgen"))
import t19_starters as S  # noqa: E402  (the soft-reset helpers: continue_game, save_game, enemy_mon, the text reader, the nature table)
import story_data_lairs as D  # noqa: E402

SHOTS = Path(ROOT).parent / "tile_review"
STRIDE, O_SPECIES, O_MOVES, O_STAGES, O_HP, O_MAXHP = 140, 0, 12, 24, 42, 46   # struct BattlePokemon (measured on this build): gBattleMons[battler]
RAIN_PRIMAL = 0x4                                                              # B_WEATHER_RAIN_PRIMAL, bit 2 of gBattleWeather
SUN_PRIMAL = 0x20


def mon_data_ids():
    txt = (Path(ROOT) / "include" / "pokemon.h").read_text(errors="replace")
    body = txt[txt.index("enum MonData"):]
    body = body[:body.index("};")]
    ids, n = {}, 0
    for line in body.splitlines()[1:]:
        m = re.match(r"\s+(MON_DATA_\w+)\s*(=\s*(\w+))?,", line)
        if m:
            if m.group(3):
                n = int(m.group(3), 0) if m.group(3).isdigit() else ids[m.group(3)]
            ids[m.group(1)] = n
            n += 1
    return ids


MD = mon_data_ids()


def SP(name):
    return enum_value("species.h", "SPECIES_" + name)


def MV(name):
    return enum_value("moves.h", "MOVE_" + name)


def bm(b, battler, off, size=2):
    a = b.sym("gBattleMons") + battler * STRIDE + off
    return b.r16(a) if size == 2 else b.r8(a)


def state(b, boss=1):
    return dict(bars=b.call("GetBossBarsRemaining") & 0xFF, total=b.call("GetBossTotalBars") & 0xFF, is_boss=bool(b.call("IsBossBattle") & 1),
                visible=b.call("CountVisibleBossHealthBarSprites") & 0xFF, species=bm(b, boss, O_SPECIES),
                moves=[bm(b, boss, O_MOVES + 2 * i) for i in range(4)], hp=bm(b, boss, O_HP), maxhp=bm(b, boss, O_MAXHP),
                weather=b.r16(b.sym("gBattleWeather")), stages=[bm(b, boss, O_STAGES + i, 1) for i in range(8)])


def turn_counter(b):
    return b.r16(b.sym("gBattleTurnCounter"))


def at_menu(b):
    return (b.r32(b.sym("gBattleMainFunc")) & ~1) == b.sym("HandleTurnActionSelectionState")


def wait_menu(b, tries=500):
    """mash A through the intro / messages until the turn menu waits; True when it does"""
    for _ in range(tries):
        b.check_alive("boss battle")
        if not b.in_battle():
            return False
        if at_menu(b):
            b.frames(40)
            if at_menu(b):
                return True
        b.press("A", 4, 26)
    return False


ORIG = {"moves": None}


def start_battle(b, tries=80):
    """presses A until a battle is on; the foe's own moves are read the moment it starts (the boss phases rewrite them a few frames later)"""
    for _ in range(tries):
        if b.in_battle():
            ORIG["moves"] = enemy_moves(b)
            return True
        b.press("A", 4, 26)
    return b.in_battle()


def heal_player(b):
    b.w16(b.sym("gBattleMons") + O_HP, bm(b, 0, O_MAXHP))


def text_now(b):
    return S.text_at(b, "gDisplayedStringBattle", 200).replace("\n", " ")


def attack(b, boss=1, kill=True, frames_log=None, target_down=False, limit=500):
    """one turn: the boss goes to 1 HP (kill) and the tester's first move (Psychic) finishes it; mashes A until the next turn menu (a turn counted) or the
    battle's end. frames_log collects (text, png) every ~15 frames while the messages play. Returns True while the battle goes on."""
    heal_player(b)
    if kill:
        b.w16(b.sym("gBattleMons") + boss * STRIDE + O_HP, 1)
    turn0 = turn_counter(b)
    b.press("A", 4, 30)          # BATTLE
    b.press("A", 4, 30)          # the first move
    if target_down:
        b.press("DOWN", 4, 20)   # the lower foe cell in a double battle
        b.press("A", 4, 30)
    for i in range(limit):
        b.check_alive("boss turn")
        if not b.in_battle():
            return False
        if at_menu(b) and turn_counter(b) != turn0:
            b.frames(40)
            if at_menu(b):
                return True
        if frames_log is not None and i % 2 == 0:
            frames_log.append((text_now(b), b.shot("seq_%02d" % len(frames_log))))
        b.press("A", 4, 26) if i % 3 == 2 else b.frames(15)
    return False


def copy_shot(png, name):
    SHOTS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, SHOTS / name)


def montage(frames, name, picks):
    """picks: substrings of the on-screen text; one frame per pick (the first match), in one picture"""
    from PIL import Image
    chosen = []
    for p in picks:
        idx = next((i for i, f in enumerate(frames) if p in f[0]), None)
        if idx is not None:
            chosen.append(frames[min(len(frames) - 1, idx + 4)][1])     # a few frames on: the message has been typed out by then
    if not chosen:
        return False
    ims = [Image.open(p).convert("RGB") for p in chosen]
    w, h = ims[0].size
    cols = 2 if len(ims) > 1 else 1
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (0, 0, 0))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    SHOTS.mkdir(parents=True, exist_ok=True)
    sheet.save(SHOTS / name)
    return True


def party_data(b, slot, md):
    return b.call("GetMonData2", S.party_mon(b, slot), MD[md]) & 0xFFFF


def party_moves(b, slot):
    return [party_data(b, slot, "MON_DATA_MOVE%d" % (i + 1)) for i in range(4)]


def enemy_data(b, md):
    return b.call("GetMonData2", S.enemy_mon(b), MD[md]) & 0xFFFF


def enemy_moves(b):
    return [enemy_data(b, "MON_DATA_MOVE%d" % (i + 1)) for i in range(4)]


def intro_text(b, tries=400):
    for _ in range(tries):
        b.frames(5)
        txt = S.text_at(b, "gDisplayedStringBattle")
        if txt.startswith("A wild"):
            return txt
    return None


def end_battle(b, tries=120):
    """finish whatever is left of a battle with the autopilot (a win is forced)"""
    for _ in range(tries):
        if not b.in_battle():
            break
        b.fight(10)
    b.frames(60)
    b.advance_text(60)


def setup(b):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    for i in range(1, 9):
        b.set_flag("FLAG_BADGE0%d_GET" % i)       # a level 100 tester only obeys with the badges


def catch_through(b, n0):
    """after the last bar broke: the victory catch's prompts and the Master Ball are all A presses; B declines the nickname"""
    for _ in range(400):
        if not b.in_battle():
            break
        b.press("A", 4, 26)
    for _ in range(80):
        if b.script_status() == 2 and not b.in_battle():
            break
        b.press("B", 4, 30)
    b.frames(60)
    b.advance_text(60)
    return b.party_count() == n0 + 1


# ------------------------------------------------------------------------------------------------------------------------------------------ the finale
def finale_kyogre(b, t):
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN", True)
    b.warp("LandsEnd_DrownedTemple", 9, 6)
    b.face("U")
    b.press("A", 4, 26)
    t.check("the Kyogre raid starts a battle", start_battle(b))
    t.check("... which reaches the turn menu", wait_menu(b))
    s = state(b)
    copy_shot(b.shot("kyogre_raid_3bars"), "boss_finale_kyogre_3bars.png")
    t.check("raid Kyogre is a boss with 3 health bars, 2 barrier icons on the healthbox", s["is_boss"] and s["total"] == 3 and s["bars"] == 3 and s["visible"] == 2, s)
    t.check("it starts as Kyogre, not Primal (no orb), with the first phase's moves",
            s["species"] == SP("KYOGRE") and s["moves"] == [MV("HYDRO_PUMP"), MV("ICE_BEAM"), MV("CALM_MIND"), MV("SURF")] and not s["weather"] & RAIN_PRIMAL,
            "%s weather %#x" % (s["moves"], s["weather"]))
    hp0 = s["maxhp"]
    # -- bar 1 breaks: Primal Reversion
    frames = []
    t.check("bar 1 breaks and the battle goes on", attack(b, 1, True, frames))
    s = state(b)
    t.check("breaking bar 1: 2 bars left (1 icon), the HP is full again, not fainted", s["bars"] == 2 and s["visible"] == 1 and s["hp"] == s["maxhp"] and s["is_boss"], s)
    t.check("the first break is a Primal Reversion: Primal Kyogre", s["species"] == SP("KYOGRE_PRIMAL"), s["species"])
    t.check("... with the second phase's moves (Origin Pulse, Ice Beam, Thunder, Water Spout)",
            s["moves"] == [MV("ORIGIN_PULSE"), MV("ICE_BEAM"), MV("THUNDER"), MV("WATER_SPOUT")], s["moves"])
    t.check("... and Primordial Sea (its ability's switch-in effect ran)", bool(s["weather"] & RAIN_PRIMAL), "%#x" % s["weather"])
    t.check("... its max HP follows the form", s["maxhp"] >= hp0, (hp0, s["maxhp"]))
    texts = [f[0] for f in frames]
    t.check("the break is announced ('barrier broke') and the Primal Reversion has its own text",
            any("barrier broke" in x for x in texts) and any("primal state" in x for x in texts), texts[:8])
    t.check("the phase change picture was taken", montage(frames, "boss_phase_change_kyogre.png", ["barrier broke", "primal state", "heavy rain"]))
    # lower a stat stage: the last stand lifts every lowered stage back to normal
    b.w16(b.sym("gBattleMons") + STRIDE + O_STAGES, 0)    # Attack and Defense stages 0 (-6)
    frames = []
    t.check("bar 2 breaks and the battle goes on", attack(b, 1, True, frames))
    s = state(b)
    t.check("breaking bar 2: the last bar (0 icons), full HP, the last stand lifts its lowered stat stages back to normal",
            s["bars"] == 1 and s["visible"] == 0 and s["hp"] == s["maxhp"] and min(s["stages"]) >= 6, s)
    t.check("... still Primal Kyogre, the third phase's moves", s["species"] == SP("KYOGRE_PRIMAL") and s["moves"] == [MV("ORIGIN_PULSE"), MV("ICE_BEAM"), MV("THUNDER"), MV("CALM_MIND")], s["moves"])
    t.check("the last stand is announced", any("last stand" in f[0] for f in frames), [f[0] for f in frames][:6])
    montage(frames, "boss_last_stand_kyogre.png", ["last stand"])
    copy_shot(b.shot("kyogre_last_stand_menu"), "boss_finale_kyogre_last_bar.png")
    # -- the last bar: a trainer-borne boss is simply beaten
    attack(b, 1, True)
    for _ in range(300):
        if not b.in_battle():
            break
        b.press("A", 4, 26)
    t.check("the third break ends the battle: a win (a trainer's Pokemon is not caught)", not b.in_battle())
    b.advance_text(60)
    b.frames(60)
    t.check("the raid script ran on: Kyogre calmed", b.flag("FLAG_KYOGRE_CALMED"), b.where())


def finale_groudon(b, t):
    b.set_flag("FLAG_KYOGRE_CALMED", False)
    b.set_flag("FLAG_GROUDON_CALMED", False)
    b.set_flag("FLAG_ROUTE25_OPEN", False)
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.warp("LandsEnd_SaltCathedral", 11, 5)
    b.face("U")
    b.press("A", 4, 26)
    t.check("the Groudon raid starts a battle", start_battle(b))
    wait_menu(b)
    s = state(b)
    t.check("raid Groudon: a boss with 3 bars, as Groudon (no Red Orb), Earthquake first", s["is_boss"] and s["total"] == 3 and s["species"] == SP("GROUDON") and MV("EARTHQUAKE") in s["moves"], s)
    copy_shot(b.shot("groudon_raid_3bars"), "boss_finale_groudon_3bars.png")
    attack(b, 1, True)
    s = state(b)
    t.check("Groudon's first break: Primal Groudon with Precipice Blades, Desolate Land (extremely harsh sunlight)",
            s["bars"] == 2 and s["species"] == SP("GROUDON_PRIMAL") and MV("PRECIPICE_BLADES") in s["moves"] and bool(s["weather"] & SUN_PRIMAL), "%s %#x" % (s, s["weather"]))
    end_battle(b)


def rayquaza_battler(b):
    for battler in (1, 3):
        if bm(b, battler, O_SPECIES) in (SP("RAYQUAZA"), SP("RAYQUAZA_MEGA")):
            return battler
    return 1


def finale_rayquaza(b, t):
    """the 2 v 1 raid: Jayden's partner, 4 bars"""
    b.set_var("VAR_ORLEANS_STORY", 42)
    b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 2)
    b.set_flag("FLAG_HIDE_SHRINE_RAYQUAZA", False)
    b.set_flag("FLAG_HIDE_SHRINE_JAYDEN", False)
    b.warp("OldestShrine", 16, 10)
    b.face("U")
    b.press("A", 4, 26)
    t.check("the Rayquaza raid starts a battle", start_battle(b, 200))
    t.check("... which reaches the turn menu (a double battle with Jayden)", wait_menu(b, 700))
    rq = rayquaza_battler(b)
    s = state(b, rq)
    copy_shot(b.shot("rayquaza_raid_4bars"), "boss_finale_rayquaza_4bars.png")
    t.check("Rayquaza raid (2 v 1): a boss with 4 bars, 3 icons", s["is_boss"] and s["total"] == 4 and s["bars"] == 4 and s["visible"] == 3, s)
    t.check("... as plain Rayquaza (no Dragon Ascent yet, so no Mega Evolution)", s["species"] == SP("RAYQUAZA") and MV("DRAGON_ASCENT") not in s["moves"], s["moves"])
    down = rq == 3
    t.check("bar 1 breaks", attack(b, rq, True, None, target_down=down))
    s = state(b, rq)
    t.check("... 3 bars left, full HP, still Rayquaza", s["bars"] == 3 and s["hp"] == s["maxhp"] and s["species"] == SP("RAYQUAZA"), s)
    t.check("bar 2 breaks", attack(b, rq, True, None, target_down=down))
    s = state(b, rq)
    # the partner can land a second hit in the same turn: the Mega phase is reached either way
    t.check("... bars <= 2: Mega Rayquaza with Dragon Ascent (Delta Stream)", s["bars"] <= 2 and s["species"] == SP("RAYQUAZA_MEGA") and MV("DRAGON_ASCENT") in s["moves"], "%s" % s)
    copy_shot(b.shot("rayquaza_mega_menu"), "boss_finale_rayquaza_mega.png")
    end_battle(b)


# ------------------------------------------------------------------------------------------------------------------------------------------ the lairs
def stand_at(b, key):
    (sx, sy), face = D.STAND[key]
    b.warp(D.LAIRS[key]["map"], sx, sy)
    b.face(face)
    b.frames(20)


def describe(b, species):
    return S.describe(b, S.enemy_mon(b), species)


def lair_celebi(b, t):
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_CELEBI", False)
    b.give_item("ITEM_MASTER_BALL", 3)
    b.set_clock(12)
    b.frames(30)
    stand_at(b, "celebi")
    n0 = b.party_count()
    b.press("A", 4, 26)
    t.check("Celebi's lair: a battle starts", start_battle(b))
    txt = intro_text(b)
    nat, gen, shiny = describe(b, SP("CELEBI"))
    m = S.WILD.search(txt or "")
    t.check("the wild intro still names the gender and nature (%s %s): %r" % (gen, nat, txt), m is not None and (m.group(1) or "") == gen and m.group(2) == nat, (txt, nat, gen))
    wait_menu(b)
    orig_moves = ORIG["moves"]
    s = state(b)
    copy_shot(b.shot("celebi_2bars"), "boss_lair_celebi_2bars.png")
    t.check("Celebi is a boss with 2 bars (1 icon), no form change, its own moves", s["is_boss"] and s["total"] == 2 and s["bars"] == 2 and s["visible"] == 1
            and s["species"] == SP("CELEBI") and s["moves"] == orig_moves, s)
    atk_plain = party_stat(b)
    t.check("the 110%% stat multiplier is on (Attack in battle %d vs the plain stat %d)" % (bm(b, 1, 2), atk_plain), bm(b, 1, 2) > atk_plain, (bm(b, 1, 2), atk_plain))
    ok = attack(b, 1, True)
    s = state(b)
    t.check("bar 1 breaks: 1 bar left (the last stand), full HP, still Celebi, same moves", ok and s["bars"] == 1 and s["hp"] == s["maxhp"] and s["species"] == SP("CELEBI")
            and s["moves"] == orig_moves and s["visible"] == 0, s)
    # the last break offers the catch (guaranteed): the A-mash says Yes, opens the bag on the balls and throws the Master Ball
    attack(b, 1, True, limit=700)
    caught = catch_through(b, n0)
    t.check("breaking the last bar offers the victory catch; the Master Ball catches it (party %d -> %d)" % (n0, b.party_count()), caught)
    last = b.party_count() - 1
    t.check("the caught Pokemon is Celebi with its own moves", party_data(b, last, "MON_DATA_SPECIES") == SP("CELEBI") and party_moves(b, last) == orig_moves,
            (party_data(b, last, "MON_DATA_SPECIES"), party_moves(b, last), orig_moves))
    t.check("a catch retires the encounter (FLAG_PG_CELEBI set)", b.flag("FLAG_PG_CELEBI"))


def party_stat(b):
    """the enemy mon's plain Attack stat (MON_DATA_ATK of the party mon)"""
    return enemy_data(b, "MON_DATA_ATK")


def lair_leave_standing(b, t):
    """a boss that is beaten but not caught stays: Raikou (a forced win, not a catch) keeps its flag clear and fights again"""
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_RAIKOU", False)
    stand_at(b, "raikou")
    b.press("A", 4, 26)
    t.check("Raikou's lair: a boss battle starts", start_battle(b))
    wait_menu(b)
    s = state(b)
    t.check("Raikou: 2 bars, no form change", s["is_boss"] and s["total"] == 2 and s["species"] == SP("RAIKOU") and s["visible"] == 1, s)
    end_battle(b)
    t.check("a win without a catch leaves Raikou standing (not retired)", not b.flag("FLAG_PG_RAIKOU"))
    b.set_flag("FLAG_PG_RAIKOU", True)


def lair_rougarou(b, t):
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_BADGE06_GET")
    b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
    b.set_flag("FLAG_RECEIVED_LYCANROCITE", False)
    b.set_clock(22)
    b.frames(30)
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.frames(20)
    stand_at(b, "rougarou")
    b.set_move(0, "MOVE_AURA_SPHERE")                    # Rock / Dark: Psychic cannot hurt it
    b.press("A", 4, 26)
    t.check("the rougarou's lair: a battle starts", start_battle(b))
    wait_menu(b)
    s = state(b)
    orig = ORIG["moves"]
    copy_shot(b.shot("rougarou_2bars"), "boss_lair_rougarou_2bars.png")
    t.check("the rougarou: a boss with 2 bars as Lycanroc (Midnight), its own moves", s["is_boss"] and s["total"] == 2 and s["species"] == SP("LYCANROC_MIDNIGHT") and s["moves"] == orig, s)
    frames = []
    attack(b, 1, True, frames)
    s = state(b)
    t.check("breaking its bar unleashes Mega Lycanroc (form), HP full, 1 bar left, its moves unchanged (a form-only phase)",
            s["species"] == SP("LYCANROC_MIDNIGHT_MEGA") and s["bars"] == 1 and s["hp"] == s["maxhp"] and s["moves"] == orig, s)
    montage(frames, "boss_phase_change_rougarou.png", ["barrier broke", "surging", "transformed"])
    end_battle(b)
    b.set_move(0, "MOVE_PSYCHIC")
    b.set_flag("FLAG_HIDE_ROUTE14_ROUGAROU", True)


def lair_kyogre_arena(b, t):
    """the Drowned Temple's post-game Kyogre: 2 bars, Primal on the break; caught as plain Kyogre with its own moves"""
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 2)
    b.set_flag("FLAG_PG_KYOGRE_RE", False)
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN", True)
    b.give_item("ITEM_MASTER_BALL", 3)
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.frames(20)
    b.warp("LandsEnd_DrownedTemple", 9, 6)
    b.face("U")
    b.frames(20)
    n0 = b.party_count()
    b.press("A", 4, 26)
    t.check("the Drowned Temple's Kyogre: a battle starts", start_battle(b))
    wait_menu(b)
    orig = ORIG["moves"]
    s = state(b)
    t.check("Kyogre (post-game): a boss with 2 bars, phase 0 moves in battle (its own moves are kept aside)",
            s["is_boss"] and s["total"] == 2 and s["species"] == SP("KYOGRE") and s["moves"] == [MV("HYDRO_PUMP"), MV("ICE_BEAM"), MV("CALM_MIND"), MV("SURF")], s)
    attack(b, 1, True)
    s = state(b)
    t.check("its break: Primal Kyogre with the Primal moves, 1 bar left", s["species"] == SP("KYOGRE_PRIMAL") and s["bars"] == 1 and MV("ORIGIN_PULSE") in s["moves"], s)
    attack(b, 1, True, limit=700)
    caught = catch_through(b, n0)
    t.check("the last break offers the catch and the Master Ball catches it (party %d -> %d)" % (n0, b.party_count()), caught)
    last = b.party_count() - 1
    sp = party_data(b, last, "MON_DATA_SPECIES")
    t.check("the caught one is plain Kyogre (the Primal form ended with the battle)", sp == SP("KYOGRE"), sp)
    t.check("... and its own moves are back (not the boss phase moves)", party_moves(b, last) == orig, (party_moves(b, last), orig))
    t.check("the catch retires it (FLAG_PG_KYOGRE_RE)", b.flag("FLAG_PG_KYOGRE_RE"))


def no_leak(b, t):
    """a plain scripted wild battle after the bosses: no bars, no boss flag"""
    b.set_flag("FLAG_BADGE03_GET")
    o = [o for o in map_data("CrescentCity_Dept1f")["objects"] if "Rotom" in o["script"]]
    t.check("(the Rotom TV object exists to start a plain battle)", bool(o), "")
    if not o:
        return
    b.warp("CrescentCity_Dept1f", o[0]["x"], o[0]["y"] + 1)
    b.face("U")
    b.frames(20)
    b.press("A", 4, 26)
    t.check("a plain wild battle starts", start_battle(b))
    wait_menu(b)
    s = state(b, 1)
    t.check("... with no boss, no bars, no barrier icons", not s["is_boss"] and s["total"] == 0 and s["visible"] == 0, s)
    end_battle(b)


# ------------------------------------------------------------------------------------------------------------------------------------------ the soft reset
def soft_reset(b0, t):
    """a save made in front of Celebi; boots with different timing roll different Pokemon in the boss encounter (the roll happens when the battle starts)"""
    b = Bot(rom=b0.rom, out_dir=b0.out / "sr_save")
    try:
        soft_reset_run(b, t)
    finally:
        b.close()


def soft_reset_run(b, t):
    setup(b)
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_CELEBI", False)
    b.set_clock(12)
    stand_at(b, "celebi")
    b.frames(30)
    S.save_game(b)
    sav = b.out / "boss_pre.sav"
    b.h.cmd("dumpsave " + wsl_path(sav))
    rolls = []
    for extra in (0, 53, 197, 311):
        c = Bot(rom=b.rom, out_dir=b.out / ("sboot_%d" % extra), save=sav)
        try:
            S.continue_game(c, extra)
            c.face("U")
            c.press("A", 4, 26)
            if not start_battle(c):
                rolls.append(None)
                continue
            txt = intro_text(c)
            pers = c.r32(S.enemy_mon(c))
            nat, gen, shiny = describe(c, SP("CELEBI"))
            m = S.WILD.search(txt or "")
            wait_menu(c)
            boss = state(c)["is_boss"]
            rolls.append((pers, nat, gen, shiny, boss, m is not None and m.group(2) == nat))
        finally:
            c.close()
    t.check("every boot reached the boss battle with the wild intro matching the roll", all(r and r[4] and r[5] for r in rolls), rolls)
    pers = {r[0] for r in rolls if r}
    natures = {r[1] for r in rolls if r}
    t.check("different boot timing gives different Pokemon (%d personalities, natures %s)" % (len(pers), sorted(natures)), len(pers) >= 3 and len(natures) >= 2,
            ["%08x %s %s" % (r[0], r[1], r[2]) for r in rolls if r])


def run(b, t):
    setup(b)
    finale_kyogre(b, t)
    finale_groudon(b, t)
    finale_rayquaza(b, t)
    lair_celebi(b, t)
    lair_leave_standing(b, t)
    lair_rougarou(b, t)
    lair_kyogre_arena(b, t)
    no_leak(b, t)
    soft_reset(b, t)
