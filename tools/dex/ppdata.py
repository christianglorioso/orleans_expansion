"""Parses tools/dex/out/pokemon_pp.c (src/pokemon.c preprocessed with the real build flags by pp.sh)."""
import re
from pathlib import Path

PP = Path(__file__).resolve().parent / "out" / "pokemon_pp.c"


def _num(expr):
    expr = expr.strip()
    m = re.fullmatch(r"\(?(\d+) >= (\d+) \? (\d+) : (\d+)\)?", expr)
    if m:
        a, b, x, y = map(int, m.groups())
        return x if a >= b else y
    if re.fullmatch(r"\d+", expr):
        return int(expr)
    return None


def load(path=PP):
    t = path.read_text(encoding="utf-8", errors="replace")
    i = t.index("const struct SpeciesInfo gSpeciesInfo[] =")
    # top-level entries
    j = t.index("{", i)
    depth, k, start, entries = 0, j, None, {}
    name = None
    n = len(t)
    pos = j + 1
    depth = 1
    # iterate entries
    ent_re = re.compile(r"\[(SPECIES_\w+)\]\s*=\s*")
    while depth > 0 and pos < n:
        m = ent_re.search(t, pos)
        if not m:
            break
        # find opening brace after '='
        b = t.index("{", m.end()) if t[m.end()] == "{" else None
        if b is None:
            break
        d, q = 0, b
        while q < n:
            c = t[q]
            if c == "{":
                d += 1
            elif c == "}":
                d -= 1
                if d == 0:
                    break
            elif c == '"':
                q += 1
                while t[q] != '"':
                    if t[q] == "\\":
                        q += 1
                    q += 1
            q += 1
        entries[m.group(1)] = t[b:q + 1]
        pos = q + 1
        k2 = pos
        while k2 < n and (t[k2].isspace() or t[k2] == ","):
            k2 += 1
        if k2 < n and t[k2] == "}":
            break
    return t, entries


def fields(body):
    d = {}
    stat_names = dict(hp="baseHP", atk="baseAttack", def_="baseDefense", spe="baseSpeed", spa="baseSpAttack", spd="baseSpDefense")
    d["stats"] = {}
    for k, f in stat_names.items():
        m = re.search(r"\." + f + r"\s*=\s*([^,\n]+),", body)
        d["stats"][k] = _num(m.group(1)) if m else None
    m = re.search(r"\.types = \{ (\w+), (\w+) \}", body)
    d["types"] = [m.group(1)] if m and m.group(1) == m.group(2) else [m.group(1), m.group(2)] if m else None
    m = re.search(r"\.abilities = \{ ([^}]*)\}", body)
    ab = [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []
    d["abilities"] = (ab + ["ABILITY_NONE"] * 3)[:3]
    for key, f in (("levelUp", "levelUpLearnset"), ("teach", "teachableLearnset"), ("egg", "eggMoveLearnset"),
                   ("natdex", "natDexNum")):
        m = re.search(r"\." + f + r"\s*=\s*(\w+)", body)
        d[key] = m.group(1) if m else None
    m = re.search(r'\.speciesName = _\("([^"]*)"\)', body)
    d["name"] = m.group(1) if m else None
    m = re.search(r"\.evolutions = ", body)
    d["evo_pos"] = m.start() if m else None
    return d


def levelup_sets(t):
    out = {}
    for m in re.finditer(r"static const struct LevelUpMove (\w+)\[\] = \{(.*?)\n\};", t, re.S):
        out[m.group(1)] = [(mm.group(1), int(mm.group(2))) for mm in re.finditer(r"\{\.move = (\w+), \.level = (\d+)\}", m.group(2))
                           if mm.group(1) != "0xFFFF"]
    return out


def move_sets(t, suffix):
    out = {}
    for m in re.finditer(r"static const u16 (\w+" + suffix + r")\[\] = \{(.*?)\};", t, re.S):
        out[m.group(1)] = [x for x in re.findall(r"MOVE_\w+", m.group(2))]
    return out
