CrescentCity_GameCorner_MapScripts::
	.byte 0

@ The Crescent City Game Corner, a riverboat-casino hall: the coin clerk (coins for money, and the Coin Case), the prize counter (items
@ for coins), a Blackjack table, four capsule machines (Gacha: first-stage starters) and the Derby window. Ported from the Game Corner
@ Expansion (heyopc, agsmgmaster64): see CREDITS.md. The coins are the vanilla coin system (src/coins.c); 50 coins cost 1000 yen.

@ ---------------------------------------------------------------- shared
CrescentCity_GameCorner_EventScript_NoCoinCase::
	msgbox CrescentCity_GameCorner_Text_NeedCoinCase, MSGBOX_DEFAULT
	releaseall
	end

CrescentCity_GameCorner_EventScript_Decline::
	closemessage
	releaseall
	end

@ ---------------------------------------------------------------- the coin clerk: coins for money, and the Coin Case
CrescentCity_GameCorner_EventScript_CoinClerk0::
	lock
	faceplayer
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_GameCorner_EventScript_CoinClerkSell
	msgbox CrescentCity_GameCorner_Text_ClerkWelcome, MSGBOX_DEFAULT
	giveitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_CoinClerkEnd
CrescentCity_GameCorner_EventScript_CoinClerkSell:
	message CrescentCity_GameCorner_Text_ClerkSell
	waitmessage
	showmoneybox 0, 0
	showcoinsbox 0, 5
	multichoicedefault 15, 0, MULTI_GAME_CORNER_COINS, 0, FALSE
	switch VAR_RESULT
	case 0, CrescentCity_GameCorner_EventScript_Buy50
	case 1, CrescentCity_GameCorner_EventScript_Buy500
	goto CrescentCity_GameCorner_EventScript_BuyCancel

CrescentCity_GameCorner_EventScript_Buy50::
	checkcoins VAR_TEMP_1
	goto_if_ge VAR_TEMP_1, (MAX_COINS + 1 - 50), CrescentCity_GameCorner_EventScript_BuyFull
	checkmoney 1000
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_BuyNoMoney
	addcoins 50
	removemoney 1000
	goto CrescentCity_GameCorner_EventScript_BuyDone

CrescentCity_GameCorner_EventScript_Buy500::
	checkcoins VAR_TEMP_1
	goto_if_ge VAR_TEMP_1, (MAX_COINS + 1 - 500), CrescentCity_GameCorner_EventScript_BuyFull
	checkmoney 10000
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_BuyNoMoney
	addcoins 500
	removemoney 10000
	goto CrescentCity_GameCorner_EventScript_BuyDone

CrescentCity_GameCorner_EventScript_BuyDone:
	updatemoneybox
	updatecoinsbox
	playse SE_SHOP
	msgbox CrescentCity_GameCorner_Text_ClerkThanks, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_BuyEnd

CrescentCity_GameCorner_EventScript_BuyNoMoney:
	msgbox CrescentCity_GameCorner_Text_ClerkNoMoney, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_BuyEnd

CrescentCity_GameCorner_EventScript_BuyFull:
	msgbox CrescentCity_GameCorner_Text_ClerkFull, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_BuyEnd

CrescentCity_GameCorner_EventScript_BuyCancel:
	msgbox CrescentCity_GameCorner_Text_ClerkCancel, MSGBOX_DEFAULT
CrescentCity_GameCorner_EventScript_BuyEnd:
	hidemoneybox
	hidecoinsbox
CrescentCity_GameCorner_EventScript_CoinClerkEnd:
	release
	end

@ ---------------------------------------------------------------- the prize counter: items for coins (cheaper than any machine; the machines pay in Pokemon only)
@ VAR_0x8008 = the item, VAR_0x8009 = its price in coins
CrescentCity_GameCorner_EventScript_PrizeClerk1::
	lock
	faceplayer
	msgbox CrescentCity_GameCorner_Text_PrizeIntro, MSGBOX_DEFAULT
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_PrizeNoCase
	showcoinsbox 0, 0
CrescentCity_GameCorner_EventScript_PrizeMenu:
	message CrescentCity_GameCorner_Text_PrizeWhich
	waitmessage
	dynmultichoice 12, 0, FALSE, 4, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_GameCorner_Text_CatItems, CrescentCity_GameCorner_Text_CatBalls, CrescentCity_GameCorner_Text_CatTms, CrescentCity_GameCorner_Text_Exit
	switch VAR_RESULT
	case 0, CrescentCity_GameCorner_EventScript_PrizeItems
	case 1, CrescentCity_GameCorner_EventScript_PrizeBalls
	case 2, CrescentCity_GameCorner_EventScript_PrizeTms
	goto CrescentCity_GameCorner_EventScript_PrizeExit

CrescentCity_GameCorner_EventScript_PrizeItems:
	dynmultichoice 12, 0, FALSE, 6, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_GameCorner_Text_HeartScale, CrescentCity_GameCorner_Text_FireStone, CrescentCity_GameCorner_Text_WaterStone, CrescentCity_GameCorner_Text_ThunderStone, CrescentCity_GameCorner_Text_LeafStone, CrescentCity_GameCorner_Text_MoonStone, CrescentCity_GameCorner_Text_Back
	switch VAR_RESULT
	case 0, CrescentCity_GameCorner_EventScript_PrizeHeartScale
	case 1, CrescentCity_GameCorner_EventScript_PrizeFireStone
	case 2, CrescentCity_GameCorner_EventScript_PrizeWaterStone
	case 3, CrescentCity_GameCorner_EventScript_PrizeThunderStone
	case 4, CrescentCity_GameCorner_EventScript_PrizeLeafStone
	case 5, CrescentCity_GameCorner_EventScript_PrizeMoonStone
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeBalls:
	dynmultichoice 12, 0, FALSE, 5, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_GameCorner_Text_LuxuryBall, CrescentCity_GameCorner_Text_DuskBall, CrescentCity_GameCorner_Text_QuickBall, CrescentCity_GameCorner_Text_RepeatBall, CrescentCity_GameCorner_Text_Back
	switch VAR_RESULT
	case 0, CrescentCity_GameCorner_EventScript_PrizeLuxuryBall
	case 1, CrescentCity_GameCorner_EventScript_PrizeDuskBall
	case 2, CrescentCity_GameCorner_EventScript_PrizeQuickBall
	case 3, CrescentCity_GameCorner_EventScript_PrizeRepeatBall
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeTms:
	dynmultichoice 12, 0, FALSE, 5, 0, DYN_MULTICHOICE_CB_NONE, CrescentCity_GameCorner_Text_TmFacade, CrescentCity_GameCorner_Text_TmAerialAce, CrescentCity_GameCorner_Text_TmSludgeBomb, CrescentCity_GameCorner_Text_TmBrickBreak, CrescentCity_GameCorner_Text_Back
	switch VAR_RESULT
	case 0, CrescentCity_GameCorner_EventScript_PrizeTmFacade
	case 1, CrescentCity_GameCorner_EventScript_PrizeTmAerialAce
	case 2, CrescentCity_GameCorner_EventScript_PrizeTmSludgeBomb
	case 3, CrescentCity_GameCorner_EventScript_PrizeTmBrickBreak
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeHeartScale:
	setvar VAR_0x8008, ITEM_HEART_SCALE
	setvar VAR_0x8009, 100
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeFireStone:
	setvar VAR_0x8008, ITEM_FIRE_STONE
	setvar VAR_0x8009, 300
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeWaterStone:
	setvar VAR_0x8008, ITEM_WATER_STONE
	setvar VAR_0x8009, 300
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeThunderStone:
	setvar VAR_0x8008, ITEM_THUNDER_STONE
	setvar VAR_0x8009, 300
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeLeafStone:
	setvar VAR_0x8008, ITEM_LEAF_STONE
	setvar VAR_0x8009, 300
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeMoonStone:
	setvar VAR_0x8008, ITEM_MOON_STONE
	setvar VAR_0x8009, 300
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeLuxuryBall:
	setvar VAR_0x8008, ITEM_LUXURY_BALL
	setvar VAR_0x8009, 60
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeDuskBall:
	setvar VAR_0x8008, ITEM_DUSK_BALL
	setvar VAR_0x8009, 60
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeQuickBall:
	setvar VAR_0x8008, ITEM_QUICK_BALL
	setvar VAR_0x8009, 60
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeRepeatBall:
	setvar VAR_0x8008, ITEM_REPEAT_BALL
	setvar VAR_0x8009, 60
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeTmFacade:
	setvar VAR_0x8008, ITEM_TM_FACADE
	checkitem VAR_0x8008
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_GameCorner_EventScript_PrizeHaveTm
	setvar VAR_0x8009, 400
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeTmAerialAce:
	setvar VAR_0x8008, ITEM_TM_AERIAL_ACE
	checkitem VAR_0x8008
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_GameCorner_EventScript_PrizeHaveTm
	setvar VAR_0x8009, 400
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeTmSludgeBomb:
	setvar VAR_0x8008, ITEM_TM_SLUDGE_BOMB
	checkitem VAR_0x8008
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_GameCorner_EventScript_PrizeHaveTm
	setvar VAR_0x8009, 400
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

CrescentCity_GameCorner_EventScript_PrizeTmBrickBreak:
	setvar VAR_0x8008, ITEM_TM_BRICK_BREAK
	checkitem VAR_0x8008
	goto_if_eq VAR_RESULT, TRUE, CrescentCity_GameCorner_EventScript_PrizeHaveTm
	setvar VAR_0x8009, 400
	goto CrescentCity_GameCorner_EventScript_PrizeBuy

@ confirm, check the coins and the bag, then pay and hand it over; every outcome returns to the menu
CrescentCity_GameCorner_EventScript_PrizeBuy:
	bufferitemname STR_VAR_1, VAR_0x8008
	buffernumberstring STR_VAR_2, VAR_0x8009
	msgbox CrescentCity_GameCorner_Text_PrizeConfirm, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_PrizeMenu
	checkcoins VAR_TEMP_1
	goto_if_lt VAR_TEMP_1, VAR_0x8009, CrescentCity_GameCorner_EventScript_PrizeNoCoins
	checkitemspace VAR_0x8008
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_PrizeNoRoom
	removecoins VAR_0x8009
	updatecoinsbox
	playse SE_SHOP
	giveitem VAR_0x8008
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeNoCoins:
	msgbox CrescentCity_GameCorner_Text_PrizeNoCoins, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

@ TMs are reusable (I_REUSABLE_TMS): a second copy would waste the coins
CrescentCity_GameCorner_EventScript_PrizeHaveTm:
	msgbox CrescentCity_GameCorner_Text_PrizeHaveTm, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeNoRoom:
	msgbox CrescentCity_GameCorner_Text_PrizeNoRoom, MSGBOX_DEFAULT
	goto CrescentCity_GameCorner_EventScript_PrizeMenu

CrescentCity_GameCorner_EventScript_PrizeExit:
	hidecoinsbox
	msgbox CrescentCity_GameCorner_Text_PrizeBye, MSGBOX_DEFAULT
	release
	end

CrescentCity_GameCorner_EventScript_PrizeNoCase:
	msgbox CrescentCity_GameCorner_Text_NeedCoinCase, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- Blackjack (src/game_corner_blackjack.c; the winnings go straight into the coin case)
CrescentCity_GameCorner_EventScript_Dealer2::
	lock
	faceplayer
	goto CrescentCity_GameCorner_EventScript_Blackjack
	end

CrescentCity_GameCorner_EventScript_Blackjack::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_BlackjackAsk, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	playbgm MUS_GAME_CORNER, FALSE
	special StartBlackJack
	waitstate
	savebgm MUS_DUMMY
	fadedefaultbgm
	releaseall
	end

@ ---------------------------------------------------------------- the capsule machines (src/game_corner_gacha.c; VAR_0x8004 = the machine, 1 Basic .. 4 Master)
CrescentCity_GameCorner_EventScript_GachaBasic::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_GachaBasic, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	setvar VAR_0x8004, 1
	call CrescentCity_GameCorner_EventScript_GachaCommon
	releaseall
	end

CrescentCity_GameCorner_EventScript_GachaGreat::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_GachaGreat, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	setvar VAR_0x8004, 2
	call CrescentCity_GameCorner_EventScript_GachaCommon
	releaseall
	end

CrescentCity_GameCorner_EventScript_GachaUltra::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_GachaUltra, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	setvar VAR_0x8004, 3
	call CrescentCity_GameCorner_EventScript_GachaCommon
	releaseall
	end

CrescentCity_GameCorner_EventScript_GachaMaster::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_GachaMaster, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	setvar VAR_0x8004, 4
	call CrescentCity_GameCorner_EventScript_GachaCommon
	releaseall
	end

CrescentCity_GameCorner_EventScript_GachaCommon::
	playbgm MUS_RG_CINNABAR, FALSE
	special StartGacha
	waitstate
	savebgm MUS_DUMMY
	fadedefaultbgm
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, CrescentCity_GameCorner_EventScript_GachaMonParty
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, CrescentCity_GameCorner_EventScript_GachaMonPC
CrescentCity_GameCorner_EventScript_GachaEnd:
	return

CrescentCity_GameCorner_EventScript_GachaMonParty:
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_GachaEnd
	call Common_EventScript_GetGiftMonPartySlot
	call Common_EventScript_NameReceivedPartyMon
	goto CrescentCity_GameCorner_EventScript_GachaEnd

CrescentCity_GameCorner_EventScript_GachaMonPC:
	msgbox gText_NicknameThisPokemon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_GachaToPC
	call Common_EventScript_NameReceivedBoxMon
CrescentCity_GameCorner_EventScript_GachaToPC:
	call Common_EventScript_TransferredToPC
	goto CrescentCity_GameCorner_EventScript_GachaEnd

@ ---------------------------------------------------------------- the Derby window (src/derby.c)
@ The race screen takes the bet out of the coin case itself; a win comes back in VAR_TEMP_4 (GAME_CORNER_VAR_WINNINGS) and is paid here.
@ The line-up (FLAG_DERBY_RESET, VAR_DERBY_RACER_1..6) is kept until a race has been run.
CrescentCity_GameCorner_EventScript_DerbyAttendant3::
	lock
	faceplayer
	goto CrescentCity_GameCorner_EventScript_Derby
	end

CrescentCity_GameCorner_EventScript_Derby::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, CrescentCity_GameCorner_EventScript_NoCoinCase
	msgbox CrescentCity_GameCorner_Text_DerbyAsk, MSGBOX_YESNO
	closemessage
	goto_if_eq VAR_RESULT, NO, CrescentCity_GameCorner_EventScript_Decline
	setvar VAR_TEMP_4, 0
	playbgm MUS_RG_PEWTER, FALSE
	special StartDerby
	waitstate
	savebgm MUS_DUMMY
	fadedefaultbgm
	goto_if_eq VAR_TEMP_4, 0, CrescentCity_GameCorner_EventScript_DerbyNoWin
	showcoinsbox 1, 1
	buffernumberstring STR_VAR_1, VAR_TEMP_4
	msgbox CrescentCity_GameCorner_Text_DerbyWon, MSGBOX_DEFAULT
	waitmessage
	addcoins VAR_TEMP_4
	setvar VAR_TEMP_4, 0
	updatecoinsbox
	playse SE_SHOP
	delay 40
	hidecoinsbox
CrescentCity_GameCorner_EventScript_DerbyNoWin:
	releaseall
	end

@ ---------------------------------------------------------------- text
CrescentCity_GameCorner_Text_OutOfOrder:
	.string "Out of order for now.$"

CrescentCity_GameCorner_Text_NeedCoinCase:
	.string "You need a COIN CASE to play.\n"
	.string "The clerk by the door has them.$"

CrescentCity_GameCorner_Text_ClerkWelcome:
	.string "Welcome aboard! This hall floats\n"
	.string "on coins, not water.\p"
	.string "You'll need a COIN CASE. Take\n"
	.string "this one, on the house.$"

CrescentCity_GameCorner_Text_ClerkSell:
	.string "Coins for sale. Fifty for 1,000,\n"
	.string "five hundred for 10,000.$"

CrescentCity_GameCorner_Text_ClerkThanks:
	.string "Thank you! Here are your coins.\n"
	.string "Play nice, and play long.$"

CrescentCity_GameCorner_Text_ClerkNoMoney:
	.string "You don't have enough money.$"

CrescentCity_GameCorner_Text_ClerkFull:
	.string "Your COIN CASE is full. Spend a\n"
	.string "few first!$"

CrescentCity_GameCorner_Text_ClerkCancel:
	.string "No coins today? The hall will\n"
	.string "still be here.$"

CrescentCity_GameCorner_Text_PrizeIntro:
	.string "The prize counter. Coins buy\n"
	.string "things the machines never pay.$"

CrescentCity_GameCorner_Text_PrizeWhich:
	.string "Which prizes would you like\n"
	.string "to see?$"

CrescentCity_GameCorner_Text_PrizeConfirm:
	.string "{STR_VAR_1} for {STR_VAR_2} coins.\n"
	.string "Is that right?$"

CrescentCity_GameCorner_Text_PrizeNoCoins:
	.string "You don't have enough coins.$"

CrescentCity_GameCorner_Text_PrizeHaveTm:
	.string "You already have that TM. It never\n"
	.string "wears out, so one is plenty.$"

CrescentCity_GameCorner_Text_PrizeNoRoom:
	.string "Your BAG has no room for that.$"

CrescentCity_GameCorner_Text_PrizeBye:
	.string "Come back when your case is\n"
	.string "heavy again.$"

CrescentCity_GameCorner_Text_CatItems:
	.string "STONES, SCALES$"

CrescentCity_GameCorner_Text_CatBalls:
	.string "RARE BALLS$"

CrescentCity_GameCorner_Text_CatTms:
	.string "TMs$"

CrescentCity_GameCorner_Text_Exit:
	.string "EXIT$"

CrescentCity_GameCorner_Text_Back:
	.string "BACK$"

CrescentCity_GameCorner_Text_HeartScale:
	.string "HEART SCALE  100$"

CrescentCity_GameCorner_Text_FireStone:
	.string "FIRE STONE  300$"

CrescentCity_GameCorner_Text_WaterStone:
	.string "WATER STONE  300$"

CrescentCity_GameCorner_Text_ThunderStone:
	.string "THUNDER STONE  300$"

CrescentCity_GameCorner_Text_LeafStone:
	.string "LEAF STONE  300$"

CrescentCity_GameCorner_Text_MoonStone:
	.string "MOON STONE  300$"

CrescentCity_GameCorner_Text_LuxuryBall:
	.string "LUXURY BALL  60$"

CrescentCity_GameCorner_Text_DuskBall:
	.string "DUSK BALL  60$"

CrescentCity_GameCorner_Text_QuickBall:
	.string "QUICK BALL  60$"

CrescentCity_GameCorner_Text_RepeatBall:
	.string "REPEAT BALL  60$"

CrescentCity_GameCorner_Text_TmFacade:
	.string "TM FACADE  400$"

CrescentCity_GameCorner_Text_TmAerialAce:
	.string "TM AERIAL ACE  400$"

CrescentCity_GameCorner_Text_TmSludgeBomb:
	.string "TM SLUDGE BOMB  400$"

CrescentCity_GameCorner_Text_TmBrickBreak:
	.string "TM BRICK BREAK  400$"

CrescentCity_GameCorner_Text_BlackjackAsk:
	.string "A BLACKJACK table. The house\n"
	.string "pays double, 3 to 2 on a natural.\p"
	.string "Care for a hand?$"

CrescentCity_GameCorner_Text_GachaBasic:
	.string "BASIC capsule machine. From 50\n"
	.string "coins a turn: Bulbasaur, Charmander,\p"
	.string "Mudkip, Snivy and Fennekin, now\n"
	.string "and then Quaxly. Give it a turn?$"

CrescentCity_GameCorner_Text_GachaGreat:
	.string "GREAT capsule machine. From 250\n"
	.string "coins a turn, with Chikorita and\p"
	.string "Totodile among the prizes.\n"
	.string "Give it a turn?$"

CrescentCity_GameCorner_Text_GachaUltra:
	.string "ULTRA capsule machine. From 1,000\n"
	.string "coins a turn, with Fuecoco among\p"
	.string "the rarest. Give it a turn?$"

CrescentCity_GameCorner_Text_GachaMaster:
	.string "MASTER capsule machine. From 4,500\n"
	.string "coins a turn. The rare starters\p"
	.string "come up most here. Give it a turn?$"

CrescentCity_GameCorner_Text_DerbyAsk:
	.string "The CRESCENT DERBY. Doduo and\n"
	.string "Dodrio run the levee, six to a race.\p"
	.string "Want to place a bet?$"

CrescentCity_GameCorner_Text_DerbyWon:
	.string "Your racer came in first!\n"
	.string "You won {STR_VAR_1} coins!$"

@ --- mapgen: generated NPC scripts (begin) ---

CrescentCity_GameCorner_EventScript_Gambler4::
	msgbox CrescentCity_GameCorner_Text_Gambler4, MSGBOX_NPC
	end

CrescentCity_GameCorner_Text_Gambler4:
	.string "The slots are gone, but the capsule\nmachines still pay out. Mostly in\pdisappointment.$"

CrescentCity_GameCorner_EventScript_Regular5::
	msgbox CrescentCity_GameCorner_Text_Regular5, MSGBOX_NPC
	end

CrescentCity_GameCorner_Text_Regular5:
	.string "The capsule machines hold the first\npartners from the old river towns.\pGrass, fire, water, one per swing.\nThe pricier the machine, the rarer.$"

@ --- mapgen: generated NPC scripts (end) ---
