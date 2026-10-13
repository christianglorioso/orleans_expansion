"""The post-game: everything hidden until the game is cleared (story 45), then balls and legends appear; the Fais Do-Do Ribbon (badge 6), the Floette
(Eternal Flower) seed, Rayquaza's return, an arena legend only if Jayden took it, the night-only Ursaluna; the Battle Frontier gate and Tower."""
import re
from pathlib import Path

from bot import map_data, ROOT

DAY = 1760000000
NIGHT = DAY + 14 * 3600


def has_item(b, name):
    from bot import enum_value
    return bool(b.call("CheckBagHasItem", enum_value("items.h", name), 1) & 0xFF)


def set_time(b, secs):
    b.h.cmd("rtc %d" % secs)
    b.frames(30)


def settle(b, n=40):
    b.frames(n)
    b.advance_text(60)


def other_map(b):
    b.advance_text(30)
    b.frames(30)
    b.warp("LandsEnd_Pokecenter", 7, 5)
    b.frames(30)
    b.advance_text(30)


def run(b, t):
    b.new_game()
    b.give_mon("SPECIES_MEWTWO", 100)
    b.give_mon("SPECIES_MEW", 100)
    b.set_var("VAR_STARTER_MON", 2)
    set_time(b, DAY)

    # ---------------------------------------------------------------- the audit: every dex-required item has a source
    import subprocess
    r = subprocess.run(["python", "tools/dex/obtain_audit.py"], cwd=str(ROOT), capture_output=True, text=True)
    t.check("obtain_audit: no dex-required item is missing a source", r.returncode == 0 and "missing: none" in r.stdout, r.stdout[-200:])

    # ---------------------------------------------------------------- the Fais Do-Do Ribbon (the accordion player, badge 6)
    b.set_flag("FLAG_BADGE06_GET", False)
    b.set_flag("FLAG_RECEIVED_FAIS_DO_DO", False)
    acc = [o for o in map_data("IsleMarais_Shelter")["objects"] if o["script"].endswith("Accordion6")][0]
    b.warp("IsleMarais_Shelter", acc["x"], acc["y"] + 1)
    b.interact("U", 120)
    t.check("without the sixth badge the accordion player only plays", not b.flag("FLAG_RECEIVED_FAIS_DO_DO"))
    b.set_flag("FLAG_BADGE06_GET", True)
    other_map(b)
    b.warp("IsleMarais_Shelter", acc["x"], acc["y"] + 1)
    b.interact("U", 120)
    t.check("with the sixth badge: the Fais Do-Do Ribbon", b.flag("FLAG_RECEIVED_FAIS_DO_DO") and has_item(b, "ITEM_FAIS_DO_DO_RIBBON"))

    # ---------------------------------------------------------------- below story 45 the post-game objects are hidden on load
    b.set_var("VAR_ORLEANS_STORY", 44)
    for f in ("FLAG_PG_CHANDELURITE", "FLAG_PG_SCOVILLAINITE", "FLAG_PG_HEARTHFLAME_MASK"):
        b.set_flag(f, False)
    other_map(b)
    b.warp("Redfield", 20, 18)
    b.frames(30)
    t.check("at story 44 Redfield's post-game balls are hidden on load", b.flag("FLAG_PG_CHANDELURITE") and b.flag("FLAG_PG_SCOVILLAINITE") and b.flag("FLAG_PG_HEARTHFLAME_MASK"))

    # ---------------------------------------------------------------- the game is cleared: the flags are cleared by the epilogue (simulated), the balls can be taken
    b.set_var("VAR_ORLEANS_STORY", 45)
    for f in ("FLAG_PG_CHANDELURITE", "FLAG_PG_SCOVILLAINITE", "FLAG_PG_HEARTHFLAME_MASK"):
        b.set_flag(f, False)
    b.set_var("VAR_REDFIELD_ARRIVAL", 1)
    other_map(b)
    b.warp("Redfield", 20, 18)
    b.frames(30)
    t.check("at story 45 the balls stay (the load does not hide them)", not b.flag("FLAG_PG_CHANDELURITE") and not b.flag("FLAG_PG_SCOVILLAINITE"))
    ball = [o for o in map_data("Redfield")["objects"] if o.get("flag") == "FLAG_PG_CHANDELURITE"][0]
    b.warp("Redfield", ball["x"], ball["y"] + 1)
    b.interact("U", 120)
    t.check("the Chandelurite is picked up (item in the bag, ball hidden for good)", has_item(b, "ITEM_CHANDELURITE") and b.flag("FLAG_PG_CHANDELURITE"))

    # ---------------------------------------------------------------- a static legend: Raikou on Route 2
    b.set_flag("FLAG_PG_RAIKOU", False)
    other_map(b)
    b.warp("Route2", 25, 16)
    b.frames(30)
    rk = [o for o in map_data("Route2")["objects"] if o.get("flag") == "FLAG_PG_RAIKOU"][0]
    b.warp("Route2", rk["x"], rk["y"] + 1)
    b.face("U")
    b.press("A", 4, 20)
    for _ in range(300):
        if b.in_battle():
            b.fight()
        elif b.flag("FLAG_PG_RAIKOU"):
            break
        else:
            b.press("A", 4, 26)
    b.frames(30)
    b.advance_text(60)
    t.check("Raikou: the battle ends in a win/catch and the object is hidden for good", b.flag("FLAG_PG_RAIKOU"))

    # ---------------------------------------------------------------- night-only Ursaluna Bloodmoon (Route 23)
    b.set_flag("FLAG_PG_URSALUNA_BM", True)
    b.set_flag("FLAG_PG_URSALUNA_DONE", False)
    set_time(b, DAY)
    other_map(b)
    b.warp("Route23", 24, 20)
    b.frames(30)
    t.check("by day Ursaluna is hidden", b.flag("FLAG_PG_URSALUNA_BM"))
    set_time(b, NIGHT)
    other_map(b)
    b.warp("Route23", 24, 20)
    b.frames(30)
    t.check("at night (story 45) Ursaluna appears", not b.flag("FLAG_PG_URSALUNA_BM"))
    set_time(b, DAY)

    # ---------------------------------------------------------------- the arena legend only if Jayden took it
    b.set_var("VAR_ORLEANS_LEGENDARY_PICK", 1)           # the player has Kyogre: Jayden has Groudon -> Groudon's arena
    b.set_flag("FLAG_PG_GROUDON_RE", False)
    b.set_flag("FLAG_PG_KYOGRE_RE", False)
    other_map(b)
    b.warp("LandsEnd_SaltCathedral", 10, 12)
    b.frames(30)
    other_map(b)
    b.warp("LandsEnd_DrownedTemple", 8, 12)
    b.frames(30)
    t.check("with Kyogre the player's, Groudon waits in its cathedral and Kyogre's hall is empty", not b.flag("FLAG_PG_GROUDON_RE") and b.flag("FLAG_PG_KYOGRE_RE"))

    # ---------------------------------------------------------------- Rayquaza returns to the stone
    b.set_flag("FLAG_PG_RAYQUAZA", False)
    other_map(b)
    b.warp("OldestShrine", 18, 12)
    b.frames(30)
    t.check("at story 45 Rayquaza's post-game object is shown", not b.flag("FLAG_PG_RAYQUAZA"))

    # ---------------------------------------------------------------- the herbalist's apprentice: the Floette (Eternal Flower) seed
    b.set_flag("FLAG_RECEIVED_FLOETTE_EF", False)
    b.set_flag("FLAG_RECEIVED_FLOETTITE", False)
    ap = [o for o in map_data("LutinsHollow_Herbalist")["objects"] if o["script"].endswith("Apprentice1")][0]
    other_map(b)
    b.warp("LutinsHollow_Herbalist", ap["x"], ap["y"] + 1)
    b.interact("U", 120)
    t.check("the apprentice gives the Floette (Eternal Flower) and the Floettite", b.flag("FLAG_RECEIVED_FLOETTE_EF") and b.flag("FLAG_RECEIVED_FLOETTITE") and has_item(b, "ITEM_FLOETTITE"))

    # ---------------------------------------------------------------- shop stock and trades (static: the built scripts)
    d2 = (Path(ROOT) / "data/maps/CrescentCity_Dept2f/scripts.inc").read_text()
    t.check("the department store sells the Metal Alloy (badge 6) and the four stones (story 45)",
            "ITEM_METAL_ALLOY" in d2 and all(x in d2.split("Pokemart_Clerk03:")[1] for x in ("ITEM_SUN_STONE", "ITEM_ICE_STONE", "ITEM_DUSK_STONE", "ITEM_SHINY_STONE")))
    tr = (Path(ROOT) / "data/maps/CrescentCity_Trades/scripts.inc").read_text()
    t.check("the trade house offers the three Alolan trades", all(x in tr for x in ("INGAME_TRADE_ALOLAN_RAICHU", "INGAME_TRADE_ALOLAN_VULPIX", "INGAME_TRADE_ALOLAN_SANDSHREW")))

    # ---------------------------------------------------------------- the epilogue's unhide script clears every post-game flag and the Frontier guard's
    sh = (Path(ROOT) / "data/maps/OldestShrine/scripts.inc").read_text()
    un = sh.split("PostGame_EventScript_Unhide:")[1].split("return")[0]
    flags = [o["flag"] for m in ("Redfield", "Route2", "OldestShrine", "Route13") for o in map_data(m)["objects"] if str(o.get("flag", "")).startswith("FLAG_PG_")]
    t.check("PostGame_EventScript_Unhide clears the Redfield, Route 2, Oldest Shrine and Route 13 post-game flags and the guard's",
            all("clearflag " + f in un for f in flags) and "setflag FLAG_UNUSED_0x2D9" in un and "call PostGame_EventScript_Unhide" in sh, str(len(flags)))

    # ---------------------------------------------------------------- the Battle Frontier: the Arena door leads to the vanilla lobby, its exit mat comes back
    b.set_var("VAR_ORLEANS_STORY", 45)
    other_map(b)
    b.warp("CrescentCity", 25, 50)
    b.face("U")
    b.press("A", 4, 20)
    for _ in range(60):
        if b.map_name() == "BattleFrontier_BattleArenaLobby":
            break
        b.press("A", 4, 30)
    b.frames(40)
    t.check("the Battle Arena's door leads to the Arena lobby", b.map_name() == "BattleFrontier_BattleArenaLobby", b.where())
    b.advance_text(30)
    b.press("DOWN", 8, 8)
    b.press("DOWN", 8, 8)
    b.frames(160)
    t.check("the lobby's exit mat returns to the Frontier plaza in Crescent City", b.map_name() == "CrescentCity" and b.pos() == (25, 50), b.where())
