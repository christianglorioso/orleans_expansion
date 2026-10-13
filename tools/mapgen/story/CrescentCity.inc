CrescentCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CrescentCity_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CrescentCity_OnFrameTable
	.byte 0

@ The respawn point is set ONCE, in the arrival scene below (a blackout in the streets returns to the Quarter Center, not to
@ Storm's Edge). It must not be set on every load: that would override the Waterfront Center after healing there.
@
@ People who appear for one story value are hidden on every load and shown again only for that value: Lafayette outside the
@ conservation center while the story is 13, Wren at the Drowned Ward gate while it is 16.
CrescentCity_OnTransition:
	setflag FLAG_HIDE_CRESCENT_LAFAYETTE
	setflag FLAG_HIDE_CRESCENT_WREN
	setflag FLAG_HIDE_CRESCENT_GYM_USHER
	call_if_lt VAR_ORLEANS_STORY, 15, CrescentCity_EventScript_ShowUsher
	call_if_eq VAR_ORLEANS_STORY, 13, CrescentCity_EventScript_ShowLafayette
	call_if_eq VAR_ORLEANS_STORY, 16, CrescentCity_EventScript_ShowWren
	end

CrescentCity_EventScript_ShowLafayette:
	clearflag FLAG_HIDE_CRESCENT_LAFAYETTE
	return

CrescentCity_EventScript_ShowWren:
	clearflag FLAG_HIDE_CRESCENT_WREN
	return

CrescentCity_EventScript_ShowUsher:
	clearflag FLAG_HIDE_CRESCENT_GYM_USHER
	return

@ the gym's usher: nobody climbs to the gym before Lafayette's briefing and the market speech (story 15)
CrescentCity_EventScript_GymUsher::
	msgbox CrescentCity_Text_GymUsher, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- frame scripts
@ 11 or 12: the first arrival (Ch2 end). 14: the market speech, if the player left the city after Lafayette's briefing
@ before it played (it normally follows the briefing at once).
CrescentCity_OnFrameTable:
	map_script_2 VAR_ORLEANS_STORY, 11, CrescentCity_EventScript_ArrivalSkippedJayden
	map_script_2 VAR_ORLEANS_STORY, 12, CrescentCity_EventScript_Arrival
	map_script_2 VAR_ORLEANS_STORY, 14, CrescentCity_EventScript_MarketSpeechFrame
	.2byte 0

CrescentCity_EventScript_ArrivalSkippedJayden::
	lockall
	setflag FLAG_HIDE_ROUTE3_JAYDEN
	msgbox CrescentCity_Text_JaydenAhead, MSGBOX_DEFAULT
	goto CrescentCity_EventScript_ArrivalScene

@ Quiet scene: the city, then a PokeNav message from Lafayette, who waits at the conservation center's door on the waterfront.
CrescentCity_EventScript_Arrival::
	lockall
CrescentCity_EventScript_ArrivalScene:
	msgbox CrescentCity_Text_Arrival1, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_Arrival2, MSGBOX_DEFAULT
	playse SE_PIN
	msgbox CrescentCity_Text_PokenavMessage, MSGBOX_DEFAULT
	setrespawn HEAL_LOCATION_CRESCENT_CITY
	setvar VAR_ORLEANS_STORY, 13
	clearflag FLAG_HIDE_CRESCENT_LAFAYETTE
	addobject LOCALID_CRESCENT_CITY_LAFAYETTE
	releaseall
	end

@ ---------------------------------------------------------------- 3.1 Lafayette's briefing (story 13 -> 14), 3.2 the market speech (14 -> 15)
@ He waits at the conservation center's door. The conservation project: bring him species (the Pokedex count is the tally, see
@ CrescentCity_Conservation.inc for the rewards: 10 species, then the apartment key at 25).
CrescentCity_EventScript_Lafayette::
	lock
	faceplayer
	msgbox CrescentCity_Text_LafayetteBrief1, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_LafayetteBrief2, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_LafayetteBrief3, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 14
	setflag FLAG_HIDE_CRESCENT_LAFAYETTE
	closemessage
	removeobject LOCALID_CRESCENT_CITY_LAFAYETTE
	goto CrescentCity_EventScript_MarketSpeech

CrescentCity_EventScript_MarketSpeechFrame::
	lockall
CrescentCity_EventScript_MarketSpeech:
	msgbox CrescentCity_Text_Speech1, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_Speech2, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_Speech3, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_Speech4, MSGBOX_DEFAULT
	setvar VAR_ORLEANS_STORY, 15
	setflag FLAG_HIDE_CRESCENT_GYM_USHER
	removeobject LOCALID_CRESCENT_CITY_GYM_USHER
	releaseall
	end

@ ---------------------------------------------------------------- 3.8 the parade leader (a Quaxly after gym 3)
CrescentCity_EventScript_ParadeLeader::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_QUAXLY, CrescentCity_EventScript_ParadeAfterQuaxly
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_EventScript_ParadeBefore
	msgbox CrescentCity_Text_ParadeGift, MSGBOX_DEFAULT
	givemon SPECIES_QUAXLY, 18
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, CrescentCity_EventScript_ParadeNoRoom
	setflag FLAG_RECEIVED_QUAXLY
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, CrescentCity_EventScript_ParadeToPC
	msgbox CrescentCity_Text_ParadeReceived, MSGBOX_DEFAULT
	release
	end

@ after gym 6 (plan 3.8): the leader hands over Quaquavalite, Quaquaval's Mega Stone (once; bag-full safe)
CrescentCity_EventScript_ParadeAfterQuaxly:
	goto_if_unset FLAG_BADGE06_GET, CrescentCity_EventScript_ParadeAfter
	goto_if_set FLAG_RECEIVED_QUAQUAVALITE, CrescentCity_EventScript_ParadeAfter
	msgbox CrescentCity_Text_ParadeStone, MSGBOX_DEFAULT
	giveitem ITEM_QUAQUAVALITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_QUAQUAVALITE
	release
	end

CrescentCity_EventScript_ParadeToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_QUAXLY
	call Common_EventScript_TransferredToPC
	msgbox CrescentCity_Text_ParadeReceived, MSGBOX_DEFAULT
	release
	end

CrescentCity_EventScript_ParadeNoRoom:
	call Common_EventScript_NoMoreRoomForPokemon
	release
	end

CrescentCity_EventScript_ParadeBefore:
	msgbox CrescentCity_Text_ParadeBefore, MSGBOX_DEFAULT
	release
	end

CrescentCity_EventScript_ParadeAfter:
	msgbox CrescentCity_Text_ParadeAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- 3.7 the Rotom quest, last stop: the waterfront generator
@ (the other four are in the department store's TV, the cafe's blender, the laundry's washer and the ice-cream freezer)
CrescentCity_EventScript_RotomGenerator::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_EventScript_RotomGeneratorQuiet
	playmoncry SPECIES_ROTOM_HEAT, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_Text_RotomGenerator, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM_HEAT, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CrescentCity_EventScript_RotomDone
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_EventScript_RotomDone
	release
	end

CrescentCity_EventScript_RotomDone:
	setflag FLAG_CRESCENT_ROTOM_GENERATOR
	removeobject LOCALID_CRESCENT_CITY_ROTOM_GENERATOR
	release
	end

CrescentCity_EventScript_RotomGeneratorQuiet:
	msgbox CrescentCity_Text_GeneratorHum, MSGBOX_DEFAULT
	release
	end

@ City Park's lawn mower: the sixth stop (Mow form)
CrescentCity_EventScript_RotomMow::
	lock
	faceplayer
	goto_if_unset FLAG_BADGE03_GET, CrescentCity_EventScript_RotomMowQuiet
	playmoncry SPECIES_ROTOM_MOW, CRY_MODE_ENCOUNTER
	msgbox CrescentCity_Text_RotomMow, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_ROTOM_MOW, 22
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, CrescentCity_EventScript_RotomMowDone
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, CrescentCity_EventScript_RotomMowDone
	release
	end

CrescentCity_EventScript_RotomMowDone:
	setflag FLAG_CRESCENT_ROTOM_MOW
	removeobject LOCALID_CRESCENT_CITY_ROTOM_MOW
	release
	end

CrescentCity_EventScript_RotomMowQuiet:
	msgbox CrescentCity_Text_MowIdle, MSGBOX_DEFAULT
	release
	end

@ the Drowned Ward's door is blocked by this worker until the third badge (the object is hidden by FLAG_BADGE03_GET)
CrescentCity_EventScript_WardGuard::
	msgbox CrescentCity_Text_WardGuard, MSGBOX_NPC
	end

@ ---------------------------------------------------------------- 3.6 Wren at the Drowned Ward gate (story 16 -> into the base)
CrescentCity_EventScript_Wren::
	lock
	faceplayer
	msgbox CrescentCity_Text_WrenGate1, MSGBOX_DEFAULT
	msgbox CrescentCity_Text_WrenGate2, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_HIDE_CRESCENT_WREN
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CRESCENT_CITY_WREN
	warp MAP_CRESCENT_CITY_BLACKSNAKE_BASE, 0
	waitstate
	release
	end

@ ---------------------------------------------------------------- Route 14: the floodwater gate (until gym 6)
@ Every walkable cell of the bottom row inside the Route 14 connection (x 39-66) runs this (spec "triggers", story_overlay.py;
@ the trigger's var is the FLAG FLAG_BADGE06_GET with value 0, so it only fires while the flag is clear). The player is turned
@ back; the chapter that scripts Route 14 swaps this for the real water state (like Storm's Edge's bridge) and removes the
@ triggers. (NEVER "var": "0": TRIGGER_RUN_IMMEDIATELY freezes on a msgbox.)
CrescentCity_EventScript_FloodedRoad::
	lockall
	goto_if_set FLAG_BADGE06_GET, CrescentCity_EventScript_FloodedRoadOpen
	msgbox CrescentCity_Text_FloodedRoad, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, CrescentCity_Movement_StepBackNorth
	waitmovement 0
CrescentCity_EventScript_FloodedRoadOpen:
	releaseall
	end

CrescentCity_Movement_StepBackNorth:
	walk_up
	step_end

@ ---------------------------------------------------------------- text
CrescentCity_Text_Arrival1:
	.string "The causeway ends in lamplight and\n"
	.string "iron balconies.\p"
	.string "CRESCENT CITY. Every road in the\n"
	.string "region bends here, sooner or later.$"

CrescentCity_Text_Arrival2:
	.string "Brass music drifts from somewhere\n"
	.string "inside, thin over the flood-line\p"
	.string "stains on the old brick. The\n"
	.string "city is rebuilding too.$"

CrescentCity_Text_PokenavMessage:
	.string "Your POKéNAV buzzes. A message.\p"
	.string "LAFAYETTE: You made it to CRESCENT\n"
	.string "CITY! Come find me at the\p"
	.string "conservation center, down on the\n"
	.string "waterfront. I have a favor to ask.$"

CrescentCity_Text_JaydenAhead:
	.string "A boy in a grey hood slips through\n"
	.string "the crowd ahead, a bundle of\p"
	.string "snake-marked pamphlets under his\n"
	.string "arm. JAYDEN. He doesn't look back.$"

CrescentCity_Text_LafayetteBrief1:
	.string "LAFAYETTE: {PLAYER}! You made it.\n"
	.string "Did the road treat you well?\p"
	.string "This is my conservation center:\n"
	.string "a zoo, an aquarium, a library.$"

CrescentCity_Text_LafayetteBrief2:
	.string "The storm moved every species in\n"
	.string "the region. Some will never find\p"
	.string "their way home. So I give them\n"
	.string "a home here, and I count them.$"

CrescentCity_Text_LafayetteBrief3:
	.string "Bring me species, {PLAYER}. Ten, and\n"
	.string "I'll thank you properly.\p"
	.string "Twenty-five, and the city will\n"
	.string "find you an apartment. Come in!$"

CrescentCity_Text_Speech1:
	.string "As you step away, a voice carries\n"
	.string "across the market square.\p"
	.string "A man in a grey coat stands on a\n"
	.string "crate. A crowd has gathered.$"

CrescentCity_Text_Speech2:
	.string "“The bayou is wounded, friends.\n"
	.string "Wounded by someone's hand.\p"
	.string "They told you the serpent died of\n"
	.string "old age. It was hunted. Killed.”$"

CrescentCity_Text_Speech3:
	.string "“And the ones who did it sing\n"
	.string "their songs in the swamp, proud.\p"
	.string "The water takes our homes, and no\n"
	.string "one answers for it. Until now.”$"

CrescentCity_Text_Speech4:
	.string "Recruiters in snake-marked jackets\n"
	.string "hand pamphlets through the crowd.\p"
	.string "You know that quiet voice. The man\n"
	.string "at the levee: “Same water.”$"

CrescentCity_Text_ParadeBefore:
	.string "Second line, second line! Come\n"
	.string "back when you've beaten FIFOLET.\p"
	.string "The old cemetery has a way of\n"
	.string "making people brave. Or loud.$"

CrescentCity_Text_ParadeGift:
	.string "You beat FIFOLET! Then you've\n"
	.string "earned a place in the parade.\p"
	.string "A QUAXLY wandered in during the\n"
	.string "storm and joined the band. Take it!$"

CrescentCity_Text_ParadeReceived:
	.string "{PLAYER} received QUAXLY!\p"
	.string "It struts a little. It has the\n"
	.string "rhythm already.$"

CrescentCity_Text_ParadeAfter:
	.string "Second line, second line! Come\n"
	.string "back after the sixth BADGE. The\p"
	.string "band's got a fancier friend for\n"
	.string "you by then.$"

CrescentCity_Text_RotomGenerator:
	.string "The waterfront generator's casing\n"
	.string "rattles. Something hums inside!\p"
	.string "A ROTOM bursts out in a shower\n"
	.string "of sparks!$"

CrescentCity_Text_GeneratorHum:
	.string "The waterfront generator hums.\n"
	.string "It sounds almost like a giggle.$"

CrescentCity_Text_WrenGate1:
	.string "WREN: There you are! I heard you\n"
	.string "beat FIFOLET. The third verse!\p"
	.string "But that's not why I'm here. Look\n"
	.string "at that warehouse. The snake sign.$"

CrescentCity_Text_WrenGate2:
	.string "WREN: RITA's people took it over,\n"
	.string "and they took a carving from my\p"
	.string "village. A verse. If they broke\n"
	.string "it... Come on. Together!$"

CrescentCity_Text_FloodedRoad:
	.string "Brown floodwater covers the levee\n"
	.string "road south of the city.\p"
	.string "It's far too deep to cross. It\n"
	.string "will have to go down first.$"

CrescentCity_Text_RotomMow:
	.string "The park mower coughs awake\nall by itself.\p"
	.string "Its blades stop. A ROTOM hops out\nof the engine, cackling!$"

CrescentCity_Text_MowIdle:
	.string "The park mower rattles in the grass\nwith nobody at the handles.$"

CrescentCity_Text_WardGuard:
	.string "WORKER: The Drowned Ward is shut.\nFlooded stairs, bad wiring, worse\p"
	.string "company. The city says to stay out.\nCome back when someone says so.$"

CrescentCity_Text_GymUsher:
	.string "USHER: The gym is closed to anyone\nwho hasn't met LAFAYETTE yet.\p"
	.string "He's at the conservation center, on\nthe waterfront. Check in first.$"

CrescentCity_Text_ParadeStone:
	.string "PARADE LEADER: Six verses! The whole\nparade felt that one. The little\p"
	.string "QUAXLY you took is grown. Here, a\nstone for the big finish.\p"
	.string "QUAQUAVALITE. Dance it out.$"

