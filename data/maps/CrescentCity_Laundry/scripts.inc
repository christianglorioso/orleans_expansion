CrescentCity_Laundry_MapScripts::
	.byte 0

@ The ROTOM quest (after gym 3): a mischievous appliance. Before the badge it only pranks; after, the ROTOM inside battles (a wild
@ battle, level 22). The flag hides it once the battle is over, however it ended.
CrescentCity_Laundry_EventScript_RotomWasher1::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_Laundry_EventScript_RotomQuiet
	playmoncry SPECIES_ROTOM_WASH, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_Laundry_Text_RotomGo, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM_WASH, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CrescentCity_Laundry_EventScript_RotomDone
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_Laundry_EventScript_RotomDone
	release
	end

CrescentCity_Laundry_EventScript_RotomDone:
	setflag FLAG_CRESCENT_ROTOM_WASHER
	removeobject LOCALID_CRESCENT_CITY_LAUNDRY_ROTOM_WASHER1
	release
	end

CrescentCity_Laundry_EventScript_RotomQuiet:
	msgbox CrescentCity_Laundry_Text_RotomQuiet, MSGBOX_DEFAULT
	release
	end

CrescentCity_Laundry_Text_RotomQuiet:
	.string "The washer spins with nothing in\n"
	.string "it. Something inside is giggling.$"

CrescentCity_Laundry_Text_RotomGo:
	.string "The washer shudders and spins,\n"
	.string "empty. Soapy water sloshes.\p"
	.string "Suds fly everywhere! A ROTOM pops\n"
	.string "out of the washer, laughing!$"

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Laundry_EventScript_Owner0::
	msgbox CrescentCity_Laundry_Text_Owner0, MSGBOX_NPC
	end

CrescentCity_Laundry_Text_Owner0:
	.string "One machine keeps running with\nnothing in it. I've stopped asking.$"

@ --- mapgen: generated NPC scripts (end) ---
