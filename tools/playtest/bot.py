"""Playtest bot for the Orleans ROM: drives tools/playtest/harness (headless libmgba in WSL) from Windows.

    from bot import Bot
    b = Bot("my_run")             # boots the current pokemon_orleans.gba, screenshots go to out/my_run/
    b.press("A"); b.walk("RRDD"); b.warp("CrescentCity", 40, 60); b.shot("here")
    b.var("VAR_ORLEANS_STORY"); b.set_var("VAR_ORLEANS_STORY", 11); b.flag("FLAG_BADGE06_GET")

The in-game clock is the fake RTC saved in the ROM: b.set_clock(hour, minute), b.clock(), b.time_of_day() (see "the in-game clock" below).
Symbols come from the build's link map (plus readelf for the thumb bit), constants from include/constants/*.h.
Direct memory writes are used for test setup only; flags/vars are set through the game's own FlagSet/VarSet
(the harness can call ROM functions), so the SaveBlock layout never has to be hard-coded.
"""
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PLAYTEST = Path(__file__).resolve().parent
OUT = PLAYTEST / "out"
ROM = ROOT / "pokemon_orleans.gba"
WSL_DISTRO = "Ubuntu"
WSL_HOME_ROM_DIR = "orleans_expansion"          # the build mirror (tools/wsl_build.sh)
HARNESS_CMD = "~/.cache/orleans_playtest/harness"
GBA_FRAME_RATE = 60

DIRS = {"U": "UP", "D": "DOWN", "L": "LEFT", "R": "RIGHT"}


def wsl_path(p):
    p = Path(p).resolve()
    drive = p.drive[0].lower()
    return "/mnt/%s/%s" % (drive, p.as_posix().split(":", 1)[1].lstrip("/"))


def wsl(cmd, **kw):
    return subprocess.run(["wsl.exe", "-d", WSL_DISTRO, "--", "bash", "-c", cmd],
                          capture_output=True, text=True, **kw)


def rom_sha1(path=ROM):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- symbols
class Symbols:
    """name -> address. Primary source: readelf -sW of the mirror's pokemon_orleans.elf (has the thumb bit for
    functions), cross-checked against pokemon_orleans.map. Falls back to the map file alone (all functions then
    assumed thumb). Cached per ROM hash."""

    def __init__(self, sha):
        cache = OUT / ("symbols_%s.json" % sha[:12])
        if cache.exists():
            d = json.loads(cache.read_text())
            self.addr, self.thumb = d["addr"], set(d["thumb"])
            return
        self.addr, self.thumb = {}, set()
        self._from_map()
        self._from_elf()
        OUT.mkdir(exist_ok=True)
        cache.write_text(json.dumps({"addr": self.addr, "thumb": sorted(self.thumb)}))

    def _from_map(self):
        r = wsl("cat ~/%s/pokemon_orleans.map 2>/dev/null || cat ~/%s/pokeemerald.map" % (WSL_HOME_ROM_DIR, WSL_HOME_ROM_DIR))
        for line in r.stdout.splitlines():
            m = re.match(r"^\s+0x([0-9a-f]{8})\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", line)
            if m and m.group(2) not in self.addr:
                self.addr[m.group(2)] = int(m.group(1), 16)

    def _from_elf(self):
        r = wsl("readelf -sW ~/%s/pokemon_orleans.elf 2>/dev/null || readelf -sW ~/%s/pokeemerald.elf" % (WSL_HOME_ROM_DIR, WSL_HOME_ROM_DIR))   # no shell variables: they do not survive wsl.exe here
        for line in r.stdout.splitlines():
            p = line.split()
            if len(p) >= 8 and p[3] in ("FUNC", "OBJECT", "NOTYPE") and re.fullmatch(r"[0-9a-f]+", p[1]):
                val = int(p[1], 16)
                name = p[7]
                if p[3] == "FUNC":
                    if val & 1:
                        self.thumb.add(name)
                    val &= ~1
                self.addr.setdefault(name, val)
                if name in self.addr and p[3] == "FUNC":
                    self.addr[name] = val

    def __getitem__(self, name):
        if name not in self.addr:
            raise KeyError("symbol not found: " + name)
        return self.addr[name]

    def call_addr(self, name):
        a = self[name]
        return a | 1 if (name in self.thumb or not self.thumb) else a


# --------------------------------------------------------------------------- constants
class Consts:
    """#define table for vars.h / flags.h, produced by the real preprocessor (arm-none-eabi-gcc -E -dM in WSL) so
    conditionals and nested macros (TRAINER_FLAGS_END, SYSTEM_FLAGS + n ...) come out right. Cached on the headers' hash."""

    def __init__(self):
        self.defs = {}
        inc = ROOT / "include"
        key = hashlib.sha1(b"".join((inc / "constants" / f).read_bytes() for f in
                                    ("vars.h", "flags.h", "opponents.h", "trainers.h"))).hexdigest()[:12]
        cache = OUT / ("consts_%s.json" % key)
        if cache.exists():
            self.defs = json.loads(cache.read_text())
        else:
            src = "\n".join(['#include "global.h"', '#include "constants/vars.h"', '#include "constants/flags.h"', ''])
            r = subprocess.run(["wsl.exe", "-d", WSL_DISTRO, "--", "bash", "-c",
                                "cd %s && arm-none-eabi-gcc -E -dM -I include -x c -" % wsl_path(ROOT)],
                               input=src, capture_output=True, text=True)
            for m in re.finditer(r"^#define\s+((?:VAR|FLAG|SYSTEM|TRAINER|MAX|NUM|TEMP|VARS|FLAGS|SPECIAL|OBJ_EVENT|DAILY|MAP)\w*)\s+(.+)$", r.stdout, re.M):
                if "(" not in m.group(1):
                    self.defs[m.group(1)] = m.group(2).strip()
            if not self.defs:
                raise RuntimeError("could not preprocess constants: " + r.stderr[:300])
            OUT.mkdir(exist_ok=True)
            cache.write_text(json.dumps(self.defs))
        self.cache = {}

    def get(self, name):
        if isinstance(name, int):
            return name
        if name in self.cache:
            return self.cache[name]
        expr = self.defs[name]
        val = self._ev(expr, 0)
        self.cache[name] = val
        return val

    def _ev(self, expr, depth):
        if depth > 20:
            raise ValueError(expr)
        expr = re.sub(r"(?<!\w)[A-Za-z_]\w*", lambda m: str(self._ident(m.group(0), depth)), expr)
        return int(eval(expr, {"__builtins__": {}}, {}))

    def _ident(self, ident, depth):
        if ident in self.cache:
            return self.cache[ident]
        if ident not in self.defs:
            raise KeyError("unknown constant " + ident)
        v = self._ev(self.defs[ident], depth + 1)
        self.cache[ident] = v
        return v


class Maps:
    """(group, num) <-> name, from data/maps/map_groups.json (group = index in group_order, num = index in group)."""

    def __init__(self):
        g = json.loads((ROOT / "data/maps/map_groups.json").read_text())
        self.by_id, self.by_name = {}, {}
        for gi, gname in enumerate(g["group_order"]):
            for ni, mname in enumerate(g[gname]):
                self.by_id[(gi, ni)] = mname
                self.by_name[mname] = (gi, ni)

    def name(self, group, num):
        return self.by_id.get((group, num), "?%d/%d" % (group, num))

    def lookup(self, name):
        """accepts 'CrescentCity', 'MAP_CRESCENT_CITY' (via map.json ids) or (group, num)"""
        if isinstance(name, tuple):
            return name
        if name in self.by_name:
            return self.by_name[name]
        for mname, gn in self.by_name.items():
            mj = ROOT / "data/maps" / mname / "map.json"
            if mj.exists() and json.loads(mj.read_text()).get("id") == name:
                return gn
        raise KeyError("map not found: %s" % name)


# --------------------------------------------------------------------------- harness process
class Harness:
    def __init__(self, rom, rtc=None, log=None, save=None):
        cmd = "%s %s" % (HARNESS_CMD, wsl_path(rom))
        self.log = open(log, "w") if log else subprocess.DEVNULL
        if rtc or save:
            cmd += " %d" % (rtc or 1760000000)
        if save:
            cmd += " " + wsl_path(save)
        self.p = subprocess.Popen(["wsl.exe", "-d", WSL_DISTRO, "--", "bash", "-c", cmd],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log,
                                  text=True, bufsize=1)
        ready = self.p.stdout.readline().strip()
        if not ready.startswith("OK ready"):
            raise RuntimeError("harness did not start: %r (build it with tools/playtest/build_harness.sh in WSL)" % ready)

    def cmd(self, line):
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()
        r = self.p.stdout.readline().strip()
        if not r:
            raise RuntimeError("harness died on: " + line)
        if r.startswith("ERR"):
            raise RuntimeError("harness: %s (%s)" % (r, line))
        return r[3:].strip()

    def close(self):
        try:
            self.cmd("quit")
        except Exception:
            pass
        try:
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


class GameCrash(Exception):
    """the game fell back to its boot code (soft reset / wild jump) while the bot was driving it"""


# --------------------------------------------------------------------------- the bot
class Bot:
    def __init__(self, run="adhoc", rom=ROM, rtc=1760000000, out_dir=None, save=None):
        self.rom = Path(rom)
        self.sha = rom_sha1(self.rom)
        self.out = Path(out_dir) if out_dir else OUT / run
        self.out.mkdir(parents=True, exist_ok=True)
        OUT.mkdir(exist_ok=True)
        self.syms = Symbols(self.sha)
        self.consts = Consts()
        self.maps = Maps()
        self.h = Harness(self.rom, rtc, log=self.out / "harness.log", save=save)   # save: a .sav (flash image) from another run/build
        # ROM functions are called from a clean point in the main loop (see harness.c callFn)
        self.h.cmd("safepoint %d" % self.syms["PlayTimeCounter_Update"])
        self.force_win = True    # battle autopilot shortcut (see Bot.fight); set False to really play the fights
        self.shots = []          # (label, path)
        self.log = []

    def close(self):
        self.h.close()

    # ---- raw
    def frames(self, n):
        self.h.cmd("frames %d" % n)

    def seconds(self, s):
        self.frames(int(s * GBA_FRAME_RATE))

    def press(self, keys, hold=6, release=6):
        self.h.cmd("press %s %d %d" % (keys, hold, release))

    def hold(self, keys):
        self.h.cmd("hold " + keys)

    def release(self):
        self.h.cmd("release")

    def r8(self, a): return int(self.h.cmd("read8 %d" % a))
    def r16(self, a): return int(self.h.cmd("read16 %d" % a))
    def r32(self, a): return int(self.h.cmd("read32 %d" % a))
    def w8(self, a, v): self.h.cmd("write8 %d %d" % (a, v))
    def w16(self, a, v): self.h.cmd("write16 %d %d" % (a, v))
    def w32(self, a, v): self.h.cmd("write32 %d %d" % (a, v))

    def rs16(self, a):
        v = self.r16(a)
        return v - 0x10000 if v & 0x8000 else v

    def sym(self, name):
        return self.syms[name]

    def call(self, name, *args):
        return int(self.h.cmd("call %d %s" % (self.syms.call_addr(name), " ".join(str(a & 0xFFFFFFFF) for a in args))))

    def frame_counter(self):
        return self.r32(self.sym("gMain") + 0x20)

    def screen_hash(self):
        return self.h.cmd("hash")

    def nonblack(self):
        return int(self.h.cmd("nonblack"))

    def shot(self, label):
        """screenshot -> out/<run>/NN_label.png (240x160, scaled 2x for readability)"""
        name = "%02d_%s" % (len(self.shots), re.sub(r"[^A-Za-z0-9_.-]", "_", label))
        ppm = self.out / (name + ".ppm")
        self.h.cmd("shot " + wsl_path(ppm))
        png = self.out / (name + ".png")
        Image.open(ppm).resize((480, 320), Image.NEAREST).save(png)
        ppm.unlink()
        self.shots.append((label, png))
        return png

    def savestate(self, path):
        self.h.cmd("savestate " + wsl_path(path))

    def loadstate(self, path):
        self.h.cmd("loadstate " + wsl_path(path))

    # ---- game state
    def callback2(self):
        return self.r32(self.sym("gMain") + 4)

    def crashed(self):
        """the game fell back to the boot/title code (a soft reset or a crash): callback2 is a boot-time screen"""
        cb = self.callback2() & ~1
        boot = {self.syms.addr.get(n) for n in ("CB2_InitCopyrightScreenAfterBootup", "CB2_ExpansionIntro",
                                                "MainCB2_Intro", "CB2_InitTitleScreen", "MainCB2")}
        return cb == 0 or cb in boot

    def check_alive(self, what=""):
        if self.crashed():
            try:
                self.shot("CRASH")
            except Exception:
                pass
            raise GameCrash("game reset to the boot screen %s (map before: %s)" % (what, getattr(self, "last_where", "?")))

    def in_overworld(self):
        return self.callback2() & ~1 == self.sym("CB2_Overworld")

    def callback2_name(self):
        cb = self.callback2() & ~1
        best = None
        for n, a in self.syms.addr.items():
            if a == cb and n.startswith("CB2_"):
                return n
            if a == cb and best is None:
                best = n
        return best or hex(cb)

    def script_status(self):
        return self.r8(self.sym("sGlobalScriptContextStatus"))   # 0 running, 1 waiting, 2 shutdown

    def save1(self):
        return self.r32(self.sym("gSaveBlock1Ptr"))

    def pos(self):
        s = self.save1()
        return self.rs16(s), self.rs16(s + 2)

    def map_ids(self):
        s = self.save1()
        return (self.r8(s + 4), self.r8(s + 5))

    def map_name(self):
        return self.maps.name(*self.map_ids())

    def where(self):
        return "%s %s" % (self.map_name(), self.pos())

    def fading(self):
        """a palette fade (map fade in/out, battle transition) is in progress"""
        return bool(self.r32(self.sym("gPaletteFade") + 12) >> 31)

    def settle(self, timeout_s=10):
        """run until the screen is visible, the palette fade is over and the player is standing still"""
        for _ in range(int(timeout_s * 10)):      # a map can sit black for a few seconds before its fade-in
            if self.nonblack() > 200:
                break
            self.frames(6)
        for _ in range(int(timeout_s * 10)):
            self.frames(6)
            # fog / rain / sandstorm fade in after the screen does (field_weather): input is ignored until they are up
            if self.in_overworld() and not self.fading() and self.player_idle() and (self.call("IsWeatherNotFadingIn") & 0xFF):
                break
        self.frames(10)

    def active_tasks(self):
        """names of the running overworld Tasks (gTasks, 16 slots of 40 bytes)"""
        if not hasattr(self, "_inv"):
            self._inv = {}
            for n, a in self.syms.addr.items():
                if n.startswith("Task_") or n.startswith("Cb2_") or "Task" in n:
                    self._inv.setdefault(a, n)
        t = self.sym("gTasks")
        out = []
        for i in range(16):
            if self.r8(t + i * 40 + 4):
                f = self.r32(t + i * 40) & ~1
                out.append(self._inv.get(f, hex(f)))
        return out

    def player_idle(self):
        a = self.sym("gPlayerAvatar")
        return self.r8(a + 2) == 0 and self.r8(a + 3) == 0   # runningState, tileTransitionState

    def player_locked(self):
        a = self.sym("gPlayerAvatar")
        return bool(self.r8(a + 6))  # preventStep

    def var(self, name):
        return self.call("VarGet", self.consts.get(name))

    def set_var(self, name, value):
        self.call("VarSet", self.consts.get(name), value)

    def flag(self, name):
        return bool(self.call("FlagGet", self.consts.get(name)) & 0xFF)

    def set_flag(self, name, on=True):
        self.call("FlagSet" if on else "FlagClear", self.consts.get(name))

    # ---- movement
    def step(self, d, tries=3):
        """Move one tile in direction d (U/D/L/R). Returns True if the position changed."""
        before = (self.pos(), self.map_ids())
        key = DIRS[d]
        for _ in range(tries):
            self.hold(key)
            for _ in range(24):
                self.frames(1)
                if (self.pos(), self.map_ids()) != before:
                    break
            if (self.pos(), self.map_ids()) != before:
                self.release()           # release at once, or the held key walks a second tile
                for _ in range(40):      # finish the step
                    if self.player_idle():
                        break
                    self.frames(1)
                self.frames(3)
                if self.fading():           # a door/warp: wait for the fade out and the new map's fade in
                    self.settle()
                return True
            self.release()
            self.frames(2)
        return False

    def walk(self, path, stop_on_block=False):
        """path like 'RRDD3L' (digits repeat the following letter... use 'R3' = RRR). Returns steps that failed."""
        failed = 0
        for d, n in re.findall(r"([UDLR])(\d*)", path.upper()):
            for _ in range(int(n) if n else 1):
                if not self.step(d):
                    failed += 1
                    if stop_on_block:
                        return failed
        return failed

    def wait_overworld(self, timeout_s=15):
        for _ in range(int(timeout_s * 4)):
            if self.in_overworld() and self.player_idle() and self.script_status() == 2:
                return True
            self.frames(15)
        return False

    def warp(self, mapname, x, y, timeout_s=20):
        """Test-setup warp: write sWarpDestination and call DoWarp (what the debug menu does), wait to arrive."""
        g, n = self.maps.lookup(mapname)
        wd = self.sym("sWarpDestination")
        self.w8(wd, g)
        self.w8(wd + 1, n)
        self.w8(wd + 2, 0xFF)
        self.w16(wd + 4, x)
        self.w16(wd + 6, y)
        self.call("DoWarp")
        for _ in range(int(timeout_s * 4)):
            self.frames(15)
            if self.in_overworld() and self.map_ids() == (g, n) and self.pos() == (x, y) and self.player_idle():
                self.settle()
                return True
        return False

    # ---- freeze detection
    def watch(self, seconds, probe=True, poll_s=0.5):
        """Run for `seconds`; returns a dict describing liveness.
        frozen = screen unchanged the whole time AND script context still running AND probing A/B did not move it.
        counter_ok = the game's own frame counter advanced (soft check: game loop alive)."""
        c0 = self.frame_counter()
        h0 = self.screen_hash()
        static = True
        t = 0.0
        while t < seconds:
            self.seconds(poll_s)
            t += poll_s
            if self.screen_hash() != h0:
                static = False
                break
        counter_ok = self.frame_counter() != c0
        status = self.script_status()
        running = status != 2
        frozen = False
        if static and running:
            if probe:
                self.press("A", 6, 30)
                self.press("B", 6, 30)
                frozen = self.screen_hash() == h0 and self.script_status() != 2
            else:
                frozen = True
        return {"static": static, "script_running": running, "frame_counter_advancing": counter_ok,
                "frozen": frozen, "cb2": self.callback2_name()}

    def mash(self, keys="A", n=40, hold=4, release=10):
        for _ in range(n):
            self.press(keys, hold, release)


# --------------------------------------------------------------------------- higher-level helpers
_ENUM_CACHE = {}


def enum_value(header, name):
    """value of `NAME = n,` style enum constants (species.h, items.h)."""
    if header not in _ENUM_CACHE:
        txt = (ROOT / "include/constants" / header).read_text(errors="replace")
        _ENUM_CACHE[header] = {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(\d+)\s*,", txt, re.M)}
    return _ENUM_CACHE[header][name]


_LAYOUTS = None
_MAPDATA = {}


def map_data(name):
    """dict(width, height, coll[y][x], objects, warps, coords) for a map by directory name."""
    global _LAYOUTS
    if name in _MAPDATA:
        return _MAPDATA[name]
    mj = json.loads((ROOT / "data/maps" / name / "map.json").read_text())
    if _LAYOUTS is None:
        _LAYOUTS = {l["id"]: l for l in json.loads((ROOT / "data/layouts/layouts.json").read_text())["layouts"]}
    lay = _LAYOUTS[mj["layout"]]
    w, h = lay["width"], lay["height"]
    raw = (ROOT / lay["blockdata_filepath"]).read_bytes()
    coll = [[(int.from_bytes(raw[(y * w + x) * 2:(y * w + x) * 2 + 2], "little") >> 10) & 3 for x in range(w)] for y in range(h)]
    d = {"width": w, "height": h, "coll": coll, "objects": mj.get("object_events", []),
         "warps": mj.get("warp_events", []), "coords": mj.get("coord_events", []),
         "connections": mj.get("connections") or [], "id": mj.get("id")}
    _MAPDATA[name] = d
    return d


def _bot_in_battle(self):
    return bool(self.r8(self.sym("gMain") + 0x439) & 2)


def _bot_give_mon(self, species, level=50):
    sp = species if isinstance(species, int) else enum_value("species.h", species)
    r = self.call("ScriptGiveMon", sp, level, 0)
    self.set_move(0, "MOVE_PSYCHIC", self.party_count() - 1)   # reliable strong first move (Psychic) for the battle autopilot
    return r


def _bot_party_count(self):
    return self.r8(self.r32(self.sym("gPlayerPartyCountPtr")))


def _bot_set_move(self, slot, move, mon=0):
    """put a move into party slot `mon`, move slot `slot` (test setup: give the tester a reliable first move)"""
    mv = move if isinstance(move, int) else enum_value("moves.h", move)
    self.call("SetMonMoveSlot", self.r32(self.sym("gPlayerPartyPtr")) + mon * 100, mv, slot)


def _bot_give_item(self, item, n=1):
    it = item if isinstance(item, int) else enum_value("items.h", item)
    return self.call("AddBagItem", it, n)


def _bot_fight(self, max_s=120, force_win=None):
    """Battle autopilot: mash A through intro text; once the battle waits for an action, force the win by pointing
    gBattleMainFunc at HandleEndTurn_BattleWon (test setup only; the turn engine itself is not what the smoke tests check).
    With force_win=False it plays FIGHT / first move instead."""
    main_func = self.sym("gBattleMainFunc")
    if force_win is None:
        force_win = self.force_win
    for i in range(int(max_s * 2)):
        self.check_alive("during a battle")
        if not self.in_battle():
            return True
        if force_win and (self.r32(main_func) & ~1) == self.sym("HandleTurnActionSelectionState"):
            self.w32(self.sym("gBattleOutcome") & ~3, self.r32(self.sym("gBattleOutcome") & ~3))
            self.w8(self.sym("gBattleOutcome"), 1)                                  # B_OUTCOME_WON
            self.w32(main_func, self.syms.call_addr("HandleEndTurn_BattleWon"))
        self.press("A", 4, 26)
        if i % 7 == 6:
            self.frames(60)
    return not self.in_battle()


def _bot_advance_text(self, timeout_s=40, fight=True):
    """Dismiss message boxes until the script context is finished. Returns True when the script ended."""
    t = 0.0
    while t < timeout_s:
        self.check_alive("during a scene")
        if self.in_battle():
            if not fight:
                return False
            self.fight()
            continue
        self.last_where = self.where()
        if self.script_status() == 2 and self.in_overworld() and not self.fading():
            self.frames(10)
            if self.script_status() == 2 and self.in_overworld() and not self.in_battle():
                return True
        self.press("A", 4, 22)
        t += 26 / 60
    return False


def _bot_face(self, d):
    """turn to face direction d (U/D/L/R); if the tile is free the player walks, so use next to a wall/NPC."""
    self.press(DIRS[d], 8, 8)


def _bot_interact(self, d, timeout_s=40):
    self.face(d)
    self.press("A", 4, 20)
    return self.advance_text(timeout_s)


def _bot_goto(self, x, y, max_replans=40):
    """Walk to map cell (x, y) on the current map: BFS over layout collision, avoiding NPCs, warps and trigger cells
    (except the goal); re-plans when a step is blocked (water, ledges...). Returns True on arrival."""
    name = self.map_name()
    md = map_data(name)
    blocked_dyn = set()
    for _ in range(max_replans):
        cur = self.pos()
        if cur == (x, y):
            return True
        avoid = set()
        for o in md["objects"]:
            fl = o.get("flag", "0")
            if str(fl) not in ("0", "") and self.flag(fl):
                continue
            avoid.add((o["x"], o["y"]))
        for w in md["warps"]:
            avoid.add((w["x"], w["y"]))
        for c in md["coords"]:
            avoid.add((c["x"], c["y"]))
        avoid |= blocked_dyn
        avoid.discard((x, y))
        W, H = md["width"], md["height"]
        prev = {cur: None}
        q = [cur]
        found = False
        while q and not found:
            nq = []
            for (cx, cy) in q:
                for d, (dx, dy) in (("U", (0, -1)), ("D", (0, 1)), ("L", (-1, 0)), ("R", (1, 0))):
                    n = (cx + dx, cy + dy)
                    if n in prev or not (0 <= n[0] < W and 0 <= n[1] < H):
                        continue
                    if md["coll"][n[1]][n[0]] or n in avoid:
                        continue
                    prev[n] = ((cx, cy), d)
                    if n == (x, y):
                        found = True
                        break
                    nq.append(n)
                if found:
                    break
            q = nq
        if not found:
            return False
        path = []
        n = (x, y)
        while prev[n]:
            n, d = prev[n][0], prev[n][1]
            path.append((d, n))
        path.reverse()
        moved = True
        # path entries are (dir, from_cell); the cell stepped onto is the next one
        cells = []
        cx, cy = cur
        for d, _frm in path:
            dx, dy = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}[d]
            cx, cy = cx + dx, cy + dy
            cells.append((d, (cx, cy)))
        for d, cell in cells:
            before_map = self.map_ids()
            if not self.step(d):
                blocked_dyn.add(cell)
                moved = False
                break
            if self.script_status() != 2 or self.map_ids() != before_map:
                return self.pos() == (x, y) and self.map_ids() == before_map
        if moved and self.pos() == (x, y):
            return True
    return self.pos() == (x, y)


Bot.in_battle = _bot_in_battle
Bot.give_mon = _bot_give_mon
Bot.party_count = _bot_party_count
Bot.give_item = _bot_give_item
Bot.set_move = _bot_set_move
Bot.fight = _bot_fight
Bot.advance_text = _bot_advance_text
Bot.face = _bot_face
Bot.interact = _bot_interact
Bot.goto = _bot_goto


# --------------------------------------------------------------------------- boot helpers
def _boot_flow(b, shot_every=0):
    """Title -> New Game -> intro speech -> default name -> overworld. Returns True when the player has control."""
    b.truck_seen = False
    b.frames(1500)                       # logos + intro movie
    b.shot("title")
    for _ in range(4):
        b.press("START", 6, 50)          # skip intro, pass the title
    b.shot("main_menu")
    b.press("A", 6, 90)                  # NEW GAME
    naming_done = False
    for i in range(400):
        cb = b.callback2() & ~1
        if cb == b.sym("CB2_NamingScreen") and not naming_done:
            b.shot("naming_screen")
            b.press("START", 6, 20)      # jump to OK -> default name
            b.press("A", 6, 60)
            naming_done = True
            continue
        if b.in_overworld():
            # Orleans has no moving-truck intro (CB2_NewGame fades in); flag it if the vanilla truck task ever runs
            if "Task_HandleTruckSequence" in b.active_tasks():
                b.truck_seen = True
            b.settle()
            if b.player_idle() and b.script_status() == 2:
                return True
        b.press("A", 4, 26)
        if shot_every and i % shot_every == 0:
            b.shot("intro_%03d" % i)
    return False


Bot.new_game = lambda self, shot_every=0: _boot_flow(self, shot_every)


# --------------------------------------------------------------------------- the in-game clock
# The ROM runs on the fake RTC (OW_USE_FAKE_RTC, Gen 9 ratio): the clock lives in the save (SaveBlock3.fakeRTC) and advances 20 game seconds per
# second of play (one day = 72 minutes), whatever the emulator's own RTC says. Tests set it directly through the game's own function.
TIMES_OF_DAY = ("morning", "day", "evening", "night")   # the TimeOfDay enum order; boundaries (Gen 8+): 6, 10, 19, 20
CLOCK_SECONDS_PER_SECOND = 20


def _bot_set_clock(self, hour, minute=0, day=0):
    """put the in-game clock at day:hour:minute (test setup; RtcCalcLocalTimeOffset also zeroes the local offset so the clock reads exactly this)"""
    self.call("RtcCalcLocalTimeOffset", day, hour, minute, 0)
    self.frames(2)


def _bot_clock(self):
    """(day, hour, minute, second) of the local clock, recomputed from the fake RTC"""
    self.call("RtcCalcLocalTime")
    g = self.sym("gLocalTime")
    return self.rs16(g), self.r8(g + 2), self.r8(g + 3), self.r8(g + 4)


def _bot_clock_seconds(self):
    d, h, m, s = self.clock()
    return ((d * 24 + h) * 60 + m) * 60 + s


def _bot_time_of_day(self):
    """0 morning, 1 day, 2 evening, 3 night, as the engine's GetTimeOfDay says"""
    return self.call("GetTimeOfDay") & 0xFF


Bot.set_clock = _bot_set_clock
Bot.clock = _bot_clock
Bot.clock_seconds = _bot_clock_seconds
Bot.time_of_day = _bot_time_of_day


def contact_sheet(shots, path, cols=6, thumb=(240, 160)):
    """shots: [(label, png path)] -> one PNG grid with a caption under each thumbnail."""
    from PIL import ImageDraw
    if not shots:
        return None
    cap = 14
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb[0], rows * (thumb[1] + cap)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(shots):
        x, y = (i % cols) * thumb[0], (i // cols) * (thumb[1] + cap)
        try:
            sheet.paste(Image.open(p).convert("RGB").resize(thumb, Image.NEAREST), (x, y + cap))
        except Exception:
            pass
        d.text((x + 2, y + 2), str(label)[:44], fill=(230, 230, 120))
    sheet.save(path)
    return path
