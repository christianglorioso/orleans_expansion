"""Fix B (maps + events): hidden items reachable at the elevation the player has (by Surf too), Heart Scales on the shores, signs readable from the
water, trainers that really spot the player (water and shore sight lines), the Arena lobby's BP clerks, and the Lutin sprite.
(The floodwater gate is t02; the dive and shaft warps themselves are t10.)"""
import json

from bot import ROOT, enum_value
from mapwalk import Grid


def bag(b, item):
    """quantity of an item in the bag (CheckBagHasItem(item, n) is true for n <= quantity)"""
    it = enum_value("items.h", item)
    n = 0
    while n < 999 and b.call("CheckBagHasItem", it, n + 1) & 0xFF:
        n += 1
    return n


def turn(b, d):
    """face direction d without stepping (a short tap only turns the player)"""
    b.press({"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}[d], 2, 14)


def mapj(name):
    return json.load(open(ROOT / "data/maps" / name / "map.json", encoding="utf-8"))


def approach(b, mapname, x, y, water, probe):
    """warp two cells from (x, y) in a straight line (both free, surfable when `water`), then take ONE step toward it: the player ends up on
    the neighbouring cell facing (x, y) without stepping onto it (a tap does not turn without moving here). Returns the facing, or None."""
    b.warp(mapname, *probe)
    g = Grid(b)
    for d, dx, dy in (("D", 0, -1), ("U", 0, 1), ("R", -1, 0), ("L", 1, 0)):
        c1, c2 = (x + dx, y + dy), (x + 2 * dx, y + 2 * dy)
        ok = True
        for c in (c1, c2):
            if c not in g.cells or g.cells[c][1] != 0 or g.surfable(c) != water:
                ok = False
        if ok:
            b.warp(mapname, *c2)
            b.step(d)
            return d
    return None


def press_item(b, mapname, x, y, flag, water, probe):
    facing = approach(b, mapname, x, y, water, probe)
    if facing is None:
        return False, "no straight approach"
    b.press("A", 4, 20)
    b.frames(40)
    b.advance_text(30)
    return b.flag(flag), "%s facing %s at %s" % (mapname, facing, b.where())


def trainer_spots(b, t, label, mapname, spot, lateral):
    """warp beside the sight line (the lateral cell), step into `spot`: the trainer must engage (a TRAINER battle)"""
    b.set_var("VAR_REPEL_STEP_COUNT", 250)
    b.give_item("ITEM_MAX_REPEL", 1)
    b.warp(mapname, *lateral)
    step = "".join(k for k, (dx, dy) in (("U", (0, -1)), ("D", (0, 1)), ("L", (-1, 0)), ("R", (1, 0)))
                   if (lateral[0] + dx, lateral[1] + dy) == spot)
    b.step(step)
    b.frames(120)
    spotted = b.script_status() != 2 or b.in_battle()    # the trainer walks up and the intro text waits for A: the script is running
    t.check("%s spots the player at %s" % (label, spot), spotted, "script=%d battle=%s at %s" % (b.script_status(), b.in_battle(), b.where()))
    if spotted:
        b.advance_text(40)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.set_var("VAR_STARTER_MON", 2)
    b.set_flag("FLAG_RECEIVED_HM_SURF", True)

    # ---- hidden items on water: picked up by Surf (the player's elevation is 1), not only from the shore
    names = ("Route10", "Route11", "Route21", "Route22", "Route25", "Route2", "Route3", "Route5", "Route9", "Route12", "StormsEdge")
    m = {n: mapj(n) for n in names}
    water_items = [("Route10", "ITEM_PEARL"), ("Route11", "ITEM_ETHER"), ("Route21", "ITEM_MAX_REVIVE"), ("Route22", "ITEM_BIG_PEARL")]
    for name, item in water_items:
        ev = next(e for e in m[name]["bg_events"] if e["type"] == "hidden_item" and e["item"] == item)
        t.check("%s hidden %s has the surfer's elevation (1) or the wildcard (0)" % (name, item), ev["elevation"] in (0, 1), ev["elevation"])
        ok, why = press_item(b, name, ev["x"], ev["y"], ev["flag"], True, (ev["x"] + 1, ev["y"]))
        t.check("%s: %s picked up by Surf (flag set)" % (name, item), ok, why)

    # ---- signs read from the water / beside the new entrances
    b.warp("Route25", 18, 8)
    b.step("U")
    b.press("A", 4, 20)
    b.frames(30)
    t.check("Route 25 sign reads from the water", b.script_status() != 2, b.where())
    b.advance_text(30)
    b.warp("Route22", 2, 25)
    b.step("U")
    b.press("A", 4, 20)
    b.frames(30)
    t.check("Route 22 ruin sign reads from the water", b.script_status() != 2, b.where())
    b.shot("route22_sign_from_water")
    b.advance_text(30)
    b.warp("Route24", 38, 9)
    b.step("U")
    b.press("A", 4, 20)
    b.frames(30)
    t.check("Route 24 shaft sign beside the dome door reads", b.script_status() != 2, b.where())
    b.shot("route24_sign")
    b.advance_text(30)

    # ---- Heart Scales on the shores
    scales = []
    for name in ("Route2", "Route3", "Route5", "Route9", "Route12", "StormsEdge"):
        for e in m[name]["bg_events"]:
            if e["type"] == "hidden_item" and e["item"] == "ITEM_HEART_SCALE":
                scales.append((name, e))
    t.check("six hidden Heart Scales (the tutor's price) exist", len(scales) >= 5, len(scales))
    before = bag(b, "ITEM_HEART_SCALE")
    got = 0
    for name, e in scales:
        ok, why = press_item(b, name, e["x"], e["y"], e["flag"], False, (e["x"], e["y"] + 1))
        t.check("%s Heart Scale at (%d,%d) can be picked up" % (name, e["x"], e["y"]), ok, why)
        got += 1 if ok else 0
    t.check("the Heart Scales landed in the bag", bag(b, "ITEM_HEART_SCALE") - before == got, "%d -> %d" % (before, bag(b, "ITEM_HEART_SCALE")))

    # ---- trainers whose sight lines were blind (spot = a cell on the line, lateral = the cell beside it we step in from)
    cases = [
        ("Route6 fisherman (water below the shore)", "Route6", (11, 10), (11, 12), (10, 12)),
        ("Route11 swimmer (turned along the water)", "Route11", (43, 5), (41, 5), (41, 4)),
        ("Route18 swimmer (turned along the water)", "Route18", (17, 20), (20, 20), (20, 21)),
        ("Route19 sailor (shore above the water)", "Route19", (15, 8), (15, 11), (14, 11)),
        ("Route19 boy (shore above the water)", "Route19", (23, 9), (23, 11), (22, 11)),
        ("Route20 Germain (land above the water strip; faces west since fix S, sees the water row 8)", "Route20", (29, 8), (26, 8), (26, 9)),
        ("Route22 Leontine (rock moved aside)", "Route22", (28, 14), (28, 17), (27, 17)),
        ("Route25 Genevieve (rock moved aside)", "Route25", (14, 14), (14, 17), (13, 17)),
    ]
    for label, name, (tx, ty), spot, lat in cases:
        ev = next((o for o in mapj(name)["object_events"] if (o["x"], o["y"]) == (tx, ty)), None)
        t.check("%s stands at (%d,%d)" % (label, tx, ty), ev is not None, name)
        if ev is not None:
            trainer_spots(b, t, label, name, spot, lat)
    b.warp("GrandOak_Gym", 10, 18)
    b.step("R")
    b.frames(120)
    t.check("Grand Oak gym gardener spots the player in the corridor", b.script_status() != 2 or b.in_battle(), b.where())
    b.advance_text(40)

    # ---- the Arena lobby's BP clerks (Exchange Service Corner vitamins / hold items)
    b.warp("BattleFrontier_BattleArenaLobby", 10, 10)
    b.set_var("VAR_0x8004", 20)
    b.call("GiveFrontierBattlePoints")
    bp0 = b.call("GetFrontierBattlePoints") & 0xFFFF
    t.check("20 Battle Points in the purse (test setup)", bp0 >= 20, bp0)
    turn(b, "U")
    b.press("A", 4, 20)
    b.frames(60)
    t.check("the vitamin clerk talks (script running)", b.script_status() != 2, b.where())
    b.shot("bp_clerk")
    prot0 = bag(b, "ITEM_PROTEIN")
    for _ in range(40):              # welcome -> list (first entry: Protein) -> confirm -> bought (the list comes back)
        b.press("A", 4, 30)
        if (b.call("GetFrontierBattlePoints") & 0xFFFF) < bp0:
            break
    b.frames(60)
    for _ in range(30):              # leave the list
        if b.script_status() == 2:
            break
        b.press("B", 4, 30)
    bp1 = b.call("GetFrontierBattlePoints") & 0xFFFF
    t.check("a vitamin was bought for BP (BP down, Protein up)", bp1 < bp0 and bag(b, "ITEM_PROTEIN") > prot0,
            "BP %d -> %d, protein %d -> %d" % (bp0, bp1, prot0, bag(b, "ITEM_PROTEIN")))
    t.check("the player is not left frozen at the clerk", b.script_status() == 2 and b.in_overworld(), b.where())
    b.warp("BattleFrontier_BattleArenaLobby", 12, 10)
    turn(b, "U")
    b.press("A", 4, 20)
    b.frames(60)
    t.check("the hold-item clerk talks (script running)", b.script_status() != 2, b.where())
    for _ in range(30):
        if b.script_status() == 2:
            break
        b.press("B", 4, 30)
    t.check("and releases the player", b.script_status() == 2, b.where())

    # ---- Lutin is a woman: the gym's four Lutins use a woman's sprite
    gm = mapj("LutinsHollow_Gym")
    gfx = [o["graphics_id"] for o in gm["object_events"] if "A_LUTIN" in o["local_id"] or "THE_REAL" in o["local_id"]]
    t.check("the four Lutins are not the male sprite", len(gfx) == 4 and all(g != "OBJ_EVENT_GFX_MAN_5" for g in gfx), gfx)
