CampCocodrie_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CampCocodrie_OnFrameTable
	.byte 0

@ Camp Cocodrie (Chapter 5). Story: 23 arrived (this frame script, once: VAR_CAMP_ARRIVAL; frame tables compare vars only), 24 Isaac
@ beaten (he stands on the nurse cabin's only approach cell, (7, 22), until then), 25 the gumbo cook-off judged a tie (in the
@ cookhouse), 26 the brothers beaten: badge 5, verse 5, the lake road (Route 10) opens (FLAG_BADGE05_GET).

CampCocodrie_OnFrameTable:
	map_script_2 VAR_CAMP_ARRIVAL, 0, CampCocodrie_EventScript_Arrival
	.2byte 0

@ the first landing (the camp is only reachable once the Route 6 jam is gone, story >= 22; a debug warp below that plays nothing and
@ keeps the scene armed). The respawn point moves to the camp's nurse cabin (set once, here; the cabin sets it again on entry).
CampCocodrie_EventScript_Arrival::
	goto_if_lt VAR_ORLEANS_STORY, 22, CampCocodrie_EventScript_ArrivalSkip
	lockall
	setvar VAR_CAMP_ARRIVAL, 1
	setrespawn HEAL_LOCATION_CAMP_COCODRIE
	call_if_eq VAR_ORLEANS_STORY, 22, CampCocodrie_EventScript_SetStory23
	msgbox CampCocodrie_Text_Arrival1, MSGBOX_DEFAULT
	msgbox CampCocodrie_Text_Arrival2, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_EventScript_ArrivalSkip:
	end

CampCocodrie_EventScript_SetStory23:
	setvar VAR_ORLEANS_STORY, 23
	return

@ ---------------------------------------------------------------- 5.3 Isaac (story 23 -> 24)
CampCocodrie_EventScript_Isaac::
	trainerbattle_single TRAINER_ORLEANS_ISAAC_CAMP, CampCocodrie_Text_IsaacIntro, CampCocodrie_Text_IsaacDefeat, CampCocodrie_EventScript_IsaacDefeated
	msgbox CampCocodrie_Text_IsaacAfter, MSGBOX_AUTOCLOSE
	end

CampCocodrie_EventScript_IsaacDefeated::
	msgbox CampCocodrie_Text_IsaacSeed1, MSGBOX_DEFAULT
	msgbox CampCocodrie_Text_IsaacSeed2, MSGBOX_DEFAULT
	call_if_eq VAR_ORLEANS_STORY, 23, CampCocodrie_EventScript_SetStory24
	setflag FLAG_HIDE_CAMP_ISAAC
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_CAMP_COCODRIE_ISAAC
	fadescreen FADE_FROM_BLACK
	release
	end

CampCocodrie_EventScript_SetStory24:
	setvar VAR_ORLEANS_STORY, 24
	return

@ ---------------------------------------------------------------- the brothers outdoors (their lines follow the story)
CampCocodrie_EventScript_Boudreaux::
	lock
	faceplayer
	goto CampCocodrie_EventScript_BrothersLine

CampCocodrie_EventScript_Thibodeaux::
	lock
	faceplayer
	goto CampCocodrie_EventScript_BrothersLine

CampCocodrie_EventScript_BrothersLine:
	goto_if_set FLAG_BADGE05_GET, CampCocodrie_EventScript_BrothersBeaten
	goto_if_ge VAR_ORLEANS_STORY, 25, CampCocodrie_EventScript_BrothersReady
	goto_if_ge VAR_ORLEANS_STORY, 24, CampCocodrie_EventScript_BrothersCook
	msgbox CampCocodrie_Text_BrothersFirst, MSGBOX_DEFAULT
	release
	end

CampCocodrie_EventScript_BrothersCook:
	msgbox CampCocodrie_Text_BrothersCook, MSGBOX_DEFAULT
	release
	end

CampCocodrie_EventScript_BrothersReady:
	msgbox CampCocodrie_Text_BrothersReady, MSGBOX_DEFAULT
	release
	end

CampCocodrie_EventScript_BrothersBeaten:
	msgbox CampCocodrie_Text_BrothersBeaten, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- the shrimp (a battle with the dock's fisherman)
CampCocodrie_EventScript_Fisherman::
	trainerbattle_single TRAINER_ORLEANS_CAMP_FISHERMAN, CampCocodrie_Text_FishermanIntro, CampCocodrie_Text_FishermanDefeat, CampCocodrie_EventScript_FishermanDefeated
	goto_if_set FLAG_CAMP_SHRIMP, CampCocodrie_EventScript_FishermanDone
	setflag FLAG_CAMP_SHRIMP
	msgbox CampCocodrie_Text_FishermanShrimp, MSGBOX_DEFAULT
	release
	end

CampCocodrie_EventScript_FishermanDefeated::
	setflag FLAG_CAMP_SHRIMP
	msgbox CampCocodrie_Text_FishermanShrimp, MSGBOX_DEFAULT
	release
	end

CampCocodrie_EventScript_FishermanDone:
	msgbox CampCocodrie_Text_FishermanAfter, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- the okra garden (north-east): pick it once the gardener has been asked
CampCocodrie_EventScript_OkraPatch1::
CampCocodrie_EventScript_OkraPatch2::
	lockall
	goto_if_set FLAG_CAMP_OKRA, CampCocodrie_EventScript_OkraHave
	goto_if_unset FLAG_CAMP_OKRA_ASKED, CampCocodrie_EventScript_OkraNotAsked
	setflag FLAG_CAMP_OKRA
	msgbox CampCocodrie_Text_OkraPicked, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_EventScript_OkraNotAsked:
	msgbox CampCocodrie_Text_OkraNotAsked, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_EventScript_OkraHave:
	msgbox CampCocodrie_Text_OkraHave, MSGBOX_DEFAULT
	releaseall
	end

@ ---------------------------------------------------------------- text
CampCocodrie_Text_Arrival1:
	.string "The water gives way to a boardwalk\n"
	.string "and a ring of stilt cabins.\p"
	.string "CAMP COCODRIE. Woodsmoke, the smell\n"
	.string "of onions, and somewhere an\p"
	.string "accordion that's out of tune on\n"
	.string "purpose.$"

CampCocodrie_Text_Arrival2:
	.string "A boy in a dark jacket watches you\n"
	.string "from the nurse cabin's steps.\p"
	.string "He's trying hard to look bored.\n"
	.string "He isn't managing it.$"

CampCocodrie_Text_IsaacIntro:
	.string "ISAAC: So you're the one who keeps\n"
	.string "showing up. RITA's wondering.\p"
	.string "I'm not wondering. I'm bored.\n"
	.string "...Fine. One battle. For form.$"

CampCocodrie_Text_IsaacDefeat:
	.string "ISAAC: Hm. That's about what I\n"
	.string "expected. Both ways.$"

CampCocodrie_Text_IsaacAfter:
	.string "ISAAC: Nurse's cabin is open.\n"
	.string "Nobody's stopping you.$"

CampCocodrie_Text_IsaacSeed1:
	.string "ISAAC: You know, JAYDEN talks about\n"
	.string "you. He pretends he doesn't.\p"
	.string "He wanted to be someone who fixed\n"
	.string "things. We all did. Then the\p"
	.string "flood came and fixing wasn't on\n"
	.string "offer. Only something louder.$"

CampCocodrie_Text_IsaacSeed2:
	.string "ISAAC: Go on. Beat the brothers.\n"
	.string "Eat the gumbo. It's good gumbo.\p"
	.string "I'll be around. I'm always around.\n"
	.string "That's the problem with me.$"

CampCocodrie_Text_BrothersFirst:
	.string "BOUDREAUX: We don't fight on an\n"
	.string "empty stomach. Or a worried one.\p"
	.string "THIBODEAUX: A boy in a dark jacket\n"
	.string "is lurking at the nurse cabin.\p"
	.string "BOUDREAUX: Deal with him. Then\n"
	.string "we'll talk gumbo.$"

CampCocodrie_Text_BrothersCook:
	.string "THIBODEAUX: Four things make a\n"
	.string "gumbo. Andouille, shrimp, okra and\p"
	.string "filé. Bring them to the cookhouse.\n"
	.string "BOUDREAUX: And judge. Honestly.$"

CampCocodrie_Text_BrothersReady:
	.string "BOUDREAUX: The pots are judged.\n"
	.string "THIBODEAUX: And we were both right.\p"
	.string "BOUDREAUX: Come in. Battle us,\n"
	.string "both of us, at once.$"

CampCocodrie_Text_BrothersBeaten:
	.string "BOUDREAUX: Two cooks, one pot, and\n"
	.string "a kid who tasted both.\p"
	.string "THIBODEAUX: That's all the verse\n"
	.string "ever asked. Eat together.$"

CampCocodrie_Text_FishermanIntro:
	.string "GASTON: Shrimp? I've got the best on\n"
	.string "the dock. I don't give it away.\p"
	.string "You want it, you fight for it!$"

CampCocodrie_Text_FishermanDefeat:
	.string "GASTON: Ha! Fought fair.$"

CampCocodrie_Text_FishermanShrimp:
	.string "GASTON: A bucket of fresh shrimp\n"
	.string "for the brothers' pot. Don't let\p"
	.string "it sit in the sun. The ISAAC kid\n"
	.string "would say it's a metaphor.$"

CampCocodrie_Text_FishermanAfter:
	.string "GASTON: The shrimp's yours. The\n"
	.string "airboat dock's open any time.$"

CampCocodrie_Text_OkraNotAsked:
	.string "Neat rows of okra. Somebody's\n"
	.string "garden. Better ask the gardener\p"
	.string "in the east cabin before picking.$"

CampCocodrie_Text_OkraPicked:
	.string "You pick a handful of tender okra\n"
	.string "pods. They squeak when you twist\p"
	.string "them. Good ones.$"

CampCocodrie_Text_OkraHave:
	.string "The okra rows are bare of the\n"
	.string "good pods. You took them.$"

@ --- mapgen: generated NPC scripts (begin) ---

CampCocodrie_EventScript_OldNeighbour::
	msgbox CampCocodrie_Text_OldNeighbour, MSGBOX_NPC
	end

CampCocodrie_Text_OldNeighbour:
	.string "My grandson plays the porch.\nCabin's open if you want filé.$"

CampCocodrie_EventScript_ZydecoAccordion::
	msgbox CampCocodrie_Text_ZydecoAccordion, MSGBOX_NPC
	end

CampCocodrie_Text_ZydecoAccordion:
	.string "Zydeco isn't played. It's survived.\nCome back at night.$"

CampCocodrie_EventScript_ZydecoRubboard::
	msgbox CampCocodrie_Text_ZydecoRubboard, MSGBOX_NPC
	end

CampCocodrie_Text_ZydecoRubboard:
	.string "The rub-board's older than the camp.\nDon't touch. It bites.$"

CampCocodrie_EventScript_Wrangler::
	msgbox CampCocodrie_Text_Wrangler, MSGBOX_NPC
	end

CampCocodrie_Text_Wrangler:
	.string "Gator pens are behind the cabins.\nThey're friendlier than they look.$"

CampCocodrie_EventScript_Kid::
	msgbox CampCocodrie_Text_Kid, MSGBOX_NPC
	end

CampCocodrie_Text_Kid:
	.string "The brothers make their gumbo by\narguing. It tastes the same!$"

CampCocodrie_EventScript_Smoker::
	msgbox CampCocodrie_Text_Smoker, MSGBOX_NPC
	end

CampCocodrie_Text_Smoker:
	.string "The smokehouse door's always open.\nThe sausage doesn't mind.$"

CampCocodrie_EventScript_SignLanding::
	msgbox CampCocodrie_Text_SignLanding, MSGBOX_SIGN
	end

CampCocodrie_Text_SignLanding:
	.string "CAMP COCODRIE\nGator pens: look, don't touch.$"

CampCocodrie_EventScript_SignCookhouse::
	msgbox CampCocodrie_Text_SignCookhouse, MSGBOX_SIGN
	end

CampCocodrie_Text_SignCookhouse:
	.string "COOKHOUSE\nBring your own fixings!$"

@ --- mapgen: generated NPC scripts (end) ---
