#ifndef GUARD_REGIONS_H
#define GUARD_REGIONS_H

#include "global.h"
#include "constants/regions.h"

enum KantoSubRegion GetKantoSubregion(u32 mapSecId);

STATIC_ASSERT(MAPSEC_ROUTE_25 - MAPSEC_ROUTE_1 == 24, OrleansRouteSectionsMustBeConsecutive);

static inline enum Region GetRegionForSectionId(u32 sectionId)
{
    // Orleans: the routes reuse the FRLG sections MAPSEC_ROUTE_1..25; they belong to the Orleans (Hoenn-slot) map
    if (sectionId >= MAPSEC_ROUTE_1 && sectionId <= MAPSEC_ROUTE_25)
        return REGION_HOENN;
    if (sectionId >= KANTO_MAPSEC_START && sectionId < MAPSEC_SPECIAL_AREA)
        return REGION_KANTO;
    return REGION_HOENN;
}

static inline enum Region GetCurrentRegion(void)
{
    return GetRegionForSectionId(gMapHeader.regionMapSectionId);
}

#endif // GUARD_REGIONS_H
