"""Phase-3 fix S (scripts + maps + text, audit/20_phase3_fix_plan.md S1-S9).

  S1  the shipped ROM holds the fixed text: every line the audit found drifting (Route 6 Tristan, the Pointe Rouge angler, the Route 10 swimmers, Cayenne's trial)
      is present in the ROM bytes and its old wording is gone; the source-vs-generated lint (tools/mapgen/gen_drift_check.py --fast) is clean
  S2  Fifolet's story-16 line no longer says the riverboat sails (read from the engine's string buffer)
  S3  the Grand Oak Pokemon Center's cushions and the Battle Frontier Center's are faced from every open side (rest menu opens, B backs out), and a
      rest cell no longer swallows the player (the cell blocks, the room stays connected)
  S4  Route 15 Trainer3 / Trainer5 and Route 20 Germain see more than one cell: the player stepping into the line is spotted
  S5  the Route 25 sign reads from its west cell; Tupelo at the Old Water ceremony answers from the water cell north of him
  S6  Chloe fights with Joltik + Elekid
  S7  Route 12's fishing table stays at or under Lutin's ace (43)
  S8  the Pry Bar's icon is no longer the Wailmer Pail placeholder
  S9  the Arena BP clerk's competitive shop: every description is at most two lines of the box (re-wrapped), none is empty
"""
import json
import re
from pathlib import Path

from bot import ROOT, enum_value, map_data

# ------------------------------------------------------------------ helpers
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


def charmap():
    cm = {}
    for line in (ROOT / "charmap.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("@ Hiragana"):
            break
        m = re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$", line)
        if m:
            cm[m.group(1)] = int(m.group(2), 16)
    cm["'"] = 0xB4          # the charmap writes it as ''' (escaped)
    return cm


def encode(text, cm):
    """a .string body (with the \\n / \\p escapes as written in the .inc) -> Gen 3 bytes, $ included"""
    out = bytearray()
    i = 0
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            out.append({"n": 0xFE, "p": 0xFB, "l": 0xFA}[text[i + 1]])
            i += 2
            continue
        out.append(0xFF if c == "$" else cm[c])
        i += 1
    return bytes(out)


def rom_has(rom, cm, text):
    return rom.find(encode(text, cm)) >= 0


def obj(mapname, suffix):
    for o in map_data(mapname)["objects"]:
        if o.get("script", "").endswith(suffix):
            return o
    raise KeyError(mapname + suffix)


def mon_data_ids():
    txt = (ROOT / "include" / "pokemon.h").read_text(errors="replace")
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


def turn(b, d):
    b.press({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[d], 2, 14)


def menu_open(b):
    return any("ultichoice" in str(x) or "esNo" in str(x) or "YesNo" in str(x) or "Menu" in str(x) for x in b.active_tasks())


def stand_cells(name, cells):
    """(stand x, y, face towards the cell) for every walkable neighbour (no object, no warp) of each rest cell"""
    d = map_data(name)
    busy = {(o["x"], o["y"]) for o in d["objects"]} | {(o["x"], o["y"]) for o in d["warps"]}
    out = []
    for x, y in cells:
        for dx, dy, face in ((0, 1, "U"), (0, -1, "D"), (-1, 0, "R"), (1, 0, "L")):
            sx, sy = x + dx, y + dy
            if 0 <= sx < d["width"] and 0 <= sy < d["height"] and d["coll"][sy][sx] == 0 and (sx, sy) not in busy:
                out.append(((x, y), (sx, sy), face))
    return out


def rest_cells(name):
    m = json.loads((ROOT / "data/maps" / name / "map.json").read_text(encoding="utf-8"))
    return [(e["x"], e["y"]) for e in m.get("bg_events", []) if e.get("script") == "Common_EventScript_RestSpot"]


def connected(name):
    """all walkable cells of an interior reach every warp / object-adjacent cell: flood fill from the first exit"""
    d = map_data(name)
    w, h, coll = d["width"], d["height"], d["coll"]
    start = (d["warps"][0]["x"], d["warps"][0]["y"])
    seen, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and (coll[n[1]][n[0]] == 0 or n in {(o["x"], o["y"]) for o in d["warps"]}):
                seen.add(n)
                todo.append(n)
    free = {(x, y) for y in range(h) for x in range(w) if coll[y][x] == 0}
    return free - seen


def trainer_spots(b, t, label, mapname, spot, lateral):
    """warp beside the sight line (the lateral cell), step into `spot`: the trainer must engage"""
    b.set_var("VAR_REPEL_STEP_COUNT", 250)
    b.give_item("ITEM_MAX_REPEL", 1)
    b.warp(mapname, *lateral)
    step = "".join(k for k, (dx, dy) in (("U", (0, -1)), ("D", (0, 1)), ("L", (-1, 0)), ("R", (1, 0)))
                   if (lateral[0] + dx, lateral[1] + dy) == spot)
    b.step(step)
    b.frames(120)
    spotted = b.script_status() != 2 or b.in_battle()
    t.check("%s spots the player at %s" % (label, spot), spotted, "script=%d battle=%s at %s" % (b.script_status(), b.in_battle(), b.where()))
    if spotted:
        b.advance_text(40)


def run(b, t):
    cm = charmap()
    rom = Path(b.rom).read_bytes()

    # ---------------------------------------------------------------- S1: the shipped text is the fixed text (and the source regenerates it)
    cases = [
        ("Route 6 Tristan: the current bends west", "The current bends west. It wants to\\ncarry you to the camp.$", "The current bends east"),
        ("Pointe Rouge angler: the river is a road", "The big ones hide under the bridges.\\nKINGFISHER says the river is a road.$", "river is a gift"),
        ("Route 10 Baptiste (n0) after-text", "The brothers' gumbo smell carries\\nall the way to the canal.$", None),
        ("Route 10 Celeste (n2) intro", "Big Lake is bigger than it looks.\\nDon't drown. Battle!$", None),
        ("Cayenne's trial is punctuated", "mirrors. Light them in order by day.\\p", "six mirrors\\nLight them in order, by day."),
    ]
    for name, new, old in cases:
        t.check("S1 %s" % name, rom_has(rom, cm, new), "new text in the ROM")
        if old:
            t.check("S1 %s: old wording gone" % name, not rom_has(rom, cm, old), old)
    # the Route 10 swimmers: Baptiste (a man, DOWN) says the lake road line, Celeste the "Big Lake" line (the lines belong to the right trainer)
    src = (ROOT / "tools/mapgen/story_data_ch6.py").read_text(encoding="utf-8")
    t.check("S1 story_data_ch6 carries the Route 10 swap", src.index("The lake road's open again!") < src.index('name="CELESTE"') < src.index("Big Lake is bigger than it looks."),
            "the source, not just Route10.inc")
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "tools/mapgen/gen_drift_check.py"), "--fast"], capture_output=True, text=True, cwd=str(ROOT))
    t.check("S1 gen_drift_check --fast: source and generated trainer/party/splice output agree", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    r = subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "tools/mapgen/story_lint.py")], capture_output=True, text=True, cwd=str(ROOT))
    t.check("S1 story_lint (text boxes + drift) is clean", r.returncode == 0, (r.stdout + r.stderr)[-300:])

    # ---------------------------------------------------------------- common setup
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    b.set_flag("FLAG_RECEIVED_HM_SURF", True)

    # ---------------------------------------------------------------- S2: Fifolet at story 16 and 17
    b.set_flag("FLAG_BADGE03_GET", True)
    b.set_flag("FLAG_RECEIVED_MIMIKYU", True)        # the gym rewards are done: the leader goes straight to his after-line
    o = obj("CrescentCity_Gym", "Fifolet0")

    def fifolet(story):
        b.set_var("VAR_ORLEANS_STORY", story)
        b.warp("CrescentCity_Gym", o["x"], o["y"] + 1)
        b.frames(20)
        b.face("U")
        b.press("A", 4, 30)
        b.frames(60)
        txt = ""
        for _ in range(20):
            txt = message(b, 300)
            if "riverboat" in txt:
                break
            b.press("A", 4, 26)
            b.frames(20)
        txt = message(b, 300)
        b.advance_text(30)
        return txt
    txt = fifolet(16)
    b.shot("fifolet16")
    t.check("S2 Fifolet at story 16 no longer says the riverboat sails now", "riverboat" in txt and "now sails" not in txt and "sails for" not in txt, repr(txt))
    t.check("S2 the story-16 line says it will sail once the Ward is sorted", "will sail" in txt, repr(txt))
    txt = fifolet(17)
    t.check("S2 at story 17 the riverboat line is the real one (the pass is the badge)", "riverboat" in txt and "will sail" not in txt, repr(txt))

    # ---------------------------------------------------------------- S3: the rest cushions are faced from every open side
    for room in ("GrandOak_PokemonCenter", "BattleFrontier_PokemonCenter_1F"):
        cells = rest_cells(room)
        d = map_data(room)
        t.check("S3 %s: every rest cell blocks (it is faced, never walked onto)" % room, all(d["coll"][y][x] != 0 for x, y in cells), cells)
        cut = connected(room)
        near = {(x + dx, y + dy) for x, y in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        t.check("S3 %s: blocking the rest cells cuts nothing off (cells unreachable from the exit: %s, none beside a rest cell)" % (room, sorted(cut)),
                not (cut & near), sorted(cut & near))
        spots = stand_cells(room, cells)
        t.check("S3 %s: every rest cell has a cell to be faced from" % room, {c for c, _, _ in spots} == set(cells), spots)
        for cell, (sx, sy), face in spots:
            b.warp(room, sx, sy)
            b.frames(20)
            b.face(face)
            b.press("A", 4, 20)
            b.frames(40)
            opened = b.script_status() != 2
            t.check("S3 %s: rest menu opens from (%d,%d) facing %s toward %s" % (room, sx, sy, face, cell), opened,
                    "status %d at %s" % (b.script_status(), b.where()))
            if room == "GrandOak_PokemonCenter" and (sx, sy) == (11, 4):
                b.shot("grandoak_rest_front")
            b.press("B", 4, 20)
            b.advance_text(20)
            b.frames(30)
    # walking toward a cushion no longer carries the player onto it
    b.warp("GrandOak_PokemonCenter", 11, 4)
    b.frames(20)
    b.step("D")
    b.frames(10)
    t.check("S3 pressing toward the Grand Oak cushion does not walk onto it", b.pos() == (11, 4), b.where())
    b.advance_text(10)

    # ---------------------------------------------------------------- S4: sight lines
    trainer_spots(b, t, "Route 15 Aurele (Trainer3, now facing east)", "Route15", (19, 14), (19, 13))
    b.warp("Route15", 5, 5)
    b.frames(10)
    trainer_spots(b, t, "Route 15 Remi (Trainer5, now facing west)", "Route15", (31, 22), (31, 21))
    b.warp("Route15", 5, 5)
    b.frames(10)
    trainer_spots(b, t, "Route 20 Germain (now facing west)", "Route20", (27, 8), (27, 7))
    for mapname, suffix in (("Route15", "Trainer3"), ("Route15", "Trainer5"), ("Route20", "Trainer4")):
        mv = next(o["movement_type"] for o in json.loads((ROOT / "data/maps" / mapname / "map.json").read_text(encoding="utf-8"))["object_events"]
                  if o.get("script", "").endswith(suffix))
        t.check("S4 %s %s faces along open ground (%s)" % (mapname, suffix, mv), mv.endswith(("LEFT", "RIGHT")), mv)

    # ---------------------------------------------------------------- S5: the Route 25 sign from the west, Tupelo from the water
    b.warp("Route25", 17, 6)
    b.frames(20)
    b.face("R")
    b.press("A", 4, 20)
    b.frames(40)
    t.check("S5 the Route 25 sign answers from its west cell", b.script_status() != 2, "status %d at %s" % (b.script_status(), b.where()))
    txt = message(b, 200)
    t.check("S5 the Route 25 sign text is the shrine sign", "OLDEST" in txt or "SHRINE" in txt, repr(txt))
    b.advance_text(20)
    b.set_var("VAR_OLD_WATER_CEREMONY", 3)
    b.set_flag("FLAG_HIDE_CER_TUPELO", False)
    b.warp("OldWater", 24, 28)
    b.frames(40)
    b.face("D")
    b.press("A", 4, 20)
    b.frames(40)
    b.shot("tupelo_from_water")
    t.check("S5 Tupelo answers from the water cell north of him (ceremony)", b.script_status() != 2, "status %d at %s" % (b.script_status(), b.where()))
    b.set_var("VAR_OLD_WATER_CEREMONY", 0)

    # ---------------------------------------------------------------- S6: Chloe's team
    b.set_var("VAR_ORLEANS_STORY", 8)
    o = obj("StormsEdge_Gym", "Electrician2")
    b.warp("StormsEdge_Gym", o["x"], o["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 30)
    for _ in range(20):
        if b.in_battle():
            break
        b.press("A", 4, 26)
        b.frames(10)
    if b.in_battle():
        b.frames(120)
        base = b.r32(b.sym("gEnemyPartyPtr"))
        got = [b.call("GetMonData2", base + k * 100, mon_data_ids()["MON_DATA_SPECIES"]) & 0xFFFF for k in range(2)]
        want = [enum_value("species.h", "SPECIES_JOLTIK"), enum_value("species.h", "SPECIES_ELEKID")]
        t.check("S6 Chloe's team is Joltik + Elekid", got == want, "%s vs %s" % (got, want))
        b.shot("chloe")
    else:
        t.check("S6 Chloe starts a battle", False, "no battle; %s" % b.where())

    # ---------------------------------------------------------------- S7: Route 12 fishing levels
    wild = json.loads((ROOT / "src/data/wild_encounters.json").read_text(encoding="utf-8"))
    tab = None
    for g in wild["wild_encounter_groups"]:
        for e in g["encounters"]:
            if e.get("base_label") == "gRoute12_Orleans":
                tab = e["fishing_mons"]["mons"]
    top = max(m["max_level"] for m in tab)
    t.check("S7 Route 12 fishing (source) tops out at 43 or less", top <= 43, top)
    sym = None
    for name in ("gRoute12_OrleansFishingMons_Day", "gRoute12_OrleansFishingMons", "gRoute12_Orleans_FishingMons"):
        try:
            sym = b.sym(name)
            break
        except Exception:
            continue
    if sym is not None:
        lv = [b.r8(sym + 4 * k + 1) for k in range(10)]        # struct WildPokemon { u8 minLevel; u8 maxLevel; u16 species; }
        t.check("S7 the compiled Route 12 fishing table tops out at 43 or less", max(lv) <= 43, lv)
    else:
        t.note("S7: the compiled fishing table symbol was not found; the source check stands")

    # ---------------------------------------------------------------- S8: the Pry Bar's icon
    import struct
    base = b.sym("gItemsInfo") - 0x08000000
    pry, sword = enum_value("items.h", "ITEM_PRY_BAR"), enum_value("items.h", "ITEM_RUSTED_SWORD")
    def pointers(sym):
        needle = struct.pack("<I", b.sym(sym))
        return [i for i in range(base, base + 250_000, 4) if rom[i:i + 4] == needle]
    sw = pointers("gItemIcon_RustedSword")
    wp = pointers("gItemIcon_WailmerPail")
    stride = (sw[1] - sw[0]) // (pry - sword) if len(sw) >= 2 and sword < pry else 0
    t.check("S8 the Pry Bar entry uses the rusted-sword icon (two gItemsInfo entries point at it, %d entries apart)" % (pry - sword),
            len(sw) == 2 and stride > 0 and (sw[1] - sw[0]) == stride * (pry - sword), "positions %s" % sw)
    entry = base + pry * stride
    t.check("S8 the Pry Bar entry no longer holds the Wailmer Pail icon pointer", stride > 0 and not any(entry <= p < entry + stride for p in wp),
            "pry entry %d..%d, pail pointers at %s" % (entry, entry + stride, wp))

    # ---------------------------------------------------------------- S9: the Arena BP clerk's descriptions
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.warp("BattleFrontier_BattleArenaLobby", 8, 10)
    b.frames(40)
    b.set_var("VAR_0x8004", 5000)
    b.call("GiveFrontierBattlePoints")
    b.face("U")
    b.press("A", 4, 20)
    b.frames(30)
    for _ in range(25):
        if any("ultichoice" in str(x) or "Scroll" in str(x) for x in b.active_tasks()):
            break
        b.press("A", 4, 26)
    b.frames(30)
    rows, longest = [], 0
    for k in range(48):
        b.frames(14)
        txt = message(b, 240)
        rows.append(txt)
        longest = max(longest, txt.count("\n") + 1)
        if k in (6, 7, 8, 22):
            b.shot("bp_row%d" % k)
        b.press("DOWN", 4, 6)
    shown = [r for r in rows if r]
    t.check("S9 every competitive-shop row has a description (%d rows read)" % len(shown), len(shown) >= 46, len(shown))
    t.check("S9 no description needs more than two lines of the box", longest <= 2, "longest %d lines; e.g. %r" % (longest, max(rows, key=lambda r: r.count("\n"))))
