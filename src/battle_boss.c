#include "global.h"
#include "battle.h"
#include "battle_anim.h"
#include "battle_boss.h"
#include "battle_gimmick.h"
#include "battle_interface.h"
#include "battle_script_commands.h"
#include "battle_util.h"
#include "event_data.h"
#include "palette.h"
#include "pokemon.h"
#include "script.h"
#include "sprite.h"
#include "battle_main.h"
#include "battle_scripts.h"
#include "battle_setup.h"
#include "random.h"
#include "constants/form_change_types.h"

#define TAG_BOSS_BARRIER_TILE  0x57B0
#define TAG_BOSS_BARRIER_PAL   (0x57B1 | BLEND_IMMUNE_FLAG)
#define BOSS_BARRIER_SPACING   14

static const s8 sBossBarrierPosition[2] = {45, 7};

// Boss battles are singles, plus the Rayquaza raid (the player and Jayden against one Pokemon: the foe side has one battler)
static bool32 IsBossBattleFormatSupported(void)
{
    return !IsDoubleBattle() || BATTLE_TWO_VS_ONE_OPPONENT;
}

enum
{
    BOSS_BARRIER_BROKE,
    BOSS_LAST_STAND,
};

struct BossPhase
{
    u16 species;
    enum Move moves[MAX_MON_MOVES];
};

struct BossPhaseProfile
{
    u16 baseSpecies;
    u8 phaseCount;
    const struct BossPhase *phases;
};

// Orleans phase profiles. A profile gives the form and moveset of each health bar; phase 0 is applied when the battle starts and every
// broken bar steps to the next phase. A profile may have more phases than the battle has bars (a 2-bar arena uses the first two), never fewer.
// Moves were checked against the Orleans learnsets (level-up, TM/tutor, egg; the signature moves are level-up): all legal for the species.
// A phase whose first move is MOVE_NONE changes the form only and keeps the moveset.
#if P_FAMILY_KYOGRE && P_PRIMAL_REVERSIONS
static const struct BossPhase sKyogreBossPhases[] =
{
    {
        .species = SPECIES_KYOGRE,
        .moves = {MOVE_HYDRO_PUMP, MOVE_ICE_BEAM, MOVE_CALM_MIND, MOVE_SURF},
    },
    {
        .species = SPECIES_KYOGRE_PRIMAL,
        .moves = {MOVE_ORIGIN_PULSE, MOVE_ICE_BEAM, MOVE_THUNDER, MOVE_WATER_SPOUT},
    },
    {
        .species = SPECIES_KYOGRE_PRIMAL,
        .moves = {MOVE_ORIGIN_PULSE, MOVE_ICE_BEAM, MOVE_THUNDER, MOVE_CALM_MIND},
    },
    {
        .species = SPECIES_KYOGRE_PRIMAL,
        .moves = {MOVE_ORIGIN_PULSE, MOVE_ICE_BEAM, MOVE_THUNDER, MOVE_WATER_SPOUT},
    },
};

static const struct BossPhaseProfile sKyogreBossProfile =
{
    .baseSpecies = SPECIES_KYOGRE,
    .phaseCount = ARRAY_COUNT(sKyogreBossPhases),
    .phases = sKyogreBossPhases,
};
#endif

#if P_FAMILY_GROUDON && P_PRIMAL_REVERSIONS
static const struct BossPhase sGroudonBossPhases[] =
{
    {
        .species = SPECIES_GROUDON,
        .moves = {MOVE_EARTHQUAKE, MOVE_THUNDER_WAVE, MOVE_STONE_EDGE, MOVE_BULK_UP},
    },
    {
        .species = SPECIES_GROUDON_PRIMAL,
        .moves = {MOVE_PRECIPICE_BLADES, MOVE_STONE_EDGE, MOVE_FIRE_BLAST, MOVE_DRAGON_PULSE},
    },
    {
        .species = SPECIES_GROUDON_PRIMAL,
        .moves = {MOVE_PRECIPICE_BLADES, MOVE_STONE_EDGE, MOVE_FIRE_BLAST, MOVE_SWORDS_DANCE},
    },
    {
        .species = SPECIES_GROUDON_PRIMAL,
        .moves = {MOVE_PRECIPICE_BLADES, MOVE_STONE_EDGE, MOVE_FIRE_BLAST, MOVE_DRAGON_PULSE},
    },
};

static const struct BossPhaseProfile sGroudonBossProfile =
{
    .baseSpecies = SPECIES_GROUDON,
    .phaseCount = ARRAY_COUNT(sGroudonBossPhases),
    .phases = sGroudonBossPhases,
};
#endif

#if P_FAMILY_RAYQUAZA && P_MEGA_EVOLUTIONS
// The finale: two bars as Rayquaza, then Mega (Dragon Ascent) for the rest
static const struct BossPhase sRayquazaBossPhases[] =
{
    {
        .species = SPECIES_RAYQUAZA,
        .moves = {MOVE_DRAGON_DANCE, MOVE_EARTHQUAKE, MOVE_EXTREME_SPEED, MOVE_DRAGON_CLAW},
    },
    {
        .species = SPECIES_RAYQUAZA,
        .moves = {MOVE_DRAGON_DANCE, MOVE_EARTHQUAKE, MOVE_EXTREME_SPEED, MOVE_DRAGON_CLAW},
    },
    {
        .species = SPECIES_RAYQUAZA_MEGA,
        .moves = {MOVE_DRAGON_ASCENT, MOVE_DRAGON_DANCE, MOVE_EXTREME_SPEED, MOVE_EARTHQUAKE},
    },
    {
        .species = SPECIES_RAYQUAZA_MEGA,
        .moves = {MOVE_DRAGON_ASCENT, MOVE_DRAGON_DANCE, MOVE_EXTREME_SPEED, MOVE_DRAGON_CLAW},
    },
};

static const struct BossPhaseProfile sRayquazaBossProfile =
{
    .baseSpecies = SPECIES_RAYQUAZA,
    .phaseCount = ARRAY_COUNT(sRayquazaBossPhases),
    .phases = sRayquazaBossPhases,
};

// The Oldest Shrine's post-game fight: two bars, Mega on the second
static const struct BossPhase sRayquazaShrineBossPhases[] =
{
    {
        .species = SPECIES_RAYQUAZA,
        .moves = {MOVE_DRAGON_DANCE, MOVE_EARTHQUAKE, MOVE_EXTREME_SPEED, MOVE_DRAGON_CLAW},
    },
    {
        .species = SPECIES_RAYQUAZA_MEGA,
        .moves = {MOVE_DRAGON_ASCENT, MOVE_DRAGON_DANCE, MOVE_EXTREME_SPEED, MOVE_EARTHQUAKE},
    },
};

static const struct BossPhaseProfile sRayquazaShrineBossProfile =
{
    .baseSpecies = SPECIES_RAYQUAZA,
    .phaseCount = ARRAY_COUNT(sRayquazaShrineBossPhases),
    .phases = sRayquazaShrineBossPhases,
};
#endif

#if P_FAMILY_ROCKRUFF && P_MEGA_EVOLUTIONS
// The rougarou: Lycanroc (Midnight) unleashed into its Mega on the second bar (form only, its own moves stay)
static const struct BossPhase sLycanrocBossPhases[] =
{
    {
        .species = SPECIES_LYCANROC_MIDNIGHT,
        .moves = {MOVE_NONE},
    },
    {
        .species = SPECIES_LYCANROC_MIDNIGHT_MEGA,
        .moves = {MOVE_NONE},
    },
};

static const struct BossPhaseProfile sLycanrocBossProfile =
{
    .baseSpecies = SPECIES_LYCANROC_MIDDAY,
    .phaseCount = ARRAY_COUNT(sLycanrocBossPhases),
    .phases = sLycanrocBossPhases,
};
#endif

struct PendingBossBattle
{
    u16 megaSpecies;
    u8 totalBars;
    u8 statMultiplier;
    u8 phaseProfile;
    bool8 autoMega;
    bool8 active;
};

static EWRAM_DATA struct PendingBossBattle sPendingBossBattle = {0};

static const u32 sBossBarrierGfx[] = INCBIN_U32("graphics/raid/raid_barrier.4bpp");
static const u16 sBossBarrierPal[] = INCBIN_U16("graphics/raid/raid_barrier.gbapal");

static void SpriteCB_BossBarrier(struct Sprite *sprite);

static const struct OamData sOamData_BossBarrier =
{
    .y = 0,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(16x16),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(16x16),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

static const struct SpriteSheet sBossBarrierSpriteSheet =
{
    .data = sBossBarrierGfx,
    .size = sizeof(sBossBarrierGfx),
    .tag = TAG_BOSS_BARRIER_TILE,
};

static const struct SpritePalette sBossBarrierSpritePalette =
{
    .data = sBossBarrierPal,
    .tag = TAG_BOSS_BARRIER_PAL,
};

static const struct SpriteTemplate sBossBarrierSpriteTemplate =
{
    .tileTag = TAG_BOSS_BARRIER_TILE,
    .paletteTag = TAG_BOSS_BARRIER_PAL,
    .oam = &sOamData_BossBarrier,
    .anims = gDummySpriteAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCB_BossBarrier,
};

static const struct BossPhaseProfile *GetBossPhaseProfile(u8 profileId)
{
    switch (profileId)
    {
#if P_FAMILY_RAYQUAZA && P_MEGA_EVOLUTIONS
    case BOSS_PHASE_PROFILE_RAYQUAZA:
        return &sRayquazaBossProfile;
    case BOSS_PHASE_PROFILE_RAYQUAZA_SHRINE:
        return &sRayquazaShrineBossProfile;
#endif
#if P_FAMILY_KYOGRE && P_PRIMAL_REVERSIONS
    case BOSS_PHASE_PROFILE_KYOGRE:
        return &sKyogreBossProfile;
#endif
#if P_FAMILY_GROUDON && P_PRIMAL_REVERSIONS
    case BOSS_PHASE_PROFILE_GROUDON:
        return &sGroudonBossProfile;
#endif
#if P_FAMILY_ROCKRUFF && P_MEGA_EVOLUTIONS
    case BOSS_PHASE_PROFILE_LYCANROC:
        return &sLycanrocBossProfile;
#endif
    default:
        return NULL;
    }
}

bool32 IsBossBattlePending(void)
{
    return sPendingBossBattle.active;
}

void ConfigureBossBattle(u8 totalBars, u16 megaSpecies, u8 statMultiplier)
{
    ConfigureBossBattleWithProfile(totalBars, megaSpecies, statMultiplier, BOSS_PHASE_PROFILE_NONE);
}

void ConfigureBossBattleWithProfile(u8 totalBars, u16 megaSpecies, u8 statMultiplier, u8 phaseProfile)
{
    bool8 autoMega;

    totalBars = min(MAX_BOSS_HEALTH_BARS, max(1, totalBars));
    if (phaseProfile >= BOSS_PHASE_PROFILE_COUNT)
        phaseProfile = BOSS_PHASE_PROFILE_NONE;
    autoMega = megaSpecies == SPECIES_NONE && phaseProfile == BOSS_PHASE_PROFILE_NONE;
    if (statMultiplier == 0)
        statMultiplier = DEFAULT_BOSS_STAT_MULTIPLIER;
    if (!autoMega && (megaSpecies >= NUM_SPECIES || !IsSpeciesEnabled(megaSpecies)))
        megaSpecies = SPECIES_NONE;
    if (gBattleStruct != NULL && gMain.inBattle && !IsBossBattleFormatSupported())
    {
        CancelBossBattleConfiguration();
        return;
    }

    if (gBattleStruct != NULL && gMain.inBattle)
    {
        gBattleTypeFlags |= BATTLE_TYPE_BOSS;
        gBattleStruct->boss.megaSpecies = megaSpecies;
        gBattleStruct->boss.totalBars = totalBars;
        gBattleStruct->boss.barsRemaining = totalBars;
        gBattleStruct->boss.statMultiplier = statMultiplier;
        gBattleStruct->boss.phaseProfile = phaseProfile;
        gBattleStruct->boss.autoMega = autoMega;
        gBattleStruct->boss.active = TRUE;
        gBattleStruct->boss.initialized = FALSE;
        gBattleStruct->boss.originalMovesStored = FALSE;
        gBattleStruct->boss.phaseChangedForm = FALSE;
        for (u32 i = 0; i < ARRAY_COUNT(gBattleStruct->boss.barrierSpriteIds); i++)
            gBattleStruct->boss.barrierSpriteIds[i] = SPRITE_NONE;
    }
    else
    {
        sPendingBossBattle.megaSpecies = megaSpecies;
        sPendingBossBattle.totalBars = totalBars;
        sPendingBossBattle.statMultiplier = statMultiplier;
        sPendingBossBattle.phaseProfile = phaseProfile;
        sPendingBossBattle.autoMega = autoMega;
        sPendingBossBattle.active = TRUE;
    }
}

void CancelBossBattleConfiguration(void)
{
    memset(&sPendingBossBattle, 0, sizeof(sPendingBossBattle));
    gBattleTypeFlags &= ~BATTLE_TYPE_BOSS;
}

void ScriptConfigureBossBattle(struct ScriptContext *ctx)
{
    u16 totalBars = VarGet(ScriptReadHalfword(ctx));
    u16 megaSpecies = VarGet(ScriptReadHalfword(ctx));
    u16 statMultiplier = VarGet(ScriptReadHalfword(ctx));
    u16 phaseProfile = VarGet(ScriptReadHalfword(ctx));

    Script_RequestEffects(SCREFF_V1);
    ConfigureBossBattleWithProfile(totalBars, megaSpecies, statMultiplier, phaseProfile);
}

void ScriptCancelBossBattle(struct ScriptContext *ctx)
{
    Script_RequestEffects(SCREFF_V1);
    CancelBossBattleConfiguration();
}

void InitBossBattleData(void)
{
    // the Battle Frontier has no legendaries (and no bosses); link and recorded battles are never bosses
    if (gBattleTypeFlags & (BATTLE_TYPE_FRONTIER | BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED))
    {
        CancelBossBattleConfiguration();
        return;
    }

    if ((gBattleTypeFlags & BATTLE_TYPE_BOSS) && !IsBossBattleFormatSupported())
    {
        CancelBossBattleConfiguration();
        return;
    }

    if (!(gBattleTypeFlags & BATTLE_TYPE_BOSS))
    {
        memset(&sPendingBossBattle, 0, sizeof(sPendingBossBattle));
        return;
    }

    gBattleStruct->boss.megaSpecies = sPendingBossBattle.megaSpecies;
    gBattleStruct->boss.totalBars = sPendingBossBattle.active ? sPendingBossBattle.totalBars : 2;
    gBattleStruct->boss.barsRemaining = gBattleStruct->boss.totalBars;
    gBattleStruct->boss.statMultiplier = sPendingBossBattle.active ? sPendingBossBattle.statMultiplier : DEFAULT_BOSS_STAT_MULTIPLIER;
    gBattleStruct->boss.phaseProfile = sPendingBossBattle.active ? sPendingBossBattle.phaseProfile : BOSS_PHASE_PROFILE_NONE;
    gBattleStruct->boss.autoMega = sPendingBossBattle.active ? sPendingBossBattle.autoMega : TRUE;
    gBattleStruct->boss.active = TRUE;
    gBattleStruct->boss.initialized = FALSE;
    gBattleStruct->boss.originalMovesStored = FALSE;
    gBattleStruct->boss.phaseChangedForm = FALSE;
    for (u32 i = 0; i < ARRAY_COUNT(gBattleStruct->boss.barrierSpriteIds); i++)
        gBattleStruct->boss.barrierSpriteIds[i] = SPRITE_NONE;

    memset(&sPendingBossBattle, 0, sizeof(sPendingBossBattle));
}

// the bar counts of the running boss battle (0 outside one); the playtest bot reads them
u8 GetBossTotalBars(void)
{
    return IsBossBattle() ? gBattleStruct->boss.totalBars : 0;
}

u8 GetBossBarsRemaining(void)
{
    return IsBossBattle() ? gBattleStruct->boss.barsRemaining : 0;
}

bool32 IsBossBattle(void)
{
    return gBattleStruct != NULL
        && (gBattleTypeFlags & BATTLE_TYPE_BOSS)
        && gBattleStruct->boss.active;
}

static u16 GetAutomaticBossMegaSpecies(enum BattlerId battler)
{
    const struct FormChange *formChanges = GetSpeciesFormChanges(gBattleMons[battler].species);

    for (u32 i = 0; formChanges != NULL && formChanges[i].method != FORM_CHANGE_TERMINATOR; i++)
    {
        if (formChanges[i].method == FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM
         || formChanges[i].method == FORM_CHANGE_BATTLE_MEGA_EVOLUTION_MOVE)
            return formChanges[i].targetSpecies;
    }

    return SPECIES_NONE;
}

static bool32 IsLegalBossMegaSpecies(u16 baseSpecies, u16 targetSpecies)
{
    const struct FormChange *formChanges;

    if (targetSpecies == SPECIES_NONE
     || targetSpecies >= NUM_SPECIES
     || !IsSpeciesEnabled(targetSpecies))
        return FALSE;

    formChanges = GetSpeciesFormChanges(baseSpecies);
    for (u32 i = 0; formChanges != NULL && formChanges[i].method != FORM_CHANGE_TERMINATOR; i++)
    {
        if ((formChanges[i].method == FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM
          || formChanges[i].method == FORM_CHANGE_BATTLE_MEGA_EVOLUTION_MOVE)
         && formChanges[i].targetSpecies == targetSpecies)
            return TRUE;
    }

    return FALSE;
}

static bool32 IsBossPhaseProfileValid(const struct BossPhaseProfile *profile, enum BattlerId battler)
{
    if (profile == NULL
     || profile->phaseCount < gBattleStruct->boss.totalBars
     || GET_BASE_SPECIES_ID(gBattleMons[battler].species) != profile->baseSpecies)
        return FALSE;

    for (u32 phase = 0; phase < profile->phaseCount; phase++)
    {
        u16 species = profile->phases[phase].species;

        if (species == SPECIES_NONE
         || species >= NUM_SPECIES
         || !IsSpeciesEnabled(species)
         || GET_BASE_SPECIES_ID(species) != profile->baseSpecies)
            return FALSE;

        if (profile->phases[phase].moves[0] != MOVE_NONE)
        {
            for (u32 moveSlot = 0; moveSlot < MAX_MON_MOVES; moveSlot++)
            {
                if (profile->phases[phase].moves[moveSlot] >= MOVES_COUNT_ALL)
                    return FALSE;
            }
        }
    }

    return TRUE;
}

static void StoreBossOriginalMoves(enum BattlerId battler)
{
    struct Pokemon *mon = GetBattlerMon(battler);

    if (gBattleStruct->boss.originalMovesStored)
        return;

    for (u32 moveSlot = 0; moveSlot < MAX_MON_MOVES; moveSlot++)
    {
        gBattleStruct->boss.originalMoves[moveSlot] = GetMonData(mon, MON_DATA_MOVE1 + moveSlot);
        gBattleStruct->boss.originalPp[moveSlot] = GetMonData(mon, MON_DATA_PP1 + moveSlot);
    }
    gBattleStruct->boss.originalMovesStored = TRUE;
}

static void ResetBossMoveLocks(enum BattlerId battler)
{
    gBattleMons[battler].volatiles.disabledMove = MOVE_NONE;
    gBattleMons[battler].volatiles.disableTimer = 0;
    gBattleMons[battler].volatiles.encoredMove = MOVE_NONE;
    gBattleMons[battler].volatiles.encoreTimer = 0;
    gBattleMons[battler].volatiles.torment = FALSE;
    gBattleMons[battler].volatiles.tormentTimer = 0;
    gBattleMons[battler].volatiles.multipleTurns = FALSE;
    gBattleMons[battler].volatiles.rampageTurns = 0;
    gBattleMons[battler].volatiles.bideTurns = 0;
    gBattleMons[battler].volatiles.rechargeTimer = 0;
    gBattleMons[battler].volatiles.usedMoves = 0;
    gBattleStruct->choicedMove[battler] = MOVE_NONE;
    gLockedMoves[battler] = MOVE_NONE;
    gProtectStructs[battler].noValidMoves = FALSE;
    gProtectStructs[battler].chargingTurn = FALSE;
}

static enum BattlerId GetBossPhaseMoveTarget(enum BattlerId battler, enum Move move)
{
    // Boss battles are singles (or one boss against the player and a partner), so target selection only needs
    // to distinguish moves aimed across the field from moves aimed at the user.
    // Keeping this attacker-explicit avoids mutating battle-script globals in
    // the middle of the player's move-end processing.
    switch (GetBattlerMoveTargetType(battler, move))
    {
    case TARGET_SELECTED:
    case TARGET_SMART:
    case TARGET_OPPONENT:
    case TARGET_RANDOM:
    case TARGET_DEPENDS:
    case TARGET_BOTH:
    case TARGET_FOES_AND_ALLY:
    case TARGET_OPPONENTS_FIELD:
        if (IsDoubleBattle() && gBattleStruct->boss.active && !IsOnPlayerSide(battler))
        {
            // one of the two player-side battlers, as the AI would pick
            enum BattlerId left = GetBattlerAtPosition(B_POSITION_PLAYER_LEFT), right = GetBattlerAtPosition(B_POSITION_PLAYER_RIGHT);

            if (IsBattlerAlive(left) && IsBattlerAlive(right))
                return (Random() & 1) ? left : right;
            return IsBattlerAlive(left) ? left : right;
        }
        return GetBattlerAtPosition(B_POSITION_PLAYER_LEFT);
    default:
        return battler;
    }
}

static void ApplyBossPhaseMoves(enum BattlerId battler, const struct BossPhase *phase)
{
    struct Pokemon *mon = GetBattlerMon(battler);
    u8 ppBonuses;

    // MOVE_NONE in the first slot is an explicit opt-out for profiles that only
    // need form changes. Other empty slots remain valid moveset entries.
    if (phase->moves[0] == MOVE_NONE)
        return;

    StoreBossOriginalMoves(battler);
    ppBonuses = GetMonData(mon, MON_DATA_PP_BONUSES);
    for (u32 moveSlot = 0; moveSlot < MAX_MON_MOVES; moveSlot++)
    {
        enum Move move = phase->moves[moveSlot];
        u8 pp = CalculatePPWithBonus(move, ppBonuses, moveSlot);

        SetMonData(mon, MON_DATA_MOVE1 + moveSlot, &move);
        SetMonData(mon, MON_DATA_PP1 + moveSlot, &pp);
        gBattleMons[battler].moves[moveSlot] = move;
        gBattleMons[battler].pp[moveSlot] = pp;
    }

    ResetBossMoveLocks(battler);

    // If the boss has already selected a move this turn, keep its selected slot
    // but make that slot use the new phase's move. This avoids executing a stale
    // move ID after the old moveset has been replaced.
    if (gChosenActionByBattler[battler] == B_ACTION_USE_MOVE && !HasBattlerActedThisTurn(battler))
    {
        u8 moveSlot = gBattleStruct->chosenMovePositions[battler];

        if (moveSlot < MAX_MON_MOVES)
        {
            gChosenMoveByBattler[battler] = gBattleMons[battler].moves[moveSlot];
            gBattleStruct->moveTarget[battler] = GetBossPhaseMoveTarget(battler, gChosenMoveByBattler[battler]);
        }
    }
}

static void ApplyBossStatMultiplier(enum BattlerId battler)
{
    u32 multiplier = gBattleStruct->boss.statMultiplier;

    gBattleMons[battler].attack = min(MAX_u16, gBattleMons[battler].attack * multiplier / 100);
    gBattleMons[battler].defense = min(MAX_u16, gBattleMons[battler].defense * multiplier / 100);
    gBattleMons[battler].speed = min(MAX_u16, gBattleMons[battler].speed * multiplier / 100);
    gBattleMons[battler].spAttack = min(MAX_u16, gBattleMons[battler].spAttack * multiplier / 100);
    gBattleMons[battler].spDefense = min(MAX_u16, gBattleMons[battler].spDefense * multiplier / 100);
}

void ApplyBossStatMultiplierAfterRecalculation(enum BattlerId battler)
{
    if (!IsBossBattle()
     || !gBattleStruct->boss.initialized
     || battler != GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT)
     || gBattleOutcome != 0
     || gBattleStruct->victoryCatchState != VICTORY_CATCH_START)
        return;

    ApplyBossStatMultiplier(battler);
}

static bool32 ForceBossFormChange(enum BattlerId battler, u16 targetSpecies)
{
    struct Pokemon *mon = GetBattlerMon(battler);
    struct PartyState *partyState = GetBattlerPartyState(battler);

    if (targetSpecies == SPECIES_NONE || targetSpecies == gBattleMons[battler].species)
        return FALSE;

    if (partyState != NULL && partyState->changedSpecies == SPECIES_NONE)
        partyState->changedSpecies = gBattleMons[battler].species;

    SetMonData(mon, MON_DATA_SPECIES, &targetSpecies);
    gBattleMons[battler].species = targetSpecies;
    RecalcBattlerStats(battler, mon, FALSE);
    SetActiveGimmick(battler, GIMMICK_MEGA);
    SetGimmickAsActivated(battler, GIMMICK_MEGA);
    return TRUE;
}

static bool32 ApplyBossPhase(enum BattlerId battler, const struct BossPhase *phase)
{
    bool32 changedForm = ForceBossFormChange(battler, phase->species);

    ApplyBossPhaseMoves(battler, phase);
    return changedForm;
}

bool32 TryStartBossBattle(void)
{
    enum BattlerId battler;
    u16 megaSpecies;
    const struct BossPhaseProfile *profile;

    if (!IsBossBattle() || gBattleStruct->boss.initialized)
        return FALSE;

    battler = GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT);
    profile = GetBossPhaseProfile(gBattleStruct->boss.phaseProfile);
    if (gBattleStruct->boss.phaseProfile != BOSS_PHASE_PROFILE_NONE)
    {
        gBattleStruct->boss.initialized = TRUE;
        if (IsBossPhaseProfileValid(profile, battler))
        {
            gBattleStruct->boss.phaseChangedForm = ApplyBossPhase(battler, &profile->phases[0]);
            if (!gBattleStruct->boss.phaseChangedForm)
                ApplyBossStatMultiplierAfterRecalculation(battler);
            if (gBattleStruct->boss.phaseChangedForm)
            {
                gBattlerAttacker = battler;
                gBattleScripting.battler = battler;
                return TRUE;
            }
            return FALSE;
        }

        // A profile for the wrong species, bar count, or disabled forms is
        // ignored safely instead of indexing invalid ROM data.
        gBattleStruct->boss.phaseProfile = BOSS_PHASE_PROFILE_NONE;
        ApplyBossStatMultiplierAfterRecalculation(battler);
        return FALSE;
    }

    megaSpecies = gBattleStruct->boss.megaSpecies;
    if (gBattleStruct->boss.autoMega)
        megaSpecies = GetAutomaticBossMegaSpecies(battler);
    else if (!IsLegalBossMegaSpecies(gBattleMons[battler].species, megaSpecies))
        megaSpecies = SPECIES_NONE;

    gBattleStruct->boss.initialized = TRUE;
    if (ForceBossFormChange(battler, megaSpecies))
    {
        gBattlerAttacker = battler;
        gBattleScripting.battler = battler;
        return TRUE;
    }

    ApplyBossStatMultiplierAfterRecalculation(battler);
    return FALSE;
}

static void ResetBossPhaseConditions(enum BattlerId battler, bool32 enteringLastStand)
{
    u32 status = STATUS1_NONE;

    if (enteringLastStand)
    {
        for (enum Stat stat = 0; stat < NUM_BATTLE_STATS; stat++)
        {
            if (gBattleMons[battler].statStages[stat] < DEFAULT_STAT_STAGE)
                gBattleMons[battler].statStages[stat] = DEFAULT_STAT_STAGE;
        }
    }

    gBattleMons[battler].status1 = status;
    SetMonData(GetBattlerMon(battler), MON_DATA_STATUS, &status);

    gBattleMons[battler].volatiles.confusionTimer = 0;
    gBattleMons[battler].volatiles.flinched = FALSE;
    gBattleMons[battler].volatiles.wrapped = FALSE;
    gBattleMons[battler].volatiles.infatuation = 0;
    gBattleMons[battler].volatiles.escapePrevention = FALSE;
    gBattleMons[battler].volatiles.leechSeed = 0;
    gBattleMons[battler].volatiles.perishSong = FALSE;
}

bool32 TryBossHealthBarBreak(enum BattlerId battler)
{
    const struct BossPhaseProfile *profile;
    u16 hp;

    if (!IsBossBattle()
     || battler != GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT)
     || IsBattlerAlive(battler)
     || gBattleStruct->boss.barsRemaining <= 1)
        return FALSE;

    gBattleStruct->boss.barsRemaining--;
    gBattleStruct->boss.phaseChangedForm = FALSE;
    // A phase boundary ends the current attack. Otherwise a multi-hit move
    // would continue striking the freshly restored bar.
    if (gMultiHitCounter > 1)
        gMultiHitCounter = 1;

    profile = GetBossPhaseProfile(gBattleStruct->boss.phaseProfile);
    if (profile != NULL)
    {
        u32 phase = gBattleStruct->boss.totalBars - gBattleStruct->boss.barsRemaining;

        if (phase < profile->phaseCount)
            gBattleStruct->boss.phaseChangedForm = ApplyBossPhase(battler, &profile->phases[phase]);
    }

    hp = gBattleMons[battler].maxHP;
    gBattleMons[battler].hp = hp;
    SetMonData(GetBattlerMon(battler), MON_DATA_HP, &hp);
    gBattleCommunication[MULTISTRING_CHOOSER] = gBattleStruct->boss.barsRemaining == 1
        ? BOSS_LAST_STAND
        : BOSS_BARRIER_BROKE;
    ResetBossPhaseConditions(battler, gBattleStruct->boss.barsRemaining == 1);
    SyncBossHealthBarSprites(battler);
    return TRUE;
}

bool32 DidBossPhaseChangeForm(void)
{
    return IsBossBattle() && gBattleStruct->boss.phaseChangedForm;
}

// The battle script for the bar that just broke: the plain break, or with a form change (Primal Reversion gets its own animation and text)
const u8 *GetBossBarBreakScript(void)
{
    u16 species = gBattleMons[GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT)].species;

    if (!DidBossPhaseChangeForm())
        return BattleScript_BossHealthBarBreak;
    gBattleStruct->boss.deferFormIndicator = TRUE;
    if (species == SPECIES_KYOGRE_PRIMAL || species == SPECIES_GROUDON_PRIMAL)
        return BattleScript_BossHealthBarBreakAndPrimal;
    return BattleScript_BossHealthBarBreakAndFormChange;
}

void RestoreBossOriginalMovesForCapture(enum BattlerId battler)
{
    struct Pokemon *mon;

    if (!IsBossBattle()
     || !gBattleStruct->boss.originalMovesStored
     || battler != GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT))
        return;

    mon = GetBattlerMon(battler);
    for (u32 moveSlot = 0; moveSlot < MAX_MON_MOVES; moveSlot++)
    {
        enum Move move = gBattleStruct->boss.originalMoves[moveSlot];
        u8 pp = gBattleStruct->boss.originalPp[moveSlot];

        SetMonData(mon, MON_DATA_MOVE1 + moveSlot, &move);
        SetMonData(mon, MON_DATA_PP1 + moveSlot, &pp);
        gBattleMons[battler].moves[moveSlot] = move;
        gBattleMons[battler].pp[moveSlot] = pp;
    }
}

void RefreshBossHealthbox(enum BattlerId battler)
{
    if (!IsBossBattle()
     || battler >= gBattlersCount
     || gHealthboxSpriteIds[battler] >= MAX_SPRITES
     || !gSprites[gHealthboxSpriteIds[battler]].inUse)
        return;

    UpdateHealthboxAttribute(gHealthboxSpriteIds[battler], GetBattlerMon(battler), HEALTHBOX_ALL);
}

static void SpriteCB_BossBarrier(struct Sprite *sprite)
{
    enum BattlerId battler = sprite->data[0];
    u32 barrier = sprite->data[1];
    struct Sprite *healthbox;

    if (!IsBossBattle()
     || battler >= gBattlersCount
     || gHealthboxSpriteIds[battler] >= MAX_SPRITES
     || !gSprites[gHealthboxSpriteIds[battler]].inUse)
    {
        sprite->invisible = TRUE;
        return;
    }

    healthbox = &gSprites[gHealthboxSpriteIds[battler]];

    // The base position is fixed when the sprite is created. Follow only the
    // healthbox's movement offsets so both sprites remain synchronized.
    sprite->x2 = healthbox->x2;
    sprite->y2 = healthbox->y2;
    // Battle animations temporarily change healthbox priority. Matching it
    // keeps the barrier's lower subpriority consistently above the frame.
    sprite->oam.priority = healthbox->oam.priority;
    sprite->invisible = healthbox->invisible
        || barrier >= gBattleStruct->boss.barsRemaining - 1;

    // Time-of-day and weather blending operate on the faded buffer. Restore
    // this UI palette once normal screen fades have finished.
    if (barrier == 0 && !gPaletteFade.active)
        CpuCopy16(sBossBarrierPal, &gPlttBufferFaded[OBJ_PLTT_ID(sprite->oam.paletteNum)], PLTT_SIZE_4BPP);
}

void SyncBossHealthBarSprites(enum BattlerId battler)
{
    if (!IsBossBattle() || battler != GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT))
        return;

    for (u32 i = 0; i < ARRAY_COUNT(gBattleStruct->boss.barrierSpriteIds); i++)
    {
        u8 spriteId = gBattleStruct->boss.barrierSpriteIds[i];
        if (spriteId < MAX_SPRITES
         && gSprites[spriteId].inUse
         && gSprites[spriteId].template == &sBossBarrierSpriteTemplate)
            SpriteCB_BossBarrier(&gSprites[spriteId]);
    }
}

u8 CountVisibleBossHealthBarSprites(void)
{
    u8 count = 0;

    if (!IsBossBattle())
        return 0;

    for (u32 i = 0; i < ARRAY_COUNT(gBattleStruct->boss.barrierSpriteIds); i++)
    {
        u8 spriteId = gBattleStruct->boss.barrierSpriteIds[i];
        if (spriteId < MAX_SPRITES
         && gSprites[spriteId].inUse
         && gSprites[spriteId].template == &sBossBarrierSpriteTemplate
         && !gSprites[spriteId].invisible)
            count++;
    }
    return count;
}

void CreateBossHealthBarSprites(enum BattlerId battler)
{
    s16 x, y;

    if (!IsBossBattle()
     || battler != GetBattlerAtPosition(B_POSITION_OPPONENT_LEFT)
     || gBattleStruct->boss.totalBars <= 1
     || gHealthboxSpriteIds[battler] >= MAX_SPRITES
     || !gSprites[gHealthboxSpriteIds[battler]].inUse)
        return;

    for (u32 i = 0; i < ARRAY_COUNT(gBattleStruct->boss.barrierSpriteIds); i++)
    {
        u8 spriteId = gBattleStruct->boss.barrierSpriteIds[i];

        if (spriteId < MAX_SPRITES
         && gSprites[spriteId].inUse
         && gSprites[spriteId].template == &sBossBarrierSpriteTemplate)
            DestroySprite(&gSprites[spriteId]);
        gBattleStruct->boss.barrierSpriteIds[i] = SPRITE_NONE;
    }

    GetBattlerHealthboxCoords(battler, &x, &y);
    if (GetSpriteTileStartByTag(TAG_BOSS_BARRIER_TILE) == 0xFFFF)
        LoadSpriteSheet(&sBossBarrierSpriteSheet);
    if (IndexOfSpritePaletteTag(TAG_BOSS_BARRIER_PAL) == 0xFF)
        LoadSpritePalette(&sBossBarrierSpritePalette);

    for (u32 i = 0; i < gBattleStruct->boss.totalBars - 1; i++)
    {
        u8 spriteId = CreateSprite(&sBossBarrierSpriteTemplate,
                                   x + sBossBarrierPosition[0] - (s16)(i * BOSS_BARRIER_SPACING),
                                   y + sBossBarrierPosition[1],
                                   0);
        if (spriteId == MAX_SPRITES)
            break;
        gBattleStruct->boss.barrierSpriteIds[i] = spriteId;
        gSprites[spriteId].data[0] = battler;
        gSprites[spriteId].data[1] = i;
    }
    SyncBossHealthBarSprites(battler);
}
