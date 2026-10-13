CrescentCity_BlacksnakeBase_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_BlacksnakeBase_OnTransition
	.byte 0

@ Team Blacksnake's base in the Drowned Ward (act 1), cleared with Wren after gym 3 (story 16 -> 17). Wren stands inside only while
@ the story is 16; the lieutenant is hidden for good once beaten (FLAG_HIDE_CRESCENT_LIEUTENANT).
@ Rene and Marcel are single battles on sight. The lieutenant and her guard Louise are the first PARTNER battle (plan 3.6): talk to
@ either and WREN steps in beside the player (multi_fixed_2_vs_2, PARTNER_WREN_BASE_<starter>, low-level, by the starter line that
@ neither the player nor Jayden took). A loss offers TRY AGAIN / NOT YET; the carving stays guarded until ODETTE is beaten.
CrescentCity_BlacksnakeBase_OnTransition:
	call CrescentCity_BlacksnakeBase_EventScript_PGSetup
	setflag FLAG_HIDE_CRESCENT_BASE_WREN
	call_if_eq VAR_ORLEANS_STORY, 16, CrescentCity_BlacksnakeBase_EventScript_ShowWren
	end

CrescentCity_BlacksnakeBase_EventScript_ShowWren:
	clearflag FLAG_HIDE_CRESCENT_BASE_WREN
	return

CrescentCity_BlacksnakeBase_EventScript_Trainer0::
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_POISON, CrescentCity_BlacksnakeBase_Text_PoisonIntro, CrescentCity_BlacksnakeBase_Text_PoisonDefeat
	msgbox CrescentCity_BlacksnakeBase_Text_PoisonAfter, MSGBOX_AUTOCLOSE
	end

CrescentCity_BlacksnakeBase_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_DARK, CrescentCity_BlacksnakeBase_Text_DarkIntro, CrescentCity_BlacksnakeBase_Text_DarkDefeat
	msgbox CrescentCity_BlacksnakeBase_Text_DarkAfter, MSGBOX_AUTOCLOSE
	end

CrescentCity_BlacksnakeBase_EventScript_Trainer2::
	lock
	faceplayer
	goto_if_defeated TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER, CrescentCity_BlacksnakeBase_EventScript_WaterAfter
	goto CrescentCity_BlacksnakeBase_EventScript_PairStart

CrescentCity_BlacksnakeBase_EventScript_WaterAfter:
	msgbox CrescentCity_BlacksnakeBase_Text_WaterAfter, MSGBOX_DEFAULT
	release
	end

@ RITA's lieutenant and her guard LOUISE: the partner battle with WREN. The lieutenant retreats after it (and is gone from then on)
CrescentCity_BlacksnakeBase_EventScript_AdminRitas3::
	lock
	faceplayer
	goto_if_defeated TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_EventScript_LieutenantAfterTalk
	goto CrescentCity_BlacksnakeBase_EventScript_PairStart

CrescentCity_BlacksnakeBase_EventScript_LieutenantAfterTalk:
	msgbox CrescentCity_BlacksnakeBase_Text_LieutenantAfter, MSGBOX_DEFAULT
	release
	end

CrescentCity_BlacksnakeBase_EventScript_PairStart:
	msgbox CrescentCity_BlacksnakeBase_Text_PairIntro, MSGBOX_DEFAULT
	closemessage
CrescentCity_BlacksnakeBase_EventScript_PairBattle:
	call_if_eq VAR_STARTER_MON, 0, CrescentCity_BlacksnakeBase_EventScript_PairFuecoco
	call_if_eq VAR_STARTER_MON, 1, CrescentCity_BlacksnakeBase_EventScript_PairTotodile
	call_if_eq VAR_STARTER_MON, 2, CrescentCity_BlacksnakeBase_EventScript_PairChikorita
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_WON, CrescentCity_BlacksnakeBase_EventScript_PairLost
	settrainerflag TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER
	settrainerflag TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT
	special HealPlayerParty
	goto CrescentCity_BlacksnakeBase_EventScript_LieutenantRetreats

@ Wren raised the starter that neither the player (0 Totodile, 1 Chikorita, 2 Fuecoco) nor Jayden took
CrescentCity_BlacksnakeBase_EventScript_PairFuecoco:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER, CrescentCity_BlacksnakeBase_Text_WaterDefeat, TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_Text_LieutenantDefeat, PARTNER_WREN_BASE_FUECOCO
	return

CrescentCity_BlacksnakeBase_EventScript_PairTotodile:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER, CrescentCity_BlacksnakeBase_Text_WaterDefeat, TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_Text_LieutenantDefeat, PARTNER_WREN_BASE_TOTODILE
	return

CrescentCity_BlacksnakeBase_EventScript_PairChikorita:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER, CrescentCity_BlacksnakeBase_Text_WaterDefeat, TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_Text_LieutenantDefeat, PARTNER_WREN_BASE_CHIKORITA
	return

@ a loss: heal, then TRY AGAIN or NOT YET (B = not yet)
CrescentCity_BlacksnakeBase_EventScript_PairLost:
	special HealPlayerParty
	msgbox CrescentCity_BlacksnakeBase_Text_PairRetry, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, CrescentCity_BlacksnakeBase_EventScript_PairAgain
	msgbox CrescentCity_BlacksnakeBase_Text_PairNotYet, MSGBOX_DEFAULT
	release
	end

CrescentCity_BlacksnakeBase_EventScript_PairAgain:
	closemessage
	goto CrescentCity_BlacksnakeBase_EventScript_PairBattle

CrescentCity_BlacksnakeBase_EventScript_LieutenantRetreats::
	msgbox CrescentCity_BlacksnakeBase_Text_LieutenantRetreat, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_HIDE_CRESCENT_LIEUTENANT
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CRESCENT_CITY_BLACKSNAKE_BASE_ADMIN_RITAS3
	fadescreen FADE_FROM_BLACK
	release
	end

CrescentCity_BlacksnakeBase_EventScript_Wren4::
	lock
	faceplayer
	goto_if_not_defeated TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_EventScript_WrenWaiting
	msgbox CrescentCity_BlacksnakeBase_Text_WrenLook, MSGBOX_DEFAULT
	release
	end

CrescentCity_BlacksnakeBase_EventScript_WrenWaiting:
	msgbox CrescentCity_BlacksnakeBase_Text_WrenHold, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- the damaged carving (story 16 -> 17)
CrescentCity_BlacksnakeBase_EventScript_Carving::
	lockall
	goto_if_set FLAG_CARVING_FOUND, CrescentCity_BlacksnakeBase_EventScript_CarvingSeen
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_BlacksnakeBase_EventScript_CarvingGuarded
	goto_if_lt VAR_ORLEANS_STORY, 16, CrescentCity_BlacksnakeBase_EventScript_CarvingGuarded
	goto_if_not_defeated TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_EventScript_CarvingGuarded
	msgbox CrescentCity_BlacksnakeBase_Text_Carving1, MSGBOX_DEFAULT
	msgbox CrescentCity_BlacksnakeBase_Text_Carving2, MSGBOX_DEFAULT
	msgbox CrescentCity_BlacksnakeBase_Text_Carving3, MSGBOX_DEFAULT
	setflag FLAG_CARVING_FOUND
	call_if_lt VAR_ORLEANS_STORY, 17, CrescentCity_BlacksnakeBase_EventScript_SetStory17
	setflag FLAG_HIDE_CRESCENT_BASE_WREN
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CRESCENT_CITY_BLACKSNAKE_BASE_WREN4
	fadescreen FADE_FROM_BLACK
	msgbox CrescentCity_BlacksnakeBase_Text_WrenGoes, MSGBOX_DEFAULT
	releaseall
	end

CrescentCity_BlacksnakeBase_EventScript_SetStory17:
	setvar VAR_ORLEANS_STORY, 17
	return

CrescentCity_BlacksnakeBase_EventScript_CarvingGuarded:
	msgbox CrescentCity_BlacksnakeBase_Text_CarvingGuarded, MSGBOX_DEFAULT
	releaseall
	end

CrescentCity_BlacksnakeBase_EventScript_CarvingSeen:
	msgbox CrescentCity_BlacksnakeBase_Text_CarvingSeen, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- text
CrescentCity_BlacksnakeBase_Text_PoisonIntro:
	.string "Stop right there! This warehouse\n"
	.string "belongs to the true believers.$"

CrescentCity_BlacksnakeBase_Text_PoisonDefeat:
	.string "Venom wasted.$"

CrescentCity_BlacksnakeBase_Text_PoisonAfter:
	.string "RITA's recruiting every flooded\n"
	.string "street. We're the only ones who\p"
	.string "feed them. What did you ever do?$"

CrescentCity_BlacksnakeBase_Text_DarkIntro:
	.string "You're the kid from the shelter!\n"
	.string "JAYDEN said you'd come sniffing.$"

CrescentCity_BlacksnakeBase_Text_DarkDefeat:
	.string "I knew it. I knew I'd lose.$"

CrescentCity_BlacksnakeBase_Text_DarkAfter:
	.string "The boss says the bayou's wounded.\n"
	.string "I've seen my house floating off.\p"
	.string "He's not wrong. Not all wrong.$"

CrescentCity_BlacksnakeBase_Text_WaterDefeat:
	.string "Washed out!$"

CrescentCity_BlacksnakeBase_Text_WaterAfter:
	.string "I only joined for the hot meals.\n"
	.string "...And a bed. And someone to ask\p"
	.string "where I'd been all day.$"

CrescentCity_BlacksnakeBase_Text_LieutenantDefeat:
	.string "ODETTE: Tch. Not what I was paid\n"
	.string "for.$"

CrescentCity_BlacksnakeBase_Text_LieutenantRetreat:
	.string "ODETTE: Fine. RITA has other\n"
	.string "wards, and other lieutenants.\p"
	.string "Keep the warehouse. It's flooded\n"
	.string "anyway. We'll find another.$"

CrescentCity_BlacksnakeBase_Text_LieutenantAfter:
	.string "ODETTE: Don't look so pleased.\n"
	.string "This was only the first ward.$"

CrescentCity_BlacksnakeBase_Text_WrenHold:
	.string "WREN: The lieutenant and her guard\n"
	.string "stand in front of the carving.\p"
	.string "Talk to them and I'll step in\n"
	.string "beside you. Together, like I said.$"

CrescentCity_BlacksnakeBase_Text_WrenLook:
	.string "WREN: The lieutenant's gone. Look\n"
	.string "at the carving. Please.$"

CrescentCity_BlacksnakeBase_Text_PairIntro:
	.string "ODETTE: RITA warned me about a\n"
	.string "meddling child. Polite, in the way.\p"
	.string "LOUISE: The flooded hall is ours!\n"
	.string "Nobody crosses without paying!\p"
	.string "WREN: Two of you? Then two of us.\n"
	.string "Ready, {PLAYER}?$"

CrescentCity_BlacksnakeBase_Text_PairRetry:
	.string "WREN: Again. Together this time.\n"
	.string "Ready?$"

CrescentCity_BlacksnakeBase_Text_PairNotYet:
	.string "WREN: Then get stronger and come\n"
	.string "back. I'll hold the hall.$"

CrescentCity_BlacksnakeBase_Text_CarvingGuarded:
	.string "A Rootkin carving, propped against\n"
	.string "the wall, one corner gouged.\p"
	.string "The lieutenant still stands in\n"
	.string "the way.$"

CrescentCity_BlacksnakeBase_Text_Carving1:
	.string "A Rootkin carving, as long as\n"
	.string "your arm. Some lines of the old\p"
	.string "telling are cut into the wood.\n"
	.string "One corner has been chipped away.$"

CrescentCity_BlacksnakeBase_Text_Carving2:
	.string "The line near the break reads:\n"
	.string "“...the Long One was laid low...”\p"
	.string "The chip runs through the words\n"
	.string "after it, fresh and pale.$"

CrescentCity_BlacksnakeBase_Text_Carving3:
	.string "WREN: That can't be all of it.\n"
	.string "The line doesn't stop at “low.”\p"
	.string "Somebody chipped the rest away,\n"
	.string "on purpose. So it would read\p"
	.string "“laid low.” That the Long One\n"
	.string "was killed.$"

CrescentCity_BlacksnakeBase_Text_WrenGoes:
	.string "WREN gathers the carving in her\n"
	.string "arms like something alive.\p"
	.string "“TUPELO has to see this. I'll go\n"
	.string "ahead. Meet me at the OLD WATER.”$"

CrescentCity_BlacksnakeBase_Text_CarvingSeen:
	.string "The empty spot where the damaged\n"
	.string "carving stood. Dust in a shape\p"
	.string "like a long, folded snake.$"

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
CrescentCity_BlacksnakeBase_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, CrescentCity_BlacksnakeBase_EventScript_PGHide
CrescentCity_BlacksnakeBase_EventScript_PGSetupDone:
	return

CrescentCity_BlacksnakeBase_EventScript_PGHide:
	setflag FLAG_PG_WEEZINGITE
	return

CrescentCity_BlacksnakeBase_EventScript_Pgweezingite5::
	lock
	giveitem ITEM_WEEZINGITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_PG_WEEZINGITE
	removeobject LOCALID_CRESCENT_CITY_BLACKSNAKE_BASE_PGWEEZINGITE5
	release
	end

@ --- end post-game ---
