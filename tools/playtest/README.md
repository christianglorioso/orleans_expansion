# Orleans playtest bot

Headless smoke tests for the ROM: a tiny libmgba program (WSL) driven from Python (Windows). No display, no GUI.

```
python tools/playtest/run_all.py                  # every test against the current pokemon_orleans.gba
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
(the bot reads `~/orleans_expansion/pokemon_orleans.map` and `.elf` in the WSL mirror for symbol addresses; they must match the ROM).

## How it works

- `harness.c`: loads the ROM, runs frames, reads/writes memory, takes screenshots, save states; line protocol on stdin/stdout
  (`frames N`, `press KEYS HOLD [REL]`, `read8/16/32`, `write8/16/32`, `shot`, `hash`, `nonblack`, `savestate`, `loadstate`,
  `reset`, `rtc`, `dumpsave PATH`, `regs`, `runto`, `call ADDR r0..r3`). `harness ROM [unix_time [save.sav]]`: the optional .sav is loaded as
  the cartridge's flash save (a save from another build), `dumpsave` writes the flash image out. The emulated hardware RTC (`rtc`) is no longer
  used by the game: since 2026-10-13 the ROM runs on its own in-game clock (fake RTC, Gen 9 ratio: 20 game seconds per second of play, a day = 72
  minutes), kept in the save. Tests set it with `b.set_clock(hour, minute, day)` (calls `RtcCalcLocalTimeOffset`), read it with `b.clock()` /
  `b.clock_seconds()` / `b.time_of_day()` (0 morning, 1 day, 2 evening, 3 night; boundaries 6/10/19/20). `stepto ADDR N` (ring of executed pcs, regs and stack at a function entry) and `watchring ADDR N` (the pcs before a RAM word changes) find who calls or corrupts what. `call` runs a ROM function from a clean point in the main loop
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
| t12_healers | every healer's nurse restores the party and the script ends; a whiteout respawns at a healer |
| t13_clock | the in-game clock: new game at 08:00, 20 game seconds per second, midnight rollover, time-of-day boundaries; the rest spots (all 13 healer rooms: menu opens, B backs out) and Rest until MORNING / DAY / EVENING / NIGHT (clock, heal, "already", CANCEL); Redfield mirrors (night: nothing, rest until morning: they turn), Ursaluna Bloodmoon and the rougarou (night only), the day/night tint; `FakeRtc_MigrateSave` on a save without a clock |
| t13b_oldsave | a real save from the previous (real-RTC) build, `fixtures/old_build.sav` (git-ignored; made with that ROM through the START menu, `dumpsave`), is continued on this ROM: same place, story, flags, party, a morning clock, and a save/continue round trip keeps the clock |
| t15_fixa_story | audit fix phase A: the Blacksnake base partner battle (Wren's low-level team per starter line, loss -> retry, win -> carving), the carving text, Wren no longer at the gate, Tupelo's late lines (badge count / finale / both entrances), draws in the Wren and Rayquaza raids are not wins, the ceremony's water landing on Route 8, the buoy Voltorb you ran from, the nurse's bed hint, the Frontier couple, the real raid partner per starter. Reads the message text from `gStringVar4` |
| t16_weather | overworld weather per map (`tools/mapgen/weather_plan.py`) read from `GetCurrentWeather` at the key story values / flags, the switches before and after, interiors none, map.json headers match |
| t17_firstbattle | a real new game with no set_var jumps: Mom, starter pick (story 3 directly, the Wingull scene is cut), free shelter steps, Lafayette, Jayden at the landing as the first battle (story 5) |
| t14_fixb | fix B: hidden items picked up by Surf (Routes 10, 11, 21, 22), signs read from the water, six hidden Heart Scales, the blind trainers now spot the player (Routes 6, 11, 18, 19, 20, 22, 25, Grand Oak gym), the Arena lobby BP clerks sell, Lutin's sprite |
| t18_frontier | the Battle Frontier: all seven facilities from the Crescent plaza (door in, mat out, a real challenge started through the attendant with party selection and save, retire, a lost challenge, save + reset + Continue; Pike path room, Pyramid stairs) and every exit lands on the plaza in front of the same door, never a Hoenn map |
| t24_config | the 2026-10-14 config batch: HGSS followers (the worst object windows of 17 maps incl. the lairs and the Game Corner: follower present, no NPC lost, Surf/Dive/bikes hide it, FLAG_TEMP_HIDE_FOLLOWER, large/legendary/placeholder-form leads), first-pickup item descriptions, Lafayette's Exp. Share (chapter 3) and its toggle flag, reusable TMs (gift absorbed, SOLD OUT in the shop), the IV/EV summary cycle (stats / IVs / EVs) with the heap budget, Dex+ pages for 12 Orleans species (regional order, forms, Linking Cord / Black Augurite / Fais-do-do Ribbon evolutions), the fishing chain. Screenshots: `tile_review/config_*.png` |
| t28_fixS | phase-3 fix S: the shipped ROM holds the fixed text (Route 6 Tristan, the Pointe Rouge angler, the Route 10 swimmers, Cayenne) and `gen_drift_check --fast` / `story_lint` are clean, Fifolet at story 16, rest cushions faced from every side (Grand Oak, Frontier Center), the one-cell sight lines (Route 15 x2, Route 20), the Route 25 sign from the west and Tupelo from the water at the ceremony, Chloe Joltik + Elekid, Route 12 fishing cap, the Pry Bar icon, the BP clerk descriptions in two lines |
| t_transitions | SLOW (about 4 min, `run_all.py --slow` or name it). Walks the player across all 34 connections in both directions (10 cells before to 10 after, a frame per step, Surf forced on water), detects blocked passages / seam flips / black cells, and grades the border view along every unconnected edge. Output: `out/<run>/t_transitions/{filmstrips,pairs,joins,edges}`, `summary.txt`, `results.json` |
| t_edges | every outdoor map: warp next to each connection seam and open edge, screenshot (about 335 shots, 8 contact sheets) |

## Known limits

- Real play-through in mGBA, not Pizza Boy: a crash that shows up only here may be an emulator difference, but a crash in
  mGBA is worth checking on device. Save/load (SRAM) is in memory only; use `savestate`/`loadstate`.
- `goto` ignores tile behaviours (water, ledges); it re-plans when a step is blocked.
- Battles are shortcut by default (see above); wild encounters are not exercised.
