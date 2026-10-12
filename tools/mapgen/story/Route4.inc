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
