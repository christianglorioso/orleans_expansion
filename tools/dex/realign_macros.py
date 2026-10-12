"""Cosmetic: re-pad the line-continuation backslash of macro field lines that apply_stats.py edited."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_stats
import cdata

BS = chr(92)
for p in cdata.SI_FILES:
    t = p.read_text(encoding="utf-8")
    out = []
    region = []
    changed = False
    lines = t.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("#define") and lines[i].rstrip().endswith(BS):
            j = i
            while j < len(lines) and lines[j].rstrip().endswith(BS):
                j += 1
            seg = "\n".join(lines[i:j + 1])
            new = apply_stats.realign_macro_fields(seg)
            if new != seg:
                changed = True
            out += new.split("\n")
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    if changed:
        p.write_text("\n".join(out), encoding="utf-8", newline="\n")
        print("realigned", p.name)
