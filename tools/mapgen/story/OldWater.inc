OldWater_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldWater_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, OldWater_OnFrameTable
	.byte 0

@ Isaac's raid (Chapter 7, 7.6, story 33 -> 34). VAR_OLD_WATER_RAID: 0 idle, 1 armed (Wren's call at Redfield, or any first visit while the story
@ is 33), 2 done. Stage 0 only re-routes to the fixed landing cell of the scene; stage 1 plays it. A blackout in the battle leaves the var at 1,
@ so the scene replays. The player and Wren fight two grunts as a partner battle (the engine's multi battle, Wren is PARTNER_WREN_<starter>).

@ the raid actors are hidden on every load; the scene brings them in (clearflag + addobject)
OldWater_OnTransition:
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_RAID_WREN
	end

OldWater_OnFrameTable:
	map_script_2 VAR_OLD_WATER_RAID, 0, OldWater_EventScript_RaidEntry
	map_script_2 VAR_OLD_WATER_RAID, 1, OldWater_EventScript_RaidScene
	.2byte 0

OldWater_EventScript_RaidEntry::
	goto_if_ne VAR_ORLEANS_STORY, 33, OldWater_EventScript_RaidIdle
	lockall
	setvar VAR_OLD_WATER_RAID, 1
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER, 22, 32
	waitstate
	releaseall
	end

OldWater_EventScript_RaidIdle:
	end

OldWater_EventScript_RaidScene::
	goto_if_ne VAR_ORLEANS_STORY, 33, OldWater_EventScript_RaidStale
	lockall
	clearflag FLAG_HIDE_RAID_ISAAC
	clearflag FLAG_HIDE_RAID_GRUNT1
	clearflag FLAG_HIDE_RAID_GRUNT2
	clearflag FLAG_HIDE_RAID_WREN
	addobject LOCALID_OLD_WATER_RAID_ISAAC
	addobject LOCALID_OLD_WATER_RAID_GRUNT1
	addobject LOCALID_OLD_WATER_RAID_GRUNT2
	addobject LOCALID_OLD_WATER_RAID_WREN
	msgbox OldWater_Text_Scene1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Grunt1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Wren1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Grunt2, MSGBOX_DEFAULT
	closemessage
	goto OldWater_EventScript_RaidBattle

@ stage 1 with the story elsewhere (a debug warp): nothing to play, and it must not loop
OldWater_EventScript_RaidStale:
	setvar VAR_OLD_WATER_RAID, 2
	end

OldWater_EventScript_RaidBattle:
	call_if_eq VAR_STARTER_MON, 0, OldWater_EventScript_BattleChikorita
	call_if_eq VAR_STARTER_MON, 1, OldWater_EventScript_BattleFuecoco
	call_if_eq VAR_STARTER_MON, 2, OldWater_EventScript_BattleTotodile
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_LOST, OldWater_EventScript_RaidLost
	goto OldWater_EventScript_RaidWon

OldWater_EventScript_BattleChikorita:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_CHIKORITA
	return

OldWater_EventScript_BattleFuecoco:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_FUECOCO
	return

OldWater_EventScript_BattleTotodile:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_TOTODILE
	return

@ a loss: heal, then TRY AGAIN or NOT YET (B = not yet): NOT YET sends the player back to Redfield with the raid reset (Wren waits outside the mill)
OldWater_EventScript_RaidLost:
	special HealPlayerParty
	msgbox OldWater_Text_Retry, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 2, 0, DYN_MULTICHOICE_CB_NONE, OldWater_Text_ChoiceAgain, OldWater_Text_ChoiceNotYet
	goto_if_eq VAR_RESULT, 0, OldWater_EventScript_RaidAgain
	goto OldWater_EventScript_RaidNotYet

OldWater_EventScript_RaidAgain:
	closemessage
	goto OldWater_EventScript_RaidBattle

OldWater_EventScript_RaidNotYet:
	msgbox OldWater_Text_NotYet, MSGBOX_DEFAULT
	closemessage
	setvar VAR_OLD_WATER_RAID, 0
	setvar VAR_REDFIELD_RAID_CALL, 1
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_RAID_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_ISAAC
	removeobject LOCALID_OLD_WATER_RAID_GRUNT1
	removeobject LOCALID_OLD_WATER_RAID_GRUNT2
	removeobject LOCALID_OLD_WATER_RAID_WREN
	warpsilent MAP_REDFIELD, 37, 14
	waitstate
	releaseall
	end

OldWater_EventScript_RaidWon:
	special HealPlayerParty
	msgbox OldWater_Text_Isaac2, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac3, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac4, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ORLEANS_STORY, 34
	setvar VAR_OLD_WATER_RAID, 2
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_REDFIELD_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_ISAAC
	removeobject LOCALID_OLD_WATER_RAID_GRUNT1
	removeobject LOCALID_OLD_WATER_RAID_GRUNT2
	fadescreen FADE_FROM_BLACK
	msgbox OldWater_Text_Wren2, MSGBOX_DEFAULT
	msgbox OldWater_Text_Wren3, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_HIDE_RAID_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_WREN
	warpsilent MAP_REDFIELD, 37, 14
	waitstate
	releaseall
	end

@ the raid actors (hidden when the scene is not running); talking to them does nothing special
OldWater_EventScript_RaidIsaac::
OldWater_EventScript_RaidGrunt1::
OldWater_EventScript_RaidGrunt2::
OldWater_EventScript_RaidWren::
	end

@ ---------------------------------------------------------------- text
OldWater_Text_Scene1:
	.string "The OLD WATER is wrong. No bells, no\n"
	.string "singing. Smoke drifts between the\p"
	.string "stilt houses, and strangers in\n"
	.string "dark coats stand on the green.$"

OldWater_Text_Grunt1:
	.string "GRUNT: The song-house wall comes\n"
	.string "down. Every panel. That's the order.\p"
	.string "GRUNT: Move, sir. The boat's\n"
	.string "waiting.$"

OldWater_Text_Isaac1:
	.string "ISAAC: ...Wait. Just wait a\n"
	.string "minute.$"

OldWater_Text_Wren1:
	.string "WREN: ISAAC! You ate at the camp's\n"
	.string "table! You judged it a tie!\p"
	.string "ISAAC: ...I know. I remember.$"

OldWater_Text_Grunt2:
	.string "GRUNT: Enough talk. Take the girl\n"
	.string "and the kid!$"

OldWater_Text_DefeatA:
	.string "My CROBAT...$"

OldWater_Text_DefeatB:
	.string "That's not what we were promised.$"

OldWater_Text_Isaac2:
	.string "ISAAC: Stop. Stop it, both of you.\n"
	.string "Pack up. We're leaving.\p"
	.string "GRUNT: Sir, the order's from above!\n"
	.string "ISAAC: I said pack up.$"

OldWater_Text_Isaac3:
	.string "ISAAC: JAYDEN said the song was a\n"
	.string "lie that drowned a town. But the\p"
	.string "gumbo was real. The tie was real.\n"
	.string "I'll find my own answer.$"

OldWater_Text_Isaac4:
	.string "ISAAC: Tell TUPELO I'm sorry. And\n"
	.string "tell the boy I'm not coming back.$"

OldWater_Text_Wren2:
	.string "WREN: He turned. He actually\n"
	.string "turned.\p"
	.string "WREN: I'll stay and help TUPELO put\n"
	.string "the green back in order.$"

OldWater_Text_Wren3:
	.string "WREN: The sixth and seventh verses\n"
	.string "hold. Go on to LAND'S END. I'll\p"
	.string "send word. Take the boat. It's\n"
	.string "faster than the road.$"

OldWater_Text_Retry:
	.string "WREN: Again? Together this time?\n"
	.string "Or come back later?$"

OldWater_Text_NotYet:
	.string "WREN: Not yet, then. Back to the\n"
	.string "mill. I'll be waiting.$"

OldWater_Text_ChoiceAgain:
	.string "TRY AGAIN$"

OldWater_Text_ChoiceNotYet:
	.string "NOT YET$"

