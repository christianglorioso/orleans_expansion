CampCocodrie_NurseCabin_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CampCocodrie_NurseCabin_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_CAMP_COCODRIE_NURSE_CABIN_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

@ --- mapgen: generated NPC scripts (end) ---
