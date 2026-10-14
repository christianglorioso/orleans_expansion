"""Hail is replaced by Snowscape everywhere the game uses it (2026-10-14):
  * species that learned Hail now learn Snowscape (level-up, read from a freshly made mon), nobody knows Hail at a level where it was learned;
  * TM07 teaches Snowscape;
  * a real Battle Frontier battle where Snowscape is used shows the Snow text ("It started to snow!"), starts Snow weather and counts for Snow Setter;
  * the new trophy texts are in the ROM and the TROPHIES menu shows them.
"""
import sys
from pathlib import Path

from bot import Bot, ROOT, enum_value

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
import lairutil as LU  # noqa: E402
import t15_fixa_story as S15  # noqa: E402
import t18_frontier as F  # noqa: E402
import t25_boss as B  # noqa: E402
import t29_lair_unlocks as T29  # noqa: E402

MON_DATA_MOVE1 = 20
GLYPHS = S15.GLYPHS


def text_at(b, sym, n=200):
    a = b.sym(sym)
    out = []
    for i in range(n):
        c = b.r8(a + i)
        if c == 0xFF:
            break
        out.append(GLYPHS.get(c, "?"))
    return "".join(out)


def party_moves(b, slot):
    mon = b.r32(b.sym("gPlayerPartyPtr")) + slot * 100
    return [b.call("GetMonData2", mon, MON_DATA_MOVE1 + i) & 0xFFFF for i in range(4)]


def run(b, t):
    b.new_game()
    snow = enum_value("moves.h", "MOVE_SNOWSCAPE")
    hail = enum_value("moves.h", "MOVE_HAIL")
    # ---- a Frontier battle with Snowscape
    b.set_var("VAR_ORLEANS_STORY", 45)
    for s in ("SPECIES_PIKACHU", "SPECIES_EEVEE", "SPECIES_SNORLAX", "SPECIES_GYARADOS"):
        b.give_mon(s, 50)
    b.frames(300)
    b.set_move(0, "MOVE_SNOWSCAPE", 0)
    F.start_challenge(b, "Tower")
    started = False
    for _ in range(400):
        if b.in_battle():
            started = True
            break
        b.press("A", 4, 26)
        b.frames(8)
    t.check("a Frontier battle starts", started, b.where())
    if started:
        t.check("the first turn menu waits", B.wait_menu(b))
        s0 = LU.counter(b, "SNOW")
        turn0 = B.turn_counter(b)
        T29.choose(b, 0)
        seen = []
        shot = False
        for i in range(400):
            b.check_alive("snowscape turn")
            txt = text_at(b, "gDisplayedStringBattle")
            if txt and txt not in seen:
                seen.append(txt)
            if "snow" in txt.lower() and not shot:
                shot = True
                b.shot("snow_text")
            if B.at_menu(b) and B.turn_counter(b) != turn0:
                break
            b.press("A", 4, 26) if i % 3 == 2 else b.frames(10)
        t.check("the battle text says it started to snow (%s)" % seen[-6:], any("snow" in x.lower() for x in seen))
        t.check("no hail text", not any("hail" in x.lower() for x in seen))
        w = b.r16(b.sym("gBattleWeather"))
        t.check("the battle weather is Snow (gBattleWeather %#x)" % w, w & 0x100)
        t.check("Snow Setter counts it: SNOW %d -> %d" % (s0, LU.counter(b, "SNOW")), LU.counter(b, "SNOW") == s0 + 1)

    # ---- learnsets (after the battle: the party was the battle team): a mon made at the level where Hail used to be learned knows Snowscape now
    cases = [("SPECIES_MAMOSWINE", 25), ("SPECIES_SNORUNT", 50), ("SPECIES_FROSLASS", 40), ("SPECIES_GLACEON", 35), ("SPECIES_SPHEAL", 48), ("SPECIES_VANILLITE", 40)]
    for i, (sp, lv) in enumerate(cases):
        b.call("ScriptGiveMon", enum_value("species.h", sp), lv, 0)
        mv = party_moves(b, b.party_count() - 1)
        t.check("%s at Lv%d knows Snowscape, not Hail (%s)" % (sp, lv, mv), snow in mv and hail not in mv)
    # ---- TM07
    tm = enum_value("items.h", "ITEM_TM07")
    mv = b.call("ItemIdToBattleMoveId", tm) & 0xFFFF
    t.check("TM07 teaches Snowscape (move %d)" % mv, mv == snow)

    # ---- the new trophy texts are in the ROM, and the TROPHIES menu opens on them
    import re
    rev = {v: k for k, v in GLYPHS.items()}
    rev["\n"] = 0xFE
    src = (ROOT / "src/data/achievements.h").read_text(encoding="utf-8", errors="replace")
    rom = (Path(ROOT) / "pokemon_orleans.gba").read_bytes()
    for key, want in (("LEGEND_OGERPON", "Obtain Ogerpon in the Courir Glade"), ("MIDNIGHT_WOLF", "Obtain Lycanroc Midnight at night"),
                      ("LEGEND_ARTICUNO_GALAR", "Obtain Galarian Articuno at the")):
        m = re.search(r'\.id = ACH_' + key + r',.*?\.description = COMPOUND_STRING\("([^"]*)"\)', src, re.S)
        s = m.group(1).replace(chr(92) + "n", chr(10))
        rev[" "] = 0
        enc = bytes(rev.get(ch, 0xFF) for ch in s)
        t.check("%s: '%s' is in the ROM" % (key, s.replace("\n", " / ")), s.startswith(want) and enc in rom and 0xFF not in enc)
    b.set_flag("FLAG_SYS_POKEDEX_GET")
    b.set_flag("FLAG_SYS_POKEMON_GET")
    b.warp("CrescentCity", 45, 63)
    b.frames(60)
    b.press("START", 6, 30)
    b.frames(30)
    b.press("UP", 6, 10)
    b.press("A", 6, 10)
    b.frames(120)
    t.check("TROPHIES opens", "AchievementsMenu" in b.callback2_name(), b.callback2_name())
    # no trophy description clips in the footer panel: walk every row of every page, find the right-most text pixel (white on the blue panel)
    from PIL import Image
    widest = []
    for page in range(7):
        seen = set()
        for row in range(60):
            b.frames(8)
            png = b.shot("p%d_r%d" % (page, row))
            im = Image.open(png).convert("RGB")
            h = hash(im.tobytes())
            if h in seen:
                break
            seen.add(h)
            xs = [x for y in range(250, 316) for x in range(0, 480) if min(im.getpixel((x, y))) > 200]
            widest.append((max(xs) if xs else 0, str(png)))
            b.press("DOWN", 4, 12)
        b.press("RIGHT", 4, 20)
        b.frames(30)
    widest.sort(reverse=True)
    t.note("widest footer lines: %s" % widest[:8])
    t.check("no trophy footer line reaches the panel edge (widest text pixel x=%d of 480)" % widest[0][0], widest[0][0] < 452, widest[:3])
