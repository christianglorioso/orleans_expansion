#ifndef GUARD_LAIR_COUNTERS_H
#define GUARD_LAIR_COUNTERS_H

// Battle counters behind the lair-unlock trophies (map_pass/lair_unlocks_spec.md), kept in SaveBlock3 (struct LairCounterSaveData, zeroed by a new game).
// Ids: LAIR_COUNTER_* in constants/achievements.h.
#include "constants/achievements.h"
#include "constants/battle.h"

#define LAIR_FRONTIER_COUNTERS 8 // PARALYZE .. TRICK_ROOM, one byte each (saturating at 255)

void LairCounters_Reset(void);
u32 LairCounter_Get(u32 id);
void LairCounter_Set(u32 id, u32 value);

// battle hooks (battle_util.c, battle_script_commands.c, battle_move_resolution.c)
void LairCounters_OnWeatherSet(enum BattlerId battler, u32 battleWeatherId);
void LairCounters_OnTerrainSet(enum BattlerId battler, enum BattleTerrain terrain);
void LairCounters_OnTrickRoomSet(enum BattlerId battler);
void LairCounters_OnTailwindSet(enum BattlerId battler);
void LairCounters_OnParalysisSet(enum BattlerId causer, enum BattlerId target);
void LairCounters_OnMoveDamage(enum BattlerId attacker, enum BattlerId target, enum Move move, u32 hpLost, u32 moveResultFlags);

#endif // GUARD_LAIR_COUNTERS_H
