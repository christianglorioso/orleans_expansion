GrandOak_PokemonCenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, GrandOak_PokemonCenter_OnTransition
	.byte 0

@ Walking in sets the respawn point (the slice defined the heal location but nothing ever selected it)
GrandOak_PokemonCenter_OnTransition:
	setrespawn HEAL_LOCATION_GRAND_OAK
	end

@ --- mapgen: generated NPC scripts (begin) ---

GrandOak_PokemonCenter_EventScript_Nurse0::
	setvar VAR_0x800B, LOCALID_GRAND_OAK_POKEMON_CENTER_NURSE0
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

GrandOak_PokemonCenter_EventScript_Traveller1::
	msgbox GrandOak_PokemonCenter_Text_Traveller1, MSGBOX_NPC
	end

GrandOak_PokemonCenter_Text_Traveller1:
	.string "MAGNOLIA's gym uses Grassy Terrain.\nBug, Flying or Poison types help.$"

GrandOak_PokemonCenter_EventScript_Volunteer2::
	msgbox GrandOak_PokemonCenter_Text_Volunteer2, MSGBOX_NPC
	end

GrandOak_PokemonCenter_Text_Volunteer2:
	.string "The shelter in ISLE MARAIS still\nneeds supplies, if you're heading back.$"

@ --- mapgen: generated NPC scripts (end) ---
