LandsEnd_MarineSupply_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

LandsEnd_MarineSupply_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart LandsEnd_MarineSupply_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
LandsEnd_MarineSupply_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

LandsEnd_MarineSupply_EventScript_Diver1::
	msgbox LandsEnd_MarineSupply_Text_Diver1, MSGBOX_NPC
	end

LandsEnd_MarineSupply_Text_Diver1:
	.string "the Drowned Temple's door\nwon't open for just anyone$"

@ --- mapgen: generated NPC scripts (end) ---
