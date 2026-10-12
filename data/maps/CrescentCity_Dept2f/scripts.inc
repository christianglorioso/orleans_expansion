CrescentCity_Dept2f_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Dept2f_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Dept2f_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept2f_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_Dept2f_EventScript_Clerk1::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Dept2f_Pokemart1
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept2f_Pokemart1:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

CrescentCity_Dept2f_EventScript_Shopper2::
	msgbox CrescentCity_Dept2f_Text_Shopper2, MSGBOX_NPC
	end

CrescentCity_Dept2f_Text_Shopper2:
	.string "trade evolutions just need a\nLinking Cord here$"

@ --- mapgen: generated NPC scripts (end) ---
