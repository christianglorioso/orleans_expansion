"""Orleans Pokedex: regional numbering of all 300 entries, form/Mega species exist, TM/tutor compatibility, a party mon of
an Orleanian form and of a custom Mega base can be created. Reads the expected numbers from tools/dex/out/dex_order.txt
(written by tools/dex/apply_dex_order.py)."""
from pathlib import Path

from bot import enum_value

ROOT = Path(__file__).resolve().parents[3]
FORM_CONSTS = {"SPECIES_RAICHU_ALOLA", "SPECIES_VULPIX_ALOLA", "SPECIES_NINETALES_ALOLA", "SPECIES_LILLIGANT_HISUI", "SPECIES_ROTOM_HEAT",
               "SPECIES_ROTOM_WASH", "SPECIES_ROTOM_FROST", "SPECIES_ROTOM_FAN", "SPECIES_ROTOM_MOW", "SPECIES_ROCKRUFF_OWN_TEMPO",
               "SPECIES_LYCANROC_DUSK", "SPECIES_LYCANROC_MIDNIGHT", "SPECIES_SANDSHREW_ALOLA", "SPECIES_SANDSLASH_ALOLA",
               "SPECIES_FLOETTE_ETERNAL", "SPECIES_URSALUNA_BLOODMOON", "SPECIES_ARTICUNO_GALAR", "SPECIES_ZAPDOS_GALAR",
               "SPECIES_MOLTRES_GALAR", "SPECIES_OGERPON_WELLSPRING", "SPECIES_OGERPON_HEARTHFLAME", "SPECIES_OGERPON_CORNERSTONE"}


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
    # the 22 alternate forms with their own national number open as themselves in the Pokedex (not as the base species)
    forms = [r for r in rows if r[2] in FORM_CONSTS]
    t.check("found the 22 alternate-form rows", len(forms) == 22, len(forms))
    wrong = []
    for num, name, const, nd in forms:
        sp = enum_value("species.h", const)
        natnum = b.call("SpeciesToNationalPokedexNum", sp) & 0xFFFF
        back = b.call("NationalPokedexNumToSpecies", natnum) & 0xFFFF
        if back != sp:
            wrong.append((name, back, sp))
    t.check("each alternate form's national number resolves to that exact species", not wrong, wrong[:5])
    # move relearner: tutor and egg lists stay closed until the Crescent City tutor sets their flags
    party = b.r32(b.sym("gPlayerPartyPtr"))
    idx = b.party_count() - 1
    mon = party + 100 * idx
    LEVEL, EGG, TM, TUTOR = 0, 1, 2, 3
    closed = [bool(b.call("CanBoxMonRelearnMoves", mon, s) & 0xFF) for s in (EGG, TUTOR)]
    t.check("tutor and egg relearners are closed before the tutor flags", closed == [False, False], closed)
    b.set_flag("FLAG_ORLEANS_TUTOR_RELEARNER")
    b.set_flag("FLAG_ORLEANS_EGG_RELEARNER")
    opened = bool(b.call("CanBoxMonRelearnMoves", mon, TUTOR) & 0xFF)
    t.check("tutor relearner offers moves once FLAG_ORLEANS_TUTOR_RELEARNER is set", opened)
    w = b.watch(3)
    t.check("game loop alive afterwards", not w["frozen"] and w["frame_counter_advancing"], w)
