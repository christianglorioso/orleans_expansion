GrandOak_Mart_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

GrandOak_Mart_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart GrandOak_Mart_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
GrandOak_Mart_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_ESCAPE_ROPE
	pokemartlistend

GrandOak_Mart_EventScript_Shopper1::
	msgbox GrandOak_Mart_Text_Shopper1, MSGBOX_NPC
	end

GrandOak_Mart_Text_Shopper1:
	.string "RITA's people bought out every\nSUPER POTION in town.$"

@ --- mapgen: generated NPC scripts (end) ---
