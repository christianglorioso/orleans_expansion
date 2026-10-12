CrescentCity_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CrescentCity_OnFrameTable
	.byte 0

@ The respawn point is set ONCE, in the arrival scene below (a blackout in the streets returns to the Quarter Center, not to
@ Storm's Edge). It must not be set on every load: that would override the Waterfront Center after healing there.

@ ---------------------------------------------------------------- Ch2 end: the first arrival (story 11 or 12 -> 13)
@ A frame script, so it runs however the player came in (any cell of the Route 3 causeway, or any other edge). 12 is the normal
@ case (Jayden beaten on the bridge); 11 means Jayden's trigger was missed, so the arrival also settles that beat.
CrescentCity_OnFrameTable:
	map_script_2 VAR_ORLEANS_STORY, 11, CrescentCity_EventScript_ArrivalSkippedJayden
	map_script_2 VAR_ORLEANS_STORY, 12, CrescentCity_EventScript_Arrival
	.2byte 0

CrescentCity_EventScript_ArrivalSkippedJayden::
	lockall
	setflag FLAG_HIDE_ROUTE3_JAYDEN
	msgbox CrescentCity_Text_JaydenAhead, MSGBOX_DEFAULT
	goto CrescentCity_EventScript_ArrivalScene

@ Quiet scene: the city, then a PokeNav message from Lafayette, who is already at the conservation center on the waterfront
@ (Ch3 starts there).
CrescentCity_EventScript_Arrival::
	lockall
CrescentCity_EventScript_ArrivalScene:
	msgbox CrescentCity_Text_Arrival1, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_Arrival2, MSGBOX_DEFAULT
	playse SE_PIN
	msgbox CrescentCity_Text_PokenavMessage, MSGBOX_DEFAULT
	setrespawn HEAL_LOCATION_CRESCENT_CITY
	setvar VAR_ORLEANS_STORY, 13
	releaseall
	end

@ ---------------------------------------------------------------- Route 14: the floodwater gate (until gym 6)
@ Every walkable cell of the bottom row inside the Route 14 connection (x 39-66) runs this (spec "triggers", story_overlay.py;
@ the trigger's var is the FLAG FLAG_BADGE06_GET with value 0, so it only fires while the flag is clear). The player is turned
@ back; the chapter that scripts Route 14 swaps this for the real water state (like Storm's Edge's bridge) and removes the
@ triggers. (NEVER "var": "0": TRIGGER_RUN_IMMEDIATELY freezes on a msgbox.)
CrescentCity_EventScript_FloodedRoad::
	lockall
	goto_if_set FLAG_BADGE06_GET, CrescentCity_EventScript_FloodedRoadOpen
	msgbox CrescentCity_Text_FloodedRoad, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, CrescentCity_Movement_StepBackNorth
	waitmovement 0
CrescentCity_EventScript_FloodedRoadOpen:
	releaseall
	end

CrescentCity_Movement_StepBackNorth:
	walk_up
	step_end

@ ---------------------------------------------------------------- text
CrescentCity_Text_Arrival1:
	.string "The causeway ends in lamplight and\n"
	.string "iron balconies.\p"
	.string "CRESCENT CITY. Every road in the\n"
	.string "region bends here, sooner or later.$"

CrescentCity_Text_Arrival2:
	.string "Brass music drifts from somewhere\n"
	.string "inside, thin over the flood-line\p"
	.string "stains on the old brick. The\n"
	.string "city is rebuilding too.$"

CrescentCity_Text_PokenavMessage:
	.string "Your POKéNAV buzzes. A message.\p"
	.string "LAFAYETTE: You made it to CRESCENT\n"
	.string "CITY! Come find me at the\p"
	.string "conservation center, down on the\n"
	.string "waterfront. I have a favor to ask.$"

CrescentCity_Text_JaydenAhead:
	.string "A boy in a grey hood slips through\n"
	.string "the crowd ahead, a bundle of\p"
	.string "snake-marked pamphlets under his\n"
	.string "arm. JAYDEN. He doesn't look back.$"

CrescentCity_Text_FloodedRoad:
	.string "Brown floodwater covers the levee\n"
	.string "road south of the city.\p"
	.string "It's far too deep to cross. It\n"
	.string "will have to go down first.$"

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_EventScript_FrontierGuard::
	msgbox CrescentCity_Text_FrontierGuard, MSGBOX_NPC
	end

CrescentCity_Text_FrontierGuard:
	.string "(The Battle Frontier opens after the\nRayquaza finale.)$"

CrescentCity_EventScript_ParadeLeader::
	msgbox CrescentCity_Text_ParadeLeader, MSGBOX_NPC
	end

CrescentCity_Text_ParadeLeader:
	.string "(Second-line parade leader:\nplaceholder.)$"

CrescentCity_EventScript_Lafayette::
	msgbox CrescentCity_Text_Lafayette, MSGBOX_NPC
	end

CrescentCity_Text_Lafayette:
	.string "(Lafayette: placeholder.)$"

CrescentCity_EventScript_Painter::
	msgbox CrescentCity_Text_Painter, MSGBOX_NPC
	end

CrescentCity_Text_Painter:
	.string "(Painter: the light on the pond is\nperfect today.)$"

CrescentCity_EventScript_ParkStroller::
	msgbox CrescentCity_Text_ParkStroller, MSGBOX_NPC
	end

CrescentCity_Text_ParkStroller:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_ParkKid::
	msgbox CrescentCity_Text_ParkKid, MSGBOX_NPC
	end

CrescentCity_Text_ParkKid:
	.string "(Kid: I saw something red in the\nlong grass!)$"

CrescentCity_EventScript_Mourner::
	msgbox CrescentCity_Text_Mourner, MSGBOX_NPC
	end

CrescentCity_Text_Mourner:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_Shopper::
	msgbox CrescentCity_Text_Shopper, MSGBOX_NPC
	end

CrescentCity_Text_Shopper:
	.string "(Shopper: placeholder.)$"

CrescentCity_EventScript_QuarterGent::
	msgbox CrescentCity_Text_QuarterGent, MSGBOX_NPC
	end

CrescentCity_Text_QuarterGent:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_QuarterLass::
	msgbox CrescentCity_Text_QuarterLass, MSGBOX_NPC
	end

CrescentCity_Text_QuarterLass:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_Sailor::
	msgbox CrescentCity_Text_Sailor, MSGBOX_NPC
	end

CrescentCity_Text_Sailor:
	.string "(Sailor: the riverboat sails for\nPointe Rouge.)$"

CrescentCity_EventScript_Fisherman::
	msgbox CrescentCity_Text_Fisherman, MSGBOX_NPC
	end

CrescentCity_Text_Fisherman:
	.string "(Fisherman: placeholder.)$"

CrescentCity_EventScript_Stroller::
	msgbox CrescentCity_Text_Stroller, MSGBOX_NPC
	end

CrescentCity_Text_Stroller:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_OldMan::
	msgbox CrescentCity_Text_OldMan, MSGBOX_NPC
	end

CrescentCity_Text_OldMan:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_VergeBoy::
	msgbox CrescentCity_Text_VergeBoy, MSGBOX_NPC
	end

CrescentCity_Text_VergeBoy:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_Busker::
	msgbox CrescentCity_Text_Busker, MSGBOX_NPC
	end

CrescentCity_Text_Busker:
	.string "(Busker: a tune for the shoppers.)$"

CrescentCity_EventScript_ShopMom::
	msgbox CrescentCity_Text_ShopMom, MSGBOX_NPC
	end

CrescentCity_Text_ShopMom:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_ConservationKid::
	msgbox CrescentCity_Text_ConservationKid, MSGBOX_NPC
	end

CrescentCity_Text_ConservationKid:
	.string "(Kid: there is a real alligator\ninside!)$"

CrescentCity_EventScript_FrontierJogger::
	msgbox CrescentCity_Text_FrontierJogger, MSGBOX_NPC
	end

CrescentCity_Text_FrontierJogger:
	.string "(Jogger: I'm training for the\nFrontier.)$"

CrescentCity_EventScript_FrontierPair::
	msgbox CrescentCity_Text_FrontierPair, MSGBOX_NPC
	end

CrescentCity_Text_FrontierPair:
	.string "(Townsperson: placeholder.)$"

CrescentCity_EventScript_FrontierFan::
	msgbox CrescentCity_Text_FrontierFan, MSGBOX_NPC
	end

CrescentCity_Text_FrontierFan:
	.string "(Fan: one day I'll battle at the\nDome.)$"

CrescentCity_EventScript_Picnicker::
	msgbox CrescentCity_Text_Picnicker, MSGBOX_NPC
	end

CrescentCity_Text_Picnicker:
	.string "(Picnicker: the levee breeze is\nlovely.)$"

CrescentCity_EventScript_CemeterySign::
	msgbox CrescentCity_Text_CemeterySign, MSGBOX_SIGN
	end

CrescentCity_Text_CemeterySign:
	.string "OLD CEMETERY\nFifolet Gym ahead.\pFollow the steady blue lights;\nthe flickering ones lead astray.$"

CrescentCity_EventScript_OldCypressSign::
	msgbox CrescentCity_Text_OldCypressSign, MSGBOX_SIGN
	end

CrescentCity_Text_OldCypressSign:
	.string "THE OLD CYPRESS\nThe oldest tree in the park.$"

CrescentCity_EventScript_CitySign::
	msgbox CrescentCity_Text_CitySign, MSGBOX_SIGN
	end

CrescentCity_Text_CitySign:
	.string "CRESCENT CITY\nThe Crescent on the Emerald River.$"

CrescentCity_EventScript_ParkSign::
	msgbox CrescentCity_Text_ParkSign, MSGBOX_SIGN
	end

CrescentCity_Text_ParkSign:
	.string "CITY PARK\nPlease keep off the flower beds.$"

CrescentCity_EventScript_FrontierSign::
	msgbox CrescentCity_Text_FrontierSign, MSGBOX_SIGN
	end

CrescentCity_Text_FrontierSign:
	.string "BATTLE FRONTIER\nOpen to champions only.$"

CrescentCity_EventScript_LeveeSign::
	msgbox CrescentCity_Text_LeveeSign, MSGBOX_SIGN
	end

CrescentCity_Text_LeveeSign:
	.string "SOUTH: Route 14\nThe levee road.$"

@ --- mapgen: generated NPC scripts (end) ---
