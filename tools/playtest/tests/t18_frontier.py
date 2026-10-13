"""The Battle Frontier (Chapter 10): all seven facilities open from the Crescent City plaza at story 45 and every way out comes back to the plaza.

For each of Tower, Dome, Palace, Arena, Factory, Pike and Pyramid:
  * walk into the door on the plaza -> the facility's own lobby; walk out over the mat -> Crescent City, in front of the same door;
  * start a real challenge through the attendant (menus, three-Pokemon selection, the save), then RETIRE (the retire script of that facility) and
    leave: the lobby, then the mat, then the plaza;
  * start another and LOSE (a forced loss in a real battle for Tower / Palace / Arena, whose first battle the bot can reach; the facility's own loss
    script for the others), then leave;
  * start another, save inside (the challenge's own save), reset, CONTINUE and leave;
  * Pike: walk out of the first room into a path room; Pyramid: take the stairs to the next floor (the game's own stairs script).
Every exit asserts the map is CrescentCity or that facility's own maps, never a Hoenn BattleFrontier_Outside*.
"""
import json
from pathlib import Path

from bot import Bot, ROOT, wsl_path

STORY = 45
FAC = {   # name: (lobby map, where to stand to face the attendant, a retire script, a loss script or None for 'a real forced loss')
    "Tower": ("BattleFrontier_BattleTowerLobby", (6, 6), "BattleFrontier_BattleTowerBattleRoom_EventScript_AskRetireChallenge"),
    "Dome": ("BattleFrontier_BattleDomeLobby", (5, 11), "BattleFrontier_BattleDomePreBattleRoom_EventScript_AskRetireChallenge"),
    "Palace": ("BattleFrontier_BattlePalaceLobby", (5, 7), "BattleFrontier_BattlePalaceBattleRoom_EventScript_AskRetireChallenge"),
    "Arena": ("BattleFrontier_BattleArenaLobby", (7, 8), "BattleFrontier_BattleArenaBattleRoom_EventScript_WarpToLobbyLost"),
    "Factory": ("BattleFrontier_BattleFactoryLobby", (4, 8), "BattleFrontier_BattleFactoryBattleRoom_EventScript_WarpToLobbyLost"),
    "Pike": ("BattleFrontier_BattlePikeLobby", (5, 6), "BattleFrontier_BattlePike_EventScript_Retire"),
    "Pyramid": ("BattleFrontier_BattlePyramidLobby", (7, 13), "BattlePyramid_Retire"),
}
ROOM = {"Tower": "BattleFrontier_BattleTowerBattleRoom", "Dome": "BattleFrontier_BattleDomePreBattleRoom", "Palace": "BattleFrontier_BattlePalaceBattleRoom",
        "Arena": "BattleFrontier_BattleArenaBattleRoom", "Factory": "BattleFrontier_BattleFactoryPreBattleRoom",
        "Pike": "BattleFrontier_BattlePikeThreePathRoom", "Pyramid": "BattleFrontier_BattlePyramidFloor"}   # where a challenge first hands over control
REAL_LOSS = ("Tower", "Palace", "Arena")
LOSS_SCRIPT = {"Dome": "BattleFrontier_BattleDomeBattleRoom_EventScript_WarpToLobbyLost", "Factory": "BattleFrontier_BattleFactoryBattleRoom_EventScript_WarpToLobby",
               "Pike": "BattleFrontier_BattlePikeRoomNormal_EventScript_WarpToLobbyLost", "Pyramid": "BattleFrontier_BattlePyramid_EventScript_WarpToLobbyLost"}
PICK = ("SPECIES_PIKACHU", "SPECIES_EEVEE", "SPECIES_SNORLAX", "SPECIES_GYARADOS")


def mapj(name):
    return json.load(open(ROOT / "data" / "maps" / name / "map.json", encoding="utf-8"))


def leave_by_mat(b, lobby):
    """walk to the first warp of the lobby (the mat) and over it"""
    w = mapj(lobby)["warp_events"][0]
    b.goto(w["x"], w["y"])
    for _ in range(3):                   # the mat is a door tile: the warp fires when the player walks down off it
        if b.map_name() != lobby:
            break
        moved = b.step("D")
        b.frames(90)
        b.settle()
        if not moved or b.map_name() == lobby:
            b.step("U")
            b.goto(w["x"], w["y"])
        b.frames(40)
    b.frames(30)
    b.settle()


def mash_until(b, cond, n=120, fight=True):
    for _ in range(n):
        if cond():
            return True
        if b.in_battle() and fight:
            b.fight()
            continue
        b.press("A", 4, 40)
        b.frames(20)
    return cond()


def pick_three(b):
    for _ in range(3):
        b.press("A", 4, 25); b.frames(15)
        b.press("A", 4, 25); b.frames(20)
        b.press("DOWN", 4, 15); b.frames(10)
    b.press("START", 4, 20); b.frames(20)
    b.press("A", 4, 30)


def start_challenge(b, fac, stop_after=None):
    """talk to the attendant and mash through the menus, the party selection and the save until the player has left the lobby; returns the map."""
    lobby, (x, y), _ = FAC[fac]
    if b.map_name() != lobby:
        b.warp(lobby, x, y)
    elif b.pos() != (x, y):
        b.goto(x, y)
    b.face("U")
    b.press("A", 4, 20)
    for _ in range(200):
        if b.map_name() == ROOM[fac] and b.in_overworld() and not b.fading():
            break
        if b.callback2_name() == "CB2_UpdatePartyMenu":
            pick_three(b)
            continue
        b.press("A", 4, 40)
        b.frames(30)
    b.frames(120)
    return b.map_name()


def run_label(b, name):
    if b.script_status() != 2 and ("Palace" in name or "WarpToLobby" in name):   # the Palace room's intro script is still running: end it first
        b.call("ScriptContext_Stop")
        b.frames(10)
    b.call("ScriptContext_SetupScript", b.sym(name))
    b.frames(30)


def retire(b, fac):
    lobby, _, label = FAC[fac]
    run_label(b, label)
    b.frames(90)
    if "AskRetire" in label:
        b.press("UP", 4, 20)      # the YES/NO box defaults to NO
        b.frames(10)
    for _ in range(150):
        if b.map_name() == lobby and b.script_status() != 0 and b.in_overworld() and not b.fading():
            break
        b.press("A", 4, 40)
        b.frames(20)
    b.frames(60)


def lose(b, fac):
    """lose the challenge: a forced defeat in the first battle (Tower, Palace, Arena) or the facility's own loss script"""
    lobby = FAC[fac][0]
    if fac in REAL_LOSS:
        main_func = b.sym("gBattleMainFunc")
        for _ in range(400):
            if b.map_name() == lobby and b.script_status() != 0 and b.in_overworld() and not b.fading():
                break
            if b.in_battle():
                if (b.r32(main_func) & ~1) == b.sym("HandleTurnActionSelectionState"):
                    b.w8(b.sym("gBattleOutcome"), 2)                       # B_OUTCOME_LOST
                    b.w32(main_func, b.syms.call_addr("HandleEndTurn_BattleLost"))
            b.press("A", 4, 26)
            b.frames(8)
    else:
        run_label(b, LOSS_SCRIPT[fac])
        mash_until(b, lambda: b.map_name() == lobby and b.script_status() != 0 and b.in_overworld() and not b.fading(), 80)
    b.frames(60)


def clear_lobby_script(b, lobby):
    """the lobby says its piece after a lost / retired challenge (and saves): mash A until it is over"""
    mash_until(b, lambda: b.map_name() == lobby and b.script_status() == 2 and b.in_overworld() and not b.fading(), 120)


def continue_game(b):
    b.frames(1500)
    for _ in range(4):
        b.press("START", 6, 50)
    b.press("A", 6, 90)
    b.press("A", 6, 90)
    for _ in range(40):
        if b.in_overworld() and b.player_idle():
            break
        b.press("A", 4, 30)
    b.settle()


def run(b, t):
    doors = {}
    cc = mapj("CrescentCity")
    for n, (lobby, _, _) in FAC.items():
        const = {"Tower": "TOWER", "Dome": "DOME", "Palace": "PALACE", "Arena": "ARENA", "Factory": "FACTORY", "Pike": "PIKE", "Pyramid": "PYRAMID"}[n]
        hit = [w for w in cc["warp_events"] if w["dest_map"] == "MAP_BATTLE_FRONTIER_BATTLE_%s_LOBBY" % const]
        t.check("Crescent City has one door warp into the %s lobby" % n, len(hit) == 1, len(hit))
        doors[n] = (hit[0]["x"], hit[0]["y"]) if hit else (0, 0)
    t.check("the seven doors are on seven different cells", len(set(doors.values())) == 7, doors)

    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", STORY)
    for sp in PICK:
        b.give_mon(sp, 50)

    for fac, (lobby, stand, _) in FAC.items():
        dx, dy = doors[fac]

        def at_door(tag):
            t.check("%s %s: back on the plaza in front of its door" % (fac, tag), b.map_name() == "CrescentCity" and b.pos()[0] == dx and b.pos()[1] in (dy, dy + 1),
                    b.where())

        # ---- in through the plaza door, out over the mat
        b.warp("CrescentCity", dx, dy + 1)
        b.step("U")
        b.frames(60)
        b.settle()
        t.check("%s: the plaza door leads into its lobby" % fac, b.map_name() == lobby, b.where())
        b.shot("%s_lobby" % fac)
        clear_lobby_script(b, lobby)      # a challenge left unfinished by the previous facility is wound up by this lobby ("you did not save...")
        leave_by_mat(b, lobby)
        at_door("walk-out")

        # ---- a challenge, retired
        m = start_challenge(b, fac)
        t.check("%s: a challenge starts (the attendant, the selection and the save lead out of the lobby)" % fac, m != lobby and m.startswith("BattleFrontier_Battle" + fac), b.where())
        if fac == "Pike":
            for _ in range(12):
                if b.map_name() != "BattleFrontier_BattlePikeThreePathRoom":
                    break
                b.step("U")
            b.frames(60)
            b.settle()
            t.check("Pike: walking out of the first room enters one of the path rooms", b.map_name().startswith("BattleFrontier_BattlePike") and b.map_name() != "BattleFrontier_BattlePikeThreePathRoom",
                    b.where())
            b.shot("pike_room")
        if fac == "Pyramid":
            before = b.screen_hash()
            run_label(b, "BattlePyramid_WarpToNextFloor")
            b.frames(120)
            b.settle()
            t.check("Pyramid: the stairs lead to the next floor (another floor of the Pyramid)", b.map_name() == "BattleFrontier_BattlePyramidFloor" and b.screen_hash() != before and b.in_overworld(), b.where())
            b.shot("pyramid_floor2")
        retire(b, fac)
        t.check("%s: retiring ends in the lobby" % fac, b.map_name() == lobby, b.where())
        clear_lobby_script(b, lobby)
        leave_by_mat(b, lobby)
        at_door("retire")

        # ---- a challenge, lost
        b.warp(lobby, *stand)
        m = start_challenge(b, fac)
        t.check("%s: a second challenge starts" % fac, m != lobby, b.where())
        lose(b, fac)
        t.check("%s: losing ends in the lobby, never a Hoenn map" % fac, b.map_name() == lobby, b.where())
        clear_lobby_script(b, lobby)
        leave_by_mat(b, lobby)
        at_door("loss")

        # ---- save inside, reset, continue
        b.warp(lobby, *stand)
        m = start_challenge(b, fac)
        t.check("%s: a third challenge starts and has saved" % fac, m != lobby, b.where())
        path = b.out / ("frontier_%s.sav" % fac)
        b.h.cmd("dumpsave " + wsl_path(path))
        again = Bot(rom=b.rom, out_dir=b.out / ("cont_" + fac), save=path)
        try:
            continue_game(again)
            again.shot("%s_continued" % fac)
            t.check("%s: Continue lands in one of its own maps" % fac, again.map_name().startswith("BattleFrontier_Battle" + fac), again.where())
            clear_lobby_script(again, lobby) if again.map_name() == lobby else None
            if again.map_name() != lobby:
                run_label(again, "BattlePyramid_Retire" if fac == "Pyramid" else "BattleFrontier_BattlePike_EventScript_Retire" if fac == "Pike" else LOSS_SCRIPT.get(fac, FAC[fac][2]))
                mash_until(again, lambda: again.map_name() == lobby and again.script_status() == 2, 80)
            leave_by_mat(again, lobby)
            t.check("%s: after Continue the mat leads to the plaza in front of its door" % fac, again.map_name() == "CrescentCity" and again.pos()[0] == dx and again.pos()[1] in (dy, dy + 1), again.where())
        finally:
            again.close()

    # ---- a whiteout in a Frontier map lands at the last heal location (an Orleans map), never in a Hoenn one
    b.warp("BattleFrontier_BattleArenaLobby", 7, 8)
    b.call("SetWarpDestinationToLastHealLocation")
    b.call("DoWarp")
    b.frames(240)
    b.settle()
    t.check("the last heal location is in Orleans, not BattleFrontier_Outside*", not b.map_name().startswith("BattleFrontier_Outside"), b.where())
    t.check("no facility map has a warp left for a Hoenn Frontier map",
            all(w["dest_map"] not in ("MAP_BATTLE_FRONTIER_OUTSIDE_EAST", "MAP_BATTLE_FRONTIER_OUTSIDE_WEST")
                for n in FAC for p in (ROOT / "data" / "maps").glob("BattleFrontier_Battle%s*" % n) for w in mapj(p.name).get("warp_events", [])))
