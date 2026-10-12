LutinsHollow_Pokecenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LutinsHollow_Pokecenter_OnTransition
	.byte 0

@ Walking in sets the respawn point
LutinsHollow_Pokecenter_OnTransition:
	setrespawn HEAL_LOCATION_LUTINS_HOLLOW
	end

@ --- mapgen: generated NPC scripts (begin) ---

LutinsHollow_Pokecenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_LUTINS_HOLLOW_POKECENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

LutinsHollow_Pokecenter_EventScript_Traveller1::
	msgbox LutinsHollow_Pokecenter_Text_Traveller1, MSGBOX_NPC
	end

LutinsHollow_Pokecenter_Text_Traveller1:
	.string "The moss moves when nobody is\nlooking. I counted. Twice.$"

@ --- mapgen: generated NPC scripts (end) ---
