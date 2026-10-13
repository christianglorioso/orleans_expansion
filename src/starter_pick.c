#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "script_menu.h"
#include "string_util.h"
#include "constants/pokemon.h"
#include "constants/species.h"

// Orleans: the three starter Poke Balls in the shelter. A ball's personality (nature, gender, shiny, ability slot) is rolled the first time the
// player looks at THAT ball and kept in plain RAM (never saved): looking again in the same session shows the same values and the Pokemon that is
// handed over matches them exactly, while a save made before choosing + a soft reset gives a fresh roll.

#define STARTER_COUNT   3
#define ROLL_VALID      (1 << 15)
#define ROLL_NATURE(r)  ((r) & 0x1F)
#define ROLL_GENDER(r)  (((r) >> 5) & 3)    // 0 male, 1 female, 2 genderless
#define ROLL_SHINY(r)   (((r) >> 7) & 1)
#define ROLL_ABILITY(r) (((r) >> 8) & 3)

static EWRAM_DATA u16 sStarterRoll[STARTER_COUNT] = {0};

static const u16 sStarterSpecies[STARTER_COUNT] = { SPECIES_TOTODILE, SPECIES_CHIKORITA, SPECIES_FUECOCO };

static u16 RollStarter(u32 idx)
{
    enum Species species = sStarterSpecies[idx];
    u32 personality = Random32();
    u32 nature = Random32() % NUM_NATURES;
    u32 gender, shiny, ability = 0;
    u8 g = GetGenderFromSpeciesAndPersonality(species, personality);

    gender = (g == MON_MALE) ? 0 : (g == MON_FEMALE) ? 1 : 2;
    shiny = ComputePlayerShinyOdds(personality, Random32()) ? 1 : 0;
    // a regular ability slot (not the hidden one): slot 1 only when the species has one
    if (GetAbilityBySpecies(species, 1) != ABILITY_NONE)
        ability = Random() & 1;
    return ROLL_VALID | nature | (gender << 5) | (shiny << 7) | (ability << 8);
}

// VAR_0x8004 = 0/1/2. Rolls the ball if it has not been rolled this session, then writes:
//   VAR_0x8005 nature, VAR_0x8006 ability slot, VAR_0x8007 gender (MON_MALE/FEMALE/GENDERLESS), VAR_0x8008 shiny (0/1)  -> exactly what givemon takes
//   STR_VAR_1 species name, STR_VAR_2 "male, " / "female, " / "" , STR_VAR_3 nature name; VAR_RESULT = shiny
void StarterBall_Prepare(void)
{
    u32 idx = gSpecialVar_0x8004;
    u16 r;
    u32 g;

    if (idx >= STARTER_COUNT)
        idx = 0;
    if (!(sStarterRoll[idx] & ROLL_VALID))
        sStarterRoll[idx] = RollStarter(idx);
    r = sStarterRoll[idx];
    g = ROLL_GENDER(r);

    gSpecialVar_0x8005 = ROLL_NATURE(r);
    gSpecialVar_0x8006 = ROLL_ABILITY(r);
    gSpecialVar_0x8007 = (g == 0) ? MON_MALE : (g == 1) ? MON_FEMALE : MON_GENDERLESS;
    gSpecialVar_0x8008 = ROLL_SHINY(r);

    StringCopy(gStringVar1, GetSpeciesName(sStarterSpecies[idx]));
    StringCopy(gStringVar2, (g == 0) ? COMPOUND_STRING("male, ") : (g == 1) ? COMPOUND_STRING("female, ") : COMPOUND_STRING(""));
    StringCopy(gStringVar3, gNaturesInfo[ROLL_NATURE(r)].name);
    gSpecialVar_Result = ROLL_SHINY(r);
}

// the pic box (8x8 tiles at x,y) for the ball in VAR_0x8004, in its shiny palette when it rolled shiny
void StarterBall_ShowPic(void)
{
    StarterBall_Prepare();
    // personality only picks the gender-difference sprite: 0 is "female", 0xFF "male"
    ScriptMenu_SetPicShiny(gSpecialVar_0x8008, gSpecialVar_0x8007 == MON_FEMALE ? 0 : 0xFF);
    ScriptMenu_ShowPokemonPic(sStarterSpecies[gSpecialVar_0x8004 < STARTER_COUNT ? gSpecialVar_0x8004 : 0], 1, 1);
    ScriptMenu_SetPicShiny(FALSE, 0x8000);
}
