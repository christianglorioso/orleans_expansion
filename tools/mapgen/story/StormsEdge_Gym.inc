StormsEdge_Gym_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, StormsEdge_Gym_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, StormsEdge_Gym_OnLoad
	.byte 0

@ Gym 2, the Storm's Edge substation: Eclair (Electric Terrain).
@ The trial: six junction panels (bg events from story_overlay.py) in two rows of three,
@   1 2 3
@   4 5 6
@ Using a panel flips it AND the panels next to it (up, down, left, right: a 2x3 "lights out"). Light all six and the control
@ desk wakes up (FLAG_STORMS_EDGE_DESK_POWERED); only then will Eclair battle. The start pattern is 1, 2, 3 and 5 lit,
@ which takes junctions 1, 2 and 6 to solve. Whatever the player presses stays solvable (any lights-out state reached from
@ a solvable one is solvable), so the puzzle can never dead-end. Lit flags: FLAG_STORMS_EDGE_JUNCTION_1..6.
@ Panel art: stand-in tiles (metatile ids are filled in by story.py when it splices this file).

StormsEdge_Gym_OnTransition:
	@ Eclair stops waiting outside once the player is in her substation
	setflag FLAG_HIDE_STORMS_EDGE_ECLAIR
	call_if_unset FLAG_STORMS_EDGE_PUZZLE_STARTED, StormsEdge_Gym_EventScript_SetStartPattern
	end

StormsEdge_Gym_EventScript_SetStartPattern:
	setflag FLAG_STORMS_EDGE_PUZZLE_STARTED
	setflag FLAG_STORMS_EDGE_JUNCTION_1
	setflag FLAG_STORMS_EDGE_JUNCTION_2
	setflag FLAG_STORMS_EDGE_JUNCTION_3
	clearflag FLAG_STORMS_EDGE_JUNCTION_4
	setflag FLAG_STORMS_EDGE_JUNCTION_5
	clearflag FLAG_STORMS_EDGE_JUNCTION_6
	return

StormsEdge_Gym_OnLoad:
	call StormsEdge_Gym_EventScript_DrawJunction1
	call StormsEdge_Gym_EventScript_DrawJunction2
	call StormsEdge_Gym_EventScript_DrawJunction3
	call StormsEdge_Gym_EventScript_DrawJunction4
	call StormsEdge_Gym_EventScript_DrawJunction5
	call StormsEdge_Gym_EventScript_DrawJunction6
	end

@ Draw one panel from its flag (lit = screen glow, dark = grey casing; both solid)
StormsEdge_Gym_EventScript_DrawJunction1:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_1, StormsEdge_Gym_EventScript_LitJunction1
	setmetatile 6, 7, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction1:
	setmetatile 6, 7, @@mt:ph:40E@@, TRUE
	return

StormsEdge_Gym_EventScript_DrawJunction2:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_2, StormsEdge_Gym_EventScript_LitJunction2
	setmetatile 10, 7, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction2:
	setmetatile 10, 7, @@mt:ph:40E@@, TRUE
	return

StormsEdge_Gym_EventScript_DrawJunction3:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_3, StormsEdge_Gym_EventScript_LitJunction3
	setmetatile 14, 7, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction3:
	setmetatile 14, 7, @@mt:ph:40E@@, TRUE
	return

StormsEdge_Gym_EventScript_DrawJunction4:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_4, StormsEdge_Gym_EventScript_LitJunction4
	setmetatile 6, 10, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction4:
	setmetatile 6, 10, @@mt:ph:40E@@, TRUE
	return

StormsEdge_Gym_EventScript_DrawJunction5:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_5, StormsEdge_Gym_EventScript_LitJunction5
	setmetatile 10, 10, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction5:
	setmetatile 10, 10, @@mt:ph:40E@@, TRUE
	return

StormsEdge_Gym_EventScript_DrawJunction6:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_6, StormsEdge_Gym_EventScript_LitJunction6
	setmetatile 14, 10, @@mt:mt:453@@, TRUE
	return

StormsEdge_Gym_EventScript_LitJunction6:
	setmetatile 14, 10, @@mt:ph:40E@@, TRUE
	return

@ Flip one flag
StormsEdge_Gym_EventScript_Flip1:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_1, StormsEdge_Gym_EventScript_Unlight1
	setflag FLAG_STORMS_EDGE_JUNCTION_1
	return

StormsEdge_Gym_EventScript_Unlight1:
	clearflag FLAG_STORMS_EDGE_JUNCTION_1
	return

StormsEdge_Gym_EventScript_Flip2:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_2, StormsEdge_Gym_EventScript_Unlight2
	setflag FLAG_STORMS_EDGE_JUNCTION_2
	return

StormsEdge_Gym_EventScript_Unlight2:
	clearflag FLAG_STORMS_EDGE_JUNCTION_2
	return

StormsEdge_Gym_EventScript_Flip3:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_3, StormsEdge_Gym_EventScript_Unlight3
	setflag FLAG_STORMS_EDGE_JUNCTION_3
	return

StormsEdge_Gym_EventScript_Unlight3:
	clearflag FLAG_STORMS_EDGE_JUNCTION_3
	return

StormsEdge_Gym_EventScript_Flip4:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_4, StormsEdge_Gym_EventScript_Unlight4
	setflag FLAG_STORMS_EDGE_JUNCTION_4
	return

StormsEdge_Gym_EventScript_Unlight4:
	clearflag FLAG_STORMS_EDGE_JUNCTION_4
	return

StormsEdge_Gym_EventScript_Flip5:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_5, StormsEdge_Gym_EventScript_Unlight5
	setflag FLAG_STORMS_EDGE_JUNCTION_5
	return

StormsEdge_Gym_EventScript_Unlight5:
	clearflag FLAG_STORMS_EDGE_JUNCTION_5
	return

StormsEdge_Gym_EventScript_Flip6:
	goto_if_set FLAG_STORMS_EDGE_JUNCTION_6, StormsEdge_Gym_EventScript_Unlight6
	setflag FLAG_STORMS_EDGE_JUNCTION_6
	return

StormsEdge_Gym_EventScript_Unlight6:
	clearflag FLAG_STORMS_EDGE_JUNCTION_6
	return

@ The six panels. Junction n flips itself and its neighbours (1: 1 2 4, 2: 2 1 3 5, 3: 3 2 6, 4: 4 1 5, 5: 5 2 4 6, 6: 6 3 5).
StormsEdge_Gym_EventScript_Junction1::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip1
	call StormsEdge_Gym_EventScript_Flip2
	call StormsEdge_Gym_EventScript_Flip4
	msgbox StormsEdge_Gym_Text_Junction1, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_Junction2::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip2
	call StormsEdge_Gym_EventScript_Flip1
	call StormsEdge_Gym_EventScript_Flip3
	call StormsEdge_Gym_EventScript_Flip5
	msgbox StormsEdge_Gym_Text_Junction2, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_Junction3::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip3
	call StormsEdge_Gym_EventScript_Flip2
	call StormsEdge_Gym_EventScript_Flip6
	msgbox StormsEdge_Gym_Text_Junction3, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_Junction4::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip4
	call StormsEdge_Gym_EventScript_Flip1
	call StormsEdge_Gym_EventScript_Flip5
	msgbox StormsEdge_Gym_Text_Junction4, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_Junction5::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip5
	call StormsEdge_Gym_EventScript_Flip2
	call StormsEdge_Gym_EventScript_Flip4
	call StormsEdge_Gym_EventScript_Flip6
	msgbox StormsEdge_Gym_Text_Junction5, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_Junction6::
	lockall
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_JunctionLocked
	playse SE_CLICK
	call StormsEdge_Gym_EventScript_Flip6
	call StormsEdge_Gym_EventScript_Flip3
	call StormsEdge_Gym_EventScript_Flip5
	msgbox StormsEdge_Gym_Text_Junction6, MSGBOX_DEFAULT
	goto StormsEdge_Gym_EventScript_Redraw

StormsEdge_Gym_EventScript_JunctionLocked:
	msgbox StormsEdge_Gym_Text_JunctionLocked, MSGBOX_DEFAULT
	releaseall
	end

StormsEdge_Gym_EventScript_Redraw:
	call StormsEdge_Gym_EventScript_DrawJunction1
	call StormsEdge_Gym_EventScript_DrawJunction2
	call StormsEdge_Gym_EventScript_DrawJunction3
	call StormsEdge_Gym_EventScript_DrawJunction4
	call StormsEdge_Gym_EventScript_DrawJunction5
	call StormsEdge_Gym_EventScript_DrawJunction6
	special DrawWholeMapView
	@ all six lit?
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_1, StormsEdge_Gym_EventScript_NotYet
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_2, StormsEdge_Gym_EventScript_NotYet
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_3, StormsEdge_Gym_EventScript_NotYet
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_4, StormsEdge_Gym_EventScript_NotYet
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_5, StormsEdge_Gym_EventScript_NotYet
	goto_if_unset FLAG_STORMS_EDGE_JUNCTION_6, StormsEdge_Gym_EventScript_NotYet
	setflag FLAG_STORMS_EDGE_DESK_POWERED
	playse SE_THUNDER
	msgbox StormsEdge_Gym_Text_DeskPowered, MSGBOX_DEFAULT
StormsEdge_Gym_EventScript_NotYet:
	releaseall
	end

@ ---------------------------------------------------------------- the people
StormsEdge_Gym_EventScript_GymGuide0::
	lock
	faceplayer
	goto_if_set FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_GuideAfter
	msgbox StormsEdge_Gym_Text_GuideHint, MSGBOX_DEFAULT
	release
	end

StormsEdge_Gym_EventScript_GuideAfter:
	msgbox StormsEdge_Gym_Text_GuideAfter, MSGBOX_DEFAULT
	release
	end

StormsEdge_Gym_EventScript_Lineworker1::
	trainerbattle_single TRAINER_ORLEANS_STORMS_EDGE_GYM_LINEWORKER, StormsEdge_Gym_Text_LineworkerIntro, StormsEdge_Gym_Text_LineworkerDefeat
	msgbox StormsEdge_Gym_Text_LineworkerAfter, MSGBOX_AUTOCLOSE
	end

StormsEdge_Gym_EventScript_Electrician2::
	trainerbattle_single TRAINER_ORLEANS_STORMS_EDGE_GYM_ELECTRICIAN, StormsEdge_Gym_Text_ElectricianIntro, StormsEdge_Gym_Text_ElectricianDefeat
	msgbox StormsEdge_Gym_Text_ElectricianAfter, MSGBOX_AUTOCLOSE
	end

@ Buoy VOLTORB roll along the conduits; talking to one (or bumping into it) starts a wild battle. Gone once beaten or caught.
StormsEdge_Gym_EventScript_Voltorb4::
	lock
	faceplayer
	playmoncry SPECIES_VOLTORB_ORLEANIAN, CRY_MODE_ENCOUNTER
	msgbox StormsEdge_Gym_Text_VoltorbRolls, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_VOLTORB_ORLEANIAN, 15
	dowildbattle
	setflag FLAG_HIDE_STORMS_EDGE_VOLTORB_1
	removeobject LOCALID_STORMS_EDGE_GYM_VOLTORB4
	release
	end

StormsEdge_Gym_EventScript_Voltorb5::
	lock
	faceplayer
	playmoncry SPECIES_VOLTORB_ORLEANIAN, CRY_MODE_ENCOUNTER
	msgbox StormsEdge_Gym_Text_VoltorbRolls, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_VOLTORB_ORLEANIAN, 16
	dowildbattle
	setflag FLAG_HIDE_STORMS_EDGE_VOLTORB_2
	removeobject LOCALID_STORMS_EDGE_GYM_VOLTORB5
	release
	end

@ ---------------------------------------------------------------- Eclair
StormsEdge_Gym_EventScript_Eclair3::
	lock
	faceplayer
	goto_if_set FLAG_BADGE02_GET, StormsEdge_Gym_EventScript_EclairAfter
	goto_if_unset FLAG_STORMS_EDGE_DESK_POWERED, StormsEdge_Gym_EventScript_EclairDeskDead
	trainerbattle_single TRAINER_ECLAIR, StormsEdge_Gym_Text_EclairIntro, StormsEdge_Gym_Text_EclairDefeat, StormsEdge_Gym_EventScript_EclairDefeated, NO_MUSIC
	goto StormsEdge_Gym_EventScript_EclairAfter
	end

StormsEdge_Gym_EventScript_EclairDeskDead:
	msgbox StormsEdge_Gym_Text_EclairDeskDead, MSGBOX_DEFAULT
	release
	end

@ Everything that matters (badge, grid, story, the yard stone) is set first, then the rewards: a full bag can never lose the
@ progress, and each reward has its own flag that is only set once it is really in the bag, so talking to Eclair again retries.
StormsEdge_Gym_EventScript_EclairDefeated::
	message StormsEdge_Gym_Text_ReceivedBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	setflag FLAG_BADGE02_GET
	@ the lights come back street by street: the drawbridge comes down when the player steps outside
	setflag FLAG_STORMS_EDGE_GRID_RESTORED
	setflag FLAG_HIDE_STORMS_EDGE_ECLAIR
	clearflag FLAG_UNUSED_0x28F
	setvar VAR_ORLEANS_STORY, 11
	msgbox StormsEdge_Gym_Text_BadgeInfo, MSGBOX_DEFAULT
	msgbox StormsEdge_Gym_Text_GridBack, MSGBOX_DEFAULT
	call StormsEdge_Gym_EventScript_GiveRewards
	release
	end

StormsEdge_Gym_EventScript_GiveRewards:
	goto_if_set FLAG_RECEIVED_PRY_BAR, StormsEdge_Gym_EventScript_RewardsDone
	goto_if_set FLAG_RECEIVED_TM_ECLAIR_SHOCK_WAVE, StormsEdge_Gym_EventScript_GivePryBar
	msgbox StormsEdge_Gym_Text_TakeThis, MSGBOX_DEFAULT
	giveitem ITEM_TM_SHOCK_WAVE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_TM_ECLAIR_SHOCK_WAVE
	msgbox StormsEdge_Gym_Text_ShockWaveInfo, MSGBOX_DEFAULT
StormsEdge_Gym_EventScript_GivePryBar:
	giveitem ITEM_PRY_BAR
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_PRY_BAR
	msgbox StormsEdge_Gym_Text_PryBarInfo, MSGBOX_DEFAULT
	msgbox StormsEdge_Gym_Text_SecondVerse, MSGBOX_DEFAULT
StormsEdge_Gym_EventScript_RewardsDone:
	return

StormsEdge_Gym_EventScript_EclairAfter:
	call StormsEdge_Gym_EventScript_GiveRewards
	msgbox StormsEdge_Gym_Text_EclairPost, MSGBOX_DEFAULT
	release
	end

@ ---------------------------------------------------------------- text
StormsEdge_Gym_Text_Junction1:
	.string "JUNCTION 1 clicks over.\n"
	.string "Junctions 1, 2 and 4 flipped.$"

StormsEdge_Gym_Text_Junction2:
	.string "JUNCTION 2 clicks over.\n"
	.string "Junctions 2, 1, 3 and 5 flipped.$"

StormsEdge_Gym_Text_Junction3:
	.string "JUNCTION 3 clicks over.\n"
	.string "Junctions 3, 2 and 6 flipped.$"

StormsEdge_Gym_Text_Junction4:
	.string "JUNCTION 4 clicks over.\n"
	.string "Junctions 4, 1 and 5 flipped.$"

StormsEdge_Gym_Text_Junction5:
	.string "JUNCTION 5 clicks over.\n"
	.string "Junctions 5, 2, 4 and 6 flipped.$"

StormsEdge_Gym_Text_Junction6:
	.string "JUNCTION 6 clicks over.\n"
	.string "Junctions 6, 3 and 5 flipped.$"

StormsEdge_Gym_Text_JunctionLocked:
	.string "The junction is locked in place.\n"
	.string "The whole substation is live.$"

StormsEdge_Gym_Text_DeskPowered:
	.string "All six junctions glow steady.\p"
	.string "Across the room, ÉCLAIR's control\n"
	.string "desk flickers back to life!$"

StormsEdge_Gym_Text_GuideHint:
	.string "Each junction flips itself and the\n"
	.string "ones beside it. Light up all six.\p"
	.string "The numbers start at the far wall:\n"
	.string "1, 2, 3 at the back, then 4, 5, 6.\p"
	.string "Mind the buoys!$"

StormsEdge_Gym_Text_GuideAfter:
	.string "The desk's live! Go on, ÉCLAIR's\n"
	.string "been waiting for a real battle.$"

StormsEdge_Gym_Text_LineworkerIntro:
	.string "Nobody crosses my line without a\n"
	.string "word. Here's the word: battle!$"

StormsEdge_Gym_Text_LineworkerDefeat:
	.string "Fuse blown.$"

StormsEdge_Gym_Text_LineworkerAfter:
	.string "The row farthest from the door is\n"
	.string "the first row: junctions 1, 2, 3.$"

StormsEdge_Gym_Text_ElectricianIntro:
	.string "I wired half of this substation.\n"
	.string "Let me test your circuits!$"

StormsEdge_Gym_Text_ElectricianDefeat:
	.string "Short circuit!$"

StormsEdge_Gym_Text_ElectricianAfter:
	.string "Every switch can be undone. Keep\n"
	.string "clicking till the whole board glows.$"

StormsEdge_Gym_Text_VoltorbRolls:
	.string "A buoy VOLTORB rolls out of the\n"
	.string "conduits, humming angrily!$"

StormsEdge_Gym_Text_EclairDeskDead:
	.string "ÉCLAIR: The desk's dead as a\n"
	.string "doornail until the junctions glow.\p"
	.string "Flip them till all six are lit.\n"
	.string "Then I'll show you my team!$"

StormsEdge_Gym_Text_EclairIntro:
	.string "ÉCLAIR: You lit it! Hear that\n"
	.string "hum? The whole port just woke up.\p"
	.string "My team runs on Electric Terrain.\n"
	.string "Keep your feet on the ground!$"

StormsEdge_Gym_Text_EclairDefeat:
	.string "ÉCLAIR: Whoa! That's a voltage\n"
	.string "drop I never saw coming.$"

StormsEdge_Gym_Text_ReceivedBadge:
	.string "{PLAYER} received the ÉCLAIR BADGE\n"
	.string "from ÉCLAIR.$"

StormsEdge_Gym_Text_BadgeInfo:
	.string "ÉCLAIR: That BADGE hums, doesn't it?\n"
	.string "Your POKéMON feel it too.\p"
	.string "They'll act a little quicker,\n"
	.string "like a spark finding its path.$"

StormsEdge_Gym_Text_TakeThis:
	.string "ÉCLAIR: Take these. My crew\n"
	.string "chipped in.$"

StormsEdge_Gym_Text_ShockWaveInfo:
	.string "ÉCLAIR: SHOCK WAVE never misses.\n"
	.string "Just like a downed line.$"

StormsEdge_Gym_Text_PryBarInfo:
	.string "ÉCLAIR: And a PRY BAR, from the\n"
	.string "lineworkers. Cracked rock and\p"
	.string "rusted hatches give way to it.\n"
	.string "Nothing out here stays shut.$"

StormsEdge_Gym_Text_SecondVerse:
	.string "ÉCLAIR: The second verse. TUPELO\n"
	.string "sent you, didn't he? Hear it.\p"
	.string "“The sky split open, and light ran\n"
	.string "down the wires of the world.\p"
	.string "The Long One lay down in the\n"
	.string "river bed, and the people heard\p"
	.string "it sing...”$"

StormsEdge_Gym_Text_GridBack:
	.string "Outside, the street lights stutter\n"
	.string "on, one by one.\p"
	.string "A cheer rolls down the river, and\n"
	.string "the drawbridge begins to lower.$"

StormsEdge_Gym_Text_EclairPost:
	.string "ÉCLAIR: The bridge is down. Route\n"
	.string "3 runs on to CRESCENT CITY.\p"
	.string "FIFOLET keeps the third verse in\n"
	.string "the old cemetery. Go by night!$"
