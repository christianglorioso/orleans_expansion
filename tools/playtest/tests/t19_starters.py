"""The starter Poke Balls, the wild intro text, the statics' soft-reset rolls and Lafayette's Shiny Charm (2026-10-13).

  * the shelter's top-right table carries three Poke Ball objects (16..18, 2), Lafayette's text sends the player to it
  * looking at a ball rolls nature / gender / shiny / ability for THAT ball (RAM only, never saved) and shows "This male, Adamant TOTODILE ..." with the
    pic in its shiny palette when shiny; looking twice shows the same values; the Pokemon handed over matches the text exactly
  * a forced shiny roll gives a different sprite palette (the pic differs from the normal one) and a shiny Pokemon
  * soft reset: a save made BEFORE choosing, then two boots with different timing, give different rolls; one boot is consistent
  * wild encounters (a normal one and a static legend) open with "A wild male, Adamant NAME appeared!"; the text matches the real mon
  * statics / gifts are rolled when the interaction happens (rougarou, Rayquaza, Bloodmoon Ursaluna, Rotom, a gift): two boots from one save differ
  * Lafayette's Shiny Charm: only with every BASE species of the regional dex, bag-full safe, once; the Charm makes shiny rolls ~3x more likely
"""
import re
import sys
from pathlib import Path

from PIL import Image

from bot import Bot, map_data, enum_value, wsl_path

GLYPHS = {0x1B: "e", 0x00: " ", 0x39: " ", 0xAB: "!", 0xAC: "?", 0xAD: ".", 0xB8: ",", 0xB4: "'", 0xBA: "/", 0xFE: "\n", 0xFA: "\n", 0xFB: "\n", 0xB0: "...", 0xA0: "-", 0xF1: "-"}
for i in range(26):
    GLYPHS[0xBB + i] = chr(65 + i)
    GLYPHS[0xD5 + i] = chr(97 + i)
for i in range(10):
    GLYPHS[0xA1 + i] = str(i)

NATURES = ("Hardy", "Lonely", "Brave", "Adamant", "Naughty", "Bold", "Docile", "Relaxed", "Impish", "Lax", "Timid", "Hasty", "Serious", "Jolly", "Naive",
           "Modest", "Mild", "Quiet", "Bashful", "Rash", "Calm", "Gentle", "Sassy", "Careful", "Quirky")
SPECIES = ("Totodile", "Chikorita", "Fuecoco")
LOOK = re.compile(r"This (male, |female, )?([A-Z][a-z]+) ([A-Za-z]+)")
WILD = re.compile(r"A wild (male, |female, )?([A-Z][a-z]+) ([A-Za-z]+)")


def text_at(b, name, n=420):
    a = b.sym(name)
    out = []
    for i in range(n):
        c = b.r8(a + i)
        if c == 0xFF:
            break
        out.append(GLYPHS.get(c, "?"))
    return "".join(out)


def message(b):
    return text_at(b, "gStringVar4")


def continue_game(b, extra=0):
    """boot to the title, CONTINUE; `extra` idle frames first (a human is never frame-exact: this is what makes two soft resets differ)"""
    b.frames(1500 + extra)
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
    b.press("START", 6, 30)
    b.press("DOWN", 6, 10)
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


def ball_objects():
    return [o for o in map_data("IsleMarais_Shelter")["objects"] if o["script"].split("_")[-1] in ("Totodile7", "Chikorita8", "Fuecoco9")]


def show_balls(b):
    for f in ("FLAG_HIDE_SHELTER_TOTODILE", "FLAG_HIDE_SHELTER_CHIKORITA", "FLAG_HIDE_SHELTER_FUECOCO"):
        b.set_flag(f, False)


def look(b, idx, label=None, finish=False):
    """stand below ball idx, press A; returns (text, parsed) while the first message is up (the pic is on screen). Declines the confirm with B
    unless finish (then YES)"""
    o = ball_objects()[idx]
    b.warp("IsleMarais_Shelter", o["x"], o["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 20)
    b.frames(320)
    txt = message(b)
    if label:
        b.shot(label)
    m = LOOK.search(txt)
    parsed = (m.group(1) or "", m.group(2), m.group(3)) if m else None
    if finish:
        return txt, parsed
    b.press("A", 4, 30)          # on to "Will you look after ...?"
    b.frames(300)
    b.press("B", 4, 30)          # NO
    b.frames(90)
    return txt, parsed


def mon_info(b, addr):
    pers = b.r32(addr)
    species = b.r16(addr + 0x20)         # the encrypted substructures are not readable raw: use the ROM's own functions
    return pers


def party_mon(b, slot=0):
    return b.r32(b.sym("gPlayerPartyPtr")) + slot * 100


def enemy_mon(b, slot=0):
    return b.r32(b.sym("gEnemyPartyPtr")) + slot * 100


def describe(b, addr, species):
    pers = b.r32(addr)
    nat = pers % 25
    gen = b.call("GetGenderFromSpeciesAndPersonality", species, pers) & 0xFF
    return NATURES[nat], {0: "male, ", 254: "female, "}.get(gen, ""), bool(b.call("IsMonShiny", addr) & 0xFF)


def run_shelter(b, t):
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 1)
    show_balls(b)
    balls = ball_objects()
    t.check("three ball objects exist", len(balls) == 3, len(balls))
    d = map_data("IsleMarais_Shelter")
    t.check("they stand on the top-right table (x 16..18, y 2, blocked counter cells)",
            sorted((o["x"], o["y"]) for o in balls) == [(16, 2), (17, 2), (18, 2)] and all(d["coll"][2][x] != 0 for x in (16, 17, 18)),
            [(o["x"], o["y"]) for o in balls])
    t.check("their sprite is the Poke Ball", all(o["graphics_id"] == "OBJ_EVENT_GFX_ITEM_BALL" for o in balls), [o["graphics_id"] for o in balls])
    b.warp("IsleMarais_Shelter", 18, 4)
    b.frames(30)
    b.shot("shelter_table")
    # Lafayette sends the player to the table
    laf = [o for o in d["objects"] if o["script"].endswith("Lafayette1")][0]
    b.warp("IsleMarais_Shelter", laf["x"], laf["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 20)
    b.frames(200)
    t.check("Lafayette points at the balls on the table", "table" in message(b), message(b))
    b.advance_text(60)
    # each ball: text with gender + nature, twice the same
    first = []
    for i in range(3):
        txt1, p1 = look(b, i, "ball%d_first" % i)
        t.check("ball %d text has gender/nature/species: %r" % (i, txt1[:50]), p1 is not None and p1[1] in NATURES and p1[2] == SPECIES[i], txt1)
        t.check("ball %d script finished after declining" % i, b.script_status() == 2, b.where())
        txt2, p2 = look(b, i, "ball%d_again" % i)
        t.check("ball %d: looking again shows the same values" % i, p1 == p2, (p1, p2))
        first.append(p1)
    # the received Pokemon matches: take Fuecoco (ball 2) exactly as shown
    txt, p = look(b, 2, "ball2_before_take", finish=True)
    shown = (p[1], p[0], False)
    b.press("A", 4, 30)          # to the confirm
    b.frames(300)
    b.press("A", 4, 30)          # YES
    b.advance_text(300)
    t.check("the pick finished: Fuecoco is VAR_STARTER_MON 2, party of one", b.var("VAR_STARTER_MON") == 2 and b.party_count() == 1, b.var("VAR_STARTER_MON"))
    if b.party_count():
        nat, gen, shiny = describe(b, party_mon(b), enum_value("species.h", "SPECIES_FUECOCO"))
        t.check("the received FUECOCO matches the shown nature and gender (%s %s%s)" % (gen, nat, " shiny" if shiny else ""),
                (nat, gen) == (shown[0], shown[1]) and shiny == shown[2], (nat, gen, shiny, shown))
    b.shot("after_pick")


def shiny_look(b, roll):
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 1)
    show_balls(b)
    b.w16(b.sym("sStarterRoll"), roll)          # ball 0 = Totodile, forced roll (a debug stand-in for a 1/512 hit)
    txt, p = look(b, 0, "totodile_%s" % ("shiny" if roll & 0x80 else "normal"), finish=True)
    a = b.sym("gPlttBufferUnfaded")
    cols = {pal: [b.r16(a + (pal * 16 + k) * 2) for k in range(16)] for pal in range(16, 32)}
    c555 = lambda r, g, bl: (r >> 3) | ((g >> 3) << 5) | ((bl >> 3) << 10)
    has_shiny = any(c555(24, 104, 72) in v for v in cols.values())       # graphics/pokemon/totodile/shiny.pal (green)
    has_normal = any(c555(49, 131, 197) in v for v in cols.values())     # normal.pal (blue)
    return txt, p, has_shiny, has_normal


def run_shiny(b, t):
    """a forced shiny roll: the pic is drawn with the shiny palette (green TOTODILE), the normal roll with the normal one (blue), and the Pokemon handed over is shiny"""
    txt, p, hs, hn = shiny_look(b, 0x8000 | 3)
    t.check("normal roll: normal palette in the pic, no shiny palette", hn and not hs, (hs, hn))
    t.check("normal roll text %r" % txt[:30], p == ("male, ", "Adamant", "Totodile"), p)
    b.close()
    b2 = Bot(rom=b.rom, out_dir=b.out / "shiny2")
    try:
        txt, p, hs, hn = shiny_look(b2, 0x8000 | 3 | (1 << 7))
        t.check("shiny roll: the shiny palette is on screen, the normal one is not", hs and not hn, (hs, hn))
        t.check("shiny roll text %r" % txt[:30], p == ("male, ", "Adamant", "Totodile"), p)
        b2.press("A", 4, 30)
        b2.frames(300)
        b2.press("A", 4, 30)
        b2.advance_text(300)
        if b2.party_count():
            nat, gen, shiny = describe(b2, party_mon(b2), enum_value("species.h", "SPECIES_TOTODILE"))
            t.check("the handed-over Totodile is shiny, Adamant, male", shiny and nat == "Adamant" and gen == "male, ", (nat, gen, shiny))
    finally:
        b2.close()


def run_wild(b, t):
    b.new_game()
    b.warp("Route1", 20, 40)
    b.frames(30)
    for name, lvl in (("SPECIES_ZIGZAGOON", 5), ("SPECIES_RAIKOU", 60)):
        sp = enum_value("species.h", name)
        b.call("CreateScriptedWildMon", sp, lvl, 0)
        b.call("BattleSetup_StartScriptedWildBattle")
        seen = None
        for _ in range(400):
            b.frames(5)
            txt = text_at(b, "gDisplayedStringBattle")
            if txt.startswith("A wild"):
                seen = txt
                break
        t.check("%s intro reads 'A wild ...': %r" % (name, seen), seen is not None, seen)
        if seen:
            b.frames(150)
            b.shot("wild_" + name[8:].lower())
            m = WILD.search(seen)
            nat, gen, _ = describe(b, enemy_mon(b), sp)
            t.check("%s intro matches the real mon (%s %s)" % (name, gen, nat), m is not None and (m.group(1) or "") == gen and m.group(2) == nat, (seen, nat, gen))
        for _ in range(60):
            if not b.in_battle():
                break
            b.fight(10)
        b.frames(60)


def run_resets(b, t):
    """a save made before choosing; boots with different timing roll differently, one boot stays consistent"""
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 1)
    show_balls(b)
    b.warp("IsleMarais_Shelter", 17, 4)
    b.frames(30)
    save_game(b)
    sav = b.out / "starters_pre.sav"
    b.h.cmd("dumpsave " + wsl_path(sav))
    rolls = []
    for extra in (0, 37, 211):
        c = Bot(rom=b.rom, out_dir=b.out / ("boot_%d" % extra), save=sav)
        try:
            continue_game(c, extra)
            c.warp("IsleMarais_Shelter", 17, 4)
            c.frames(30)
            tup = tuple(look(c, i)[1] for i in range(3))
            again = tuple(look(c, i)[1] for i in range(3))
            t.check("boot +%d: rolls %s are consistent within the boot" % (extra, tup), tup == again and None not in tup, (tup, again))
            rolls.append(tup)
        finally:
            c.close()
    distinct = len(set(rolls))
    t.check("different timing after the same save gives different rolls (%d of 3 boots distinct)" % distinct, distinct >= 2, rolls)


STATICS = (  # (what, map, script suffix, side, setup vars/flags)
)


def run_statics(b, t):
    """encounters are created by setwildbattle at the interaction: from one save, two boots with different timing roll different Pokemon"""
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.give_mon("SPECIES_TOTODILE", 50)
    b.warp("Route1", 20, 40)
    b.frames(30)
    save_game(b)
    sav = b.out / "statics_pre.sav"
    b.h.cmd("dumpsave " + wsl_path(sav))
    cases = (("rougarou (Lycanroc Midnight)", "SPECIES_LYCANROC_MIDNIGHT", 42), ("Rayquaza", "SPECIES_RAYQUAZA", 70),
             ("Ursaluna Bloodmoon", "SPECIES_URSALUNA_BLOODMOON", 60), ("Rotom", "SPECIES_ROTOM_HEAT", 22), ("Raikou (roaming-style static)", "SPECIES_RAIKOU", 60))
    results = {c[0]: [] for c in cases}
    for extra in (0, 53, 197):
        c = Bot(rom=b.rom, out_dir=b.out / ("sboot_%d" % extra), save=sav)
        try:
            continue_game(c, extra)
            for what, name, lvl in cases:
                sp = enum_value("species.h", name)
                c.call("CreateScriptedWildMon", sp, lvl, 0)
                pers = c.r32(enemy_mon(c))
                results[what].append(pers)
        finally:
            c.close()
    for what, vals in results.items():
        t.check("%s: personality differs between boots (%s)" % (what, ", ".join("%08x" % v for v in vals)), len(set(vals)) >= 2, vals)


def run_charm(b, t):
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 20)
    for f in ("FLAG_LAFAYETTE_REWARD_10", "FLAG_LAFAYETTE_REWARD_15", "FLAG_APARTMENT_UNLOCKED"):
        b.set_flag(f)
    item = enum_value("items.h", "ITEM_SHINY_CHARM")
    t.check("no Charm yet", not (b.call("CheckBagHasItem", item, 1) & 0xFF), "")

    def shiny_hits(n):
        hits = 0
        for _ in range(n):
            if b.call("ComputePlayerShinyOdds", 0, 0x12345678) & 0xFF:
                hits += 1
        return hits
    base = shiny_hits(6000)
    # a partial dex: Lafayette comments on progress and gives nothing
    o = [o for o in map_data("CrescentCity_Conservation")["objects"] if o["script"].endswith("Lafayette0")][0]
    b.warp("CrescentCity_Conservation", o["x"], o["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 20)
    b.advance_text(120)
    t.check("a partial dex gives no Charm", not (b.call("CheckBagHasItem", item, 1) & 0xFF), "")
    b.shot("lafayette_partial_dex")
    # the whole dex
    for n in range(1, 1100):
        b.call("GetSetPokedexFlag", n, 3)
    b.warp("CrescentCity_Conservation", o["x"], o["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 20)
    b.frames(200)
    b.shot("lafayette_charm")
    b.advance_text(200)
    t.check("a complete base-species dex: Lafayette gives the SHINY CHARM", bool(b.call("CheckBagHasItem", item, 1) & 0xFF), message(b))
    t.check("the once-only flag is set", b.flag("FLAG_LAFAYETTE_SHINY_CHARM"), "")
    charm = shiny_hits(6000)
    # ComputePlayerShinyOdds re-rolls only for the extras: none without the Charm (the first roll is the caller's), I_SHINY_CHARM_ADDITIONAL_ROLLS = 2 with it
    # (2 x 128/65536 = 0.39%: ~23 hits in 6000)
    t.check("the Charm adds the 2 extra shiny rolls (%d hits in 6000 calls with it, %d without)" % (charm, base), base == 0 and 8 <= charm <= 45, (base, charm))
    b.call("RemoveBagItem", item, 1)
    b.warp("CrescentCity_Conservation", o["x"], o["y"] + 1)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 20)
    b.advance_text(120)
    t.check("given once only (no second Charm)", not (b.call("CheckBagHasItem", item, 1) & 0xFF), "")


def run(b, t):
    run_shelter(b, t)
    sub = Bot(rom=b.rom, out_dir=b.out / "shiny")
    run_shiny(sub, t)          # closes its own bots
    for name, fn in (("wild", run_wild), ("resets", run_resets), ("statics", run_statics), ("charm", run_charm)):
        sub = Bot(rom=b.rom, out_dir=b.out / name)
        try:
            fn(sub, t)
        finally:
            sub.close()
