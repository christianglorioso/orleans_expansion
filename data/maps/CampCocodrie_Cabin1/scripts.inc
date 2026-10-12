CampCocodrie_Cabin1_MapScripts::
	.byte 0

@ The filé (cook-off ingredient): the old neighbour only gives it to someone who asks nicely (a two-choice menu; the wrong answer
@ just earns a scolding and a retry).
CampCocodrie_Cabin1_EventScript_OldNeighbour0::
	lock
	faceplayer
	goto_if_set FLAG_CAMP_FILE, CampCocodrie_Cabin1_EventScript_Done
	msgbox CampCocodrie_Cabin1_Text_Ask, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 2, 0, DYN_MULTICHOICE_CB_NONE, CampCocodrie_Cabin1_Text_Rude, CampCocodrie_Cabin1_Text_Polite
	switch VAR_RESULT
	case 1, CampCocodrie_Cabin1_EventScript_Gives
	case 0, CampCocodrie_Cabin1_EventScript_Scolds
	release
	end

CampCocodrie_Cabin1_EventScript_Gives:
	setflag FLAG_CAMP_FILE
	msgbox CampCocodrie_Cabin1_Text_Gives, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Cabin1_EventScript_Scolds:
	msgbox CampCocodrie_Cabin1_Text_Scolds, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Cabin1_EventScript_Done:
	msgbox CampCocodrie_Cabin1_Text_Done, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Cabin1_Text_Ask:
	.string "OLD NEIGHBOUR: Hm? You want\n"
	.string "something. They always want\p"
	.string "something. Well? What is it?$"

CampCocodrie_Cabin1_Text_Rude:
	.string "Gimme the filé!$"

CampCocodrie_Cabin1_Text_Polite:
	.string "Could I please have some filé?$"

CampCocodrie_Cabin1_Text_Scolds:
	.string "OLD NEIGHBOUR: Gimme?! In my\n"
	.string "house? Manners cost nothing, child.\p"
	.string "Try again.$"

CampCocodrie_Cabin1_Text_Gives:
	.string "OLD NEIGHBOUR: Now THAT'S a request.\n"
	.string "Sassafras, ground fine, from the\p"
	.string "tree out back. Tell the brothers\n"
	.string "to stir it in last.\p"
	.string "{PLAYER} received the FILÉ!$"

CampCocodrie_Cabin1_Text_Done:
	.string "OLD NEIGHBOUR: Sassafras goes in\n"
	.string "last, or it goes stringy.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---
