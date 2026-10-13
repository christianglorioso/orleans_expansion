// Orleans: Crescent City's Pokemon services (the EV changer, the IV changer and the friendship salon).
// Called from scripts with `special`; VAR_0x8004 = party slot, VAR_0x8005 = stat (0 HP, 1 Atk, 2 Def, 3 SpA, 4 SpD, 5 Spe),
// VAR_0x8006 = mode. The answer is in VAR_RESULT. Costs and menus live in the scripts (tools/mapgen/story/CrescentCity_*.inc).
#include "global.h"
#include "pokemon.h"
#include "event_data.h"
#include "overworld.h"
#include "rtc.h"
#include "constants/pokemon.h"
#include "constants/game_stat.h"
#include "constants/vars.h"
#include "constants/flags.h"

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

// VAR_RESULT: 1 at night (the zydeco band on Camp Cocodrie's dance porch plays only then), 0 otherwise
void OrleansSvc_IsNight(void)
{
    gSpecialVar_Result = (GetTimeOfDay() == TIME_NIGHT);
}

// VAR_RESULT: 1 if the current time of day is VAR_0x8004 (0 morning, 1 day, 2 evening, 3 night = the TimeOfDay enum); the rest spots use it
void OrleansSvc_IsTimeOfDay(void)
{
    gSpecialVar_Result = (GetTimeOfDay() == gSpecialVar_0x8004);
}

// ---- Redfield's mill yard trial (Chapter 7). Six mirrors (0-5 = A-F in tools/mapgen/story_data_ch7.py), each turned to one of four facings
// (0 north-east, 1 north-west, 2 south-west, 3 south-east), two bits apiece in VAR_REDFIELD_MIRRORS. Three sundials, lit in order by a
// pair of mirrors each: dial 1 (FLAG_REDFIELD_SUN1) by D and E, dial 2 (SUN2) by B and C, dial 3 (SUN3) by A and F. A lit dial's mirrors
// are fixed in place. The facings are the puzzle's answer (the sundial keeper only says the order).
static const u8 sMirrorSolution[6] = {3, 1, 0, 1, 3, 2};
static const u8 sDialMirrors[3][2] = {{3, 4}, {1, 2}, {0, 5}};
static const u16 sDialFlags[3] = {FLAG_REDFIELD_SUN1, FLAG_REDFIELD_SUN2, FLAG_REDFIELD_SUN3};

static u32 MirrorFacing(u32 mirror)
{
    return (VarGet(VAR_REDFIELD_MIRRORS) >> (mirror * 2)) & 3;
}

static bool32 DialPairRight(u32 dial)
{
    return MirrorFacing(sDialMirrors[dial][0]) == sMirrorSolution[sDialMirrors[dial][0]]
        && MirrorFacing(sDialMirrors[dial][1]) == sMirrorSolution[sDialMirrors[dial][1]];
}

// VAR_0x8004 = mirror 0-5. Turns it one step; VAR_RESULT = its new facing, or 4 if its dial is already lit (the mirror is fixed)
void OrleansSvc_TurnMirror(void)
{
    u32 mirror = gSpecialVar_0x8004;
    u32 dial, facing, bits;

    gSpecialVar_Result = 4;
    if (mirror > 5)
        return;
    for (dial = 0; dial < 3; dial++)
    {
        if ((sDialMirrors[dial][0] == mirror || sDialMirrors[dial][1] == mirror) && FlagGet(sDialFlags[dial]))
            return;
    }
    facing = (MirrorFacing(mirror) + 1) & 3;
    bits = VarGet(VAR_REDFIELD_MIRRORS) & ~(3 << (mirror * 2));
    VarSet(VAR_REDFIELD_MIRRORS, bits | (facing << (mirror * 2)));
    gSpecialVar_Result = facing;
}

// VAR_0x8004 = mirror 0-5: VAR_RESULT = its facing
void OrleansSvc_MirrorFacing(void)
{
    gSpecialVar_Result = gSpecialVar_0x8004 > 5 ? 0 : MirrorFacing(gSpecialVar_0x8004);
}

// VAR_0x8004 = mirror 0-5: VAR_RESULT = 1 if it faces the way that catches the sun (the mirror glints)
void OrleansSvc_MirrorRight(void)
{
    gSpecialVar_Result = gSpecialVar_0x8004 <= 5 && MirrorFacing(gSpecialVar_0x8004) == sMirrorSolution[gSpecialVar_0x8004];
}

// Lights every dial whose pair is right, in order (a dial lights only after the one before it). VAR_RESULT = how many dials were lit now;
// VAR_0x8005 = 1 if some pair is right but its dial has to wait for an earlier one
void OrleansSvc_MirrorCheck(void)
{
    u32 dial, lit = 0;

    gSpecialVar_0x8005 = 0;
    for (dial = 0; dial < 3; dial++)
    {
        if (FlagGet(sDialFlags[dial]))
            continue;
        if (dial == 0 || FlagGet(sDialFlags[dial - 1]))
        {
            if (DialPairRight(dial))
            {
                FlagSet(sDialFlags[dial]);
                lit++;
                continue;
            }
        }
        else if (DialPairRight(dial))
        {
            gSpecialVar_0x8005 = 1;
        }
    }
    gSpecialVar_Result = lit;
}
