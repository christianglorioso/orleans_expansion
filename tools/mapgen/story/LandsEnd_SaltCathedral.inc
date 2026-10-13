LandsEnd_SaltCathedral_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LandsEnd_SaltCathedral_OnTransitionPG
	.byte 0

@ The Salt Cathedral (Chapter 9, F.2): Groudon waits in the lowest pit (story >= 39). A trainer battle with Primal Groudon (its Red Orb makes
@ Desolate Land: Water attacks fail all fight); a win calms it (FLAG_GROUDON_CALMED). The exit mat leaves by script to Route 24.
LandsEnd_SaltCathedral_EventScript_GroudonRaid0::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 39, LandsEnd_SaltCathedral_EventScript_NotYet
	msgbox LandsEnd_SaltCathedral_Text_GroudonIntro, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_ORLEANS_GROUDON_RAID, LandsEnd_SaltCathedral_Text_GroudonDefeat
	msgbox LandsEnd_SaltCathedral_Text_GroudonCalm, MSGBOX_DEFAULT
	setflag FLAG_GROUDON_CALMED
	setflag FLAG_HIDE_GROUDON_RAID
	removeobject LOCALID_LANDS_END_SALT_CATHEDRAL_GROUDON_RAID0
	goto LandsEnd_SaltCathedral_EventScript_RaidDone

LandsEnd_SaltCathedral_EventScript_NotYet:
	msgbox LandsEnd_SaltCathedral_Text_NotYet, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_SaltCathedral_EventScript_Exit::
	lockall
	fadescreen FADE_TO_BLACK
	warpsilent MAP_ORLEANS_ROUTE24, 34, 7
	waitstate
	releaseall
	end

@ The second raid done: story 40, the channel to the Oldest Shrine opens (FLAG_ROUTE25_OPEN), and the dusk ceremony at the Old Water follows.
LandsEnd_SaltCathedral_EventScript_RaidDone:
	goto_if_unset FLAG_KYOGRE_CALMED, LandsEnd_SaltCathedral_EventScript_OneLeft
	setflag FLAG_ROUTE25_OPEN
	call_if_eq VAR_ORLEANS_STORY, 39, LandsEnd_SaltCathedral_EventScript_SetStory40
	msgbox LandsEnd_SaltCathedral_Text_BothDone, MSGBOX_DEFAULT
	closemessage
	setvar VAR_OLD_WATER_CEREMONY, 1
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER, 22, 32
	waitstate
	releaseall
	end

LandsEnd_SaltCathedral_EventScript_SetStory40:
	setvar VAR_ORLEANS_STORY, 40
	return

LandsEnd_SaltCathedral_EventScript_OneLeft:
	msgbox LandsEnd_SaltCathedral_Text_OneLeft, MSGBOX_DEFAULT
	releaseall
	end

LandsEnd_SaltCathedral_Text_GroudonIntro:
	.string "The Salt Cathedral: white pillars,\n"
	.string "red light climbing from the cracks.\p"
	.string "GROUDON stands in the lowest pit,\n"
	.string "its markings burning. Heat shimmers.$"

LandsEnd_SaltCathedral_Text_GroudonDefeat:
	.string "GROUDON kneels, its glow dimming.$"

LandsEnd_SaltCathedral_Text_GroudonCalm:
	.string "The song reaches it. GROUDON settles\n"
	.string "into the salt like a hill, and the\p"
	.string "cracks go dark. The land remembers.$"

LandsEnd_SaltCathedral_Text_OneLeft:
	.string "One sleeper is calm. The other waits\n"
	.string "behind the ruin door off ROUTE 22:\p"
	.string "KYOGRE, in the DROWNED TEMPLE.$"

LandsEnd_SaltCathedral_Text_BothDone:
	.string "Far away, a storm wall breaks. The\n"
	.string "channel to the SHRINE is open. A\p"
	.string "pale light calls from the OLD\n"
	.string "WATER.$"

LandsEnd_SaltCathedral_Text_NotYet:
	.string "The heat pushes you back. Not yet.$"

LandsEnd_SaltCathedral_OnTransitionPG:
	call LandsEnd_SaltCathedral_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
LandsEnd_SaltCathedral_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, LandsEnd_SaltCathedral_EventScript_PGHide
	goto_if_lt VAR_ORLEANS_STORY, 45, LandsEnd_SaltCathedral_EventScript_PGSetupDone
	call_if_ne VAR_ORLEANS_LEGENDARY_PICK, 1, LandsEnd_SaltCathedral_EventScript_PGHideGroudonRe
LandsEnd_SaltCathedral_EventScript_PGSetupDone:
	return

LandsEnd_SaltCathedral_EventScript_PGHide:
	setflag FLAG_PG_GROUDON_RE
	return

LandsEnd_SaltCathedral_EventScript_Pggroudon_re1::
	lock
	faceplayer
	playmoncry SPECIES_GROUDON, CRY_MODE_ENCOUNTER
	msgbox LandsEnd_SaltCathedral_Text_PGGroudonRe, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_GROUDON, 70
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, LandsEnd_SaltCathedral_EventScript_Pggroudon_re1Done
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, LandsEnd_SaltCathedral_EventScript_Pggroudon_re1Still
	release
	end

LandsEnd_SaltCathedral_EventScript_Pggroudon_re1Still:
	msgbox LandsEnd_SaltCathedral_Text_PGStillGroudonRe, MSGBOX_DEFAULT
	release
	end

LandsEnd_SaltCathedral_EventScript_Pggroudon_re1Done:
	setflag FLAG_PG_GROUDON_RE
	removeobject LOCALID_LANDS_END_SALT_CATHEDRAL_PGGROUDON_RE1
	release
	end

LandsEnd_SaltCathedral_EventScript_PGHideGroudonRe:
	setflag FLAG_PG_GROUDON_RE
	return

LandsEnd_SaltCathedral_Text_PGGroudonRe:
	.string "GROUDON stands before you,\n"
	.string "the floor cracking with heat.$"

LandsEnd_SaltCathedral_Text_PGStillGroudonRe:
	.string "GROUDON shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---
