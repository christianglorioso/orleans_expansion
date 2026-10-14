PointeRouge_IcePlant_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_IcePlant_OnTransitionPG
	.byte 0

PointeRouge_IcePlant_OnTransitionPG:
	call PointeRouge_IcePlant_EventScript_PGSetup
	end

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
PointeRouge_IcePlant_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, PointeRouge_IcePlant_EventScript_PGHide
PointeRouge_IcePlant_EventScript_PGSetupDone:
	return

PointeRouge_IcePlant_EventScript_PGHide:
	setflag FLAG_PG_ARTICUNO
	return

PointeRouge_IcePlant_EventScript_Pgarticuno0::
	lock
	faceplayer
	playmoncry SPECIES_ARTICUNO, CRY_MODE_ENCOUNTER
	msgbox PointeRouge_IcePlant_Text_PGArticuno, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_ARTICUNO, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, PointeRouge_IcePlant_EventScript_Pgarticuno0Done
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, PointeRouge_IcePlant_EventScript_Pgarticuno0Still
	release
	end

PointeRouge_IcePlant_EventScript_Pgarticuno0Still:
	msgbox PointeRouge_IcePlant_Text_PGStillArticuno, MSGBOX_DEFAULT
	release
	end

PointeRouge_IcePlant_EventScript_Pgarticuno0Done:
	setflag FLAG_PG_ARTICUNO
	removeobject LOCALID_POINTE_ROUGE_ICE_PLANT_PGARTICUNO0
	release
	end

PointeRouge_IcePlant_Text_PGArticuno:
	.string "ARTICUNO stands before you,\n"
	.string "frost spreading from its wings.$"

PointeRouge_IcePlant_Text_PGStillArticuno:
	.string "ARTICUNO shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---
