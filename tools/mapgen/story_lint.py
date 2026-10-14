"""Text-box lint for tools/mapgen/story/*.inc (Gen-3 limits, the brief's rules for Orleans dialogue).

For every `.string "..."` block (a label's strings up to the one ending in $) it checks
  * each line is at most 36 characters ({PLAYER} counts as 7, {RIVAL} 7, other {..} codes as 0)
  * each page (text between \\p) is at most 2 lines (lines are separated by \\n or \\l)
  * only ASCII plus e-acute/E-acute and the curly double quotes the charmap has (no other Unicode)
  * the block ends with $
usage: python tools/mapgen/story_lint.py [files...]   (default: every story/*.inc, plus the object caps and the fast source-vs-generated drift check)
Exit code 1 if anything is wrong.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OK_NON_ASCII = set("éÉ“”¥")  # accented e, curly quotes and the yen sign: all in charmap.txt
CODES = {"PLAYER": 7, "RIVAL": 7, "STR_VAR_1": 12, "STR_VAR_2": 12, "STR_VAR_3": 12}


def width(s):
    s = re.sub(r"\{(\w+)\}", lambda m: "x" * CODES.get(m.group(1), 0), s)
    return len(s)


def lint(path):
    problems = []
    lines = open(path, encoding="utf-8").read().split("\n")
    label, buf, start = None, [], 0
    for n, line in enumerate(lines, 1):
        m = re.match(r"^(\w+):\s*$", line)
        if m:
            label = m.group(1)
        s = re.match(r'^\t\.string "(.*)"\s*$', line)
        if s:
            if not buf:
                start = n
            buf.append(s.group(1))
            if s.group(1).endswith("$"):
                text = "".join(buf)[:-1]
                problems += check(path, label, start, text)
                buf = []
        elif buf and line.strip() and not line.startswith("@"):
            problems.append(f"{path}:{n}: {label}: string block not closed with $ before this line")
            buf = []
    if buf:
        problems.append(f"{path}:{start}: {label}: string block not closed with $")
    return problems


def check(path, label, n, text):
    out = []
    for ch in set(text):
        if ord(ch) > 127 and ch not in OK_NON_ASCII:
            out.append(f"{path}:{n}: {label}: character {ch!r} is not in the charmap subset")
    for pi, page in enumerate(text.split("\\p")):
        rows = re.split(r"\\n|\\l", page)
        if len(rows) > 2:
            out.append(f"{path}:{n}: {label}: page {pi + 1} has {len(rows)} lines (max 2): {page[:50]!r}")
        for r in rows:
            if width(r) > 36 and not label.endswith("_BallLooks"):   # "This female, Adamant CHIKORITA" is 30 real characters (the codes are counted at 12 each)
                out.append(f"{path}:{n}: {label}: line is {width(r)} chars (max 36): {r!r}")
    return out


def lint_object_cap():
    """Object limits (audit ch4 NEW1): a map holds at most 64 object templates, and the game keeps at most 16 objects alive at once
    (OBJECT_EVENTS_COUNT; slot 0 is the player), so no 19x12 window (the spawn area around the camera) may hold more than 15 of a
    map's objects, hidden ones included (a flag only hides after the object is spawned). Extra ones silently never appear and a
    script that applymovements one hangs."""
    import json
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "..", "..", "data", "maps", "*", "map.json"))):
        try:
            objs = json.load(open(path, encoding="utf-8")).get("object_events", [])
        except (OSError, ValueError):
            continue
        name = os.path.basename(os.path.dirname(path))
        if not re.match(r"^(IsleMarais|GrandOak|OldWater|StormsEdge|CrescentCity|PointeRouge|CampCocodrie|LutinsHollow|Redfield|LandsEnd|"
                        r"Route([1-9]|1\d|2[0-5])$|OldestShrine)", name):
            continue   # the Hoenn leftovers (Frontier, Route 111...) are vanilla
        if len(objs) > 64:
            out.append(f"{name}: {len(objs)} object templates (max 64)")
        pts = [(o["x"], o["y"]) for o in objs]
        worst = 0
        for x0, _ in pts:
            for _, y0 in pts:
                worst = max(worst, sum(1 for x, y in pts if x0 <= x < x0 + 19 and y0 <= y < y0 + 12))
        if worst > 15:
            out.append(f"{name}: {worst} objects inside one 19x12 window (max 15: slot 0 is the player)")
    return out


def lint_drift():
    """source vs generated drift (gen_drift_check.py, the fast half: trainer tables, party files, partners, story splice); the slow half
    (outdoor and interior generators) runs with `python tools/mapgen/gen_drift_check.py`"""
    import gen_drift_check
    cwd = os.getcwd()
    os.chdir(gen_drift_check.ROOT)
    try:
        return [p for p in gen_drift_check.check_trainers() + gen_drift_check.check_splice()]
    finally:
        os.chdir(cwd)


def main(argv):
    files = argv or sorted(glob.glob(os.path.join(HERE, "story", "*.inc")))
    bad = []
    for f in files:
        bad += lint(f)
    if not argv:
        bad += lint_object_cap()
        bad += lint_drift()
    for p in bad:
        print(p)
    print(f"{len(files)} files, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
