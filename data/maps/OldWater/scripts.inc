OldWater_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldWater_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, OldWater_OnFrameTable
	.byte 0

@ Isaac's raid (Chapter 7, 7.6, story 33 -> 34). VAR_OLD_WATER_RAID: 0 idle, 1 armed (Wren's call at Redfield, or any first visit while the story
@ is 33), 2 done. Stage 0 only re-routes to the fixed landing cell of the scene; stage 1 plays it. A blackout in the battle leaves the var at 1,
@ so the scene replays. The player and Wren fight two grunts as a partner battle (the engine's multi battle, Wren is PARTNER_WREN_<starter>).

@ the raid actors are hidden on every load; the scene brings them in (clearflag + addobject)
OldWater_OnTransition:
	setflag FLAG_VISITED_OLD_WATER
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_RAID_WREN
	setflag FLAG_HIDE_CER_KYOGRE
	setflag FLAG_HIDE_CER_GROUDON
	setflag FLAG_HIDE_CER_TUPELO
	setflag FLAG_HIDE_CER_JAYDEN
	setflag FLAG_HIDE_CER_WREN
	call_if_eq VAR_OLD_WATER_CEREMONY, 3, OldWater_EventScript_ShowCerTupelo
	end

OldWater_OnFrameTable:
	map_script_2 VAR_OLD_WATER_CEREMONY, 1, OldWater_EventScript_Ceremony
	map_script_2 VAR_OLD_WATER_RAID, 0, OldWater_EventScript_RaidEntry
	map_script_2 VAR_OLD_WATER_RAID, 1, OldWater_EventScript_RaidScene
	.2byte 0

OldWater_EventScript_RaidEntry::
	goto_if_ne VAR_ORLEANS_STORY, 33, OldWater_EventScript_RaidIdle
	lockall
	setvar VAR_OLD_WATER_RAID, 1
	fadescreen FADE_TO_BLACK
	warpsilent MAP_OLD_WATER, 22, 32
	waitstate
	releaseall
	end

OldWater_EventScript_RaidIdle:
	end

OldWater_EventScript_RaidScene::
	goto_if_ne VAR_ORLEANS_STORY, 33, OldWater_EventScript_RaidStale
	lockall
	clearflag FLAG_HIDE_RAID_ISAAC
	clearflag FLAG_HIDE_RAID_GRUNT1
	clearflag FLAG_HIDE_RAID_GRUNT2
	clearflag FLAG_HIDE_RAID_WREN
	addobject LOCALID_OLD_WATER_RAID_ISAAC
	addobject LOCALID_OLD_WATER_RAID_GRUNT1
	addobject LOCALID_OLD_WATER_RAID_GRUNT2
	addobject LOCALID_OLD_WATER_RAID_WREN
	msgbox OldWater_Text_Scene1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Grunt1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Wren1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Grunt2, MSGBOX_DEFAULT
	closemessage
	goto OldWater_EventScript_RaidBattle

@ stage 1 with the story elsewhere (a debug warp): nothing to play, and it must not loop
OldWater_EventScript_RaidStale:
	setvar VAR_OLD_WATER_RAID, 2
	end

OldWater_EventScript_RaidBattle:
	call_if_eq VAR_STARTER_MON, 0, OldWater_EventScript_BattleFuecoco
	call_if_eq VAR_STARTER_MON, 1, OldWater_EventScript_BattleTotodile
	call_if_eq VAR_STARTER_MON, 2, OldWater_EventScript_BattleChikorita
	specialvar VAR_RESULT, GetBattleOutcome
	@ anything but a win (a loss, or a draw where both sides faint) offers the retry: the multi special never whites out (audit fin S2)
	goto_if_ne VAR_RESULT, B_OUTCOME_WON, OldWater_EventScript_RaidLost
	goto OldWater_EventScript_RaidWon

OldWater_EventScript_BattleChikorita:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_CHIKORITA
	return

OldWater_EventScript_BattleFuecoco:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_FUECOCO
	return

OldWater_EventScript_BattleTotodile:
	multi_fixed_2_vs_2 TRAINER_ORLEANS_RAID_GRUNT_A, OldWater_Text_DefeatA, TRAINER_ORLEANS_RAID_GRUNT_B, OldWater_Text_DefeatB, PARTNER_WREN_TOTODILE
	return

@ a loss: heal, then TRY AGAIN or NOT YET (B = not yet): NOT YET sends the player back to Redfield with the raid reset (Wren waits outside the mill)
OldWater_EventScript_RaidLost:
	special HealPlayerParty
	msgbox OldWater_Text_Retry, MSGBOX_DEFAULT
	dynmultichoice 1, 1, FALSE, 2, 0, DYN_MULTICHOICE_CB_NONE, OldWater_Text_ChoiceAgain, OldWater_Text_ChoiceNotYet
	goto_if_eq VAR_RESULT, 0, OldWater_EventScript_RaidAgain
	goto OldWater_EventScript_RaidNotYet

OldWater_EventScript_RaidAgain:
	closemessage
	goto OldWater_EventScript_RaidBattle

OldWater_EventScript_RaidNotYet:
	msgbox OldWater_Text_NotYet, MSGBOX_DEFAULT
	closemessage
	setvar VAR_OLD_WATER_RAID, 0
	setvar VAR_REDFIELD_RAID_CALL, 1
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_RAID_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_ISAAC
	removeobject LOCALID_OLD_WATER_RAID_GRUNT1
	removeobject LOCALID_OLD_WATER_RAID_GRUNT2
	removeobject LOCALID_OLD_WATER_RAID_WREN
	warpsilent MAP_REDFIELD, 37, 14
	waitstate
	releaseall
	end

OldWater_EventScript_RaidWon:
	special HealPlayerParty
	msgbox OldWater_Text_Isaac2, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac3, MSGBOX_DEFAULT
	msgbox OldWater_Text_Isaac4, MSGBOX_DEFAULT
	closemessage
	setvar VAR_ORLEANS_STORY, 34
	setvar VAR_OLD_WATER_RAID, 2
	setflag FLAG_HIDE_RAID_ISAAC
	setflag FLAG_HIDE_RAID_GRUNT1
	setflag FLAG_HIDE_RAID_GRUNT2
	setflag FLAG_HIDE_REDFIELD_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_ISAAC
	removeobject LOCALID_OLD_WATER_RAID_GRUNT1
	removeobject LOCALID_OLD_WATER_RAID_GRUNT2
	fadescreen FADE_FROM_BLACK
	msgbox OldWater_Text_Wren2, MSGBOX_DEFAULT
	msgbox OldWater_Text_Wren3, MSGBOX_DEFAULT
	goto_if_unset FLAG_RECEIVED_CYPRESS_CHARM, OldWater_EventScript_RaidWrenCharm
OldWater_EventScript_RaidWrenDone:
	closemessage
	setflag FLAG_HIDE_RAID_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_OLD_WATER_RAID_WREN
	warpsilent MAP_REDFIELD, 37, 14
	waitstate
	releaseall
	end

@ the raid actors (hidden when the scene is not running); talking to them does nothing special
OldWater_EventScript_RaidIsaac::
OldWater_EventScript_RaidGrunt1::
OldWater_EventScript_RaidGrunt2::
OldWater_EventScript_RaidWren::
	end

@ ---------------------------------------------------------------- text
OldWater_Text_Scene1:
	.string "The OLD WATER is wrong. No bells, no\n"
	.string "singing. Smoke drifts between the\p"
	.string "stilt houses, and strangers in\n"
	.string "dark coats stand on the green.$"

OldWater_Text_Grunt1:
	.string "GRUNT: The song-house wall comes\n"
	.string "down. Every panel. That's the order.\p"
	.string "GRUNT: Move, sir. The boat's\n"
	.string "waiting.$"

OldWater_Text_Isaac1:
	.string "ISAAC: ...Wait. Just wait a\n"
	.string "minute.$"

OldWater_Text_Wren1:
	.string "WREN: ISAAC! You ate at the camp's\n"
	.string "table! You judged it a tie!\p"
	.string "ISAAC: ...I know. I remember.$"

OldWater_Text_Grunt2:
	.string "GRUNT: Enough talk. Take the girl\n"
	.string "and the kid!$"

OldWater_Text_DefeatA:
	.string "My whole team...$"

OldWater_Text_DefeatB:
	.string "That's not what we were promised.$"

OldWater_Text_Isaac2:
	.string "ISAAC: Stop. Stop it, both of you.\n"
	.string "Pack up. We're leaving.\p"
	.string "GRUNT: Sir, the order's from above!\n"
	.string "ISAAC: I said pack up.$"

OldWater_Text_Isaac3:
	.string "ISAAC: JAYDEN said the song was a\n"
	.string "lie that drowned a town. But the\p"
	.string "gumbo was real. The tie was real.\n"
	.string "I'll find my own answer.$"

OldWater_Text_Isaac4:
	.string "ISAAC: Tell TUPELO I'm sorry. And\n"
	.string "tell the boy I'm not coming back.$"

OldWater_Text_Wren2:
	.string "WREN: He turned. He actually\n"
	.string "turned.\p"
	.string "WREN: I'll stay and help TUPELO put\n"
	.string "the green back in order.$"

OldWater_EventScript_RaidWrenCharm:
	msgbox OldWater_Text_WrenCharm, MSGBOX_DEFAULT
	goto OldWater_EventScript_RaidWrenDone

OldWater_Text_WrenCharm:
	.string "WREN: You haven't got the CHARM yet.\n"
	.string "The CARVER by the landing has it.$"

OldWater_Text_Wren3:
	.string "WREN: The sixth and seventh verses\n"
	.string "hold. Go on to LAND'S END. I'll\p"
	.string "send word. Follow the river by\n"
	.string "Surf.$"

OldWater_Text_Retry:
	.string "WREN: Again? Together this time?\n"
	.string "Or come back later?$"

OldWater_Text_NotYet:
	.string "WREN: Not yet, then. Back to the\n"
	.string "mill. I'll be waiting.$"

OldWater_Text_ChoiceAgain:
	.string "TRY AGAIN$"

OldWater_Text_ChoiceNotYet:
	.string "NOT YET$"

@ ---------------------------------------------------------------- the dusk orb ceremony (Chapter 9, F.4: story 40 -> 41)
@ The second raid's end sets VAR_OLD_WATER_CEREMONY 1 and warps here; the player picks Kyogre or Groudon (VAR_ORLEANS_LEGENDARY_PICK 1 or 2), Jayden
@ takes the other. The legendary and its orb are given (own flags, retried by talking to Tupelo while the ceremony is open).
OldWater_EventScript_Ceremony::
	goto_if_lt VAR_ORLEANS_STORY, 40, OldWater_EventScript_CeremonySkip
	lockall
	setvar VAR_OLD_WATER_CEREMONY, 3
	clearflag FLAG_HIDE_CER_KYOGRE
	clearflag FLAG_HIDE_CER_GROUDON
	clearflag FLAG_HIDE_CER_TUPELO
	clearflag FLAG_HIDE_CER_JAYDEN
	clearflag FLAG_HIDE_CER_WREN
	addobject LOCALID_OLD_WATER_CER_KYOGRE
	addobject LOCALID_OLD_WATER_CER_GROUDON
	addobject LOCALID_OLD_WATER_CER_TUPELO
	addobject LOCALID_OLD_WATER_CER_JAYDEN
	addobject LOCALID_OLD_WATER_CER_WREN
	msgbox OldWater_Text_Cer1, MSGBOX_DEFAULT
	msgbox OldWater_Text_Cer2, MSGBOX_DEFAULT
	msgbox OldWater_Text_Cer3, MSGBOX_DEFAULT
	msgbox OldWater_Text_Cer4, MSGBOX_DEFAULT
	goto OldWater_EventScript_CerChoose

OldWater_EventScript_CeremonySkip:
	end

OldWater_EventScript_CerChoose:
	goto_if_set FLAG_RECEIVED_LEGENDARY, OldWater_EventScript_CerOrb
	msgbox OldWater_Text_CerAsk, MSGBOX_DEFAULT
	dynmultichoice 1, 1, TRUE, 2, 0, DYN_MULTICHOICE_CB_NONE, OldWater_Text_ChoiceKyogre, OldWater_Text_ChoiceGroudon
	goto_if_eq VAR_RESULT, 1, OldWater_EventScript_SureGroudon
	msgbox OldWater_Text_SureKyogre, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OldWater_EventScript_CerChoose
	setvar VAR_ORLEANS_LEGENDARY_PICK, 1
	givemon SPECIES_KYOGRE, 60
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, OldWater_EventScript_CerNoRoom
	setflag FLAG_RECEIVED_LEGENDARY
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, OldWater_EventScript_KyogreToPC
	msgbox OldWater_Text_GotKyogre, MSGBOX_DEFAULT
	msgbox OldWater_Text_JaydenK, MSGBOX_DEFAULT
	goto OldWater_EventScript_CerOrb

OldWater_EventScript_KyogreToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_KYOGRE
	call Common_EventScript_TransferredToPC
	msgbox OldWater_Text_GotKyogre, MSGBOX_DEFAULT
	msgbox OldWater_Text_JaydenK, MSGBOX_DEFAULT
	goto OldWater_EventScript_CerOrb

OldWater_EventScript_SureGroudon:
	msgbox OldWater_Text_SureGroudon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, OldWater_EventScript_CerChoose
	goto OldWater_EventScript_PickGroudon

OldWater_EventScript_PickGroudon:
	setvar VAR_ORLEANS_LEGENDARY_PICK, 2
	givemon SPECIES_GROUDON, 60
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, OldWater_EventScript_CerNoRoom
	setflag FLAG_RECEIVED_LEGENDARY
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, OldWater_EventScript_GroudonToPC
	msgbox OldWater_Text_GotGroudon, MSGBOX_DEFAULT
	msgbox OldWater_Text_JaydenG, MSGBOX_DEFAULT
	goto OldWater_EventScript_CerOrb

OldWater_EventScript_GroudonToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_GROUDON
	call Common_EventScript_TransferredToPC
	msgbox OldWater_Text_GotGroudon, MSGBOX_DEFAULT
	msgbox OldWater_Text_JaydenG, MSGBOX_DEFAULT
	goto OldWater_EventScript_CerOrb

OldWater_EventScript_CerBagFull:
	msgbox OldWater_Text_BagFull, MSGBOX_DEFAULT
	releaseall
	end

OldWater_EventScript_ShowCerTupelo:
	clearflag FLAG_HIDE_CER_TUPELO
	return

OldWater_EventScript_CerNoRoom:
	setvar VAR_ORLEANS_LEGENDARY_PICK, 0
	msgbox OldWater_Text_NoRoom, MSGBOX_DEFAULT
	releaseall
	end

OldWater_EventScript_CerOrb:
	goto_if_set FLAG_RECEIVED_LEGENDARY_ORB, OldWater_EventScript_CerEnd
	msgbox OldWater_Text_OrbGive, MSGBOX_DEFAULT
	goto_if_eq VAR_ORLEANS_LEGENDARY_PICK, 2, OldWater_EventScript_RedOrb
	giveitem ITEM_BLUE_ORB
	goto_if_eq VAR_RESULT, FALSE, OldWater_EventScript_CerBagFull
	setflag FLAG_RECEIVED_LEGENDARY_ORB
	goto OldWater_EventScript_CerEnd

OldWater_EventScript_RedOrb:
	giveitem ITEM_RED_ORB
	goto_if_eq VAR_RESULT, FALSE, OldWater_EventScript_CerBagFull
	setflag FLAG_RECEIVED_LEGENDARY_ORB
	goto OldWater_EventScript_CerEnd

@ the story moves on (40 -> 41) and the river carries the player to the water off Route 8's north islet; the actors leave
OldWater_EventScript_CerEnd:
	msgbox OldWater_Text_Cer5, MSGBOX_DEFAULT
	closemessage
	setvar VAR_OLD_WATER_CEREMONY, 2
	call_if_eq VAR_ORLEANS_STORY, 40, OldWater_EventScript_SetStory41
	fadescreen FADE_TO_BLACK
	setflag FLAG_HIDE_CER_KYOGRE
	setflag FLAG_HIDE_CER_GROUDON
	setflag FLAG_HIDE_CER_TUPELO
	setflag FLAG_HIDE_CER_JAYDEN
	setflag FLAG_HIDE_CER_WREN
	@ onto the open water just south of the islet: a warp onto a surfable tile gives the surfing avatar, so a party with no Surf user is never stranded (audit fin S4)
	warpsilent MAP_ORLEANS_ROUTE8, 11, 10
	waitstate
	releaseall
	end

OldWater_EventScript_SetStory41:
	setvar VAR_ORLEANS_STORY, 41
	return

@ the ceremony actors: Tupelo re-offers the choice while it is open (a full party); the rest are scenery
OldWater_EventScript_CerTupelo::
	lock
	faceplayer
	goto_if_eq VAR_OLD_WATER_CEREMONY, 3, OldWater_EventScript_CerChoose
	goto_if_ne VAR_OLD_WATER_CEREMONY, 1, OldWater_EventScript_CerIdle
	goto OldWater_EventScript_CerChoose

OldWater_EventScript_CerIdle:
	release
	end

OldWater_EventScript_CerKyogre::
OldWater_EventScript_CerGroudon::
OldWater_EventScript_CerJayden::
OldWater_EventScript_CerWren::
	end

OldWater_Text_Cer1:
	.string "Dusk over the OLD WATER. Lamps burn\n"
	.string "along every piling. TUPELO stands at\p"
	.string "the landing, singing.$"

OldWater_Text_Cer2:
	.string "KYOGRE rises from the water by the\n"
	.string "landing. GROUDON climbs the bank.\p"
	.string "Neither roars. They listen.$"

OldWater_Text_Cer3:
	.string "TUPELO: The Long One will not come\n"
	.string "alone. Two voices must walk with it,\p"
	.string "or it will wake the storms.\p"
	.string "TUPELO: One of these two will walk\n"
	.string "beside you. The other, the boy.$"

OldWater_Text_Cer4:
	.string "JAYDEN: I'll take whichever you\n"
	.string "leave. I owe somebody that much.\p"
	.string "WREN: And I'll hold the lamps.$"

OldWater_Text_CerAsk:
	.string "TUPELO: Which will you walk with?$"

OldWater_Text_ChoiceKyogre:
	.string "KYOGRE$"

OldWater_Text_ChoiceGroudon:
	.string "GROUDON$"

OldWater_Text_GotKyogre:
	.string "KYOGRE chooses to walk with you.\n"
	.string "The tide at your feet rises.$"

OldWater_Text_GotGroudon:
	.string "GROUDON chooses to walk with you.\n"
	.string "The earth underfoot is warm.$"

OldWater_Text_JaydenK:
	.string "JAYDEN: Then GROUDON's with me.$"

OldWater_Text_JaydenG:
	.string "JAYDEN: Then KYOGRE's with me.$"

OldWater_Text_OrbGive:
	.string "TUPELO: And its orb. It carries the\n"
	.string "sea, or the land. Hold it on the\p"
	.string "legendary and the old power wakes.$"

OldWater_Text_SureKyogre:
	.string "TUPELO: KYOGRE, the sea. You are\n"
	.string "sure?$"

OldWater_Text_SureGroudon:
	.string "TUPELO: GROUDON, the land. You are\n"
	.string "sure?$"

OldWater_Text_BagFull:
	.string "TUPELO: Your bag is full. Make room,\n"
	.string "then speak to me. I will wait.$"

OldWater_Text_NoRoom:
	.string "TUPELO: Your party and boxes are\n"
	.string "full. Make room, then speak to me.$"

OldWater_Text_Cer5:
	.string "TUPELO: The OLDEST SHRINE is across\n"
	.string "the channel north of ROUTE 8. The\p"
	.string "river carries you to its edge. Go\n"
	.string "at dawn.$"

@ --- mapgen: generated NPC scripts (begin) ---

OldWater_EventScript_Tupelo::
	msgbox OldWater_Text_Tupelo, MSGBOX_NPC
	end

OldWater_Text_Tupelo:
	.string "TUPELO: The water told us you\nwere coming. Sit. Listen.$"

OldWater_EventScript_Wren::
	msgbox OldWater_Text_Wren, MSGBOX_NPC
	end

OldWater_Text_Wren:
	.string "WREN: You made it! Welcome to\nthe Old Water.$"

OldWater_EventScript_Carver::
	msgbox OldWater_Text_Carver, MSGBOX_NPC
	end

OldWater_Text_Carver:
	.string "CARVER: Cypress keeps its shape\nlonger than any of us.$"

OldWater_EventScript_UxieShrine::
	msgbox OldWater_Text_UxieShrine, MSGBOX_SIGN
	end

OldWater_Text_UxieShrine:
	.string "A small stone, worn smooth.\nIt feels like being remembered.$"

@ --- mapgen: generated NPC scripts (end) ---
