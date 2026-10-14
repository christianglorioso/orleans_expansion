#ifndef GUARD_BATTLE_BOSS_H
#define GUARD_BATTLE_BOSS_H

#define MAX_BOSS_HEALTH_BARS 4
#define DEFAULT_BOSS_STAT_MULTIPLIER 110

struct ScriptContext;

void ConfigureBossBattle(u8 totalBars, u16 megaSpecies, u8 statMultiplier);
void ConfigureBossBattleWithProfile(u8 totalBars, u16 megaSpecies, u8 statMultiplier, u8 phaseProfile);
void CancelBossBattleConfiguration(void);
void ScriptConfigureBossBattle(struct ScriptContext *ctx);
void ScriptCancelBossBattle(struct ScriptContext *ctx);
bool32 IsBossBattlePending(void);
void InitBossBattleData(void);
bool32 IsBossBattle(void);
u8 GetBossTotalBars(void);
u8 GetBossBarsRemaining(void);
bool32 TryStartBossBattle(void);
void ApplyBossStatMultiplierAfterRecalculation(enum BattlerId battler);
bool32 TryBossHealthBarBreak(enum BattlerId battler);
bool32 DidBossPhaseChangeForm(void);
const u8 *GetBossBarBreakScript(void);
void RestoreBossOriginalMovesForCapture(enum BattlerId battler);
void RefreshBossHealthbox(enum BattlerId battler);
void SyncBossHealthBarSprites(enum BattlerId battler);
u8 CountVisibleBossHealthBarSprites(void);
void CreateBossHealthBarSprites(enum BattlerId battler);

#endif // GUARD_BATTLE_BOSS_H
