CrescentCity_NameRater_MapScripts::
	.byte 0

@ The Name Rater: renames POKéMON for free
CrescentCity_NameRater_EventScript_NameRater0::
	lock
	faceplayer
	msgbox CrescentCity_NameRater_Text_Welcome, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_NameRater_EventScript_Declined
	getpartysize
	goto_if_eq VAR_RESULT, 0, CrescentCity_NameRater_EventScript_Declined
	msgbox CrescentCity_NameRater_Text_Which, MSGBOX_DEFAULT
	special ChoosePartyMon
	waitstate
	goto_if_ge VAR_0x8004, PARTY_SIZE, CrescentCity_NameRater_EventScript_Declined
	specialvar VAR_RESULT, ScriptGetPartyMonSpecies
	goto_if_eq VAR_RESULT, SPECIES_EGG, CrescentCity_NameRater_EventScript_Egg
	msgbox CrescentCity_NameRater_Text_NewName, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_NameRater_EventScript_Declined
	call Common_EventScript_NameReceivedPartyMon
	setvar VAR_0x8004, ACH_A_NAME_OF_ITS_OWN
	special Achievement_UnlockVar8004
	msgbox CrescentCity_NameRater_Text_Done, MSGBOX_DEFAULT
	release
	end

CrescentCity_NameRater_EventScript_Egg:
	msgbox CrescentCity_NameRater_Text_Egg, MSGBOX_DEFAULT
	release
	end

CrescentCity_NameRater_EventScript_Declined:
	msgbox CrescentCity_NameRater_Text_Declined, MSGBOX_DEFAULT
	release
	end

CrescentCity_NameRater_Text_Welcome:
	.string "NAME RATER: A name is a promise.\n"
	.string "Would you like me to help you\p"
	.string "pick a better one? It's free.$"

CrescentCity_NameRater_Text_Which:
	.string "Which POKéMON's name?$"

CrescentCity_NameRater_Text_NewName:
	.string "A fine choice. Shall we give it a\n"
	.string "new name?$"

CrescentCity_NameRater_Text_Done:
	.string "NAME RATER: A splendid name! It\n"
	.string "suits it down to the ground.$"

CrescentCity_NameRater_Text_Egg:
	.string "NAME RATER: An Egg? It hasn't\n"
	.string "decided who it is yet.$"

CrescentCity_NameRater_Text_Declined:
	.string "NAME RATER: As you wish. A name\n"
	.string "will keep. Come back any time.$"
