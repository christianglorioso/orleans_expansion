Route23_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route23_OnTransitionPG
	map_script MAP_SCRIPT_ON_LOAD, Route23_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route23_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_HIKER, Route23_Text_Route23HikerIntro, Route23_Text_Route23HikerDefeat
	msgbox Route23_Text_Route23HikerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer5::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_RUIN_MANIAC, Route23_Text_Route23RuinManiacIntro, Route23_Text_Route23RuinManiacDefeat
	msgbox Route23_Text_Route23RuinManiacAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_PICNICKER, Route23_Text_Route23PicnickerIntro, Route23_Text_Route23PicnickerDefeat
	msgbox Route23_Text_Route23PicnickerAfter, MSGBOX_AUTOCLOSE
	end

Route23_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE23_BLACK_BELT, Route23_Text_Route23BlackBeltIntro, Route23_Text_Route23BlackBeltDefeat
	msgbox Route23_Text_Route23BlackBeltAfter, MSGBOX_AUTOCLOSE
	end

Route23_Text_Route23HikerIntro:
	.string "The dust's gone, finally. The\nplains are mine again.$"

Route23_Text_Route23HikerDefeat:
	.string "Dust to dust.$"

Route23_Text_Route23HikerAfter:
	.string "The salt mine's north-east. Don't\ngo in without a light.$"

Route23_Text_Route23RuinManiacIntro:
	.string "The storm uncovered an old wall.\nI'm guarding it. Fight me!$"

Route23_Text_Route23RuinManiacDefeat:
	.string "Buried.$"

Route23_Text_Route23RuinManiacAfter:
	.string "The wall sings when the wind\nhits it. Like a flute.$"

Route23_Text_Route23PicnickerIntro:
	.string "Grass grows back through dust.\nI came to watch it.$"

Route23_Text_Route23PicnickerDefeat:
	.string "Pressed flat.$"

Route23_Text_Route23PicnickerAfter:
	.string "A shadow crossed the whole sky.\nI felt it in my teeth.$"

Route23_Text_Route23BlackBeltIntro:
	.string "The storm's lifted. My training\ncan resume. Spar with me!$"

Route23_Text_Route23BlackBeltDefeat:
	.string "Sparred out.$"

Route23_Text_Route23BlackBeltAfter:
	.string "Cleaner air makes better\ntraining.$"

@ --- end route trainers ---

Route23_OnTransitionPG:
	call Route23_EventScript_StoryWeather
	end

@ weather (weather_plan.py): sandstorm until Rayquaza lifts the dust storms, then clear. Runs from OnTransition, before the weather starts.
Route23_EventScript_StoryWeather:
	goto_if_unset FLAG_DUST_STORMS_LIFTED, Route23_EventScript_StoryWeatherDone
	setweather WEATHER_NONE
Route23_EventScript_StoryWeatherDone:
	return

@ Bloodmoon Ursaluna's lair (Route23_BloodmoonArroyo, story/Route23_BloodmoonArroyo.inc): the arroyo's way in is the cleft in the north scrub (22-23, rows 0-2),
@ sealed in map.bin; from story 45 the generated Route23_EventScript_StateUrsalunaOpen swaps the open look in on load and arms the entrance trigger
@ (FLAG_TEMP_1, cleared on every map load, so a sealed way never has a live trigger).


Route23_EventScript_LairEnter::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE23_BLOODMOON_ARROYO, 10, 13
	waitstate
	end

Route23_Movement_LairFaceUp:
	face_up
	step_end

@ Batch-2 legendary lairs' ways in (story_data_lairs.py, build.py gates()): each is sealed in map.bin; from story 45 the generated
@ Route23_EventScript_State<Name>Open swaps the open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load,
@ so a sealed way never has a live trigger). Entering = LairEnter<Name>; leaving = the lair's Exit script.

Route23_EventScript_LairEnterAzelf::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE23_UNFAILING_SPRING, 10, 13
	waitstate
	end

Route23_EventScript_LairEnterLandorus::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route23_Movement_LairFaceDown
	waitmovement 0
	warp MAP_ROUTE23_BOUNTIFUL_FIELD, 10, 2
	waitstate
	end

Route23_Movement_LairFaceDown:
	face_down
	step_end

@ --- lair gates (tools/mapgen/lair_gates.py; generated, do not edit) begin ---

@ The lairs' ways in (story_data_lairs.GATES): each opens only when its trophy is complete and the post-game has begun; re-checked on every map load.
Route23_OnLoad:
	setvar VAR_0x8004, ACH_PSYCHIC_FURY
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route23_EventScript_LairOpenUrsaluna
	setvar VAR_0x8004, ACH_MIST_WEAVER
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route23_EventScript_LairOpenAzelf
	setvar VAR_0x8004, ACH_SANDSTORM_CALLER
	call LairGate_EventScript_Check
	call_if_eq VAR_RESULT, TRUE, Route23_EventScript_LairOpenLandorus
	end

Route23_EventScript_LairOpenUrsaluna:
	call Route23_EventScript_StateUrsalunaOpen
	setflag FLAG_TEMP_1
	return

Route23_EventScript_LairOpenAzelf:
	call Route23_EventScript_StateAzelfOpen
	setflag FLAG_TEMP_2
	return

Route23_EventScript_LairOpenLandorus:
	call Route23_EventScript_StateLandorusOpen
	setflag FLAG_TEMP_3
	return

Route23_EventScript_LairSealUrsaluna::
	goto_if_set FLAG_TEMP_1, Route23_EventScript_LairSealEnd
	msgbox Route23_Text_LairSealUrsaluna, MSGBOX_SIGN
	end

Route23_Text_LairSealUrsaluna:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Deal 10,000 super-effective\n"
	.string "damage with Psychic moves.$"

Route23_EventScript_LairSealAzelf::
	goto_if_set FLAG_TEMP_2, Route23_EventScript_LairSealEnd
	msgbox Route23_Text_LairSealAzelf, MSGBOX_SIGN
	end

Route23_Text_LairSealAzelf:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Set Misty Terrain 10 times in\n"
	.string "the Battle Frontier.$"

Route23_EventScript_LairSealLandorus::
	goto_if_set FLAG_TEMP_3, Route23_EventScript_LairSealEnd
	msgbox Route23_Text_LairSealLandorus, MSGBOX_SIGN
	end

Route23_Text_LairSealLandorus:
	.string "Sealed until the game is beaten,\n"
	.string "and it needs a trophy:\p"
	.string "Set Sandstorm 25 times in the\n"
	.string "Battle Frontier.$"

Route23_EventScript_LairSealEnd:
	end

@ --- lair gates end ---
