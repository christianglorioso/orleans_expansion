Route14_RougarouHollow_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route14_RougarouHollow_OnTransition
	.byte 0

@ The rougarou's levee hollow (Route 14, through the trail in the east canopy beside the pond; open from the flood, any hour).
@ A new, unconnected map (lairs.py builds it from the approved mock). The way out is the gap in the south wall: the exit triggers (10..11, 14) put the
@ player back on the trail's mouth. The rougarou is a one-off night Lycanroc Midnight (Lv. 42): its object shows at night only, until it is caught (a KO
@ leaves it for another try); then a LYCANROCITE (given once, bag-full safe: the flag is set after the stone is in the bag). By day the hollow is empty.
Route14_RougarouHollow_OnTransition:
	setflag FLAG_TEMP_1
	setflag FLAG_HIDE_ROUTE14_ROUGAROU
	goto_if_set FLAG_RECEIVED_LYCANROCITE, Route14_RougarouHollow_EventScript_NoRougarou
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, TRUE, Route14_RougarouHollow_EventScript_ShowRougarou
Route14_RougarouHollow_EventScript_NoRougarou:
	end

Route14_RougarouHollow_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, Route14_RougarouHollow_Movement_FaceLeft
	waitmovement 0
	warp MAP_ORLEANS_ROUTE14, 25, 30
	waitstate
	end

Route14_RougarouHollow_Movement_FaceLeft:
	face_left
	step_end

Route14_RougarouHollow_EventScript_ShowRougarou:
	clearflag FLAG_HIDE_ROUTE14_ROUGAROU
	end

Route14_RougarouHollow_EventScript_Rougarou::
	lock
	faceplayer
	goto_if_set FLAG_ROUTE14_ROUGAROU_DONE, Route14_RougarouHollow_EventScript_RougarouStone
	playmoncry SPECIES_LYCANROC_MIDNIGHT, CRY_MODE_ENCOUNTER
	msgbox Route14_RougarouHollow_Text_Rougarou1, MSGBOX_DEFAULT
	waitmoncry
	setwildbattle SPECIES_LYCANROC_MIDNIGHT, 42
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route14_RougarouHollow_EventScript_RougarouBeaten
	msgbox Route14_RougarouHollow_Text_RougarouRan, MSGBOX_DEFAULT
	release
	end

Route14_RougarouHollow_EventScript_RougarouBeaten:
	setflag FLAG_ROUTE14_ROUGAROU_DONE
	goto Route14_RougarouHollow_EventScript_RougarouStone

Route14_RougarouHollow_EventScript_RougarouStone:
	goto_if_set FLAG_RECEIVED_LYCANROCITE, Route14_RougarouHollow_EventScript_RougarouGone
	msgbox Route14_RougarouHollow_Text_RougarouStone, MSGBOX_DEFAULT
	giveitem ITEM_LYCANROCITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_LYCANROCITE
	setflag FLAG_HIDE_ROUTE14_ROUGAROU
	removeobject LOCALID_ROUTE14_ROUGAROU_HOLLOW_ROUGAROU
	release
	end

Route14_RougarouHollow_EventScript_RougarouGone:
	msgbox Route14_RougarouHollow_Text_RougarouGone, MSGBOX_DEFAULT
	release
	end

Route14_RougarouHollow_Text_Rougarou1:
	.string "Something big stands in the hollow,\n"
	.string "silver in the dark. It lifts\p"
	.string "its head and howls, once.$"

Route14_RougarouHollow_Text_RougarouRan:
	.string "The rougarou melts into the cane.\n"
	.string "The hollow is quiet again.$"

Route14_RougarouHollow_Text_RougarouStone:
	.string "Where it stood, a stone glows dimly:\n"
	.string "a LYCANROCITE, left in the grass.$"

Route14_RougarouHollow_Text_RougarouGone:
	.string "The hollow is empty now. Only the\n"
	.string "wind, and a flattened ring of grass.$"
