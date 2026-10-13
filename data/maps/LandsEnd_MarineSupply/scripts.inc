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
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_MAX_REPEL
	pokemartlistend

LandsEnd_MarineSupply_EventScript_Diver1::
	msgbox LandsEnd_MarineSupply_Text_Diver1, MSGBOX_NPC
	end

LandsEnd_MarineSupply_Text_Diver1:
	.string "The DROWNED TEMPLE's door won't open\nfor just anyone. It wants a song.$"

@ --- mapgen: generated NPC scripts (end) ---
