"""Phase-3 fix agent D (engine + data), 2026-10-14. One section per item, each isolated so one failure does not hide the others.

  D1  the nurse with an EMPTY party (Isle Marais shelter, before the starter): a polite line and the script ends; the heal field effect itself
      (PokeballGlowEffect_PlaceBalls, sNumMons u8 wrapped from 0) finishes instead of running out of sprite slots
  D2  Primordial Sea / Delta Stream bypass the overworld-weather block: the Rayquaza raid under the shrine thunderstorm sets Strong Winds at the Mega,
      and a player Primal Kyogre on a rain map (Storm's Edge) brings Primordial Sea
  D4  Galarian Corsola is obtainable: the Day Care keeps the Cursola egg as Corsola-Galar; the Lands End Surf table (5% slot) has one
  D5  the Alpha indicator of a Primal boss appears after the reversion animation, not with the barrier-broke text
  D6  a victory catch that cannot start (no Poke Balls) says why
  D7  OW 4x: a normal D-pad tap (up to 7 frames) turns in place instead of stepping, at every speed; a long press still walks
  D8  Ominous Wind / Razor Wind / Silver Wind are not Wind moves
  D9  Budew's egg list carries Bullet Seed and Power Whip; Alolan Raichu can relearn Pikachu's five dagger moves
  D10 Kingfisher opens with Tailwind in every one of several real fights
(D3 Derby speeds live in t17_gamecorner; D11 is an investigation, see audit/21_fixes_D.md)
"""
import sys
from pathlib import Path

from bot import Bot, ROOT, enum_value, map_data

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
import t25_boss as T  # noqa: E402  (boss-battle helpers: start_battle, wait_menu, attack, state, end_battle, text_now)
import t19_starters as S  # noqa: E402
import t16_speed as SPD  # noqa: E402

STRONG_WINDS = 1 << 10     # B_WEATHER_STRONG_WINDS (BATTLE_WEATHER_STRONG_WINDS = 10)
RAIN_PRIMAL = 1 << 2
TAG_NONE = 0xFFFF
BADGES = ["FLAG_BADGE0%d_GET" % i for i in range(1, 9)]


def section(t, name, fn, *a):
    try:
        fn(*a)
    except Exception as e:      # noqa: BLE001  (a crash of the emulator is also reported, and then the rest of the run is lost anyway)
        t.check("%s: no exception" % name, False, repr(e)[:300])
        if type(e).__name__ == "GameCrash":
            raise


def hold_item(b, slot, item):
    base = b.r32(b.sym("gPlayerPartyPtr")) + slot * 100
    scratch = b.sym("gStringVar4")
    b.w16(scratch, enum_value("items.h", item))
    b.call("SetMonData", base, T.MD["MON_DATA_HELD_ITEM"], scratch)


def reset_party(b, *mons):
    b.call("ZeroPlayerPartyMons")
    for sp, lv in mons:
        b.give_mon(sp, lv)


def full_setup(b, story):
    b.set_var("VAR_STARTER_MON", 2)
    for f in BADGES + ["FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_RECEIVED_HM_SURF", "FLAG_DUST_STORMS_LIFTED", "FLAG_RECEIVED_DIVING_GEAR"]:
        b.set_flag(f, True)
    b.give_item("ITEM_LANTERN", 1)
    b.set_var("VAR_ORLEANS_STORY", story)


# ------------------------------------------------------------------------------------------------------------------------------------------ D1
def d1_nurse(b, t):
    t.check("(setup) the party is empty", b.party_count() == 0, b.party_count())
    b.warp("IsleMarais_Shelter", 2, 5)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 26)
    b.frames(90)
    txt = S.text_at(b, "gStringVar4", 200).replace("\n", " ")
    t.check("the nurse tells an empty-handed player to come back with a POKeMON (no heal prompt)", "Come back when you have" in txt, txt)
    done = b.advance_text(30)
    b.check_alive("nurse with an empty party")
    t.check("... and the script ends, the player is free", done and b.script_status() == 2 and b.in_overworld(), b.where())
    b.shot("nurse_empty")


def d1_effect(b, t):
    """the engine half: the heal field effect with 0 mons must finish (before the fix it created sprites until the engine asserted)"""
    import re
    fx = int(re.search(r"#define FLDEFF_POKECENTER_HEAL\s+(\d+)", (Path(ROOT) / "include/constants/field_effects.h").read_text()).group(1))
    b.call("FieldEffectStart", fx)
    b.frames(30)
    t.check("the heal effect started", b.call("FieldEffectActiveListContains", fx) & 0xFF == 1)
    for _ in range(20):
        b.frames(30)
        if b.call("FieldEffectActiveListContains", fx) & 0xFF == 0:
            break
    b.check_alive("heal effect with 0 mons")
    t.check("the heal field effect with an empty party finishes (no sprite-slot runaway)", b.call("FieldEffectActiveListContains", fx) & 0xFF == 0, "")
    t.check("... and the game is still in the overworld", b.in_overworld(), b.callback2_name())


# ------------------------------------------------------------------------------------------------------------------------------------------ D2
def d2_rayquaza(b, t):
    b.set_var("VAR_ORLEANS_STORY", 42)
    b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 2)
    b.set_flag("FLAG_HIDE_SHRINE_RAYQUAZA", False)
    b.set_flag("FLAG_HIDE_SHRINE_JAYDEN", False)
    b.warp("OldestShrine", 16, 10)
    b.face("U")
    t.check("(setup) the shrine has overworld weather in the raid (thunderstorm)", b.call("GetCurrentWeather") & 0xFF != 0, b.call("GetCurrentWeather") & 0xFF)
    b.press("A", 4, 26)
    t.check("the Rayquaza raid starts", T.start_battle(b, 200))
    t.check("... and reaches the turn menu", T.wait_menu(b, 700))
    rq = T.rayquaza_battler(b)
    down = rq == 3
    T.attack(b, rq, True, None, target_down=down)
    T.attack(b, rq, True, None, target_down=down)
    s = T.state(b, rq)
    t.check("Mega Rayquaza reached", s["species"] == T.SP("RAYQUAZA_MEGA"), s)
    t.check("Delta Stream took hold under the overworld thunderstorm (Strong Winds in gBattleWeather, %#x)" % s["weather"], bool(s["weather"] & STRONG_WINDS), "%#x" % s["weather"])
    b.shot("rayquaza_delta_stream")
    T.end_battle(b)


def d2_kyogre(b, t):
    reset_party(b, ("SPECIES_KYOGRE", 60))
    hold_item(b, 0, "ITEM_BLUE_ORB")
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_clock(12)
    b.frames(30)
    b.set_flag("FLAG_PG_ZAPDOS", False)
    b.warp("StormsEdge", 22, 21)
    b.frames(40)
    t.check("(setup) Storm's Edge has overworld weather", b.call("GetCurrentWeather") & 0xFF != 0, b.call("GetCurrentWeather") & 0xFF)
    b.face("U")
    b.press("A", 4, 26)
    t.check("Zapdos's lair starts a battle", T.start_battle(b, 200))
    T.wait_menu(b, 900)
    sp = T.bm(b, 0, T.O_SPECIES)
    w = b.r16(b.sym("gBattleWeather"))
    t.check("the player's Kyogre holding the Blue Orb reverts to Primal Kyogre", sp == T.SP("KYOGRE_PRIMAL"), sp)
    t.check("... and Primordial Sea is set under the overworld weather (gBattleWeather %#x)" % w, bool(w & RAIN_PRIMAL), "%#x" % w)
    b.shot("primal_kyogre_stormsedge")
    T.end_battle(b)


# ------------------------------------------------------------------------------------------------------------------------------------------ D4
def d4_daycare(b, t):
    sb1 = b.save1()
    dc = sb1 + 0x3138
    party = b.r32(b.sym("gPlayerPartyPtr"))
    cnt = b.r32(b.sym("gPlayerPartyCountPtr"))
    results = []
    for parent in ("SPECIES_CURSOLA", "SPECIES_CORSOLA_GALAR"):
        b.set_flag("FLAG_PENDING_DAYCARE_EGG", False)
        for i in range(0x150 // 4):
            b.w32(dc + 4 * i, 0)
        b.call("ZeroPlayerPartyMons")
        b.give_mon(parent, 30)
        for i in range(20):
            b.w32(dc + 4 * i, b.r32(party + 4 * i))
        b.call("ZeroPlayerPartyMons")
        b.give_mon("SPECIES_DITTO", 30)
        for i in range(20):
            b.w32(dc + 0x8C + 4 * i, b.r32(party + 4 * i))
        b.call("ZeroPlayerPartyMons")
        b.give_item("ITEM_OVAL_CHARM", 1)
        got = None
        for n in range(40000):
            b.call("IncrementDaycareSteps")
            if b.flag("FLAG_PENDING_DAYCARE_EGG"):
                b.call("GiveEggFromDaycare")
                got = b.call("GetMonData2", party, T.MD["MON_DATA_SPECIES"]) & 0xFFFF
                break
        results.append((parent, got))
    want = enum_value("species.h", "SPECIES_CORSOLA_GALAR")
    for parent, got in results:
        t.check("Day Care: %s + Ditto gives a Galarian Corsola egg (got species %s, want %d)" % (parent, got, want), got == want, results)


def d4_wild(t):
    import json
    d = json.loads((Path(ROOT) / "src/data/wild_encounters.json").read_text(encoding="utf-8"))
    hits = []
    for g in d["wild_encounter_groups"]:
        for e in g["encounters"]:
            if e.get("base_label") != "gLandsEnd_Orleans":
                continue
            for i, m in enumerate(e["water_mons"]["mons"]):
                if m["species"] == "SPECIES_CORSOLA_GALAR":
                    hits.append((i, m["min_level"], m["max_level"]))
    t.check("Lands End (the waters round the Drowned Temple) Surf table holds Galarian Corsola in the 5% slot (index 2)", len(hits) == 1 and hits[0][0] == 2, hits)


# ------------------------------------------------------------------------------------------------------------------------------------------ D5 / D6
def break_bar_log(b, boss=1, limit=500):
    """kill the boss's bar and poll while the break plays: [(frame text, indicator pal tag, species)] every ~6 frames"""
    T.heal_player(b)
    b.w16(b.sym("gBattleMons") + boss * T.STRIDE + T.O_HP, 1)
    turn0 = T.turn_counter(b)
    b.press("A", 4, 30)
    b.press("A", 4, 30)
    log = []
    for i in range(limit):
        b.check_alive("bar break")
        if not b.in_battle():
            break
        txt = T.text_now(b)
        tag = b.call("GetIndicatorPalTag", boss) & 0xFFFFFFFF
        log.append((txt, tag, T.bm(b, boss, T.O_SPECIES)))
        if T.at_menu(b) and T.turn_counter(b) != turn0:
            break
        b.frames(6)
        if i % 5 == 4:
            b.press("A", 4, 4)
    return log


def d5_indicator(b, t):
    reset_party(b, ("SPECIES_MEWTWO", 100))
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN", True)
    b.warp("LandsEnd_DrownedTemple", 9, 6)
    b.face("U")
    b.press("A", 4, 26)
    t.check("(setup) the Kyogre raid starts", T.start_battle(b) and T.wait_menu(b))
    tag0 = b.call("GetIndicatorPalTag", 1) & 0xFFFFFFFF
    t.check("before the break the boss shows plain 'Lv' (no indicator)", tag0 == TAG_NONE or tag0 == 0xFFFFFFFF or tag0 >= 0xFFFF, hex(tag0))
    log = break_bar_log(b)
    broke = [x for x in log if "barrier broke" in x[0]]
    primal_txt = [x for x in log if "primal state" in x[0]]
    t.check("the break and the reversion texts both showed", bool(broke) and bool(primal_txt), [x[0][:30] for x in log][:12])
    if broke and primal_txt:
        t.check("with the 'barrier broke' text up the healthbox still shows 'Lv' (no Alpha yet)", all(x[1] >= 0xFFFF for x in broke), [hex(x[1]) for x in broke])
        t.check("once the reversion text is up the indicator is on", all(x[1] < 0xFFFF for x in primal_txt), [hex(x[1]) for x in primal_txt])
    last = log[-1] if log else None
    t.check("after the break the Primal indicator stays (Primal Kyogre)", last is not None and last[1] < 0xFFFF and last[2] == T.SP("KYOGRE_PRIMAL"), last)
    T.end_battle(b)


def d6_no_balls(b, t):
    """a lair boss' victory catch with no Poke Balls: the boss faints and says why there is no catch prompt; with balls it still asks"""
    reset_party(b, ("SPECIES_MEWTWO", 100))
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_CELEBI", False)
    b.set_clock(12)
    b.frames(30)
    pk = b.sym("gBagPockets") + 8 * 1          # POCKET_POKE_BALLS
    slots, cap = b.r32(pk), b.r16(pk + 4) & 0x3FF
    for k in range(cap * 4):
        b.w8(slots + k, 0)
    T.stand_at(b, "celebi")
    b.press("A", 4, 26)
    t.check("(setup) Celebi's lair starts", T.start_battle(b))
    T.wait_menu(b)
    T.attack(b, 1, True)
    seen = []
    T.heal_player(b)
    b.w16(b.sym("gBattleMons") + T.STRIDE + T.O_HP, 1)
    b.press("A", 4, 30)
    b.press("A", 4, 30)
    for i in range(400):
        if not b.in_battle():
            break
        txt = T.text_now(b)
        if txt and (not seen or seen[-1] != txt):
            seen.append(txt)
        b.frames(8)
        if i % 4 == 3:
            b.press("A", 4, 4)
    t.check("no balls: the player is told (message mentions Poke Balls)", any("no Pok" in x and "Ball" in x for x in seen), seen[-6:])
    t.check("... and no catch prompt came up", not any("Throw a Pok" in x for x in seen), seen[-6:])
    b.advance_text(40)
    b.frames(60)
    t.check("the battle ended and the player is free", not b.in_battle(), b.where())
    b.set_flag("FLAG_PG_CELEBI", True)


# ------------------------------------------------------------------------------------------------------------------------------------------ D7
def d7_tap(b, t):
    reset_party(b, ("SPECIES_TOTODILE", 20))
    b.warp("CrescentCity", 46, 12)
    b.frames(30)
    rows = {}
    for ow in (0, 1, 2, 3):
        SPD.set_opts(b, ow=ow)
        row = {}
        for hold in (3, 5, 7, 14):
            b.warp("CrescentCity", 46, 12)
            b.frames(40)
            p0 = b.pos()
            b.press("RIGHT", hold, 0)
            b.release()
            b.frames(60)
            row[hold] = "STEP" if b.pos() != p0 else "turn"
        rows[ow + 1] = row
        t.check("OW %dx: taps of 3, 5 and 7 frames only turn" % (ow + 1), all(row[h] == "turn" for h in (3, 5, 7)), row)
        t.check("OW %dx: a 14-frame press walks" % (ow + 1), row[14] == "STEP", row)
    SPD.set_opts(b, ow=0)
    t.note(rows)


# ------------------------------------------------------------------------------------------------------------------------------------------ D8 / D9
def d8_wind(b, t):
    src = (Path(ROOT) / "src/data/moves_info.h").read_text(encoding="utf-8", errors="replace")
    ok = {}
    for mv in ("OMINOUS_WIND", "RAZOR_WIND", "SILVER_WIND"):
        i = src.index("[MOVE_%s] =" % mv)
        block = src[i:src.index("\n    },", i)]
        ok[mv] = ".windMove = FALSE" in block
    t.check("moves_info.h: Ominous Wind, Razor Wind and Silver Wind carry no Wind flag", all(ok.values()), ok)
    # in-ROM: the compiled flag (IsWindMove is a static inline, so read it from the data when the symbol exists)
    try:
        f = b.syms["IsWindMove"]
    except Exception:       # noqa: BLE001
        f = None
    if f:
        for mv, want in (("OMINOUS_WIND", 0), ("RAZOR_WIND", 0), ("SILVER_WIND", 0), ("GUST", 1), ("HURRICANE", 1)):
            got = b.call("IsWindMove", enum_value("moves.h", "MOVE_" + mv)) & 0xFF
            t.check("ROM: IsWindMove(%s) == %d" % (mv, want), got == want, got)
    else:
        t.note("IsWindMove has no out-of-line symbol in this build; the source check above is the evidence")


def d9_moves(b, t):
    reset_party(b, ("SPECIES_ROSELIA", 50))
    party = b.r32(b.sym("gPlayerPartyPtr"))
    buf = b.sym("gDisplayedStringBattle")

    def relearn(fn):
        n = b.call(fn, party, buf) & 0xFF
        return [b.r16(buf + 2 * i) for i in range(n)]

    for slot in range(4):
        b.call("SetMonMoveSlot", party, 0, slot)
    eggs = relearn("GetRelearnerEggMoves")
    t.check("Roselia can relearn Bullet Seed and Power Whip as egg moves (base species Budew)",
            enum_value("moves.h", "MOVE_BULLET_SEED") in eggs and enum_value("moves.h", "MOVE_POWER_WHIP") in eggs, len(eggs))
    reset_party(b, ("SPECIES_BUDEW", 5))
    eggs = relearn("GetRelearnerEggMoves")
    t.check("Budew's own egg list has them", enum_value("moves.h", "MOVE_BULLET_SEED") in eggs and enum_value("moves.h", "MOVE_POWER_WHIP") in eggs, len(eggs))
    reset_party(b, ("SPECIES_RAICHU_ALOLA", 100))
    for slot in range(4):
        b.call("SetMonMoveSlot", party, 0, slot)
    lv = relearn("GetRelearnerLevelUpMoves")
    want = ["DOUBLE_KICK", "SWIFT", "ZIPPY_ZAP", "SPLISHY_SPLASH", "WILD_CHARGE"]
    missing = [m for m in want if enum_value("moves.h", "MOVE_" + m) not in lv]
    t.check("Alolan Raichu can relearn Pikachu's five dagger moves", not missing, missing)


# ------------------------------------------------------------------------------------------------------------------------------------------ D10
def d10_kingfisher(b, t):
    firsts = []
    mv_tail = enum_value("moves.h", "MOVE_TAILWIND")
    objs = map_data("PointeRouge_Gym")["objects"]
    o = [x for x in objs if "Kingfisher0" in x.get("script", "")][0]
    for extra in range(6):
        c = Bot(rom=b.rom, out_dir=b.out / ("king_%d" % extra))
        try:
            c.new_game()
            c.give_mon("SPECIES_SHUCKLE", 60)
            c.set_var("VAR_STARTER_MON", 1)
            for f in ("FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET", "FLAG_POINTE_TOURNEY_WON", "FLAG_POINTE_GYM_TAILWIND"):
                c.set_flag(f)
            c.set_var("VAR_ORLEANS_STORY", 20)
            c.warp("PointeRouge_Gym", o["x"], o["y"] + 1)
            c.frames(30 + extra * 7)
            c.face("U")
            c.press("A", 4, 30)
            for _ in range(200):
                if c.in_battle():
                    break
                c.press("A", 4, 22)
                c.frames(5)
            c.force_win = False
            first = None
            ch = c.sym("gChosenMoveByBattler")
            for _ in range(1500):
                c.frames(8)
                if not c.in_battle():
                    break
                mv = c.r16(ch + 2)
                if mv:
                    first = mv
                    break
                c.press("A", 3, 3)
            firsts.append(first)
        finally:
            c.close()
    t.check("Kingfisher's first move is Tailwind in all 6 real fights", all(f == mv_tail for f in firsts), firsts)


def run(b, t):
    b.new_game()
    section(t, "D1 nurse", d1_nurse, b, t)
    section(t, "D1 effect", d1_effect, b, t)
    section(t, "D4 wild table", lambda: d4_wild(t))
    section(t, "D8 wind", d8_wind, b, t)
    reset_party(b, ("SPECIES_MEWTWO", 100))
    full_setup(b, 42)
    section(t, "D2 rayquaza", d2_rayquaza, b, t)
    section(t, "D2 kyogre", d2_kyogre, b, t)
    section(t, "D5 indicator", d5_indicator, b, t)
    section(t, "D6 no balls", d6_no_balls, b, t)
    section(t, "D4 daycare", d4_daycare, b, t)
    section(t, "D7 tap", d7_tap, b, t)
    section(t, "D9 moves", d9_moves, b, t)
    section(t, "D10 kingfisher", d10_kingfisher, b, t)
