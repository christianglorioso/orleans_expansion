"""Brains, Battle Pike and Battle Pyramid tables for the Frontier redesign (called by gen_frontier.py --install).

The brain table replaces sFrontierBrainsMons in src/frontier_util.c (between the markers it writes the first time), the Pike tables replace
sLvl50_Mons1 .. sLvlOpenMons in src/battle_pike.c, and the two Pyramid wild-mon files are rewritten whole (levels are kept from the file).
"""
import hashlib
import random
import re
from pathlib import Path

import typechart as tc

ROOT = Path(__file__).resolve().parents[2]

# ------------------------------------------------------------------------------------------------ brains
# (species, forced role) per slot; Greta's Arena teams are hand-written below.
AUTO_BRAINS = {
    "FRONTIER_FACILITY_TOWER": dict(  # Celeste: the salon belle; psychic poise, a firebrand and a big appetite
        silver=[("SPECIES_HYPNO", "setup"), ("SPECIES_DELPHOX", "attacker"), ("SPECIES_OINKOLOGNE_M", "attacker")],
        gold=[("SPECIES_MALAMAR", "setup"), ("SPECIES_WYRDEER", "attacker"), ("SPECIES_URSALUNA", "choice")]),
    "FRONTIER_FACILITY_DOME": dict(  # Beauregard: the zydeco showman's all-rounders
        silver=[("SPECIES_SWAMPERT", "attacker"), ("SPECIES_DRAGONITE", "setup"), ("SPECIES_CHARIZARD", "attacker")],
        gold=[("SPECIES_SWAMPERT", "choice"), ("SPECIES_METAGROSS", "setup"), ("SPECIES_DRAGAPULT", "attacker")]),
    "FRONTIER_FACILITY_PALACE": dict(  # Armand: Mardi Gras revellers, a bat, a loud one and a lady of the water
        silver=[("SPECIES_CROBAT", "attacker"), ("SPECIES_EXPLOUD", "attacker"), ("SPECIES_MILOTIC", "attacker")],
        gold=[("SPECIES_NINETALES", "attacker"), ("SPECIES_EXPLOUD", "choice"), ("SPECIES_VAPOREON", "setup")]),
    "FRONTIER_FACILITY_PIKE": dict(  # Lucille: venom, steel and a sea serpent
        silver=[("SPECIES_SEVIPER", "attacker"), ("SPECIES_FERROTHORN", "bulky"), ("SPECIES_MILOTIC", "bulky")],
        gold=[("SPECIES_SEVIPER", "setup"), ("SPECIES_ARCHALUDON", "attacker"), ("SPECIES_GYARADOS", "setup")]),
    "FRONTIER_FACILITY_PYRAMID": dict(  # Lafitte: the mound king's stone and ice
        silver=[("SPECIES_GIGALITH", "attacker"), ("SPECIES_MAGNEZONE", "attacker"), ("SPECIES_VANILLUXE", "attacker")],
        gold=[("SPECIES_NINETALES_ALOLA", "attacker"), ("SPECIES_COALOSSAL", "attacker"), ("SPECIES_CLOYSTER", "setup")]),
}
# Factory: random rentals fill the real party; these are only the species the brain card / Steven-style display uses
FACTORY = dict(silver=[("SPECIES_METANG", "ITEM_SITRUS_BERRY"), ("SPECIES_CORVIKNIGHT", "ITEM_LUM_BERRY"), ("SPECIES_ARCHALUDON", "ITEM_LEFTOVERS")],
               gold=[("SPECIES_METAGROSS", "ITEM_SITRUS_BERRY"), ("SPECIES_CORVIKNIGHT", "ITEM_CHESTO_BERRY"), ("SPECIES_ARCHALUDON", "ITEM_LUM_BERRY")])

# Greta, the Battle Arena brain: a bayou brawler's krewe (crawfish, the dancer, the bear), no setup stalling: the Arena judges three turns
GRETA = dict(
    silver=[
        dict(species="SPECIES_KINGLER_ORLEANIAN", item="ITEM_SCOPE_LENS", ability="ABILITY_SHEER_FORCE", nature="NATURE_ADAMANT", ev=(106, 152, 0, 152, 0, 0),
             moves=["MOVE_CRABHAMMER", "MOVE_SUPERPOWER", "MOVE_HIGH_HORSEPOWER", "MOVE_KNOCK_OFF"]),
        dict(species="SPECIES_URSALUNA", item="ITEM_FLAME_ORB", ability="ABILITY_GUTS", nature="NATURE_ADAMANT", ev=(152, 152, 100, 106, 0, 0),
             moves=["MOVE_FACADE", "MOVE_CLOSE_COMBAT", "MOVE_HEADLONG_RUSH", "MOVE_EARTHQUAKE"]),
        dict(species="SPECIES_FLOATZEL", item="ITEM_LIFE_ORB", ability="ABILITY_SWIFT_SWIM", nature="NATURE_JOLLY", ev=(6, 152, 0, 252, 0, 100),
             moves=["MOVE_WAVE_CRASH", "MOVE_AQUA_JET", "MOVE_ICE_PUNCH", "MOVE_CRUNCH"]),
    ],
    gold=[
        dict(species="SPECIES_CRAWDAUNT_ORLEANIAN", item="ITEM_LIFE_ORB", ability="ABILITY_ADAPTABILITY", nature="NATURE_ADAMANT", ev=(252, 252, 4, 0, 0, 0),
             moves=["MOVE_LIQUIDATION", "MOVE_FIRE_LASH", "MOVE_CLOSE_COMBAT", "MOVE_AQUA_JET"]),
        dict(species="SPECIES_QUAQUAVAL", item="ITEM_QUAQUAVALITE", ability="ABILITY_MOXIE", nature="NATURE_JOLLY", ev=(4, 252, 0, 252, 0, 0),
             moves=["MOVE_AQUA_STEP", "MOVE_CLOSE_COMBAT", "MOVE_BRAVE_BIRD", "MOVE_KNOCK_OFF"]),
        dict(species="SPECIES_FERALIGATR", item="ITEM_LUM_BERRY", ability="ABILITY_SHEER_FORCE", nature="NATURE_ADAMANT", ev=(4, 252, 0, 252, 0, 0),
             moves=["MOVE_WATERFALL", "MOVE_CRUNCH", "MOVE_ICE_PUNCH", "MOVE_DRAGON_DANCE"]),
    ])


def brain_text(G):
    """the whole 'sFrontierBrainsMons' initialiser body (without the declaration line)"""
    order = ["FRONTIER_FACILITY_TOWER", "FRONTIER_FACILITY_DOME", "FRONTIER_FACILITY_PALACE", "FRONTIER_FACILITY_ARENA", "FRONTIER_FACILITY_FACTORY",
             "FRONTIER_FACILITY_PIKE", "FRONTIER_FACILITY_PYRAMID"]
    out = []

    def mon(m, iv):
        ev = m["ev"]
        r = [f"            {{", f"                .species = {m['species']},", f"                .heldItem = {m['item']},"]
        if m.get("ability"):
            r.append(f"                .ability = {m['ability']},")
        r.append(f"                .fixedIV = {iv},")
        if m.get("nature"):
            r.append(f"                .nature = {m['nature']},")
            r.append(f"                .evs = {{{', '.join(str(x) for x in ev)}}},")
            r.append(f"                .moves = {{{', '.join(list(m['moves']) + ['MOVE_NONE'] * (4 - len(m['moves'])))}}},")
        r.append("            },")
        return r

    for fac in order:
        out.append(f"    [{fac}] =")
        out.append("    {")
        if fac == "FRONTIER_FACILITY_FACTORY":
            out.append("        // Because Factory's Pokémon are random, this facility's Brain also uses random Pokémon; these species are only what the")
            out.append("        // brain's card shows (Steven's steel team in the original).")
        for sym, iv in (("silver", "20"), ("gold", "MAX_PER_STAT_IVS")):
            out.append(f"        // {'Silver' if sym == 'silver' else 'Gold'} Symbol.")
            out.append("        {")
            if fac == "FRONTIER_FACILITY_FACTORY":
                for sp, it in FACTORY[sym]:
                    out += mon(dict(species=sp, item=it, ev=None), iv)
            elif fac == "FRONTIER_FACILITY_ARENA":
                for m in GRETA[sym]:
                    out += mon(m, iv)
            else:
                for sp, role in AUTO_BRAINS[fac][sym]:
                    s = G.b.build(sp, "H", 2 if sym == "gold" else 1, avoid_roles=(), force_role=role, tag="brain" + fac)
                    ev = s.ev if sym == "gold" else tuple((x * 8 // 10) // 4 * 4 for x in s.ev)
                    out += mon(dict(species=sp, item=s.item, ability=s.ability, nature=s.nature, ev=ev, moves=s.moves), iv)
            out.append("        },")
        out.append("    },")
    return "\n".join(out)


def patch_brains(G, path):
    t = path.read_text(encoding="utf-8")
    head = "static const struct FrontierBrainMon sFrontierBrainsMons[][2][FRONTIER_PARTY_SIZE] =\n{\n"
    i = t.index(head) + len(head)
    j = t.index("\n};\n", i)
    new = "// BEGIN GENERATED (tools/frontier/gen_extras.py): do not edit by hand\n" + brain_text(G) + "\n// END GENERATED"
    if "// BEGIN GENERATED (tools/frontier/gen_extras.py)" in t[i:j]:
        a = t.index("// BEGIN GENERATED (tools/frontier/gen_extras.py)", i)
        j2 = t.index("// END GENERATED", a) + len("// END GENERATED")
        t = t[:a] + new + t[j2:]
    else:
        t = t[:i] + new + t[j:]
    # the struct and the creation code learn about abilities
    if "enum Ability ability;" not in t.split("struct FrontierBrainMon")[1][:200]:
        t = t.replace("    enum Item heldItem;\n    u8 fixedIV;", "    enum Item heldItem;\n    enum Ability ability;\n    u8 fixedIV;", 1)
    hook = "        SetMonData(&gParties[B_TRAINER_OPPONENT_A][monPartyId], MON_DATA_HELD_ITEM, &sFrontierBrainsMons[facility][symbol][i].heldItem);\n"
    add = ("        if (sFrontierBrainsMons[facility][symbol][i].ability != ABILITY_NONE)\n"
           "        {\n"
           "            // pin the brain mon's ability (Orleans): the slot that holds it, else the first\n"
           "            u32 abilityNum;\n"
           "            for (abilityNum = 0; abilityNum < NUM_ABILITY_SLOTS; abilityNum++)\n"
           "                if (gSpeciesInfo[sFrontierBrainsMons[facility][symbol][i].species].abilities[abilityNum] == sFrontierBrainsMons[facility][symbol][i].ability)\n"
           "                    break;\n"
           "            if (abilityNum >= NUM_ABILITY_SLOTS)\n"
           "                abilityNum = 0;\n"
           "            SetMonData(&gParties[B_TRAINER_OPPONENT_A][monPartyId], MON_DATA_ABILITY_NUM, &abilityNum);\n"
           "        }\n")
    if add not in t:
        assert hook in t
        t = t.replace(hook, hook + add, 1)
    path.write_text(t, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------------------------------------ pike
PIKE_THIRD_50 = ["SPECIES_JELLICENT", "SPECIES_ELECTRODE_ORLEANIAN", "SPECIES_BRELOOM", "SPECIES_HYPNO"]
PIKE_THIRD_OPEN = ["SPECIES_MISMAGIUS", "SPECIES_ELECTRODE_ORLEANIAN", "SPECIES_BRELOOM", "SPECIES_MALAMAR"]


def pike_text(G):
    out = ["// BEGIN GENERATED (tools/frontier/gen_extras.py): Pike wild mons; SpeciesToPikeMonId needs Seviper first, Milotic second",
           "// Const rom data."]
    for kind, thirds in (("Lvl50", PIKE_THIRD_50), ("LvlOpen", PIKE_THIRD_OPEN)):
        for n, third in enumerate(thirds, 1):
            out.append(f"static const struct PikeWildMon s{kind}_Mons{n}[] =")
            out.append("{")
            for k, (sp, delta) in enumerate((("SPECIES_SEVIPER", 4), ("SPECIES_MILOTIC", 4), (third, 5))):
                s = G.b.build(sp, "B2" if kind == "Lvl50" else "B3", n, force_role="disrupt" if k != 1 else "bulky", tag=f"pike{kind}{n}")
                mv = list(s.moves)
                out.append("    {")
                out.append(f"        .species = {sp},")
                out.append(f"        .levelDelta = {delta},")
                out.append(f"        .moves = {{{', '.join(mv + ['MOVE_NONE'] * (4 - len(mv)))}}}")
                out.append("    }" + ("," if k < 2 else ""))
            out.append("};")
        out.append("")
        out.append(f"static const struct PikeWildMon *const s{kind}Mons[] =" if kind == "Lvl50" else "static const struct PikeWildMon *const sLvlOpenMons[] =")
        out.append("{")
        out += [f"    s{kind}_Mons{n}" + ("," if n < 4 else "") for n in range(1, 5)]
        out.append("};")
        out.append("")
    out.append("// END GENERATED")
    return "\n".join(out)


def patch_pike(G, path):
    t = path.read_text(encoding="utf-8")
    new = pike_text(G)
    if "// BEGIN GENERATED (tools/frontier/gen_extras.py)" in t:
        a = t.index("// BEGIN GENERATED (tools/frontier/gen_extras.py)")
        b = t.index("// END GENERATED") + len("// END GENERATED")
        t = t[:a] + new + t[b:]
    else:
        a = t.index("// Const rom data.\nstatic const struct PikeWildMon sLvl50_Mons1[] =")
        b = t.index("static const struct PikeWildMon *const sLvlOpenMons[] =\n{")
        b = t.index("};\n", b) + 3
        t = t[:a] + new + t[b:]
    # SpeciesToPikeMonId stays: Seviper 0, Milotic 1, anything else 2
    path.write_text(t, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------------------------------------ pyramid
ROUND_TYPES = ["ELECTRIC", "FIRE", "WATER", "GRASS", "ROCK", "GROUND", "BUG", "FIGHTING", "POISON", "PSYCHIC", "GHOST", "FLYING", "NORMAL", "ICE",
               "DARK", "STEEL", "DRAGON", "FAIRY", "WATER", "DRAGON"]


def pyramid_files(G):
    d = G.d
    bst = lambda s: sum(d.stats(s).values())
    base = ROOT / "src/data/battle_frontier"
    lv50 = (base / "battle_pyramid_level_50_wild_mons.h").read_text(encoding="utf-8")
    lvop = (base / "battle_pyramid_open_level_wild_mons.h").read_text(encoding="utf-8")
    lv_50 = [int(x) for x in re.findall(r"\.lvl = (\d+)", lv50)]
    lv_op = [int(x) for x in re.findall(r"\.lvl = (\d+)", lvop)]
    assert len(lv_50) == len(lv_op) == 160
    from layoutplan import BANNED, EXCLUDED, is_legend
    pool = [s for s in d.species if s not in BANNED and s not in EXCLUDED and not is_legend(d, s)]
    rounds = []
    used_global = {}
    for r in range(20):
        ty = ROUND_TYPES[r]
        cand = [s for s in pool if ty in [t[5:] for t in d.types(s)]]
        mons = []
        chosen = set()
        for k in range(8):
            lo = lv_op[r * 8 + k]
            young = lo < 22
            pick = [s for s in cand if s not in chosen and (not d.fully_evolved(s)) == young] or [s for s in cand if s not in chosen] or [s for s in pool if s not in chosen]
            pick.sort(key=lambda s: (used_global.get(s, 0), hashlib.md5(f"{r}:{k}:{s}".encode()).hexdigest()))
            sp = pick[0]
            chosen.add(sp)
            used_global[sp] = used_global.get(sp, 0) + 1
            legal = d.legal(sp, min(lv_op[r * 8 + k], lv_50[r * 8 + k]))
            rng = random.Random(f"pyr:{r}:{k}:{sp}")
            prof = G.b.profile(sp)
            ability = G.b.pick_ability(sp, "attacker", G.b.can_set_weather(legal, None), rng, prof)
            mv = G.b.build_moves(sp, prof, ability, "attacker", legal, rng, 1)
            mons.append((sp, mv))
        rounds.append(mons)

    def emit(prefix, levels):
        out = []
        for r in range(20):
            out.append(f"static const struct PyramidWildMon s{prefix}WildMons_Round{r + 1}[] =")
            out.append("{")
            for k, (sp, mv) in enumerate(rounds[r]):
                out += ["    {", f"        .species = {sp},", f"        .lvl = {levels[r * 8 + k]},", "        .abilityNum = ABILITY_RANDOM,",
                        f"        .moves = {{{', '.join(mv + ['MOVE_NONE'] * (4 - len(mv)))}}}", "    }" + ("," if k < 7 else "")]
            out.append("};")
            out.append("")
        out.append(f"static const struct PyramidWildMon *const s{prefix}WildMonPointers[] =")
        out.append("{")
        out += [f"    s{prefix}WildMons_Round{r + 1}" + ("," if r < 19 else "") for r in range(20)]
        out.append("};")
        return "// Generated by tools/frontier/gen_frontier.py: do not edit by hand.\n" + "\n".join(out) + "\n"

    return emit("Level50", lv_50), emit("OpenLevel", lv_op)
