"""Orleans Pokedex: regional numbering of all 300 entries, form/Mega species exist, TM/tutor compatibility, a party mon of
an Orleanian form and of a custom Mega base can be created. Reads the expected numbers from tools/dex/out/dex_order.txt
(written by tools/dex/apply_dex_order.py)."""
from pathlib import Path

from bot import enum_value

ROOT = Path(__file__).resolve().parents[3]


def run(b, t):
    b.new_game()
    rows = [l.split("\t") for l in (ROOT / "tools/dex/out/dex_order.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    t.check("sheet order file has 300 entries", len(rows) == 300, len(rows))
    wrong = []
    for num, name, const, nd in rows:
        got = b.call("SpeciesToHoennPokedexNum", enum_value("species.h", const)) & 0xFFFF
        if got != int(num):
            wrong.append((name, int(num), got))
    t.check("every Orleans dex entry resolves to its sheet number", not wrong, wrong[:6])
    # removed lines are outside the regional dex
    out = [n for n in ("SPECIES_LOTAD", "SPECIES_LOMBRE", "SPECIES_LUDICOLO", "SPECIES_PINCURCHIN", "SPECIES_CHATOT")
           if (b.call("SpeciesToHoennPokedexNum", enum_value("species.h", n)) & 0xFFFF) != 0]
    t.check("Lotad line, Pincurchin and Chatot have no Orleans dex number", not out, out)
    tm = lambda sp, mv: bool(b.call("CanLearnTeachableMove", enum_value("species.h", sp), enum_value("moves.h", mv)) & 0xFF)
    t.check("Orleanian Voltorb learns Thunderbolt by TM", tm("SPECIES_VOLTORB_ORLEANIAN", "MOVE_THUNDERBOLT"))
    t.check("Orleanian Voltorb cannot learn Dragon Claw", not tm("SPECIES_VOLTORB_ORLEANIAN", "MOVE_DRAGON_CLAW"))
    for sp in ("SPECIES_TANGELA_ORLEANIAN", "SPECIES_CHANDELURE_ORLEANIAN", "SPECIES_SKELEDIRGE", "SPECIES_LYCANROC_MIDNIGHT"):
        before = b.party_count()
        b.give_mon(sp, 30)
        t.check("can create a %s in the party" % sp, b.party_count() == before + 1, b.party_count())
    w = b.watch(3)
    t.check("game loop alive afterwards", not w["frozen"] and w["frame_counter_advancing"], w)
