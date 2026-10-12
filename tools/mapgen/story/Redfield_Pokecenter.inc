Redfield_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Redfield_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
Redfield_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_REDFIELD
	end
