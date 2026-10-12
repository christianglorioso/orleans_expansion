PointeRouge_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PointeRouge_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
PointeRouge_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_POINTE_ROUGE
	end
