"""Readers for the Battle Frontier data files (src/data/battle_frontier/*.h) and the engine constants.

Used by inventory.py, the generator and frontier_check.py.  Pure text parsing, no build needed.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = Path(os.environ["FRONTIER_OVERLAY"]) if "FRONTIER_OVERLAY" in os.environ else None  # an install tree made by gen_frontier.py --install-to


def src(rel):
    """repo file, or the overlay copy when FRONTIER_OVERLAY holds one"""
    if OVERLAY and (OVERLAY / rel).exists():
        return OVERLAY / rel
    return ROOT / rel


BF = Path(os.environ.get("FRONTIER_DIR", src("src/data/battle_frontier/battle_frontier_mons.h").parent))  # FRONTIER_DIR: lint a dry-run output dir (gen_frontier.py --out)
CONST = (BF / "battle_frontier_mons_const.h") if "FRONTIER_DIR" in os.environ else src("include/constants/battle_frontier_mons.h")


def read(p):
    return Path(p).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")


def mon_consts(path=None):
    """FRONTIER_MON_* name -> index, in file order; plus the NUM and tier markers"""
    t = read(path or CONST)
    return {n: int(v) for n, v in re.findall(r"#define (FRONTIER_MON_\w+)\s+(\d+)\s*$", t, flags=re.M)}


def parse_mons(path=None):
    """list (index order) of dict(const, species, moves, item, ev, nature, ball, ability, gender, raw)"""
    t = read(path or BF / "battle_frontier_mons.h")
    out = []
    for m in re.finditer(r"\[(FRONTIER_MON_\w+)\] = \{(.*?)\n    \},?", t, flags=re.S):
        body = m.group(2)
        g = lambda k: (re.search(r"\." + k + r" = ([^\n]*?),?\n", body + "\n") or [None, None])[1]
        mv = re.search(r"\.moves = \{([^}]*)\}", body)
        ev = re.search(r"TRAINER_PARTY_EVS\(([^)]*)\)", body)
        out.append(dict(const=m.group(1), species=g("species"),
                        moves=[x.strip() for x in mv.group(1).split(",")] if mv else [],
                        item=g("heldItem"), ev=[int(x) for x in ev.group(1).split(",")] if ev else None,
                        nature=g("nature"), ball=g("ball"), ability=g("ability"), gender=g("gender")))
    return out


def parse_pools(path=None):
    """macro name -> list of FRONTIER_MON_* names (macro pools in battle_frontier_trainer_mons.h)"""
    t = read(path or BF / "battle_frontier_trainer_mons.h")
    pools = {}
    bs = re.escape(chr(92)) + chr(10)  # a literal backslash then a newline
    for m in re.finditer(r"#define (FRONTIER_MONS_\w+)(\([^)]*\))? *" + bs + "((?:.*" + bs + ")*.*)", t):
        body = m.group(3)
        pools[m.group(1)] = re.findall(r"FRONTIER_MON_\w+|FRONTIER_MONS_\w+|\b[a-z]\w*\b(?=,)", body)
    return pools


def parse_trainers(path=None):
    """list of dict(const, facilityClass, name, pool) in index order"""
    t = read(path or BF / "battle_frontier_trainers.h")
    out = []
    for m in re.finditer(r"\[(FRONTIER_TRAINER_\w+)\] = \{(.*?)\n    \},?", t, flags=re.S):
        b = m.group(2)
        out.append(dict(const=m.group(1),
                        cls=re.search(r"\.facilityClass = (\w+)", b).group(1),
                        name=re.search(r'\.trainerName = _\("([^"]*)"\)', b).group(1),
                        pool=re.search(r"\.monSet = \(const u16\[\]\)\{([^}]*)\}", b).group(1).strip()))
    return out
