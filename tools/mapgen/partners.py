"""Partner (multi-battle) parties: written into src/data/battle_partners.party and include/constants/battle_partner.h.

PARTNERS in a story_data_chN.py: [(PARTNER_CONST, [(species, level, held item or None), ...][, ivs])]. Sections with the same name are replaced
in place (file order is kept, so a rerun is a no-op), new ids are added at the end and before PARTNER_COUNT in the header.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def partner_block(name, team, iv=28):
    jay = "JAYDEN" in name
    block = [f"=== {name} ===", "Name: " + ("JAYDEN" if jay else "WREN"), "Class: Rival", "Pic: " + ("Brendan" if jay else "May"),
             "Gender: " + ("Male" if jay else "Female"), "Music: " + ("Male" if jay else "Female"), "AI: Basic Trainer", ""]
    for sp, lv, item in team:
        block += [sp + (f" @ {item}" if item else ""), f"Level: {lv}",
                  "IVs: " + " / ".join(f"{iv} {st}" for st in ("HP", "Atk", "Def", "SpA", "SpD", "Spe")), ""]
    return "\n".join(block)


def norm(entry):
    """(const, team) or (const, team, iv) -> (const, team, iv)"""
    return (entry[0], entry[1], entry[2] if len(entry) > 2 else 28)


def rendered(partners, text):
    """text with every named section replaced IN PLACE (new ones appended): idempotent whichever chapter runs first"""
    partners = [norm(e) for e in partners]
    want = {n: partner_block(n, team, iv) for n, team, iv in partners}
    parts = re.split(r"(?m)^(?==== PARTNER_\w+ ===$)", text)
    out, done = [], set()
    for part in parts:
        m = re.match(r"=== (PARTNER_\w+) ===", part)
        if m and m.group(1) in want:
            out.append(want[m.group(1)].rstrip("\n") + "\n\n")
            done.add(m.group(1))
        else:
            out.append(part)
    text = "".join(out).rstrip("\n") + "\n"
    for n, _, _ in partners:
        if n not in done:
            text += "\n" + want[n].rstrip("\n") + "\n"
    return text


def write_partners(partners):
    pp = os.path.join(ROOT, "src", "data", "battle_partners.party")
    text = open(pp, encoding="utf-8").read().replace("\r\n", "\n")
    open(pp, "w", encoding="utf-8", newline="\n").write(rendered(partners, text))
    hp = os.path.join(ROOT, "include", "constants", "battle_partner.h")
    h = open(hp, encoding="utf-8").read().replace("\r\n", "\n")
    have = set(re.findall(r"#define (PARTNER_\w+) \d+", h))
    nxt = int(re.search(r"#define PARTNER_COUNT (\d+)", h).group(1))
    add = ""
    for name, *_ in partners:
        if name not in have:
            add += f"#define {name} {nxt}\n"
            nxt += 1
    h = re.sub(r"#define PARTNER_COUNT \d+", lambda m: add + f"#define PARTNER_COUNT {nxt}", h)
    open(hp, "w", encoding="utf-8", newline="\n").write(h)
    print("wrote partners:", len(partners))
