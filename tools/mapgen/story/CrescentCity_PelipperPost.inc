CrescentCity_PelipperPost_MapScripts::
	.byte 0

@ The Pelipper Post flies the player to the Old Water once the Rootkin's channel is open (story >= 6). The boatman at the Old
@ Water's canoe docks has the way back (OldWater_CanoeDocks.inc).
CrescentCity_PelipperPost_EventScript_PelipperHandler1::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 6, CrescentCity_PelipperPost_EventScript_Birds
	msgbox CrescentCity_PelipperPost_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_PelipperPost_EventScript_Declined
	msgbox CrescentCity_PelipperPost_Text_Go, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	warp MAP_OLD_WATER, 24, 35
	waitstate
	release
	end

CrescentCity_PelipperPost_EventScript_Birds:
	msgbox CrescentCity_PelipperPost_Text_Birds, MSGBOX_DEFAULT
	release
	end

CrescentCity_PelipperPost_EventScript_Declined:
	msgbox CrescentCity_PelipperPost_Text_Declined, MSGBOX_DEFAULT
	release
	end

CrescentCity_PelipperPost_Text_Birds:
	.string "HANDLER: The birds know every roof\n"
	.string "in the city. Every roof, and a few\p"
	.string "places nobody's mapped yet.\n"
	.string "Ask again when you've been out.$"

CrescentCity_PelipperPost_Text_Offer:
	.string "HANDLER: One of my birds knows a\n"
	.string "hidden place in the bayou. The Old\p"
	.string "Water, they call it. It'll carry\n"
	.string "you there. Fancy a flight?$"

CrescentCity_PelipperPost_Text_Go:
	.string "HANDLER: Hold on tight. Pelipper\n"
	.string "don't do gentle.$"

CrescentCity_PelipperPost_Text_Declined:
	.string "HANDLER: The bird will wait. It\n"
	.string "has nothing better to do.$"
