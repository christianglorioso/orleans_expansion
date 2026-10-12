LutinsHollow_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LutinsHollow_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
LutinsHollow_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_LUTINS_HOLLOW
	end
