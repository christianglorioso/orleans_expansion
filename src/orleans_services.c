// Orleans: Crescent City's Pokemon services (the EV changer, the IV changer and the friendship salon).
// Called from scripts with `special`; VAR_0x8004 = party slot, VAR_0x8005 = stat (0 HP, 1 Atk, 2 Def, 3 SpA, 4 SpD, 5 Spe),
// VAR_0x8006 = mode. The answer is in VAR_RESULT. Costs and menus live in the scripts (tools/mapgen/story/CrescentCity_*.inc).
#include "global.h"
#include "pokemon.h"
#include "event_data.h"
#include "overworld.h"
#include "constants/pokemon.h"
#include "constants/game_stat.h"
#include "constants/vars.h"

static const u8 sEvData[6] = {MON_DATA_HP_EV, MON_DATA_ATK_EV, MON_DATA_DEF_EV, MON_DATA_SPATK_EV, MON_DATA_SPDEF_EV, MON_DATA_SPEED_EV};
static const u8 sIvData[6] = {MON_DATA_HP_IV, MON_DATA_ATK_IV, MON_DATA_DEF_IV, MON_DATA_SPATK_IV, MON_DATA_SPDEF_IV, MON_DATA_SPEED_IV};

// mode 0: clear the stat's EVs; mode 1: add 10 (up to the per-stat and total caps). VAR_RESULT: 1 if the EVs changed
void OrleansSvc_ChangeEv(void)
{
    struct Pokemon *mon = &gPlayerParty[gSpecialVar_0x8004];
    u16 stat = gSpecialVar_0x8005;
    u32 i, total = 0;
    u32 cur, next;

    gSpecialVar_Result = 0;
    if (gSpecialVar_0x8004 >= PARTY_SIZE || stat > 5)
        return;
    for (i = 0; i < 6; i++)
        total += GetMonData(mon, sEvData[i]);
    cur = GetMonData(mon, sEvData[stat]);
    if (gSpecialVar_0x8006 == 0)
    {
        if (cur == 0)
            return;
        next = 0;
    }
    else
    {
        next = cur + 10;
        if (next > MAX_PER_STAT_EVS)
            next = MAX_PER_STAT_EVS;
        if (total - cur + next > MAX_TOTAL_EVS)
            next = MAX_TOTAL_EVS - (total - cur);
        if (next <= cur)
            return;
    }
    SetMonData(mon, sEvData[stat], &next);
    CalculateMonStats(mon);
    gSpecialVar_Result = 1;
}

// Sets the stat's IV to 31. VAR_RESULT: 1 if it changed, 0 if it already was 31
void OrleansSvc_MaxIv(void)
{
    struct Pokemon *mon = &gPlayerParty[gSpecialVar_0x8004];
    u16 stat = gSpecialVar_0x8005;
    u32 iv = MAX_PER_STAT_IVS;

    gSpecialVar_Result = 0;
    if (gSpecialVar_0x8004 >= PARTY_SIZE || stat > 5 || GetMonData(mon, sIvData[stat]) >= MAX_PER_STAT_IVS)
        return;
    SetMonData(mon, sIvData[stat], &iv);
    CalculateMonStats(mon);
    gSpecialVar_Result = 1;
}

// Friendship to 255. VAR_RESULT: 1 if it changed, 0 if it already was 255 (or the slot is empty / an Egg)
void OrleansSvc_MaxFriendship(void)
{
    struct Pokemon *mon = &gPlayerParty[gSpecialVar_0x8004];
    u32 friendship = 255;

    gSpecialVar_Result = 0;
    if (gSpecialVar_0x8004 >= PARTY_SIZE || GetMonData(mon, MON_DATA_SPECIES_OR_EGG) == SPECIES_EGG
        || GetMonData(mon, MON_DATA_FRIENDSHIP) >= 255)
        return;
    SetMonData(mon, MON_DATA_FRIENDSHIP, &friendship);
    gSpecialVar_Result = 1;
}

// The Route 5 fishing tournament: the score is the number of fishing bites (GAME_STAT_FISHING_ENCOUNTERS, +1 per bite).
// SetFishingBaseline stores the counter at entry in VAR_TOURNEY_BASELINE; FishingBites returns the bites since in VAR_RESULT.
void OrleansSvc_SetFishingBaseline(void)
{
    VarSet(VAR_TOURNEY_BASELINE, (u16)GetGameStat(GAME_STAT_FISHING_ENCOUNTERS));
}

void OrleansSvc_FishingBites(void)
{
    gSpecialVar_Result = (u16)((u16)GetGameStat(GAME_STAT_FISHING_ENCOUNTERS) - VarGet(VAR_TOURNEY_BASELINE));
}
