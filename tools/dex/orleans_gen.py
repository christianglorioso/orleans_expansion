"""Shared helpers for the stages that add species (forms, Megas)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdata
import species_map as sm

ROOT = cdata.ROOT
SPECIES_H = ROOT / "include/constants/species.h"
FORM_SPECIES_H = ROOT / "src/data/pokemon/form_species_tables.h"
FORM_CHANGE_H = ROOT / "src/data/pokemon/form_change_tables.h"
SPECIES_INFO_H = ROOT / "src/data/pokemon/species_info.h"
ORL_FORMS_H = cdata.SI_DIR / "orleans_forms.h"
ORL_MEGAS_H = cdata.SI_DIR / "orleans_megas.h"
BS = chr(92)


def ensure_species_consts():
    """add SPECIES_* ids for all new Orleans species (idempotent)"""
    t = SPECIES_H.read_text(encoding="utf-8")
    if sm.NEW_SPECIES_ORDER[0] in t:
        return 0
    start = int(re.search(r"SPECIES_GLIMMORA_MEGA = (\d+),", t).group(1)) + 1
    lines = "".join(f"    {c} = {start + i},\n" for i, c in enumerate(sm.NEW_SPECIES_ORDER))
    marker = "    // Add any custom species between here and SPECIES_CUSTOM_END\n"
    assert marker in t
    t = t.replace(marker, marker + lines)
    SPECIES_H.write_text(t, encoding="utf-8", newline="\n")
    return len(sm.NEW_SPECIES_ORDER)


def pascal(const):
    """SPECIES_ROSERADE_ORLEANIAN -> RoseradeOrleanian"""
    return "".join(w.capitalize() for w in const[len("SPECIES_"):].split("_"))


def table_name(base_const):
    return f"s{pascal(base_const)}FormSpeciesIdTable"


def get_field_line(block, field):
    m = re.search(r"^        \." + field + r" = ([^\n]*?),?\n", block, re.M)
    return m.group(1) if m else None


def remove_field(block, field):
    """remove a (possibly multi-line, paren-balanced) `.field = ...,` entry"""
    m = re.search(r"^        \." + field + r"\b[^\n]*\n", block, re.M)
    if not m:
        return block
    i = m.start()
    depth, j = 0, m.start()
    n = len(block)
    while j < n:
        c = block[j]
        if c in "({":
            depth += 1
        elif c in ")}":
            depth -= 1
        elif c == "\n" and depth <= 0:
            # statement ends at end-of-line when parens balanced and line ends with a comma
            if block[i:j].rstrip().endswith(","):
                j += 1
                break
        j += 1
    return block[:i] + block[j:]


def set_or_insert_field(block, field, value, before=("levelUpLearnset",)):
    """set `.field = value,` replacing an existing one, else insert before the first existing `before` field"""
    line = f"        .{field} = {value},\n"
    if re.search(r"^        \." + field + r"\b", block, re.M):
        block = remove_field(block, field)
    for b in before:
        m = re.search(r"^        \." + b + r"\b", block, re.M)
        if m:
            return block[:m.start()] + line + block[m.start():]
    # fall back: before the closing brace
    k = block.rindex("    },")
    return block[:k] + line + block[k:]


def append_to_text_file(path, marker, text):
    t = path.read_text(encoding="utf-8")
    if marker in t:
        return False
    t = t.rstrip("\n") + "\n\n" + text
    path.write_text(t, encoding="utf-8", newline="\n")
    return True


def form_table_text(name, species, guard=None):
    body = "static const u16 %s[] = {\n" % name + "".join(f"    {s},\n" for s in species) + "    FORM_SPECIES_END,\n};\n"
    return body


def include_in_species_info(rel):
    t = SPECIES_INFO_H.read_text(encoding="utf-8")
    inc = f'    #include "species_info/{rel}"\n'
    if inc in t:
        return
    anchor = "    /* You may add any custom species below this point"
    assert anchor in t
    t = t.replace(anchor, inc + "\n" + anchor, 1)
    SPECIES_INFO_H.write_text(t, encoding="utf-8", newline="\n")


def replace_field(block, field, value):
    """replace a (possibly multi-line) `.field = ...,` in place, or insert before the first learnset field if missing"""
    m = re.search(r"^        \." + field + r"\b[^\n]*\n", block, re.M)
    if not m:
        return set_or_insert_field(block, field, value, before=("formSpeciesIdTable", "formChangeTable", "levelUpLearnset"))
    i = m.start()
    cut = remove_field(block, field)
    # remove_field removed [i, j); recompute j as the length difference
    removed = len(block) - len(cut)
    return block[:i] + f"        .{field} = {value},\n" + block[i + removed:]
