CrescentCity_Cafe_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Cafe_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Cafe_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Cafe_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_Cafe_EventScript_Regular1::
	msgbox CrescentCity_Cafe_Text_Regular1, MSGBOX_NPC
	end

CrescentCity_Cafe_Text_Regular1:
	.string "Pokéblocks make contest-style\ncondition... and happy Pokémon$"

@ --- mapgen: generated NPC scripts (end) ---
