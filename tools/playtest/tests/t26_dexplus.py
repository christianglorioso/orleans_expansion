"""Pokedex Plus on Orleans (2026-10-14): the list header reads ORLEANS (the sprite text in graphics/pokedex/hgss/tileset_interface*.png, no longer HOENN) and
the AREA page uses the Orleans region map (graphics/pokedex/region_map.png is the Pokenav map's picture) with glowing area markers.

Screenshots: C:/Users/chris/orleans_expansion/tile_review/dexplus_list.png, dexplus_area_<species>.png (reviewed by eye)."""
import shutil
import sys
from pathlib import Path

from bot import ROOT, enum_value
sys.path.insert(0, str(Path(__file__).parent))
from t24_config import REVIEW, start_menu


def snap(b, name):
    png = b.shot(name)
    REVIEW.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, REVIEW / ("dexplus_%s.png" % name))


def run(b, t):
    b.new_game()
    rows = [l.split("\t") for l in (ROOT / "tools/dex/out/dex_order.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    number = {r[2]: int(r[0]) for r in rows}
    for num, name, const, nd in rows:
        nat = b.call("SpeciesToNationalPokedexNum", enum_value("species.h", const)) & 0xFFFF
        b.call("GetSetPokedexFlag", nat, 2)
        b.call("GetSetPokedexFlag", nat, 3)
    b.set_flag("FLAG_SYS_POKEDEX_GET", True)
    b.set_flag("FLAG_SYS_POKEMON_GET", True)
    b.warp("Route6", 19, 14)
    b.frames(30)
    start_menu(b, "MENU_ACTION_POKEDEX")
    t.check("the Pokedex opens (Dex+ list)", b.callback2_name() == "CB2_Pokedex", b.callback2_name())
    snap(b, "list")
    cursor = 1
    for const in ("SPECIES_SPEAROW_ORLEANIAN", "SPECIES_RATTATA", "SPECIES_ZIGZAGOON"):
        delta = number[const] - cursor
        for _ in range(abs(delta) // 7):
            b.press("RIGHT" if delta > 0 else "LEFT", 6, 18)
        for _ in range(abs(delta) % 7):
            b.press("DOWN" if delta > 0 else "UP", 6, 14)
        cursor = number[const]
        b.frames(30)
        b.press("A", 6, 30)
        b.frames(60)
        b.press("RIGHT", 6, 30)                     # INFO -> AREA
        b.frames(120)
        snap(b, "area_" + const[8:].lower())
        t.check("%s: the AREA page is up" % const, b.callback2_name() == "CB2_Pokedex" and b.nonblack() > 1000 and not b.crashed(), b.callback2_name())
        b.press("B", 6, 30)
        b.frames(40)

    # Dept 2F: the TM clerk (3, 5) can be talked to across the shelf (MB_COUNTER) from the south cell (3, 7), and from the north cell (3, 4)
    b.warp("CrescentCity_Dept2f", 3, 7)
    b.frames(30)
    t.check("Dept2f: standing at (3, 7)", b.pos() == (3, 7), b.pos())
    b.face("U")
    b.press("A", 4, 20)
    b.frames(30)
    t.check("Dept2f: A across the shelf starts the clerk's script", b.script_status() != 2 or not b.in_overworld(), b.where())
