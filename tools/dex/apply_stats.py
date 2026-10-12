"""Stage 1: types, base stats and abilities from orleans_dex.xlsx onto the existing species; adds the 36 custom abilities.

Idempotent. Writes tools/dex/out/stage1_changes.md. Orleanian forms and the 16 custom Megas are created in later stages
(apply_forms.py / apply_megas.py), which reuse the helpers here.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdata
import ppdata
import sheet_data
import species_map as sm
from new_abilities import NEW_ABILITIES

ROOT = cdata.ROOT
OUT = Path(__file__).resolve().parent / "out"

# engine forms that share a sheet row's numbers but have their own block
SIBLINGS = {"SPECIES_MIMIKYU_DISGUISED": ["SPECIES_MIMIKYU_BUSTED"], "SPECIES_ZARUDE": ["SPECIES_ZARUDE_DADA"]}

ABIL_CHAIN = re.compile(
    r"(?:^    #if[^\n]*\n)?^        \.abilities = [^\n]*\n(?:^    #(?:else|elif)[^\n]*\n^        \.abilities = [^\n]*\n)*(?:^    #endif[^\n]*\n)?",
    re.M)
STATS = list(cdata.STAT_FIELDS)


def add_abilities():
    p = ROOT / "include/constants/abilities.h"
    t = p.read_text(encoding="utf-8")
    if "ABILITY_BLUR" in t:
        return 0
    lines = "".join(f"    ABILITY_{c} = {320 + i},\n" for i, (c, *_r) in enumerate(NEW_ABILITIES))
    assert "    ABILITY_AURA_GUARD = 319,\n" in t
    t = t.replace("    ABILITY_AURA_GUARD = 319,\n",
                  "    ABILITY_AURA_GUARD = 319,\n\n    // Orleans custom abilities (see tools/dex/new_abilities.py)\n" + lines)
    p.write_text(t, encoding="utf-8", newline="\n")
    p = ROOT / "src/data/abilities.h"
    t = p.read_text(encoding="utf-8")
    blocks = ""
    for c, name, desc, ai in NEW_ABILITIES:
        blocks += (f'\n    [ABILITY_{c}] =\n    {{\n        .name = _("{name}"),\n'
                   f'        .description = COMPOUND_STRING("{desc}"),\n        .aiRating = {ai},\n    }},\n')
    idx = t.rindex("};")
    t = t[:idx].rstrip("\n") + "\n" + blocks + "\n" + t[idx:]
    p.write_text(t, encoding="utf-8", newline="\n")
    return len(NEW_ABILITIES)


def edit_region(text, d, abil, only):
    """Edit literal fields in `text` (a block or a macro body) for the field keys in `only`. Returns (text, handled)."""
    done = set()
    for k, f in cdata.STAT_FIELDS.items():
        if k not in only:
            continue
        pat = re.compile(r"^(\s*\." + f.strip() + r"\s*=\s*)[^,\n]+(,)", re.M)
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + str(d["stats"][k]) + m.group(2), text, count=1)
            done.add(k)
    if "types" in only:
        ts = ", ".join(cdata.TYPE_NAMES[t] for t in d["types"])
        pat = re.compile(r"^(\s*\.types = )[^\n,]*(?:\([^\n]*\))?[^\n,]*(,)([ \\]*)$", re.M)
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + f"MON_TYPES({ts})" + m.group(2) + m.group(3), text, count=1)
            done.add("types")
    if "abilities" in only:
        a = (abil + ["ABILITY_NONE"] * 3)[:3]
        if "\\\n" in text:
            pat = re.compile(r"^(\s*\.abilities = )[^\n]*?(,)([ \\]*)$", re.M)
            if pat.search(text):
                text = pat.sub(lambda m: m.group(1) + "{ %s, %s, %s }" % tuple(a) + m.group(2) + m.group(3), text, count=1)
                done.add("abilities")
        elif ABIL_CHAIN.search(text):
            text = ABIL_CHAIN.sub("        .abilities = { %s, %s, %s },\n" % tuple(a), text, count=1)
            done.add("abilities")
    return text, done


def macros_in(text):
    return re.findall(r"^\s+([A-Z][A-Z0-9_]+)\(", text, re.M) + re.findall(r"\b([A-Z][A-Z0-9_]+_(?:INFO|INFO_\w+))\(", text)


def apply_to_species(sf, tc, d, abil_consts, diffs, log):
    """Apply sheet row d to species tc; returns list of unresolved field names."""
    p, m = sf.find(tc)
    if not m:
        return list(diffs)
    only = set()
    if "stats" in diffs:
        only |= set(STATS)
    if "types" in diffs:
        only.add("types")
    if "abilities" in diffs:
        only.add("abilities")
    block = m.group(0)
    new, done = edit_region(block, d, abil_consts, only)
    if new != block:
        sf.put(tc, new)
    remaining = only - done
    # macro bodies reached from the block (BFS)
    seen, queue = set(), macros_in(new)
    while remaining and queue:
        mac = queue.pop(0)
        if mac in seen:
            continue
        seen.add(mac)
        ptxt = sf.text[p]
        dm = re.search(r"^#define " + mac + r"\([^\n]*\n(?:[^\n]*\\\n)*[^\n]*\n", ptxt, re.M)
        if not dm:
            continue
        body, got = edit_region(dm.group(0), d, abil_consts, remaining)
        if got:
            sf.text[p] = ptxt[:dm.start()] + body + ptxt[dm.end():]
            log.append(f"{tc}: {sorted(got)} edited in shared macro {mac}")
            remaining -= got
        queue += macros_in(dm.group(0))
    unresolved = []
    if remaining & set(STATS):
        unresolved.append("stats")
    for x in ("types", "abilities"):
        if x in remaining:
            unresolved.append(x)
    return unresolved


def main():
    n_abil = add_abilities()
    sf = cdata.SpeciesFiles()
    t_pp, ents = ppdata.load()
    cons = sm.species_consts()
    log, changed, unresolved = [], [], []
    for r in sheet_data.load_dex():
        if r["name"] in sm.CUSTOM_MEGAS or r["name"] in sm.ORLEANIAN:
            continue
        const = sm.base_const(r["name"], cons)
        wa = [sm.ability_const(a) for a in r["abilities"]]
        wt = [cdata.TYPE_NAMES[x] for x in r["types"]]
        for tc in [const] + SIBLINGS.get(const, []):
            cur = ppdata.fields(ents[tc])
            diffs = []
            if cur["stats"] != r["stats"]:
                diffs.append("stats")
            if cur["types"] != wt:
                diffs.append("types")
            if cur["abilities"] != (wa + ["ABILITY_NONE"] * 3)[:3]:
                diffs.append("abilities")
            if not diffs:
                continue
            un = apply_to_species(sf, tc, r, wa, diffs, log)
            changed.append((r["name"], tc, diffs))
            if un:
                unresolved.append((tc, un))
    sf.save()
    OUT.mkdir(exist_ok=True)
    md = ["# Stage 1 changes (types/stats/abilities)", f"abilities added: {n_abil}", f"species touched: {len(changed)}", ""]
    md += [f"- {n} ({tc}): {', '.join(d)}" for n, tc, d in changed]
    md += ["", "## unresolved (macro-defined; handle by hand)"] + [f"- {u}" for u in unresolved]
    md += ["", "## log"] + [f"- {x}" for x in log]
    (OUT / "stage1_changes.md").write_text("\n".join(md), encoding="utf-8")
    print(f"abilities added {n_abil}; species touched {len(changed)}; unresolved {len(unresolved)}")
    for u in unresolved:
        print("UNRESOLVED", u)


if __name__ == "__main__":
    main()


def realign_macro_fields(text):
    """pad the line-continuation backslash of edited .base*/.types/.abilities macro lines to the column of the others"""
    BS = chr(92)
    lines = text.split("\n")
    cols = [len(l.rstrip()) - 1 for l in lines if l.rstrip().endswith(BS) and not re.search(r"\.(base|types|abilities)", l)]
    if not cols:
        return text
    col = max(set(cols), key=cols.count)
    out = []
    for l in lines:
        if l.rstrip().endswith(BS) and re.search(r"\.(base\w+|types|abilities)\b", l):
            body = l.rstrip()[:-1].rstrip()
            l = body.ljust(col) + BS if len(body) < col else body + " " + BS
        out.append(l)
    return "\n".join(out)
