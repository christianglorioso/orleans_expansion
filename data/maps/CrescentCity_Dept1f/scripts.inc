CrescentCity_Dept1f_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_Dept1f_EventScript_Receptionist0::
	msgbox CrescentCity_Dept1f_Text_Receptionist0, MSGBOX_NPC
	end

CrescentCity_Dept1f_Text_Receptionist0:
	.string "floor guide$"

CrescentCity_Dept1f_EventScript_Clerk1::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CrescentCity_Dept1f_Pokemart1
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept1f_Pokemart1:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

@ --- mapgen: generated NPC scripts (end) ---
