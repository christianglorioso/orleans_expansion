LandsEnd_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LandsEnd_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, LandsEnd_OnFrameTable
	.byte 0

@ Land's End (Chapter 8). Story: 35 arrived (this frame script, once: VAR_LANDS_END_ARRIVAL; from 34), 36 Heron beaten (LandsEnd_Gym),
@ 37 Andrew named and Jayden battle 5 (his first Mega), 38 Rayquaza wakes (the dust storms lift: FLAG_DUST_STORMS_LIFTED), 39 the full telling
@ at the Old Water (OldWater_SongHouse). Andrew and Jayden wait in front of the pavilion only while the story is 36: a frame script on
@ VAR_LANDS_END_SCENE plays the scene wherever the player stands (leaving the gym by its door warp, any route), and a blackout in the battle replays it.

LandsEnd_OnTransition:
	setflag FLAG_VISITED_LANDS_END
	setflag FLAG_HIDE_LANDS_END_ANDREW
	setflag FLAG_HIDE_LANDS_END_JAYDEN
	call_if_eq VAR_ORLEANS_STORY, 36, LandsEnd_EventScript_ShowPair
	call_if_ge VAR_ORLEANS_STORY, 33, LandsEnd_EventScript_SetRespawn
	end

@ the respawn moves from story 33 on (Surf lets a player in before the raid). Set here, NOT in the frame script: an effectful
@ command in a frame script that never sets its var re-runs every frame and freezes the player (hotfix 2026-10-13)
LandsEnd_EventScript_SetRespawn:
	setrespawn HEAL_LOCATION_LANDS_END
	return

LandsEnd_EventScript_ShowPair:
	clearflag FLAG_HIDE_LANDS_END_ANDREW
	clearflag FLAG_HIDE_LANDS_END_JAYDEN
	return

LandsEnd_OnFrameTable:
	map_script_2 VAR_LANDS_END_ARRIVAL, 0, LandsEnd_EventScript_Arrival
	map_script_2 VAR_LANDS_END_SCENE, 0, LandsEnd_EventScript_Scene
	.2byte 0

@ ---------------------------------------------------------------- 8.1 arrival (story 34 -> 35); the respawn point moves from story 33 on
@ (Surf lets a player in before the raid: at 33 nothing but the respawn happens and the arrival stays armed, so the scene still plays,
@ and 34 -> 35 is still set, once the raid is done); a debug warp below story 33 plays nothing
LandsEnd_EventScript_Arrival::
	goto_if_lt VAR_ORLEANS_STORY, 33, LandsEnd_EventScript_ArrivalSkip
	goto_if_eq VAR_ORLEANS_STORY, 33, LandsEnd_EventScript_ArrivalEarly
	lockall
	setvar VAR_LANDS_END_ARRIVAL, 1
	setrespawn HEAL_LOCATION_LANDS_END
	call_if_eq VAR_ORLEANS_STORY, 34, LandsEnd_EventScript_SetStory35
	msgbox LandsEnd_Text_Arrival1, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_EventScript_ArrivalSkip:
	end

@ effect-free on purpose (Script_HasNoEffect drops it): the arrival stays armed at 33 without locking the player
LandsEnd_EventScript_ArrivalEarly:
	end

LandsEnd_EventScript_SetStory35:
	setvar VAR_ORLEANS_STORY, 35
	return

@ ---------------------------------------------------------------- 8.4 Andrew and Jayden 5 (36 -> 37), 8.5 Rayquaza wakes (37 -> 38)
LandsEnd_EventScript_Scene::
	goto_if_ne VAR_ORLEANS_STORY, 36, LandsEnd_EventScript_SceneSkip
	lockall
	msgbox LandsEnd_Text_SceneA, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Andrew1, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Telling, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Andrew2, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Andrew3, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Jayden1, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_STARTER_MON, 0, LandsEnd_EventScript_BattleJaydenChikorita
	call_if_eq VAR_STARTER_MON, 1, LandsEnd_EventScript_BattleJaydenFuecoco
	call_if_eq VAR_STARTER_MON, 2, LandsEnd_EventScript_BattleJaydenTotodile
	msgbox LandsEnd_Text_Jayden2, MSGBOX_DEFAULT
	msgbox LandsEnd_Text_Andrew4, MSGBOX_DEFAULT
	closemessage
	setvar VAR_LANDS_END_SCENE, 1
	setvar VAR_ORLEANS_STORY, 37
	setflag FLAG_HIDE_LANDS_END_ANDREW
	setflag FLAG_HIDE_LANDS_END_JAYDEN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_LANDS_END_ANDREW
	removeobject LOCALID_LANDS_END_JAYDEN
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	goto LandsEnd_EventScript_RayquazaWakes

LandsEnd_EventScript_SceneSkip:
	end

@ a variant per starter (like battles 2-4); a blackout between the battle and its end replays the scene
LandsEnd_EventScript_BattleJaydenChikorita:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_LANDS_END_CHIKORITA, LandsEnd_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_LANDS_END_CHIKORITA, LandsEnd_Text_JaydenDefeat
	return

LandsEnd_EventScript_BattleJaydenFuecoco:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_LANDS_END_FUECOCO, LandsEnd_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_LANDS_END_FUECOCO, LandsEnd_Text_JaydenDefeat
	return

LandsEnd_EventScript_BattleJaydenTotodile:
	goto_if_defeated TRAINER_ORLEANS_JAYDEN_LANDS_END_TOTODILE, LandsEnd_EventScript_JaydenDone
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_LANDS_END_TOTODILE, LandsEnd_Text_JaydenDefeat
	return

LandsEnd_EventScript_JaydenDone:
	return

@ 8.5: the storm cinematic; the dust storms on Route 23 lift (the Pointe Rouge gate keys on FLAG_DUST_STORMS_LIFTED); a Pelipper brings Tupelo's note
LandsEnd_EventScript_RayquazaWakes:
	setflag FLAG_PREVENT_OVERWORLD_SPEEDUP @ storm cinematic: 1x (cleared on the next map load)
	fadescreen FADE_TO_WHITE
	playse SE_THUNDER
	waitse
	fadescreen FADE_FROM_WHITE
	msgbox LandsEnd_Text_Storm1, MSGBOX_DEFAULT
	setflag FLAG_DUST_STORMS_LIFTED
	call_if_eq VAR_ORLEANS_STORY, 37, LandsEnd_EventScript_SetStory38
	msgbox LandsEnd_Text_Note, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER_SONG_HOUSE, 9, 12
	waitstate
	releaseall
	end

LandsEnd_EventScript_SetStory38:
	setvar VAR_ORLEANS_STORY, 38
	return

LandsEnd_EventScript_Andrew::
	msgbox LandsEnd_Text_AndrewIdle, MSGBOX_NPC
	end

LandsEnd_EventScript_Jayden::
	msgbox LandsEnd_Text_JaydenIdle, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- text
LandsEnd_Text_Arrival1:
	.string "LAND'S END. A town on pilings, the\n"
	.string "tide slapping under the boards.\p"
	.string "Rain drums on a pavilion roof to\n"
	.string "the south: HERON's.$"

LandsEnd_Text_SceneA:
	.string "The pavilion's door stands open. Two\n"
	.string "figures wait before it: a man in a\p"
	.string "black coat, and JAYDEN.$"

LandsEnd_Text_Andrew1:
	.string "ANDREW: My name is ANDREW. I spoke\n"
	.string "in CRESCENT CITY. You were there.\p"
	.string "ANDREW: Eight Singers, eight verses.\n"
	.string "Let's hear the telling whole.$"

LandsEnd_Text_Telling:
	.string "HERON recites the telling from the\n"
	.string "pavilion, all eight verses, in a\p"
	.string "voice the rain obeys.\n"
	.string "The Long One lay down to guard.$"

LandsEnd_Text_Andrew2:
	.string "ANDREW: A bedtime story. A serpent\n"
	.string "murdered, and the water remembers.\p"
	.string "ANDREW: I have watched your songs\n"
	.string "teach people to sit and wait.$"

LandsEnd_Text_Andrew3:
	.string "ANDREW: The Long One isn't asleep.\n"
	.string "It's a debt. Debts get collected.$"

LandsEnd_Text_Jayden1:
	.string "JAYDEN: I heard every verse. WREN\n"
	.string "sang me half. I can't unhear it.\p"
	.string "JAYDEN: But I'm done being told\n"
	.string "what to believe. Battle me. Really.$"

LandsEnd_Text_JaydenDefeat:
	.string "That MEGA should have been enough.$"

LandsEnd_Text_Jayden2:
	.string "JAYDEN: ...Fine. You win. The song\n"
	.string "might hold. I hope it holds.\p"
	.string "JAYDEN: If it comes to waking\n"
	.string "something, I want to be there.$"

LandsEnd_Text_Andrew4:
	.string "ANDREW: Enough, JAYDEN. We're off.\n"
	.string "Your song won't hold, singer.\p"
	.string "Nothing does. We'll meet at the end.$"

LandsEnd_Text_Storm1:
	.string "The sky turns green. Thunder walks\n"
	.string "across the Gulf, and the dust-choked\p"
	.string "wind from the north goes still.\n"
	.string "A long shadow crosses the clouds:\p"
	.string "vast, green, and awake. Far to the\n"
	.string "north-west the dust falls to the\p"
	.string "ground.$"

LandsEnd_Text_Note:
	.string "A PELIPPER lands with a note: It's\n"
	.string "awake. Come to the OLD WATER. The\p"
	.string "telling must be sung whole. TUPELO$"

LandsEnd_Text_AndrewIdle:
	.string "ANDREW: We have nothing more to say.$"

LandsEnd_Text_JaydenIdle:
	.string "JAYDEN: ...$"

@ --- mapgen: generated NPC scripts (begin) ---

LandsEnd_EventScript_Heron::
	msgbox LandsEnd_Text_Heron, MSGBOX_NPC
	end

LandsEnd_Text_Heron:
	.string "HERON keeps the rain pavilion. She\nsays the rain only listens to order.$"

LandsEnd_EventScript_Fisherman::
	msgbox LandsEnd_Text_Fisherman, MSGBOX_NPC
	end

LandsEnd_Text_Fisherman:
	.string "The flats on Route 19 drain at dawn.\nFossils turn up in the mud.$"

LandsEnd_EventScript_BoatmanW::
	msgbox LandsEnd_Text_BoatmanW, MSGBOX_NPC
	end

LandsEnd_Text_BoatmanW:
	.string "West of here, the delta road to the\nmill. The span fell. Good riddance.$"

LandsEnd_EventScript_BoatmanS::
	msgbox LandsEnd_Text_BoatmanS, MSGBOX_NPC
	end

LandsEnd_Text_BoatmanS:
	.string "South, past Route 21, the Gulf. The\nbarge sat there for years.$"

LandsEnd_EventScript_Kid::
	msgbox LandsEnd_Text_Kid, MSGBOX_NPC
	end

LandsEnd_Text_Kid:
	.string "My dad says the pavilion's rain is a\npuzzle. I just get wet.$"

LandsEnd_EventScript_Shrimper::
	msgbox LandsEnd_Text_Shrimper, MSGBOX_NPC
	end

LandsEnd_Text_Shrimper:
	.string "Shrimp run in the rain. I love\nHeron's pavilion. Business!$"

LandsEnd_EventScript_SignWest::
	msgbox LandsEnd_Text_SignWest, MSGBOX_SIGN
	end

LandsEnd_Text_SignWest:
	.string "LAND'S END\nWest: Route 20, by Surf.$"

LandsEnd_EventScript_SignPavilion::
	msgbox LandsEnd_Text_SignPavilion, MSGBOX_SIGN
	end

LandsEnd_Text_SignPavilion:
	.string "THE RAIN PAVILION\nSeven carved verses. Mind the rain.$"

@ --- mapgen: generated NPC scripts (end) ---
