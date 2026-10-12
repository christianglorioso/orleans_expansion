"""Swap the Orleans trainers' off-dex species for Orleans-dex species of the same type/role (user decision 2026-10-12).
Applies to src/data/trainers.party and tools/mapgen/trainers/*.party. Idempotent."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SWAPS = {
    "TRAINER_ORLEANS_ROUTE1_BUG_CATCHER": {"Wurmple": "Nincada", "Venonat": "Ledyba"},
    "TRAINER_ORLEANS_ROUTE1_LASS": {"Hoppip": "Budew-Orleanian"},
    "TRAINER_ORLEANS_GRAND_OAK_GYM_RANGER": {"Sewaddle": "Foongus"},
    "TRAINER_ORLEANS_GRAND_OAK_GYM_AROMA_LADY": {"Hoppip": "Oddish"},
    "TRAINER_ORLEANS_STORMS_EDGE_GYM_ELECTRICIAN": {"Elekid": "Magnemite"},
    "TRAINER_ORLEANS_CRESCENT_GYM_MEDIUM": {"Abra": "Inkay", "Natu": "Hoothoot"},
    "TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_DARK": {"Poochyena": "Sandile", "Murkrow": "Spearow-Orleanian", "Houndour": "Impidimp"},
    "TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT": {"Mightyena": "Krokorok"},
}


def process(path):
    txt = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    parts = re.split(r"^(=== TRAINER_\w+ ===\n)", txt, flags=re.M)
    changed = 0
    for i in range(1, len(parts), 2):
        const = parts[i].strip().strip("=").strip()
        if const not in SWAPS:
            continue
        paras = parts[i + 1].split("\n\n")
        for k, para in enumerate(paras):
            lines = para.split("\n")
            for old, new in SWAPS[const].items():
                m = re.match(r"^(?P<a>(?:.+ \()?)" + old + r"(?P<b>\)?(?: \([MF]\))?(?: @ .+)?)$", lines[0])
                if m and k > 0:
                    lines[0] = m.group("a") + new + m.group("b")
                    changed += 1
            paras[k] = "\n".join(lines)
        parts[i + 1] = "\n\n".join(paras)
    if changed:
        path.write_text("".join(parts), encoding="utf-8", newline="\n")
    return changed


if __name__ == "__main__":
    n = process(ROOT / "src/data/trainers.party")
    for p in sorted((ROOT / "tools/mapgen/trainers").glob("*.party")):
        n += process(p)
    print("swapped", n)
