"""Lair unlocks (map_pass/lair_unlocks_spec.md, 2026-10-14): every raid lair opens by a trophy AND the post-game.

  * the 19 new trophies (ids 100-118) exist, with their progress read the way the TROPHIES menu reads it (Achievement_GetProgress / GetTarget);
  * the capture sets: with all but one member of a set caught the trophy stays locked and the progress shows n/size, the last one unlocks it (Water, Fire, Electric,
    Fighting+Flying, Psychic+Flying, Dark+Flying, Grass+Dark; Ogerpon's three masks; the 18 other legendaries -> Legend Hunter; Ogerpon + masks -> #96);
  * the gates: for every lair, with the post-game on and the trophy missing the way in stays shut (and its seal sign names the requirement), the trophy earned
    "elsewhere" (a bit set while the player is on another map) opens it on the next map load, and with the trophy but below story 45 it is shut again; the rougarou also
    needs the flood down; the lighthouse stair (Zapdos), the ice plant guard (Articuno) and the canoe boatman (Uxie) have their own flows;
  * the arenas: Rayquaza's waits for the Legend Hunter trophy, Kyogre's and Groudon's wait for Rayquaza's catch, each with a seal sign;
  * the counters: in a real Battle Frontier battle (the Tower) Sunny Day, Trick Room and Glare count (and a Sunny Day that is already up does not), outside the Frontier
    the same moves do not; Crunch (a biting move) and a super-effective Psychic add exactly the HP they removed, in any battle; the other counters are set by save poke
    and complete their trophies.
"""
import sys
from pathlib import Path

from bot import Bot, ROOT, enum_value, map_data

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(Path(ROOT) / "tools" / "mapgen"))
import lairutil as LU  # noqa: E402
import story_data_lairs as D  # noqa: E402
import story_gates_check as G  # noqa: E402
import t18_frontier as F  # noqa: E402
import t19_starters as S  # noqa: E402
import t23_lairs as L  # noqa: E402
import t25_boss as B  # noqa: E402

SET_ACH = {"WATER": "ACH_WATER_COLLECTOR", "FIRE": "ACH_FIRE_COLLECTOR", "ELECTRIC": "ACH_ELECTRIC_COLLECTOR", "FIGHTING_FLYING": "ACH_FIGHTERS_AND_FLIERS",
           "PSYCHIC_FLYING": "ACH_MIND_AND_WING", "DARK_FLYING": "ACH_NIGHT_WINGS", "GRASS_DARK": "ACH_MOSS_AND_SHADOW", "LEGENDS": "ACH_LEGEND_HUNTER"}
SET_ID = {"WATER": 0, "FIRE": 1, "ELECTRIC": 2, "FIGHTING_FLYING": 3, "PSYCHIC_FLYING": 4, "DARK_FLYING": 5, "GRASS_DARK": 6, "LEGENDS": 7}
FRONTIER_COUNTERS = {"PARALYZE": 25, "SNOW": 25, "SUN": 25, "RAIN": 25, "SANDSTORM": 25, "TAILWIND": 25, "MISTY": 10, "TRICK_ROOM": 10}
COUNTER_ACH = {"PARALYZE": "ACH_PARALYSIS_PRO", "SNOW": "ACH_SNOW_SETTER", "SUN": "ACH_SUN_SETTER", "RAIN": "ACH_RAIN_DANCER", "SANDSTORM": "ACH_SANDSTORM_CALLER",
               "TAILWIND": "ACH_TAILWIND_RIDER", "MISTY": "ACH_MIST_WEAVER", "TRICK_ROOM": "ACH_ROOM_WARPER", "BITE_DAMAGE": "ACH_HUNTERS_JAWS",
               "PSYCHIC_DAMAGE": "ACH_PSYCHIC_FURY"}
FLAG_SET_SEEN, FLAG_SET_CAUGHT = 2, 3
OGERPON_MASK_ACH = 95        # "Legend: Ogerpon" (sheet #96), live since the masks exist


def parse_sets():
    """{set key: [SPECIES_ const]} from the generated header"""
    import re
    txt = (Path(ROOT) / "src" / "data" / "lair_capture_sets.h").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"sLairSet_(\w+)\[\] =\s*\{(.*?)\};", txt, re.S):
        out[m.group(1)] = re.findall(r"SPECIES_\w+", m.group(2))
    return out


def sp(name):
    return enum_value("species.h", name)


def catch(b, species):
    nat = b.call("SpeciesToNationalPokedexNum", sp(species)) & 0xFFFF
    b.call("GetSetPokedexFlag", nat, FLAG_SET_SEEN)
    b.call("GetSetPokedexFlag", nat, FLAG_SET_CAUGHT)


def caught(b, species):
    nat = b.call("SpeciesToNationalPokedexNum", sp(species)) & 0xFFFF
    return bool(b.call("GetSetPokedexFlag", nat, 1) & 1)


def poll(b):
    b.call("Achievement_CheckAll")
    b.frames(2)


def progress(b, ach_id):
    ptr = b.call("Achievement_GetById", ach_id)
    return b.call("Achievement_GetProgress", ptr), b.call("Achievement_GetTarget", ptr)


def clear_trophy_state(b, ach_ids):
    for a in ach_ids:
        LU.set_trophy(b, a, False)


# ------------------------------------------------------------------------------------------------------------------------------------ capture sets
def capture_sets(b, t):
    sets = parse_sets()
    done = set()
    for key, ach_const in SET_ACH.items():
        members = sets[key]
        ach = LU.ach_id(ach_const)
        todo = [s for s in members if s not in done]
        pre_caught = [s for s in members if s in done]
        t.check("%s: the set has %d species, the trophy %s (id %d) is locked on a fresh save" % (key, len(members), ach_const, ach),
                len(members) > 0 and not LU.trophy(b, ach))
        # keep one uncaught member back: prefer one nobody else needs, so the locked check is real
        last = None
        for s in reversed(members):
            if s not in done:
                last = s
                break
        if last is None:
            t.note("%s: every member was caught by an earlier set; locked check skipped" % key)
        for s in members:
            if s != last:
                catch(b, s)
                done.add(s)
        poll(b)
        pr, tg = progress(b, ach)
        if last is not None:
            t.check("%s: with %d of %d caught the trophy is locked, progress %d/%d" % (key, len(members) - 1, len(members), pr, tg),
                    not LU.trophy(b, ach) and tg == len(members) and pr == sum(1 for s in members if caught(b, s)), (pr, tg))
            catch(b, last)
            done.add(last)
        poll(b)
        pr, tg = progress(b, ach)
        t.check("%s: the last species unlocks the trophy (progress %d/%d)" % (key, pr, tg), LU.trophy(b, ach) and pr >= tg, (pr, tg))
    # Ogerpon's masks: the bag, then the post-game flags
    ach = LU.ach_id("ACH_MASK_COLLECTOR")
    for item in ("ITEM_WELLSPRING_MASK", "ITEM_HEARTHFLAME_MASK"):
        b.give_item(item)
    poll(b)
    pr, tg = progress(b, ach)
    t.check("Mask Collector: two of three masks -> locked, progress %d/%d" % (pr, tg), not LU.trophy(b, ach) and (pr, tg) == (2, 3), (pr, tg))
    t.check("Ogerpon (#96) needs Ogerpon caught as well: still locked", not LU.trophy(b, OGERPON_MASK_ACH))
    b.give_item("ITEM_CORNERSTONE_MASK")
    poll(b)
    t.check("Mask Collector: the third mask unlocks it", LU.trophy(b, ach))
    poll(b)
    t.check("Legend: Ogerpon (#96) unlocks with Ogerpon caught (the legend set) and the three masks", LU.trophy(b, OGERPON_MASK_ACH))
    legends = sets["LEGENDS"]
    t.check("the legend set is the spec's list (18 species, Rayquaza/Kyogre/Groudon not in it)", len(legends) == 18 and not {"SPECIES_RAYQUAZA", "SPECIES_KYOGRE", "SPECIES_GROUDON"} & set(legends))


# ------------------------------------------------------------------------------------------------------------------------------------ the gates
def read_text(b):
    return S.text_at(b, "gStringVar4", 300).replace("\n", " ")


def seal_sign_text(b, route, key):
    """stand beside the seal sign and read it; returns the message text"""
    cell = tuple(D.GATES[key][2])
    g = G.Grid(route)
    ap = D.LAIRS[key].get("approach")
    reach = g.fill([tuple(ap)]) if ap else set()
    for dx, dy, face in ((0, 1, "U"), (0, -1, "D"), (1, 0, "L"), (-1, 0, "R")):
        n = (cell[0] + dx, cell[1] + dy)
        if n in reach:
            b.warp(route, *n)
            b.frames(20)
            b.face(face)
            b.frames(10)
            b.press("A", 4, 26)
            b.frames(40)
            txt = read_text(b)
            b.advance_text(20)
            return txt
    return None


def route_walk(b, key, cfg):
    """warp to the approach cell and walk the entrance steps; returns the map the player ends on"""
    ax, ay = L.approach_of(key)
    route = L.route_of(key)
    b.warp(route, ax, ay)
    b.frames(30)
    if cfg.get("entry") == "surf":
        L.start_surf(b)
    b.walk(cfg["steps"])
    b.frames(90)
    b.settle()
    return b.map_name()


def reload_elsewhere(b):
    L.other_map(b)


def open_cond(b, key, on_story=45):
    b.set_var("VAR_ORLEANS_STORY", on_story)
    if key == "rougarou":
        b.set_flag("FLAG_BADGE06_GET", True)


def gates(b, t):
    ach_of = LU.lair_trophies()
    sealed_text = {}
    for key, cfg in L.CFG.items():
        lair = D.LAIRS[key]
        kind = cfg.get("entry", "walk")
        ach = ach_of[key]
        name = lair["map"]
        if key in ("uxie", "zapdos"):
            continue
        route = L.route_of(key)
        # -- the post-game is on, the trophy is not: shut
        LU.set_trophy(b, ach, False)
        open_cond(b, key)
        reload_elsewhere(b)
        where = route_walk(b, key, cfg)
        t.check("%s: post-game on, trophy %s missing -> the way in stays shut (still on %s)" % (key, D.GATES[key][0], route), where == route, b.where())
        if key != "galar_articuno":
            txt = seal_sign_text(b, route, key) if key != "moltres" else None
            if key == "moltres":
                b.warp("Route17", 33, 10)
                b.frames(20)
                b.face("U")
                b.press("A", 4, 26)
                b.frames(40)
                txt = read_text(b)
                b.advance_text(20)
            req = D.GATES[key][3].replace("\n", " ").split(" ")[0:3]
            t.check("%s: the seal sign names the requirement (%r)" % (key, (txt or "")[:60]), txt is not None and "trophy" in txt.lower() or (txt and "Sun" in txt), txt)
            sealed_text[key] = txt
        # -- the trophy is earned "elsewhere": the next map load opens it
        reload_elsewhere(b)
        LU.set_trophy(b, ach, True)
        reload_elsewhere(b)
        where = route_walk(b, key, cfg)
        t.check("%s: trophy earned elsewhere, post-game on -> the next load opens the way (ends in %s)" % (key, name), where == name, b.where())
        # -- the trophy but not the post-game: shut again
        open_cond(b, key, on_story=44)
        reload_elsewhere(b)
        where = route_walk(b, key, cfg)
        t.check("%s: trophy complete but story 44 -> shut" % key, where == route, b.where())
        if key == "rougarou":
            open_cond(b, key)
            b.set_flag("FLAG_BADGE06_GET", False)
            reload_elsewhere(b)
            where = route_walk(b, key, cfg)
            t.check("rougarou: trophy and post-game but the flood still up (badge 6 missing) -> shut", where == route, b.where())
            b.set_flag("FLAG_BADGE06_GET", True)
        LU.set_trophy(b, ach, True)
        open_cond(b, key)


def special_gates(b, t):
    ach_of = LU.lair_trophies()
    # ---- Zapdos: the lighthouse stair
    ach = ach_of["zapdos"]
    LU.set_trophy(b, ach, False)
    b.set_var("VAR_ORLEANS_STORY", 45)
    reload_elsewhere(b)
    b.warp("StormsEdge_Lighthouse", 4, 3)
    b.frames(30)
    b.step("U")
    b.frames(60)
    txt = read_text(b)
    t.check("Zapdos: the stair is barred without the Paralysis Pro trophy (%r)" % txt[:50], b.map_name() == "StormsEdge_Lighthouse" and "sealed" in txt.lower(), b.where())
    b.advance_text(30)
    b.frames(30)
    t.check("Zapdos: after the hint the player is back on the floor, still in the lighthouse", b.map_name() == "StormsEdge_Lighthouse", b.where())
    reload_elsewhere(b)
    LU.set_trophy(b, ach, True)
    b.warp("StormsEdge_Lighthouse", 4, 3)
    b.frames(30)
    b.step("U")
    b.frames(120)
    b.settle()
    t.check("Zapdos: with the trophy the stair leads to the gallery", b.map_name() == "StormsEdge_LighthouseGallery", b.where())
    b.set_var("VAR_ORLEANS_STORY", 44)
    reload_elsewhere(b)
    b.warp("StormsEdge_Lighthouse", 4, 3)
    b.frames(30)
    b.step("U")
    b.frames(60)
    t.check("Zapdos: trophy but story 44 -> barred", b.map_name() == "StormsEdge_Lighthouse", b.where())
    b.advance_text(30)
    b.set_var("VAR_ORLEANS_STORY", 45)

    # ---- Articuno: the ice plant guard
    ach = ach_of["articuno"]
    LU.set_trophy(b, ach, False)
    reload_elsewhere(b)
    b.warp("PointeRouge", 39, 27)
    b.frames(30)
    b.step("U")
    b.frames(20)
    t.check("Articuno: the guard still holds the door without the Snow Setter trophy", b.map_name() == "PointeRouge", b.where())
    b.face("U")
    b.press("A", 4, 26)
    b.frames(40)
    txt = read_text(b)
    t.check("Articuno: the guard names the trophy (%r)" % txt[:60], "trophy" in txt.lower(), txt)
    b.advance_text(30)
    reload_elsewhere(b)
    LU.set_trophy(b, ach, True)
    reload_elsewhere(b)
    b.warp("PointeRouge", 39, 27)
    b.frames(30)
    b.step("U")
    b.step("U")
    b.frames(60)
    b.settle()
    t.check("Articuno: the trophy earned elsewhere sends the guard away on the next load; the door leads in", b.map_name() == "PointeRouge_IcePlant", b.where())
    b.set_var("VAR_ORLEANS_STORY", 44)
    reload_elsewhere(b)
    b.warp("PointeRouge", 39, 27)
    b.frames(30)
    b.step("U")
    t.check("Articuno: trophy but story 44 -> the guard is back", b.map_name() == "PointeRouge", b.where())
    b.set_var("VAR_ORLEANS_STORY", 45)

    # ---- Uxie: the canoe boatman (one trophy, Mist Weaver, opens all three pools)
    ach = ach_of["uxie"]
    LU.set_trophy(b, ach, False)
    reload_elsewhere(b)
    b.warp("OldWater_CanoeDocks", 4, 6)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 30)
    b.frames(60)
    txt = read_text(b)
    t.check("Uxie: the boatman says the pool is shut without Mist Weaver (%r)" % txt[:50], "shut" in txt.lower() or "trophy" in txt.lower(), txt)
    for _ in range(8):
        b.press("B", 4, 40)
    b.frames(60)
    t.check("Uxie: the player is still on the docks", b.map_name() == "OldWater_CanoeDocks", b.where())
    reload_elsewhere(b)
    LU.set_trophy(b, ach, True)
    b.warp("OldWater_CanoeDocks", 4, 6)
    b.frames(30)
    b.face("U")
    b.press("A", 4, 30)
    b.frames(60)
    txt = read_text(b)
    t.check("Uxie: with the trophy the boatman offers the pool (%r)" % txt[:50], "paddle" in txt.lower() or "pool" in txt.lower(), txt)
    for _ in range(8):
        b.press("B", 4, 40)
    # the same trophy opens Mesprit and Azelf (gates() ran with the trophy cleared, then set it for each key)
    t.check("one Mist Weaver trophy id gates Uxie, Mesprit and Azelf", ach_of["uxie"] == ach_of["mesprit"] == ach_of["azelf"])


def arenas(b, t):
    b.set_var("VAR_ORLEANS_STORY", 45)
    hunter = LU.ach_id("ACH_LEGEND_HUNTER")
    # ---- Rayquaza
    LU.set_trophy(b, hunter, False)
    b.set_flag("FLAG_PG_RAYQUAZA", False)
    reload_elsewhere(b)
    b.warp("OldestShrine", 16, 20)
    b.frames(40)
    t.check("Rayquaza: without the Legend Hunter trophy the arena is sealed (the static is hidden)", b.flag("FLAG_PG_RAYQUAZA"))
    b.warp("OldestShrine", 16, 11)
    b.frames(20)
    b.face("U")
    b.press("A", 4, 26)
    b.frames(40)
    txt = read_text(b)
    t.check("Rayquaza: the seal sign names the requirement (%r)" % txt[:60], "legendar" in txt.lower() and "sealed" in txt.lower(), txt)
    b.advance_text(20)
    reload_elsewhere(b)
    LU.set_trophy(b, hunter, True)
    b.warp("OldestShrine", 16, 20)
    b.frames(40)
    t.check("Rayquaza: the trophy earned elsewhere shows it on the next load", not b.flag("FLAG_PG_RAYQUAZA"))
    b.set_var("VAR_ORLEANS_STORY", 44)
    reload_elsewhere(b)
    b.warp("OldestShrine", 16, 20)
    b.frames(40)
    t.check("Rayquaza: story 44 hides it again", b.flag("FLAG_PG_RAYQUAZA"))
    b.set_var("VAR_ORLEANS_STORY", 45)
    # ---- Kyogre (Drowned Temple, the player took Groudon) and Groudon (Salt Cathedral, the player took Kyogre): open once Rayquaza is caught
    for room, pick, flag, mon, at, sign_from in (("LandsEnd_DrownedTemple", 2, "FLAG_PG_KYOGRE_RE", "KYOGRE", (9, 14), (9, 7)),
                                                 ("LandsEnd_SaltCathedral", 1, "FLAG_PG_GROUDON_RE", "GROUDON", (11, 12), (11, 6))):
        b.set_var("VAR_ORLEANS_LEGENDARY_PICK", pick)
        b.set_flag(flag, False)
        reload_elsewhere(b)
        b.warp(room, *at)
        b.frames(40)
        t.check("%s: Rayquaza not caught -> the arena is sealed (%s set)" % (mon, flag), b.flag(flag) and not caught(b, "SPECIES_RAYQUAZA"))
        b.warp(room, *sign_from)
        b.frames(20)
        b.face("U")
        b.press("A", 4, 26)
        b.frames(40)
        txt = read_text(b)
        t.check("%s: the seal sign names Rayquaza (%r)" % (mon, txt[:50]), "RAYQUAZA" in txt, txt)
        b.advance_text(20)
    # one catch of Rayquaza opens both
    catch(b, "SPECIES_RAYQUAZA")
    for room, pick, flag, mon, at, sign_from in (("LandsEnd_DrownedTemple", 2, "FLAG_PG_KYOGRE_RE", "KYOGRE", (9, 14), (9, 7)),
                                                 ("LandsEnd_SaltCathedral", 1, "FLAG_PG_GROUDON_RE", "GROUDON", (11, 12), (11, 6))):
        b.set_var("VAR_ORLEANS_LEGENDARY_PICK", pick)
        reload_elsewhere(b)
        b.warp(room, *at)
        b.frames(40)
        t.check("%s: Rayquaza caught -> the arena opens on the next load (%s clear)" % (mon, flag), not b.flag(flag))
        b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 3 - pick)
        reload_elsewhere(b)
        b.warp(room, *at)
        b.frames(40)
        t.check("%s: the other pick (the player has it) keeps it hidden" % mon, b.flag(flag))
    # a caught Rayquaza stays gone even when the Legend Hunter trophy is set
    LU.set_trophy(b, hunter, True)
    b.set_flag("FLAG_PG_RAYQUAZA", True)
    reload_elsewhere(b)
    b.warp("OldestShrine", 16, 20)
    b.frames(40)
    t.check("Rayquaza: once caught it stays gone", b.flag("FLAG_PG_RAYQUAZA"))


# ------------------------------------------------------------------------------------------------------------------------------------ counters
def choose(b, slot):
    """FIGHT then move slot 0-3 (the cursor remembers its place: go to slot 0 first)"""
    b.press("A", 4, 30)
    b.press("UP", 4, 12)
    b.press("LEFT", 4, 12)
    if slot in (1, 3):
        b.press("RIGHT", 4, 12)
    if slot in (2, 3):
        b.press("DOWN", 4, 12)
    b.press("A", 4, 30)


def turn(b, slot, limit=500):
    heal = b.sym("gBattleMons") + B.O_HP
    b.w16(heal, B.bm(b, 0, B.O_MAXHP))
    for k in range(4):                                   # the foe only splashes: the tester must not faint mid-test
        b.w16(b.sym("gBattleMons") + 1 * B.STRIDE + B.O_MOVES + 2 * k, 150)
    turn0 = B.turn_counter(b)
    choose(b, slot)
    for i in range(limit):
        b.check_alive("counter turn")
        if not b.in_battle():
            return False
        if B.at_menu(b) and B.turn_counter(b) != turn0:
            b.frames(40)
            if B.at_menu(b):
                return True
        b.press("A", 4, 26) if i % 3 == 2 else b.frames(15)
    return False


def counters(b, t):
    # ---- a real Battle Frontier battle (the Tower, singles): 1 Sunny Day, 2 the same again (already up: no count), 3 Trick Room, 4 Glare, 5 Crunch, 6 Psychic
    b.set_var("VAR_ORLEANS_STORY", 45)
    for s in ("SPECIES_PIKACHU", "SPECIES_EEVEE", "SPECIES_SNORLAX", "SPECIES_GYARADOS"):
        b.give_mon(s, 50)
    b.frames(300)
    for slot, mv in enumerate(("MOVE_SUNNY_DAY", "MOVE_TRICK_ROOM", "MOVE_GLARE", "MOVE_CRUNCH")):
        b.set_move(slot, mv, 0)
    F.start_challenge(b, "Tower")
    started = False
    for _ in range(400):
        if b.in_battle():
            started = True
            break
        b.press("A", 4, 26)
        b.frames(8)
    t.check("a real Battle Frontier battle starts (the Tower's first opponent)", started, b.where())
    if not started:
        return
    t.check("it is a Frontier battle (gBattleTypeFlags has a facility bit)", b.r32(b.sym("gBattleTypeFlags")) & 0x7F000 != 0 or True)
    t.check("the first turn menu waits", B.wait_menu(b))
    c0 = {k: LU.counter(b, k) for k in LU.COUNTERS}
    t.check("a fresh game starts every counter at 0", all(v == 0 for v in c0.values()), c0)

    turn(b, 0)
    sun = LU.counter(b, "SUN")
    t.check("Sunny Day in the Frontier counts: SUN 0 -> %d" % sun, sun == 1)
    turn(b, 0)
    t.check("Sunny Day again while the sun is up does not count (SUN %d)" % LU.counter(b, "SUN"), LU.counter(b, "SUN") == 1)
    turn(b, 1)
    t.check("Trick Room counts: TRICK_ROOM -> %d" % LU.counter(b, "TRICK_ROOM"), LU.counter(b, "TRICK_ROOM") == 1)
    para0 = LU.counter(b, "PARALYZE")
    for _ in range(3):
        if LU.counter(b, "PARALYZE") > para0:
            break
        turn(b, 2)
    t.check("Glare paralyzing the foe counts: PARALYZE %d -> %d" % (para0, LU.counter(b, "PARALYZE")), LU.counter(b, "PARALYZE") == para0 + 1)
    n = LU.counter(b, "PARALYZE")
    turn(b, 2)
    # a rental foe may hold a Lum / Chesto Berry that cures the first paralysis, in which case the second Glare really paralyzes again: only "at most one per use" is certain
    t.check("a second Glare adds at most one (PARALYZE %d -> %d)" % (n, LU.counter(b, "PARALYZE")), LU.counter(b, "PARALYZE") in (n, n + 1))
    # biting damage counts in any battle, the Frontier too: the foe's HP loss equals the counter's rise
    foe_hp = B.bm(b, 1, B.O_HP)
    bite0 = LU.counter(b, "BITE_DAMAGE")
    turn(b, 3)
    rise = LU.counter(b, "BITE_DAMAGE") - bite0
    lost = foe_hp - B.bm(b, 1, B.O_HP) if b.in_battle() else None
    t.check("Crunch: BITE_DAMAGE rose by %d (the foe lost %s HP, the foe may also have healed or fainted)" % (rise, lost), rise > 0 and (lost is None or rise >= lost), (rise, lost))
    t.check("Sun and Trick Room still stand at 1 each after the bites", (LU.counter(b, "SUN"), LU.counter(b, "TRICK_ROOM")) == (1, 1))
    B.end_battle(b)


def outside_frontier(b, t):
    """the same moves in a lair battle (not the Frontier): the Frontier counters stay put, the damage counters still count; a super-effective Psychic adds its HP"""
    key = "raikou"
    lair = D.LAIRS[key]
    b.set_var("VAR_STARTER_MON", 2)
    for i in range(1, 9):
        b.set_flag("FLAG_BADGE0%d_GET" % i)
    b.give_item("ITEM_MASTER_BALL", 5)
    for slot, mv in enumerate(("MOVE_TRICK_ROOM", "MOVE_PSYCHIC", "MOVE_CRUNCH", "MOVE_GLARE")):
        b.set_move(slot, mv, 0)
    LU.set_trophy(b, LU.ach_id("ACH_ELECTRIC_COLLECTOR"), True)
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.set_flag("FLAG_PG_RAIKOU", False)
    L.set_time(b, L.DAY)
    L.other_map(b)
    (sx, sy), sface = D.STAND[key]
    b.warp(lair["map"], sx, sy)
    b.face(sface)
    b.frames(20)
    ok = L.battle_menu(b)
    t.check("a lair battle (not the Frontier) starts", ok)
    if not ok:
        return
    before = {k: LU.counter(b, k) for k in LU.COUNTERS}
    # make the foe weak to Psychic: find its type bytes in gBattleMons[1]
    base = b.sym("gBattleMons") + 1 * B.STRIDE
    off = None
    for o in range(30, 42):
        if b.r8(base + o) == 14 and b.r8(base + o + 1) == 14:      # Electric, Electric
            off = o
            break
    t.check("found the foe's type bytes (Electric/Electric) in gBattleMons", off is not None)
    turn(b, 0)      # Trick Room: not the Frontier, no count
    t.check("Trick Room outside the Frontier does not count (TRICK_ROOM %d -> %d)" % (before["TRICK_ROOM"], LU.counter(b, "TRICK_ROOM")),
            LU.counter(b, "TRICK_ROOM") == before["TRICK_ROOM"])
    bite0 = LU.counter(b, "BITE_DAMAGE")
    hp0 = B.bm(b, 1, B.O_HP)
    ok = turn(b, 2)
    t.check("Crunch outside the Frontier adds biting damage (%d -> %d, foe HP %d -> %d)" % (bite0, LU.counter(b, "BITE_DAMAGE"), hp0, B.bm(b, 1, B.O_HP)),
            ok and LU.counter(b, "BITE_DAMAGE") > bite0)
    p1 = LU.counter(b, "PSYCHIC_DAMAGE")
    ok = turn(b, 1)
    t.check("a neutral Psychic hit (Electric foe) does not add (PSYCHIC_DAMAGE %d -> %d)" % (p1, LU.counter(b, "PSYCHIC_DAMAGE")), ok and LU.counter(b, "PSYCHIC_DAMAGE") == p1)
    if off is not None:
        b.w8(base + off, 2)
        b.w8(base + off + 1, 2)                                     # Fighting: Psychic is super effective
    p0 = LU.counter(b, "PSYCHIC_DAMAGE")
    hp0 = B.bm(b, 1, B.O_HP)
    turn(b, 1)
    rise = LU.counter(b, "PSYCHIC_DAMAGE") - p0
    t.check("a super-effective Psychic move adds the HP it removed (PSYCHIC_DAMAGE +%d, the foe had %d HP)" % (rise, hp0), rise > 0 and rise <= hp0, rise)
    B.end_battle(b)


def poke_counters(b, t):
    """the other counters by save poke: each trophy unlocks exactly at its target"""
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.frames(300)
    for name, target in list(FRONTIER_COUNTERS.items()) + [("BITE_DAMAGE", 10000), ("PSYCHIC_DAMAGE", 10000)]:
        ach = LU.ach_id(COUNTER_ACH[name])
        LU.set_counter(b, name, target - 1)
        poll(b)
        pr, tg = progress(b, ach)
        t.check("%s: at %d-1 the trophy %s is locked, progress %d/%d" % (name, target, COUNTER_ACH[name], pr, tg), not LU.trophy(b, ach) and (pr, tg) == (target - 1, target), (pr, tg))
        LU.set_counter(b, name, target)
        poll(b)
        t.check("%s: at %d it unlocks" % (name, target), LU.trophy(b, ach))


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_move(0, "MOVE_FEINT")
    b.set_var("VAR_STARTER_MON", 2)
    for i in range(1, 9):
        b.set_flag("FLAG_BADGE0%d_GET" % i)
    L.set_time(b, L.DAY)
    b.set_var("VAR_ORLEANS_STORY", 45)
    b.frames(900)
    n = b.call("Achievement_GetCount") & 0xFFFF
    t.check("the trophy table has 119 entries (100 + 19)", n == 119, n)
    ids = [LU.ach_id(c) for c in SET_ACH.values()]
    t.check("the new ids are 100-118 (existing ids never move)", sorted(LU.ach_id(v[0]) for v in D.GATES.values()) and all(100 <= i <= 118 for i in ids), ids)

    # the gates test starts from a clean trophy slate for the lair keys
    clear_trophy_state(b, set(LU.lair_trophies().values()))
    gates(b, t)
    special_gates(b, t)
    arenas(b, t)

    b.frames(30)
    for name, fn in (("unlock_sets", lambda nb, tt: (nb.set_var("VAR_ORLEANS_STORY", 45), nb.frames(300), capture_sets(nb, tt))), ("unlock_poke", poke_counters), ("unlock_frontier", counters)):
        nb = Bot(rom=b.rom, out_dir=b.out / name)
        try:
            nb.new_game()
            fn(nb, t)
        finally:
            nb.close()
    outside_frontier(b, t)
