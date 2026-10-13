Route11_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, Route11_OnLoad
	.byte 0

@ --- route trainers (gen_route_trainers.py) ---
Route11_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER_F, Route11_Text_Route11SwimmerFIntro, Route11_Text_Route11SwimmerFDefeat
	msgbox Route11_Text_Route11SwimmerFAfter, MSGBOX_AUTOCLOSE
	end

Route11_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER, Route11_Text_Route11SwimmerIntro, Route11_Text_Route11SwimmerDefeat
	msgbox Route11_Text_Route11SwimmerAfter, MSGBOX_AUTOCLOSE
	end

Route11_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE11_SWIMMER_2, Route11_Text_Route11Swimmer2Intro, Route11_Text_Route11Swimmer2Defeat
	msgbox Route11_Text_Route11Swimmer2After, MSGBOX_AUTOCLOSE
	end

Route11_Text_Route11SwimmerFIntro:
	.string "The water's perfect today. Is\nyour team, though?$"

Route11_Text_Route11SwimmerFDefeat:
	.string "Lost the current.$"

Route11_Text_Route11SwimmerFAfter:
	.string "The lake's colder past the\nsecond bend.$"

Route11_Text_Route11SwimmerIntro:
	.string "I race the ferries. Today\nI race you!$"

Route11_Text_Route11SwimmerDefeat:
	.string "Second place again.$"

Route11_Text_Route11SwimmerAfter:
	.string "Routes 12 and 13 climb into\nthe hills. It's green up there.$"

Route11_Text_Route11Swimmer2Intro:
	.string "Slow down! This is a toll lake.\nThe toll is a battle.$"

Route11_Text_Route11Swimmer2Defeat:
	.string "Toll paid.$"

Route11_Text_Route11Swimmer2After:
	.string "I saw something glow under the\nlilies at dusk. Twice.$"

@ --- end route trainers ---

@ The legendary lair's way in (story_data_lairs.py, build.py gates()): sealed in map.bin; from story 45 the generated Route11_EventScript_StateSuicuneOpen swaps the
@ open look in on load and arms the entrance trigger (FLAG_TEMP_1, cleared on every map load, so a sealed way never has a live trigger).
Route11_OnLoad:
	call_if_ge VAR_ORLEANS_STORY, 45, Route11_EventScript_LairOpen
	end

Route11_EventScript_LairOpen:
	call Route11_EventScript_StateSuicuneOpen
	setflag FLAG_TEMP_1
	return

Route11_EventScript_LairEnter::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route11_Movement_LairFaceUp
	waitmovement 0
	warp MAP_ROUTE11_SUICUNE_ISLE, 10, 13
	waitstate
	end

Route11_Movement_LairFaceUp:
	face_up
	step_end

@ --- mapgen: generated NPC scripts (begin) ---

Route11_EventScript_StateSuicuneOpen::
	setmetatile 28, 20, 0x287, TRUE
	setmetatile 29, 20, 0x289, TRUE
	setmetatile 28, 21, 0x288, FALSE
	setmetatile 29, 21, 0x28A, FALSE
	return

@ --- mapgen: generated NPC scripts (end) ---
