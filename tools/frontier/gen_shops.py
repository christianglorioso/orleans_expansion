"""Competitive held items for sale (user decision 2026-10-13): at the Battle Point clerks in the Frontier (a third clerk in the Arena lobby, same
Exchange-Corner UI) and at the Crescent City department store (floor 2, clerk 0, after the game is cleared, story 45+, at the engine's item prices).

usage: python tools/frontier/gen_shops.py [--root DIR]     (idempotent; DIR = an overlay tree, files are copied from the repo first)
The same item list feeds frontier_check's 'obtainable' view because the ids now appear in the map scripts.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else ROOT

# (item, menu name, Battle Points)
BP_ITEMS = [
    ("ITEM_HP_UP_EX", "HP UP EX", 10), ("ITEM_PROTEIN_EX", "PROTEIN EX", 10), ("ITEM_IRON_EX", "IRON EX", 10),
    ("ITEM_CALCIUM_EX", "CALCIUM EX", 10), ("ITEM_ZINC_EX", "ZINC EX", 10), ("ITEM_CARBOS_EX", "CARBOS EX", 10),
    ("ITEM_LIFE_ORB", "LIFE ORB", 96), ("ITEM_CHOICE_SPECS", "CHOICE SPECS", 96), ("ITEM_CHOICE_SCARF", "CHOICE SCARF", 96),
    ("ITEM_ASSAULT_VEST", "ASSAULT VEST", 80), ("ITEM_FOCUS_SASH", "FOCUS SASH", 64), ("ITEM_EXPERT_BELT", "EXPERT BELT", 64),
    ("ITEM_ROCKY_HELMET", "ROCKY HELMET", 64), ("ITEM_WEAKNESS_POLICY", "WEAKNESS POLICY", 64), ("ITEM_EVIOLITE", "EVIOLITE", 64),
    ("ITEM_SHELL_BELL", "SHELL BELL", 48), ("ITEM_BLACK_SLUDGE", "BLACK SLUDGE", 48), ("ITEM_LIGHT_CLAY", "LIGHT CLAY", 48),
    ("ITEM_FLAME_ORB", "FLAME ORB", 32), ("ITEM_TOXIC_ORB", "TOXIC ORB", 32), ("ITEM_MUSCLE_BAND", "MUSCLE BAND", 32),
    ("ITEM_WISE_GLASSES", "WISE GLASSES", 32), ("ITEM_AIR_BALLOON", "AIR BALLOON", 32), ("ITEM_HEAVY_DUTY_BOOTS", "HVY-DUTY BOOTS", 32),
    ("ITEM_SITRUS_BERRY", "SITRUS BERRY", 16), ("ITEM_SALAC_BERRY", "SALAC BERRY", 16), ("ITEM_LIECHI_BERRY", "LIECHI BERRY", 16),
    ("ITEM_PETAYA_BERRY", "PETAYA BERRY", 16), ("ITEM_LEPPA_BERRY", "LEPPA BERRY", 16),
    ("ITEM_SILK_SCARF", "SILK SCARF", 16), ("ITEM_BLACK_BELT", "BLACK BELT", 16), ("ITEM_SHARP_BEAK", "SHARP BEAK", 16), ("ITEM_POISON_BARB", "POISON BARB", 16),
    ("ITEM_SOFT_SAND", "SOFT SAND", 16), ("ITEM_HARD_STONE", "HARD STONE", 16), ("ITEM_SILVER_POWDER", "SILVER POWDER", 16), ("ITEM_SPELL_TAG", "SPELL TAG", 16),
    ("ITEM_METAL_COAT", "METAL COAT", 16), ("ITEM_CHARCOAL", "CHARCOAL", 16), ("ITEM_MYSTIC_WATER", "MYSTIC WATER", 16), ("ITEM_MIRACLE_SEED", "MIRACLE SEED", 16),
    ("ITEM_MAGNET", "MAGNET", 16), ("ITEM_TWISTED_SPOON", "TWISTED SPOON", 16), ("ITEM_NEVER_MELT_ICE", "NEVERMELTICE", 16), ("ITEM_DRAGON_FANG", "DRAGON FANG", 16),
    ("ITEM_BLACK_GLASSES", "BLACKGLASSES", 16), ("ITEM_FAIRY_FEATHER", "FAIRY FEATHER", 16),
]
RESIST_BERRIES = ["OCCA", "PASSHO", "WACAN", "RINDO", "YACHE", "CHOPLE", "KEBIA", "SHUCA", "COBA", "PAYAPA", "TANGA", "CHARTI", "KASIB", "HABAN", "COLBUR", "BABIRI", "ROSELI"]
# the department store (money): everything the clerks above sell plus the resist berries and the Light Ball
DEPT_ITEMS = [i for i, _, _ in BP_ITEMS if not i.endswith("_EX")] + ["ITEM_%s_BERRY" % b for b in RESIST_BERRIES] + ["ITEM_LIGHT_BALL"]


def dest(rel):
    d = OUT / rel
    d.parent.mkdir(parents=True, exist_ok=True)
    if OUT != ROOT and not d.exists():
        shutil.copy(ROOT / rel, d)
    return d


def sub1(t, a, b, what):
    if a not in t:
        raise SystemExit("gen_shops: anchor not found: " + what)
    return t.replace(a, b, 1)


def engine():
    n = len(BP_ITEMS)
    # --- enum
    p = dest("include/constants/field_specials.h")
    t = p.read_text(encoding="utf-8")
    t = t.replace("#define MAX_SCROLL_MULTI_LENGTH 16", "#define MAX_SCROLL_MULTI_LENGTH 64")   # the competitive-item clerk lists 48 rows
    if "COMPETITIVE_VENDOR" not in t:
        t = sub1(t, "    SCROLL_MULTI_BF_EXCHANGE_CORNER_HOLD_ITEM_VENDOR,\n", "    SCROLL_MULTI_BF_EXCHANGE_CORNER_HOLD_ITEM_VENDOR,\n    SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR,\n", "enum")
    p.write_text(t, encoding="utf-8", newline="\n")
    # --- exchange corner item list
    p = dest("src/data/battle_frontier/battle_frontier_exchange_corner.h")
    t = p.read_text(encoding="utf-8")
    if "sFrontierExchangeCorner_Competitive" not in t:
        lst = "static const enum Item sFrontierExchangeCorner_Competitive[] =\n{\n" + "".join("    %s,\n" % i for i, _, _ in BP_ITEMS) + "    ITEM_LIST_END\n};\n\n"
        t = sub1(t, "static const u8 *const sFrontierExchangeCorner_Decor1Descriptions[] =", lst + "static const u8 *const sFrontierExchangeCorner_Decor1Descriptions[] =", "exchange list")
    p.write_text(t, encoding="utf-8", newline="\n")
    # --- field_specials.c
    p = dest("src/field_specials.c")
    t = p.read_text(encoding="utf-8")
    if "COMPETITIVE_VENDOR" not in t:
        case = ("    case SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR:\n        task->tMaxItemsOnScreen = MAX_SCROLL_MULTI_ON_SCREEN;\n"
                "        task->tNumItems = %d;\n        task->tLeft = 14;\n        task->tTop = 1;\n        task->tWidth = 15;\n        task->tHeight = 12;\n"
                "        task->tKeepOpenAfterSelect = FALSE;\n        task->tTaskId = taskId;\n        break;\n" % (n + 1))
        t = sub1(t, "    case SCROLL_MULTI_BERRY_POWDER_VENDOR:\n        task->tMaxItemsOnScreen", case + "    case SCROLL_MULTI_BERRY_POWDER_VENDOR:\n        task->tMaxItemsOnScreen", "task case")
        opts = "    [SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR] =\n    {\n" + "".join(
            '        COMPOUND_STRING("%s{CLEAR_TO %d}%dBP"),\n' % (nm, 94 if bp >= 10 else 100, bp) for _, nm, bp in BP_ITEMS) + "        gText_Exit\n    },\n"
        t = sub1(t, "    [SCROLL_MULTI_BERRY_POWDER_VENDOR] =\n    {\n", opts + "    [SCROLL_MULTI_BERRY_POWDER_VENDOR] =\n    {\n", "options")
        t = sub1(t, "menu <= SCROLL_MULTI_BF_EXCHANGE_CORNER_HOLD_ITEM_VENDOR)", "menu <= SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR)", "range")
        fill = ("        case SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR:\n"
                "            AddTextPrinterParameterized2(0, FONT_NORMAL, sFrontierExchangeCorner_Competitive[selection] == ITEM_LIST_END ? gText_Exit : GetItemDescription(sFrontierExchangeCorner_Competitive[selection]), 0, NULL, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_WHITE, TEXT_COLOR_LIGHT_GRAY);\n"
                "            ShowFrontierExchangeCornerItemIcon(sFrontierExchangeCorner_Competitive[selection]);\n            break;\n")
        t = sub1(t, "        default:\n            break;\n        }\n    }\n}\n\nstatic void ShowFrontierExchangeCornerItemIcon", fill + "        default:\n            break;\n        }\n    }\n}\n\nstatic void ShowFrontierExchangeCornerItemIcon", "fill")
        t = sub1(t, "        case SCROLL_MULTI_BF_EXCHANGE_CORNER_HOLD_ITEM_VENDOR:\n            // This makes sure", "        case SCROLL_MULTI_BF_EXCHANGE_CORNER_HOLD_ITEM_VENDOR:\n        case SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR:\n            // This makes sure", "hide")
    p.write_text(t, encoding="utf-8", newline="\n")
    # --- scripts of the corner
    p = dest("data/maps/BattleFrontier_ExchangeServiceCorner/scripts.inc")
    t = p.read_text(encoding="utf-8")
    if "CompetitiveClerk" not in t:
        nl = "\n"
        s = ("BattleFrontier_ExchangeServiceCorner_EventScript_CompetitiveClerk::\n\tlock\n\tfaceplayer\n\tsetvar VAR_TEMP_2, EXCHANGE_CORNER_HOLD_ITEM_CLERK\n"
             "\tcall BattleFrontier_ExchangeServiceCorner_EventScript_ClerkWelcome\n\tgoto BattleFrontier_ExchangeServiceCorner_EventScript_ChooseCompetitive\n\tend\n\n"
             "BattleFrontier_ExchangeServiceCorner_EventScript_ChooseCompetitive::\n\tsetvar VAR_0x8004, SCROLL_MULTI_BF_EXCHANGE_CORNER_COMPETITIVE_VENDOR\n"
             "\tspecial ShowFrontierExchangeCornerItemIconWindow\n\tspecial ShowScrollableMultichoice\n\tspecial CloseFrontierExchangeCornerItemIconWindow\n\tswitch VAR_RESULT\n")
        s += "".join("\tcase %d, BattleFrontier_ExchangeServiceCorner_EventScript_Competitive%d\n" % (k, k) for k in range(n))
        s += ("\tcase %d, BattleFrontier_ExchangeServiceCorner_EventScript_ClerkGoodbye\n\tcase MULTI_B_PRESSED, BattleFrontier_ExchangeServiceCorner_EventScript_ClerkGoodbye\n\tend\n\n" % n)
        s += ("BattleFrontier_ExchangeServiceCorner_EventScript_PurchaseCompetitive::\n\tbufferitemname STR_VAR_1, VAR_0x8009\n"
              "\tmsgbox BattleFrontier_ExchangeServiceCorner_Text_ConfirmPurchase, MSGBOX_YESNO\n"
              "\tgoto_if_eq VAR_RESULT, NO, BattleFrontier_ExchangeServiceCorner_EventScript_ChooseCompetitive\n"
              "\tspecialvar VAR_TEMP_1, GetFrontierBattlePoints\n"
              "\tgoto_if_lt VAR_TEMP_1, VAR_0x8008, BattleFrontier_ExchangeServiceCorner_EventScript_CompetitiveTooPoor\n"
              "\tcheckitemspace VAR_0x8009\n\tgoto_if_eq VAR_RESULT, FALSE, BattleFrontier_ExchangeServiceCorner_EventScript_BagFull\n"
              "\tcopyvar VAR_0x8004, VAR_0x8008\n\tspecial TakeFrontierBattlePoints\n\tadditem VAR_0x8009\n\tspecial UpdateBattlePointsWindow\n\tplayse SE_SHOP\n"
              "\tmsgbox BattleFrontier_ExchangeServiceCorner_Text_HereIsYourPrize, MSGBOX_DEFAULT\n\tgoto BattleFrontier_ExchangeServiceCorner_EventScript_ChooseCompetitive\n\tend\n\n"
              "BattleFrontier_ExchangeServiceCorner_EventScript_CompetitiveTooPoor::\n\tmsgbox BattleFrontier_ExchangeServiceCorner_Text_DontHaveEnoughPoints, MSGBOX_DEFAULT\n"
              "\tgoto BattleFrontier_ExchangeServiceCorner_EventScript_ChooseCompetitive\n\tend\n\n")
        for k, (item, nm, bp) in enumerate(BP_ITEMS):
            s += "BattleFrontier_ExchangeServiceCorner_EventScript_Competitive%d::\n\tsetitemandprice %s, %d\n\tgoto BattleFrontier_ExchangeServiceCorner_EventScript_PurchaseCompetitive\n\n" % (k, item, bp)
        t = sub1(t, "BattleFrontier_ExchangeServiceCorner_EventScript_Man::\n", s + "BattleFrontier_ExchangeServiceCorner_EventScript_Man::\n", "corner scripts")
    p.write_text(t, encoding="utf-8", newline="\n")
    # --- Arena lobby: the third clerk
    p = dest("data/maps/BattleFrontier_BattleArenaLobby/map.json")
    raw = p.read_text(encoding="utf-8")
    if "CompetitiveClerk" not in raw:
        m = json.loads(raw)
        m["object_events"].append({"graphics_id": "OBJ_EVENT_GFX_TEALA", "x": 8, "y": 9, "elevation": 3, "movement_type": "MOVEMENT_TYPE_FACE_DOWN",
                                   "movement_range_x": 0, "movement_range_y": 0, "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0",
                                   "script": "BattleFrontier_ExchangeServiceCorner_EventScript_CompetitiveClerk", "flag": "0"})
        p.write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8", newline="\n")


def dept():
    add = "".join("\t.2byte %s\n" % i for i in DEPT_ITEMS)
    for rel in ("tools/mapgen/story/CrescentCity_Dept2f.inc", "data/maps/CrescentCity_Dept2f/scripts.inc"):
        p = dest(rel)
        t = p.read_text(encoding="utf-8")
        if "ITEM_LIFE_ORB" in t:
            continue
        i = t.index("CrescentCity_Dept2f_Pokemart_Clerk03:")
        j = t.index("\t.2byte ITEM_HEART_SCALE\n", i)
        t = t[:j] + add + t[j:]
        p.write_text(t, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    engine()
    dept()
    print("shops:", len(BP_ITEMS), "BP items,", len(DEPT_ITEMS), "department store items")
