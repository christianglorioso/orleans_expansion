IsleMarais_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IsleMarais_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, IsleMarais_OnLoad
	.byte 0

IsleMarais_OnTransition:
	call IsleMarais_EventScript_StoryWeather
	end

@ weather (weather_plan.py): rain until the player has left for Grand Oak (story 6), then sunny with clouds. Runs from OnTransition, before the weather starts.
IsleMarais_EventScript_StoryWeather:
	goto_if_lt VAR_ORLEANS_STORY, 6, IsleMarais_EventScript_StoryWeatherDone
	setweather WEATHER_SUNNY_CLOUDS
IsleMarais_EventScript_StoryWeatherDone:
	return

IsleMarais_OnLoad:
	call_if_unset FLAG_BADGE01_GET, IsleMarais_EventScript_BoardUpPlayersHouse
	end

@ The player's house is boarded up until Magnolia is beaten; then Mom moves back in.
IsleMarais_EventScript_BoardUpPlayersHouse::
	setmetatile 16, 18, @@mt:shady:25C@@, TRUE   @ the cabin wall where the door was (a name, not an id: ids move when the tileset is recomposed)
	return

IsleMarais_EventScript_BoardedDoor::
	goto_if_set FLAG_BADGE01_GET, IsleMarais_EventScript_BoardedDoorEnd
	msgbox IsleMarais_Text_BoardedDoor, MSGBOX_SIGN
IsleMarais_EventScript_BoardedDoorEnd:
	end

IsleMarais_Text_BoardedDoor:
	.string "The door's boarded up.\n"
	.string "MOM says it isn't safe yet.$"

