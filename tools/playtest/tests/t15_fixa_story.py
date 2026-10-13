"""Audit fix phase A (2026-10-13): story and text fixes that change behaviour.

  * the Blacksnake base partner battle (Wren fights beside the player against the lieutenant and Louise; a win retires the lieutenant and opens the
    carving; a loss offers TRY AGAIN; the right Wren party for each starter), Wren no longer waits at the gate once she is inside
  * the carving scene no longer names the "laid down to guard" phrase (text read from the engine's string buffer)
  * a draw in the Wren raid and in the Rayquaza raid is not a win (the retry menu appears, the story does not move)
  * the Route 8 islet: the ceremony's end puts the player on the water, afloat, even with no Surf user in the party
  * the buoy Voltorb you ran from stays; Tupelo's late lines follow the finale and the badge count
  * the nurse hint, the Fisherman at story 0, the Frontier couple at story 45, the Floette gift message
"""
from bot import map_data, enum_value

GLYPHS = {0x1B: "e", 0x00: " ", 0xAB: "!", 0xAC: "?", 0xAD: ".", 0xB8: ",", 0xB4: "'", 0xBA: "/", 0xFE: "\n", 0xFA: "\n", 0xFB: "\n", 0xB0: "...", 0xA0: "-", 0xF1: "-"}
for i in range(26):
    GLYPHS[0xBB + i] = chr(65 + i)
    GLYPHS[0xD5 + i] = chr(97 + i)
for i in range(10):
    GLYPHS[0xA1 + i] = str(i)


def message(b, n=400):
    """the text of the message box the game is showing / last showed (gStringVar4 holds the whole expanded message)"""
    a = b.sym("gStringVar4")
    out = []
    for i in range(n):
        c = b.r8(a + i)
        if c == 0xFF:
            break
        out.append(GLYPHS.get(c, "?"))
    return "".join(out)


def obj_by_script(mapname, suffix):
    for o in map_data(mapname)["objects"]:
        if o.get("script", "").endswith(suffix):
            return o
    return None


def talk(b, mapname, suffix, side="D", timeout=240, advance=False):
    o = obj_by_script(mapname, suffix)
    dx, dy = {"D": (0, 1), "U": (0, -1), "L": (-1, 0), "R": (1, 0)}[side]
    face = {"D": "U", "U": "D", "L": "R", "R": "L"}[side]
    b.warp(mapname, o["x"] + dx, o["y"] + dy)
    b.frames(20)
    if advance:
        return b.interact(face, timeout)
    b.face(face)
    b.press("A", 4, 30)
    b.frames(40)


def mash_until(b, cond, n=200, fight=True):
    for _ in range(n):
        if cond():
            return True
        if b.in_battle():
            if fight:
                b.fight()
                continue
        b.press("A", 4, 26)
    return cond()


def force_outcome(b, outcome, handler="HandleEndTurn_BattleLost"):
    """end the current battle now with a given outcome (2 lost, 3 drew, 4 ran) once the turn menu is up"""
    main_func = b.sym("gBattleMainFunc")
    for _ in range(400):
        if not b.in_battle():
            return True
        if (b.r32(main_func) & ~1) == b.sym("HandleTurnActionSelectionState"):
            b.w8(b.sym("gBattleOutcome"), outcome)
            b.w32(main_func, b.syms.call_addr(handler))
        b.press("A", 4, 26)
    return not b.in_battle()


def choice_open(b):
    return any("ultichoice" in str(x) or "esNo" in str(x) or "YesNo" in str(x) for x in b.active_tasks())


def partner_party(b):
    names = {}
    for n in ("WINGULL", "ROSELIA_ORLEANIAN", "BAYLEEF", "FUECOCO", "CROCONAW", "PELIPPER", "MEGANIUM", "SKELEDIRGE", "FERALIGATR"):
        try:
            names[enum_value("species.h", "SPECIES_" + n)] = n
        except Exception:
            pass
    base = b.sym("gParties") + 2 * 6 * 100          # B_TRAINER_PARTNER = 2
    out = []
    for k in range(3):
        s = b.call("GetMonData2", base + k * 100, 18) & 0xFFFF
        lv = b.call("GetMonData2", base + k * 100, 64) & 0xFF
        out.append((names.get(s, s), lv))
    return out


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)
    for f in ("FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET"):
        b.set_flag(f, True)

    # ---------------------------------------------------------------- the Fisherman in the shelter at story 0 (ch1 S2)
    b.set_var("VAR_ORLEANS_STORY", 0)
    talk(b, "IsleMarais_Shelter", "Fisherman5")
    t.check("the shelter Fisherman at story 0 does not claim the rescue is done", "dry off" in message(b), message(b)[:60])
    b.advance_text()

    # ---------------------------------------------------------------- the base: Wren at the gate stays inside once she went in (ch3 R2)
    b.set_var("VAR_ORLEANS_STORY", 16)
    b.set_flag("FLAG_CRESCENT_WREN_IN_BASE", False)
    b.warp("CrescentCity", 57, 58)
    b.frames(30)
    t.check("story 16: Wren waits at the Drowned Ward gate", not b.flag("FLAG_HIDE_CRESCENT_WREN"), "hide=%s" % b.flag("FLAG_HIDE_CRESCENT_WREN"))
    b.set_flag("FLAG_CRESCENT_WREN_IN_BASE", True)
    b.warp("CrescentCity", 57, 58)
    b.frames(30)
    t.check("story 16 after she went into the base: she is not at the gate again", b.flag("FLAG_HIDE_CRESCENT_WREN"), "hide=%s" % b.flag("FLAG_HIDE_CRESCENT_WREN"))

    # ---------------------------------------------------------------- the partner battle (ch3 S4), all three starter lines
    expect = {0: "FUECOCO", 1: "CROCONAW", 2: "BAYLEEF"}   # VAR_STARTER_MON 0 Totodile -> Wren has Fuecoco, 1 Chikorita -> Totodile (Croconaw), 2 Fuecoco -> Chikorita
    for starter in (0, 1, 2):
        b.set_var("VAR_STARTER_MON", starter)
        b.set_var("VAR_ORLEANS_STORY", 16)
        b.set_flag("FLAG_HIDE_CRESCENT_LIEUTENANT", False)
        b.warp("CrescentCity_BlacksnakeBase", 18, 10)
        b.frames(60)
        b.face("R")
        b.press("A", 4, 30)
        started = False
        for _ in range(120):
            if b.in_battle():
                started = True
                break
            b.press("A", 4, 26)
        b.frames(90)
        t.check("starter %d: talking to the lieutenant starts a battle" % starter, started, b.where())
        if not started:
            continue
        party = partner_party(b)
        t.check("starter %d: Wren fights beside the player with her low-level team (%s)" % (starter, expect[starter]),
                [p[0] for p in party] == ["WINGULL", "ROSELIA_ORLEANIAN", expect[starter]] and all(p[1] <= 22 for p in party), str(party))
        if starter != 2:
            force_outcome(b, 2)           # leave without finishing: answer NOT YET
            b.frames(60)
            for _ in range(120):          # the retry question arrives by itself after the message: do not press A early (it would answer YES)
                if choice_open(b):
                    break
                b.frames(10)
            b.press("B", 4, 30)
            mash_until(b, lambda: not b.in_battle() and b.script_status() == 2, 60, fight=False)
            b.frames(30)
            b.frames(120)
            t.check("starter %d: NOT YET leaves the lieutenant standing" % starter, not b.flag("FLAG_HIDE_CRESCENT_LIEUTENANT") and not b.in_battle(), b.where())
            continue
        # starter 2 plays the full story: a loss first
        force_outcome(b, 2)
        b.frames(60)
        for _ in range(120):
            if choice_open(b):
                break
            b.frames(10)
        t.check("a loss offers the retry (the defeat is not a win)", choice_open(b) or b.script_status() != 2, str(b.active_tasks()[:3]))
        b.press("A", 4, 30)              # YES: again
        b.frames(60)
        again = False
        for _ in range(80):
            if b.in_battle():
                again = True
                break
            b.press("A", 4, 26)
        t.check("TRY AGAIN starts the partner battle again", again, b.where())
        b.frames(60)
        for _ in range(60):
            if not b.in_battle():
                break
            b.fight()
        mash_until(b, lambda: b.flag("FLAG_HIDE_CRESCENT_LIEUTENANT") and b.script_status() == 2, 200, fight=False)
        b.frames(30)
        t.check("a win retires the lieutenant", b.flag("FLAG_HIDE_CRESCENT_LIEUTENANT"), b.where())
        t.check("the script ended and the player is free", b.script_status() == 2 and not b.player_locked(), "script=%s" % b.script_status())
        # the carving is no longer guarded: story 17
        b.warp("CrescentCity_BlacksnakeBase", 3, 14)
        b.frames(20)
        b.press("UP", 2, 10)
        b.press("A", 4, 30)
        mash_until(b, lambda: b.var("VAR_ORLEANS_STORY") == 17 and b.script_status() == 2, 200, fight=False)
        txt = message(b)
        t.check("the carving is found after the partner battle (story 17)", b.var("VAR_ORLEANS_STORY") == 17, "story=%d" % b.var("VAR_ORLEANS_STORY"))
    # the carving text itself: Wren senses the cut but does not recite the true phrase
    b.set_var("VAR_ORLEANS_STORY", 16)
    b.set_flag("FLAG_CARVING_FOUND", False)
    b.warp("CrescentCity_BlacksnakeBase", 3, 14)
    b.frames(20)
    b.press("UP", 2, 10)
    b.press("A", 4, 30)
    seen = ""
    for _ in range(60):
        seen += message(b) + "|"
        if b.var("VAR_ORLEANS_STORY") == 17:
            break
        b.press("A", 4, 26)
    t.check("the carving scene never says 'laid down to guard' (that is TUPELO's piece at story 21)", "down to guard" not in seen and "can't be all of it" in seen, seen[-160:])
    b.advance_text()

    # ---------------------------------------------------------------- Tupelo's late lines (ch6 S2, ch8 S1, fin S1)
    cases = [
        # (story, extra flags set, expected phrase)
        (22, ["FLAG_BADGE04_GET", "FLAG_RECEIVED_HM_SURF"], "Four verses"),
        (26, ["FLAG_BADGE05_GET"], "Five verses"),
        (30, ["FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD"], "Six verses"),
        (34, ["FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD"], "Seven verses"),
        (39, ["FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD"], "ROUTE 24"),
        (40, ["FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD", "FLAG_KYOGRE_CALMED", "FLAG_GROUDON_CALMED"], "Both sleepers are calm"),
        (42, ["FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD"], "OLDEST SHRINE"),
        (45, ["FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD"], "telling is sung"),
    ]
    for story, flags, phrase in cases:
        for f in ("FLAG_BADGE04_GET", "FLAG_BADGE05_GET", "FLAG_BADGE06_GET", "FLAG_BADGE07_GET", "FLAG_RECEIVED_CYPRESS_CHARM", "FLAG_VERSE6_HEARD",
                  "FLAG_KYOGRE_CALMED", "FLAG_GROUDON_CALMED", "FLAG_RECEIVED_HM_SURF", "FLAG_CARVING_FOUND"):
            b.set_flag(f, False)
        for f in flags + ["FLAG_RECEIVED_HM_SURF", "FLAG_ROUTE6_DEBRIS_CLEARED"]:
            b.set_flag(f, True)
        b.set_flag("FLAG_CARVING_FOUND", False)
        b.set_var("VAR_ORLEANS_STORY", story)
        b.set_var("VAR_OLD_WATER_TELLING", 2)
        b.set_var("VAR_OLD_WATER_CEREMONY", 2)
        b.set_flag("FLAG_HIDE_OLD_WATER_TUPELO", False)
        talk(b, "OldWater_SongHouse", "Tupelo0")
        msg = message(b)
        t.check("Tupelo at story %d says it (%s)" % (story, phrase), phrase in msg, msg[:90].replace("\n", "/"))
        b.advance_text()
    b.set_var("VAR_ORLEANS_STORY", 39)
    for f in ("FLAG_KYOGRE_CALMED", "FLAG_GROUDON_CALMED", "FLAG_BADGE06_GET", "FLAG_RECEIVED_CYPRESS_CHARM"):
        b.set_flag(f, True if f.endswith("CHARM") or f.endswith("06_GET") else False)
    talk(b, "OldWater_SongHouse", "Tupelo0")
    msg = message(b)
    t.check("Tupelo at story 39 names both entrances (the ruin door on Route 22, the cave on Route 24)", "ROUTE 22" in msg and "ROUTE 24" in msg, msg[:140].replace("\n", "/"))
    b.advance_text()
    b.set_flag("FLAG_KYOGRE_CALMED", True)
    talk(b, "OldWater_SongHouse", "Tupelo0")
    msg = message(b)
    t.check("one sleeper calmed: Tupelo says one is calm", "One sleeper is calm" in msg, msg[:80].replace("\n", "/"))
    b.advance_text()

    # ---------------------------------------------------------------- Wren's raid partner follows the song-house mapping (ch1 NEW-1 / ch6 S1, fixed in the hotfix)
    want = {0: "SKELEDIRGE", 1: "FERALIGATR", 2: "MEGANIUM"}     # Wren raised the starter the player did not pick and Jayden did not take
    for starter in (0, 1, 2):
        b.set_var("VAR_STARTER_MON", starter)
        b.set_var("VAR_ORLEANS_STORY", 33)
        b.set_var("VAR_OLD_WATER_RAID", 1)
        b.warp("OldWater", 22, 32)
        for _ in range(400):
            if b.in_battle():
                break
            b.press("A", 4, 22)
        b.frames(120)
        party = partner_party(b)
        t.check("raid partner for starter %d ends with %s" % (starter, want[starter]), b.in_battle() and party[2][0] == want[starter], str(party))
        force_outcome(b, 2)
        b.frames(60)
        for _ in range(80):          # the raid's retry text needs an A before its TRY AGAIN / NOT YET menu appears
            if choice_open(b):
                break
            b.press("A", 4, 26)
        b.press("B", 4, 30)          # NOT YET: back to Redfield, the raid reset
        b.frames(120)
        mash_until(b, lambda: not b.in_battle() and b.script_status() == 2, 60, fight=False)
        t.check("raid partner for starter %d: NOT YET leaves the battle" % starter, not b.in_battle() and b.map_name() == "Redfield", b.where())

    # ---------------------------------------------------------------- draws are not wins (fin S2)
    b.set_var("VAR_STARTER_MON", 0)
    b.set_var("VAR_ORLEANS_STORY", 33)
    b.set_var("VAR_OLD_WATER_RAID", 1)
    b.warp("OldWater", 22, 32)
    for _ in range(400):
        if b.in_battle():
            break
        b.press("A", 4, 22)
    t.check("the Wren raid starts", b.in_battle(), b.where())
    b.frames(90)
    force_outcome(b, 3)
    b.frames(120)
    for _ in range(80):
        if choice_open(b):
            break
        b.press("A", 4, 26)
    st = b.var("VAR_ORLEANS_STORY")
    t.check("a draw in the Wren raid is not a win: the retry menu appears and the story stays 33", choice_open(b) and st == 33, "story=%d tasks=%s" % (st, b.active_tasks()[:3]))

    b.set_var("VAR_ORLEANS_STORY", 42)
    b.set_flag("FLAG_RECEIVED_LEGENDARY", True)
    b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 2)
    b.give_mon("SPECIES_KYOGRE", 60)
    b.warp("OldestShrine", 17, 24)
    b.frames(30)
    b.warp("OldestShrine", 16, 10)
    b.face("U")
    b.press("A", 4, 20)
    for _ in range(60):
        if b.in_battle():
            break
        b.press("A", 4, 26)
        b.frames(10)
    t.check("the Rayquaza raid starts", b.in_battle(), b.where())
    b.frames(90)
    force_outcome(b, 3)
    b.frames(120)
    for _ in range(80):
        if choice_open(b):
            break
        b.press("A", 4, 26)
    st = b.var("VAR_ORLEANS_STORY")
    t.check("a draw in the Rayquaza raid is not a win: the retry menu appears and the story stays 42", choice_open(b) and st == 42, "story=%d tasks=%s" % (st, b.active_tasks()[:3]))

    # ---------------------------------------------------------------- the Route 8 islet (fin S4): the ceremony's end lands on water, afloat
    b.warp("Route8", 11, 10)      # the exact spot of the ceremony's warp
    b.frames(40)
    av = b.r8(b.sym("gPlayerAvatar"))
    t.check("a warp onto the water south of the islet gives the surfing avatar (no Surf user needed)", (av & 0x08) != 0 or (av & 0x20) != 0, "avatar flags 0x%02x" % av)
    moved = False
    for d in ("D", "L", "R", "D"):
        if b.step(d):
            moved = True
    t.check("and the player can sail on from there", moved, b.where())

    # ---------------------------------------------------------------- the buoy Voltorb you ran from stays (ch2 N1)
    b.set_flag("FLAG_HIDE_STORMS_EDGE_VOLTORB_1", False)
    b.set_var("VAR_ORLEANS_STORY", 10)
    v = obj_by_script("StormsEdge_Gym", "Voltorb4")
    b.warp("StormsEdge_Gym", v["x"], v["y"] + 1)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 30)
    for _ in range(80):
        if b.in_battle():
            break
        b.press("A", 4, 26)
    t.check("the buoy Voltorb battle starts", b.in_battle(), b.where())
    b.frames(60)
    force_outcome(b, 4, "HandleEndTurn_RanFromBattle")
    b.frames(90)
    mash_until(b, lambda: not b.in_battle() and b.script_status() == 2, 80, fight=False)
    t.check("after running from it, that Voltorb is still there", not b.flag("FLAG_HIDE_STORMS_EDGE_VOLTORB_1"), b.where())

    # ---------------------------------------------------------------- the nurse hint (every healer)
    b.warp("GrandOak_PokemonCenter", 7, 4)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 30)
    seen = ""
    for _ in range(80):
        seen += message(b) + "|"
        if choice_open(b):
            b.press("A", 4, 30)
        else:
            b.press("A", 4, 26)
        if b.script_status() == 2:
            break
    t.check("the nurse mentions the free beds", "beds are free" in seen, seen[-160:].replace("\n", "/"))

    # ---------------------------------------------------------------- the Frontier couple (pg S2)
    pair = obj_by_script("CrescentCity", "FrontierPair")
    b.set_var("VAR_ORLEANS_STORY", 30)
    talk(b, "CrescentCity", "FrontierPair")
    t.check("before the ending the couple still wait for the Frontier", "waiting for the Frontier" in message(b), message(b)[:60])
    b.advance_text()
    b.set_var("VAR_ORLEANS_STORY", 45)
    talk(b, "CrescentCity", "FrontierPair")
    t.check("after the ending the couple know it opened", "It opened" in message(b), message(b)[:60])
    b.advance_text()
