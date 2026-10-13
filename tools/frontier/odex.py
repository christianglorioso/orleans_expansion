"""The Orleans species database for the Frontier tools: dex membership, types, stats, abilities and legal moves.

Reads the same sources as tools/dex/validate_dex.py: the dex sheet (membership) and tools/dex/out/pokemon_pp.c
(the built species data; refresh it with tools/dex/pp.sh after a build).  Nothing here writes to the repo.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/dex"))
import party_check as pc  # noqa: E402
import ppdata  # noqa: E402
import sheet_data as sd  # noqa: E402
import species_map as sm  # noqa: E402


class Dex:
    def __init__(self):
        t, ents = ppdata.load()
        self.ents = ents
        self.lv = ppdata.levelup_sets(t)
        self.tc = ppdata.move_sets(t, "TeachableLearnset")
        self.eg = ppdata.move_sets(t, "EggMoveLearnset")
        self.info = {k: ppdata.fields(v) for k, v in ents.items()}
        self.prev = {}
        for k, v in ents.items():
            i = v.find(".evolutions =")
            if i < 0:
                continue
            seg = v[i:]
            j = seg.find("{ 0xFFFF }")
            for m in re.finditer(r"\{EVO_\w+, [^{}]*?(SPECIES_\w+)(?:,|\})", seg[:j] if j > 0 else seg):
                self.prev.setdefault(m.group(1), set()).add(k)
        cons = sm.species_consts()
        self.rows = sd.load_dex()
        self.species = {}      # species const -> dex row (non-Mega, non-Primal)
        self.megas = {}        # mega species const -> row
        for r in self.rows:
            if r["name"] in sm.ORLEANIAN and r["kind"] == "species":
                k = sm.orleanian_const(r["name"])
            else:
                k = sm.base_const(r["name"], cons)
            if r["kind"] == "species":
                self.species[k] = r
            else:
                self.megas[k] = r
        self.moves = sd.load_move_names()
        self._move_consts = set(self.moves.values())
        self._legal = {}
        self._evc = {}
        self._canon = {}

    def canonical(self, const):
        c = self._canon.get(const)
        if c is None:
            c = self._canon[const] = sm.canonical(const)
        return c

    def in_dex(self, const):
        return self.canonical(const) in self.species

    def types(self, const):
        return self.info[self.canonical(const)]["types"]

    def stats(self, const):
        return self.info[self.canonical(const)]["stats"]

    def abilities(self, const):
        return [a for a in self.info[self.canonical(const)]["abilities"] if a != "ABILITY_NONE"]

    def legal(self, const, level=50):
        key = (self.canonical(const), level)
        if key not in self._legal:
            self._legal[key] = pc.legal_moves(key[0], level, self.info, self.lv, self.tc, self.eg, self.prev)
        return self._legal[key]

    def evo_prev(self, const):
        return self.prev.get(self.canonical(const), set())

    def evo_next(self, const):
        c = self._evc.get(const)
        if c is None:
            c = self._evc[const] = self._evo_next(const)
        return c

    def _evo_next(self, const):
        """species this one evolves into directly (evolution targets of the built data)"""
        ev = self.ents[self.canonical(const)]
        i = ev.find(".evolutions =")
        if i < 0:
            return []
        seg = ev[i:]
        k = seg.find("{ 0xFFFF }")
        seg = seg[:k] if k > 0 else seg
        return [m.group(1) for m in re.finditer(r"\{EVO_(?!NONE)\w+, [^{}(]*?(SPECIES_\w+)", seg)]

    def fully_evolved(self, const):
        return not self.evo_next(const)
