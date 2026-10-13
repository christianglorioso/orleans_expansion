"""Renames the seven Frontier Brains as Orleans characters everywhere their vanilla names / titles show up (idempotent, re-runnable).

usage: python tools/frontier/rename_brains.py [--root DIR]      (DIR = an overlay tree; files are copied from the repo first)

 name (<= 10 letters, the trainer-table limit) and title (<= 12, the trainer-class-name limit):
   Tower   ANABEL  / SALON MAIDEN  ->  CELESTE    / SALON BELLE   (a French Quarter salon hostess)
   Dome    TUCKER  / DOME ACE      ->  BEAUREGARD / ZYDECO ACE    (a zydeco showman who treats every match as a dance hall)
   Palace  SPENSER / PALACE MAVEN  ->  ARMAND     / MARDI MAVEN   (a Mardi Gras float builder)
   Arena   GRETA   / ARENA TYCOON  ->  MARGUERITE / KREWE QUEEN   (the krewe captain who trained the Crescent parade leader)
   Factory NOLAND  / FACTORY HEAD  ->  ETIENNE    / MILL FOREMAN  (a sugar-mill foreman)
   Pike    LUCY    / PIKE QUEEN    ->  LUCILLE    / SWAMP QUEEN   (a bayou matriarch)
   Pyramid BRANDON / PYRAMID KING  ->  LAFITTE    / MOUND KING    (a pirate-king of the old mounds)
 Edited: src/data/trainers.party (Name:), src/battle_main.c (class titles), src/frontier_util.c (gFrontierBrainInfo lines), the .string lines of
 data/maps/BattleFrontier_*/scripts.inc, and the Arena brain's own dialogue (rewritten with the parade-leader tie-in).
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT
if "--root" in sys.argv:
    OUT = Path(sys.argv[sys.argv.index("--root") + 1])

BRAINS = [  # facility, trainer const, old name, new name, old title, new title
    ("TOWER", "TRAINER_ANABEL", "ANABEL", "CELESTE", "SALON MAIDEN", "SALON BELLE"),
    ("DOME", "TRAINER_TUCKER", "TUCKER", "BEAUREGARD", "DOME ACE", "ZYDECO ACE"),
    ("PALACE", "TRAINER_SPENSER", "SPENSER", "ARMAND", "PALACE MAVEN", "MARDI MAVEN"),
    ("ARENA", "TRAINER_GRETA", "GRETA", "MARGUERITE", "ARENA TYCOON", "KREWE QUEEN"),
    ("FACTORY", "TRAINER_NOLAND", "NOLAND", "ETIENNE", "FACTORY HEAD", "MILL FOREMAN"),
    ("PIKE", "TRAINER_LUCY", "LUCY", "LUCILLE", "PIKE QUEEN", "SWAMP QUEEN"),
    ("PYRAMID", "TRAINER_BRANDON", "BRANDON", "LAFITTE", "PYRAMID KING", "MOUND KING"),
]
CLASS = {"SALON MAIDEN": "SALON_MAIDEN", "DOME ACE": "DOME_ACE", "PALACE MAVEN": "PALACE_MAVEN", "ARENA TYCOON": "ARENA_TYCOON",
         "FACTORY HEAD": "FACTORY_HEAD", "PIKE QUEEN": "PIKE_QUEEN", "PYRAMID KING": "PYRAMID_KING"}

# gFrontierBrainInfo lines: (silver lost, gold lost, silver won, gold won); each "line1\nline2" (36 characters per line at most)
TEXTS = {
    "TOWER": ("Mon Dieu... well fought, cher.", "Merci, cher.\\nThe salon bows to you.", "Oh, cher... not tonight.\\nCome back when you've practiced.", "A lady never loses her poise.\\nOr her battle."),
    "DOME": ("Mais non!\\nThe crowd won't believe it!", "Ha ha! Now THAT'S a show,\\ncher!", "Hee hee! Aren't you embarrassed?\\nThe whole hall's watching!", "A ZYDECO ACE never misses a beat!"),
    "PALACE": ("Laissez les bons temps rouler...\\nyou earned this one.", "Well, I'll be.\\nYou danced right around me!", "Pas de probleme, cher.\\nTry again next Mardi Gras.", "That's how a MARDI MAVEN does it!"),
    "ARENA": ("Mais non!\\nY'all earned that one!", "Mais non!\\nYou beat the KREWE QUEEN?!", "Come on now, cher!\\nYou gotta hit harder than that!", "Heh heh!\\nThat's how we do in the Arena!"),
    "FACTORY": ("Well, I'll be.\\nYou out-built me.", "Mon ami, that's a fine machine\\nyou've got there!", "Back to the shop floor\\nfor you, cher.", "The mill never stops.\\nNeither do I!"),
    "PIKE": ("Hmph. The swamp doesn't give up\\nits own so easy.", "Well now...\\nthe bayou's got a new favorite.", "The bayou takes its toll,\\nchild.", "Nobody leaves my swamp\\nunless I say so."),
    "PYRAMID": ("Arr, ye took my mound,\\nmatey!", "The old mound bows to a\\nnew king!", "The mound holds its own.\\nCome back later.", "No treasure for ye today!"),
}

ARENA_TEXT = {
    "GretaYoureChallenger": 'MARGUERITE: Bonjour, cher!\\nWelcome to my Arena!\\p...Wait, are you the challenger?',
    "GretaYoureToughAfterAll": 'MARGUERITE: Mais non, wait a second!\\nYou are tough after all!\\pI like you, cher!\\nLet\'s see your FRONTIER PASS.',
    "GretaLookingForwardToSeeingAgain": ('MARGUERITE: Bonjour, cher!\\nYou finally made your way up to me!\\p'
                                         'The parade leader up in CRESCENT CITY\\nlearned every step of his dance from me.\\p'
                                         'He told me he gave you his\\nQUAQUAVALITE. Let\'s see if it was\\lwell spent!'),
    "GretaBlownAway": 'MARGUERITE: Mais non! Blown away!\\nLet\'s see your FRONTIER PASS!',
    "IfWeBattleAgainWontLose": 'Arrrgh!\\nThat\'s what I get for showin\' off!\\pIf we ever battle again, I won\'t lose!\\nDon\'t you forget it, cher!\\nLaissez les bons temps rouler!',
}


def dest(rel):
    d = OUT / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    if OUT != ROOT and not d.exists():
        shutil.copy(ROOT / rel, d)
    return d


def swap_strings(text):
    """upper-case names / titles inside .string lines and C string literals"""
    out = []
    for line in text.split("\n"):
        if ".string" in line or 'COMPOUND_STRING(' in line or '_("' in line or line.lstrip().startswith('"'):
            for _, _, on, nn, ot, nt in BRAINS:
                line = re.sub(r"\b" + ot + r"\b", nt, line)
                line = re.sub(r"\b" + on + r"\b", nn, line)
                line = re.sub(r"\b" + ot.title() + r"\b", nt.title(), line)
                line = re.sub(r"\b" + on.title() + r"\b", nn.title(), line)
        out.append(line)
    return "\n".join(out)


def main():
    # 1. trainer names
    p = dest("src/data/trainers.party")
    t = p.read_text(encoding="utf-8")
    for _, const, on, nn, ot, nt in BRAINS:
        t = re.sub(r"(=== " + const + r" ===\nName: )" + on, r"\g<1>" + nn, t)
    p.write_text(t, encoding="utf-8", newline="\n")
    # 2. class titles
    p = dest("src/battle_main.c")
    t = p.read_text(encoding="utf-8")
    for _, const, on, nn, ot, nt in BRAINS:
        t = t.replace('[TRAINER_CLASS_%s] = { _("%s")' % (CLASS[ot], ot), '[TRAINER_CLASS_%s] = { _("%s")' % (CLASS[ot], nt))
    p.write_text(t, encoding="utf-8", newline="\n")
    # 3. brain info lines
    p = dest("src/frontier_util.c")
    t = p.read_text(encoding="utf-8")
    for fac, const, on, nn, ot, nt in BRAINS:
        m = re.search(r"\[FRONTIER_FACILITY_" + fac + r"\] =\n    \{.*?\.trainerId = " + const + r",.*?\.battledBit", t, flags=re.S)
        if not m:
            continue
        blk = m.group(0)
        sl, gl, sw, gw = TEXTS[fac]
        q = lambda s: 'COMPOUND_STRING("' + s + '")'
        nl = chr(92) + "n"
        fix = lambda s: s.replace(chr(92) + chr(92) + "n", nl)
        sl, gl, sw, gw = (fix(x) for x in (sl, gl, sw, gw))
        repl = (".lostTexts = {\n            " + q(sl) + ", //Silver\n            " + q(gl) + "  //Gold\n        },\n        .wonTexts = {\n            " + q(sw) + ", //Silver\n            " + q(gw) + "  //Gold\n        },\n")
        new = re.sub(r"\.lostTexts = \{.*?\},\n        \.wonTexts = \{.*?\},\n", lambda m: repl, blk, flags=re.S)
        t = t.replace(blk, new)
    p.write_text(t, encoding="utf-8", newline="\n")
    # 4. map scripts
    for f in sorted((ROOT / "data/maps").glob("BattleFrontier_*/scripts.inc")):
        rel = f.relative_to(ROOT).as_posix()
        s = f.read_text(encoding="utf-8")
        n = swap_strings(s)
        if f.parent.name == "BattleFrontier_BattleArenaBattleRoom":
            for label, txt in ARENA_TEXT.items():
                lab = "BattleFrontier_BattleArenaBattleRoom_Text_" + label + ":\n"
                i = n.index(lab) + len(lab)
                j = n.find("\n\n", i)
                if j < 0:
                    j = len(n.rstrip("\n"))
                body = "\n".join('\t.string "' + seg + '"' for seg in _chunks(txt))
                n = n[:i] + body + n[j:]
        if n != s:
            d = dest(rel)
            d.write_text(n, encoding="utf-8", newline="\n")


def _chunks(txt):
    """split on the literal backslash-n / backslash-p / backslash-l sequences into .string lines (the last one ends with $)"""
    parts = re.split(r"(?<=" + re.escape(chr(92)) + r"[npl])", txt)
    lines = []
    for k, seg in enumerate(parts):
        lines.append(seg + ("$" if k == len(parts) - 1 else ""))
    return lines


if __name__ == "__main__":
    main()
