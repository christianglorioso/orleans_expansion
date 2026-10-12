Route4_MapScripts::
	.byte 0

@ The riverboat landing's deckhand takes the player back to Crescent City's terminal. (The rest of Route 4 is Chapter 4's.)
Route4_EventScript_Deckhand::
	lock
	faceplayer
	msgbox Route4_Text_DeckhandOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route4_EventScript_DeckhandNo
	msgbox Route4_Text_DeckhandGo, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warp MAP_CRESCENT_CITY, 56, 51
	waitstate
	release
	end

Route4_EventScript_DeckhandNo:
	msgbox Route4_Text_DeckhandNo, MSGBOX_DEFAULT
	release
	end

Route4_Text_DeckhandOffer:
	.string "DECKHAND: The riverboat goes back\n"
	.string "to CRESCENT CITY. Heading back?$"

Route4_Text_DeckhandGo:
	.string "DECKHAND: Mind the gangway.$"

Route4_Text_DeckhandNo:
	.string "DECKHAND: She sails when you're\n"
	.string "ready. The river's not going\p"
	.string "anywhere.$"

@ --- mapgen: generated NPC scripts (begin) ---

Route4_EventScript_Trainer0::
	msgbox Route4_Text_Trainer0, MSGBOX_NPC
	end

Route4_Text_Trainer0:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_Trainer1::
	msgbox Route4_Text_Trainer1, MSGBOX_NPC
	end

Route4_Text_Trainer1:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_Trainer2::
	msgbox Route4_Text_Trainer2, MSGBOX_NPC
	end

Route4_Text_Trainer2:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_Trainer4::
	msgbox Route4_Text_Trainer4, MSGBOX_NPC
	end

Route4_Text_Trainer4:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_Trainer6::
	msgbox Route4_Text_Trainer6, MSGBOX_NPC
	end

Route4_Text_Trainer6:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_Trainer8::
	msgbox Route4_Text_Trainer8, MSGBOX_NPC
	end

Route4_Text_Trainer8:
	.string "(Trainer: first-pass placeholder.)$"

Route4_EventScript_SignCity::
	msgbox Route4_Text_SignCity, MSGBOX_SIGN
	end

Route4_Text_SignCity:
	.string "POINTE ROUGE\nCity limits: welcome!$"

Route4_EventScript_RouteSign1::
	msgbox Route4_Text_RouteSign1, MSGBOX_SIGN
	end

Route4_Text_RouteSign1:
	.string "POINTE ROUGE FREIGHT YARD\nAuthorized personnel only.$"

Route4_EventScript_RouteSign2::
	msgbox Route4_Text_RouteSign2, MSGBOX_SIGN
	end

Route4_Text_RouteSign2:
	.string "RIVERBOAT LANDING\nTickets at the office.$"

@ --- mapgen: generated NPC scripts (end) ---
