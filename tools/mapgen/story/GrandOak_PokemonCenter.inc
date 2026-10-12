GrandOak_PokemonCenter_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, GrandOak_PokemonCenter_OnTransition
	.byte 0

@ Walking in sets the respawn point (the slice defined the heal location but nothing ever selected it)
GrandOak_PokemonCenter_OnTransition:
	setrespawn HEAL_LOCATION_GRAND_OAK
	end
