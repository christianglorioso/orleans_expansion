"""Loads orleans_dex.xlsx and orleans_learnsets.xlsx into plain Python structures.

Used by the apply_*.py stages and by validate_dex.py. Paths are the user-confirmed copies in
C:/Users/chris/orleans_expansion (override with ORLEANS_SHEETS_DIR).
"""
import os
import re
import sys
from pathlib import Path

import openpyxl

SHEETS = Path(os.environ.get("ORLEANS_SHEETS_DIR", r"C:\Users\chris\orleans_expansion"))
ROOT = Path(__file__).resolve().parents[2]


def _wb(name):
    return openpyxl.load_workbook(SHEETS / name, data_only=True)


def load_dex():
    """Rows of the Pokedex sheet (343): dict(num, name, types, stats, abilities, notes, kind)."""
    ws = _wb("orleans_dex.xlsx")["Pokedex"]
    out = []
    for r in list(ws.iter_rows(values_only=True))[1:]:
        if r[0] is None or r[1] is None:
            continue
        name = str(r[1]).strip()
        kind = "mega" if name.startswith("Mega ") else "primal" if name.startswith("Primal ") else "species"
        out.append(dict(
            num=int(r[0]), name=name, kind=kind,
            types=[t for t in (r[2], r[3]) if t],
            stats=dict(hp=int(r[4]), atk=int(r[5]), def_=int(r[6]), spa=int(r[7]), spd=int(r[8]), spe=int(r[9])),
            bst=int(r[10]),
            abilities=[r[11], r[12], r[13]],
            notes=r[14] or "",
        ))
    return out


def _split(s):
    return [x.strip() for x in str(s).split(";") if x.strip()] if s else []


# The project sheets still say "Hail"; the game uses MOVE_SNOWSCAPE in its place (MOVE_HAIL stays
# defined but unused).  Map the sheet's names here rather than editing the sheets.
MOVE_ALIASES = {"hail": "Snowscape"}


def canon_move(name):
    """Sheet move name -> the name the game uses (Hail -> Snowscape)."""
    return MOVE_ALIASES.get(re.sub(r"[^a-z0-9]", "", str(name).lower()), name)


def _dedupe(d):
    """After the Hail->Snowscape rename a species can list Snowscape twice: keep the earliest level-up
    entry (Evo/Form entries count as level 0/1) and one entry per list otherwise."""
    best = None
    for e in d["levelup"]:
        if e[1] == "Snowscape" and (best is None or e[0] < best[0]):
            best = e
    d["levelup"] = [e for e in d["levelup"] if e[1] != "Snowscape" or e is best]
    for key in ("tm", "tutor", "egg"):
        out, got = [], False
        for e in d[key]:
            if e[0] == "Snowscape":
                if got:
                    continue
                got = True
            out.append(e)
        d[key] = out


def parse_move_tok(tok):
    """'Ancient Power †★' -> (name, pre_evo, star)"""
    pre = "†" in tok
    star = "★" in tok
    name = tok.replace("†", "").replace("★", "").strip()
    m = re.match(r"^((?:\d+|Evo|Form) )?(.+)$", name)
    name = (m.group(1) or "") + canon_move(m.group(2))
    return name, pre, star


def load_learnsets():
    """dict dex_num -> dict(name, levelup=[(level, move, pre, star)], tm=[(move,pre,star)], tutor=[...], egg=[...]).

    level is an int; 0 means the Evo move (learned on evolving); 1 for Form moves (form-change moves)
    with tag in a 5th element.
    """
    ws = _wb("orleans_learnsets.xlsx")["By Pokémon"]
    out = {}
    for r in list(ws.iter_rows(values_only=True))[1:]:
        if not isinstance(r[0], (int, float)):
            continue
        d = dict(name=r[1], typing=r[2], levelup=[], tm=[], tutor=[], egg=[])
        for tok in _split(r[4]):
            name, pre, star = parse_move_tok(tok)
            m = re.match(r"^(\d+) (.+)$", name)
            if m:
                d["levelup"].append((int(m.group(1)), m.group(2), pre, star, ""))
            else:
                m = re.match(r"^(Evo|Form) (.+)$", name)
                if not m:
                    raise ValueError(f"bad level-up token {tok!r} for {r[1]}")
                d["levelup"].append((0 if m.group(1) == "Evo" else 1, m.group(2), pre, star, m.group(1)))
        for key, col in (("tm", 6), ("tutor", 8), ("egg", 10)):
            for tok in _split(r[col]):
                d[key].append(parse_move_tok(tok))
        _dedupe(d)
        out[int(r[0])] = d
    return out


def load_hack_additions():
    ws = _wb("orleans_learnsets.xlsx")["Hack Additions"]
    return [r for r in list(ws.iter_rows(values_only=True))[1:] if r[0]]


def load_move_index():
    ws = _wb("orleans_learnsets.xlsx")["Move Index"]
    rows = list(ws.iter_rows(values_only=True))
    body = [((canon_move(r[0]) if r[0] else r[0]),) + tuple(r[1:]) for r in rows[1:]]
    return rows[0], body


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("é", "e"))


def load_move_names():
    """normalized display name -> MOVE_ constant, from the repo's moves_info.h"""
    txt = (ROOT / "src/data/moves_info.h").read_text(encoding="utf-8")
    out = {}
    parts = re.split(r"\n    \[(MOVE_\w+)\] =", txt)
    for i in range(1, len(parts), 2):
        m = re.search(r'\.name = COMPOUND_STRING\("([^"]*)"\)', parts[i + 1])
        if m and parts[i] != "MOVE_HAIL":
            out.setdefault(norm(m.group(1)), parts[i])
    for alias, target in MOVE_ALIASES.items():
        out[alias] = out[norm(target)]
    return out


if __name__ == "__main__":
    d = load_dex()
    l = load_learnsets()
    print(len(d), "dex rows;", len(l), "learnset rows")
