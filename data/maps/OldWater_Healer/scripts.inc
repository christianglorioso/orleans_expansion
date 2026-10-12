OldWater_Healer_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldWater_Healer_OnTransition
	.byte 0

@ Walking in sets the respawn point (the slice defined the heal location but nothing ever selected it)
OldWater_Healer_OnTransition:
	setrespawn HEAL_LOCATION_OLD_WATER
	end

@ --- mapgen: generated NPC scripts (begin) ---

OldWater_Healer_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_OLD_WATER_HEALER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

OldWater_Healer_EventScript_Apprentice1::
	msgbox OldWater_Healer_Text_Apprentice1, MSGBOX_NPC
	end

OldWater_Healer_Text_Apprentice1:
	.string "That one's sweetgrass. That one's\nfor fevers. That one... I forget.$"

@ --- mapgen: generated NPC scripts (end) ---
