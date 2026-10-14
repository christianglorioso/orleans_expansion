#include "global.h"
#include "lair_counters.h"
#include "battle.h"
#include "battle_util.h"
#include "move.h"

// Orleans: the counters behind the lair-unlock trophies. Frontier counters count what the PLAYER's side causes (move or ability) inside Battle Frontier
// facilities; "set" means the effect actually started (the hooks sit after the engine's own success checks, so a failed move or a weather that was already
// up never gets here). The two damage counters count the HP actually removed from opposing Pokemon, in any battle.

static struct LairCounterSaveData *Counters(void)
{
    return &gSaveBlock3Ptr->lairCounters;
}

void LairCounters_Reset(void)
{
    memset(Counters(), 0, sizeof(*Counters()));
}

u32 LairCounter_Get(u32 id)
{
    if (id < LAIR_FRONTIER_COUNTERS)
        return Counters()->frontier[id];
    if (id < LAIR_COUNTER_COUNT)
        return Counters()->damage[id - LAIR_FRONTIER_COUNTERS];
    return 0;
}

void LairCounter_Set(u32 id, u32 value)
{
    if (id < LAIR_FRONTIER_COUNTERS)
        Counters()->frontier[id] = value > 255 ? 255 : value;
    else if (id < LAIR_COUNTER_COUNT)
        Counters()->damage[id - LAIR_FRONTIER_COUNTERS] = value;
}

static void AddFrontier(u32 id)
{
    u32 v = LairCounter_Get(id);

    if (v < 255)
        Counters()->frontier[id] = v + 1;
}

static bool32 PlayerFrontierEvent(enum BattlerId battler)
{
    return (gBattleTypeFlags & BATTLE_TYPE_FRONTIER) && GetBattlerSide(battler) == B_SIDE_PLAYER;
}

void LairCounters_OnWeatherSet(enum BattlerId battler, u32 battleWeatherId)
{
    if (!PlayerFrontierEvent(battler))
        return;
    switch (battleWeatherId)
    {
    case BATTLE_WEATHER_SUN:
    case BATTLE_WEATHER_SUN_PRIMAL:
        AddFrontier(LAIR_COUNTER_SUN);
        break;
    case BATTLE_WEATHER_RAIN:
    case BATTLE_WEATHER_RAIN_PRIMAL:
    case BATTLE_WEATHER_RAIN_DOWNPOUR:
        AddFrontier(LAIR_COUNTER_RAIN);
        break;
    case BATTLE_WEATHER_SANDSTORM:
        AddFrontier(LAIR_COUNTER_SANDSTORM);
        break;
    case BATTLE_WEATHER_SNOW:
    case BATTLE_WEATHER_HAIL:
        AddFrontier(LAIR_COUNTER_SNOW);
        break;
    }
}

void LairCounters_OnTerrainSet(enum BattlerId battler, enum BattleTerrain terrain)
{
    if (terrain == B_TERRAIN_MISTY && PlayerFrontierEvent(battler))
        AddFrontier(LAIR_COUNTER_MISTY);
}

void LairCounters_OnTrickRoomSet(enum BattlerId battler)
{
    if (PlayerFrontierEvent(battler))
        AddFrontier(LAIR_COUNTER_TRICK_ROOM);
}

void LairCounters_OnTailwindSet(enum BattlerId battler)
{
    if (PlayerFrontierEvent(battler))
        AddFrontier(LAIR_COUNTER_TAILWIND);
}

// causer = the battler whose move or ability did it; only a Pokemon of the other side counts (paralyzing "25 Pokemon")
void LairCounters_OnParalysisSet(enum BattlerId causer, enum BattlerId target)
{
    if (PlayerFrontierEvent(causer) && GetBattlerSide(target) != B_SIDE_PLAYER)
        AddFrontier(LAIR_COUNTER_PARALYZE);
}

static void AddDamage(u32 id, u32 hp)
{
    u32 v = LairCounter_Get(id);

    Counters()->damage[id - LAIR_FRONTIER_COUNTERS] = (v + hp < v || v + hp > 1000000) ? 1000000 : v + hp;
}

void LairCounters_OnMoveDamage(enum BattlerId attacker, enum BattlerId target, enum Move move, u32 hpLost, u32 moveResultFlags)
{
    if (hpLost == 0 || GetBattlerSide(attacker) != B_SIDE_PLAYER || GetBattlerSide(target) == B_SIDE_PLAYER)
        return;
    if (IsBitingMove(move))
        AddDamage(LAIR_COUNTER_BITE_DAMAGE, hpLost);
    if (GetBattleMoveType(move) == TYPE_PSYCHIC && (moveResultFlags & MOVE_RESULT_HIGH_EFFECTIVENESS))
        AddDamage(LAIR_COUNTER_PSYCHIC_DAMAGE, hpLost);
}
