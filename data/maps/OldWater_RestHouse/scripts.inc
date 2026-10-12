OldWater_RestHouse_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

OldWater_RestHouse_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_OLD_WATER_REST_HOUSE_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

@ --- mapgen: generated NPC scripts (end) ---
