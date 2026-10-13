"""Wild held items (2026-10-13): every competitive held item has a wild source (data lint), the 5% itemRare slot really applies, the wild intro announces the
held item ("It's holding an Oran Berry."), a Thief on the wild Pokemon takes it, trainer battles do not announce.

  * lint: tools/dex/wild_held_items.py (every listed item farmable from a species that appears in Orleans' wild tables)
  * rate: SetWildMonHeldItem on the Wacan Berry species (itemCommon none, itemRare Wacan Berry): ~5% hold it, none hold anything else
  * intro: a wild mon with a forced held item (CreateScriptedWildMon takes an item): the intro text names it, with a/an; none for an item-less one; one announcement only
  * Thief: a level-40 Totodile with Thief takes the wild mon's Leftovers
"""
import re
import sys
from pathlib import Path

from bot import ROOT, enum_value

sys.path.insert(0, str(ROOT / "tools" / "dex"))

GLYPHS = {0x1B: "e", 0x00: " ", 0x39: " ", 0xAB: "!", 0xAC: "?", 0xAD: ".", 0xB8: ",", 0xB4: "'", 0xBA: "/", 0xFE: "\n", 0xFA: "\n", 0xFB: "\n", 0xB0: "...", 0xA0: "-", 0xF1: "-"}
for i in range(26):
    GLYPHS[0xBB + i] = chr(65 + i)
    GLYPHS[0xD5 + i] = chr(97 + i)
for i in range(10):
    GLYPHS[0xA1 + i] = str(i)


def text_at(b, name, n=420):
    a = b.sym(name)
    out = []
    for i in range(n):
        c = b.r8(a + i)
        if c == 0xFF:
            break
        out.append(GLYPHS.get(c, "?"))
    return "".join(out)


def mon_data_id(name):
    txt = (ROOT / "include/pokemon.h").read_text(errors="replace")
    body = txt[txt.index("enum MonData {") + 14:]
    body = body[:body.index("};")]
    ids = [m.group(1) for m in re.finditer(r"^\s*(MON_DATA_[A-Z0-9_]+)\s*,", body, re.M)]
    return ids.index(name)


def item_name(item):
    txt = (ROOT / "src/data/items.h").read_text(errors="replace")
    m = re.search(r"\[%s\]\s*=\s*\{\s*\.name\s*=\s*ITEM_NAME\(\"([^\"]+)\"\)" % item, txt)
    return m.group(1)


def enemy_mon(b, slot=0):
    return b.r32(b.sym("gEnemyPartyPtr")) + slot * 100


def start_wild(b, species, level, item=0, harmless=False):
    b.call("CreateScriptedWildMon", enum_value("species.h", species), level, enum_value("items.h", item) if item else 0)
    if harmless:                                   # the foe only splashes: the Thief test must not depend on its moves (sleep, rain, crits)
        for slot in range(4):
            b.call("SetMonMoveSlot", enemy_mon(b), enum_value("moves.h", "MOVE_SPLASH"), slot)
    b.call("BattleSetup_StartScriptedWildBattle")


def intro_text(b):
    for _ in range(400):
        b.frames(5)
        txt = text_at(b, "gDisplayedStringBattle")
        if txt.startswith("A wild"):
            return txt
    return None


def leave_battle(b):
    for _ in range(80):
        if not b.in_battle():
            break
        b.fight(10)
    b.frames(60)


def run(b, t):
    # ---- data lint
    import wild_held_items
    src = wild_held_items.sources()
    missing = [i for i in wild_held_items.ITEMS if i not in src]
    t.check("every competitive held item has a wild source (%d items)" % len(wild_held_items.ITEMS), not missing, missing)
    t.check("the checked set covers the core items (Life Orb, Choice x3, Assault Vest, Leftovers, Focus Sash, Rocky Helmet, Eviolite, Boots, Weakness Policy, plates)",
            all(i in src for i in ("LIFE_ORB", "CHOICE_BAND", "CHOICE_SPECS", "CHOICE_SCARF", "ASSAULT_VEST", "LEFTOVERS", "FOCUS_SASH", "ROCKY_HELMET", "EVIOLITE",
                                   "HEAVY_DUTY_BOOTS", "WEAKNESS_POLICY", "FLAME_PLATE", "SPLASH_PLATE", "OCCA_BERRY")), "")
    b.new_game()
    b.warp("Route1", 20, 40)
    b.frames(30)
    # ---- the 5% slot
    held_id = mon_data_id("MON_DATA_HELD_ITEM")
    rate_species, rate_slot, _ = src["WACAN_BERRY"][0]
    wacan = enum_value("items.h", "ITEM_WACAN_BERRY")
    n, hit, other = 2500, 0, 0
    for _ in range(n):
        b.call("CreateScriptedWildMon", enum_value("species.h", "SPECIES_" + rate_species), 5, 0)
        b.call("SetWildMonHeldItem")
        it = b.call("GetMonData2", enemy_mon(b), held_id) & 0xFFFF
        if it == wacan:
            hit += 1
        elif it:
            other += 1
    t.check("%s holds its Wacan Berry about 5%% of the time (%d of %d), nothing else (it has no common item)" % (rate_species, hit, n), rate_slot == "5%" and 80 <= hit <= 175 and other == 0, (hit, other))
    # ---- the intro
    start_wild(b, "SPECIES_ZIGZAGOON", 5, "ITEM_ORAN_BERRY")
    txt = intro_text(b)
    t.check("a held Oran Berry is announced with 'an': %r" % txt, txt is not None and "It's holding an Oran Berry." in txt and txt.count("holding") == 1, txt)
    b.frames(150)
    b.press("A", 4, 30)
    b.frames(200)
    b.shot("intro_oran_berry_page2")
    leave_battle(b)
    start_wild(b, "SPECIES_ZIGZAGOON", 5, "ITEM_LEFTOVERS")
    txt = intro_text(b)
    t.check("a held Leftovers is announced with 'a': %r" % txt, txt is not None and "It's holding a Leftovers." in txt, txt)
    b.frames(150)
    b.press("A", 4, 30)
    b.frames(200)
    b.shot("intro_leftovers_page2")
    leave_battle(b)
    start_wild(b, "SPECIES_ZIGZAGOON", 5, "ITEM_WEAKNESS_POLICY")
    txt = intro_text(b)
    t.check("the longest names still read: %r" % txt, txt is not None and "It's holding a Weakness Policy." in txt, txt)
    b.frames(150)
    b.press("A", 4, 30)
    b.frames(200)
    b.shot("intro_weakness_policy_page2")
    leave_battle(b)
    # a species with no common/rare item of its own (Zigzagoon holds a Potion half the time: SetWildMonHeldItem rolls it at battle start)
    start_wild(b, "SPECIES_WAILMER", 5, 0)
    txt = intro_text(b)
    t.check("no item: no announcement: %r" % txt, txt is not None and "holding" not in txt, txt)
    b.frames(200)
    b.shot("intro_no_item")
    leave_battle(b)
    # ---- Thief takes it
    b.give_mon("SPECIES_TOTODILE", 40)
    for slot in range(4):
        b.set_move(slot, "MOVE_THIEF", 0)          # whichever move the cursor lands on is Thief
    b.force_win = False
    start_wild(b, "SPECIES_WAILORD", 20, "ITEM_LEFTOVERS", harmless=True)
    intro_text(b)
    stolen = False
    for _ in range(160):
        b.press("A", 4, 40)
        txt = text_at(b, "gDisplayedStringBattle")
        if "stole the wild Wailord's" in txt and "Leftovers" in txt:
            stolen = True
            break
        if not b.in_battle():
            break
    t.check("Thief takes the wild mon's held item (battle text: stole the wild Wailord's Leftovers!)", stolen, repr(txt))
    b.frames(120)
    b.shot("after_thief")
    b.force_win = True
    leave_battle(b)
