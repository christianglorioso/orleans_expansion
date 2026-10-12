CampCocodrie_NurseCabin_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CampCocodrie_NurseCabin_OnTransition
	.byte 0

@ Walking in sets the respawn point (the camp's Pokemon Center)
CampCocodrie_NurseCabin_OnTransition:
	setrespawn HEAL_LOCATION_CAMP_COCODRIE
	end

@ --- mapgen: generated NPC scripts (begin) ---

CampCocodrie_NurseCabin_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_CAMP_COCODRIE_NURSE_CABIN_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

@ --- mapgen: generated NPC scripts (end) ---
