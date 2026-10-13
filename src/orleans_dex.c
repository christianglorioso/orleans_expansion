#include "global.h"
#include "event_data.h"
#include "pokedex.h"
#include "pokemon.h"
#include "constants/pokedex.h"

// Orleans: Lafayette's Shiny Charm check. Counts the BASE species of the regional (Orleans) dex only: alternate forms that have a dex number of
// their own (Alolan, Rotom appliances, Lycanroc, ...) and Megas do not count, and neither do mythicals unless the dex forces them.
// Writes VAR_0x8005 = base species caught, VAR_0x8006 = base species required; VAR_RESULT = TRUE when every one of them is caught.
void OrleansDex_CheckBaseComplete(void)
{
    u32 i, caught = 0, total = 0;

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
        total++;
        if (GetSetPokedexFlag(nat, FLAG_GET_CAUGHT))
            caught++;
    }
    gSpecialVar_0x8005 = caught;
    gSpecialVar_0x8006 = total;
    gSpecialVar_Result = (caught >= total);
}
