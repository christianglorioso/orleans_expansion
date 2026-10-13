LutinsHollow_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LutinsHollow_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, LutinsHollow_OnFrameTable
	.byte 0

@ Lutin's Hollow (Chapter 6). Story: 27 arrived (this frame script, once: VAR_HOLLOW_ARRIVAL), 28 Jayden battle 4 and Wren's song (the pair
@ stand by the south pools while the story is 27; talk to either), 29 Lutin beaten (gym), 30 the cypress-wood charm (Old Water).
@ The gym door's only approach cell (25, 7) is held by Lutin's pupil until story 28, so the scene cannot be skipped.

LutinsHollow_OnTransition:
	setflag FLAG_VISITED_LUTINS_HOLLOW
	setflag FLAG_HIDE_HOLLOW_JAYDEN
	setflag FLAG_HIDE_HOLLOW_WREN
	setflag FLAG_HIDE_HOLLOW_GYM_USHER
	call_if_eq VAR_ORLEANS_STORY, 27, LutinsHollow_EventScript_ShowSingers
	call_if_lt VAR_ORLEANS_STORY, 28, LutinsHollow_EventScript_ShowUsher
	end

LutinsHollow_EventScript_ShowSingers:
	clearflag FLAG_HIDE_HOLLOW_JAYDEN
	clearflag FLAG_HIDE_HOLLOW_WREN
	return

LutinsHollow_EventScript_ShowUsher:
	clearflag FLAG_HIDE_HOLLOW_GYM_USHER
	return

LutinsHollow_OnFrameTable:
	map_script_2 VAR_HOLLOW_ARRIVAL, 0, LutinsHollow_EventScript_Arrival
	.2byte 0

@ The first time in (needs the brothers' verse, story >= 26: a debug warp below that plays nothing and keeps the scene armed).
@ Respawn moves to the hollow's tree Center (set once here; the Center sets it again on entry).
LutinsHollow_EventScript_Arrival::
	goto_if_lt VAR_ORLEANS_STORY, 26, LutinsHollow_EventScript_ArrivalSkip
	lockall
	setvar VAR_HOLLOW_ARRIVAL, 1
	setrespawn HEAL_LOCATION_LUTINS_HOLLOW
	call_if_eq VAR_ORLEANS_STORY, 26, LutinsHollow_EventScript_SetStory27
	call_if_eq VAR_ORLEANS_STORY, 27, LutinsHollow_EventScript_AddSingers
	msgbox LutinsHollow_Text_Arrival1, MSGBOX_DEFAULT
	msgbox LutinsHollow_Text_Arrival2, MSGBOX_DEFAULT
	releaseall
	end

LutinsHollow_EventScript_ArrivalSkip:
	end

LutinsHollow_EventScript_SetStory27:
	setvar VAR_ORLEANS_STORY, 27
	return

LutinsHollow_EventScript_AddSingers:
	clearflag FLAG_HIDE_HOLLOW_JAYDEN
	clearflag FLAG_HIDE_HOLLOW_WREN
	addobject LOCALID_LUTINS_HOLLOW_JAYDEN
	addobject LOCALID_LUTINS_HOLLOW_WREN
	return

@ ---------------------------------------------------------------- 6.3 Jayden battle 4 and Wren's song (story 27 -> 28)
LutinsHollow_EventScript_Jayden::
	lock
	faceplayer
	goto LutinsHollow_EventScript_Singers

LutinsHollow_EventScript_Wren::
	lock
	faceplayer
	goto LutinsHollow_EventScript_Singers

LutinsHollow_EventScript_Singers:
	msgbox LutinsHollow_Text_Song1, MSGBOX_DEFAULT
	msgbox LutinsHollow_Text_Song2, MSGBOX_DEFAULT
	msgbox LutinsHollow_Text_Song3, MSGBOX_DEFAULT
	msgbox LutinsHollow_Text_JaydenChallenge, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_STARTER_MON, 0, LutinsHollow_EventScript_BattleJaydenChikorita
	call_if_eq VAR_STARTER_MON, 1, LutinsHollow_EventScript_BattleJaydenFuecoco
	call_if_eq VAR_STARTER_MON, 2, LutinsHollow_EventScript_BattleJaydenTotodile
	msgbox LutinsHollow_Text_JaydenAfter, MSGBOX_DEFAULT
	msgbox LutinsHollow_Text_WrenAfter, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_ORLEANS_STORY, 27, LutinsHollow_EventScript_SetStory28
	setflag FLAG_HIDE_HOLLOW_JAYDEN
	setflag FLAG_HIDE_HOLLOW_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_LUTINS_HOLLOW_JAYDEN
	removeobject LOCALID_LUTINS_HOLLOW_WREN
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	release
	end

LutinsHollow_EventScript_SetStory28:
	setvar VAR_ORLEANS_STORY, 28
	@ the pupil leaves the gym door with the scene (not only on the next map load)
	setflag FLAG_HIDE_HOLLOW_GYM_USHER
	removeobject LOCALID_LUTINS_HOLLOW_GYM_USHER
	return

@ a variant per starter (like Route 3 and the refinery); a blackout between the song and the end of the battle skips what is done
LutinsHollow_EventScript_BattleJaydenChikorita:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_HOLLOW_CHIKORITA, LutinsHollow_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_HOLLOW_CHIKORITA, LutinsHollow_Text_JaydenDefeat
	return

LutinsHollow_EventScript_BattleJaydenFuecoco:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_HOLLOW_FUECOCO, LutinsHollow_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_HOLLOW_FUECOCO, LutinsHollow_Text_JaydenDefeat
	return

LutinsHollow_EventScript_BattleJaydenTotodile:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_HOLLOW_TOTODILE, LutinsHollow_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_HOLLOW_TOTODILE, LutinsHollow_Text_JaydenDefeat
	return

LutinsHollow_EventScript_JaydenDone:
	return

@ ---------------------------------------------------------------- the gym door's pupil (until story 28)
LutinsHollow_EventScript_GymUsher::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 28, LutinsHollow_EventScript_GymUsherOpen
	msgbox LutinsHollow_Text_GymUsher, MSGBOX_DEFAULT
	release
	end

LutinsHollow_EventScript_GymUsherOpen:
	msgbox LutinsHollow_Text_GymUsherOpen, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
LutinsHollow_Text_Arrival1:
	.string "The road narrows into a lane of\n"
	.string "moss. Cypress knees, hung with\p"
	.string "grey beards, close overhead.\n"
	.string "The air turns green and still.$"

LutinsHollow_Text_Arrival2:
	.string "LUTIN'S HOLLOW. Somewhere a bell\n"
	.string "rings, though nothing's ringing.\p"
	.string "By the south pools, two voices:\n"
	.string "one singing, one pretending not\p"
	.string "to listen.$"

LutinsHollow_Text_Song1:
	.string "WREN: ...the Long One lay down in\n"
	.string "the river bed, and the people\p"
	.string "feared. The word they carved was\n"
	.string "never 'low'.$"

LutinsHollow_Text_Song2:
	.string "WREN: ...'laid down to guard.' To\n"
	.string "guard, JAYDEN. The river, the\p"
	.string "people, the ones too small to\n"
	.string "stand against the water.$"

LutinsHollow_Text_Song3:
	.string "JAYDEN: ...That's not how RITA\n"
	.string "tells it. She says the Long One\p"
	.string "drowned the city and slept. She\n"
	.string "says it was a punishment.\p"
	.string "WREN: Who's telling it better?\n"
	.string "The one who needs you angry?$"

LutinsHollow_Text_JaydenChallenge:
	.string "JAYDEN: ...Don't. Don't say it.\n"
	.string "You're here, so we fight.\p"
	.string "I need to know which of us is\n"
	.string "right. Hands up, {PLAYER}.$"

LutinsHollow_Text_JaydenDefeat:
	.string "JAYDEN: ...I didn't want to win.\n"
	.string "I only wanted it to mean something.$"

LutinsHollow_Text_JaydenAfter:
	.string "JAYDEN: The refinery. The camp. The\n"
	.string "Ward. I kept telling myself it was\p"
	.string "for the town. It was for her.\n"
	.string "...I have to think. Alone.$"

LutinsHollow_Text_WrenAfter:
	.string "WREN: {PLAYER}, LUTIN is inside,\n"
	.string "behind the moss. I'll stay with\p"
	.string "JAYDEN. Hers is the sixth verse.\n"
	.string "Two more wait after it.$"

LutinsHollow_Text_GymUsher:
	.string "PUPIL: The gym's closed to anyone\n"
	.string "who hasn't heard the singers at\p"
	.string "the south pools. Listen first.\n"
	.string "The hollow likes to be listened to.$"

LutinsHollow_Text_GymUsherOpen:
	.string "PUPIL: The hollow has been listened\nto. The gym is open. Mind the moss.$"

