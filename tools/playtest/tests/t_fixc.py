"""Audit fix C (dex + engine): NPC palette tags and the worker sprite's palette, Champions move values, Oinkologne-F data, the pre-evolution
moves in the relearner, every source of the 10 formerly unobtainable species (Feebas, Duraludon, Vanillite, Beldum), Rotom/rougarou retiring
only on a catch, and the legend raid intros (no "PKMN TRAINER", no player-lookalike pic)."""
import json
from pathlib import Path

from bot import ROOT, enum_value

PAL_RAM = "gPlttBufferUnfaded"


def sp(n):
    return enum_value("species.h", n)


def mv(n):
    return enum_value("moves.h", n)


def obj_of(mapname, script):
    d = json.loads((ROOT / "data/maps" / mapname / "map.json").read_text(encoding="utf-8"))
    for o in d["object_events"]:
        if o["script"] == script:
            return o
    raise KeyError(script)


def spots(name, nx, ny):
    """(x, y, facing) cells from which an object can be talked to: next to it, or across one counter tile"""
    from bot import map_data
    d = map_data(name)
    res = []
    for dx, dy, face in ((0, 1, "U"), (0, -1, "D"), (-1, 0, "R"), (1, 0, "L")):
        for dist in (1, 2):
            x, y = nx + dx * dist, ny + dy * dist
            if not (0 <= x < d["width"] and 0 <= y < d["height"]):
                break
            if d["coll"][y][x] == 0 and (dist == 1 or d["coll"][ny + dy][nx + dx] != 0):
                res.append((x, y, face))
                break
    return res


def talk(b, mapname, script, frames=200):
    """walk next to the object (across a counter if needed) and press A on it"""
    o = obj_of(mapname, script)
    for x, y, face in spots(mapname, o["x"], o["y"]):
        if b.goto(x, y):
            b.face(face)
            b.press("A", 4, 20)
            return True
    return False


def md(name):
    """value of a MON_DATA_* enumerator (include/pokemon.h: enum MonData, counted in order)"""
    import re
    n, on = 0, False
    for l in (ROOT / "include/pokemon.h").read_text(errors="replace").splitlines():
        if not on:
            on = "enum MonData" in l
            continue
        m = re.match(r"\s+(MON_DATA_\w+)\s*(=\s*\w+)?,", l)
        if m:
            if m.group(1) == name:
                return n
            n += 1
    raise KeyError(name)


def money(b):
    return b.call("GetMoney", b.save1() + 0x490)


def decode(raw):
    out = ""
    for c in raw:
        if c == 0xFF:
            break
        if 0xBB <= c <= 0xD4:
            out += chr(ord("A") + c - 0xBB)
        elif 0xD5 <= c <= 0xEE:
            out += chr(ord("a") + c - 0xD5)
        elif c == 0:
            out += " "
        else:
            out += "."
    return out


def pal_hw(path):
    lines = Path(path).read_text().split()
    n = int(lines[2])
    vals = list(map(int, lines[3:3 + 3 * n]))
    out = []
    for i in range(n):
        r, g, bl = vals[3 * i:3 * i + 3]
        out.append((r >> 3) | ((g >> 3) << 5) | ((bl >> 3) << 10))
    return out


def gfx_id(name):
    import re
    n = 0
    for l in (ROOT / "include/constants/event_objects.h").read_text(errors="replace").splitlines()[26:420]:
        m = re.match(r"\s+(OBJ_EVENT_GFX_\w+)\s*(=\s*[\w ]+)?,", l)
        if m:
            if m.group(1) == name:
                return n
            n += 1
    raise KeyError(name)


def sprite_palette(b, mapname, gfx_const):
    """the 16 palette-RAM colours of the first object on the map drawn with gfx_const, plus its palette number"""
    gid = gfx_id(gfx_const)
    base = b.sym("gObjectEvents")
    for i in range(16):
        e = base + i * 0x24
        if (b.r8(e) & 1) and b.r16(e + 4) == gid:
            spr = b.sym("gSprites") + b.r8(e + 0x23) * 0x44
            pn = (b.r16(spr + 4) >> 12) & 15
            ram = b.sym(PAL_RAM) + (256 + pn * 16) * 2
            return pn, [b.r16(ram + 2 * k) for k in range(16)]
    return None, None


def sample_species(b, fn, n, *args):
    seen = {}
    for _ in range(n):
        if b.call(fn, *args) & 0xFF:
            s = b.call("GetMonData2", b.r32(b.sym("gEnemyPartyPtr")), md("MON_DATA_SPECIES")) & 0xFFFF
            seen[s] = seen.get(s, 0) + 1
    return seen


def run(b, t):
    b.new_game()

    # ---------------------------------------------------------------- engine: NPC palettes, worker sprite
    b.set_var("VAR_ORLEANS_STORY", 20)
    b.warp("StormsEdge_Pokecenter", 4, 5)
    b.frames(30)
    pn, cols = sprite_palette(b, "StormsEdge_Pokecenter", "OBJ_EVENT_GFX_WORKER_M")
    t.check("the line worker (WorkerM) is on the map with a palette slot", cols is not None, pn)
    if cols:
        green = pal_hw(ROOT / "graphics/object_events/palettes/npc_green.pal")
        white = pal_hw(ROOT / "graphics/object_events/palettes/npc_white.pal")
        t.check("WorkerM draws with the npc_green palette (not blank/other)", cols[1:] == green[1:], "%s vs %s" % (cols[:6], green[:6]))
        t.check("WorkerM is not using the npc_white palette", cols[1:] != white[1:])
    b.shot("worker")
    b.warp("StormsEdge", 20, 19)
    b.frames(30)
    pn, cols = sprite_palette(b, "StormsEdge", "OBJ_EVENT_GFX_WORKER_F")
    if cols:
        blue_or_pink = [pal_hw(ROOT / "graphics/object_events/palettes/npc_%s.pal" % c) for c in ("green", "blue", "pink", "white")]
        t.check("WorkerF (Eclair) palette is loaded (one of the NPC colour palettes)", any(cols[1:] == p[1:] for p in blue_or_pink), cols[:6])
    b.shot("eclair")

    # ---------------------------------------------------------------- Champions values (the sheet's 22 values + 5 flags)
    gm = b.sym("gMovesInfo")
    w = b.r32(gm - 4 + 64 * mv("MOVE_POUND") + 12)   # entry k starts at gm - 4 + 64k (probed: 3 pointers then the bit-field words)
    t.check("MoveInfo layout probe: Pound has power 40", (w >> 23) & 0x1FF == 40, hex(w))

    def info(m):
        e = gm - 4 + 64 * mv(m)
        w8, wc, w10 = b.r32(e + 12), b.r32(e + 16), b.r32(e + 24)
        return dict(power=(w8 >> 23) & 0x1FF, type=(w8 >> 16) & 31, acc=wc & 0x7F, pp=(wc >> 16) & 0xFF, sound=(w10 >> 24) & 1, slicing=(w10 >> 29) & 1)

    want = {"MOVE_PROTECT": (0, 0, 5), "MOVE_SLASH": (80, 100, 20), "MOVE_PSYSHIELD_BASH": (90, 90, 10), "MOVE_BEAK_BLAST": (120, 100, 5),
            "MOVE_SANDSTORM": (0, 0, 5), "MOVE_ANCHOR_SHOT": (90, 100, 20), "MOVE_NIGHT_SLASH": (70, 100, 20), "MOVE_CRABHAMMER": (100, 95, 10),
            "MOVE_MAKE_IT_RAIN": (120, 95, 5), "MOVE_SYRUP_BOMB": (60, 90, 10), "MOVE_BLOOD_MOON": (130, 100, 5), "MOVE_FISHIOUS_REND": (80, 100, 10),
            "MOVE_SNOWSCAPE": (0, 0, 5), "MOVE_SPIKY_SHIELD": (0, 0, 5), "MOVE_FIRE_LASH": (90, 100, 15), "MOVE_FIRST_IMPRESSION": (100, 100, 10),
            "MOVE_INFERNAL_PARADE": (65, 100, 15), "MOVE_REVELATION_DANCE": (100, 100, 15), "MOVE_SPIRIT_SHACKLE": (90, 100, 10)}
    bad = []
    for m, (pw, acc, pp) in want.items():
        i = info(m)
        if (i["power"], i["acc"], i["pp"]) != (pw, acc, pp):
            bad.append((m, (i["power"], i["acc"], i["pp"]), (pw, acc, pp)))
    t.check("Champions power/accuracy/PP for 19 moves (the sheet's values)", not bad, bad)
    t.check("Growth is a Grass move", info("MOVE_GROWTH")["type"] == enum_value("pokemon.h", "TYPE_GRASS"), info("MOVE_GROWTH"))
    for m in ("MOVE_DRAGON_CLAW", "MOVE_CRUSH_CLAW", "MOVE_METAL_CLAW", "MOVE_SHADOW_CLAW"):
        t.check("%s is a slicing move" % m, info(m)["slicing"] == 1, info(m))
    t.check("Dragon Cheer is a sound move", info("MOVE_DRAGON_CHEER")["sound"] == 1, info("MOVE_DRAGON_CHEER"))
    t.check("control: Slash slicing, Pound not", info("MOVE_SLASH")["slicing"] == 1 and info("MOVE_POUND")["slicing"] == 0)

    # ---------------------------------------------------------------- Oinkologne-F carries the sheet's single Oinkologne
    m_hp, f_hp = (b.call("GetSpeciesBaseHP", sp(s)) & 0xFF for s in ("SPECIES_OINKOLOGNE_M", "SPECIES_OINKOLOGNE_F"))
    t.check("Oinkologne-F has the male form's base HP (110)", m_hp == f_hp == 110, (m_hp, f_hp))
    ab_m, ab_f = (b.call("GetSpeciesAbility", sp(s), 0) & 0xFFFF for s in ("SPECIES_OINKOLOGNE_M", "SPECIES_OINKOLOGNE_F"))
    t.check("Oinkologne-F has the male form's first ability (Lingering Aroma)", ab_m == ab_f, (ab_m, ab_f))

    # ---------------------------------------------------------------- the engine switch: pre-evolution moves in the relearner
    cfg = (ROOT / "include/config/summary_screen.h").read_text()
    t.check("P_PRE_EVO_MOVES is TRUE", "#define P_PRE_EVO_MOVES            TRUE" in cfg)
    b.give_mon("SPECIES_SKELEDIRGE", 100)
    party = b.r32(b.sym("gPlayerPartyPtr"))
    mon = party + 100 * (b.party_count() - 1)
    # blank the four moves of the Level 100 Skeledirge so only the relearner list matters; Ember is a Fuecoco/Crocalor move
    for slot in range(4):
        b.call("SetMonMoveSlot", mon, mv("MOVE_TACKLE") if slot == 0 else 0, slot)
    buf = b.sym("gDisplayedStringBattle")   # scratch buffer (u8[~300]) used as the output list
    lst = buf
    n = b.call("GetRelearnerLevelUpMoves", mon, lst) if "GetRelearnerLevelUpMoves" in b.syms.addr else None
    if n is not None:
        moves = [b.r16(lst + 2 * i) for i in range(n & 0xFF)]
        pre = [m for m in ("MOVE_EMBER", "MOVE_SCARY_FACE", "MOVE_LEER") if mv(m) in moves]
        t.check("Skeledirge's relearner offers a pre-evolution (Fuecoco/Crocalor) move", bool(pre), [hex(m) for m in moves][:20])
    else:
        t.check("relearner has level-up moves for an evolved mon", bool(b.call("CanBoxMonRelearnMoves", mon, 0) & 0xFF))

    # ---------------------------------------------------------------- Feebas: Route 5 super rod (day), Duraludon: Route 3 night land
    night_json = json.loads((ROOT / "src/data/wild_encounters.json").read_text(encoding="utf-8"))
    hdrs = {e["base_label"]: e for e in night_json["wild_encounter_groups"][0]["encounters"]}
    t.check("Route 3 night land table holds Duraludon", any(m["species"] == "SPECIES_DURALUDON" for m in hdrs["gRoute3_Orleans_Night"]["land_mons"]["mons"]))
    t.check("Route 5 day fishing holds Feebas", any(m["species"] == "SPECIES_FEEBAS" for m in hdrs["gRoute5_Orleans"]["fishing_mons"]["mons"]))
    t.check("Route 13 and the Hollow water sit at the ch6 levels (<= 42)",
            max(m["max_level"] for m in hdrs["gRoute13_Orleans"]["land_mons"]["mons"]) <= 42 and
            max(m["max_level"] for m in hdrs["gLutinsHollow_Orleans"]["water_mons"]["mons"]) <= 42)

    # ---------------------------------------------------------------- Vanillite at the ice cream stand
    b.set_flag("FLAG_BADGE03_GET")
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.warp("CrescentCity_IceCream", 4, 6)
    o = obj_of("CrescentCity_IceCream", "CrescentCity_IceCream_EventScript_Clerk0")
    b.call("AddMoney", b.save1() + 0x490, 5000)
    before = b.party_count()
    t.check("reached the clerk", talk(b, "CrescentCity_IceCream", "CrescentCity_IceCream_EventScript_Clerk0"))
    b.advance_text(200)
    b.frames(30)
    got_van = b.flag("FLAG_RECEIVED_VANILLITE")
    t.check("the ice cream clerk sells a VANILLITE (flag set, party grew, 2500 spent)", got_van and b.party_count() == before + 1, "flag=%s party=%d money=%d" % (got_van, b.party_count(), money(b)))
    b.shot("vanillite")

    # ---------------------------------------------------------------- Beldum from Lafayette after the shrine (story 43+)
    b.set_var("VAR_ORLEANS_STORY", 43)
    b.warp("CrescentCity_Conservation", 4, 6)
    o = obj_of("CrescentCity_Conservation", "CrescentCity_Conservation_EventScript_Lafayette0")
    before = b.party_count()
    t.check("reached Lafayette", talk(b, "CrescentCity_Conservation", "CrescentCity_Conservation_EventScript_Lafayette0"))
    b.advance_text(200)
    b.frames(30)
    t.check("Lafayette gives the BELDUM after the shrine fight", b.flag("FLAG_RECEIVED_BELDUM_GIFT") and b.party_count() == before + 1,
            "flag=%s party=%d" % (b.flag("FLAG_RECEIVED_BELDUM_GIFT"), b.party_count()))

    # ---------------------------------------------------------------- Rotom: a KO leaves it in place
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.warp("CrescentCity_Dept1f", 4, 6)
    o = obj_of("CrescentCity_Dept1f", "CrescentCity_Dept1f_EventScript_RotomTv2")
    t.check("reached the Rotom", talk(b, "CrescentCity_Dept1f", "CrescentCity_Dept1f_EventScript_RotomTv2"))
    b.advance_text(400)
    b.frames(30)
    t.check("a KO'd Rotom is not retired (flag unset, script ended)", not b.flag("FLAG_CRESCENT_ROTOM_TV") and b.script_status() == 2, "flag=%s" % b.flag("FLAG_CRESCENT_ROTOM_TV"))

    # ---------------------------------------------------------------- legend raid intro text
    b.set_var("VAR_ORLEANS_STORY", 39)
    b.set_flag("FLAG_RECEIVED_DIVING_GEAR")
    b.set_flag("FLAG_TEMPLE_DOOR_OPEN")
    b.warp("LandsEnd_DrownedTemple", 9, 6)
    b.face("U")
    b.press("A", 4, 20)
    seen = set()
    for _ in range(260):
        b.press("A", 4, 14)
        if b.in_battle():
            seen.add(decode([b.r8(b.sym("gDisplayedStringBattle") + i) for i in range(80)]))
    txt = " | ".join(sorted(seen))
    t.check("Kyogre raid opens without 'TRAINER' (empty class)", seen and "TRAINER" not in txt, txt[:200])
    t.check("Kyogre raid intro reads 'bars the way'", "bars the way" in txt, txt[:200])
    b.shot("kyogre_intro")
    run_ex_items(b, t)
    run_type_icons(b, t)
    run_feebas(b, t)


def run_ex_items(b, t):  # called at the end of run()
    """SoulGold's EX vitamins: Calcium EX maxes the Sp. Atk EV (252), respects the 510 total cap, and does nothing at 252."""
    b.new_game()
    b.give_mon("SPECIES_PIKACHU", 50)
    party = b.r32(b.sym("gPlayerPartyPtr"))
    mon = party + 100 * (b.party_count() - 1)
    MON_DATA_SPATK_EV = md("MON_DATA_SPATK_EV")
    MON_DATA_HP_EV = md("MON_DATA_HP_EV")
    ex = enum_value("items.h", "ITEM_CALCIUM_EX")
    t.check("ITEM_CALCIUM_EX is a real item (id 917+)", ex >= 917, ex)
    # blank EVs, then use the item the way the party menu does (ItemUseOutOfBattle -> PokemonUseItemEffects)
    ok = b.call("PokemonUseItemEffects", mon, ex, 0, 0, 0)
    spatk = b.call("GetMonData2", mon, MON_DATA_SPATK_EV) & 0xFF
    t.check("Calcium EX maxes the Sp. Atk EV from 0 (252)", spatk == 252, spatk)
    again = b.call("PokemonUseItemEffects", mon, ex, 0, 0, 0) & 0xFF
    t.check("a second Calcium EX at 252 is refused (item not used)", again == 1, again)
    # total cap: 252 Sp. Atk + 252 HP + 6 left -> Carbos EX raises Speed by only the 6 that remain
    hp = b.call("PokemonUseItemEffects", mon, enum_value("items.h", "ITEM_HP_UP_EX"), 0, 0, 0)
    spe = b.call("PokemonUseItemEffects", mon, enum_value("items.h", "ITEM_CARBOS_EX"), 0, 0, 0)
    ev_spd = b.call("GetMonData2", mon, md("MON_DATA_SPEED_EV")) & 0xFF
    ev_hp = b.call("GetMonData2", mon, MON_DATA_HP_EV) & 0xFF
    t.check("HP Up EX then Carbos EX respect the 510 total (HP 252, Speed 6)", ev_hp == 252 and ev_spd == 6, (ev_hp, ev_spd))
    tot = sum(b.call("GetMonData2", mon, MON_DATA_HP_EV + k) & 0xFF for k in range(6))
    t.check("total EVs are exactly 510", tot == 510, tot)
    cfg = (ROOT / "include/config/battle.h").read_text(encoding="utf-8", errors="replace")
    t.check("B_SHOW_TYPES is SHOW_TYPES_ALWAYS and B_SHOW_EFFECTIVENESS stays SEEN", "#define B_SHOW_TYPES               SHOW_TYPES_ALWAYS" in cfg and "#define B_SHOW_EFFECTIVENESS        SHOW_EFFECTIVENESS_SEEN" in cfg)


def run_type_icons(b, t):  # called at the end of run()
    """B_SHOW_TYPES = SHOW_TYPES_ALWAYS: in a double wild battle against two Orleanian regional forms (altered types), the type icons
    appear next to the HP bars while choosing the target. Verified by comparing the target-selection screen with the one a turn
    earlier (the icons are sprites drawn only then) and by saving both shots for a human look."""
    b.new_game()
    b.give_mon("SPECIES_PIKACHU", 30)
    b.give_mon("SPECIES_PIDGEY", 30)
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.warp("Route3", 20, 30)
    b.frames(30)
    b.call("CreateScriptedDoubleWildMon", sp("SPECIES_SPEAROW_ORLEANIAN"), 20, 0, sp("SPECIES_VOLTORB_ORLEANIAN"), 20, 0)
    b.call("BattleSetup_StartScriptedDoubleWildBattle")
    main_func = b.sym("gBattleMainFunc")
    sel = b.syms.call_addr("HandleTurnActionSelectionState") & ~1
    for _ in range(900):
        if (b.r32(main_func) & ~1) == sel:
            break
        b.press("A", 4, 20)
    b.frames(30)
    t.check("the double battle reached the action menu", (b.r32(main_func) & ~1) == sel)
    b.shot("menu")
    base = b.screen_hash()
    b.press("A", 4, 30)      # FIGHT
    b.frames(20)
    b.press("A", 4, 30)      # the first move (Psychic): a double battle asks for a target
    b.frames(40)
    b.shot("target_select")
    t.check("target selection screen differs from the move menu (a target cursor and type icons appear)", b.screen_hash() != base)


def run_feebas(b, t):  # last: every FishingWildEncounter call starts a battle
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 30)
    b.set_clock(12, 0, 1)
    b.warp("Route5", 20, 30)
    b.frames(20)
    fish = sample_species(b, "FishingWildEncounter", 600, 2)
    b.w8(b.sym("gMain") + 0x439, b.r8(b.sym("gMain") + 0x439) & ~2)      # the sampling left gMain.inBattle set
    b.set_clock(23, 0, 1)
    b.warp("Route3", 20, 30)
    b.frames(30)
    t.check("Feebas turns up on the Route 5 super rod by day (%s)" % {k: v for k, v in fish.items() if k == sp("SPECIES_FEEBAS")}, sp("SPECIES_FEEBAS") in fish, len(fish))
