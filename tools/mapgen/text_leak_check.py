"""Find spec / mockup phrasing that leaked into NPC, sign and interior text.

usage (from the decomp root): python tools/mapgen/text_leak_check.py
Scans every `.string` text label in data/maps/<Orleans map>/scripts.inc and the story .inc files for: a box that starts
lowercase, designer parentheses, third-person notes ("gives", "tells"...), draft / proposed / placeholder words, and lines
longer than 36 characters (the box width). Exit 1 if anything is found.
"""
import glob
import os
import re
import sys

ROOT = os.getcwd()
MAPS = os.path.join(ROOT, "data", "maps")
ORLEANS = re.compile(r"^(IsleMarais|GrandOak|OldWater|StormsEdge|CrescentCity|PointeRouge|CampCocodrie|LutinsHollow|Redfield|LandsEnd|"
                     r"Route([1-9]|1\d|2[0-5])$|OldestShrine|Orleans)")
NOTE_WORDS = re.compile(r"\b(draft|proposed|placeholder|tbd|todo|mockup|spec|marker|to be scripted|scripted|the player|npc)\b", re.I)
THIRD = re.compile(r"^(gives|tells|hands|logs|swaps|sells|retreats|fights|opens|raises|watches|casts|sign up here|wants|picks|"
                   r"answer three|no reflection)\b", re.I)
PAREN = re.compile(r"\([^)]*[a-z]{3}")
STRING = re.compile(r'\.string\s+"((?:[^"\\]|\\.)*)"')
LABEL = re.compile(r"^(\w+):\s*$")


def texts(path):
    label, parts = None, []
    for line in open(path, encoding="utf-8", errors="ignore"):
        m = LABEL.match(line.rstrip())
        s = STRING.search(line)
        if m:
            if label and parts:
                yield label, "".join(parts)
            label, parts = m.group(1), []
        elif s and label:
            parts.append(s.group(1))
        elif line.strip() and not line.lstrip().startswith("@") and label and parts:
            yield label, "".join(parts)
            label, parts = None, []
    if label and parts:
        yield label, "".join(parts)


def problems(body):
    out = []
    plain = re.sub(r"\{[^}]*\}", "X", body).rstrip("$")
    first = re.sub(r"^(\\[nlp])+", "", plain)
    if first and first[0].islower():
        out.append("starts lowercase")
    if THIRD.match(first):
        out.append("third-person note")
    if PAREN.search(plain):
        out.append("parentheses")
    if NOTE_WORDS.search(plain):
        out.append("designer word")
    for seg in re.split(r"\\[nlp]", plain):
        if len(seg) > 36:
            out.append("line over 36 (%d)" % len(seg))
            break
    return out


def main():
    found = 0
    files = [p for p in glob.glob(os.path.join(MAPS, "*", "scripts.inc")) if ORLEANS.match(os.path.basename(os.path.dirname(p)))]
    files += glob.glob(os.path.join(ROOT, "tools", "mapgen", "story", "*.inc"))
    for p in sorted(files):
        for label, body in texts(p):
            pr = problems(body)
            if pr:
                found += 1
                print("%s: %s: %s\n    %s" % (os.path.relpath(p, ROOT), label, ", ".join(pr), body[:110]))
    print("text_leak_check: %s (%d suspicious, %d files)" % ("FAIL" if found else "ok", found, len(files)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
