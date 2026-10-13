"""Bot run of the Battle Arena against the generated rosters: several rounds, force-win OFF for chosen battles, opponents' teams logged
and screenshotted.  usage (from the decomp root):  python tools/frontier/arena_run.py [--rounds 3] [--real 1,8] [--tag frontier_arena]

Outputs go to tools/playtest/out/<tag>/ (PNGs) and <tag>/teams.json (every opponent party seen: species, item, moves).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/playtest"))
from bot import Bot, ROM, enum_value  # noqa: E402

BADGES = ["FLAG_BADGE0%d_GET" % i for i in range(1, 9)]
_SP, _MV, _IT, _MD = {}, {}, {}, {}


def _enum_names(path, prefix, store):
    if store:
        return store
    t = (ROOT / path).read_text(encoding="utf-8")
    for m in re.finditer(r"^\s*(?:#define\s+)?(" + prefix + r"[A-Z0-9_]+)\s*(?:=|\s)\s*(\d+)", t, re.M):
        store.setdefault(int(m.group(2)), m.group(1))
    return store


def mon_data_idx(name):
    if not _MD:
        t = (ROOT / "include/pokemon.h").read_text(encoding="utf-8")
        i = t.index("MON_DATA_PERSONALITY")
        j = t.index("}", i)
        names = [x.strip().split("=")[0].strip() for x in t[i:j].split(",") if x.strip().startswith("MON_DATA")]
        _MD.update({n: k for k, n in enumerate(names)})
    return _MD[name]


def species_name(n):
    return _enum_names("include/constants/species.h", "SPECIES_", _SP).get(n, "?%d" % n)


def move_name(n):
    return _enum_names("include/constants/moves.h", "MOVE_", _MV).get(n, "?%d" % n)


def item_name(n):
    return _enum_names("include/constants/items.h", "ITEM_", _IT).get(n, "?%d" % n)


def enemy_party(b):
    base = b.r32(b.sym("gEnemyPartyPtr"))
    out = []
    for slot in range(6):
        p = base + slot * 100
        sp = b.call("GetMonData3", p, mon_data_idx("MON_DATA_SPECIES")) & 0xFFFF
        if not sp:
            continue
        mv = [b.call("GetMonData3", p, mon_data_idx("MON_DATA_MOVE1") + k) & 0xFFFF for k in range(4)]
        it = b.call("GetMonData3", p, mon_data_idx("MON_DATA_HELD_ITEM")) & 0xFFFF
        out.append(dict(species=species_name(sp), item=item_name(it), moves=[move_name(m) for m in mv if m]))
    return out


def setup(b, story=45):
    b.new_game()
    b.set_var("VAR_STARTER_MON", 2)
    for f in ("FLAG_SYS_POKEMON_GET", "FLAG_SYS_POKEDEX_GET", "FLAG_ROUTE6_DEBRIS_CLEARED", "FLAG_RECEIVED_HM_SURF", "FLAG_DUST_STORMS_LIFTED", "FLAG_RECEIVED_DIVING_GEAR"):
        b.set_flag(f, True)
    for f in BADGES:
        b.set_flag(f, True)
    for v, val in (("VAR_ROUTE4_ARRIVAL", 1), ("VAR_CAMP_ARRIVAL", 1), ("VAR_HOLLOW_ARRIVAL", 3), ("VAR_REDFIELD_ARRIVAL", 1), ("VAR_LANDS_END_ARRIVAL", 1)):
        b.set_var(v, val)
    b.set_flag("FLAG_STORMS_EDGE_GRID_RESTORED", True)
    b.set_var("VAR_ORLEANS_STORY", story)


def until_menu(b, n=40):
    for _ in range(n):
        if any("ultichoice" in str(x) for x in b.active_tasks()):
            return True
        b.press("A", 4, 26)
        b.frames(10)
    return False


def to_party(b):
    b.warp("BattleFrontier_BattleArenaLobby", 7, 9)
    b.frames(30)
    b.goto(7, 8)
    b.face("U")
    b.press("A", 4, 20)
    until_menu(b)
    b.frames(20)
    b.press("A", 4, 20)          # Level 50
    b.frames(40)
    until_menu(b)
    b.frames(20)
    b.press("A", 4, 20)
    b.frames(40)
    for _ in range(25):
        b.press("A", 4, 26)
        b.frames(10)
        if b.callback2_name() == "CB2_UpdatePartyMenu":
            break
    b.frames(60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--real", default="1", help="battle numbers fought for real (force-win off), comma separated")
    ap.add_argument("--tag", default="frontier_arena")
    ap.add_argument("--rom", default=str(ROM))
    a = ap.parse_args()
    real = {int(x) for x in a.real.split(",") if x}
    b = Bot(run=a.tag, rom=a.rom)
    teams = []
    try:
        setup(b)
        for sp in ("SPECIES_DRAGONITE", "SPECIES_GENGAR", "SPECIES_METAGROSS", "SPECIES_SWAMPERT"):
            b.give_mon(sp, 100)
        battles, inb = 0, False
        for rnd in range(a.rounds):
            to_party(b)
            for k in range(3):
                b.press("DOWN", 6, 10); b.press("A", 4, 20); b.frames(30); b.press("A", 4, 20); b.frames(30)
            b.press("A", 4, 20)
            b.frames(40)
            rb0, lobby_i = battles, 0
            for i in range(1500):
                b.check_alive("arena")
                if b.in_battle():
                    if not inb:
                        inb = True
                        battles += 1
                        b.frames(30)
                        party = enemy_party(b)
                        teams.append(dict(battle=battles, round=rnd + 1, party=party))
                        print("battle", battles, [p["species"][8:] for p in party], flush=True)
                        for q in range(3):
                            b.frames(40)
                            b.shot("b%02d_%d" % (battles, q))
                    b.fight(max_s=90, force_win=(battles not in real))
                    continue
                inb = False
                if b.map_name() == "BattleFrontier_BattleArenaLobby" and battles - rb0 >= 1:
                    lobby_i += 1
                    if lobby_i > 40:
                        break
                b.press("A", 4, 26)
                b.frames(8)
            print("round", rnd + 1, "battles", battles, "where", b.where(), "BP", b.call("GetFrontierBattlePoints") & 0xFFFF, flush=True)
            b.advance_text(30)
            b.frames(30)
    finally:
        out = Path(b.out) / "teams.json"
        out.write_text(json.dumps(teams, indent=1), encoding="utf-8")
        print("teams ->", out)
        b.close()


if __name__ == "__main__":
    main()
