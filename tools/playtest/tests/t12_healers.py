"""Every healer in Orleans: talking to the nurse restores the party and the script ends (the nurse bow movement exists only on
OBJ_EVENT_GFX_NURSE, so a healer with another sprite freezes on "We hope you excel!"), plus a whiteout that respawns at a healer."""
import glob
import json
import re
from pathlib import Path

from bot import ROOT, map_data

PARTY_HP = 0x56
PARTY_MAXHP = 0x58


def healers():
    """[(map, local_id, x, y)] for every Orleans map that calls Common_EventScript_PkmnCenterNurse"""
    out = []
    for p in sorted(glob.glob(str(ROOT / "data/maps/*/scripts.inc"))):
        d = Path(p).parent
        if d.name.startswith(("BattleFrontier", "TrainerHill")):
            continue
        sc = Path(p).read_text(encoding="utf-8", errors="ignore")
        if "Common_EventScript_PkmnCenterNurse" not in sc:
            continue
        m = json.loads((d / "map.json").read_text(encoding="utf-8"))
        for o in m["object_events"]:
            i = sc.find(o["script"] + "::")
            if i >= 0 and "Common_EventScript_PkmnCenterNurse" in sc[i:].split("\n\n")[0]:
                out.append((d.name, o["local_id"], o["x"], o["y"], o["graphics_id"]))
    return out


def spots(name, nx, ny):
    """(x, y, facing) cells from which the nurse can be talked to: next to her, or across one counter tile"""
    d = map_data(name)
    res = []
    for dx, dy, face in ((0, 1, "U"), (0, -1, "D"), (-1, 0, "R"), (1, 0, "L")):
        for dist in (1, 2):
            x, y = nx + dx * dist, ny + dy * dist
            if not (0 <= x < d["width"] and 0 <= y < d["height"]):
                break
            if d["coll"][y][x] == 0 and (dist == 1 or d["coll"][ny + dy][nx + dx] != 0):
                res.append((x, y, face))
                break
    return res


def party_base(b):
    return b.r32(b.sym("gPlayerPartyPtr"))


def hurt(b, hp):
    b.w16(party_base(b) + PARTY_HP, hp)


def hp(b):
    base = party_base(b)
    return b.r16(base + PARTY_HP), b.r16(base + PARTY_MAXHP)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_TOTODILE", 50)
    hs = healers()
    t.check("found the healers (10 Centers, Camp cabin, Old Water healer and rest house)", len(hs) >= 12, [h[0] for h in hs])
    for name, lid, nx, ny, gfx in hs:
        t.check(f"{name}: healer sprite is the nurse", gfx == "OBJ_EVENT_GFX_NURSE", gfx)
        healed = False
        for x, y, face in spots(name, nx, ny):
            b.warp(name, x, y)
            hurt(b, 1)
            done = b.interact(face)
            cur, mx = hp(b)
            if cur == mx and mx > 1:
                healed = True
                t.check(f"{name}: heal script finishes (no freeze)", done, b.callback2_name())
                b.walk("D" if face == "U" else "U")
                t.check(f"{name}: player can move afterwards", b.script_status() == 2 and b.in_overworld(), b.where())
                break
        t.check(f"{name}: party restored", healed, hp(b))
        b.shot("heal_" + name)

    # --- whiteout at the Old Water healer (the one that used a different sprite) and at a normal Center
    ids = [i["id"] for i in json.loads((ROOT / "src/data/heal_locations.json").read_text())["heal_locations"]]
    for locname, nurse_map in (("HEAL_LOCATION_REDFIELD", "Redfield_Pokecenter"), ("HEAL_LOCATION_OLD_WATER", "OldWater_Healer")):
        b.warp("OldWater", 10, 10)
        b.call("SetLastHealLocationWarp", ids.index(locname) + 1)
        hurt(b, 0)
        b.call("SetCB2WhiteOut")
        done = b.advance_text(60)
        t.check(f"whiteout ends in {nurse_map}", b.map_name() == nurse_map, b.where())
        t.check(f"whiteout at {nurse_map}: script finishes (no freeze)", done, b.callback2_name())
        cur, mx = hp(b)
        t.check(f"whiteout at {nurse_map}: party healed", cur == mx and mx > 0, (cur, mx))
        b.shot("whiteout_" + nurse_map)
        b.settle()
        # the respawn cell can sit right in front of the nurse (Old Water): the bot's A presses may start a second talk; cancel it
        for _ in range(30):
            b.frames(20)
            if b.script_status() == 2:
                break
            b.press("B", 4, 22)
        before = b.pos()
        t.note(("before steps: script", b.script_status(), "locked", b.player_locked(), "tasks", b.active_tasks()))
        moved = b.step("D") or b.step("L") or b.step("R") or b.step("U")
        b.shot("moved_" + nurse_map)
        t.note(("frames-after", b.callback2_name(), b.active_tasks(), b.where()))
        t.check(f"whiteout at {nurse_map}: player can move afterwards", moved and b.in_overworld(),
                (b.where(), before, "script", b.script_status(), "locked", b.player_locked()))
