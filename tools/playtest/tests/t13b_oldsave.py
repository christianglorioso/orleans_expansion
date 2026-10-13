"""Old saves and the in-game clock: a real save made by the previous ROM (no fake RTC: tools/playtest/fixtures/old_build.sav, new game on the old
build, story 20, one badge, Mew, standing in Redfield, saved through the START menu) is continued on this ROM. It must load where it was saved, with its
story, flags and party, get a clock (day 0, 08:00, morning), and the clock must then survive a save/continue round trip on this ROM (the marker
persists, no second migration). The fixture is a git-ignored .sav (the repo does not carry saves); without it the test only notes that."""
from pathlib import Path

from bot import Bot, PLAYTEST

FIXTURE = PLAYTEST / "fixtures" / "old_build.sav"


def continue_game(b):
    """boot to the title, CONTINUE, until the player has control"""
    b.frames(1500)
    for _ in range(4):
        b.press("START", 6, 50)
    b.press("A", 6, 90)               # CONTINUE
    b.press("A", 6, 90)               # the save file's summary
    for _ in range(40):
        if b.in_overworld() and b.player_idle():
            break
        b.press("A", 4, 30)
    b.settle()


def save_game(b):
    """START menu -> SAVE (the third entry) -> YES -> (a save exists) YES; waits for the slow text and the long flash write"""
    b.press("START", 6, 30)
    b.press("DOWN", 6, 10)
    b.press("DOWN", 6, 10)
    b.press("A", 6, 40)
    b.frames(150)                     # the prompt types out
    b.press("A", 6, 40)               # YES
    b.frames(200)
    b.press("A", 6, 40)               # "overwrite the previous save?": YES
    b.frames(900)
    for _ in range(4):
        b.press("A", 4, 60)
    b.frames(120)


def run(b, t):
    if not FIXTURE.exists():
        t.note("fixture %s missing: old-save continue not tested" % FIXTURE)
        return
    old = Bot(rom=b.rom, out_dir=b.out / "oldsave", save=FIXTURE)
    try:
        continue_game(old)
        old.shot("continued_old_save")
        t.check("the old save loads where it was saved (Redfield 12,15)", old.map_name() == "Redfield" and old.pos() == (12, 15), old.where())
        t.check("its story, flag and party survived", old.var("VAR_ORLEANS_STORY") == 20 and old.flag("FLAG_BADGE03_GET") and old.party_count() == 1,
                "story=%d party=%d" % (old.var("VAR_ORLEANS_STORY"), old.party_count()))
        d, h, m, s = old.clock()
        t.check("it gets a clock: day 0, 08:00, morning", d == 0 and h == 8 and m < 5 and old.time_of_day() == 0, (d, h, m, s, old.time_of_day()))
        t0 = old.clock_seconds()
        old.frames(60 * 30)
        t.check("the clock runs on the migrated save (30 s of play = 10 game minutes)", abs(old.clock_seconds() - t0 - 600) <= 30, old.clock_seconds() - t0)
        # a save/continue round trip on this ROM keeps the clock (the marker persists: no second migration)
        old.set_clock(15, 30, day=3)
        save_game(old)
        out = b.out / "oldsave" / "roundtrip.sav"
        old.h.cmd("dumpsave " + _wsl(out))
    finally:
        old.close()
    again = Bot(rom=b.rom, out_dir=b.out / "oldsave2", save=out)
    try:
        continue_game(again)
        d, h, m, s = again.clock()
        again.shot("continued_new_save")
        t.check("a save made on the clock build keeps its clock (day 3, 15:30)", (d, h) == (3, 15) and 25 <= m <= 45, (d, h, m, s))
        t.check("and its place", again.map_name() == "Redfield", again.where())
    finally:
        again.close()


def _wsl(p):
    from bot import wsl_path
    return wsl_path(Path(p))
