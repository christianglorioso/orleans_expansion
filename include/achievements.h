#ifndef GUARD_ACHIEVEMENTS_H
#define GUARD_ACHIEVEMENTS_H

// Achievement ("trophy") system. Engine lifted from SoulGold (Eemeliri); comfy_anim by Montblanc via SoulGold. See CREDITS.md.
// The table is generated (tools/achievements/), rewards are in src/data/achievement_rewards.h.

#include "main.h"
#include "constants/achievements.h"

struct Achievement
{
    u8 id;
    u8 category;
    u8 tier;
    u8 trigger;
    u16 arg;
    u32 value;
    bool32 (*predicate)(void);
    const u8 *name;
    const u8 *description;
};

// Up to two item stacks, money and Battle Points. All-zero = no reward.
struct AchievementReward
{
    u16 item;
    u16 item2;
    u16 qty;
    u16 qty2;
    u16 money;
    u16 bp;
};


bool32 Achievement_Unlock(enum AchievementId id);
void Achievement_CheckAll(void);
void Achievement_OnTrainerBattleWon(u16 trainerId);
void Achievement_OnMegaEvolved(void);
void Achievement_OnMapEntered(void);
void Achievement_Reset(void);
void Achievement_TryShowQueuedPopup(void);
void Achievement_HidePopup(void);
u16 Achievement_CountUnlocked(void);
u16 Achievement_GetCount(void);
bool32 Achievement_IsUnlocked(enum AchievementId id);
bool32 Achievement_IsRewardPending(enum AchievementId id);
bool32 Achievement_GiveReward(enum AchievementId id); // TRUE when handed over (or nothing to give)
u8 *Achievement_BuildRewardText(enum AchievementId id, u8 *dst); // "3 Great Balls, 500 BP"; empty string when none
u32 Achievement_GetProgress(const struct Achievement *achievement);
u32 Achievement_GetTarget(const struct Achievement *achievement);
const struct Achievement *Achievement_GetByIndex(u16 index);
const struct Achievement *Achievement_GetById(enum AchievementId id);
const u8 *Achievement_GetCategoryName(enum AchievementCategory category);
u16 Achievement_GetTierBallItem(enum AchievementTier tier);
bool32 Achievement_IsComingSoon(const struct Achievement *achievement);

// specials
void Achievement_Poll(void);
void Achievement_UnlockVar8004(void);
void Achievement_CheckAllSpecial(void);
void Achievement_GetCountSpecial(void);
void Achievement_ClaimNextReward(void); // VAR_RESULT: 0 nothing waiting, 1 given (gStringVar4 = message), 2 bag full

void CB2_InitAchievementsMenu(void);
void CB2_InitAchievementsMenuWithCallback(MainCallback callback);

#endif // GUARD_ACHIEVEMENTS_H
