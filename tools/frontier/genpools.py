"""Pools (per-class mon sets), trainers and the file writers for gen_frontier.py."""
import hashlib
import re

import names
import typechart as tc

# class theme: (primary types, secondary types, speed bonus threshold or None)
THEMES = {
    "YOUNGSTER_LASS": None, "SCHOOL_KID": None, "COOLTRAINER": None, "GENERAL": None, "POKEFAN_2": None,
    "RICH_BOY_LADY": (["NORMAL", "FAIRY", "PSYCHIC", "DARK"], ["ICE", "STEEL"], None),
    "CAMPER_PICNICKER": (["GRASS", "GROUND", "BUG", "NORMAL", "FIGHTING"], ["ROCK", "FIRE"], None),
    "TUBER": (["WATER"], ["ICE", "FLYING"], None),
    "SWIMMER": (["WATER"], ["ICE", "ELECTRIC"], None),
    "SWIMMING_TRIATHLETE": (["WATER"], ["ICE", "ELECTRIC"], None),
    "POKEFAN": (["NORMAL", "ELECTRIC", "FAIRY"], ["GRASS", "WATER"], None),
    "BUG_CATCHER": (["BUG"], ["GRASS", "POISON"], None),
    "BUG_MANIAC": (["BUG"], ["GRASS", "POISON"], None),
    "NINJA_BOY": (["POISON", "DARK", "BUG", "GHOST"], ["FIGHTING", "STEEL"], None),
    "FISHERMAN": (["WATER"], ["POISON", "ICE"], None),
    "RUIN_MANIAC": (["ROCK", "GROUND", "STEEL"], ["PSYCHIC", "GHOST"], None),
    "PARASOL_LADY": (["WATER", "GRASS", "FAIRY"], ["FLYING", "BUG"], None),
    "AROMA_LADY": (["GRASS", "POISON", "FAIRY"], ["BUG", "WATER"], None),
    "GUITARIST": (["ELECTRIC", "NORMAL", "STEEL"], ["FIRE", "FAIRY"], None),
    "BIRD_KEEPER": (["FLYING"], ["NORMAL", "DRAGON"], None),
    "SAILOR": (["WATER", "FIGHTING"], ["ROCK", "STEEL"], None),
    "HIKER": (["ROCK", "GROUND", "FIGHTING", "STEEL"], ["FIRE", "NORMAL"], None),
    "KINDLER": (["FIRE"], ["DRAGON", "GHOST"], None),
    "RUNNING_TRIATHLETE": (["NORMAL", "FIRE", "ELECTRIC", "FIGHTING"], ["FLYING", "GROUND"], 90),
    "CYCLING_TRIATHLETE": (["ELECTRIC", "FLYING", "STEEL"], ["NORMAL", "BUG"], 90),
    "BLACK_BELT": (["FIGHTING"], ["ROCK", "STEEL", "DARK"], None),
    "BATTLE_GIRL": (["FIGHTING"], ["ROCK", "STEEL", "DARK"], None),
    "EXPERT": (["FIGHTING", "PSYCHIC", "DARK", "STEEL"], ["NORMAL", "GHOST"], None),
    "PSYCHIC": (["PSYCHIC", "FAIRY"], ["GHOST", "DARK"], None),
    "HEX_MANIAC": (["GHOST", "DARK", "POISON"], ["FAIRY", "PSYCHIC"], None),
    "POKEMANIAC": (["DRAGON", "ROCK", "GROUND", "STEEL"], ["ICE", "FIRE"], None),
    "GENTLEMAN": (["NORMAL", "DARK", "STEEL", "FAIRY"], ["PSYCHIC", "ICE"], None),
    "COLLECTOR": (["ROCK", "STEEL", "GHOST", "DRAGON", "ICE"], ["PSYCHIC", "BUG"], None),
    "BEAUTY": (["WATER", "GRASS", "FAIRY", "ICE"], ["PSYCHIC", "FLYING"], None),
    "PKMN_RANGER": (["GRASS", "GROUND", "BUG", "NORMAL", "FLYING"], ["ROCK", "FIGHTING"], None),
    "DRAGON_TAMER": (["DRAGON"], ["FLYING", "FIRE", "GHOST"], None),
    "PKMN_BREEDER": (["NORMAL", "FAIRY", "GRASS", "WATER"], ["PSYCHIC", "ELECTRIC"], None),
}
EEVEE_FAMILY = {"SPECIES_EEVEE", "SPECIES_VAPOREON", "SPECIES_JOLTEON", "SPECIES_FLAREON", "SPECIES_ESPEON", "SPECIES_UMBREON", "SPECIES_LEAFEON", "SPECIES_GLACEON", "SPECIES_SYLVEON"}

FEATURED = {  # vanilla macro argument -> the Orleans (non-legendary) species it features
    "LATIOS": ["SPECIES_HYPNO"], "LATIAS": ["SPECIES_MALAMAR"], "TYRANITAR": ["SPECIES_URSALUNA"], "DRAGONITE": ["SPECIES_DRAGONITE"],
    "ARTICUNO": ["SPECIES_NINETALES_ALOLA"], "ZAPDOS": ["SPECIES_RAICHU_ALOLA"], "MOLTRES": ["SPECIES_DELPHOX"],
    "RAIKOU": ["SPECIES_JOLTEON"], "ENTEI": ["SPECIES_FLAREON"], "SUICUNE": ["SPECIES_VAPOREON"],
    "REGIROCK": ["SPECIES_GIGALITH"], "REGICE": ["SPECIES_VANILLUXE"], "REGISTEEL": ["SPECIES_ARCHALUDON"],
    "METAPOD": ["SPECIES_NINCADA"], "KAKUNA": ["SPECIES_PARAS"], "SILCOON": ["SPECIES_JOLTIK"], "CASCOON": ["SPECIES_CUTIEFLY"],
}


def theme_key(macro):
    m = macro.replace("FRONTIER_MONS_", "")
    for k in sorted(THEMES, key=len, reverse=True):
        if m.startswith(k):
            return k
    for k, v in (("EEVEELUTIONS", "EEVEE"), ("YOUNGSTER", "YOUNGSTER_LASS"), ("SWIMMING", "SWIMMING_TRIATHLETE"), ("PKMN_BREEDER", "PKMN_BREEDER"), ("COOLTRAINER", "COOLTRAINER")):
        if m.startswith(k):
            return v
    return "GENERAL"


def noise(*a):
    return int(hashlib.md5("|".join(map(str, a)).encode()).hexdigest()[:6], 16) / 0xFFFFFF


class PoolMixin:
    def feature(self, i):
        s = self.sets[i]
        return dict(types=[t[5:] for t in self.d.types(s.species)], spe=self.d.stats(s.species)["spe"])

    def theme_score(self, i, key):
        th = THEMES.get(key)
        if key == "EEVEE":
            return 5.0 if self.sets[i].species in EEVEE_FAMILY else 0.0
        if not th:
            return 1.0
        f = self.feature(i)
        pri, sec, spd = th
        sc = 0.0
        if any(t in pri for t in f["types"]):
            sc += 3.0
        elif any(t in sec for t in f["types"]):
            sc += 1.2
        if spd and f["spe"] >= spd:
            sc += 1.5
        return sc

    def build_pool(self, macro, lo, hi, n, featured=()):
        key = theme_key(macro)
        win = list(range(max(0, lo), min(hi, len(self.sets) - 1) + 1))
        if key == "EEVEE":
            ids = [i for i in range(len(self.sets)) if self.sets[i].species in EEVEE_FAMILY]
            return sorted(ids)
        if n >= 0.9 * len(win):
            ids = list(win)
        else:
            scored = sorted(win, key=lambda i: -(self.theme_score(i, key) + noise(macro, i) * 0.9))
            ids, per = [], {}
            for i in scored:
                sp = self.sets[i].species
                if per.get(sp, 0) >= 3:
                    continue
                ids.append(i)
                per[sp] = per.get(sp, 0) + 1
                if len(ids) >= n:
                    break
        for sp in featured:
            ids += [i for i, s in enumerate(self.sets) if s.species == sp and i not in ids]
        # a party filler needs variety: grow the pool with the best remaining window ids until it has enough species and items
        def ok(ids_):
            low = [i for i in ids_ if i <= 849]
            return len({self.sets[i].species for i in low}) >= 10 and len({self.sets[i].item for i in low}) >= 8
        grow = sorted([i for i in win if i not in ids], key=lambda i: -(self.theme_score(i, key) + noise(macro, i, 1)))
        while not ok(ids) and grow:
            ids.append(grow.pop(0))
        return sorted(set(ids))

    def pool_name(self, vanilla_pool):
        m = re.match(r"(FRONTIER_MONS_\w+?)(?:\((.*)\))?$", vanilla_pool.strip())
        base, args = m.group(1), m.group(2)
        if not args:
            return base, ()
        a = [x.strip() for x in args.split(",")]
        return base + "_" + "_".join(FEATURED[x][0][8:] if x in FEATURED else x for x in a), tuple(a)

    def build_pools_and_trainers(self):
        L = self.layout
        self.pools = {}      # new macro name -> [mon ids]
        self.trainers = []
        gender_ct = {"M": 0, "F": 0}
        for t in L["trainers"]:
            name, args = self.pool_name(t["pool"])
            base = re.match(r"(FRONTIER_MONS_\w+?)(?:\(|$)", t["pool"]).group(1)
            if name not in self.pools:
                pl = L["pools"][base]
                feat = []
                for a in args:
                    feat += FEATURED.get(a, [])
                if base == "FRONTIER_MONS_YOUNGSTER_LASS_2_NO_DUGTRIO":
                    pl = pl
                self.pools[name] = self.build_pool(base, pl["lo"], pl["hi"], pl["n"], feat)
            g = names.class_gender(t["cls"])
            bank = names.MALE if g == "M" else names.FEMALE
            nm = bank[gender_ct[g]]
            gender_ct[g] += 1
            self.trainers.append(dict(const=t["const"], cls=t["cls"], name=nm, before=t["before"], win=t["win"], lose=t["lose"], pool=name))

    # ------------------------------------------------------------------ writers
    def write_constants(self, path):
        cons = self.names()
        self.mon_names = cons
        out = ["#ifndef GUARD_CONSTANTS_BATTLE_FRONTIER_MONS_H", "#define GUARD_CONSTANTS_BATTLE_FRONTIER_MONS_H", "",
               "// Generated by tools/frontier/gen_frontier.py: do not edit by hand.", "// Ids are tier-ordered; the engine (battle_factory.c ranges, FRONTIER_MONS_HIGH_TIER) depends on the boundaries below.", ""]
        for i, c in enumerate(cons):
            out.append(f"#define {c:<40}{i}")
        out += ["", "#define FRONTIER_MONS_HIGH_TIER     849 // Mons above this point can only appear > level 50", "",
                "// Factory rental / opponent ranges (inclusive), see sInitialRentalMonRanges in battle_factory.c",
                "#define FRONTIER_MONS_MID_FIRST     110", "#define FRONTIER_MONS_MID_LAST      199",
                "#define FRONTIER_MONS_A1_FIRST      162", "#define FRONTIER_MONS_A1_LAST       266",
                "#define FRONTIER_MONS_A2_FIRST      267", "#define FRONTIER_MONS_A2_LAST       371",
                "#define FRONTIER_MONS_B1_FIRST      372", "#define FRONTIER_MONS_B1_LAST       467",
                "#define FRONTIER_MONS_B2_FIRST      468", "#define FRONTIER_MONS_B2_LAST       563",
                "#define FRONTIER_MONS_B3_FIRST      564", "#define FRONTIER_MONS_B3_LAST       659",
                "#define FRONTIER_MONS_B4_FIRST      660", "#define FRONTIER_MONS_B4_LAST       755",
                "", f"#define NUM_FRONTIER_MONS           {len(self.sets)}", "", "#endif //GUARD_CONSTANTS_BATTLE_FRONTIER_MONS_H", ""]
        path.write_text("\n".join(out), encoding="utf-8", newline="\n")

    def write_mons(self, path):
        out = ["// Generated by tools/frontier/gen_frontier.py (frontier/01_plan.md): do not edit by hand.",
               "const struct TrainerMon gBattleFrontierMons[NUM_FRONTIER_MONS] =", "{"]
        for c, s in zip(self.mon_names, self.sets):
            mv = list(s.moves) + ["MOVE_NONE"] * (4 - len(s.moves))
            out += [f"    [{c}] = {{",
                    f"        .species = {s.species},",
                    f"        .moves = {{{', '.join(mv)}}},",
                    f"        .heldItem = {s.item},",
                    f"        .ev = TRAINER_PARTY_EVS({', '.join(str(x) for x in s.ev)}),",
                    f"        .nature = {s.nature},",
                    f"        .ability = {s.ability},",
                    f"        .ball = {s.ball}",
                    "    },"]
        out += ["};", ""]
        path.write_text("\n".join(out), encoding="utf-8", newline="\n")

    def write_pools(self, path):
        out = ["// Generated by tools/frontier/gen_frontier.py (frontier/01_plan.md): do not edit by hand.",
               "// One macro per trainer class and tier; each is a -1 terminated list of FRONTIER_MON_* ids (the party filler draws three or four at random).", ""]
        for name, ids in self.pools.items():
            out.append(f"#define {name} \\")
            for i in ids:
                out.append(f"    {self.mon_names[i]}, \\")
            out += ["    -1", ""]
        path.write_text("\n".join(out), encoding="utf-8", newline="\n")

    def write_trainers(self, path):
        out = ["// Generated by tools/frontier/gen_frontier.py (frontier/01_plan.md): do not edit by hand.",
               "const struct BattleFrontierTrainer gBattleFrontierTrainers[FRONTIER_TRAINERS_COUNT] =", "{"]
        for t in self.trainers:
            out += [f"    [{t['const']}] = {{",
                    f"        .facilityClass = {t['cls']},",
                    f"        .trainerName = _(\"{t['name']}\"),",
                    f"        .speechBefore = {t['before']},",
                    f"        .speechWin = {t['win']},",
                    f"        .speechLose = {t['lose']},",
                    f"        .monSet = (const u16[]){{{t['pool']}}}",
                    "    },"]
        out += ["};", ""]
        path.write_text("\n".join(out), encoding="utf-8", newline="\n")
