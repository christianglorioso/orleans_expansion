"""Text-box lint for tools/mapgen/story/*.inc (Gen-3 limits, the brief's rules for Orleans dialogue).

For every `.string "..."` block (a label's strings up to the one ending in $) it checks
  * each line is at most 36 characters ({PLAYER} counts as 7, {RIVAL} 7, other {..} codes as 0)
  * each page (text between \\p) is at most 2 lines (lines are separated by \\n or \\l)
  * only ASCII plus e-acute/E-acute and the curly double quotes the charmap has (no other Unicode)
  * the block ends with $
usage: python tools/mapgen/story_lint.py [files...]   (default: every story/*.inc)
Exit code 1 if anything is wrong.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
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
            if width(r) > 36:
                out.append(f"{path}:{n}: {label}: line is {width(r)} chars (max 36): {r!r}")
    return out


def main(argv):
    files = argv or sorted(glob.glob(os.path.join(HERE, "story", "*.inc")))
    bad = []
    for f in files:
        bad += lint(f)
    for p in bad:
        print(p)
    print(f"{len(files)} files, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
