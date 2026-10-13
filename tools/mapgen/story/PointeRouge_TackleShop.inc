PointeRouge_TackleShop_MapScripts::
	.byte 0

@ The tackle shop: Net and Dive Balls for the river, plus the basics. The registrar explains the tournament (the
@ tournament itself is run by the angler on Route 5, see Route5.inc).
PointeRouge_TackleShop_EventScript_Clerk0::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart PointeRouge_TackleShop_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
PointeRouge_TackleShop_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_NET_BALL
	.2byte ITEM_DIVE_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_REPEL
	pokemartlistend

PointeRouge_TackleShop_EventScript_TournamentRegistrar1::
	lock
	faceplayer
	goto_if_ge VAR_ORLEANS_STORY, 21, PointeRouge_TackleShop_EventScript_RegistrarDone
	goto_if_set FLAG_POINTE_TOURNEY_WON, PointeRouge_TackleShop_EventScript_RegistrarWon
	goto_if_ge VAR_ORLEANS_STORY, 19, PointeRouge_TackleShop_EventScript_RegistrarOpen
	msgbox PointeRouge_TackleShop_Text_RegistrarClosed, MSGBOX_DEFAULT
	release
	end

PointeRouge_TackleShop_EventScript_RegistrarOpen:
	msgbox PointeRouge_TackleShop_Text_RegistrarOpen, MSGBOX_DEFAULT
	release
	end

PointeRouge_TackleShop_EventScript_RegistrarWon:
	msgbox PointeRouge_TackleShop_Text_RegistrarWon, MSGBOX_DEFAULT
	release
	end

PointeRouge_TackleShop_EventScript_RegistrarDone:
	msgbox PointeRouge_TackleShop_Text_RegistrarDone, MSGBOX_DEFAULT
	release
	end

PointeRouge_TackleShop_Text_RegistrarClosed:
	.string "REGISTRAR: The tournament's off.\n"
	.string "Nobody fishes in a poisoned river.\p"
	.string "Somebody has to stop that leak at\n"
	.string "the refinery first.$"

PointeRouge_TackleShop_Text_RegistrarOpen:
	.string "REGISTRAR: Entries go through the\n"
	.string "angler at the Route 5 shack.\p"
	.string "Five bites out of the lake, and\n"
	.string "KINGFISHER will battle you.$"

PointeRouge_TackleShop_Text_RegistrarWon:
	.string "REGISTRAR: Winner! The boathouse is\n"
	.string "south, on the quay. Go on up.$"

PointeRouge_TackleShop_Text_RegistrarDone:
	.string "REGISTRAR: Another tournament next\n"
	.string "year. You're a hard act to follow.$"
