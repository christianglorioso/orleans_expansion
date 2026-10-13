"""Generate include/constants/achievements.h and src/data/achievements.h from achievements_data.py, and (only if it does not exist yet, or with
--rewards) the PLACEHOLDER reward table src/data/achievement_rewards.h, which is then edited by hand.

    python tools/achievements/gen_achievements.py [--rewards]
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from achievements_data import ROWS, CATEGORIES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WRAP = 38

# --- placeholder rewards: num -> dict(item, qty, item2, qty2, money, bp, sheet, note) ---
R = {}


def rw(nums, sheet, item=None, qty=1, item2=None, qty2=1, money=0, bp=0, note=""):
    for n in ([nums] if isinstance(nums, int) else nums):
        R[n] = dict(item=item, qty=qty, item2=item2, qty2=qty2, money=money, bp=bp, sheet=sheet, note=note)


COS = "COSMETIC, no system yet: placeholder item"
rw(1, "3 Great Balls", "ITEM_GREAT_BALL", 3)
rw(2, "5 Revives", "ITEM_REVIVE", 5)
rw(range(3, 11), "3 Heart Scales + PP Up", "ITEM_HEART_SCALE", 3, "ITEM_PP_UP", 1)
rw(range(11, 19), "5,000 money", money=5000)
rw(19, "Title: Charmed", "ITEM_RARE_CANDY", 1, note=COS + " (titles do not exist yet)")
rw(20, "Title: Guardian of the Bayou + 100 Battle Points", "ITEM_RARE_CANDY", 1, bp=100, note=COS + " for the title; the 100 BP are real")
rw([21, 22], "50 Battle Points", bp=50)
rw(23, "100 Battle Points", bp=100)
rw(24, "Mega Stone of your choice", "ITEM_RARE_CANDY", 3, note="needs a choice menu: placeholder item, replace with a fixed stone or an NPC claim")
rw([25, 26], "5,000 money", money=5000)
rw(27, "10,000 money", money=10000)
rw(28, "3 Super Potions", "ITEM_SUPER_POTION", 3)
rw(range(29, 36), "25 Battle Points", bp=25)
rw(36, "Title: Frontier Legend + 100 Battle Points", "ITEM_RARE_CANDY", 1, bp=100, note=COS + " for the title; the 100 BP are real")
rw(37, "Title: Master Naturalist + decoration set", "ITEM_RARE_CANDY", 2, note=COS)
rw(38, "Apartment decoration pack", "ITEM_NUGGET", 1, note=COS)
rw(range(39, 45), "Zoo plaque decoration", "ITEM_NUGGET", 1, note=COS)
rw(45, "Ability Capsule + 5 Heart Scales", "ITEM_ABILITY_CAPSULE", 1, "ITEM_HEART_SCALE", 5)
rw(46, "Aquarium tank decoration", "ITEM_NUGGET", 1, note=COS)
rw(47, "5 Ultra Balls", "ITEM_ULTRA_BALL", 5)
rw(48, "10 Ultra Balls", "ITEM_ULTRA_BALL", 10)
rw(49, "PP Max x3", "ITEM_PP_MAX", 3)
rw(50, "Fossil decoration", "ITEM_NUGGET", 1, note=COS)
rw(51, "5 Lucky Eggs", "ITEM_LUCKY_EGG", 1, note="sheet says 5 Lucky Eggs; the Oval Charm proposal competes (study 3.5)")
rw(52, "Boat look: Salvaged Skiff", "ITEM_GREAT_BALL", 3, note="boat looks are dead (no player boat): placeholder")
rw(53, "1,000 money", money=1000)
rw(54, "Boat look: Cypress Paint", "ITEM_GREAT_BALL", 3, note="boat look is dead: placeholder")
rw(55, "Boat look: Moss Garland", "ITEM_GREAT_BALL", 3, note="boat look is dead: placeholder")
rw(56, "Boat look: Heron Flag", "ITEM_GREAT_BALL", 3, note="boat look is dead: placeholder")
rw(57, "Boat look: Storm Sail", "ITEM_GREAT_BALL", 3, note="boat look is dead: placeholder")
rw(58, "Rare item from the island", "ITEM_RARE_CANDY", 1, note="islands do not exist yet")
rw(59, "Boat look: Island Pennant", "ITEM_ULTRA_BALL", 3, note="boat look is dead: placeholder")
rw(60, "Berry set", "ITEM_SITRUS_BERRY", 3, "ITEM_LUM_BERRY", 3, note="placeholder berries")
rw(61, "Title: Shrine Seeker", "ITEM_RARE_CANDY", 1, note=COS)
rw(62, "10,000 money", money=10000)
rw(63, "Postcard decoration", "ITEM_NUGGET", 1, note=COS)
rw(64, "A Pokeblock case", "ITEM_ULTRA_BALL", 3, note="the barista already gives the case: placeholder")
rw(65, "Salon ribbon decoration", "ITEM_NUGGET", 1, note=COS)
rw(66, "Name tag decoration", "ITEM_NUGGET", 1, note=COS)
rw(67, "3 TMs of your choice", "ITEM_ELIXIR", 3, note="needs a choice menu: placeholder item")
rw(68, "6 vitamins", "ITEM_HP_UP", 3, "ITEM_PROTEIN", 3, note="placeholder vitamins")
rw(69, "3 Bottle Caps", "ITEM_BOTTLE_CAP", 3)
rw(70, "Welcome mat decoration", "ITEM_NUGGET", 1, note=COS)
rw(71, "Decorator title", "ITEM_RARE_CANDY", 1, note=COS)
rw(72, "Appliance-themed decoration", "ITEM_NUGGET", 1, note=COS)
rw(73, "Title: Keeper of the Songs", "ITEM_RARE_CANDY", 1, note=COS)
rw(74, "Rootkin charm item", "ITEM_HEART_SCALE", 3, note="the item is undefined: placeholder")
rw(75, "Prism Scale", "ITEM_HEART_SCALE", 5, note="Prism Scale is sold in Dept2f: pick another reward")
rw(range(76, 97), "Title and trophy decoration", "ITEM_RARE_CANDY", 2, note=COS)
rw([97, 98], "5 Heart Scales + PP Up", "ITEM_HEART_SCALE", 5, "ITEM_PP_UP", 1)
rw(99, "Rotom-themed item", "ITEM_NUGGET", 1, note="the item is undefined: placeholder")
rw(100, "Floette-themed item", "ITEM_NUGGET", 1, note="the item is undefined: placeholder")


def cstr(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def wrap(s):
    return "\\n".join(textwrap.wrap(s, WRAP))


def gen_constants():
    out = ["#ifndef GUARD_CONSTANTS_ACHIEVEMENTS_H", "#define GUARD_CONSTANTS_ACHIEVEMENTS_H", "",
           "// GENERATED by tools/achievements/gen_achievements.py from tools/achievements/achievements_data.py. Do not edit by hand.",
           "// Ids are the sheet row minus one and NEVER change: the id is the bit position in the save. Plain #defines so scripts can use them",
           "// (setvar VAR_0x8004, ACH_X; special Achievement_UnlockVar8004).", "",
           "#define ACHIEVEMENTS_MAX 128",
           "#define ACHIEVEMENT_UNLOCKED_BYTES ((ACHIEVEMENTS_MAX + 7) / 8)",
           "#define ACHIEVEMENT_POPUP_QUEUE_SIZE 6", ""]
    for n, cat, key, *_ in ROWS:
        out.append("#define ACH_%s %d" % (key, n - 1))
    out += ["", "#define ACH_ID_COUNT %d" % len(ROWS), "", "",
            "enum AchievementId", "{", "    ACH_ID_NONE_ = 0xFF,", "};", "",
            "enum AchievementTier", "{", "    ACH_TIER_BRONZE,", "    ACH_TIER_SILVER,", "    ACH_TIER_GOLD,", "    ACH_TIER_PLATINUM,", "};", "",
            "enum AchievementCategory", "{"]
    out += ["    ACH_CAT_%s," % c.upper().replace(" ", "_") for c in CATEGORIES]
    out += ["    ACH_CAT_COUNT", "};", "",
            "enum AchievementTrigger", "{",
            "    ACH_TRIG_MANUAL,   // unlocked by Achievement_Unlock() from a hook or script",
            "    ACH_TRIG_SOON,     // feature not built yet: shown as coming soon, never unlocks",
            "    ACH_TRIG_FLAG,     // FlagGet(arg)",
            "    ACH_TRIG_VAR_GE,   // VarGet(arg) >= value",
            "    ACH_TRIG_DEX,      // species arg caught",
            "    ACH_TRIG_DEX_COUNT,// caught species count >= value",
            "    ACH_TRIG_STAT,     // GetGameStat(arg) >= value",
            "    ACH_TRIG_PRED,     // predicate()",
            "};", "", "#endif // GUARD_CONSTANTS_ACHIEVEMENTS_H", ""]
    (ROOT / "include/constants/achievements.h").write_text("\n".join(out), encoding="utf-8")


def gen_table():
    out = ["// GENERATED by tools/achievements/gen_achievements.py from tools/achievements/achievements_data.py. Do not edit by hand.",
           "// Included by src/achievements.c (after the predicates). The table order is the menu order (grouped by category).", "",
           "static const struct Achievement sAchievements[] =", "{"]
    for n, cat, key, name, how, trig, tier, status in ROWS:
        kind = trig[0]
        arg, val, pred = "0", "0", "NULL"
        if kind == "story":
            t, arg, val = "ACH_TRIG_VAR_GE", "VAR_ORLEANS_STORY", str(trig[1])
        elif kind == "flag":
            t, arg = "ACH_TRIG_FLAG", trig[1]
        elif kind == "varge":
            t, arg, val = "ACH_TRIG_VAR_GE", trig[1], str(trig[2])
        elif kind == "dex":
            t, arg = "ACH_TRIG_DEX", trig[1]
        elif kind == "dexcount":
            t, val = "ACH_TRIG_DEX_COUNT", str(trig[1])
        elif kind == "stat":
            t, arg, val = "ACH_TRIG_STAT", trig[1], str(trig[2])
        elif kind == "pred":
            t, pred = "ACH_TRIG_PRED", "Achievement_Predicate" + trig[1]
        elif kind == "manual":
            t = "ACH_TRIG_MANUAL"
        else:
            t = "ACH_TRIG_SOON"
        out.append("    {")
        out.append("        .id = ACH_%s, .category = ACH_CAT_%s, .tier = %s, .trigger = %s," % (
            key, cat.upper().replace(" ", "_"), ["ACH_TIER_BRONZE", "ACH_TIER_SILVER", "ACH_TIER_GOLD", "ACH_TIER_PLATINUM"][tier], t))
        out.append("        .arg = %s, .value = %s, .predicate = %s," % (arg, val, pred))
        out.append('        .name = COMPOUND_STRING("%s"),' % cstr(name))
        out.append('        .description = COMPOUND_STRING("%s"),' % wrap(how))
        out.append("    },")
    out += ["};", ""]
    (ROOT / "src/data/achievements.h").write_text("\n".join(out), encoding="utf-8")


def gen_rewards():
    out = ["// ACHIEVEMENT REWARDS (placeholders). HAND-EDITED: this file is the one place to review and change what each trophy gives.",
           "// Generated once by tools/achievements/gen_achievements.py --rewards; the generator never overwrites it unless asked.",
           "//",
           "// A reward is up to two item stacks plus money and Battle Points. It is given automatically when the unlock popup shows; if the bag is",
           "// full, it waits and Lafayette (Conservation Center) hands it over. An empty line {} means no reward.",
           "// Each row's comment shows what the sheet (orleans_achievements.xlsx) asked for. NOTE flags rewards that are placeholders because",
           "// the sheet's reward (title, decoration, boat look, a choice menu, an undefined item) has no system behind it yet.", "",
           "static const struct AchievementReward sAchievementRewards[ACHIEVEMENTS_MAX] =", "{"]
    for n, cat, key, name, *_ in ROWS:
        r = R[n]
        f = []
        if r["item"]:
            f += [".item = %s" % r["item"], ".qty = %d" % r["qty"]]
        if r["item2"]:
            f += [".item2 = %s" % r["item2"], ".qty2 = %d" % r["qty2"]]
        if r["money"]:
            f.append(".money = %d" % r["money"])
        if r["bp"]:
            f.append(".bp = %d" % r["bp"])
        out.append("    // #%d %s. Sheet: %s%s" % (n, name, r["sheet"], ("  NOTE: " + r["note"]) if r["note"] else ""))
        out.append("    [ACH_%s] = { %s }," % (key, ", ".join(f)))
    out += ["};", ""]
    (ROOT / "src/data/achievement_rewards.h").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    assert len(ROWS) == 100 and [r[0] for r in ROWS] == list(range(1, 101))
    gen_constants()
    gen_table()
    p = ROOT / "src/data/achievement_rewards.h"
    if "--rewards" in sys.argv or not p.exists():
        gen_rewards()
    print("ok")
