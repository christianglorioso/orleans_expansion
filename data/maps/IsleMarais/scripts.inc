IsleMarais_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, IsleMarais_OnLoad
	.byte 0

IsleMarais_OnLoad:
	call_if_unset FLAG_BADGE01_GET, IsleMarais_EventScript_BoardUpPlayersHouse
	end

@ The player's house is boarded up until Magnolia is beaten; then Mom moves back in.
IsleMarais_EventScript_BoardUpPlayersHouse::
	setmetatile 16, 18, 573, TRUE   @ the cabin wall where the door was (a name, not an id: ids move when the tileset is recomposed)
	return

IsleMarais_EventScript_BoardedDoor::
	goto_if_set FLAG_BADGE01_GET, IsleMarais_EventScript_BoardedDoorEnd
	msgbox IsleMarais_Text_BoardedDoor, MSGBOX_SIGN
IsleMarais_EventScript_BoardedDoorEnd:
	end

@ step 4: the first battle, a Pokémon the flood displaced, blocking the shelter steps
IsleMarais_EventScript_DisplacedWingull::
	lockall
	msgbox IsleMarais_Text_WingullLunges, MSGBOX_DEFAULT
	closemessage
	setwildbattle SPECIES_WINGULL, 3
	dowildbattle
	special HealPlayerParty
	msgbox IsleMarais_Text_WingullFlewOff, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 3
	releaseall
	end

IsleMarais_Text_BoardedDoor:
	.string "The door's boarded up.\n"
	.string "MOM says it isn't safe yet.$"

IsleMarais_Text_WingullLunges:
	.string "A WINGULL blown in by the storm\n"
	.string "is tangled in the debris!\p"
	.string "It lunges at you!$"

IsleMarais_Text_WingullFlewOff:
	.string "The WINGULL shook itself free and\n"
	.string "flew off over the water.\p"
	.string "Your partner looks pleased\n"
	.string "with itself.$"

@ --- mapgen: generated NPC scripts (begin) ---

IsleMarais_EventScript_Recruiter1::
	msgbox IsleMarais_Text_Recruiter1, MSGBOX_NPC
	end

IsleMarais_Text_Recruiter1:
	.string "Rita's crew is recruiting\nhands for the cleanup.$"

IsleMarais_EventScript_Recruiter2::
	msgbox IsleMarais_Text_Recruiter2, MSGBOX_NPC
	end

IsleMarais_Text_Recruiter2:
	.string "Rita says every pair of\nhands counts after the storm.$"

IsleMarais_EventScript_LeveeWatcher::
	msgbox IsleMarais_Text_LeveeWatcher, MSGBOX_NPC
	end

IsleMarais_Text_LeveeWatcher:
	.string "...Same water.\nDifferent storm.$"

IsleMarais_EventScript_Fisherman::
	msgbox IsleMarais_Text_Fisherman, MSGBOX_NPC
	end

IsleMarais_Text_Fisherman:
	.string "The shrimp boat's stuck, but the\nMAGIKARP are still biting.$"

@ --- mapgen: generated NPC scripts (end) ---
