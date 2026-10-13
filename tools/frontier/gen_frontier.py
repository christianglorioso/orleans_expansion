"""Generates the Battle Frontier data from the Orleans dex (see frontier/01_plan.md).

usage (from the decomp root):  python tools/frontier/gen_frontier.py [--dry]
 inputs : tools/dex/out/pokemon_pp.c (run tools/dex/pp.sh), tools/frontier/out/moves_pp.c (tools/frontier/pp_moves.sh),
          tools/frontier/layout.json (frozen vanilla trainer layout), the sheets via tools/dex/sheet_data.py
 outputs: include/constants/battle_frontier_mons.h, src/data/battle_frontier/{battle_frontier_mons,battle_frontier_trainer_mons,
          battle_frontier_trainers}.h, then gen_extras.py patches the brains, Pike and Pyramid tables.
"""
import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layoutplan as lp
import movedb
import names
import odex
import typechart as tc
from hand import HAND
from genpools import PoolMixin
from setbuild import FullBuilder, TIER_Q

ROOT = Path(__file__).resolve().parents[2]
BF = ROOT / "src/data/battle_frontier"


def ability_ratings():
    t = (ROOT / "src/data/abilities.h").read_text(encoding="utf-8")
    parts = re.split(r"\n    \[(ABILITY_\w+)\] =\n", t)
    out = {}
    for i in range(1, len(parts), 2):
        m = re.search(r"\.aiRating = (-?\d+)", parts[i + 1])
        if m:
            out[parts[i]] = int(m.group(1))
    return out


def mega_map(dex):
    t = (ROOT / "src/data/pokemon/form_change_tables.h").read_text(encoding="utf-8")
    res = {}
    for mc in dex.megas:
        m = re.search(r"FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM,\s*" + mc + r",\s*(ITEM_\w+)", t)
        if not m:
            continue
        b = re.search(r"FORM_CHANGE_END_BATTLE,\s*(SPECIES_\w+)", t[m.end():]).group(1)
        res.setdefault(b, []).append((mc, m.group(1)))
    return res


def ball_for(types, tier):
    ts = [t[5:] for t in types]
    if tier in ("T0", "T1"):
        return "BALL_POKE"
    if "WATER" in ts or "BUG" in ts:
        return "BALL_NET"
    if "DARK" in ts or "GHOST" in ts:
        return "BALL_DUSK"
    if tier in ("A1", "A2"):
        return "BALL_GREAT"
    if tier in ("L", "H"):
        return "BALL_PREMIER" if tier == "L" else "BALL_ULTRA"
    return "BALL_ULTRA"


def species_name_const(sp, counters):
    base = sp[8:]
    counters[base] += 1
    return f"FRONTIER_MON_{base}_{counters[base]}"


class Gen(PoolMixin):
    def __init__(self):
        self.d = odex.Dex()
        self.mv = movedb.load()
        self.rate = ability_ratings()
        self.megas = mega_map(self.d)
        self.b = FullBuilder(self.d, self.mv, self.rate, self.megas)
        self.layout = json.load(open(Path(__file__).resolve().parent / "layout.json"))
        self.sets = [None] * lp.NUM_MONS
        self.roles_used = collections.defaultdict(list)
        self.plan = lp.plan(self.d)
        # every Mega base must be in the B list
        b = self.plan["B"]
        need = [s for s in self.megas if s in self.d.species and s not in b and s not in lp.BANNED and not lp.is_legend(self.d, s) and s != "SPECIES_SMEARGLE"]
        if need:
            drop = [s for s in b if s not in self.megas][:len(need)]
            b = sorted([s for s in b if s not in drop] + need, key=lambda s: (sum(self.d.stats(s).values()), s))
            self.plan["B"] = b

    # -------------------------------------------------------------------------------- sets
    def make(self, i, sp, tier, variant, mega=None, tag=""):
        h = HAND.get((sp, tier, variant)) or HAND.get((sp, tier)) or HAND.get(sp)
        used = self.roles_used[sp]
        for attempt in range(6):
            s = self.b.build(sp, tier, variant, mega=mega, avoid_roles=used[-2:], tag=tag + (f"r{attempt}" if attempt else ""),
                             force_role=(h or {}).get("role"))
            if not self._dup(s):
                break
        if sp in lp.OGERPON_MASK:
            s.item = lp.OGERPON_MASK[sp]
        n = 0
        while self._dup(s) and n < 12:
            n += 1
            rng = random.Random(f"dup:{sp}:{tier}:{variant}:{n}")
            q = TIER_Q[tier]
            s.item = self.b.pick_item(sp, self.b.profile(sp, as_species=mega[0] if mega else None), s.ability, s.role, s.moves, q, rng, not self.d.fully_evolved(sp)) if not mega and sp not in lp.OGERPON_MASK else s.item
            if self._dup(s) and n >= 6:
                alt = [m for m in self.b.pick_attacks(sp, self.b.profile(sp), s.ability, self.b.profile(sp)["side"], self.d.legal(sp, 50), 6, rng, strict=True) if m not in s.moves]
                if alt:
                    att = [m for m in s.moves if self.mv[m].damaging]
                    if att:
                        s.moves[s.moves.index(att[-1])] = alt[0]
        if h:
            for k in ("moves", "item", "nature", "ability", "ev"):
                if k in h:
                    setattr(s, k, h[k])
            if "moves" in h:
                s.moves = list(h["moves"])
        if sp in lp.OGERPON_MASK:
            s.item = lp.OGERPON_MASK[sp]
        s.ball = ball_for(self.d.types(sp), tier)
        used.append(s.role)
        self.sets[i] = s
        return s

    def _dup(self, s):
        for o in self.sets:
            if o and o.species == s.species and sorted(o.moves) == sorted(s.moves) and o.item == s.item:
                return True
        return False

    def build_all(self):
        p = self.plan
        i = 0
        for sp in p["T0"]:
            self.make(i, sp, "T0", 1)
            i += 1
        assert i == 110
        for sp in p["T1"]:
            self.make(i, sp, "T1", 1)
            i += 1
        assert i == 162
        for g, tier in enumerate(("A1", "A2")):
            for sp in p["A"]:
                self.make(i, sp, tier, g + 1)
                i += 1
        assert i == 372
        for g, tier in enumerate(("B1", "B2", "B3", "B4")):
            for j, sp in enumerate(p["B"]):
                mega = None
                if sp in self.megas and (tier == "B4" or (tier == "B3" and j % 3 == 0)):
                    mega = self.megas[sp][0] if tier == "B4" else (self.megas[sp][-1] if len(self.megas[sp]) > 1 else self.megas[sp][0])
                self.make(i, sp, tier, g + 1, mega=mega)
                i += 1
        assert i == 756
        # legend group: 94 slots, round-major over the species list, then extra sets for the strongest
        ls = p["L_species"]
        order = [(sp, r) for r in range(3) for sp in ls]
        order += [(sp, 3) for sp in ls[-(94 - len(order)):]]
        for sp, r in order:
            mega = None
            if sp in self.megas and r == 2:
                mega = self.megas[sp][0]
            self.make(i, sp, "L", r + 1, mega=mega)
            i += 1
        assert i == 850
        for r in range(4):
            for sp in p["H_species"]:
                mega = self.megas[sp][0] if sp in self.megas and r >= 2 else None
                self.make(i, sp, "H", r + 1, mega=mega)
                i += 1
        assert i == 882

    # -------------------------------------------------------------------------------- names / constants
    def names(self):
        counters = collections.Counter()
        out = []
        for s in self.sets:
            out.append(species_name_const(s.species, counters))
        return out


FACTORY_MAP = {"FRONTIER_MON_GRIMER": "FRONTIER_MONS_MID_FIRST", "FRONTIER_MON_FURRET_1": "FRONTIER_MONS_MID_LAST",
               "FRONTIER_MON_DELCATTY_1": "FRONTIER_MONS_A1_FIRST", "FRONTIER_MON_CLOYSTER_1": "FRONTIER_MONS_A1_LAST",
               "FRONTIER_MON_DELCATTY_2": "FRONTIER_MONS_A2_FIRST", "FRONTIER_MON_CLOYSTER_2": "FRONTIER_MONS_A2_LAST",
               "FRONTIER_MON_DUGTRIO_1": "FRONTIER_MONS_B1_FIRST", "FRONTIER_MON_SLAKING_1": "FRONTIER_MONS_B1_LAST",
               "FRONTIER_MON_DUGTRIO_2": "FRONTIER_MONS_B2_FIRST", "FRONTIER_MON_SLAKING_2": "FRONTIER_MONS_B2_LAST",
               "FRONTIER_MON_DUGTRIO_3": "FRONTIER_MONS_B3_FIRST", "FRONTIER_MON_SLAKING_3": "FRONTIER_MONS_B3_LAST",
               "FRONTIER_MON_DUGTRIO_4": "FRONTIER_MONS_B4_FIRST", "FRONTIER_MON_SLAKING_4": "FRONTIER_MONS_B4_LAST"}


def install(G, out_root=None):
    """write the real files (include/constants + src/data/battle_frontier + the patched engine tables).
    out_root: write an overlay tree instead (FRONTIER_OUT / --install-to); patched engine files are copied from the repo first."""
    import shutil

    import gen_extras
    out_root = Path(out_root) if out_root else ROOT

    def dest(rel):
        d = out_root / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        if out_root != ROOT and not d.exists() and (ROOT / rel).exists():
            shutil.copy(ROOT / rel, d)
        return d

    G.write_constants(dest("include/constants/battle_frontier_mons.h"))
    G.write_mons(dest("src/data/battle_frontier/battle_frontier_mons.h"))
    G.write_pools(dest("src/data/battle_frontier/battle_frontier_trainer_mons.h"))
    G.write_trainers(dest("src/data/battle_frontier/battle_frontier_trainers.h"))
    gen_extras.patch_brains(G, dest("src/frontier_util.c"))
    gen_extras.patch_pike(G, dest("src/battle_pike.c"))
    p50, pop = gen_extras.pyramid_files(G)
    dest("src/data/battle_frontier/battle_pyramid_level_50_wild_mons.h").write_text(p50, encoding="utf-8", newline="\n")
    dest("src/data/battle_frontier/battle_pyramid_open_level_wild_mons.h").write_text(pop, encoding="utf-8", newline="\n")
    f = dest("src/battle_factory.c")
    t = f.read_text(encoding="utf-8")
    for a, b in FACTORY_MAP.items():
        t = t.replace(a, b)
    f.write_text(t, encoding="utf-8", newline="\n")


def main():
    dry = "--dry" in sys.argv
    G = Gen()
    G.build_all()
    G.build_pools_and_trainers()
    if "--install" in sys.argv or "--install-to" in sys.argv:
        install(G, sys.argv[sys.argv.index("--install-to") + 1] if "--install-to" in sys.argv else None)
        print("sets", len(G.sets), "pools", len(G.pools), "trainers", len(G.trainers), "installed")
        return G
    out_dir = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    const_p = (out_dir / "battle_frontier_mons_const.h") if out_dir else ROOT / "include/constants/battle_frontier_mons.h"
    base = out_dir if out_dir else BF
    G.write_constants(const_p)
    G.write_mons(base / "battle_frontier_mons.h")
    G.write_pools(base / "battle_frontier_trainer_mons.h")
    G.write_trainers(base / "battle_frontier_trainers.h")
    print("sets", len(G.sets), "pools", len(G.pools), "trainers", len(G.trainers))
    return G


if __name__ == "__main__":
    main()
