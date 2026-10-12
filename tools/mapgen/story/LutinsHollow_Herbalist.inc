LutinsHollow_Herbalist_MapScripts::
	.byte 0

@ The herbalist: bitter medicine that works
LutinsHollow_Herbalist_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart LutinsHollow_Herbalist_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
LutinsHollow_Herbalist_Pokemart:
	.2byte ITEM_HEAL_POWDER
	.2byte ITEM_ENERGY_POWDER
	.2byte ITEM_ENERGY_ROOT
	.2byte ITEM_REVIVAL_HERB
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_MAX_REPEL
	pokemartlistend
