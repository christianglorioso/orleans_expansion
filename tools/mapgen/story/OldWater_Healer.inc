OldWater_Healer_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldWater_Healer_OnTransition
	.byte 0

@ Walking in sets the respawn point (the slice defined the heal location but nothing ever selected it)
OldWater_Healer_OnTransition:
	setrespawn HEAL_LOCATION_OLD_WATER
	end
