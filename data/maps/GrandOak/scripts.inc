GrandOak_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, GrandOak_OnTransition
	.byte 0

@ The first arrival sets the respawn point (a blackout on Route 2 returns here even if the Center was never entered). Only the
@ first: a later visit must not override a Center healed at in another town.
GrandOak_OnTransition:
	setflag FLAG_VISITED_GRAND_OAK
	call_if_unset FLAG_RESPAWN_GRAND_OAK_SET, GrandOak_EventScript_FirstRespawn
	end

GrandOak_EventScript_FirstRespawn:
	setflag FLAG_RESPAWN_GRAND_OAK_SET
	setrespawn HEAL_LOCATION_GRAND_OAK
	return

@ The storm hedge on the road east (Route 2): cleared with Magnolia's Garden Shears. The road is three cells wide and the
@ rest of the east edge is a magnolia wall (grand_oak.py TREES), so this hedge is the only way through. Ch2 gate: the first
@ verse has to be home (VAR_ORLEANS_STORY >= 8) before the road opens; cutting it sets 9.
GrandOak_EventScript_StormHedge1::
GrandOak_EventScript_StormHedge2::
GrandOak_EventScript_StormHedge3::
	lockall
	goto_if_lt VAR_ORLEANS_STORY, 7, GrandOak_EventScript_HedgeTangled
	goto_if_lt VAR_ORLEANS_STORY, 8, GrandOak_EventScript_HedgeNotYet
	checkitem ITEM_GARDEN_SHEARS
	goto_if_eq VAR_RESULT, FALSE, GrandOak_EventScript_HedgeNoShears
	msgbox GrandOak_Text_UseShears, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, GrandOak_EventScript_HedgeEnd
	msgbox GrandOak_Text_ShearsCut, MSGBOX_DEFAULT
	closemessage
	removeobject LOCALID_GRAND_OAK_STORM_HEDGE_1
	removeobject LOCALID_GRAND_OAK_STORM_HEDGE_2
	removeobject LOCALID_GRAND_OAK_STORM_HEDGE_3
	setflag FLAG_CUT_STORM_HEDGE
	call_if_eq VAR_ORLEANS_STORY, 8, GrandOak_EventScript_Route2Open
	msgbox GrandOak_Text_RoadEast, MSGBOX_DEFAULT
GrandOak_EventScript_HedgeEnd:
	releaseall
	end

GrandOak_EventScript_Route2Open:
	setvar VAR_ORLEANS_STORY, 9
	return

GrandOak_EventScript_HedgeTangled:
	msgbox GrandOak_Text_HedgeTangled, MSGBOX_DEFAULT
	releaseall
	end

GrandOak_EventScript_HedgeNoShears:
	msgbox GrandOak_Text_HedgeNoShears, MSGBOX_DEFAULT
	releaseall
	end

GrandOak_EventScript_HedgeNotYet:
	msgbox GrandOak_Text_HedgeNotYet, MSGBOX_DEFAULT
	releaseall
	end

@ step 10: the epilogue, Wren waiting outside the gym
GrandOak_EventScript_WrenEpilogue::
	lockall
	clearflag FLAG_HIDE_GRAND_OAK_WREN
	addobject LOCALID_GRAND_OAK_WREN
	msgbox GrandOak_Text_WrenEpilogue, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_HIDE_GRAND_OAK_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_GRAND_OAK_WREN
	msgbox GrandOak_Text_BackThroughTheReeds, MSGBOX_DEFAULT
	closemessage
	warp MAP_OLD_WATER_SONG_HOUSE, 9, 3
	waitstate
	releaseall
	end

GrandOak_EventScript_Wren::
	msgbox GrandOak_Text_WrenEpilogue, MSGBOX_NPC
	end

GrandOak_Text_HedgeNotYet:
	.string "A hedge the storm tangled into a\n"
	.string "wall. It can wait.\p"
	.string "TUPELO is expecting the first\n"
	.string "verse back at the OLD WATER.$"

GrandOak_Text_RoadEast:
	.string "The road east is open!\p"
	.string "ROUTE 2 runs under the power\n"
	.string "lines to STORM'S EDGE.$"

GrandOak_Text_HedgeTangled:
	.string "A hedge the storm tangled into a\n"
	.string "wall. It needs cutting back.$"

GrandOak_Text_HedgeNoShears:
	.string "It needs cutting back. MAGNOLIA\n"
	.string "has GARDEN SHEARS for it.$"

GrandOak_Text_UseShears:
	.string "Use the GARDEN SHEARS?$"

GrandOak_Text_ShearsCut:
	.string "{PLAYER} cut back the hedge!$"

GrandOak_Text_WrenEpilogue:
	.string "WREN: You got her verse!\n"
	.string "The whole hall is cheering!\p"
	.string "TUPELO will want to hear it from\n"
	.string "you. Come on!$"

GrandOak_Text_BackThroughTheReeds:
	.string "WREN paddles you back through\n"
	.string "the reeds to the OLD WATER...$"

@ --- mapgen: generated NPC scripts (begin) ---

GrandOak_EventScript_FloetteGardener::
	msgbox GrandOak_Text_FloetteGardener, MSGBOX_NPC
	end

GrandOak_Text_FloetteGardener:
	.string "The magnolias are late this year.\nCome back after the storms.$"

GrandOak_EventScript_Recruiter1::
	msgbox GrandOak_Text_Recruiter1, MSGBOX_NPC
	end

GrandOak_Text_Recruiter1:
	.string "Rita's paying good money for\nstrong hands. Rebuild with us!$"

GrandOak_EventScript_Recruiter2::
	msgbox GrandOak_Text_Recruiter2, MSGBOX_NPC
	end

GrandOak_Text_Recruiter2:
	.string "Sign up today. The bayou\nwon't fix itself.$"

GrandOak_EventScript_TownSign::
	msgbox GrandOak_Text_TownSign, MSGBOX_SIGN
	end

GrandOak_Text_TownSign:
	.string "GRAND OAK\nWhere the old oaks keep the town.$"

@ --- mapgen: generated NPC scripts (end) ---
