CrescentCity_IceCream_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_IceCream_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_IceCream_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_IceCream_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_IceCream_EventScript_Kid1::
	msgbox CrescentCity_IceCream_Text_Kid1, MSGBOX_NPC
	end

CrescentCity_IceCream_Text_Kid1:
	.string "the freezer growled at me!$"

@ --- mapgen: generated NPC scripts (end) ---
