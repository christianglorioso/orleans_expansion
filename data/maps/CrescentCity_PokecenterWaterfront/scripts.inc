CrescentCity_PokecenterWaterfront_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_PokecenterWaterfront_OnTransition
	.byte 0

@ Walking in sets the respawn point
CrescentCity_PokecenterWaterfront_OnTransition:
	setrespawn HEAL_LOCATION_CRESCENT_CITY_WATERFRONT
	end

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_PokecenterWaterfront_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_CRESCENT_CITY_POKECENTER_WATERFRONT_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

CrescentCity_PokecenterWaterfront_EventScript_Deckhand1::
	msgbox CrescentCity_PokecenterWaterfront_Text_Deckhand1, MSGBOX_NPC
	end

CrescentCity_PokecenterWaterfront_Text_Deckhand1:
	.string "The riverboat to POINTE ROUGE leaves\nfrom the terminal next door.$"

@ --- mapgen: generated NPC scripts (end) ---
