OldWater_CanoeDocks_MapScripts::
	.byte 0

@ canoe travel back to Route 1's boat landing
OldWater_CanoeDocks_EventScript_Boatman0::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 6, OldWater_CanoeDocks_EventScript_BoatmanTupeloFirst
	goto_if_ge VAR_ORLEANS_STORY, 45, OldWater_CanoeDocks_EventScript_BoatmanPool
OldWater_CanoeDocks_EventScript_BoatmanLanding:
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
	.string "in the song house. North, up the\p"
	.string "walkways.$"

@ From story 45 the boatman knows the way to Uxie's Knowing Pool (OldWater_KnowingPool, story/OldWater_KnowingPool.inc): a script warp, no change to the town
@ ...and only with the Mist Weaver trophy (Set Misty Terrain 10 times in the Battle Frontier): the same trophy opens all three pools (Uxie, Mesprit, Azelf). Re-checked at every talk.
OldWater_CanoeDocks_EventScript_BoatmanPool:
	setvar VAR_0x8004, ACH_MIST_WEAVER
	call LairGate_EventScript_Check
	goto_if_eq VAR_RESULT, FALSE, OldWater_CanoeDocks_EventScript_BoatmanPoolSealed
	msgbox OldWater_CanoeDocks_Text_BoatmanPoolOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OldWater_CanoeDocks_EventScript_BoatmanLanding
	msgbox OldWater_CanoeDocks_Text_BoatmanPoolGo, MSGBOX_DEFAULT
	closemessage
	warp MAP_OLD_WATER_KNOWING_POOL, 10, 13
	waitstate
	release
	end

OldWater_CanoeDocks_EventScript_BoatmanPoolSealed:
	msgbox OldWater_CanoeDocks_Text_BoatmanPoolSealed, MSGBOX_DEFAULT
	goto OldWater_CanoeDocks_EventScript_BoatmanLanding

OldWater_CanoeDocks_Text_BoatmanPoolSealed:
	.string "BOATMAN: The Knowing Pool is shut\n"
	.string "to everyone. The reeds know it.\p"
	.string "It needs a trophy: Set Misty\n"
	.string "Terrain 10 times in the Frontier.$"

OldWater_CanoeDocks_Text_BoatmanPoolOffer:
	.string "BOATMAN: Want a paddle out to the\n"
	.string "Knowing Pool in the reeds?$"

OldWater_CanoeDocks_Text_BoatmanPoolGo:
	.string "BOATMAN: Keep your voice low.\n"
	.string "It listens.$"
