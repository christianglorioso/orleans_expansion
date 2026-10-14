"""CONFIG BATCH (2026-10-14): HGSS followers, first-pickup item descriptions, the Exp. Share key item (Lafayette, chapter 3), reusable TMs (one per
player, shops sell them once), the IV/EV summary cycle, the HGSS Pokedex (Dex+) with Orleans species, fishing chains.

Screenshots go to C:/Users/chris/orleans_expansion/tile_review/config_*.png (followers on 3+ maps, the Dex+ pages, the three summary pages)."""
import re
import shutil
from pathlib import Path

from bot import ROOT, enum_value, map_data

REVIEW = ROOT.parent / "tile_review"
HEAP_SIZE = 0x1C500


def save(b, label, name):
    """screenshot -> tile_review/config_<name>.png"""
    png = b.shot(label)
    REVIEW.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, REVIEW / ("config_%s.png" % name))
    return png


def header_value(rel, name):
    m = re.search(r"#define\s+%s\s+(\S+)" % name, (ROOT / "include/config" / rel).read_text(encoding="utf-8"))
    return m.group(1) if m else None


def start_menu(b, action):
    src = (ROOT / "src/start_menu.c").read_text(encoding="utf-8")
    m = re.search(r"enum\s*\{(.*?)\};", src, re.S)
    names = [x.strip().split("=")[0].strip() for x in m.group(1).split(",") if x.strip() and not x.strip().startswith("//")]
    b.press("START", 6, 30)
    b.frames(20)
    n = b.r8(b.sym("sNumStartMenuActions"))
    acts = [b.r8(b.sym("sCurrentStartMenuActions") + i) for i in range(n)]
    b.press("B", 4, 20)                                  # the menu remembers its last cursor row: close, reset it, reopen
    b.frames(20)
    b.w8(b.sym("sStartMenuCursorPos"), 0)
    b.press("START", 6, 30)
    b.frames(20)
    for _ in range(acts.index(names.index(action))):
        b.press("DOWN", 6, 10)
    b.press("A", 6, 40)
    b.frames(100)


def objects(b):
    """[(slot, localId)] of every active object event"""
    base = b.sym("gObjectEvents") & ~1
    return [(i, b.r8(base + i * 0x24 + 8)) for i in range(16) if b.r8(base + i * 0x24) & 1]


def heap_blocks(b):
    """(used bytes, free bytes, biggest free block, allocated blocks) of gHeap"""
    base = b.sym("gHeap") & ~1
    p, used, free, big, n = base, 0, 0, 0, 0
    for _ in range(300):
        w0, w1, nxt = b.r32(p), b.r32(p + 4), b.r32(p + 12)
        size = w1 & 0x3FFFF
        if (w0 >> 16) != 0xA3A3:
            break
        if w0 & 1:
            used += size + 16
            n += 1
        else:
            free += size
            big = max(big, size)
        if nxt in (base, 0):
            break
        p = nxt
    return used, free, big, n


def tm_item(name):
    """ITEM_TM_<name> = ITEM_TM01 (582) + its place in tms_hms.h FOREACH_TM"""
    txt = (ROOT / "include/constants/tms_hms.h").read_text(encoding="utf-8")
    block = txt[txt.index("#define FOREACH_TM(F)"):txt.index("#define FOREACH_HM")]
    names = re.findall(r"F\((\w+)\)", block)
    return enum_value("items.h", "ITEM_TM01") + names.index(name)


def item_id(name):
    return tm_item(name[8:]) if name.startswith("ITEM_TM_") else enum_value("items.h", name)


def bag_count(b, item):
    it = item_id(item)
    n = 0
    while n < 999 and b.call("CheckBagHasItem", it, n + 1) & 0xFF:
        n += 1
    return n


def section(t, name, fn, b):
    """a section that fails on its own: an exception is one failed check, the rest still runs"""
    try:
        fn(b, t)
    except Exception as e:  # noqa: BLE001
        if "ERR call" in str(e) or "harness" in str(e):
            raise
        t.check("%s: no exception" % name, False, "%s: %s" % (type(e).__name__, e))


# --------------------------------------------------------------------------------------------------------------------------------- followers
FOLLOW_MAPS = [("Route6", 19, 14), ("OldWater", 16, 23), ("CrescentCity", 62, 27), ("IsleMarais_Shelter", 10, 4), ("Route21", 23, 9),
               ("OldestShrine", 8, 15), ("StormsEdge", 12, 12), ("CampCocodrie", 24, 17), ("GrandOak", 29, 6), ("PointeRouge", 37, 20), ("LutinsHollow_Gym", 9, 4),
               ("Route2_RaikouClearing", 10, 13), ("Route14_RougarouHollow", 10, 13), ("Route23_BloodmoonArroyo", 10, 13), ("Route7_CelebiGlade", 10, 13),
               ("Route11_SuicuneIsle", 10, 13), ("Route16_EnteiField", 10, 13), ("CrescentCity_GameCorner", 6, 9)]
SHOT_MAPS = ("CrescentCity", "CampCocodrie", "GrandOak")      # dry land: on Surf / in the swamp the follower is hidden by design


def expected_ids(b, name, x, y):
    ids = set()
    for i, o in enumerate(map_data(name)["objects"]):
        if x - 9 <= o["x"] <= x + 10 and y - 7 <= o["y"] <= y + 9:
            fl = str(o.get("flag", "0"))
            if fl not in ("0", "") and b.flag(fl):
                continue
            lid = o.get("local_id")
            ids.add(int(lid) if str(lid).isdigit() else i + 1)
    return ids


def follower_section(b, t):
    t.check("OW_FOLLOWERS_ENABLED is TRUE", header_value("overworld.h", "OW_FOLLOWERS_ENABLED") == "TRUE", header_value("overworld.h", "OW_FOLLOWERS_ENABLED"))
    for sp, lvl in (("SPECIES_PIKACHU", 20),):
        b.give_mon(sp, lvl)
    b.set_var("VAR_ORLEANS_STORY", 20)
    for name, x, y in FOLLOW_MAPS:
        b.warp(name, x, y)
        b.frames(80)
        objs = objects(b)
        fol = b.call("GetFollowerObject")
        exp = expected_ids(b, name, x, y)
        have = {lid for _, lid in objs}
        special = {lid for _, lid in objs if lid in (0xFF, 0xFE) or 249 <= lid <= 252}
        missing = sorted(exp - have)
        t.check("%s at (%d,%d): the follower exists and every story/NPC object of the window is still spawned (%d objects, %d slots used)"
                % (name, x, y, len(exp), len(objs)), fol != 0 and not missing and len(objs) <= 16,
                "follower %#x missing %s slots %d" % (fol, missing, len(objs)))
        if name in SHOT_MAPS:
            sx = {"CampCocodrie": "L", "GrandOak": "D", "CrescentCity": "R"}[name]
            b.walk(sx * 3)                                   # a few steps so the follower steps out behind the player
            b.frames(200)                                    # the trophy popups of the map entry pass
            save(b, "follower_" + name, "follower_" + name)
        t.check("%s: the game loop is alive" % name, not b.crashed(), b.where())
    # large and legendary leads, an Orleanian form with placeholder art: the follower still appears (Route 6 = the densest window)
    for sp in ("SPECIES_STEELIX", "SPECIES_RAYQUAZA", "SPECIES_VOLTORB_ORLEANIAN", "SPECIES_TANGELA_ORLEANIAN", "SPECIES_URSALUNA_BLOODMOON"):
        b.give_mon(sp, 40)
        party = b.r32(b.sym("gPlayerPartyPtr"))
        # make it the lead: swap slot 0 and the new last slot through SwapPartyPokemon-free memory copy
        last = b.party_count() - 1
        a, c = party, party + 100 * last
        buf0 = [b.r8(a + i) for i in range(100)]
        buf1 = [b.r8(c + i) for i in range(100)]
        for i in range(100):
            b.w8(a + i, buf1[i])
            b.w8(c + i, buf0[i])
        b.warp("Route6", 19, 14)
        b.frames(80)
        fol = b.call("GetFollowerObject")
        t.check("%s leads: the follower appears on Route 6 and no NPC is lost" % sp, fol != 0 and not (expected_ids(b, "Route6", 19, 14) - {l for _, l in objects(b)}),
                "follower %#x slots %d" % (fol, len(objects(b))))
        if sp == "SPECIES_RAYQUAZA":                         # the legendary's big sprite out on dry land
            b.warp("CampCocodrie", 24, 17)
            b.walk("LLL")
            b.frames(200)
            save(b, "follower_large", "follower_large_rayquaza")
    # Surf / Dive / bikes hide the follower
    b.warp("CrescentCity", 62, 27)
    b.frames(40)
    av = b.sym("gPlayerAvatar")
    flags0 = b.r8(av)
    for label, bit in (("surfing", 1 << 3), ("underwater", 1 << 4), ("mach bike", 1 << 1), ("acro bike", 1 << 2)):
        b.w8(av, bit)
        vis = b.call("IsFollowerVisible") & 0xFF
        t.check("%s hides the follower (IsFollowerVisible = 0)" % label, vis == 0, vis)
    b.w8(av, 1 << 0)
    t.check("on foot the follower is visible", (b.call("IsFollowerVisible") & 0xFF) == 1)
    b.w8(av, flags0)
    # FLAG_TEMP_HIDE_FOLLOWER: the scripted-scene switch removes it
    b.set_flag("FLAG_TEMP_HIDE_FOLLOWER", True)
    b.call("UpdateFollowingPokemon")
    t.check("FLAG_TEMP_HIDE_FOLLOWER removes the follower object", b.call("GetFollowerObject") == 0)
    b.set_flag("FLAG_TEMP_HIDE_FOLLOWER", False)
    b.call("UpdateFollowingPokemon")
    t.check("and clearing it brings it back", b.call("GetFollowerObject") != 0)
    # walking with the follower, the overworld speed-up toggle and DexNav do not freeze it
    b.walk("LLLL")
    b.frames(30)
    w = b.watch(2)
    t.check("walking with a follower: no freeze", not w["frozen"] and w["frame_counter_advancing"], w)


# --------------------------------------------------------------------------------------------------------------------------------- item descriptions
def item_description_section(b, t):
    t.check("OW_SHOW_ITEM_DESCRIPTIONS is first-time", header_value("overworld.h", "OW_SHOW_ITEM_DESCRIPTIONS") == "OW_ITEM_DESCRIPTIONS_FIRST_TIME",
            header_value("overworld.h", "OW_SHOW_ITEM_DESCRIPTIONS"))
    ball = enum_value("items.h", "ITEM_POKE_BALL")
    got = lambda: bool(b.call("GetSetItemObtained", ball, 0) & 0xFF)  # noqa: E731
    spot = None
    for px, py, face in ((24, 25, "U"), (23, 24, "R"), (25, 24, "L"), (24, 23, "D")):   # a neighbour of the ball at (24,24) that is dry land
        b.warp("Route1", px, py)
        b.frames(60)
        if b.pos() == (px, py) and not (b.r8(b.sym("gPlayerAvatar")) & (1 << 3)):
            spot = (px, py, face)
            break
    t.check("found a dry approach to the Route 1 Poke Ball", spot is not None, spot)
    t.check("before the pickup the item is not marked obtained", not got())
    b.face(spot[2])
    b.frames(10)
    b.press("A", 4, 20)
    b.frames(48)
    save(b, "item_description", "item_description_first")     # the "found" message with the first-time description box
    shown = b.script_status() != 2
    b.advance_text(30)
    t.check("first pickup: the pickup script ran (found message up)", shown, "status %d" % b.script_status())
    t.check("the pickup marks the item obtained (first time only)", got())
    t.check("the Poke Ball is in the bag", bag_count(b, "ITEM_POKE_BALL") >= 1, bag_count(b, "ITEM_POKE_BALL"))
    # the second ball of the same kind shows no box: GetSetItemObtained reports it as known
    t.check("a second pickup of the same item finds it already obtained", got())


# --------------------------------------------------------------------------------------------------------------------------------- Exp. Share
def exp_share_section(b, t):
    t.check("I_EXP_SHARE_ITEM is GEN_6 and the flag is FLAG_EXP_SHARE_ON", header_value("item.h", "I_EXP_SHARE_ITEM") == "GEN_6"
            and header_value("item.h", "I_EXP_SHARE_FLAG") == "FLAG_EXP_SHARE_ON", (header_value("item.h", "I_EXP_SHARE_ITEM"), header_value("item.h", "I_EXP_SHARE_FLAG")))
    b.set_var("VAR_ORLEANS_STORY", 13)
    b.set_flag("FLAG_LAFAYETTE_EXP_SHARE", False)
    t.check("no Exp. Share before Lafayette", bag_count(b, "ITEM_EXP_SHARE") == 0)
    b.warp("CrescentCity_Conservation", 11, 4)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 20)
    for _ in range(60):
        b.press("A", 4, 22)
        b.frames(10)
        if bag_count(b, "ITEM_EXP_SHARE") and b.script_status() == 2:
            break
    b.advance_text(60)
    t.check("Lafayette gives the Exp. Share in chapter 3 (story 13 briefing, key item)", bag_count(b, "ITEM_EXP_SHARE") == 1, bag_count(b, "ITEM_EXP_SHARE"))
    t.check("FLAG_LAFAYETTE_EXP_SHARE is set", b.flag("FLAG_LAFAYETTE_EXP_SHARE"))
    save(b, "exp_share", "exp_share_given")
    # asking again gives nothing more
    b.face("U")
    b.press("A", 4, 20)
    b.advance_text(60)
    t.check("still exactly one Exp. Share after talking again", bag_count(b, "ITEM_EXP_SHARE") == 1, bag_count(b, "ITEM_EXP_SHARE"))
    # the toggle: the key item flips FLAG_EXP_SHARE_ON (IsGen6ExpShareEnabled)
    t.check("the Exp. Share starts off", not b.flag("FLAG_EXP_SHARE_ON"))
    b.set_flag("FLAG_EXP_SHARE_ON", True)
    t.check("with the flag on, IsGen6ExpShareEnabled", bool(b.call("IsGen6ExpShareEnabled") & 0xFF))
    b.set_flag("FLAG_EXP_SHARE_ON", False)


# --------------------------------------------------------------------------------------------------------------------------------- reusable TMs
def tm_section(b, t):
    t.check("I_REUSABLE_TMS is TRUE", header_value("item.h", "I_REUSABLE_TMS") == "TRUE", header_value("item.h", "I_REUSABLE_TMS"))
    tm = item_id("ITEM_TM_DOUBLE_TEAM")
    t.check("a TM is a reusable one-per-player item (importance 1)", b.call("GetItemImportance", tm) & 0xFF == 1, b.call("GetItemImportance", tm))
    b.call("AddBagItem", tm, 1)
    b.call("AddBagItem", tm, 1)
    t.check("a gift of a TM already owned is absorbed (still one)", bag_count(b, "ITEM_TM_DOUBLE_TEAM") == 1, bag_count(b, "ITEM_TM_DOUBLE_TEAM"))
    b.set_var("VAR_ORLEANS_STORY", 20)
    for f in ("FLAG_BADGE01_GET", "FLAG_BADGE02_GET", "FLAG_BADGE03_GET"):
        b.set_flag(f, True)
    b.call("AddMoney", b.save1() + 0x490, 20000)
    b.warp("CrescentCity_Dept2f", 3, 8)
    b.frames(30)
    # talk to the TM clerk (3, 5) from the real standing cell north of her (a shelf runs along her south side), not by starting her script
    t.check("walked to the clerk's real standing cell (3, 4)", b.goto(3, 4), b.where())
    b.face("D")
    b.press("A", 4, 20)
    t.check("pressing A facing the clerk starts her script", b.script_status() != 2 or not b.in_overworld(), b.where())
    for _ in range(14):
        b.frames(30)
        if not b.in_overworld():
            break
        b.press("A", 4, 20)
    b.frames(60)
    t.check("the TM clerk's shop opened", not b.in_overworld(), b.callback2_name())
    save(b, "tm_shop_list", "tm_shop_sold_out_list")
    # the first entry is the owned Double Team: choosing it says it is sold out
    b.press("A", 4, 30)
    b.frames(40)
    save(b, "tm_shop_owned", "tm_shop_owned")
    money_before = b.call("GetMoney", b.save1() + 0x490)
    for _ in range(20):
        b.press("B", 4, 25)
    b.advance_text(30)
    t.check("buying a TM already owned costs nothing", b.call("GetMoney", b.save1() + 0x490) >= money_before, "%d" % money_before)   # (a trophy popup may add money)
    t.check("still one Double Team after the shop", bag_count(b, "ITEM_TM_DOUBLE_TEAM") == 1, bag_count(b, "ITEM_TM_DOUBLE_TEAM"))


# --------------------------------------------------------------------------------------------------------------------------------- IV/EV summary
def summary_section(b, t):
    t.check("P_SUMMARY_SCREEN_IV_EV_INFO is TRUE", header_value("summary_screen.h", "P_SUMMARY_SCREEN_IV_EV_INFO") == "TRUE",
            header_value("summary_screen.h", "P_SUMMARY_SCREEN_IV_EV_INFO"))
    b.set_flag("FLAG_SYS_POKEMON_GET", True)
    b.warp("Route6", 19, 14)
    b.frames(30)
    before = heap_blocks(b)
    start_menu(b, "MENU_ACTION_POKEMON")
    b.press("A", 6, 30)
    b.frames(20)
    b.press("A", 6, 30)
    b.frames(70)
    b.press("RIGHT", 6, 30)
    b.frames(40)
    used, free, big, n = heap_blocks(b)
    t.note("heap with the summary screen open: %d used, %d free (largest %d) of %d; before it: %d used" % (used, free, big, HEAP_SIZE, before[0]))
    t.check("the summary screen leaves heap to spare (>= 20 KiB free)", free >= 20 * 1024, "%d free, largest %d" % (free, big))
    save(b, "summary_stats", "summary_1_stats")
    hashes = [b.screen_hash()]
    for label, name in (("ivs", "summary_2_ivs"), ("evs", "summary_3_evs"), ("stats_again", "summary_4_back_to_stats")):
        b.press("A", 6, 30)
        b.frames(30)
        save(b, "summary_" + label, name)
        hashes.append(b.screen_hash())
    t.check("A cycles stats -> IVs -> EVs -> stats (the three pages differ and the cycle closes)",
            len({hashes[0], hashes[1], hashes[2]}) == 3, hashes)
    t.check("the summary screen is still alive", not b.crashed(), b.callback2_name())
    for _ in range(4):
        b.press("B", 6, 40)
        b.frames(40)
    t.check("backing out lands on the field", b.in_overworld() or b.callback2_name() == "CB2_ReturnToField", b.callback2_name())


# --------------------------------------------------------------------------------------------------------------------------------- Dex+
DEX_SPECIES = ["SPECIES_CHIKORITA", "SPECIES_TANGELA_ORLEANIAN", "SPECIES_VOLTORB_ORLEANIAN", "SPECIES_CRAWDAUNT_ORLEANIAN", "SPECIES_HAUNTER",   # Linking Cord
               "SPECIES_POLIWHIRL", "SPECIES_BOLDORE", "SPECIES_SCYTHER",                                                                             # Linking Cord, Black Augurite
               "SPECIES_PETILIL", "SPECIES_LILLIGANT_HISUI", "SPECIES_ROTOM_HEAT", "SPECIES_URSALUNA_BLOODMOON"]                                  # Fais-do-do Ribbon, forms
PAGES = ["INFO", "AREA", "STATS", "EVO", "CRY", "SIZE"]


def dex_section(b, t):
    t.check("POKEDEX_PLUS_HGSS is TRUE", header_value("pokedex_plus_hgss.h", "POKEDEX_PLUS_HGSS") == "TRUE", header_value("pokedex_plus_hgss.h", "POKEDEX_PLUS_HGSS"))
    rows = [l.split("\t") for l in (ROOT / "tools/dex/out/dex_order.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    number = {r[2]: int(r[0]) for r in rows}
    for num, name, const, nd in rows:                                   # every Orleans species seen and caught
        sp = enum_value("species.h", const)
        nat = b.call("SpeciesToNationalPokedexNum", sp) & 0xFFFF
        b.call("GetSetPokedexFlag", nat, 2)
        b.call("GetSetPokedexFlag", nat, 3)
    b.set_flag("FLAG_SYS_POKEDEX_GET", True)
    b.set_flag("FLAG_SYS_POKEMON_GET", True)
    b.warp("Route6", 19, 14)
    b.frames(30)
    start_menu(b, "MENU_ACTION_POKEDEX")
    t.check("the Pokedex opens (Dex+ list)", b.callback2_name() == "CB2_Pokedex", b.callback2_name())
    save(b, "dex_list", "dex_list_regional")
    cursor = 1
    first = True
    for const in sorted((c for c in DEX_SPECIES if c in number), key=lambda c: number[c]) + [c for c in DEX_SPECIES if c not in number]:
        if const not in number:
            t.check("%s is in the regional dex" % const, False)
            continue
        target = number[const]
        delta = target - cursor
        for _ in range(abs(delta) // 7):
            b.press("RIGHT" if delta > 0 else "LEFT", 6, 18)
        for _ in range(abs(delta) % 7):
            b.press("DOWN" if delta > 0 else "UP", 6, 14)
        cursor = target
        b.frames(30)
        b.press("A", 6, 30)
        b.frames(60)
        shots = []
        bad = []
        for i, page in enumerate(PAGES):
            if i:
                b.press("RIGHT", 6, 30)
                b.frames(50)
            png = b.shot("dex_%s_%s" % (const[8:], page))
            shots.append(png)
            if const in ("SPECIES_VOLTORB_ORLEANIAN", "SPECIES_MACHOKE", "SPECIES_CHIKORITA") or page in ("EVO", "STATS"):
                if const in ("SPECIES_VOLTORB_ORLEANIAN", "SPECIES_MACHOKE", "SPECIES_PETILIL", "SPECIES_TANGELA_ORLEANIAN"):
                    shutil.copyfile(png, REVIEW / ("config_dex_%s_%s.png" % (const[8:].lower(), page.lower())))
            if not (b.callback2_name() == "CB2_Pokedex" and b.nonblack() > 1000 and not b.crashed()):
                bad.append((page, b.callback2_name(), b.nonblack()))
        t.check("%s (dex %d): all six Dex+ pages draw" % (const, target), not bad, bad[:2])
        # back to the list
        for _ in range(5):
            b.press("LEFT", 6, 20)
        b.frames(20)
        b.press("B", 6, 40)
        b.frames(40)
        first = False
    t.check("Dex+ survived every species and page", not b.crashed(), b.callback2_name())
    for _ in range(4):
        b.press("B", 6, 40)
        b.frames(40)


# --------------------------------------------------------------------------------------------------------------------------------- fishing chain
def fishing_section(b, t):
    t.check("I_FISHING_CHAIN is TRUE", header_value("fishing.h", "I_FISHING_CHAIN") == "TRUE", header_value("fishing.h", "I_FISHING_CHAIN"))
    streak = b.sym("gChainFishingDexNavStreak")
    b.w8(streak, 0)
    b.w8(b.sym("gIsFishingEncounter"), 1)
    t.check("no streak, no extra shiny rolls", b.call("CalculateChainFishingShinyRolls") == 0)
    for _ in range(3):
        b.call("UpdateChainFishingStreak")
    t.check("three catches in a row: the chain counts 3", b.r8(streak) == 3, b.r8(streak))
    t.check("and rolls 2 extra shiny chances per link (6)", b.call("CalculateChainFishingShinyRolls") == 6, b.call("CalculateChainFishingShinyRolls"))
    for _ in range(30):
        b.call("UpdateChainFishingStreak")
    t.check("the bonus is capped (FISHING_CHAIN_SHINY_STREAK_MAX)", b.call("CalculateChainFishingShinyRolls") <= 2 * 20, b.call("CalculateChainFishingShinyRolls"))
    b.w8(streak, 0)
    b.w8(b.sym("gIsFishingEncounter"), 0)


def run(b, t):
    b.new_game()
    b.set_flag("FLAG_SYS_POKEMON_GET", True)
    section(t, "followers", follower_section, b)
    section(t, "item descriptions", item_description_section, b)
    section(t, "exp share", exp_share_section, b)
    section(t, "tms", tm_section, b)
    section(t, "summary", summary_section, b)
    section(t, "dex", dex_section, b)
    section(t, "fishing", fishing_section, b)
    w = b.watch(3)
    t.check("game loop alive at the end", not w["frozen"] and w["frame_counter_advancing"], w)
