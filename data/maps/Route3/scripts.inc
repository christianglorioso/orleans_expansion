Route3_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route3_OnTransition
	.byte 0

@ Jayden is only on the causeway for his scene (BridgeStandoff clears this flag), at any story value.
Route3_OnTransition:
	call Route3_EventScript_PGSetup
	setflag FLAG_HIDE_ROUTE3_JAYDEN
	end

@ Route 3: the causeway from Storm's Edge to Crescent City. Six trainers (levels 19-22, west to east), a Super Potion in the
@ rest stop, a hidden Revive under the bridge, and Jayden's second battle at the bridge (story 11 -> 12).
@ Trainer scripts are named after the mockup marker ids (Trainer1 = marker 1, ...).
Route3_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_FISHERMAN, Route3_Text_FishermanIntro, Route3_Text_FishermanDefeat
	msgbox Route3_Text_FishermanAfter, MSGBOX_AUTOCLOSE
	end

Route3_EventScript_Trainer6::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_SAILOR, Route3_Text_SailorIntro, Route3_Text_SailorDefeat
	msgbox Route3_Text_SailorAfter, MSGBOX_AUTOCLOSE
	end

Route3_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_BUG_MANIAC, Route3_Text_BugManiacIntro, Route3_Text_BugManiacDefeat
	msgbox Route3_Text_BugManiacAfter, MSGBOX_AUTOCLOSE
	end

Route3_EventScript_Trainer7::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_BREEDER, Route3_Text_BreederIntro, Route3_Text_BreederDefeat
	msgbox Route3_Text_BreederAfter, MSGBOX_AUTOCLOSE
	end

Route3_EventScript_Trainer4::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_PARASOL_LADY, Route3_Text_ParasolIntro, Route3_Text_ParasolDefeat
	msgbox Route3_Text_ParasolAfter, MSGBOX_AUTOCLOSE
	end

Route3_EventScript_Trainer8::
	trainerbattle_single TRAINER_ORLEANS_ROUTE3_COOLTRAINER, Route3_Text_CooltrainerIntro, Route3_Text_CooltrainerDefeat
	msgbox Route3_Text_CooltrainerAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Jayden at the bridge
@ Trigger cells (spec "triggers", story_overlay.py): the five walkable cells of column x 42 (rows 0, 1, 8 and the bridge's 11, 12;
@ the pond and river fill the rest of that column), live while the story is 11 (Eclair beaten, bridge down). Nobody can cross the
@ column without stepping on one. Each row script stands Jayden at (43, row), right in front of the player, then runs the scene.
@ He fights with the starter that has the advantage over the player's pick (as on Route 1).
Route3_EventScript_BridgeStandoffRow0::
	setobjectxyperm LOCALID_ROUTE3_JAYDEN, 43, 0
	goto Route3_EventScript_BridgeStandoff

Route3_EventScript_BridgeStandoffRow1::
	setobjectxyperm LOCALID_ROUTE3_JAYDEN, 43, 1
	goto Route3_EventScript_BridgeStandoff

Route3_EventScript_BridgeStandoffRow8::
	setobjectxyperm LOCALID_ROUTE3_JAYDEN, 43, 8
	goto Route3_EventScript_BridgeStandoff

Route3_EventScript_BridgeStandoffRow11::
	setobjectxyperm LOCALID_ROUTE3_JAYDEN, 43, 11
	goto Route3_EventScript_BridgeStandoff

Route3_EventScript_BridgeStandoffRow12::
	setobjectxyperm LOCALID_ROUTE3_JAYDEN, 43, 12
	goto Route3_EventScript_BridgeStandoff

Route3_EventScript_BridgeStandoff:
	lockall
	clearflag FLAG_HIDE_ROUTE3_JAYDEN
	addobject LOCALID_ROUTE3_JAYDEN
	msgbox Route3_Text_BridgeJayden1, MSGBOX_DEFAULT
	msgbox Route3_Text_BridgeJayden2, MSGBOX_DEFAULT
	msgbox Route3_Text_BridgeJayden3, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_STARTER_MON, 0, Route3_EventScript_BattleJaydenChikorita
	call_if_eq VAR_STARTER_MON, 1, Route3_EventScript_BattleJaydenFuecoco
	call_if_eq VAR_STARTER_MON, 2, Route3_EventScript_BattleJaydenTotodile
	msgbox Route3_Text_BridgeJaydenAfter, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ORLEANS_STORY, 12
	setflag FLAG_HIDE_ROUTE3_JAYDEN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_ROUTE3_JAYDEN
	special HealPlayerParty
	fadescreen FADE_FROM_BLACK
	msgbox Route3_Text_BridgeAfterwards, MSGBOX_DEFAULT
	releaseall
	end

Route3_EventScript_BattleJaydenChikorita:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE3_CHIKORITA, Route3_Text_BridgeJaydenDefeat
	return

Route3_EventScript_BattleJaydenFuecoco:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE3_FUECOCO, Route3_Text_BridgeJaydenDefeat
	return

Route3_EventScript_BattleJaydenTotodile:
	trainerbattle_no_intro TRAINER_ORLEANS_JAYDEN_ROUTE3_TOTODILE, Route3_Text_BridgeJaydenDefeat
	return

Route3_EventScript_Jayden::
	msgbox Route3_Text_BridgeJayden3, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- text
Route3_Text_FishermanIntro:
	.string "The surge pushed every fish into\n"
	.string "the causeway pools. I'm busy!$"

Route3_Text_FishermanDefeat:
	.string "You scared the whole school off.$"

Route3_Text_FishermanAfter:
	.string "Wooper don't care about wires.\n"
	.string "Good at being underfoot, though.$"

Route3_Text_SailorIntro:
	.string "My boat's tied up in STORM'S EDGE\n"
	.string "while the harbor gets fixed.\p"
	.string "So I walk. And I battle!$"

Route3_Text_SailorDefeat:
	.string "Overboard!$"

Route3_Text_SailorAfter:
	.string "The causeway's all water either\n"
	.string "side. Feels like home.$"

Route3_Text_BugManiacIntro:
	.string "Look at them all in the grass!\n"
	.string "You'll have to battle me first.$"

Route3_Text_BugManiacDefeat:
	.string "Squished my whole collection!$"

Route3_Text_BugManiacAfter:
	.string "DEWPIDER carry their own air\n"
	.string "bubble. Isn't that wonderful?$"

Route3_Text_BreederIntro:
	.string "I raise my POKéMON on the rest\n"
	.string "stop's shade. They look tough!$"

Route3_Text_BreederDefeat:
	.string "Oh, my poor darlings!$"

Route3_Text_BreederAfter:
	.string "Raised right, they always come\n"
	.string "back stronger. Like the town.$"

Route3_Text_ParasolIntro:
	.string "A little rain never hurt anybody.\n"
	.string "Shall we battle?$"

Route3_Text_ParasolDefeat:
	.string "How refreshing!$"

Route3_Text_ParasolAfter:
	.string "CRESCENT CITY is just past the\n"
	.string "bridge. Mind the manners there.$"

Route3_Text_CooltrainerIntro:
	.string "You beat ÉCLAIR? Then I'll test\n"
	.string "what's left of your batteries!$"

Route3_Text_CooltrainerDefeat:
	.string "Fully drained.$"

Route3_Text_CooltrainerAfter:
	.string "Save some strength. The third\n"
	.string "SINGER keeps odd company.$"

Route3_Text_BridgeJayden1:
	.string "JAYDEN: Tch. Of course you got\n"
	.string "across. The grid, the badge, all\p"
	.string "of it. Even the old bridge likes\n"
	.string "you better than it likes me.$"

Route3_Text_BridgeJayden2:
	.string "JAYDEN: RITA says CRESCENT CITY's\n"
	.string "flooded wards are full of people\p"
	.string "with nothing left. I hand them\n"
	.string "pamphlets. They cry. They thank me.$"

Route3_Text_BridgeJayden3:
	.string "JAYDEN: ...Don't look at me like\n"
	.string "that. They told me to slow you\p"
	.string "down. They didn't say how.\n"
	.string "So we'll do it my way!$"

Route3_Text_BridgeJaydenDefeat:
	.string "JAYDEN: ...Fine. Fine!$"

Route3_Text_BridgeJaydenAfter:
	.string "JAYDEN: That old man. TUPELO. Did\n"
	.string "he say the serpent was killed?\p"
	.string "Or did he say something else?\n"
	.string "...Forget it. Forget I asked.$"

Route3_Text_BridgeAfterwards:
	.string "JAYDEN storms off toward the\n"
	.string "city, head down.\p"
	.string "CRESCENT CITY lies ahead, across\n"
	.string "the bridge.$"

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
Route3_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, Route3_EventScript_PGHide
Route3_EventScript_PGSetupDone:
	return

Route3_EventScript_PGHide:
	setflag FLAG_PG_TORNADUS
	return

Route3_EventScript_PgTornadus::
	lock
	faceplayer
	playmoncry SPECIES_TORNADUS, CRY_MODE_ENCOUNTER
	msgbox Route3_Text_PGTornadus, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_TORNADUS, 62
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route3_EventScript_PgTornadusDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route3_EventScript_PgTornadusStill
	release
	end

Route3_EventScript_PgTornadusStill:
	msgbox Route3_Text_PGStillTornadus, MSGBOX_DEFAULT
	release
	end

Route3_EventScript_PgTornadusDone:
	setflag FLAG_PG_TORNADUS
	removeobject LOCALID_ROUTE3_PG_TORNADUS
	release
	end

Route3_Text_PGTornadus:
	.string "TORNADUS stands before you,\n"
	.string "wrapped in a roaring gale.$"

Route3_Text_PGStillTornadus:
	.string "TORNADUS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

Route3_EventScript_SignCity::
	msgbox Route3_Text_SignCity, MSGBOX_SIGN
	end

Route3_Text_SignCity:
	.string "CRESCENT CITY\nCity limits: welcome!$"

Route3_EventScript_RouteSign1::
	msgbox Route3_Text_RouteSign1, MSGBOX_SIGN
	end

Route3_Text_RouteSign1:
	.string "REST STOP\nWater and shade for travellers.$"

Route3_EventScript_RouteSign2::
	msgbox Route3_Text_RouteSign2, MSGBOX_SIGN
	end

Route3_Text_RouteSign2:
	.string "CAUSEWAY ROAD\nWest: Storm's Edge. East: Crescent.$"

@ --- mapgen: generated NPC scripts (end) ---
