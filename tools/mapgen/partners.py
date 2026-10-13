"""Partner (multi-battle) parties: written into src/data/battle_partners.party and include/constants/battle_partner.h.

PARTNERS in a story_data_chN.py: [(PARTNER_CONST, [(species, level, held item or None), ...])]. Sections with the same name are replaced, new
ids are added before PARTNER_COUNT. (Wren's three Chapter 7 partners were written by hand; this tool only touches the names it is given.)
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def write_partners(partners):
    pp = os.path.join(ROOT, "src", "data", "battle_partners.party")
    text = open(pp, encoding="utf-8").read().replace("\r\n", "\n")
    names = {n for n, _ in partners}
    parts = re.split(r"(?m)^(?==== PARTNER_\w+ ===$)", text)
    keep = []
    for p in parts:
        m = re.match(r"=== (PARTNER_\w+) ===", p)
        if not (m and m.group(1) in names):
            keep.append(p)
    out = "".join(keep).rstrip("\n") + "\n"
    for name, team in partners:
        jay = "JAYDEN" in name
        block = [f"=== {name} ===", "Name: " + ("JAYDEN" if jay else "WREN"), "Class: Rival", "Pic: " + ("Brendan" if jay else "May"),
                 "Gender: " + ("Male" if jay else "Female"), "Music: " + ("Male" if jay else "Female"), "AI: Basic Trainer", ""]
        for sp, lv, item in team:
            block += [sp + (f" @ {item}" if item else ""), f"Level: {lv}",
                      "IVs: " + " / ".join(f"28 {st}" for st in ("HP", "Atk", "Def", "SpA", "SpD", "Spe")), ""]
        out += "\n" + "\n".join(block)
    open(pp, "w", encoding="utf-8", newline="\n").write(out)
    hp = os.path.join(ROOT, "include", "constants", "battle_partner.h")
    h = open(hp, encoding="utf-8").read().replace("\r\n", "\n")
    have = set(re.findall(r"#define (PARTNER_\w+) \d+", h))
    nxt = int(re.search(r"#define PARTNER_COUNT (\d+)", h).group(1))
    add = ""
    for name, _ in partners:
        if name not in have:
            add += f"#define {name} {nxt}\n"
            nxt += 1
    h = re.sub(r"#define PARTNER_COUNT \d+", lambda m: add + f"#define PARTNER_COUNT {nxt}", h)
    open(hp, "w", encoding="utf-8", newline="\n").write(h)
    print("wrote partners:", len(partners))
