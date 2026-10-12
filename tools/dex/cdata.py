"""Helpers for reading/rewriting src/data/pokemon/species_info/*.h species blocks."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SI_DIR = ROOT / "src/data/pokemon/species_info"
SI_FILES = [SI_DIR / f"gen_{i}_families.h" for i in range(1, 10)]
BLOCK_RE = re.compile(r"^    \[(SPECIES_\w+)\] =\n    \{\n(.*?)\n    \},\n", re.M | re.S)

TYPE_NAMES = {t: "TYPE_" + t.upper() for t in
              "Normal Fighting Flying Poison Ground Rock Bug Ghost Steel Fire Water Grass Electric Psychic Ice Dragon Dark Fairy".split()}
STAT_FIELDS = dict(hp="baseHP       ", atk="baseAttack   ", def_="baseDefense  ", spe="baseSpeed    ",
                   spa="baseSpAttack ", spd="baseSpDefense")


class SpeciesFiles:
    def __init__(self):
        self.text = {p: p.read_text(encoding="utf-8") for p in SI_FILES}

    def find(self, const):
        for p, t in self.text.items():
            m = re.search(r"^    \[" + const + r"\] =\n    \{\n(.*?)\n    \},\n", t, re.M | re.S)
            if m:
                return p, m
        return None, None

    def get(self, const):
        p, m = self.find(const)
        return m.group(0) if m else None

    def put(self, const, new_block):
        p, m = self.find(const)
        assert m, const
        t = self.text[p]
        self.text[p] = t[:m.start()] + new_block + t[m.end():]

    def save(self):
        for p, t in self.text.items():
            p.write_text(t, encoding="utf-8", newline="\n")

    def all_consts(self):
        out = []
        for p in SI_FILES:
            out += [m.group(1) for m in BLOCK_RE.finditer(self.text[p])]
        return out


def get_field(block, name):
    m = re.search(r"^        \." + name + r"\s*=\s*(.*?),?$", block, re.M)
    return m.group(1) if m else None


def set_stats_types(block, d):
    """d: sheet dict. Returns new block text."""
    for k, f in STAT_FIELDS.items():
        v = d["stats"][k]
        block, n = re.subn(r"^(        \." + f.strip() + r"\s*=\s*)[^,\n]+,", lambda m: m.group(1) + str(v) + ",", block, flags=re.M)
        assert n == 1, (f, n)
    ts = [TYPE_NAMES[t] for t in d["types"]]
    block, n = re.subn(r"^        \.types = MON_TYPES\([^\n]*\),", "        .types = MON_TYPES(" + ", ".join(ts) + "),", block, flags=re.M)
    assert n == 1, "types"
    return block


def set_abilities(block, abil_consts):
    a = list(abil_consts) + ["ABILITY_NONE"] * 3
    line = "        .abilities = { %s, %s, %s }," % tuple(a[:3])
    block, n = re.subn(r"^        \.abilities = \{[^\n]*\},", line, block, flags=re.M)
    assert n == 1, "abilities"
    return block


# ---------------------------------------------------------------------------
# mini macro expansion so macro-built species (Flabebe colours, Ogerpon, Eevee abilities...) can be read
_DEF_RE = re.compile(r"^#define\s+(\w+)(\(([^)]*)\))?\s*(.*)$")


def _collect_defines(text):
    defs = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#define"):
            full = ln
            while full.rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                full = full.rstrip()[:-1] + " " + lines[i]
            m = _DEF_RE.match(full.strip())
            if m:
                params = [p.strip() for p in m.group(3).split(",")] if m.group(2) else None
                defs[m.group(1)] = (params, m.group(4))
        i += 1
    return defs


def _split_args(s):
    args, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    args.append(cur.strip())
    return args


def expand(text, defs, depth=0):
    if depth > 6:
        return text
    out, i = "", 0
    n = len(text)
    changed = False
    while i < n:
        m = re.compile(r"[A-Za-z_]\w*").match(text, i)
        if not m:
            out += text[i]
            i += 1
            continue
        name = m.group(0)
        j = m.end()
        if name in defs and not name.startswith("SPECIES_") and not name.startswith("ABILITY_"):
            params, body = defs[name]
            if params is None:
                if name.isupper() and "_" in name or name in ("ROTOM_FAMILY_TYPES", "EEVEE_ABILITIES"):
                    out += body
                    changed = True
                    i = j
                    continue
            else:
                if j < n and text[j] == "(":
                    k, d = j, 0
                    while k < n:
                        if text[k] == "(":
                            d += 1
                        elif text[k] == ")":
                            d -= 1
                            if d == 0:
                                break
                        k += 1
                    args = _split_args(text[j + 1:k])
                    b = body
                    for p, a in zip(params, args):
                        b = re.sub(r"\b" + re.escape(p) + r"\b", a.replace("\\", "\\\\"), b)
                    b = re.sub(r"\s*##\s*", "", b)
                    out += b
                    changed = True
                    i = k + 1
                    continue
        out += name
        i = j
    out = out.replace("\\n", " ")
    return expand(out, defs, depth + 1) if changed else out


_DEFS = None


def defs():
    global _DEFS
    if _DEFS is None:
        t = ""
        for p in SI_FILES:
            t += p.read_text(encoding="utf-8") + "\n"
        _DEFS = _collect_defines(t)
    return _DEFS


def effective(block_text, species_line_fallback=None):
    """expanded field view of a block: dict(types, stats, abilities, ...)"""
    # for `[SPECIES_X] = MACRO(args),` one-liners the caller passes the text after '='
    t = expand(block_text, defs())
    out = {}
    for k, f in STAT_FIELDS.items():
        ms = re.findall(r"\." + f.strip() + r"\s*=\s*(\d+)", t)
        out[k] = int(ms[-1]) if ms else None
    ty = re.findall(r"\.types = MON_TYPES\(([^)]*)\)", t)
    out["types"] = [x.strip() for x in ty[-1].split(",")] if ty else None
    if out["types"] and len(out["types"]) == 2 and out["types"][0] == out["types"][1]:
        out["types"] = out["types"][:1]
    # abilities: the active branch of any #if P_UPDATED_ABILITIES >= GEN_4 chain is the first
    ab = re.findall(r"\.abilities = \{([^}]*)\}", t)
    out["abilities"] = [x.strip() for x in ab[0].split(",") if x.strip()] if ab else None
    return out
