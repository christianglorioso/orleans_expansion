OldWater_CanoeDocks_MapScripts::
	.byte 0

@ canoe travel back to Route 1's boat landing
OldWater_CanoeDocks_EventScript_Boatman0::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 6, OldWater_CanoeDocks_EventScript_BoatmanTupeloFirst
	msgbox OldWater_CanoeDocks_Text_BoatmanOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OldWater_CanoeDocks_EventScript_BoatmanNo
	msgbox OldWater_CanoeDocks_Text_BoatmanGo, MSGBOX_DEFAULT
	closemessage
	warp MAP_ORLEANS_ROUTE1, 10, 9
	waitstate
	release
	end

OldWater_CanoeDocks_EventScript_BoatmanNo:
	msgbox OldWater_CanoeDocks_Text_BoatmanNo, MSGBOX_DEFAULT
	release
	end

OldWater_CanoeDocks_EventScript_BoatmanTupeloFirst:
	msgbox OldWater_CanoeDocks_Text_BoatmanTupeloFirst, MSGBOX_DEFAULT
	release
	end

OldWater_CanoeDocks_Text_BoatmanOffer:
	.string "BOATMAN: Need a ride back to the\n"
	.string "boat landing?$"

OldWater_CanoeDocks_Text_BoatmanGo:
	.string "BOATMAN: Hold on to the sides.$"

OldWater_CanoeDocks_Text_BoatmanNo:
	.string "BOATMAN: The canoe's here when\n"
	.string "you need it.$"

OldWater_CanoeDocks_Text_BoatmanTupeloFirst:
	.string "BOATMAN: TUPELO's waiting for you\n"
	.string "in the song house. North, up the\l"
	.string "walkways.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---
