# Orleans playtest bot

Headless smoke tests for the ROM: a tiny libmgba program (WSL) driven from Python (Windows). No display, no GUI.

```
python tools/playtest/run_all.py                  # every test against the current pokeemerald.gba
python tools/playtest/run_all.py t00 t02          # only tests whose file name starts with these
python tools/playtest/run_all.py --slow           # everything including t_transitions
python tools/playtest/run_all.py --rom X.gba --run tag
```

Prints a pass/fail table (PASS / FAIL / ERROR / CRASH). Output goes to `tools/playtest/out/<run>/` (git-ignored):
`results.json`, and per test a folder with the screenshots (`NN_label.png`, 2x), `contact*.png` contact sheets,
`result.json` and `harness.log` (emulator warnings). Exit code 1 if anything is not PASS.

## One-time setup (WSL Ubuntu)

`libmgba` (headers + `libmgba.so`) and `gcc` must be installed. Build the harness once, and again after editing `harness.c`:

```
wsl -d Ubuntu -- bash /mnt/c/Users/chris/orleans_expansion/orleans_expansion/tools/playtest/build_harness.sh
```

It writes `~/.cache/orleans_playtest/harness`. Python needs Pillow. The ROM must have been built by `tools/wsl_build.sh`
(the bot reads `~/orleans_expansion/pokeemerald.map` and `.elf` in the WSL mirror for symbol addresses; they must match the ROM).

## How it works

- `harness.c`: loads the ROM, runs frames, reads/writes memory, takes screenshots, save states; line protocol on stdin/stdout
  (`frames N`, `press KEYS HOLD [REL]`, `read8/16/32`, `write8/16/32`, `shot`, `hash`, `nonblack`, `savestate`, `loadstate`,
  `reset`, `rtc`, `regs`, `runto`, `call ADDR r0..r3`). The RTC is fixed (default 1760000000, Oct 2025) and advances
  deterministically with emulated time, so runs reproduce. `call` runs a ROM function from a clean point in the main loop
  (entry of `PlayTimeCounter_Update`), then restores all registers.
- `bot.py`: `Bot` wraps it. Symbols from the link map + `readelf`, constants from the real preprocessor (`gcc -E -dM`, cached in `out/`).
  - read: `var(name)`, `flag(name)`, `map_name()`, `pos()`, `where()`, `script_status()` (0 running, 1 waiting, 2 done), `in_battle()`, `active_tasks()`
  - write (test setup only): `set_var`, `set_flag`, `give_mon("SPECIES_X", lvl)`, `give_item`, `warp(map, x, y)` (writes `sWarpDestination`, calls `DoWarp`, like the debug menu)
  - input: `press("A")`, `step("U|D|L|R")`, `walk("RRD2")`, `goto(x, y)` (BFS over the layout collision), `interact("U")`, `advance_text()` (mashes A through messages and battles until the script ends)
  - checks: `shot(label)`, `watch(seconds)` (freeze check: screen static + script still running + probing A/B did not move it; frame counter advancing), `crashed()` / `check_alive()` (game fell back to the boot screen; raises `GameCrash`)
  - `new_game()`: title -> New Game -> intro -> default name -> control in the shelter (about 3 s of wall clock).
- Battles: the autopilot mashes A, and once the turn menu is waiting it forces the win by pointing `gBattleMainFunc` at
  `HandleEndTurn_BattleWon`. Set `bot.force_win = False` to really play (it presses FIGHT / first move, which is Psychic on the tester).

## Adding a test

Create `tools/playtest/tests/tNN_name.py` (files starting with `t` are picked up, sorted by name):

```python
def run(b, t):                      # b = Bot (fresh emulator), t = result collector
    b.new_game()
    b.set_var("VAR_ORLEANS_STORY", 13)
    b.warp("CrescentCity", 45, 63)
    b.walk("DD")
    t.check("gate shows a message", b.script_status() != 2, b.where())
    b.shot("gate")
    t.bug("optional: note a real game problem you saw")
```

Every test starts from a clean boot (new emulator). Do not put apostrophes/odd escapes through shell heredocs when generating files.
`t.check(name, cond, detail)` fails the test when `cond` is false; an exception is ERROR; the game resetting is CRASH.
Map names are the directory names in `data/maps` (`Route3`, `CrescentCity`, ...), vars and flags are the constant names.

## Tests

| test | what |
|---|---|
| t00_boot | clean boot to control in the shelter, no freeze |
| t01_slice | Mom's gifts, leaving the shelter, Wingull trigger, Lafayette's Pokedex, Jayden at the landing and the canoe (story 0 to 5) |
| t02_chapter2 | Storm's Edge arrival, Crescent arrival, the floodwater gate at Crescent's south exit (message + turn back, several columns, open after the badge flag) |
| t03_jayden_bridge | Jayden on the Route 3 bridge (all five trigger rows) |
| t_transitions | SLOW (about 4 min, `run_all.py --slow` or name it). Walks the player across all 34 connections in both directions (10 cells before to 10 after, a frame per step, Surf forced on water), detects blocked passages / seam flips / black cells, and grades the border view along every unconnected edge. Output: `out/<run>/t_transitions/{filmstrips,pairs,joins,edges}`, `summary.txt`, `results.json` |
| t_edges | every outdoor map: warp next to each connection seam and open edge, screenshot (about 335 shots, 8 contact sheets) |

## Known limits

- Real play-through in mGBA, not Pizza Boy: a crash that shows up only here may be an emulator difference, but a crash in
  mGBA is worth checking on device. Save/load (SRAM) is in memory only; use `savestate`/`loadstate`.
- `goto` ignores tile behaviours (water, ledges); it re-plans when a step is blocked.
- Battles are shortcut by default (see above); wild encounters are not exercised.
