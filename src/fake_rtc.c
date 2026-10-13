#include "global.h"
#include "string_util.h"
#include "strings.h"
#include "text.h"
#include "datetime.h"
#include "rtc.h"
#include "fake_rtc.h"
#include "event_data.h"
#include "script.h"
#include "constants/vars.h"

static void FakeRtc_CalcTimeDifference(struct Time *result, struct SiiRtcInfo *t1, struct Time *t2);

#if OW_USE_FAKE_RTC
static const u8 sFakeRtcMagic[4] = {0x0C, 0x10, 0xC4, 0x5A};
#endif

void FakeRtc_Reset(void)
{
#if OW_USE_FAKE_RTC
    memset(&gSaveBlock3Ptr->fakeRTC, 0, sizeof(gSaveBlock3Ptr->fakeRTC));
    gSaveBlock3Ptr->fakeRTC.year = 0; // offset by gGen3Epoch.year
    gSaveBlock3Ptr->fakeRTC.month = gGen3Epoch.month;
    gSaveBlock3Ptr->fakeRTC.day = gGen3Epoch.day;
    gSaveBlock3Ptr->fakeRTC.dayOfWeek = gGen3Epoch.dayOfWeek;
    memcpy(gSaveBlock3Ptr->fakeRtcMagic, sFakeRtcMagic, sizeof(sFakeRtcMagic));
#endif
}

// Orleans: a save made before the in-game clock existed has no marker (or random bytes) where the clock now lives. Give it a clock that
// reads ORLEANS_START_HOUR on day 0 and reset the local-time offset, VAR_DAYS and the berry timer so the daily/berry updates start clean.
// Called when a saved game is continued; a save that already carries the marker (any save made on the clock build) is left alone.
void FakeRtc_MigrateSave(void)
{
#if OW_USE_FAKE_RTC
    struct SiiRtcInfo *rtc = &gSaveBlock3Ptr->fakeRTC;

    if (memcmp(gSaveBlock3Ptr->fakeRtcMagic, sFakeRtcMagic, sizeof(sFakeRtcMagic)) == 0
     && rtc->month >= 1 && rtc->month <= 12 && rtc->day >= 1 && rtc->day <= 31 && rtc->hour < 24 && rtc->minute < 60 && rtc->second < 60)
        return;

    // the same call a new game makes: clock = day 0, ORLEANS_START_HOUR:00 (sets the fake RTC and the save's local-time offset together)
    RtcCalcLocalTimeOffset(0, ORLEANS_START_HOUR, 0, 0);
    gSaveBlock2Ptr->lastBerryTreeUpdate = gLocalTime;
    VarSet(VAR_DAYS, 0);
#endif
}

struct SiiRtcInfo *FakeRtc_GetCurrentTime(void)
{
#if OW_USE_FAKE_RTC
    return &gSaveBlock3Ptr->fakeRTC;
#else
    return NULL;
#endif
}

void FakeRtc_GetRawInfo(struct SiiRtcInfo *rtc)
{
    struct SiiRtcInfo *fakeRtc = FakeRtc_GetCurrentTime();
    if (fakeRtc != NULL)
        memcpy(rtc, fakeRtc, sizeof(struct SiiRtcInfo));
}

void FakeRtc_TickTimeForward(void)
{
    if (!OW_USE_FAKE_RTC)
        return;

    if (FlagGet(OW_FLAG_PAUSE_TIME))
        return;

    FakeRtc_AdvanceTimeBy(0, 0, 0, FakeRtc_GetSecondsRatio());
}

void FakeRtc_AdvanceTimeBy(u32 days, u32 hours, u32 minutes, u32 seconds)
{
    if (!OW_USE_FAKE_RTC)
        return;

    struct DateTime dateTime;
    struct SiiRtcInfo *rtc = FakeRtc_GetCurrentTime();

    ConvertRtcToDateTime(&dateTime, rtc);
    DateTime_AddSeconds(&dateTime, seconds);
    DateTime_AddMinutes(&dateTime, minutes);
    DateTime_AddHours(&dateTime, hours);
    DateTime_AddDays(&dateTime, days);
    ConvertDateTimeToRtc(rtc, &dateTime);
}

void FakeRtc_ForwardTimeTo(u32 hour, u32 minute, u32 second)
{
    if (!OW_USE_FAKE_RTC)
        return;

    Script_PauseFakeRtc();
    struct Time diff, target;
    struct SiiRtcInfo *fakeRtc = FakeRtc_GetCurrentTime();

    target.hours = hour;
    target.minutes = minute;
    target.seconds = second;

    FakeRtc_CalcTimeDifference(&diff, fakeRtc, &target);
    FakeRtc_AdvanceTimeBy(0, diff.hours, diff.minutes, diff.seconds);
    Script_ResumeFakeRtc();
}

static void FakeRtc_CalcTimeDifference(struct Time *result, struct SiiRtcInfo *t1, struct Time *t2)
{
    result->seconds = t2->seconds - t1->second;
    result->minutes = t2->minutes - t1->minute;
    result->hours = t2->hours - t1->hour;
    result->days = t2->days - t1->day;

    if (result->seconds < 0)
    {
        result->seconds += SECONDS_PER_MINUTE;
        --result->minutes;
    }

    if (result->minutes < 0)
    {
        result->minutes += MINUTES_PER_HOUR;
        --result->hours;
    }

    if (result->hours < 0)
    {
        result->hours += HOURS_PER_DAY;
        --result->days;
    }
}

void FakeRtc_ManuallySetTime(u32 day, u32 hour, u32 minute, u32 second)
{
    FakeRtc_Reset();
    FakeRtc_AdvanceTimeBy(day, hour, minute, second);
}

u32 FakeRtc_GetSecondsRatio(void)
{
    return (OW_ALTERED_TIME_RATIO == GEN_8_PLA)   ? 60 :
           (OW_ALTERED_TIME_RATIO == GEN_9)       ? 20 :
           (OW_ALTERED_TIME_RATIO == TIME_DEBUG)  ?  1 :
                                                     1;
}

STATIC_ASSERT((OW_FLAG_PAUSE_TIME == 0 || OW_USE_FAKE_RTC == TRUE), FakeRtcMustBeTrueToPauseTime);

void Script_PauseFakeRtc(void)
{
    Script_RequestEffects(SCREFF_V1 | SCREFF_SAVE);

    FlagSet(OW_FLAG_PAUSE_TIME);
}

void Script_ResumeFakeRtc(void)
{
    Script_RequestEffects(SCREFF_V1 | SCREFF_SAVE);

    FlagClear(OW_FLAG_PAUSE_TIME);
}

void Script_ToggleFakeRtc(void)
{
    Script_RequestEffects(SCREFF_V1 | SCREFF_SAVE);

    FlagToggle(OW_FLAG_PAUSE_TIME);
}
