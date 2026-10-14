"""Generate the lair-unlock gates into tools/mapgen/story/<Route>.inc (user spec 2026-10-14, map_pass/lair_unlocks_spec.md).

    python tools/mapgen/lair_gates.py            # rewrite the marked block of every route that holds lair entrances
    python tools/mapgen/lair_gates.py --check    # exit 1 if a file would change

Each route's OnLoad re-evaluates on EVERY map load: a lair entrance opens (its look swapped in and its trigger armed) only when the lair's trophy is complete AND the
post-game has begun (story 45), the rougarou also needs the flood to be down (FLAG_BADGE06_GET). The seal signs (a custom sign on the blocked cell in front of each
entrance) name the requirement while it is shut. Data: story_data_lairs.GATES. Scripts that are not route entrances (the lighthouse stair, the ice plant guard, the
canoe boatman, Moltres' mill door, the three arenas) are hand-written in their own story files and use the same LairGate_EventScript_Check.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import story_data_lairs as D  # noqa: E402

BEGIN = "@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---"
END = "@ --- lair gates end ---"
OLD_STATE = {"rougarou": "RougarouOpen", "ursaluna": "UrsalunaOpen", "celebi": "CelebiOpen", "suicune": "SuicuneOpen", "raikou": "RaikouOpen", "entei": "EnteiOpen"}
EXTRA = {"rougarou": "FLAG_BADGE06_GET"}      # a condition on top of the trophy and the post-game
ORDER = ["rougarou", "ursaluna", "celebi", "suicune", "raikou", "entei", "mesprit", "azelf", "thundurus", "zarude", "ogerpon", "tornadus", "galar_moltres",
         "galar_zapdos", "galar_articuno", "moltres", "landorus"]


def routes():
    out = {}
    for k in ORDER:
        out.setdefault(D.LAIRS[k]["route"], []).append(k)
    return out


def hint_text(label, req):
    BS = chr(92)
    lines = ['\t.string "Sealed until the game is beaten,' + BS + 'n"', '\t.string "and it needs a trophy:' + BS + 'p"']
    parts = req.split("\n")
    for i, p in enumerate(parts):
        end = "$" if i == len(parts) - 1 else BS + "n"
        lines.append('\t.string "%s%s"' % (p, end))
    return "%s:\n%s\n" % (label, "\n".join(lines))


def block(route, keys):
    o = [BEGIN, "", "@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.",
         "%s_OnLoad:" % route]
    for k in keys:
        o += ["\tsetvar VAR_0x8004, %s" % D.GATES[k][0], "\tcall LairGate_EventScript_Check", "\tcall_if_eq VAR_RESULT, TRUE, %s_EventScript_LairOpen%s" % (route, D.CAMEL[k])]
    o += ["\tend", ""]
    for k in keys:
        ach, arm, cell, req = D.GATES[k]
        state = OLD_STATE.get(k) or D.LAIRS[k]["state"]
        o.append("%s_EventScript_LairOpen%s:" % (route, D.CAMEL[k]))
        if k in EXTRA:
            o.append("\tgoto_if_unset %s, %s_EventScript_LairSealDone" % (EXTRA[k], route))
        o += ["\tcall %s_EventScript_State%s" % (route, state), "\tsetflag %s" % arm, "\treturn", ""]
    if any(k in EXTRA for k in keys):
        o += ["%s_EventScript_LairSealDone:" % route, "\treturn", ""]
    for k in keys:
        ach, arm, cell, req = D.GATES[k]
        if k == "moltres":
            continue        # the mill door has its own hand-written sign (Route17_EventScript_MillDoor)
        o += ["%s_EventScript_LairSeal%s::" % (route, D.CAMEL[k]), "\tgoto_if_set %s, %s_EventScript_LairSealEnd" % (arm, route),
              "\tmsgbox %s_Text_LairSeal%s, MSGBOX_SIGN" % (route, D.CAMEL[k]), "\tend", ""]
        o.append(hint_text("%s_Text_LairSeal%s" % (route, D.CAMEL[k]), req))
    o += ["%s_EventScript_LairSealEnd:" % route, "\tend", "", END, ""]
    return "\n".join(o)


def strip_old(text, route):
    """remove the pre-gate OnLoad / LairOpen* definitions (the first run only) and any previous generated block"""
    if BEGIN in text:
        text = text[:text.index(BEGIN)].rstrip("\n") + "\n" + text[text.index(END) + len(END):].lstrip("\n")
    for name in (r"%s_OnLoad" % route, r"%s_EventScript_LairOpen(?:B2)?" % route):
        text = re.sub(r"\n%s:\n(?:\t[^\n]*\n)+" % name, "\n", text)
    return text


def main():
    changed = False
    for route, keys in routes().items():
        path = os.path.join(HERE, "story", route + ".inc")
        old = open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
        new = strip_old(old, route).rstrip("\n") + "\n\n" + block(route, keys)
        if new != old:
            changed = True
            if "--check" not in sys.argv:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)
            print(("would change " if "--check" in sys.argv else "wrote ") + route)
    sys.exit(1 if changed and "--check" in sys.argv else 0)


if __name__ == "__main__":
    main()
