CrescentCity_Conservation_MapScripts::
	.byte 0

@ The conservation project. The tally is the National Pokedex caught count (a species counts once, however many the player
@ holds): 10 species -> 5 Great Balls (once); 25 species -> the apartment key (FLAG_APARTMENT_UNLOCKED, the Landlady checks it).
@ Lafayette is also at the door outside while the story is 13: if the player came in first, the briefing is given here.
CrescentCity_Conservation_EventScript_Lafayette0::
	lock
	faceplayer
	goto_if_lt VAR_ORLEANS_STORY, 14, CrescentCity_Conservation_EventScript_FirstBriefing
	checkitem ITEM_DOME_FOSSIL
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_Conservation_EventScript_KabutoRevive
@ Every unclaimed tier is given in order (10 species, 15, 25), each only once, however many species he is told about at a time.
CrescentCity_Conservation_EventScript_Tally:
	setvar VAR_0x8004, 1
	specialvar VAR_RESULT, ScriptGetPokedexInfo
	copyvar VAR_0x800A, VAR_0x8006
	buffernumberstring STR_VAR_1, VAR_0x800A
	goto_if_lt VAR_0x800A, 10, CrescentCity_Conservation_EventScript_Progress
	goto_if_unset FLAG_LAFAYETTE_REWARD_10, CrescentCity_Conservation_EventScript_Tier10
	goto_if_lt VAR_0x800A, 15, CrescentCity_Conservation_EventScript_Progress10
	goto_if_unset FLAG_LAFAYETTE_REWARD_15, CrescentCity_Conservation_EventScript_Tier15
	goto_if_lt VAR_0x800A, 25, CrescentCity_Conservation_EventScript_Progress15
	goto_if_unset FLAG_APARTMENT_UNLOCKED, CrescentCity_Conservation_EventScript_Tier25
	msgbox CrescentCity_Conservation_Text_Done, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_Progress:
	msgbox CrescentCity_Conservation_Text_Progress, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_Progress10:
	msgbox CrescentCity_Conservation_Text_Progress10, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_Progress15:
	msgbox CrescentCity_Conservation_Text_Progress15, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_FirstBriefing:
	msgbox CrescentCity_Conservation_Text_Inside, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 14
	setflag FLAG_HIDE_CRESCENT_LAFAYETTE
	release
	end

CrescentCity_Conservation_EventScript_Tier10:
	msgbox CrescentCity_Conservation_Text_Reward10, MSGBOX_DEFAULT
	giveitem ITEM_GREAT_BALL, 5
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_LAFAYETTE_REWARD_10
	goto CrescentCity_Conservation_EventScript_Tally

CrescentCity_Conservation_EventScript_Tier15:
	msgbox CrescentCity_Conservation_Text_Reward15, MSGBOX_DEFAULT
	giveitem ITEM_BOTTLE_CAP
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_LAFAYETTE_REWARD_15
	goto CrescentCity_Conservation_EventScript_Tally

CrescentCity_Conservation_EventScript_Tier25:
	setflag FLAG_APARTMENT_UNLOCKED
	msgbox CrescentCity_Conservation_Text_Apartment, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_Keeper1::
	lock
	faceplayer
	goto_if_set FLAG_APARTMENT_UNLOCKED, CrescentCity_Conservation_EventScript_KeeperOpen
	msgbox CrescentCity_Conservation_Text_Keeper, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_KeeperOpen:
	msgbox CrescentCity_Conservation_Text_KeeperOpen, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_Text_Inside:
	.string "LAFAYETTE: {PLAYER}! Welcome to my\n"
	.string "conservation center.\p"
	.string "The storm moved every species in\n"
	.string "the region. I count them here.\p"
	.string "Bring me species. Ten, and I'll\n"
	.string "thank you properly. Twenty-five,\p"
	.string "and the city finds you an\n"
	.string "apartment.$"

CrescentCity_Conservation_Text_Progress:
	.string "LAFAYETTE: {STR_VAR_1} so far.\nEvery species counts, even shy ones.\p"
	.string "Ten species earns a thank-you.\nTwenty-five, an apartment.$"

CrescentCity_Conservation_Text_Reward10:
	.string "LAFAYETTE: {STR_VAR_1} species!\nThe habitats are filling in nicely.\p"
	.string "Please, take these. They will help\nyou find more.$"

CrescentCity_Conservation_Text_Progress10:
	.string "LAFAYETTE: {STR_VAR_1} logged.\nFifteen species earns a rare\p"
	.string "BOTTLE CAP. Twenty-five, a flat in\nthe French Quarter.$"

CrescentCity_Conservation_Text_Reward15:
	.string "LAFAYETTE: {STR_VAR_1} species!\nTake this BOTTLE CAP. A judge in\p"
	.string "the services house can use it to\nperfect a POKéMON.$"

CrescentCity_Conservation_Text_Progress15:
	.string "LAFAYETTE: {STR_VAR_1} logged.\nTwenty-five and the city finds you\p"
	.string "an apartment in the French Quarter.$"

CrescentCity_Conservation_Text_Apartment:
	.string "LAFAYETTE: {STR_VAR_1} species!\nThat is the number they asked for.\p"
	.string "The keeper has your key. The flat\nis yours, in the French Quarter.\p"
	.string "Decorate it however you like.$"

CrescentCity_Conservation_Text_Done:
	.string "LAFAYETTE: {STR_VAR_1}. Keep going!\nThe apartment is yours. Visit the\p"
	.string "habitats, they grow with every\nnew species.$"

CrescentCity_Conservation_Text_Keeper:
	.string "The apartment key comes at 25\n"
	.string "species. Ask LAFAYETTE how many\p"
	.string "you've brought. The alligator's\n"
	.string "named Gaston. Don't feed him.$"

CrescentCity_Conservation_Text_KeeperOpen:
	.string "That's the key to your apartment.\n"
	.string "The landlady in the French Quarter\p"
	.string "will let you in. Gaston approves.\n"
	.string "He didn't say so, but he does.$"

CrescentCity_Conservation_EventScript_Scientist2::
	msgbox CrescentCity_Conservation_Text_Scientist, MSGBOX_NPC
	end

CrescentCity_Conservation_Text_Scientist:
	.string "The fossil lab revives a fossil\n"
	.string "once you bring one. Mind the dust.$"

@ the fossil revival (Chapter 8, 8.1): the Route 19 Dome Fossil becomes a KABUTO (Lv. 40); the fossil is kept if there is no room
CrescentCity_Conservation_EventScript_KabutoRevive:
	msgbox CrescentCity_Conservation_Text_FossilFound, MSGBOX_DEFAULT
	givemon SPECIES_KABUTO, 40
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, CrescentCity_Conservation_EventScript_KabutoNoRoom
	removeitem ITEM_DOME_FOSSIL
	setflag FLAG_KABUTO_REVIVED
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, CrescentCity_Conservation_EventScript_KabutoToPC
	msgbox CrescentCity_Conservation_Text_FossilDone, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_KabutoToPC:
	call Common_EventScript_TransferredToPC
	msgbox CrescentCity_Conservation_Text_FossilDone, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_EventScript_KabutoNoRoom:
	msgbox CrescentCity_Conservation_Text_FossilNoRoom, MSGBOX_DEFAULT
	release
	end

CrescentCity_Conservation_Text_FossilFound:
	.string "LAFAYETTE: A DOME FOSSIL, from the\n"
	.string "Route 19 flats! May I revive it?\p"
	.string "LAFAYETTE: The old restoration rig\n"
	.string "still works. Here we go.$"

CrescentCity_Conservation_Text_FossilDone:
	.string "Out of the machine, blinking at the\n"
	.string "light: a KABUTO!$"

CrescentCity_Conservation_Text_FossilNoRoom:
	.string "LAFAYETTE: Your party and your boxes\n"
	.string "are full. Make room and come back.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---
