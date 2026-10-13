LandsEnd_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LandsEnd_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
LandsEnd_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_LANDS_END
	end
