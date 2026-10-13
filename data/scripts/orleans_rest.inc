@ Orleans: the rest spots in every healer (Pokemon Centers, the Camp Cocodrie nurse cabin, the Old Water healer and rest house). A bed, cot or
@ bench with a sign-type bg event running Common_EventScript_RestSpot (generated into the rooms by tools/mapgen/build_interior.py).
@ "Rest until... MORNING / DAY / EVENING / NIGHT / CANCEL" skips the in-game clock (fake RTC, one day = 72 minutes of play) forward to the next
@ time of day's first hour (the engine's own boundaries, include/constants/rtc.h: MORNING_HOUR_BEGIN, DAY_HOUR_BEGIN, ...), heals the party
@ and fades back in. Choosing the time of day it already is changes nothing. The multichoice index equals the TimeOfDay enum value
@ (0 morning, 1 day, 2 evening, 3 night), which OrleansSvc_IsTimeOfDay compares with VAR_0x8004.
Common_EventScript_RestSpot::
	lock
	msgbox Common_Text_RestAsk, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 5, 0, DYN_MULTICHOICE_CB_NONE, Common_Text_RestMorning, Common_Text_RestDay, Common_Text_RestEvening, Common_Text_RestNight, Common_Text_RestCancel
	switch VAR_RESULT
	case 0, Common_EventScript_RestUntilMorning
	case 1, Common_EventScript_RestUntilDay
	case 2, Common_EventScript_RestUntilEvening
	case 3, Common_EventScript_RestUntilNight
	release
	end

Common_EventScript_RestUntilMorning:
	setvar VAR_0x8004, 0
	special OrleansSvc_IsTimeOfDay
	goto_if_eq VAR_RESULT, TRUE, Common_EventScript_RestAlready
	bufferstring STR_VAR_1, Common_Text_RestWordMorning
	call Common_EventScript_RestFadeOut
	fwdtime MORNING_HOUR_BEGIN, 0
	goto Common_EventScript_RestWakeUp

Common_EventScript_RestUntilDay:
	setvar VAR_0x8004, 1
	special OrleansSvc_IsTimeOfDay
	goto_if_eq VAR_RESULT, TRUE, Common_EventScript_RestAlready
	bufferstring STR_VAR_1, Common_Text_RestWordDay
	call Common_EventScript_RestFadeOut
	fwdtime DAY_HOUR_BEGIN, 0
	goto Common_EventScript_RestWakeUp

Common_EventScript_RestUntilEvening:
	setvar VAR_0x8004, 2
	special OrleansSvc_IsTimeOfDay
	goto_if_eq VAR_RESULT, TRUE, Common_EventScript_RestAlready
	bufferstring STR_VAR_1, Common_Text_RestWordEvening
	call Common_EventScript_RestFadeOut
	fwdtime EVENING_HOUR_BEGIN, 0
	goto Common_EventScript_RestWakeUp

Common_EventScript_RestUntilNight:
	setvar VAR_0x8004, 3
	special OrleansSvc_IsTimeOfDay
	goto_if_eq VAR_RESULT, TRUE, Common_EventScript_RestAlready
	bufferstring STR_VAR_1, Common_Text_RestWordNight
	call Common_EventScript_RestFadeOut
	fwdtime NIGHT_HOUR_BEGIN, 0
	goto Common_EventScript_RestWakeUp

Common_EventScript_RestAlready:
	msgbox Common_Text_RestAlready, MSGBOX_DEFAULT
	release
	end

Common_EventScript_RestFadeOut:
	fadescreen FADE_TO_BLACK
	return

Common_EventScript_RestWakeUp:
	special HealPlayerParty
	callnative UpdateFollowingPokemon
	playfanfare MUS_HEAL
	waitfanfare
	fadescreen FADE_FROM_BLACK
	msgbox Common_Text_RestDone, MSGBOX_DEFAULT
	release
	end

Common_Text_RestAsk:
	.string "A place to rest, free of charge.\n"
	.string "Rest until when?$"

Common_Text_RestMorning:
	.string "MORNING$"

Common_Text_RestDay:
	.string "DAY$"

Common_Text_RestEvening:
	.string "EVENING$"

Common_Text_RestNight:
	.string "NIGHT$"

Common_Text_RestCancel:
	.string "CANCEL$"

Common_Text_RestWordMorning:
	.string "morning$"

Common_Text_RestWordDay:
	.string "day$"

Common_Text_RestWordEvening:
	.string "evening$"

Common_Text_RestWordNight:
	.string "night$"

Common_Text_RestAlready:
	.string "It is already that time of day.\n"
	.string "There is no need to rest.$"

Common_Text_RestDone:
	.string "You rested until {STR_VAR_1}.\p"
	.string "Your POKéMON are fully rested!$"
