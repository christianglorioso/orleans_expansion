"""Turn a chapter's TRAINERS table (story_data_chN.TRAINERS / PARTIES) into the trainer party file and the route trainer scripts.

usage (from the decomp root):  python tools/mapgen/gen_route_trainers.py ch5
Writes tools/mapgen/trainers/orleans_<ch>.party (the route trainers + the camp parties) and, per route map, the block between
`@ --- route trainers (gen_route_trainers.py) ---` and `@ --- end route trainers ---` in tools/mapgen/story/<Map>.inc (appended if the
block is missing). The text of each trainer is intro / defeat / after (story_data_chN.T() strings). Then run orleans_trainers.py.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BEGIN = "@ --- route trainers (gen_route_trainers.py) ---"
END = "@ --- end route trainers ---"
IV = 20


def party_block(t, iv=None):
    iv = iv or t.get("iv", IV)
    out = [f"=== {t['const']} ===", f"Name: {t['name']}", f"Class: {t['cls']}", f"Pic: {t['pic']}", f"Gender: {t['sex']}",
           f"Music: {t['music']}", "Double Battle: No", f"AI: {t.get('ai', 'Basic Trainer')}"]
    if t.get("items"):
        out.append("Items: " + t["items"])
    out.append("")
    for mon in t["team"]:
        sp, lv = mon[0], mon[1]
        out.append(sp)
        out.append(f"Level: {lv}")
        out.append("IVs: " + " / ".join(f"{iv} {s}" for s in ("HP", "Atk", "Def", "SpA", "SpD", "Spe")))
        for mv in (mon[2] if len(mon) > 2 else []):
            out.append("- " + mv)
        out.append("")
    out.append("")
    return "\n".join(out)


def script_block(m, items):
    lines = [BEGIN]
    for t in items:
        label = f"{m}_EventScript_Trainer{t['n']}"
        tag = t["const"].split("_ORLEANS_")[-1].replace("_", " ").title().replace(" ", "")
        lines += [f"{label}::",
                  f"\ttrainerbattle_single {t['const']}, {m}_Text_{tag}Intro, {m}_Text_{tag}Defeat",
                  f"\tmsgbox {m}_Text_{tag}After, MSGBOX_AUTOCLOSE",
                  "\tend", ""]
    for t in items:
        tag = t["const"].split("_ORLEANS_")[-1].replace("_", " ").title().replace(" ", "")
        for suffix, key in (("Intro", "intro"), ("Defeat", "defeat"), ("After", "after")):
            lines.append(f"{m}_Text_{tag}{suffix}:")
            lines.append('\t.string "' + t[key].replace(chr(92) + "p", chr(92) + 'p"\n\t.string "') + '$"')
            lines.append("")
    lines.append(END)
    return "\n".join(lines) + "\n"


def main(ch):
    data = importlib.import_module(f"story_data_{ch}")
    trainers = data.TRAINERS
    extra = getattr(data, "CAMP_PARTIES", [])
    # party file
    party = "".join(party_block(t) for t in trainers) + "".join(party_block(t) for t in extra)
    open(os.path.join(HERE, "trainers", f"orleans_{ch}.party"), "w", encoding="utf-8", newline="\n").write(party)
    # scripts
    maps = []
    for t in trainers:
        if t["m"] not in maps:
            maps.append(t["m"])
    for m in maps:
        path = os.path.join(HERE, "story", m + ".inc")
        body = open(path, encoding="utf-8").read() if os.path.exists(path) else f"{m}_MapScripts::\n\t.byte 0\n\n"
        block = script_block(m, [t for t in trainers if t["m"] == m])
        if BEGIN in body:
            a = body.index(BEGIN)
            b = body.index(END) + len(END) + 1
            body = body[:a] + block + body[b:]
        else:
            body = body.rstrip("\n") + "\n\n" + block
        open(path, "w", encoding="utf-8", newline="\n").write(body)
        print("wrote", path)
    print("wrote", os.path.join("trainers", f"orleans_{ch}.party"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ch5")
