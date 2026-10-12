CrescentCity_PokecenterQuarter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_PokecenterQuarter_OnTransition
	.byte 0

@ Walking in sets the respawn point
CrescentCity_PokecenterQuarter_OnTransition:
	setrespawn HEAL_LOCATION_CRESCENT_CITY
	end

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_PokecenterQuarter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_CRESCENT_CITY_POKECENTER_QUARTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

CrescentCity_PokecenterQuarter_EventScript_Tourist1::
	msgbox CrescentCity_PokecenterQuarter_Text_Tourist1, MSGBOX_NPC
	end

CrescentCity_PokecenterQuarter_Text_Tourist1:
	.string "I came for the music. Stayed for\nthe storm cleanup.$"

CrescentCity_PokecenterQuarter_EventScript_ParadeFan2::
	msgbox CrescentCity_PokecenterQuarter_Text_ParadeFan2, MSGBOX_NPC
	end

CrescentCity_PokecenterQuarter_Text_ParadeFan2:
	.string "The second line passes right by\nhere. You can hear it start.$"

@ --- mapgen: generated NPC scripts (end) ---
