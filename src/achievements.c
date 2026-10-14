#include "global.h"
#include "achievements.h"
#include "battle.h"
#include "battle_setup.h"
#include "event_data.h"
#include "item.h"
#include "lair_counters.h"
#include "money.h"
#include "pokemon.h"
#include "pokedex.h"
#include "string_util.h"
#include "overworld.h"
#include "constants/battle_frontier.h"
#include "constants/characters.h"
#include "constants/flags.h"
#include "constants/game_stat.h"
#include "constants/items.h"
#include "constants/map_groups.h"
#include "constants/opponents.h"
#include "constants/species.h"
#include "constants/vars.h"

// Achievement ("trophy") system, Orleans edition.
//
// Engine lifted from SoulGold (github.com/Eemeliri/soulgold) by Eemeliri: polled table + unlock bitset + popup queue. comfy_anim is by
// Montblanc via SoulGold. Orleans changes: SaveBlock3 storage with its own magic, a data-driven trigger per row (flag / var / dex / stat /
// predicate / manual), categories, per-trophy rewards (auto-given with a Lafayette fallback), map-visit bits.
//
// Triggers are re-evaluated by Achievement_CheckAll, so unlocking is retroactive: an old save, or a trophy added later, unlocks the next time
// a poll runs (once a second in the overworld, on map entry, on the Start menu, from scripts).

#define BATTLE_POINTS_CAP 9999
#define POLL_FRAMES 60
#define STREAK_TARGET 21

// visit bits (AchievementSaveData.visited)
enum
{
    VISIT_ROUTE1 = 0, // .. VISIT_ROUTE1 + 24 = Route 25
    VISIT_OLD_WATER = 25,
    VISIT_OLDEST_SHRINE = 26,
    VISIT_CRESCENT_FIRST = 27, // 17 buildings, 27..43
    VISIT_ISLAND_FIRST = 44,   // reserved for the optional islands (4)
    VISIT_DROWNED_TEMPLE = 48,
};

static const u16 sCrescentMaps[] =
{
    MAP_CRESCENT_CITY_CAFE, MAP_CRESCENT_CITY_CATHEDRAL, MAP_CRESCENT_CITY_CONSERVATION, MAP_CRESCENT_CITY_DAY_CARE,
    MAP_CRESCENT_CITY_DEPT1F, MAP_CRESCENT_CITY_GAME_CORNER, MAP_CRESCENT_CITY_GYM, MAP_CRESCENT_CITY_ICE_CREAM,
    MAP_CRESCENT_CITY_LAUNDRY, MAP_CRESCENT_CITY_NAME_RATER, MAP_CRESCENT_CITY_PELIPPER_POST, MAP_CRESCENT_CITY_POKECENTER_QUARTER,
    MAP_CRESCENT_CITY_POKECENTER_WATERFRONT, MAP_CRESCENT_CITY_RIVERBOAT_TERMINAL, MAP_CRESCENT_CITY_SALON, MAP_CRESCENT_CITY_TRADES,
    MAP_CRESCENT_CITY_TUTOR,
};

// the 20 legendary lairs (batch 1 and 2: tools/mapgen/story_data_lairs.py); AchievementSaveData.lairs holds a "discovered" bit per entry, set on first arrival
static const u16 sLairMaps[] =
{
    MAP_ROUTE14_ROUGAROU_HOLLOW, MAP_ROUTE23_BLOODMOON_ARROYO, MAP_POINTE_ROUGE_ICE_PLANT, MAP_ROUTE7_CELEBI_GLADE, MAP_ROUTE11_SUICUNE_ISLE,
    MAP_ROUTE2_RAIKOU_CLEARING, MAP_ROUTE16_ENTEI_FIELD,
    MAP_OLD_WATER_KNOWING_POOL, MAP_ROUTE1_HEART_POOL, MAP_ROUTE23_UNFAILING_SPRING, MAP_STORMS_EDGE_LIGHTHOUSE_GALLERY, MAP_ROUTE12_LEVEE_CROWN,
    MAP_ROUTE13_DEEP_WOOD, MAP_ROUTE13_COURIR_GLADE, MAP_ROUTE3_WINDS_EYE, MAP_ROUTE14_SPANISH_FORT, MAP_ROUTE14_BUSH_TRACK, MAP_ROUTE10_MILNEBURG_PAVILION,
    MAP_ROUTE17_SUGARHOUSE, MAP_ROUTE23_BOUNTIFUL_FIELD,
};
enum { LAIR_CELEBI = 3, LAIR_KNOWING_POOL = 7, LAIR_HEART_POOL = 8, LAIR_UNFAILING_SPRING = 9 };

static const u16 sRouteMaps[] =
{
    MAP_ORLEANS_ROUTE1, MAP_ORLEANS_ROUTE2, MAP_ORLEANS_ROUTE3, MAP_ORLEANS_ROUTE4, MAP_ORLEANS_ROUTE5, MAP_ORLEANS_ROUTE6, MAP_ORLEANS_ROUTE7, MAP_ORLEANS_ROUTE8, MAP_ORLEANS_ROUTE9, MAP_ORLEANS_ROUTE10,
    MAP_ORLEANS_ROUTE11, MAP_ORLEANS_ROUTE12, MAP_ORLEANS_ROUTE13, MAP_ORLEANS_ROUTE14, MAP_ORLEANS_ROUTE15, MAP_ORLEANS_ROUTE16, MAP_ORLEANS_ROUTE17, MAP_ORLEANS_ROUTE18, MAP_ORLEANS_ROUTE19, MAP_ORLEANS_ROUTE20,
    MAP_ORLEANS_ROUTE21, MAP_ORLEANS_ROUTE22, MAP_ORLEANS_ROUTE23, MAP_ORLEANS_ROUTE24, MAP_ORLEANS_ROUTE25,
};

static const u16 sSailorTrainers[] =
{
    TRAINER_ORLEANS_ROUTE3_SAILOR, TRAINER_ORLEANS_ROUTE4_SAILOR, TRAINER_ORLEANS_ROUTE6_SAILOR, TRAINER_ORLEANS_ROUTE9_SAILOR,
    TRAINER_ORLEANS_ROUTE19_SAILOR, TRAINER_ORLEANS_ROUTE20_SAILOR,
};

static const u8 *const sCategoryNames[ACH_CAT_COUNT] =
{
    [ACH_CAT_STORY] = COMPOUND_STRING("Story"),
    [ACH_CAT_BATTLE] = COMPOUND_STRING("Battle"),
    [ACH_CAT_BATTLE_FRONTIER] = COMPOUND_STRING("Battle Frontier"),
    [ACH_CAT_CONSERVATION] = COMPOUND_STRING("Conservation"),
    [ACH_CAT_EXPLORATION] = COMPOUND_STRING("Exploration"),
    [ACH_CAT_CRAFT_AND_CULTURE] = COMPOUND_STRING("Craft and culture"),
    [ACH_CAT_COLLECTION] = COMPOUND_STRING("Collection"),
};

static const u16 sTierBallItems[] =
{
    [ACH_TIER_BRONZE] = ITEM_POKE_BALL,
    [ACH_TIER_SILVER] = ITEM_GREAT_BALL,
    [ACH_TIER_GOLD] = ITEM_ULTRA_BALL,
    [ACH_TIER_PLATINUM] = ITEM_MASTER_BALL,
};

static struct AchievementSaveData *Ach(void)
{
    return &gSaveBlock3Ptr->achievements;
}

void Achievement_Reset(void)
{
    memset(Ach(), 0, sizeof(*Ach()));
    Ach()->magic = ACHIEVEMENT_SAVE_MAGIC;
}

static void EnsureInitialized(void)
{
    if (Ach()->magic != ACHIEVEMENT_SAVE_MAGIC)
        Achievement_Reset();
}

// ---- visit bits ----
static bool32 Visited(u32 bit)
{
    return (Ach()->visited[bit / 8] >> (bit % 8)) & 1;
}

static void SetVisited(u32 bit)
{
    Ach()->visited[bit / 8] |= 1 << (bit % 8);
}

static u32 CurrentMapId(void)
{
    return (gSaveBlock1Ptr->location.mapGroup << 8) | gSaveBlock1Ptr->location.mapNum;
}

void Achievement_OnMapEntered(void)
{
    u32 i, map = CurrentMapId();

    EnsureInitialized();
    for (i = 0; i < ARRAY_COUNT(sRouteMaps); i++)
        if (sRouteMaps[i] == map)
            SetVisited(VISIT_ROUTE1 + i);
    for (i = 0; i < ARRAY_COUNT(sCrescentMaps); i++)
        if (sCrescentMaps[i] == map)
            SetVisited(VISIT_CRESCENT_FIRST + i);
    for (i = 0; i < ARRAY_COUNT(sLairMaps); i++)
        if (sLairMaps[i] == map)
            Ach()->lairs[i / 8] |= 1 << (i % 8);
    if (map == MAP_LANDS_END_DROWNED_TEMPLE)
        SetVisited(VISIT_DROWNED_TEMPLE);
    if (map == MAP_OLD_WATER)
        SetVisited(VISIT_OLD_WATER);
    else if (map == MAP_OLDEST_SHRINE)
        SetVisited(VISIT_OLDEST_SHRINE);
    Achievement_CheckAll();
}

// ---- predicates ----
static bool32 CaughtSpecies(enum Species species)
{
    return GetSetPokedexFlag(SpeciesToNationalPokedexNum(species), FLAG_GET_CAUGHT);
}

static bool32 AnyTrainerFought(const u16 *ids, u32 count)
{
    u32 i;

    for (i = 0; i < count; i++)
        if (HasTrainerBeenFought(ids[i]))
            return TRUE;
    return FALSE;
}

static bool32 Achievement_PredicateCamilleDefeated(void)
{
    return HasTrainerBeenFought(TRAINER_ORLEANS_CAMILLE) || HasTrainerBeenFought(TRAINER_ORLEANS_CAMILLE_SHRINE);
}

static bool32 Achievement_PredicateAndrewDefeated(void)
{
    return HasTrainerBeenFought(TRAINER_ORLEANS_ANDREW) || VarGet(VAR_ORLEANS_STORY) >= 43;
}

static bool32 Achievement_PredicateSailorDefeated(void)
{
    return AnyTrainerFought(sSailorTrainers, ARRAY_COUNT(sSailorTrainers));
}

static bool32 AnyStreak(const u16 *streaks, u32 count)
{
    u32 i;

    for (i = 0; i < count; i++)
        if (streaks[i] >= STREAK_TARGET)
            return TRUE;
    return FALSE;
}

#define STREAK_PREDICATE(name, field) \
static bool32 Achievement_Predicate##name(void) \
{ \
    return AnyStreak((const u16 *)gSaveBlock2Ptr->frontier.field, sizeof(gSaveBlock2Ptr->frontier.field) / sizeof(u16)); \
}

STREAK_PREDICATE(TowerStreak, towerRecordWinStreaks)
STREAK_PREDICATE(DomeStreak, domeRecordWinStreaks)
STREAK_PREDICATE(PalaceStreak, palaceRecordWinStreaks)
STREAK_PREDICATE(ArenaStreak, arenaRecordStreaks)
STREAK_PREDICATE(FactoryStreak, factoryRecordWinStreaks)
STREAK_PREDICATE(PikeStreak, pikeRecordStreaks)
STREAK_PREDICATE(PyramidStreak, pyramidRecordStreaks)

static bool32 Achievement_PredicateAllFrontierStreaks(void)
{
    return Achievement_PredicateTowerStreak() && Achievement_PredicateDomeStreak() && Achievement_PredicatePalaceStreak()
        && Achievement_PredicateArenaStreak() && Achievement_PredicateFactoryStreak() && Achievement_PredicatePikeStreak()
        && Achievement_PredicatePyramidStreak();
}

// Same rule as OrleansDex_CheckBaseComplete (src/orleans_dex.c), but without touching the script result vars: the polls can run mid-script.
static bool32 Achievement_PredicateBaseDexComplete(void)
{
    u32 i;

    for (i = 1; i < REGIONAL_DEX_COUNT; i++)
    {
        enum NationalDexOrder nat = RegionalToNationalOrder(i);
        enum Species species = NationalPokedexNumToSpecies(nat);

        if (species == SPECIES_NONE || gSpeciesInfo[species].isMegaEvolution)
            continue;
        if (GET_BASE_SPECIES_ID(species) != species)
            continue;
        if (gSpeciesInfo[species].isMythical && !gSpeciesInfo[species].dexForceRequired)
            continue;
        if (!GetSetPokedexFlag(nat, FLAG_GET_CAUGHT))
            return FALSE;
    }
    return TRUE;
}

static bool32 Achievement_PredicateAllApplianceRotoms(void)
{
    return CaughtSpecies(SPECIES_ROTOM_HEAT) && CaughtSpecies(SPECIES_ROTOM_WASH) && CaughtSpecies(SPECIES_ROTOM_FROST)
        && CaughtSpecies(SPECIES_ROTOM_FAN) && CaughtSpecies(SPECIES_ROTOM_MOW);
}

static bool32 LairDiscovered(u32 lair)
{
    return (Ach()->lairs[lair / 8] >> (lair % 8)) & 1;
}

// the six Rootkin shrines: the lake trio's three pools (Uxie, Mesprit, Azelf), Celebi's glade, the Old Water and the Oldest Shrine
static bool32 Achievement_PredicateShrinesVisited(void)
{
    return LairDiscovered(LAIR_KNOWING_POOL) && LairDiscovered(LAIR_HEART_POOL) && LairDiscovered(LAIR_UNFAILING_SPRING) && LairDiscovered(LAIR_CELEBI)
        && Visited(VISIT_OLD_WATER) && Visited(VISIT_OLDEST_SHRINE);
}

static bool32 Achievement_PredicateTempleVisited(void)
{
    return Visited(VISIT_DROWNED_TEMPLE);
}

static bool32 Achievement_PredicateRoutesVisited(void)
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sRouteMaps); i++)
        if (!Visited(VISIT_ROUTE1 + i))
            return FALSE;
    return TRUE;
}

static bool32 Achievement_PredicateCrescentVisited(void)
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sCrescentMaps); i++)
        if (!Visited(VISIT_CRESCENT_FIRST + i))
            return FALSE;
    return TRUE;
}

// ---- lair unlocks: capture sets, Ogerpon's masks ----
#include "data/lair_capture_sets.h"

static const struct
{
    const u16 *species;
    u16 count;
} sLairSets[] =
{
    [LAIR_SET_WATER] = { sLairSet_WATER, ARRAY_COUNT(sLairSet_WATER) },
    [LAIR_SET_FIRE] = { sLairSet_FIRE, ARRAY_COUNT(sLairSet_FIRE) },
    [LAIR_SET_ELECTRIC] = { sLairSet_ELECTRIC, ARRAY_COUNT(sLairSet_ELECTRIC) },
    [LAIR_SET_FIGHTING_FLYING] = { sLairSet_FIGHTING_FLYING, ARRAY_COUNT(sLairSet_FIGHTING_FLYING) },
    [LAIR_SET_PSYCHIC_FLYING] = { sLairSet_PSYCHIC_FLYING, ARRAY_COUNT(sLairSet_PSYCHIC_FLYING) },
    [LAIR_SET_DARK_FLYING] = { sLairSet_DARK_FLYING, ARRAY_COUNT(sLairSet_DARK_FLYING) },
    [LAIR_SET_GRASS_DARK] = { sLairSet_GRASS_DARK, ARRAY_COUNT(sLairSet_GRASS_DARK) },
    [LAIR_SET_LEGENDS] = { sLairSet_LEGENDS, ARRAY_COUNT(sLairSet_LEGENDS) },
};

static u32 SetCaughtCount(u32 set)
{
    u32 i, n = 0;

    if (set >= ARRAY_COUNT(sLairSets))
        return 0;
    for (i = 0; i < sLairSets[set].count; i++)
        if (CaughtSpecies(sLairSets[set].species[i]))
            n++;
    return n;
}

// the poll's check: stops at the first missing species (most sets are incomplete, so this is a handful of dex lookups instead of the whole set every second)
static bool32 SetAllCaught(u32 set)
{
    u32 i;

    if (set >= ARRAY_COUNT(sLairSets))
        return FALSE;
    for (i = 0; i < sLairSets[set].count; i++)
        if (!CaughtSpecies(sLairSets[set].species[i]))
            return FALSE;
    return TRUE;
}

static u32 SetSize(u32 set)
{
    return set < ARRAY_COUNT(sLairSets) ? sLairSets[set].count : 0;
}

// Ogerpon's three mask items. The post-game balls are hidden by their FLAG_PG_* flag until story 45 and flagged again when picked up, so from 45 on the flag means "collected"
// (the bag is checked too, for a mask that was found some other way).
static bool32 HasMask(enum Item item, u16 flag)
{
    if (VarGet(VAR_ORLEANS_STORY) < 45) // the masks are post-game balls: nothing to scan for before the game is beaten
        return FALSE;
    return FlagGet(flag) || CheckBagHasItem(item, 1);
}

static u32 MaskCount(void)
{
    return HasMask(ITEM_WELLSPRING_MASK, FLAG_PG_WELLSPRING_MASK) + HasMask(ITEM_HEARTHFLAME_MASK, FLAG_PG_HEARTHFLAME_MASK)
         + HasMask(ITEM_CORNERSTONE_MASK, FLAG_PG_CORNERSTONE_MASK);
}

#include "data/achievements.h"
#include "data/achievement_rewards.h"

// ---- table access ----
u16 Achievement_GetCount(void)
{
    return ARRAY_COUNT(sAchievements);
}

const struct Achievement *Achievement_GetByIndex(u16 index)
{
    return index < ARRAY_COUNT(sAchievements) ? &sAchievements[index] : NULL;
}

const struct Achievement *Achievement_GetById(enum AchievementId id)
{
    u16 i;

    for (i = 0; i < ARRAY_COUNT(sAchievements); i++)
        if (sAchievements[i].id == id)
            return &sAchievements[i];
    return NULL;
}

const u8 *Achievement_GetCategoryName(enum AchievementCategory category)
{
    return category < ACH_CAT_COUNT ? sCategoryNames[category] : sCategoryNames[0];
}

u16 Achievement_GetTierBallItem(enum AchievementTier tier)
{
    return tier < ARRAY_COUNT(sTierBallItems) ? sTierBallItems[tier] : sTierBallItems[0];
}

bool32 Achievement_IsComingSoon(const struct Achievement *achievement)
{
    return achievement->trigger == ACH_TRIG_SOON;
}

// ---- state ----
bool32 Achievement_IsUnlocked(enum AchievementId id)
{
    if ((u32)id >= ACHIEVEMENTS_MAX)
        return FALSE;
    EnsureInitialized();
    return (Ach()->unlocked[id / 8] >> (id % 8)) & 1;
}

bool32 Achievement_IsRewardPending(enum AchievementId id)
{
    if ((u32)id >= ACHIEVEMENTS_MAX)
        return FALSE;
    EnsureInitialized();
    return (Ach()->rewardPending[id / 8] >> (id % 8)) & 1;
}

u16 Achievement_CountUnlocked(void)
{
    u16 i, count = 0;

    for (i = 0; i < ARRAY_COUNT(sAchievements); i++)
        if (Achievement_IsUnlocked(sAchievements[i].id))
            count++;
    return count;
}

// cached caught count for one CheckAll pass (the dex loop is the only expensive trigger)
static u16 sDexCountCache;
static bool8 sDexCountValid;

static u32 GetCaughtCount(void)
{
    if (!sDexCountValid)
    {
        sDexCountCache = GetNationalPokedexCount(FLAG_GET_CAUGHT);
        sDexCountValid = TRUE;
    }
    return sDexCountCache;
}

static bool32 Evaluate(const struct Achievement *a)
{
    switch (a->trigger)
    {
    case ACH_TRIG_FLAG:
        return FlagGet(a->arg);
    case ACH_TRIG_VAR_GE:
        return VarGet(a->arg) >= a->value;
    case ACH_TRIG_DEX:
        return CaughtSpecies(a->arg);
    case ACH_TRIG_DEX_COUNT:
        return GetCaughtCount() >= a->value;
    case ACH_TRIG_STAT:
        return GetGameStat(a->arg) >= a->value;
    case ACH_TRIG_PRED:
        return a->predicate != NULL && a->predicate();
    case ACH_TRIG_SET:
        return SetAllCaught(a->arg);
    case ACH_TRIG_COUNTER:
        return LairCounter_Get(a->arg) >= a->value;
    case ACH_TRIG_MASKS:
        return MaskCount() == 3;
    default:
        return FALSE;
    }
}

u32 Achievement_GetProgress(const struct Achievement *a)
{
    if (a == NULL)
        return 0;
    if (a->trigger == ACH_TRIG_DEX_COUNT)
        return GetCaughtCount();
    if (a->trigger == ACH_TRIG_STAT)
        return GetGameStat(a->arg);
    if (a->trigger == ACH_TRIG_SET)
        return SetCaughtCount(a->arg);
    if (a->trigger == ACH_TRIG_COUNTER)
        return LairCounter_Get(a->arg);
    if (a->trigger == ACH_TRIG_MASKS)
        return MaskCount();
    return Achievement_IsUnlocked(a->id) ? 1 : 0;
}

u32 Achievement_GetTarget(const struct Achievement *a)
{
    if (a == NULL)
        return 0;
    if (a->trigger == ACH_TRIG_DEX_COUNT || a->trigger == ACH_TRIG_STAT || a->trigger == ACH_TRIG_COUNTER)
        return a->value;
    if (a->trigger == ACH_TRIG_SET)
        return SetSize(a->arg);
    if (a->trigger == ACH_TRIG_MASKS)
        return 3;
    return 1;
}

static void QueuePopup(enum AchievementId id)
{
    u8 i;

    for (i = 0; i < ACHIEVEMENT_POPUP_QUEUE_SIZE; i++)
    {
        if (Ach()->popupQueue[i] == 0)
        {
            Ach()->popupQueue[i] = id + 1;
            return;
        }
    }
    // queue full: no popup, the reward stays pending for Lafayette
}

bool32 Achievement_Unlock(enum AchievementId id)
{
    if ((u32)id >= ACHIEVEMENTS_MAX || Achievement_GetById(id) == NULL || Achievement_IsUnlocked(id))
        return FALSE;

    Ach()->unlocked[id / 8] |= 1 << (id % 8);
    Ach()->rewardPending[id / 8] |= 1 << (id % 8);
    QueuePopup(id);
    return TRUE;
}

void Achievement_CheckAll(void)
{
    u16 i;

    EnsureInitialized();
    sDexCountValid = FALSE;
    for (i = 0; i < ARRAY_COUNT(sAchievements); i++)
    {
        const struct Achievement *a = &sAchievements[i];

        if (!Achievement_IsUnlocked(a->id) && Evaluate(a))
            Achievement_Unlock(a->id);
    }
}

// called each frame from the popup file; runs the poll once a second
void Achievement_Poll(void)
{
    static u16 sTimer;

    if (++sTimer >= POLL_FRAMES)
    {
        sTimer = 0;
        Achievement_CheckAll();
    }
}

// ---- rewards ----
static bool32 RewardIsEmpty(const struct AchievementReward *r)
{
    return r->item == ITEM_NONE && r->item2 == ITEM_NONE && r->money == 0 && r->bp == 0;
}

u8 *Achievement_BuildRewardText(enum AchievementId id, u8 *dst)
{
    const struct AchievementReward *r = &sAchievementRewards[id];
    bool32 first = TRUE;

    dst[0] = EOS;
    if ((u32)id >= ACHIEVEMENTS_MAX)
        return dst;
    if (r->item != ITEM_NONE)
    {
        dst = ConvertIntToDecimalStringN(dst, r->qty, STR_CONV_MODE_LEFT_ALIGN, 3);
        *dst++ = CHAR_SPACE;
        dst = CopyItemNameHandlePlural(r->item, dst, r->qty);
        first = FALSE;
    }
    if (r->item2 != ITEM_NONE)
    {
        if (!first)
            dst = StringCopy(dst, COMPOUND_STRING(", "));
        dst = ConvertIntToDecimalStringN(dst, r->qty2, STR_CONV_MODE_LEFT_ALIGN, 3);
        *dst++ = CHAR_SPACE;
        dst = CopyItemNameHandlePlural(r->item2, dst, r->qty2);
        first = FALSE;
    }
    if (r->money != 0)
    {
        if (!first)
            dst = StringCopy(dst, COMPOUND_STRING(", "));
        *dst++ = CHAR_CURRENCY;
        dst = ConvertIntToDecimalStringN(dst, r->money, STR_CONV_MODE_LEFT_ALIGN, 5);
        first = FALSE;
    }
    if (r->bp != 0)
    {
        if (!first)
            dst = StringCopy(dst, COMPOUND_STRING(", "));
        dst = ConvertIntToDecimalStringN(dst, r->bp, STR_CONV_MODE_LEFT_ALIGN, 4);
        dst = StringCopy(dst, COMPOUND_STRING(" BP"));
    }
    *dst = EOS;
    return dst;
}

bool32 Achievement_GiveReward(enum AchievementId id)
{
    const struct AchievementReward *r;

    if ((u32)id >= ACHIEVEMENTS_MAX)
        return TRUE;
    r = &sAchievementRewards[id];
    if (!Achievement_IsRewardPending(id))
        return TRUE;
    if (!RewardIsEmpty(r))
    {
        if (r->item != ITEM_NONE && !CheckBagHasSpace(r->item, r->qty))
            return FALSE;
        if (r->item2 != ITEM_NONE && !CheckBagHasSpace(r->item2, r->qty2))
            return FALSE;
        if (r->item != ITEM_NONE && !AddBagItem(r->item, r->qty))
            return FALSE;
        if (r->item2 != ITEM_NONE && !AddBagItem(r->item2, r->qty2))
        {
            if (r->item != ITEM_NONE)
                RemoveBagItem(r->item, r->qty);
            return FALSE;
        }
        if (r->money != 0)
            AddMoney(&gSaveBlock1Ptr->money, r->money);
        if (r->bp != 0)
        {
            u32 total = gSaveBlock2Ptr->frontier.battlePoints + r->bp;

            gSaveBlock2Ptr->frontier.battlePoints = total > BATTLE_POINTS_CAP ? BATTLE_POINTS_CAP : total;
        }
    }
    Ach()->rewardPending[id / 8] &= ~(1 << (id % 8));
    return TRUE;
}

// ---- hooks ----
void Achievement_OnTrainerBattleWon(u16 trainerId)
{
    u32 i;

    if (trainerId == TRAINER_ORLEANS_RAYQUAZA_RAID)
    {
        bool32 anyFainted = FALSE;

        for (i = 0; i < PARTY_SIZE; i++)
            if (GetMonData(&gParties[B_TRAINER_PLAYER][i], MON_DATA_SPECIES) != SPECIES_NONE && GetMonData(&gParties[B_TRAINER_PLAYER][i], MON_DATA_HP) == 0)
                anyFainted = TRUE;
        if (!anyFainted)
            Achievement_Unlock(ACH_UNBROKEN);
    }
    Achievement_CheckAll();
}

void Achievement_OnMegaEvolved(void)
{
    Achievement_Unlock(ACH_BOND_BEYOND_LIMITS);
}

// ---- specials ----
void Achievement_UnlockVar8004(void)
{
    Achievement_Unlock(gSpecialVar_0x8004);
}

void Achievement_CheckAllSpecial(void)
{
    Achievement_CheckAll();
}

// Lair gates (map scripts): VAR_0x8004 = trophy id; re-polls so a trophy earned elsewhere counts, VAR_RESULT = TRUE when it is unlocked
void Achievement_CheckUnlockedVar8004(void)
{
    Achievement_CheckAll();
    gSpecialVar_Result = Achievement_IsUnlocked(gSpecialVar_0x8004);
}

// The post-game arenas: VAR_0x8004 = species, VAR_RESULT = registered CAUGHT in the Pokedex (Rayquaza's catch opens Kyogre's and Groudon's arenas)
void Achievement_SpeciesCaughtVar8004(void)
{
    gSpecialVar_Result = CaughtSpecies(gSpecialVar_0x8004);
}

void Achievement_GetCountSpecial(void)
{
    Achievement_CheckAll();
    gSpecialVar_Result = Achievement_CountUnlocked();
}

// Lafayette: hand over the next waiting reward. gSpecialVar_Result: 0 nothing waiting, 1 given (gStringVar4 = the line to show), 2 bag full.
void Achievement_ClaimNextReward(void)
{
    u16 i;

    EnsureInitialized();
    gSpecialVar_Result = 0;
    for (i = 0; i < ARRAY_COUNT(sAchievements); i++)
    {
        const struct Achievement *a = &sAchievements[i];

        if (!Achievement_IsUnlocked(a->id) || !Achievement_IsRewardPending(a->id))
            continue;
        if (!Achievement_GiveReward(a->id))
        {
            gSpecialVar_Result = 2;
            return;
        }
        StringCopy(gStringVar1, a->name);
        Achievement_BuildRewardText(a->id, gStringVar2);
        StringExpandPlaceholders(gStringVar4, COMPOUND_STRING("For the trophy {STR_VAR_1}:\n{STR_VAR_2}!"));
        gSpecialVar_Result = 1;
        return;
    }
}
