CrescentCity_PokecenterQuarter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_PokecenterQuarter_OnTransition
	.byte 0

@ Walking in sets the respawn point
CrescentCity_PokecenterQuarter_OnTransition:
	setrespawn HEAL_LOCATION_CRESCENT_CITY
	end
