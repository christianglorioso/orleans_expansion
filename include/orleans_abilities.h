#ifndef GUARD_ORLEANS_ABILITIES_H
#define GUARD_ORLEANS_ABILITIES_H

// Orleans custom abilities (tools/dex/new_abilities.py, descriptions in orleans_dex.xlsx Notes).
// Many are an existing ability plus a rider, so the engine checks for the base ability go through these macros.

#define ABILITY_IS_LEVITATE(a)       ((a) == ABILITY_LEVITATE || (a) == ABILITY_EELEVATE || (a) == ABILITY_BUOYANCY \
                                   || (a) == ABILITY_FIREDAMP || (a) == ABILITY_SWAMP_GAS || (a) == ABILITY_SKY_SCORCHER \
                                   || (a) == ABILITY_LIVE_WIRE)
#define ABILITY_IS_SUCTION_CUPS(a)   ((a) == ABILITY_SUCTION_CUPS || (a) == ABILITY_BUOYANCY || (a) == ABILITY_CYPRESS_KNEES \
                                   || (a) == ABILITY_HEARTWOOD)
#define ABILITY_IS_UNAWARE(a)        ((a) == ABILITY_UNAWARE || (a) == ABILITY_CROC_AND_ROLL)
#define ABILITY_IS_PUNK_ROCK(a)      ((a) == ABILITY_PUNK_ROCK || (a) == ABILITY_CROC_AND_ROLL)
#define ABILITY_IS_NO_GUARD(a)       ((a) == ABILITY_NO_GUARD || (a) == ABILITY_ROUGAROU)
#define ABILITY_IS_INFILTRATOR(a)    ((a) == ABILITY_INFILTRATOR || (a) == ABILITY_ROUGAROU)
#define ABILITY_IS_STRONG_JAW(a)     ((a) == ABILITY_STRONG_JAW || (a) == ABILITY_DEATH_ROLL)
#define ABILITY_IS_SHARPNESS(a)      ((a) == ABILITY_SHARPNESS || (a) == ABILITY_TIMBER)
#define ABILITY_IS_TECHNICIAN(a)     ((a) == ABILITY_TECHNICIAN || (a) == ABILITY_BLUR)
#define ABILITY_IS_SCRAPPY(a)        ((a) == ABILITY_SCRAPPY || (a) == ABILITY_ZYDECO)
#define ABILITY_IS_CONTRARY(a)       ((a) == ABILITY_CONTRARY || (a) == ABILITY_REGAL_COIL)
#define ABILITY_IS_QUEENLY(a)        ((a) == ABILITY_QUEENLY_MAJESTY || (a) == ABILITY_REGAL_COIL)
#define ABILITY_IS_REGENERATOR(a)    ((a) == ABILITY_REGENERATOR || (a) == ABILITY_GRAVEYARD_MOSS)
#define ABILITY_IS_DROUGHT(a)        ((a) == ABILITY_DROUGHT || (a) == ABILITY_SKY_SCORCHER || (a) == ABILITY_BURNING_SEASON)
#define ABILITY_IS_DANCER(a)         ((a) == ABILITY_DANCER || (a) == ABILITY_SECOND_LINE)
#define ABILITY_IS_POISON_TOUCH(a)   ((a) == ABILITY_POISON_TOUCH || (a) == ABILITY_COTTONMOUTH)
#define ABILITY_IS_STAMINA(a)        ((a) == ABILITY_STAMINA || (a) == ABILITY_HEARTWOOD)
#define ABILITY_IS_LEECH_SEED_ON_CONTACT(a) ((a) == ABILITY_CLINGING_MOSS || (a) == ABILITY_GRAVEYARD_MOSS)

static inline bool32 OrleansIsSleepInducingMove(enum Move move)
{
    return GetMoveEffect(move) == EFFECT_NON_VOLATILE_STATUS && GetMoveNonVolatileStatus(move) == MOVE_EFFECT_SLEEP;
}

// The damage-modifier switch in CalcMoveBasePowerAfterModifiers treats these as their base ability.
static inline enum Ability OrleansPowerAbilityAlias(enum Ability ability)
{
    switch (ability)
    {
    case ABILITY_BLUR:          return ABILITY_TECHNICIAN;
    case ABILITY_DEATH_ROLL:    return ABILITY_STRONG_JAW;
    case ABILITY_TIMBER:        return ABILITY_SHARPNESS;
    case ABILITY_CROC_AND_ROLL: return ABILITY_PUNK_ROCK;
    default:                    return ability;
    }
}

#endif // GUARD_ORLEANS_ABILITIES_H
