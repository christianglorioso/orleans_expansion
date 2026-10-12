"""Stage 7: keep wild encounters and Orleans trainer parties valid after the dex changes.

* wild_encounters.json: Orleans headers (base_label contains _Orleans) that use a Kantonian base species of an Orleanian
  form (Voltorb, Corphish, ...) switch to the Orleanian species. Text-level edit, so other agents' level changes stay.
* trainer parties (src/data/trainers.party Orleans trainers, tools/mapgen/trainers/*.party): same species switch; moves
  that the new learnsets make illegal are replaced by the closest legal move of the same type.
Writes tools/dex/out/stage7_changes.md. Idempotent.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import partylib
import party_check as pc
import sheet_data as sd
import species_map as sm

ROOT = sm.ROOT
OUT = Path(__file__).resolve().parent / "out"
ENC = ROOT / "src/data/wild_encounters.json"
BASE_TO_ORL = {sm.base_of_orleanian(n): sm.orleanian_const(n) for n in sm.ORLEANIAN}
NAME_TO_ORL = {n: n + "-Orleanian" for n in sm.ORLEANIAN}


def fix_encounters(log):
    t = ENC.read_text(encoding="utf-8")
    spans = [(m.start(), m.group(1)) for m in re.finditer(r'"base_label":\s*"(\w+)"', t)]
    out, last, n = [], 0, 0
    for i, (pos, label) in enumerate(spans):
        end = spans[i + 1][0] if i + 1 < len(spans) else len(t)
        seg = t[pos:end]
        if "_Orleans" in label:
            def rep(m):
                nonlocal n
                sp = m.group(1)
                if sp in BASE_TO_ORL:
                    n += 1
                    return f'"species": "{BASE_TO_ORL[sp]}"'
                return m.group(0)
            seg = re.sub(r'"species":\s*"(SPECIES_\w+)"', rep, seg)
        out.append(t[last:pos])
        out.append(seg)
        last = end
    out.append(t[last:])
    ENC.write_text("".join(out), encoding="utf-8", newline="\n")
    log.append(f"wild_encounters.json: {n} slot species switched to Orleanian forms")


REMOVED_SWAP = {"SPECIES_LOTAD": "SPECIES_POLIWAG", "SPECIES_LOMBRE": "SPECIES_POLIWHIRL", "SPECIES_LUDICOLO": "SPECIES_POLIWRATH",
                "SPECIES_PINCURCHIN": "SPECIES_MAGNEMITE", "SPECIES_CHATOT": "SPECIES_PIKIPEK"}


def swap_removed(log):
    """the removed lines (Lotad line, Pincurchin, Chatot) leave every wild table, including the dormant Hoenn headers"""
    t = ENC.read_text(encoding="utf-8")
    n = 0
    for old, new in REMOVED_SWAP.items():
        c = t.count('"species": "%s"' % old)
        if c:
            t = t.replace('"species": "%s"' % old, '"species": "%s"' % new)
            n += c
    ENC.write_text(t, encoding="utf-8", newline=chr(10))
    log.append(f"wild_encounters.json: {n} dormant Hoenn slots of removed species (Lotad line/Pincurchin/Chatot) swapped")


def move_table():
    h, rows = sd.load_move_index()
    d = {}
    for r in rows:
        if r[0]:
            p = r[3] if isinstance(r[3], (int, float)) else 0
            d[sd.norm(r[0])] = (r[1], r[2], p, r[0])
    return d


def pick_replacement(old, used, legal, mtab, mv_const):
    t, cat, pw, _ = mtab[sd.norm(old)]
    best = None
    for mc in legal:
        if mc in used:
            continue
        name = next((k for k, v in mv_const.items() if v == mc), None)
        if name is None or name not in mtab:
            continue
        t2, cat2, pw2, disp = mtab[name]
        if t2 != t or (cat == "Status") != (cat2 == "Status"):
            continue
        score = abs(pw2 - pw)
        if best is None or score < best[0]:
            best = (score, disp)
    return best[1] if best else None


def process_party(path, only, info, lv, tc, eg, prev, mtab, mv_const, log):
    txt = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    parts = re.split(r"^(=== TRAINER_\w+ ===\n)", txt, flags=re.M)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        hdr, body = parts[i], parts[i + 1]
        const = hdr.strip().strip("=").strip()
        if only is not None and const not in only:
            out += [hdr, body]
            continue
        paras = body.split("\n\n")
        newparas = []
        for pi, para in enumerate(paras):
            lines = para.split("\n")
            first = lines[0] if lines else ""
            is_mon = pi > 0 and first.strip() and not re.match(r"^\w[\w ]*: ", first) and not first.startswith("- ")
            if is_mon:
                # species switch
                for base, new in NAME_TO_ORL.items():
                    m = re.match(r"^(?P<a>(?:.+ \()?)" + re.escape(base) + r"(?P<b>\)?(?: \([MF]\))?(?: @ .+)?)$", first)
                    if m:
                        first2 = m.group("a") + new + m.group("b")
                        log.append(f"{const}: {first} -> {first2}")
                        lines[0] = first2
                        first = first2
                        break
            newparas.append(lines)
        # move legality after species switch
        for lines in newparas:
            first = lines[0] if lines else ""
            if not lines or not any(l.startswith("- ") for l in lines):
                continue
            sp = first
            if " @ " in sp:
                sp = sp.split(" @ ")[0]
            sp = re.sub(r" \([MF]\)$", "", sp)
            n = re.match(r"^(.*) \(([^()]+)\)$", sp)
            if n:
                sp = n.group(2)
            sc = sm.canonical(pc.species_const(sp))
            if sc not in info:
                continue
            lvl = next((int(l.split(":")[1]) for l in lines if l.startswith("Level:")), 1)
            legal = pc.legal_moves(sc, lvl, info, lv, tc, eg, prev)
            used = {mv_const.get(sd.norm(l[2:])) for l in lines if l.startswith("- ")}
            for k, l in enumerate(lines):
                if l.startswith("- "):
                    mc = mv_const.get(sd.norm(l[2:].strip()))
                    if mc and mc not in legal:
                        rep = pick_replacement(l[2:].strip(), used, legal, mtab, mv_const)
                        log.append(f"{const}: {first} Lv{lvl}: {l[2:]} is not legal -> {rep}")
                        if rep:
                            lines[k] = "- " + rep
                            used.add(mv_const.get(sd.norm(rep)))
        out += [hdr, "\n\n".join("\n".join(l) for l in newparas)]
    path.write_text("".join(out), encoding="utf-8", newline="\n")


def main():
    log = []
    fix_encounters(log)
    swap_removed(log)
    info, lv, tc, eg, prev = pc.build_tables()
    mtab = move_table()
    mv = sd.load_move_names()
    master = {t["const"] for t in partylib.parse(OUT / "trainers_master.party")}
    cur = partylib.parse(ROOT / "src/data/trainers.party")
    orl = {t["const"] for t in cur} - master
    process_party(ROOT / "src/data/trainers.party", orl, info, lv, tc, eg, prev, mtab, mv, log)
    for p in sorted((ROOT / "tools/mapgen/trainers").glob("*.party")):
        process_party(p, None, info, lv, tc, eg, prev, mtab, mv, log)
    (OUT / "stage7_changes.md").write_text("\n".join(["# stage 7: encounter/trainer fixes"] + [f"- {l}" for l in log]), encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
