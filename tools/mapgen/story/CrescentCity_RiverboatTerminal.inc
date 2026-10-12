CrescentCity_RiverboatTerminal_MapScripts::
	.byte 0

@ The riverboat to Pointe Rouge opens with the third badge (the BADGE is the pass). The ride lands at Route 4's riverboat
@ landing (Chapter 4 begins: story 18 = reached Pointe Rouge's road); a deckhand there rides back.
CrescentCity_RiverboatTerminal_EventScript_TicketClerk0::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_RiverboatTerminal_EventScript_NoPass
	goto_if_lt VAR_ORLEANS_STORY, 17, CrescentCity_RiverboatTerminal_EventScript_Waiting
	msgbox CrescentCity_RiverboatTerminal_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_RiverboatTerminal_EventScript_Declined
	msgbox CrescentCity_RiverboatTerminal_Text_Boarding, MSGBOX_DEFAULT
	closemessage
	call_if_lt VAR_ORLEANS_STORY, 18, CrescentCity_RiverboatTerminal_EventScript_SetReached
	fadescreen FADE_TO_BLACK
	warp MAP_ORLEANS_ROUTE4, 19, 43
	waitstate
	release
	end

CrescentCity_RiverboatTerminal_EventScript_SetReached:
	setvar VAR_ORLEANS_STORY, 18
	return

@ the boat leaves only after the Drowned Ward is dealt with (story 17: the carving was found)
CrescentCity_RiverboatTerminal_EventScript_Waiting:
	msgbox CrescentCity_RiverboatTerminal_Text_Waiting, MSGBOX_DEFAULT
	release
	end

CrescentCity_RiverboatTerminal_EventScript_NoPass:
	msgbox CrescentCity_RiverboatTerminal_Text_NoPass, MSGBOX_DEFAULT
	release
	end

CrescentCity_RiverboatTerminal_EventScript_Declined:
	msgbox CrescentCity_RiverboatTerminal_Text_Declined, MSGBOX_DEFAULT
	release
	end

CrescentCity_RiverboatTerminal_Text_NoPass:
	.string "TICKET CLERK: The riverboat to\n"
	.string "POINTE ROUGE? The pass is the\p"
	.string "third BADGE. FIFOLET's, in the old\n"
	.string "cemetery. Come back with it.$"

CrescentCity_RiverboatTerminal_Text_Offer:
	.string "TICKET CLERK: A third BADGE! That's\n"
	.string "your pass. The riverboat to\p"
	.string "POINTE ROUGE leaves now. Board?$"

CrescentCity_RiverboatTerminal_Text_Boarding:
	.string "TICKET CLERK: All aboard! Watch\n"
	.string "your step on the gangway.$"

CrescentCity_RiverboatTerminal_Text_Declined:
	.string "TICKET CLERK: Another boat leaves\n"
	.string "in an hour. They always do.$"

CrescentCity_RiverboatTerminal_Text_Waiting:
	.string "TICKET CLERK: Your pass is good. But\nthe pilot is waiting on word from\p"
	.string "the Drowned Ward. Something about a\ncarving. Sort that out first.$"
