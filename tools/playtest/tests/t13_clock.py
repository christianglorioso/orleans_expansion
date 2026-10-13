"""The in-game clock (fake RTC, Gen 9 ratio: one day = 72 minutes of play) and everything that reads it: a new game starts in the morning; the clock
advances at 20 game seconds per second of play; the rest spots in every healer (Common_EventScript_RestSpot) set each time of day, heal the party
and refuse a time that already is; the Redfield mirrors work in daylight only (rest until morning), Ursaluna Bloodmoon and the Route 14 rougarou
appear at night only (rest until night); the day/night tint follows the clock. (Plus the old-save migration, FakeRtc_MigrateSave; t13b_oldsave continues a real save from the previous build.)"""
import json
import re

from bot import ROOT, map_data, TIMES_OF_DAY, CLOCK_SECONDS_PER_SECOND

CENTER = "CrescentCity_PokecenterQuarter"      # rest cell (12, 3), stand at (12, 4) facing up
PARTY_HP = 0x56
PARTY_MAXHP = 0x58
KEY = {"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}


def hour_begins():
    """MORNING/DAY/EVENING/NIGHT_HOUR_BEGIN of the GEN_8+ (GEN_LATEST) table in include/constants/rtc.h"""
    txt = (ROOT / "include/constants/rtc.h").read_text()
    blk = txt[txt.index("#elif OW_TIMES_OF_DAY >= GEN_8"):]
    blk = blk[:blk.index("#endif")]
    return [int(re.search(r"#define %s_HOUR_BEGIN\s+(\d+)" % n, blk).group(1)) for n in ("MORNING", "DAY", "EVENING", "NIGHT")]


def menu_up(b):
    return any("ultichoice" in str(x) for x in b.active_tasks())


def menu_choice(b, down):
    """press A through the message until the option menu is up, move the cursor `down` entries, choose"""
    for _ in range(60):
        if menu_up(b):
            break
        b.press("A", 4, 30)
    b.frames(20)
    for _ in range(down):
        b.press("DOWN", 6, 14)
        b.frames(6)
    b.press("A", 4, 30)
    b.frames(20)


def party_base(b):
    return b.r32(b.sym("gPlayerPartyPtr"))


def hp(b):
    base = party_base(b)
    return b.r16(base + PARTY_HP), b.r16(base + PARTY_MAXHP)


def rest(b, choice, mapname=CENTER, sx=12, sy=4, face="U"):
    """stand at the rest cell of a room, ask, pick option `choice` (0 morning, 1 day, 2 evening, 3 night, 4 cancel); True when the script ended"""
    b.warp(mapname, sx, sy)
    b.face(face)
    b.press("A", 4, 20)
    menu_choice(b, choice)
    return b.advance_text(60)


def stand_cells(name, cells):
    """(stand x, y, face towards the rest cell) for each rest cell: a walkable neighbour that is no object and no warp"""
    d = map_data(name)
    busy = {(o["x"], o["y"]) for o in d["objects"]} | {(o["x"], o["y"]) for o in d["warps"]}
    out = []
    for x, y in cells:
        for dx, dy, face in ((0, 1, "U"), (0, -1, "D"), (-1, 0, "R"), (1, 0, "L")):
            sx, sy = x + dx, y + dy
            if 0 <= sx < d["width"] and 0 <= sy < d["height"] and d["coll"][sy][sx] == 0 and (sx, sy) not in busy:
                out.append((sx, sy, face))
                break
    return out


def rest_rooms():
    """{map: ([rest cells], map.json)} straight from the committed map.json files"""
    res = {}
    for p in sorted((ROOT / "data/maps").glob("*/map.json")):
        m = json.loads(p.read_text(encoding="utf-8"))
        cells = [(e["x"], e["y"]) for e in m.get("bg_events", []) if e.get("script") == "Common_EventScript_RestSpot"]
        if cells:
            res[p.parent.name] = (cells, m)
    return res


def run(b, t):
    begins = hour_begins()
    t.check("the engine's GEN_LATEST boundaries are morning 6, day 10, evening 19, night 20", begins == [6, 10, 19, 20], begins)

    # ---------------------------------------------------------------- the rest spots, static: every healer has one, clear of the nurse
    rooms = rest_rooms()
    healers = ["CrescentCity_PokecenterQuarter", "CrescentCity_PokecenterWaterfront", "GrandOak_PokemonCenter", "LandsEnd_Pokecenter",
               "LutinsHollow_Pokecenter", "PointeRouge_Pokecenter", "Redfield_Pokecenter", "StormsEdge_Pokecenter", "IsleMarais_Shelter",
               "BattleFrontier_PokemonCenter_1F", "CampCocodrie_NurseCabin", "OldWater_Healer", "OldWater_RestHouse"]
    t.check("every Pokemon Center, the nurse cabin and the Old Water healer/rest house has a rest spot", all(h in rooms for h in healers),
            [h for h in healers if h not in rooms])
    for h in healers:
        if h not in rooms:
            continue
        cells, m = rooms[h]
        nurses = [o for o in m["object_events"] if "NURSE" in o["graphics_id"]]
        far = all(abs(x - n["x"]) + abs(y - n["y"]) >= 3 for x, y in cells for n in nurses)
        t.check("%s: rest spot clear of the nurse, a free cell to stand on, <= 16 objects" % h,
                far and len(stand_cells(h, cells)) == len(cells) and len(m["object_events"]) <= 16,
                "cells %s nurses %s objs %d" % (cells, [(n["x"], n["y"]) for n in nurses], len(m["object_events"])))

    # ---------------------------------------------------------------- a new game starts in the morning
    b.new_game()
    b.give_mon("SPECIES_MEW", 50)
    d, h, m, s = b.clock()
    t.check("new game: day 0, 08:00-08:05, morning", d == 0 and h == 8 and m < 5 and b.time_of_day() == 0, (d, h, m, s, b.time_of_day()))
    b.shot("new_game_clock")

    # ---------------------------------------------------------------- the clock runs at the Gen 9 ratio
    b.set_clock(12, 0)
    t0 = b.clock_seconds()
    b.frames(60 * 60)                                  # 60 s of play
    dt = b.clock_seconds() - t0
    t.check("60 s of play = 20 game minutes (ratio %d)" % CLOCK_SECONDS_PER_SECOND,
            abs(dt - 60 * CLOCK_SECONDS_PER_SECOND) <= 30, "%d game seconds" % dt)
    b.set_clock(23, 59)
    b.frames(60 * 10)                                  # 10 s of play: past midnight
    d, h, m, s = b.clock()
    t.check("the clock rolls over midnight into day 1", d == 1 and h == 0, (d, h, m, s))
    for hour, tod in ((5, 3), (6, 0), (9, 0), (10, 1), (18, 1), (19, 2), (20, 3), (23, 3)):
        b.set_clock(hour, 30)
        t.check("%02d:30 is %s" % (hour, TIMES_OF_DAY[tod]), b.time_of_day() == tod, b.time_of_day())

    # ---------------------------------------------------------------- resting: each time of day, heal, already, cancel
    b.set_clock(12, 0)
    b.w16(party_base(b) + PARTY_HP, 1)
    ok = rest(b, 0)                                    # MORNING from 12:00 -> 06:00 the next day
    d, h, m, s = b.clock()
    b.shot("rested_morning")
    t.check("rest until MORNING: 06:00 next day, party healed, script ended", ok and h == 6 and m < 10 and d == 1 and b.time_of_day() == 0
            and hp(b)[0] == hp(b)[1], "clock %s hp %s ended %s" % ((d, h, m), hp(b), ok))
    for choice, name, want in ((1, "DAY", 10), (2, "EVENING", 19), (3, "NIGHT", 20)):
        b.w16(party_base(b) + PARTY_HP, 1)
        ok = rest(b, choice)
        d, h, m, s = b.clock()
        b.shot("rested_" + name.lower())
        t.check("rest until %s: %02d:00, party healed" % (name, want), ok and h == want and m < 10 and b.time_of_day() == choice
                and hp(b)[0] == hp(b)[1], "clock %s tod %d hp %s" % ((d, h, m), b.time_of_day(), hp(b)))
    before = b.clock_seconds()
    b.w16(party_base(b) + PARTY_HP, 1)
    ok = rest(b, 3)                                    # NIGHT again: it already is
    t.check("resting until the time of day it already is changes nothing (no heal, no time passes)",
            ok and abs(b.clock_seconds() - before) < 1800 and hp(b)[0] == 1, "dt %d hp %s" % (b.clock_seconds() - before, hp(b)))
    before = b.clock_seconds()
    ok = rest(b, 4)                                    # CANCEL
    t.check("CANCEL changes nothing", ok and abs(b.clock_seconds() - before) < 1800 and hp(b)[0] == 1, "dt %d" % (b.clock_seconds() - before))
    b.w16(party_base(b) + PARTY_HP, hp(b)[1])

    # ---------------------------------------------------------------- every healer's spot opens the menu (B backs out)
    for h_ in healers:
        if h_ not in rooms:
            continue
        cells, m_ = rooms[h_]
        sx, sy, face = stand_cells(h_, cells)[0]
        b.warp(h_, sx, sy)
        b.press(KEY[face], 3, 12)                      # a short tap turns in place without walking
        if b.pos() != (sx, sy):                        # the rest cell is walkable (a cushion) and we stepped onto it
            t.note("%s: stepped onto the rest cell instead of turning" % h_)
            b.warp(h_, sx, sy)
        b.press("A", 4, 20)
        shown = False
        for _ in range(40):
            if menu_up(b):
                shown = True
                break
            b.press("A", 4, 30)
        b.frames(10)
        b.shot("rest_" + h_)
        b.press("B", 4, 30)
        b.advance_text(20)
        t.check("%s: the rest spot opens the time menu and B backs out" % h_, shown and b.script_status() == 2, "shown=%s status=%d" % (shown, b.script_status()))

    # ---------------------------------------------------------------- the Redfield mirrors need daylight: night = nothing, rest until morning = they turn
    b.set_var("VAR_REDFIELD_MIRRORS", 0)
    b.set_flag("FLAG_REDFIELD_MILL_OPEN", False)
    b.set_clock(22, 0)
    b.warp("Redfield", 31, 10)
    b.interact("L", 120)
    b.frames(20)
    t.check("night: the mirror does not turn", b.var("VAR_REDFIELD_MIRRORS") == 0, b.var("VAR_REDFIELD_MIRRORS"))
    b.shot("mirror_night")
    ok = rest(b, 0, "Redfield_Pokecenter", 12, 4, "U")  # the Center's rest spot: until morning
    t.check("rested at Redfield's Center until morning", ok and b.time_of_day() == 0, (b.clock(), b.time_of_day()))
    b.warp("Redfield", 31, 10)
    b.interact("L", 120)
    b.frames(20)
    t.check("after resting until morning the mirror turns", b.var("VAR_REDFIELD_MIRRORS") != 0, b.var("VAR_REDFIELD_MIRRORS"))
    b.shot("mirror_morning")

    # ---------------------------------------------------------------- Ursaluna Bloodmoon (story 45+): night only
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_URSALUNA_BM", True)
    b.set_flag("FLAG_PG_URSALUNA_DONE", False)
    b.set_clock(12, 0)
    b.warp("Route23_BloodmoonArroyo", 10, 13)
    b.frames(30)
    t.check("by day Ursaluna is hidden", b.flag("FLAG_PG_URSALUNA_BM"))
    rest(b, 3)                                         # until night at the Quarter's Center
    b.warp("Route23_BloodmoonArroyo", 10, 13)
    b.frames(30)
    t.check("after resting until night Ursaluna appears", not b.flag("FLAG_PG_URSALUNA_BM"), b.flag("FLAG_PG_URSALUNA_BM"))
    b.shot("ursaluna_night")
    # the Route 14 rougarou: same switch
    b.set_flag("FLAG_ROUTE14_ROUGAROU_DONE", False)
    b.warp("Route14_RougarouHollow", 10, 13)
    b.frames(30)
    t.check("at night the rougarou is in its hollow off Route 14", not b.flag("FLAG_HIDE_ROUTE14_ROUGAROU"))
    rest(b, 0)                                         # back to morning
    b.warp("Route14_RougarouHollow", 10, 13)
    b.frames(30)
    t.check("by day the rougarou is gone again", b.flag("FLAG_HIDE_ROUTE14_ROUGAROU"))

    # ---------------------------------------------------------------- the day/night tint follows the clock (outdoor screen brightness)
    from PIL import Image

    def brightness():
        p = b.shot("tint")
        im = Image.open(p).convert("L")
        return sum(im.getdata()) / (im.width * im.height)
    b.set_clock(12, 0)
    b.warp("Redfield", 12, 15)
    b.frames(240)
    day_b = brightness()
    b.set_clock(23, 0)
    b.frames(400)                                      # the tint is re-blended once a game minute (3 s)
    night_b = brightness()
    t.check("outdoors the screen is darker at night than at noon (day/night tint)", night_b < day_b - 8, "noon %.1f night %.1f" % (day_b, night_b))

    # ---------------------------------------------------------------- a save from before the clock gets one (FakeRtc_MigrateSave, run when a save is continued)
    b.set_clock(15, 0, day=5)
    b.call("FakeRtc_MigrateSave")
    d, h, m, s = b.clock()
    t.check("a save that already has a clock is left alone", (d, h) == (5, 15), (d, h, m, s))
    rtc = b.call("FakeRtc_GetCurrentTime")
    for i in range(10, 16):
        b.w8(rtc + i, 0)                               # no marker: what an old save's block 3 looks like past its old size
    b.w8(rtc + 4, 99)                                  # and garbage where the clock would be
    b.set_var("VAR_DAYS", 777)
    b.call("FakeRtc_MigrateSave")
    d, h, m, s = b.clock()
    magic = b.h.cmd("readblock %d 16" % rtc)           # the marker follows the clock (SiiRtcInfo is padded to 12 bytes)
    t.check("a save without the marker gets 08:00 on day 0, VAR_DAYS 0, the marker back", (d, h, m) == (0, 8, 0) and b.var("VAR_DAYS") == 0
            and "0c10c45a" in magic, "%s var_days=%d magic=%s" % ((d, h, m, s), b.var("VAR_DAYS"), magic))
