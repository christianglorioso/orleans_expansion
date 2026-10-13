"""Audit: every item the Orleans dex needs (evolution items, Mega stones, orbs, masks) and where the player can get it.

usage (from the decomp root): python tools/dex/obtain_audit.py
Needs: the species info files (evolutions, form change tables) and the dex list (tools/dex/out/dex_order.txt); sources are item balls, hidden items,
`giveitem` in scripts, shop lists (pokemart / .2byte ITEM_ in a mart list) and the NPC trade table. Prints one line per required item:
the first source found (and how many), or MISSING. Exit code 1 if anything is missing.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)


def dex_species():
    out = set()
    for line in open("tools/dex/out/dex_order.txt", encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            out.add(parts[2])
    return out


def required_items(species):
    """item const -> why"""
    need = {}
    for path in glob.glob("src/data/pokemon/species_info/*.h"):
        text = open(path, encoding="utf-8").read()
        for m in re.finditer(r"\[(SPECIES_\w+)\]\s*=\s*\{", text):
            sp = m.group(1)
            if sp not in species:
                continue
            seg_end = text.find("\n    },\n", m.end())
            seg = text[m.end():seg_end if seg_end > 0 else m.end() + 6000]
            ev = seg.find(".evolutions =")
            if ev < 0:
                continue
            evseg = seg[ev:seg.find("{ 0xFFFF }", ev)]
            for it in re.findall(r"(ITEM_\w+)", evseg):
                if it in ("ITEM_POKE_BALL", "ITEM_NONE", "ITEM_COUNT"):
                    continue
                need.setdefault(it, f"evolution of {sp}")
    # Mega stones and orbs: form change tables of species in the dex
    ft = open("src/data/pokemon/form_change_tables.h", encoding="utf-8").read()
    for m in re.finditer(r"static const struct FormChange s(\w+)FormChangeTable\[\] =\s*\{(.*?)\n\};", ft, re.S):
        body = m.group(2)
        for mm in re.finditer(r"FORM_CHANGE_BATTLE_(?:MEGA_EVOLUTION_ITEM|PRIMAL_REVERSION),\s*(SPECIES_\w+),\s*(ITEM_\w+)", body):
            base = "SPECIES_" + re.sub(r"(?<!^)(?=[A-Z])", "_", m.group(1)).upper()
            if base not in species and not any(x.startswith(base) for x in species):
                continue
            need.setdefault(mm.group(2), f"Mega/primal form {mm.group(1)}")
    for it, why in (("ITEM_HEARTHFLAME_MASK", "Ogerpon (Hearthflame Mask)"), ("ITEM_WELLSPRING_MASK", "Ogerpon (Wellspring Mask)"),
                    ("ITEM_CORNERSTONE_MASK", "Ogerpon (Cornerstone Mask)"), ("ITEM_BLUE_ORB", "Primal Kyogre"), ("ITEM_RED_ORB", "Primal Groudon"),
                    ("ITEM_MEGA_RING", "every Mega Evolution (the Cypress Charm)"), ("ITEM_DIVING_GEAR", "the Drowned Temple dive"),
                    ("ITEM_LANTERN", "the Salt Cathedral shaft"), ("ITEM_SHINY_CHARM", "3 shiny rolls instead of 1 (Lafayette, every base species of the regional dex caught)")):
        need.setdefault(it, why)
    return need


def sources():
    src = {}

    def add(item, how):
        src.setdefault(item, []).append(how)
    for f in glob.glob("data/maps/*/map.json"):
        if "Frlg" in f:
            continue
        d = json.load(open(f, encoding="utf-8"))
        name = os.path.basename(os.path.dirname(f))
        for o in d.get("object_events", []):
            if o.get("graphics_id") == "OBJ_EVENT_GFX_ITEM_BALL" and str(o.get("trainer_sight_or_berry_tree_id", "")).startswith("ITEM_"):
                add(o["trainer_sight_or_berry_tree_id"], f"ball in {name}")
        for b in d.get("bg_events", []):
            if b.get("type") == "hidden_item":
                add(b["item"], f"hidden in {name}")
    for f in glob.glob("data/maps/*/scripts.inc") + glob.glob("data/scripts/*.inc"):
        if "Frlg" in f:
            continue
        text = open(f, encoding="utf-8", errors="replace").read()
        name = os.path.basename(os.path.dirname(f)) if "maps" in f else os.path.basename(f)
        for it in re.findall(r"giveitem\s+(ITEM_\w+)", text):
            add(it, f"given in {name}")
        for it in re.findall(r"additem\s+(ITEM_\w+)", text):
            add(it, f"given in {name}")
        for blk in re.findall(r"pokemartlistend", text):
            pass
        for m in re.finditer(r"\.2byte (ITEM_\w+)", text):
            add(m.group(1), f"sold in {name}")
    # held items of wild mons are not counted (they are not reliable)
    return src


def main():
    sp = dex_species()
    need = required_items(sp)
    for n in ("HP_UP", "PROTEIN", "IRON", "CALCIUM", "ZINC", "CARBOS"):  # SoulGold's EX vitamins (max the stat's EV)
        need[f"ITEM_{n}_EX"] = "EX vitamin (SoulGold port)"
    src = sources()
    missing = []
    for it in sorted(need):
        s = src.get(it)
        print(f"{it:28s} {'MISSING' if not s else s[0] + (' (+%d)' % (len(s) - 1) if len(s) > 1 else '')}   <- {need[it]}")
        if not s:
            missing.append(it)
    # trades the dex relies on
    trade = open("src/data/trade.h", encoding="utf-8").read() if os.path.exists("src/data/trade.h") else ""
    print("\ntrade table species:", sorted(set(re.findall(r"SPECIES_\w+", trade)))[:20])
    rows = ["# Dex-required items and where the player gets them (generated by tools/dex/obtain_audit.py; do not edit)", "",
            "| Item | Needed for | Source (first of n) |", "|---|---|---|"]
    for it in sorted(need):
        sc = src.get(it)
        rows.append(f"| {it} | {need[it]} | {(sc[0] + (' (+%d more)' % (len(sc) - 1) if len(sc) > 1 else '')) if sc else 'MISSING'} |")
    rows += ["", "Missing: " + (", ".join(missing) if missing else "none")]
    open("tools/dex/obtain_report.md", "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("\nmissing:", missing or "none")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
