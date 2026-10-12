StormsEdge_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, StormsEdge_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, StormsEdge_OnLoad
	map_script MAP_SCRIPT_ON_FRAME_TABLE, StormsEdge_OnFrameTable
	.byte 0

@ The drawbridge: map.bin has it lowered (surfers pass under it). Until the power grid is restored
@ (FLAG_STORMS_EDGE_GRID_RESTORED, set by beating Eclair in the substation gym) the raised state is swapped in: both leaves up,
@ the middle open (surfable), barriers across the deck stubs. StormsEdge_EventScript_StateBridgeRaised is written by
@ build.py from the spec's "states" (storms_edge.py), so its metatile ids always match the composed tileset.
@ The substation, the Center and the whole west bank are on the near side of the bridge (user decision 9, 2026-10-12): the
@ raised bridge is the only thing between the player and the east bank (the Mart, the lighthouse, the Route 3 causeway).
StormsEdge_OnLoad:
	call_if_unset FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_StateBridgeRaised
	end

@ Raichunite X lies in the substation yard but stays out of reach (its item flag is
@ held set) until the grid is back, when the gym victory clears the flag.
StormsEdge_OnTransition:
	call_if_unset FLAG_RESPAWN_STORMS_EDGE_SET, StormsEdge_EventScript_FirstRespawn
	call_if_unset FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_HoldRaichuniteX
	end

@ Only the first arrival sets the respawn point here; a later visit must not override a Center healed at elsewhere (the Center
@ itself sets it every time the player walks in).
StormsEdge_EventScript_FirstRespawn:
	setflag FLAG_RESPAWN_STORMS_EDGE_SET
	setrespawn HEAL_LOCATION_STORMS_EDGE
	return

StormsEdge_EventScript_HoldRaichuniteX:
	setflag FLAG_UNUSED_0x28F
	return

@ ---------------------------------------------------------------- arrival from Route 2 (story 8 or 9 -> 10)
@ A frame script, so it runs however the player came in (both Route 2 roads, the quay). 8 is a save that cut the hedge back in
@ the slice build.
StormsEdge_OnFrameTable:
	map_script_2 VAR_ORLEANS_STORY, 8, StormsEdge_EventScript_Arrival
	map_script_2 VAR_ORLEANS_STORY, 9, StormsEdge_EventScript_Arrival
	.2byte 0

StormsEdge_EventScript_Arrival::
	lockall
	msgbox StormsEdge_Text_Arrival, MSGBOX_DEFAULT
	msgbox StormsEdge_Text_ArrivalLineworker, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 10
	releaseall
	end

@ ---------------------------------------------------------------- the town (lines change when the grid is back)
StormsEdge_EventScript_BridgeTender::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_TenderRestored
	msgbox StormsEdge_Text_TenderRaised, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_TenderRestored:
	msgbox StormsEdge_Text_TenderRestored, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_Deckhand::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_DeckhandRestored
	msgbox StormsEdge_Text_DeckhandRaised, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_DeckhandRestored:
	msgbox StormsEdge_Text_DeckhandRestored, MSGBOX_DEFAULT
	release
	end

@ Eclair waits at the substation gate until the player has been inside (StormsEdge_Gym_OnTransition hides her: she is at her
@ control desk from then on), so she only ever has this line.
StormsEdge_EventScript_Eclair::
	msgbox StormsEdge_Text_EclairOutside, MSGBOX_NPC
	end

StormsEdge_EventScript_Lineman::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_LinemanAfter
	msgbox StormsEdge_Text_Lineman, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_LinemanAfter:
	msgbox StormsEdge_Text_LinemanAfter, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_Keeper::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_KeeperAfter
	msgbox StormsEdge_Text_Keeper, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_KeeperAfter:
	msgbox StormsEdge_Text_KeeperAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
StormsEdge_Text_Arrival:
	.string "The road ends at a battered port.\n"
	.string "Wires sag across the river mouth.\p"
	.string "The street is dark. Only a\n"
	.string "generator hums somewhere.$"

StormsEdge_Text_ArrivalLineworker:
	.string "A lineworker shouts from a pole:\n"
	.string "“Bridge is up! Grid is down!\p"
	.string "ÉCLAIR's crew works the substation\n"
	.string "at the west end. Go see her!”$"

StormsEdge_Text_TenderRaised:
	.string "BRIDGE TENDER: The surge fried the\n"
	.string "bridge motor. She stays up till\p"
	.string "the power's back. Nothing crosses\n"
	.string "to the east bank till then.$"

StormsEdge_Text_TenderRestored:
	.string "BRIDGE TENDER: Hear that hum? The\n"
	.string "motor's running again. Thank you!$"

StormsEdge_Text_DeckhandRaised:
	.string "DECKHAND: The bridge motor's fried.\n"
	.string "Nothing crosses till the grid is\p"
	.string "back. I'm stuck on this bank,\n"
	.string "watching the water.$"

StormsEdge_Text_DeckhandRestored:
	.string "DECKHAND: The bridge works again.\n"
	.string "I can finally go home!$"

StormsEdge_Text_EclairOutside:
	.string "ÉCLAIR: The whole grid tripped when\n"
	.string "the storm hit. My crew is inside.\p"
	.string "The control desk routes the whole\n"
	.string "grid. Light up all its junctions,\p"
	.string "and the street lights come back.\n"
	.string "Do that, and we'll talk badges.$"

StormsEdge_Text_Lineman:
	.string "Three poles down in one night.\n"
	.string "Stay clear of those wires!$"

StormsEdge_Text_LinemanAfter:
	.string "Power's back on the whole street.\n"
	.string "Now to re-hang the poles properly.$"

StormsEdge_Text_Keeper:
	.string "My lamp's been dark since the\n"
	.string "storm. Ships can't find the mouth.$"

StormsEdge_Text_KeeperAfter:
	.string "The lamp's lit! I could hug that\n"
	.string "ÉCLAIR. Maybe I will.$"
