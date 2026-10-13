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
	setflag FLAG_VISITED_STORMS_EDGE
	call StormsEdge_EventScript_StoryWeather
	call StormsEdge_EventScript_PGSetup
	call_if_unset FLAG_RESPAWN_STORMS_EDGE_SET, StormsEdge_EventScript_FirstRespawn
	call_if_unset FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_HoldRaichuniteX
	end

@ weather (weather_plan.py): thunderstorm until the grid is back, then clear. Runs from OnTransition, before the weather starts.
StormsEdge_EventScript_StoryWeather:
	goto_if_unset FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_EventScript_StoryWeatherDone
	setweather WEATHER_NONE
StormsEdge_EventScript_StoryWeatherDone:
	return

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

@ --- post-game (gen_postgame.py) ---

@ OnTransition: everything is hidden below story 45; at 45 and above the conditional ones decide for themselves
StormsEdge_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, StormsEdge_EventScript_PGHide
StormsEdge_EventScript_PGSetupDone:
	return

StormsEdge_EventScript_PGHide:
	setflag FLAG_PG_ZAPDOS
	return

StormsEdge_EventScript_PgZapdos::
	lock
	faceplayer
	playmoncry SPECIES_ZAPDOS, CRY_MODE_ENCOUNTER
	msgbox StormsEdge_Text_PGZapdos, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ZAPDOS, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, StormsEdge_EventScript_PgZapdosDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, StormsEdge_EventScript_PgZapdosStill
	release
	end

StormsEdge_EventScript_PgZapdosStill:
	msgbox StormsEdge_Text_PGStillZapdos, MSGBOX_DEFAULT
	release
	end

StormsEdge_EventScript_PgZapdosDone:
	setflag FLAG_PG_ZAPDOS
	removeobject LOCALID_STORMS_EDGE_PG_ZAPDOS
	release
	end

StormsEdge_Text_PGZapdos:
	.string "ZAPDOS stands before you,\n"
	.string "crackling with stored lightning.$"

StormsEdge_Text_PGStillZapdos:
	.string "ZAPDOS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

StormsEdge_EventScript_Fisherman::
	msgbox StormsEdge_Text_Fisherman, MSGBOX_NPC
	end

StormsEdge_Text_Fisherman:
	.string "After a blow the fish crowd the\nriver mouth. Got a rod, kid?$"

StormsEdge_EventScript_Kid::
	msgbox StormsEdge_Text_Kid, MSGBOX_NPC
	end

StormsEdge_Text_Kid:
	.string "The poles hum when the wind blows.\nZzzzt! Zzzzt!$"

StormsEdge_EventScript_Fishmonger::
	msgbox StormsEdge_Text_Fishmonger, MSGBOX_NPC
	end

StormsEdge_Text_Fishmonger:
	.string "Shrimp's cheap today. The boats\ncome and go with the tide.$"

StormsEdge_EventScript_Sailor::
	msgbox StormsEdge_Text_Sailor, MSGBOX_NPC
	end

StormsEdge_Text_Sailor:
	.string "The surge came right up to the\nstilts. That's what they're for!$"

StormsEdge_EventScript_Granny::
	msgbox StormsEdge_Text_Granny, MSGBOX_NPC
	end

StormsEdge_Text_Granny:
	.string "We raised our houses after the last\nbig storm. Saved us again.$"

StormsEdge_EventScript_Boy::
	msgbox StormsEdge_Text_Boy, MSGBOX_NPC
	end

StormsEdge_Text_Boy:
	.string "ECLAIR's crew keeps the substation\nhumming. Listen to it!$"

StormsEdge_EventScript_SignWest::
	msgbox StormsEdge_Text_SignWest, MSGBOX_SIGN
	end

StormsEdge_Text_SignWest:
	.string "STORM'S EDGE\nThe port at the river's mouth.$"

StormsEdge_EventScript_SignEast::
	msgbox StormsEdge_Text_SignEast, MSGBOX_SIGN
	end

StormsEdge_Text_SignEast:
	.string "STORM'S EDGE\nWest: the drawbridge. East: Route 3.$"

StormsEdge_EventScript_SignLighthouse::
	msgbox StormsEdge_Text_SignLighthouse, MSGBOX_SIGN
	end

StormsEdge_Text_SignLighthouse:
	.string "STORM'S EDGE LIGHT\nKeep off the rocks below.$"

StormsEdge_EventScript_SignSubstation::
	msgbox StormsEdge_Text_SignSubstation, MSGBOX_SIGN
	end

StormsEdge_Text_SignSubstation:
	.string "STORM'S EDGE SUBSTATION\nDANGER: HIGH VOLTAGE. GYM INSIDE.$"

StormsEdge_EventScript_StateBridgeRaised::
	setmetatile 24, 15, 0x26D, TRUE
	setmetatile 24, 16, 0x26E, TRUE
	setmetatile 24, 17, 0x26F, TRUE
	setmetatile 24, 18, 0x270, TRUE
	setmetatile 27, 15, 0x271, TRUE
	setmetatile 27, 16, 0x272, TRUE
	setmetatile 27, 17, 0x273, TRUE
	setmetatile 27, 18, 0x274, TRUE
	setmetatile 25, 15, 0x033, FALSE
	setmetatile 25, 16, 0x033, FALSE
	setmetatile 25, 17, 0x033, FALSE
	setmetatile 25, 18, 0x033, FALSE
	setmetatile 26, 15, 0x033, FALSE
	setmetatile 26, 16, 0x033, FALSE
	setmetatile 26, 17, 0x033, FALSE
	setmetatile 26, 18, 0x033, FALSE
	setmetatile 23, 16, 0x275, TRUE
	setmetatile 23, 17, 0x276, TRUE
	setmetatile 28, 16, 0x277, TRUE
	setmetatile 28, 17, 0x278, TRUE
	return

@ --- mapgen: generated NPC scripts (end) ---
