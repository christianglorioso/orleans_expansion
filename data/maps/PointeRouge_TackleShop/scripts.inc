PointeRouge_TackleShop_MapScripts::
	.byte 0

@ --- mapgen: generated NPC scripts (begin) ---

PointeRouge_TackleShop_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart PointeRouge_TackleShop_Pokemart0
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
PointeRouge_TackleShop_Pokemart0:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	pokemartlistend

PointeRouge_TackleShop_EventScript_TournamentRegistrar1::
	msgbox PointeRouge_TackleShop_Text_TournamentRegistrar1, MSGBOX_NPC
	end

PointeRouge_TackleShop_Text_TournamentRegistrar1:
	.string "sign up here for KINGFISHER's\ntrial$"

@ --- mapgen: generated NPC scripts (end) ---
