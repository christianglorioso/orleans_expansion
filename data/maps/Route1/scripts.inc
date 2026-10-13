Route1_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route1_OnTransitionPG
	.byte 0

@ ---------------------------------------------------------------- the south gate (before the first battle)
Route1_EventScript_TooDangerous::
	lockall
	msgbox Route1_Text_TooDangerous, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, Route1_Movement_StepBack
	waitmovement 0
	releaseall
	end

Route1_Movement_StepBack:
	walk_down
	step_end

@ ---------------------------------------------------------------- step 5: the Pokédex
Route1_EventScript_LafayetteCallsOver::
	lockall
	msgbox Route1_Text_LafayetteCalls, MSGBOX_DEFAULT
	goto Route1_EventScript_GivePokedex

Route1_EventScript_Lafayette::
	lock
	faceplayer
	goto_if_eq VAR_ORLEANS_STORY, 3, Route1_EventScript_GivePokedex
	msgbox Route1_Text_LafayetteAfter, MSGBOX_DEFAULT
	release
	end

Route1_EventScript_GivePokedex:
	msgbox Route1_Text_LafayettePokedex, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message Route1_Text_ReceivedPokedex
	waitfanfare
	setflag FLAG_SYS_POKEDEX_GET
	special SetUnlockedPokedexFlags
	msgbox Route1_Text_LafayetteBalls, MSGBOX_DEFAULT
	giveitem ITEM_POKE_BALL, 5
	msgbox Route1_Text_LafayetteGoAhead, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 4
	releaseall
	end

@ ---------------------------------------------------------------- trainers
Route1_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE1_FISHERMAN, Route1_Text_FishermanIntro, Route1_Text_FishermanDefeat
	msgbox Route1_Text_FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route1_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE1_BUG_CATCHER, Route1_Text_BugCatcherIntro, Route1_Text_BugCatcherDefeat
	msgbox Route1_Text_BugCatcherAfter, MSGBOX_AUTOCLOSE
	end

Route1_EventScript_Trainer3::
	trainerbattle_single TRAINER_ORLEANS_ROUTE1_LASS, Route1_Text_LassIntro, Route1_Text_LassDefeat
	msgbox Route1_Text_LassAfter, MSGBOX_AUTOCLOSE
	end

Route1_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE1_YOUNGSTER, Route1_Text_YoungsterIntro, Route1_Text_YoungsterDefeat
	msgbox Route1_Text_YoungsterAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- step 7: the boat landing
Route1_EventScript_LandingStandoff::
	lockall
	msgbox Route1_Text_StandoffJayden, MSGBOX_DEFAULT
	msgbox Route1_Text_StandoffWren, MSGBOX_DEFAULT
	msgbox Route1_Text_StandoffNoticed, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_STARTER_MON, 0, Route1_EventScript_BattleJaydenChikorita
	call_if_eq VAR_STARTER_MON, 1, Route1_EventScript_BattleJaydenFuecoco
	call_if_eq VAR_STARTER_MON, 2, Route1_EventScript_BattleJaydenTotodile
	msgbox Route1_Text_JaydenAfter, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE1_JAYDEN
	setflag FLAG_HIDE_ROUTE1_JAYDEN
	fadescreen FADE_FROM_BLACK
	msgbox Route1_Text_WrenTrusts, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ORLEANS_STORY, 5
	setflag FLAG_HIDE_ROUTE1_WREN
	special HealPlayerParty
	fadescreen FADE_TO_BLACK
	msgbox Route1_Text_ThroughTheReeds, MSGBOX_DEFAULT
	closemessage
	warp MAP_OLD_WATER, 24, 35
	waitstate
	releaseall
	end

Route1_EventScript_BattleJaydenChikorita:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE1_CHIKORITA, Route1_Text_JaydenDefeat
	return

Route1_EventScript_BattleJaydenFuecoco:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE1_FUECOCO, Route1_Text_JaydenDefeat
	return

Route1_EventScript_BattleJaydenTotodile:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE1_TOTODILE, Route1_Text_JaydenDefeat
	return

Route1_EventScript_Jayden::
	msgbox Route1_Text_StandoffJayden, MSGBOX_NPC
	end

Route1_EventScript_Wren::
	msgbox Route1_Text_StandoffWren, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- text
Route1_Text_TooDangerous:
	.string "A voice calls from the levee:\n"
	.string "“Not without a POKéMON, kid!\p"
	.string "The water's still moving things!”$"

Route1_Text_LafayetteCalls:
	.string "LAFAYETTE: {PLAYER}! Over here!$"

Route1_Text_LafayettePokedex:
	.string "LAFAYETTE: The storm moved every\n"
	.string "species on the island. Some won't\p"
	.string "find their way home on their own.\p"
	.string "I need help counting them, so none\n"
	.string "are forgotten. Take this.$"

Route1_Text_ReceivedPokedex:
	.string "{PLAYER} received the POKéDEX!$"

Route1_Text_LafayetteBalls:
	.string "LAFAYETTE: And these. A BUG,\n"
	.string "FLYING or POISON POKéMON would\p"
	.string "serve you well in GRAND OAK.$"

Route1_Text_LafayetteGoAhead:
	.string "LAFAYETTE: GRAND OAK is north,\n"
	.string "past the old boat landing.$"

Route1_Text_LafayetteAfter:
	.string "LAFAYETTE: Every entry counts.\n"
	.string "Keep that POKéDEX close.$"

Route1_Text_FishermanIntro:
	.string "The storm stirred up the whole\n"
	.string "bayou. Let's see what you've got!$"

Route1_Text_FishermanDefeat:
	.string "Reeled in, hook and all.$"

Route1_Text_FishermanAfter:
	.string "The fish moved upstream after the\n"
	.string "storm. So did the folks.$"

Route1_Text_BugCatcherIntro:
	.string "The bugs all came out after the\n"
	.string "rain! Battle me!$"

Route1_Text_BugCatcherDefeat:
	.string "Squashed!$"

Route1_Text_BugCatcherAfter:
	.string "BUG POKéMON are great against\n"
	.string "GRASS types. Just saying.$"

Route1_Text_LassIntro:
	.string "My WINGULL got blown all the way\n"
	.string "here. We're making the best of it!$"

Route1_Text_LassDefeat:
	.string "Oh, we got blown away again.$"

Route1_Text_LassAfter:
	.string "Someday I'll fly it home.$"

Route1_Text_YoungsterIntro:
	.string "Hey! You're from the shelter!\n"
	.string "First battle? Mine too!$"

Route1_Text_YoungsterDefeat:
	.string "Aw, I wasn't ready!$"

Route1_Text_YoungsterAfter:
	.string "Catch something before the landing.\n"
	.string "Trust me.$"

Route1_Text_StandoffJayden:
	.string "JAYDEN: Last chance. Show me\n"
	.string "the channel your people use.$"

Route1_Text_StandoffWren:
	.string "WREN: It isn't mine to show.\n"
	.string "Not to you.$"

Route1_Text_StandoffNoticed:
	.string "JAYDEN: ...You again.\n"
	.string "Stay out of this.\p"
	.string "Fine. Let's see what the\n"
	.string "PROFESSOR's pick can do.$"

Route1_Text_JaydenDefeat:
	.string "JAYDEN: Tch. Lucky.$"

Route1_Text_JaydenAfter:
	.string "JAYDEN: Keep your channel, then.\n"
	.string "RITA'll find another way.$"

Route1_Text_WrenTrusts:
	.string "WREN: You didn't have to do that.\p"
	.string "...TUPELO should meet you.\n"
	.string "Come on. I'll paddle.$"

Route1_Text_ThroughTheReeds:
	.string "WREN steers the canoe through a\n"
	.string "gap in the reeds you'd never have\p"
	.string "seen on your own...$"

Route1_OnTransitionPG:
	call Route1_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route1_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route1_EventScript_PGHide
Route1_EventScript_PGSetupDone:
	return

Route1_EventScript_PGHide:
	setflag FLAG_PG_MESPRIT
	return

Route1_EventScript_PgMesprit::
	lock
	faceplayer
	playmoncry SPECIES_MESPRIT, CRY_MODE_ENCOUNTER
	msgbox Route1_Text_PGMesprit, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_MESPRIT, 55
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route1_EventScript_PgMespritDone
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route1_EventScript_PgMespritDone
	release
	end

Route1_EventScript_PgMespritDone:
	setflag FLAG_PG_MESPRIT
	removeobject LOCALID_ROUTE1_PG_MESPRIT
	release
	end

Route1_Text_PGMesprit:
	.string "MESPRIT stands before you,\n"
	.string "its heart glowing soft and warm.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

Route1_EventScript_MespritShrine::
	msgbox Route1_Text_MespritShrine, MSGBOX_SIGN
	end

Route1_Text_MespritShrine:
	.string "A weathered stone. Someone has\nleft fresh flowers on it.$"

@ --- mapgen: generated NPC scripts (end) ---
