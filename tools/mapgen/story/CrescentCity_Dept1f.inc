CrescentCity_Dept1f_MapScripts::
	.byte 0

@ The ROTOM quest (after gym 3): the TV display. Before the badge it only pranks; after, the ROTOM inside battles (wild, level 22).
CrescentCity_Dept1f_EventScript_RotomTv2::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_Dept1f_EventScript_RotomQuiet
	playmoncry SPECIES_ROTOM, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_Dept1f_Text_RotomGo, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_Dept1f_EventScript_RotomDone
	release
	end

CrescentCity_Dept1f_EventScript_RotomDone:
	setflag FLAG_CRESCENT_ROTOM_TV
	removeobject LOCALID_CRESCENT_CITY_DEPT1F_ROTOM_TV2
	release
	end

CrescentCity_Dept1f_EventScript_RotomQuiet:
	msgbox CrescentCity_Dept1f_Text_RotomQuiet, MSGBOX_DEFAULT
	release
	end

@ First floor: balls and medicine; the stock grows with the third badge
CrescentCity_Dept1f_EventScript_Clerk1::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Dept1f_EventScript_Clerk11
	pokemart CrescentCity_Dept1f_Pokemart_Clerk10
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

CrescentCity_Dept1f_EventScript_Clerk11:
	pokemart CrescentCity_Dept1f_Pokemart_Clerk11
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
CrescentCity_Dept1f_Pokemart_Clerk10:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_REPEL
	pokemartlistend

	.align 2
CrescentCity_Dept1f_Pokemart_Clerk11:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_NET_BALL
	.2byte ITEM_DUSK_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_SUPER_REPEL
	pokemartlistend

CrescentCity_Dept1f_Text_RotomQuiet:
	.string "The TV display changes channels\n"
	.string "by itself. Static. A face. Static.$"

CrescentCity_Dept1f_Text_RotomGo:
	.string "The TV flickers through every\n"
	.string "channel at once, watching you.\p"
	.string "The screen goes white. A ROTOM\n"
	.string "leaps out of the set, sparking!$"
