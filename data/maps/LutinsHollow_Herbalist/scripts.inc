LutinsHollow_Herbalist_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

LutinsHollow_Herbalist_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart LutinsHollow_Herbalist_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
LutinsHollow_Herbalist_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

LutinsHollow_Herbalist_EventScript_Apprentice1::
	msgbox LutinsHollow_Herbalist_Text_Apprentice1, MSGBOX_NPC
	end

LutinsHollow_Herbalist_Text_Apprentice1:
	.string "the Floette seed is for later\n(post-game quest)$"

@ --- mapgen: generated NPC scripts (end) ---
