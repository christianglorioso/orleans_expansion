"""Move data for the Frontier tools, parsed from tools/frontier/out/moves_pp.c (src/move.c preprocessed with the real
build flags by tools/frontier/pp_moves.sh, so every GEN/config expression is already a number)."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PP = ROOT / "tools/frontier/out/moves_pp.c"


def run_pp():
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "/mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/frontier/pp_moves.sh"],
                       capture_output=True, text=True, env={**__import__("os").environ, "MSYS_NO_PATHCONV": "1"})
    if r.returncode:
        raise SystemExit("pp_moves.sh failed:\n" + r.stdout + r.stderr)


def _ev(expr):
    """evaluate the small C expressions the preprocessor leaves: 'a >= b ? x : y', '8 < 2', plain numbers"""
    e = expr.strip()
    for _ in range(4):
        m = re.fullmatch(r"\(?\s*([^?]+?)\s*\?\s*(.+?)\s*:\s*(.+?)\s*\)?", e)
        if not m:
            break
        e = f"({_ev(m.group(2))} if {m.group(1)} else {_ev(m.group(3))})"
    try:
        return int(eval(e, {"__builtins__": {}}, {}))
    except Exception:
        return None


class Move:
    __slots__ = ("const", "name", "effect", "power", "type", "acc", "pp", "target", "priority", "cat", "body")

    def __init__(self, const, body):
        self.const = const
        self.body = body
        g = lambda f: (re.search(r"\." + f + r" = ([^\n]*?),\n", body) or [None, None])[1]
        nm = re.search(r'\.name = COMPOUND_STRING\("([^"]*)"\)', body)
        self.name = nm.group(1) if nm else const
        self.effect = g("effect")
        self.power = _ev(g("power") or "0") or 0
        ty = g("type") or "TYPE_NORMAL"
        if "?" in ty:  # e.g. '1 ? TYPE_DARK : TYPE_NORMAL' (config expression): take the branch the build takes
            mm = re.match(r"\(?\s*(\d+)\s*\?\s*(TYPE_\w+)\s*:\s*(TYPE_\w+)", ty)
            ty = (mm.group(2) if mm.group(1) != "0" else mm.group(3)) if mm else re.search(r"TYPE_\w+", ty).group(0)
        self.type = ty
        self.acc = _ev(g("accuracy") or "0") or 0
        self.pp = _ev(g("pp") or "0") or 0
        self.target = g("target")
        self.priority = _ev(g("priority") or "0") or 0
        c = g("category")
        self.cat = {"DAMAGE_CATEGORY_PHYSICAL": "phys", "DAMAGE_CATEGORY_SPECIAL": "spec", "DAMAGE_CATEGORY_STATUS": "status"}.get(c, "status")

    def flag(self, name):
        m = re.search(r"\." + name + r" = ([^\n]*?),\n", self.body)
        return bool(m and _ev(m.group(1)))

    @property
    def damaging(self):
        return self.cat != "status"

    @property
    def spread(self):
        return self.target in ("TARGET_BOTH", "TARGET_FOES_AND_ALLY", "TARGET_ALL_BATTLERS")

    def has_effect(self, token):
        return token in self.body


def load():
    t = PP.read_text(encoding="utf-8", errors="replace")
    i = t.index("const struct MoveInfo gMovesInfo[")
    parts = re.split(r"\n    \[(MOVE_\w+)\] =\n", t[i:])
    out = {}
    for k in range(1, len(parts), 2):
        body = parts[k + 1]
        j = body.find("\n    },")
        out[parts[k]] = Move(parts[k], body[:j] if j > 0 else body)
    return out
