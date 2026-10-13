CrescentCity_Gym_MapScripts::
	.byte 0

@ Gym 3, the old cemetery: Fifolet (Ghost/Psychic). The trial is the tomb maze itself (the room is drawn from the mockup): four lights
@ stand in its corridors (spec coord events, live while the badge is not earned). Steady blue lights sit on the true way and say
@ so; flickering orange lights sit in dead-end branches and send the player back to the start. (Proposed: the maze is "night"
@ inside at any time of day; no clock gate. See the plan's open questions.)
CrescentCity_Gym_EventScript_BlueLight::
	lockall
	msgbox CrescentCity_Gym_Text_BlueLight, MSGBOX_DEFAULT
	releaseall
	end

CrescentCity_Gym_EventScript_OrangeLight::
	lockall
	msgbox CrescentCity_Gym_Text_OrangeLight, MSGBOX_DEFAULT
	closemessage
	playse SE_PIN
	fadescreen FADE_TO_BLACK
	warpsilent MAP_CRESCENT_CITY_GYM, 10, 16
	waitstate
	releaseall
	end

CrescentCity_Gym_EventScript_GymGuide3::
	lock
	faceplayer
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Gym_EventScript_GuideAfter
	msgbox CrescentCity_Gym_Text_GuideHint, MSGBOX_DEFAULT
	release
	end

CrescentCity_Gym_EventScript_GuideAfter:
	msgbox CrescentCity_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

CrescentCity_Gym_EventScript_Trainer1::
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_GYM_HEX_MANIAC, CrescentCity_Gym_Text_HexIntro, CrescentCity_Gym_Text_HexDefeat
	msgbox CrescentCity_Gym_Text_HexAfter, MSGBOX_AUTOCLOSE
	end

CrescentCity_Gym_EventScript_Trainer2::
	trainerbattle_single TRAINER_ORLEANS_CRESCENT_GYM_MEDIUM, CrescentCity_Gym_Text_MediumIntro, CrescentCity_Gym_Text_MediumDefeat
	msgbox CrescentCity_Gym_Text_MediumAfter, MSGBOX_AUTOCLOSE
	end

@ ---------------------------------------------------------------- Fifolet
@ Badge, story and the verse flag come first; the rewards (TM, Lantern, Mimikyu) each have a flag set only once the item is
@ really in the bag / party, so a full bag or party can't lose them: talking to Fifolet again retries.
CrescentCity_Gym_EventScript_Fifolet0::
	lock
	faceplayer
	goto_if_set FLAG_BADGE03_GET, CrescentCity_Gym_EventScript_FifoletAfter
	trainerbattle_single TRAINER_FIFOLET, CrescentCity_Gym_Text_FifoletIntro, CrescentCity_Gym_Text_FifoletDefeat, CrescentCity_Gym_EventScript_FifoletDefeated, NO_MUSIC
	goto CrescentCity_Gym_EventScript_FifoletAfter
	end

CrescentCity_Gym_EventScript_FifoletDefeated::
	message CrescentCity_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE03_GET
	call_if_lt VAR_ORLEANS_STORY, 16, CrescentCity_Gym_EventScript_SetStory16
	msgbox CrescentCity_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	call CrescentCity_Gym_EventScript_GiveRewards
	release
	end

CrescentCity_Gym_EventScript_SetStory16:
	setvar VAR_ORLEANS_STORY, 16
	return

CrescentCity_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_MIMIKYU, CrescentCity_Gym_EventScript_RewardsDone
	goto_if_set FLAG_RECEIVED_LANTERN, CrescentCity_Gym_EventScript_GiveMimikyu
	goto_if_set FLAG_RECEIVED_TM_SHADOW_BALL, CrescentCity_Gym_EventScript_GiveLantern
	msgbox CrescentCity_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_SHADOW_BALL
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_SHADOW_BALL
	msgbox CrescentCity_Gym_Text_ShadowBallInfo, MSGBOX_DEFAULT
CrescentCity_Gym_EventScript_GiveLantern:
	giveitem ITEM_LANTERN
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_LANTERN
	msgbox CrescentCity_Gym_Text_LanternInfo, MSGBOX_DEFAULT
CrescentCity_Gym_EventScript_GiveMimikyu:
	msgbox CrescentCity_Gym_Text_MimikyuGift, MSGBOX_DEFAULT
	givemon SPECIES_MIMIKYU, 20
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, CrescentCity_Gym_EventScript_MimikyuNoRoom
	setflag FLAG_RECEIVED_MIMIKYU
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, CrescentCity_Gym_EventScript_MimikyuToPC
	msgbox CrescentCity_Gym_Text_MimikyuReceived, MSGBOX_DEFAULT
	goto CrescentCity_Gym_EventScript_Verse

CrescentCity_Gym_EventScript_MimikyuToPC:
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_MIMIKYU
	call Common_EventScript_TransferredToPC
	msgbox CrescentCity_Gym_Text_MimikyuReceived, MSGBOX_DEFAULT
CrescentCity_Gym_EventScript_Verse:
	msgbox CrescentCity_Gym_Text_ThirdVerse, MSGBOX_DEFAULT
CrescentCity_Gym_EventScript_RewardsDone:
	return

CrescentCity_Gym_EventScript_MimikyuNoRoom:
	call Common_EventScript_NoMoreRoomForPokemon
	release
	end

CrescentCity_Gym_EventScript_FifoletAfter:
	call CrescentCity_Gym_EventScript_GiveRewards
	msgbox CrescentCity_Gym_Text_FifoletPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
CrescentCity_Gym_Text_BlueLight:
	.string "A steady blue light, floating.\n"
	.string "It does not flicker. It waits.$"

CrescentCity_Gym_Text_OrangeLight:
	.string "An orange light, guttering. It\n"
	.string "flickers... and the tombs blur!$"

CrescentCity_Gym_Text_GuideHint:
	.string "Follow the lights that don't\n"
	.string "blink. The steady blue ones are\p"
	.string "true guides. The flickering orange\n"
	.string "ones are feux follets: they lead\p"
	.string "you in circles, back to the door.$"

CrescentCity_Gym_Text_GuideAfter:
	.string "You followed the right lights.\n"
	.string "Most people follow the pretty ones.$"

CrescentCity_Gym_Text_HexIntro:
	.string "Something walked behind you down\n"
	.string "the last turn. Didn't you feel it?\p"
	.string "No? Then you're about to.$"

CrescentCity_Gym_Text_HexDefeat:
	.string "Oh! You didn't flinch once.$"

CrescentCity_Gym_Text_HexAfter:
	.string "The blue lights don't lie. The\n"
	.string "orange ones always do.$"

CrescentCity_Gym_Text_MediumIntro:
	.string "The dead tell me you're lost.\n"
	.string "They tell everyone that.\p"
	.string "Shall we ask them again?$"

CrescentCity_Gym_Text_MediumDefeat:
	.string "The dead say good game.$"

CrescentCity_Gym_Text_MediumAfter:
	.string "FIFOLET sits at the crypt's end.\n"
	.string "She's kinder than the maze.$"

CrescentCity_Gym_Text_FifoletIntro:
	.string "FIFOLET: Few come all the way\n"
	.string "through. Fewer don't scream.\p"
	.string "The lights on the water are old.\n"
	.string "They guide the lost, or mislead\p"
	.string "them. I keep them. And my\n"
	.string "friends. Come, meet my friends.$"

CrescentCity_Gym_Text_FifoletDefeat:
	.string "FIFOLET: Mm. The lamp stays lit.\n"
	.string "You walked it straight.$"

CrescentCity_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the FIFOLET BADGE\n"
	.string "from FIFOLET.$"

CrescentCity_Gym_Text_BadgeInfo:
	.string "FIFOLET: With that BADGE the\n"
	.string "friends of the dark will trust you.\p"
	.string "Even the ones you can't see. They\n"
	.string "will follow where you lead.$"

CrescentCity_Gym_Text_TakeThis:
	.string "FIFOLET: Take these. A gift from\n"
	.string "the old cemetery.$"

CrescentCity_Gym_Text_ShadowBallInfo:
	.string "FIFOLET: SHADOW BALL. A shadow,\n"
	.string "shaped like a throw.$"

CrescentCity_Gym_Text_LanternInfo:
	.string "FIFOLET: And my lantern. Its flame\n"
	.string "is steady and true, like a blue\p"
	.string "light. It will show you the way\n"
	.string "in the darkest tunnels.$"

CrescentCity_Gym_Text_MimikyuGift:
	.string "FIFOLET: One more thing. A little\n"
	.string "one has been following me about.\p"
	.string "It wears a rag and wishes to be\n"
	.string "loved. Will you take it?$"

CrescentCity_Gym_Text_MimikyuReceived:
	.string "{PLAYER} received MIMIKYU!\p"
	.string "It looks up at you from under\n"
	.string "its rag. It seems pleased.$"

CrescentCity_Gym_Text_ThirdVerse:
	.string "FIFOLET: And the third verse. You\n"
	.string "carry TUPELO's trust. Listen.\p"
	.string "“The lamps went out on the water,\n"
	.string "and the lost wandered in the dark.\p"
	.string "The Long One breathed, and one\n"
	.string "light rose, and the lost went home.”$"

CrescentCity_Gym_Text_FifoletPost:
	.string "FIFOLET: A girl from the swamp\n"
	.string "asked after you. She waits at the\p"
	.string "Drowned Ward gate, east of the\n"
	.string "market. And the riverboat now\p"
	.string "sails for POINTE ROUGE. The pass\n"
	.string "is yours. The BADGE is the pass.$"
