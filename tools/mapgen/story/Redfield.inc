Redfield_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Redfield_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Redfield_OnFrameTable
	.byte 0

@ Redfield (Chapter 7). Story: 31 arrived (this frame script, once: VAR_REDFIELD_ARRIVAL; from 29 or 30, the charm is optional), 32 Rita's
@ Mega Chandelure beaten at the yard gate, 33 Cayenne beaten (Redfield_Gym), 34 Isaac's raid defended (OldWater).
@ The mill yard trial (by day only): six mirrors in three pairs serve three sundials, lit in order (OrleansSvc_TurnMirror / MirrorCheck in
@ src/orleans_services.c). The shutter on the gym door's only approach cell (37, 13) goes up when all three burn (FLAG_REDFIELD_MILL_OPEN).
@ Wren waits outside the mill door while the story is 33 (the first return to town plays the call: VAR_REDFIELD_RAID_CALL).

Redfield_OnTransition:
	setflag FLAG_HIDE_REDFIELD_RITA
	setflag FLAG_HIDE_REDFIELD_WREN
	call_if_eq VAR_ORLEANS_STORY, 31, Redfield_EventScript_ShowRita
	call_if_eq VAR_ORLEANS_STORY, 33, Redfield_EventScript_ShowWren
	end

Redfield_EventScript_ShowRita:
	clearflag FLAG_HIDE_REDFIELD_RITA
	return

Redfield_EventScript_ShowWren:
	clearflag FLAG_HIDE_REDFIELD_WREN
	return

Redfield_OnFrameTable:
	map_script_2 VAR_REDFIELD_ARRIVAL, 0, Redfield_EventScript_Arrival
	map_script_2 VAR_REDFIELD_RAID_CALL, 0, Redfield_EventScript_RaidCall
	.2byte 0

@ ---------------------------------------------------------------- 7.1 the arrival (story 29/30 -> 31)
@ The first time in (needs the sixth badge, story >= 29: a debug warp below that plays nothing and keeps the scene armed).
Redfield_EventScript_Arrival::
	goto_if_lt VAR_ORLEANS_STORY, 29, Redfield_EventScript_ArrivalSkip
	lockall
	setvar VAR_REDFIELD_ARRIVAL, 1
	setrespawn HEAL_LOCATION_REDFIELD
	call_if_eq VAR_ORLEANS_STORY, 29, Redfield_EventScript_SetStory31
	call_if_eq VAR_ORLEANS_STORY, 30, Redfield_EventScript_SetStory31
	msgbox Redfield_Text_Arrival1, MSGBOX_DEFAULT
	goto_if_eq VAR_ORLEANS_STORY, 31, Redfield_EventScript_ArrivalRita
	releaseall
	end

Redfield_EventScript_ArrivalRita:
	msgbox Redfield_Text_Arrival2, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_ArrivalSkip:
	end

Redfield_EventScript_SetStory31:
	setvar VAR_ORLEANS_STORY, 31
	clearflag FLAG_HIDE_REDFIELD_RITA
	addobject LOCALID_REDFIELD_RITA
	return

@ ---------------------------------------------------------------- 7.3 Rita at the yard gate (story 31 -> 32)
@ A coord trigger on the two cells inside the gate (only while the story is 31) and Rita's own script both lead to the battle.
Redfield_EventScript_RitaGate::
	lockall
	goto_if_ne VAR_ORLEANS_STORY, 31, Redfield_EventScript_RitaNotNow
	applymovement LOCALID_REDFIELD_RITA, Redfield_Movement_RitaFacePlayer
	waitmovement 0
	goto Redfield_EventScript_RitaBattle

Redfield_EventScript_RitaNotNow:
	releaseall
	end

Redfield_Movement_RitaFacePlayer:
	face_player
	step_end

Redfield_EventScript_Rita::
	lock
	faceplayer
	goto_if_ne VAR_ORLEANS_STORY, 31, Redfield_EventScript_RitaGoneTalk
	goto Redfield_EventScript_RitaBattle

Redfield_EventScript_RitaGoneTalk:
	msgbox Redfield_Text_RitaGone, MSGBOX_DEFAULT
	release
	end

Redfield_EventScript_RitaBattle:
	msgbox Redfield_Text_RitaIntro1, MSGBOX_DEFAULT
	msgbox Redfield_Text_RitaIntro2, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_ORLEANS_RITA_REDFIELD, Redfield_Text_RitaDefeat
	msgbox Redfield_Text_RitaAfter, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_ORLEANS_STORY, 31, Redfield_EventScript_SetStory32
	setflag FLAG_HIDE_REDFIELD_RITA
	setflag FLAG_REDFIELD_RITA_BEATEN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_REDFIELD_RITA
	fadescreen FADE_FROM_BLACK
	releaseall
	end

Redfield_EventScript_SetStory32:
	setvar VAR_ORLEANS_STORY, 32
	return

@ ---------------------------------------------------------------- Cayenne outside the mill
Redfield_EventScript_Cayenne::
	lock
	faceplayer
	goto_if_set FLAG_REDFIELD_MILL_OPEN, Redfield_EventScript_CayenneOpen
	goto_if_lt VAR_ORLEANS_STORY, 32, Redfield_EventScript_CayenneWait
	goto_if_set FLAG_BADGE07_GET, Redfield_EventScript_CayenneAfter
	msgbox Redfield_Text_CayenneTrial, MSGBOX_DEFAULT
	release
	end

Redfield_EventScript_CayenneOpen:
	goto_if_set FLAG_BADGE07_GET, Redfield_EventScript_CayenneAfter
	msgbox Redfield_Text_CayenneOpen, MSGBOX_DEFAULT
	release
	end

Redfield_EventScript_CayenneWait:
	msgbox Redfield_Text_CayenneWait, MSGBOX_DEFAULT
	release
	end

Redfield_EventScript_CayenneAfter:
	msgbox Redfield_Text_CayenneAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- 7.4 the mill yard trial: mirrors (by day only)
@ A..F = mirrors 0..5; each mirror has two sign cells (the mirror is 1 wide, 2 tall).
Redfield_EventScript_MirrorA1::
Redfield_EventScript_MirrorA2::
	setvar VAR_0x8004, 0
	goto Redfield_EventScript_MirrorTurn

Redfield_EventScript_MirrorB1::
Redfield_EventScript_MirrorB2::
	setvar VAR_0x8004, 1
	goto Redfield_EventScript_MirrorTurn

Redfield_EventScript_MirrorC1::
Redfield_EventScript_MirrorC2::
	setvar VAR_0x8004, 2
	goto Redfield_EventScript_MirrorTurn

Redfield_EventScript_MirrorD1::
Redfield_EventScript_MirrorD2::
	setvar VAR_0x8004, 3
	goto Redfield_EventScript_MirrorTurn

Redfield_EventScript_MirrorE1::
Redfield_EventScript_MirrorE2::
	setvar VAR_0x8004, 4
	goto Redfield_EventScript_MirrorTurn

Redfield_EventScript_MirrorF1::
Redfield_EventScript_MirrorF2::
	setvar VAR_0x8004, 5
	goto Redfield_EventScript_MirrorTurn


Redfield_EventScript_MirrorTurn:
	lockall
	goto_if_set FLAG_REDFIELD_MILL_OPEN, Redfield_EventScript_MirrorDone
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Redfield_EventScript_MirrorNight
	special OrleansSvc_TurnMirror
	goto_if_eq VAR_RESULT, 4, Redfield_EventScript_MirrorLocked
	call_if_eq VAR_RESULT, 0, Redfield_EventScript_Facing0
	call_if_eq VAR_RESULT, 1, Redfield_EventScript_Facing1
	call_if_eq VAR_RESULT, 2, Redfield_EventScript_Facing2
	call_if_eq VAR_RESULT, 3, Redfield_EventScript_Facing3
	special OrleansSvc_MirrorRight
	call_if_eq VAR_RESULT, TRUE, Redfield_EventScript_Glint
	call_if_eq VAR_RESULT, FALSE, Redfield_EventScript_NoGlint
	special OrleansSvc_MirrorCheck
	goto_if_ne VAR_RESULT, 0, Redfield_EventScript_DialsLit
	goto_if_eq VAR_0x8005, 1, Redfield_EventScript_NotReady
	releaseall
	end

Redfield_EventScript_Facing0:
	msgbox Redfield_Text_Facing0, MSGBOX_DEFAULT
	return

Redfield_EventScript_Facing1:
	msgbox Redfield_Text_Facing1, MSGBOX_DEFAULT
	return

Redfield_EventScript_Facing2:
	msgbox Redfield_Text_Facing2, MSGBOX_DEFAULT
	return

Redfield_EventScript_Facing3:
	msgbox Redfield_Text_Facing3, MSGBOX_DEFAULT
	return

Redfield_EventScript_Glint:
	msgbox Redfield_Text_Glint, MSGBOX_DEFAULT
	return

Redfield_EventScript_NoGlint:
	msgbox Redfield_Text_NoGlint, MSGBOX_DEFAULT
	return

@ the highest newly lit dial gives the message; the third opens the mill (the shutter goes up for good)
Redfield_EventScript_DialsLit:
	goto_if_set FLAG_REDFIELD_SUN3, Redfield_EventScript_MillOpens
	goto_if_set FLAG_REDFIELD_SUN2, Redfield_EventScript_Dial2Lit
	msgbox Redfield_Text_Dial1Lit, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_Dial2Lit:
	msgbox Redfield_Text_Dial2Lit, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_MillOpens:
	msgbox Redfield_Text_AllLit, MSGBOX_DEFAULT
	setflag FLAG_REDFIELD_MILL_OPEN
	removeobject LOCALID_REDFIELD_SHUTTER_1
	releaseall
	end

Redfield_EventScript_NotReady:
	msgbox Redfield_Text_NotReady, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_MirrorNight:
	msgbox Redfield_Text_MirrorNight, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_MirrorDone:
	msgbox Redfield_Text_MirrorDone, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_MirrorLocked:
	msgbox Redfield_Text_MirrorLocked, MSGBOX_DEFAULT
	releaseall
	end

@ the two sundials the corridor reaches (middle = the second dial, south = the first); the north-west dial is only seen
Redfield_EventScript_DialMiddle1::
Redfield_EventScript_DialMiddle2::
	lockall
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Redfield_EventScript_DialNight
	goto_if_set FLAG_REDFIELD_SUN2, Redfield_EventScript_DialLit
	goto Redfield_EventScript_DialDark

Redfield_EventScript_DialSouth1::
Redfield_EventScript_DialSouth2::
	lockall
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Redfield_EventScript_DialNight
	goto_if_set FLAG_REDFIELD_SUN1, Redfield_EventScript_DialLit
	goto Redfield_EventScript_DialDark

Redfield_EventScript_DialLit:
	msgbox Redfield_Text_DialLit, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_DialDark:
	msgbox Redfield_Text_DialDark, MSGBOX_DEFAULT
	releaseall
	end

Redfield_EventScript_DialNight:
	msgbox Redfield_Text_DialNight, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- 7.6 the call to the Old Water (story 33)
@ The first time the player is back in town after the badge: Wren runs up and takes them to the raid (the Old Water's frame script plays it).
@ VAR_OLD_WATER_RAID 1 arms the scene; it stays 1 until the raid is defended, so a blackout replays it.
Redfield_EventScript_RaidCall::
	goto_if_ne VAR_ORLEANS_STORY, 33, Redfield_EventScript_RaidCallSkip
	lockall
	setvar VAR_REDFIELD_RAID_CALL, 1
	msgbox Redfield_Text_WrenCall1, MSGBOX_DEFAULT
	msgbox Redfield_Text_WrenCall2, MSGBOX_DEFAULT
	msgbox Redfield_Text_WrenCall3, MSGBOX_DEFAULT
	goto Redfield_EventScript_GoToOldWater

Redfield_EventScript_RaidCallSkip:
	end

Redfield_EventScript_Wren::
	lockall
	goto_if_ne VAR_ORLEANS_STORY, 33, Redfield_EventScript_WrenIdle
	msgbox Redfield_Text_WrenRetry, MSGBOX_DEFAULT
	goto Redfield_EventScript_GoToOldWater

Redfield_EventScript_WrenIdle:
	releaseall
	end

Redfield_EventScript_GoToOldWater:
	closemessage
	setvar VAR_OLD_WATER_RAID, 1
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER, 22, 32
	waitstate
	releaseall
	end

@ ---------------------------------------------------------------- text
Redfield_Text_Arrival1:
	.string "Sugar and smoke. REDFIELD's cane\n"
	.string "runs to the sky, and a brick chimney\p"
	.string "stands over the mill yard, its\n"
	.string "fence flashing with mirrors.$"

Redfield_Text_Arrival2:
	.string "A woman in a grey coat waits by the\n"
	.string "yard gate, a pale flame at her\p"
	.string "shoulder. Her CHANDELURE drifts\n"
	.string "like a lit lantern.$"

Redfield_Text_RitaIntro1:
	.string "RITA: Another traveler for the mill.\n"
	.string "I keep its books. Mind the figures.\p"
	.string "RITA: The boy said you'd come. He\n"
	.string "says you listen to the old songs.$"

Redfield_Text_RitaIntro2:
	.string "RITA: Songs are how this country\n"
	.string "drowned. I'd rather you didn't sing.\p"
	.string "RITA: Let's see what you carry.\n"
	.string "My CHANDELURE holds a stone.$"

Redfield_Text_RitaDefeat:
	.string "RITA: ...The flame bent. It never\n"
	.string "bends.$"

Redfield_Text_RitaAfter:
	.string "RITA: Go on. The sun will test you\n"
	.string "better than I did.\p"
	.string "RITA: I'd have liked to keep the\n"
	.string "mill's books in peace.\p"
	.string "She leaves through the gate, her\n"
	.string "lantern-flame trailing behind.$"

Redfield_Text_RitaGone:
	.string "Nobody stands at the yard gate now.$"

Redfield_Text_CayenneOpen:
	.string "CAYENNE: Shutter's up. You read the\n"
	.string "sun. Come in and show me the rest.$"

Redfield_Text_CayenneWait:
	.string "CAYENNE: RITA keeps the yard gate.\n"
	.string "Settle that first. I'll wait.$"

Redfield_Text_CayenneTrial:
	.string "CAYENNE: My mill runs on sunlight,\n"
	.string "and so does my gym.\p"
	.string "CAYENNE: Three sundials, six mirrors\n"
	.string "Light them in order, by day.\p"
	.string "CAYENNE: The keeper in the shotgun\n"
	.string "house knows the order, not angles.$"

Redfield_Text_CayenneAfter:
	.string "CAYENNE: The shutter's up and the\n"
	.string "seventh verse is told. Go on.$"

Redfield_Text_MirrorNight:
	.string "The mirrors only throw lamplight\n"
	.string "after dark. Come back by day.$"

Redfield_Text_MirrorDone:
	.string "The mirrors stay put. The mill is\n"
	.string "open.$"

Redfield_Text_MirrorLocked:
	.string "This mirror is fixed in place, hot\n"
	.string "from its dial's flame.$"

Redfield_Text_Facing0:
	.string "The mirror turns to face north-east.$"

Redfield_Text_Facing1:
	.string "The mirror turns to face north-west.$"

Redfield_Text_Facing2:
	.string "The mirror turns to face south-west.$"

Redfield_Text_Facing3:
	.string "The mirror turns to face south-east.$"

Redfield_Text_Glint:
	.string "A bar of light leaps off the glass,\n"
	.string "west across the yard.$"

Redfield_Text_NoGlint:
	.string "The glass shows only sky.$"

Redfield_Text_Dial1Lit:
	.string "Light lands on the south-east dial.\n"
	.string "Its shadow stands at noon and burns.$"

Redfield_Text_Dial2Lit:
	.string "The middle dial blazes, its needle\n"
	.string "a line of gold.$"

Redfield_Text_AllLit:
	.string "The north-west dial flares, and all\n"
	.string "three burn. Far off, the shutter\p"
	.string "groans upward on its chains.$"

Redfield_Text_NotReady:
	.string "A bar of light finds a dial that is\n"
	.string "not ready. The dial before it must\p"
	.string "burn first.$"

Redfield_Text_DialDark:
	.string "A sundial. Its face is dark, its\n"
	.string "needle shadowless.$"

Redfield_Text_DialLit:
	.string "The sundial's face glows gold. The\n"
	.string "needle's shadow stands at noon.$"

Redfield_Text_DialNight:
	.string "A sundial, cold in the lamplight.$"

Redfield_Text_WrenCall1:
	.string "WREN: There you are! I've run up the\n"
	.string "river since dawn.$"

Redfield_Text_WrenCall2:
	.string "WREN: Smoke over the OLD WATER. Dark\n"
	.string "boats at the landing. ISAAC's.$"

Redfield_Text_WrenCall3:
	.string "WREN: TUPELO can't hold them alone.\n"
	.string "I know a faster boat. Come on!$"

Redfield_Text_WrenRetry:
	.string "WREN: The OLD WATER's burning. Come\n"
	.string "on!$"

