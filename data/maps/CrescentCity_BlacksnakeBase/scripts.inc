CrescentCity_BlacksnakeBase_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_BlacksnakeBase_OnTransition
	.byte 0

@ Team Blacksnake's base in the Drowned Ward (act 1), cleared with Wren after gym 3 (story 16 -> 17). Wren stands inside only while
@ the story is 16; the lieutenant is hidden for good once beaten (FLAG_HIDE_CRESCENT_LIEUTENANT).
@ (Proposed: Wren doesn't fight; she holds the hall while the player takes the three grunts and the lieutenant one at a time.
@ A partner/multi battle needs engine support that isn't in yet: see the plan's open questions.)
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
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_BASE_GRUNT_WATER, CrescentCity_BlacksnakeBase_Text_WaterIntro, CrescentCity_BlacksnakeBase_Text_WaterDefeat
	msgbox CrescentCity_BlacksnakeBase_Text_WaterAfter, MSGBOX_AUTOCLOSE
	end

@ RITA's lieutenant: she retreats after the battle (and is gone from then on)
CrescentCity_BlacksnakeBase_EventScript_AdminRitas3::
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_BASE_LIEUTENANT, CrescentCity_BlacksnakeBase_Text_LieutenantIntro, CrescentCity_BlacksnakeBase_Text_LieutenantDefeat, CrescentCity_BlacksnakeBase_EventScript_LieutenantRetreats
	msgbox CrescentCity_BlacksnakeBase_Text_LieutenantAfter, MSGBOX_AUTOCLOSE
	end

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

CrescentCity_BlacksnakeBase_Text_WaterIntro:
	.string "The flooded hall is ours! Nobody\n"
	.string "crosses the water without paying!$"

CrescentCity_BlacksnakeBase_Text_WaterDefeat:
	.string "Washed out!$"

CrescentCity_BlacksnakeBase_Text_WaterAfter:
	.string "I only joined for the hot meals.\n"
	.string "...And a bed. And someone to ask\p"
	.string "where I'd been all day.$"

CrescentCity_BlacksnakeBase_Text_LieutenantIntro:
	.string "ODETTE: RITA warned me about a\n"
	.string "meddling child. She said you'd be\p"
	.string "polite and in the way. Both true.\n"
	.string "Let's see how in the way you are!$"

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
	.string "WREN: I'll hold the hall. You\n"
	.string "take them one at a time, fair?\p"
	.string "The carving's at the back. Don't\n"
	.string "let them pull it apart.$"

CrescentCity_BlacksnakeBase_Text_WrenLook:
	.string "WREN: That's the last of them.\n"
	.string "Look at the carving. Please.$"

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
	.string "WREN: That's wrong. Those words\n"
	.string "go on. “Laid down to guard.” I\p"
	.string "know them by heart. Somebody\n"
	.string "chipped off the rest, on purpose.\p"
	.string "So that it says “laid low.”\n"
	.string "That the Long One was killed.$"

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

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---
