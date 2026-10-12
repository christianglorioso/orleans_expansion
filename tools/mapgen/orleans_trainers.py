"""Orleans trainer slots: puts the trainers in tools/mapgen/trainers/*.party into the game.

The decomp has a fixed number of trainer ids (TRAINERS_COUNT = 864, one defeated-flag each; raising it costs save space),
and the slice used the last 9 free ones. Every later Orleans trainer therefore takes over an unused Hoenn slot, the way
TRAINER_MAGNOLIA took TRAINER_ROXANNE_1:
  * include/constants/opponents.h gets a marked block of `#define TRAINER_ORLEANS_X TRAINER_<hoenn slot>` aliases;
  * src/data/trainers.party loses the Hoenn trainer's section and gains the Orleans one (appended at the end).
The assignment is remembered in trainers/slots.json (name -> Hoenn constant), so ids never change between runs.
Gym leaders are pinned to their Hoenn counterparts (FIXED below); everyone else takes the next free slot in POOL.

usage (from the decomp root): python tools/mapgen/orleans_trainers.py [--check]
  --check   print the table and the problems, write nothing
Safe to re-run: it rewrites its own blocks and never touches anything else.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(HERE, "trainers")
SLOTS = os.path.join(SRC_DIR, "slots.json")
OPP = "include/constants/opponents.h"
PARTY = "src/data/trainers.party"

B_OPP, E_OPP = "// --- orleans trainers (begin) ---", "// --- orleans trainers (end) ---"

# Hoenn ids 36..260 (the route trainers and their rematch rows) are free for Orleans; leaders and E4 are kept apart.
POOL_RANGE = (36, 260)
# Gym leaders and the other named slots, pinned (name -> Hoenn constant). Magnolia is already TRAINER_ROXANNE_1.
FIXED = {
    "TRAINER_ECLAIR": "TRAINER_WATTSON_1",
    "TRAINER_FIFOLET": "TRAINER_BRAWLY_1",
    "TRAINER_KINGFISHER": "TRAINER_WINONA_1",
    "TRAINER_BOUDREAUX": "TRAINER_TATE_AND_LIZA_1",  # the brothers fight as two trainers in one double battle (trainerbattle_two_trainers)
    "TRAINER_LUTIN": "TRAINER_NORMAN_1",
    "TRAINER_CAYENNE": "TRAINER_FLANNERY_1",
    "TRAINER_HERON": "TRAINER_JUAN_1",
}


def vanilla_slots():
    """Hoenn trainer constants in POOL_RANGE, in id order."""
    out = []
    for line in open(OPP, encoding="utf-8"):
        m = re.match(r"#define (TRAINER_\w+)\s+(\d+)\s*$", line)
        if m and POOL_RANGE[0] <= int(m.group(2)) <= POOL_RANGE[1]:
            out.append((int(m.group(2)), m.group(1)))
    return [n for _, n in sorted(out)]


def read_sources():
    """name -> section text (header line included), in file order across trainers/*.party"""
    secs = {}
    for path in sorted(glob.glob(os.path.join(SRC_DIR, "*.party"))):
        text = open(path, encoding="utf-8").read()
        parts = re.split(r"(?m)^(?==== TRAINER_\w+ ===$)", text)
        for p in parts:
            m = re.match(r"=== (TRAINER_\w+) ===\n", p)
            if m:
                if m.group(1) in secs:
                    sys.exit(f"duplicate trainer {m.group(1)} ({path})")
                secs[m.group(1)] = p.rstrip("\n") + "\n"
    return secs


def strip_section(text, name):
    return re.sub(rf"(?ms)^=== {name} ===\n.*?(?=^=== |\Z)", "", text)


def main(argv):
    check = "--check" in argv
    secs = read_sources()
    slots = json.load(open(SLOTS, encoding="utf-8")) if os.path.exists(SLOTS) else {}
    pool = vanilla_slots()
    used = set(slots.values()) | set(FIXED.values())
    problems = []
    for name in secs:
        if name in FIXED:
            slots[name] = FIXED[name]
        elif name not in slots:
            free = next((s for s in pool if s not in used), None)
            if free is None:
                sys.exit("trainer pool is empty: raise MAX_TRAINERS_COUNT or widen POOL_RANGE")
            slots[name] = free
            used.add(free)
    for name, slot in slots.items():
        if name not in secs:
            problems.append(f"{name} is in slots.json but has no section (kept reserved)")
    for name in secs:
        if len(re.findall(r"(?m)^Name: .{13,}", secs[name])):
            problems.append(f"{name}: trainer name longer than 12 characters")
    print(f"{len(secs)} Orleans trainers, {len(pool) - len(used & set(pool))} pool slots left")
    for name in secs:
        print(f"  {name:48s} -> {slots[name]}")
    for p in problems:
        print("PROBLEM:", p)
    if check:
        return
    json.dump(slots, open(SLOTS, "w", encoding="utf-8", newline="\n"), indent=1)
    # opponents.h: the alias block goes right before the NOTE comment (after the slice's own ids)
    opp = open(OPP, encoding="utf-8").read()
    if B_OPP in opp:
        opp = re.sub(rf"(?s){re.escape(B_OPP)}.*?{re.escape(E_OPP)}\n", "", opp)
    block = B_OPP + "\n" + "".join(f"#define {n:48s} {slots[n]}\n" for n in secs) + E_OPP + "\n\n"
    anchor = "// NOTE: Because each Trainer uses a flag"
    if anchor not in opp:
        sys.exit("opponents.h anchor not found")
    opp = opp.replace(anchor, block + anchor, 1)
    open(OPP, "w", encoding="utf-8", newline="\n").write(opp)
    # trainers.party (trainerproc has no comment syntax between sections, so no markers): drop the Hoenn sections we
    # took over and any earlier copy of an Orleans section, then append the current ones
    party = open(PARTY, encoding="utf-8").read()
    for name in secs:
        party = strip_section(party, slots[name])
    for name in slots:
        party = strip_section(party, name)
    party = party.rstrip("\n") + "\n\n" + "\n\n".join(secs[n] for n in secs) + "\n"
    open(PARTY, "w", encoding="utf-8", newline="\n").write(party)
    print("wrote", OPP, "and", PARTY)


if __name__ == "__main__":
    main(sys.argv[1:])
