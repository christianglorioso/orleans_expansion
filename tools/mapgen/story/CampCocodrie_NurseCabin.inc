CampCocodrie_NurseCabin_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CampCocodrie_NurseCabin_OnTransition
	.byte 0

@ Walking in sets the respawn point (the camp's Pokemon Center)
CampCocodrie_NurseCabin_OnTransition:
	setrespawn HEAL_LOCATION_CAMP_COCODRIE
	end
