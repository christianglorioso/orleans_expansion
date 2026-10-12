PointeRouge_MapScripts::
	.byte 0

@ Pointe Rouge's east edge (x=65) is closed by a dust storm until Rayquaza wakes (story 38) (Route 23 and 24 are late-game). Flag-based
@ trigger on every walkable cell of the last column: stepping onto one turns the player back west. See story_data_ch3.POINTE_ROUGE.
PointeRouge_EventScript_DustStorm::
	lockall
	msgbox PointeRouge_Text_DustStorm, MSGBOX_DEFAULT
	closemessage
	applymovement OBJ_EVENT_ID_PLAYER, PointeRouge_Movement_StepBackWest
	waitmovement 0
	releaseall
	end

PointeRouge_Movement_StepBackWest:
	walk_left
	step_end

PointeRouge_Text_DustStorm:
	.string "A wall of red dust rolls in from\nthe plains. No one can see to cross.\p"
	.string "Nobody crosses in this. It will\nhave to blow itself out first.$"

@ --- mapgen: generated NPC scripts (begin) ---

PointeRouge_EventScript_Kingfisher::
	msgbox PointeRouge_Text_Kingfisher, MSGBOX_NPC
	end

PointeRouge_Text_Kingfisher:
	.string "KINGFISHER: A badge? Prove you\ncan fish first. Try Route 5's lake!$"

PointeRouge_EventScript_Clerk::
	msgbox PointeRouge_Text_Clerk, MSGBOX_NPC
	end

PointeRouge_Text_Clerk:
	.string "The legislature's in session.\nThirty-four floors of arguing!$"

PointeRouge_EventScript_Worker::
	msgbox PointeRouge_Text_Worker, MSGBOX_NPC
	end

PointeRouge_Text_Worker:
	.string "Shift change at the refinery.\nSmell that? That's overtime.$"

PointeRouge_EventScript_Angler::
	msgbox PointeRouge_Text_Angler, MSGBOX_NPC
	end

PointeRouge_Text_Angler:
	.string "The Emerald runs deep here. The\nbig ones hide under the bridge.$"

PointeRouge_EventScript_Kid::
	msgbox PointeRouge_Text_Kid, MSGBOX_NPC
	end

PointeRouge_Text_Kid:
	.string "The magnolias smell like lemons!$"

PointeRouge_EventScript_Retiree::
	msgbox PointeRouge_Text_Retiree, MSGBOX_NPC
	end

PointeRouge_Text_Retiree:
	.string "Fifty years I've watched barges\npass this bench. Never the same\lriver twice.$"

PointeRouge_EventScript_Chemist::
	msgbox PointeRouge_Text_Chemist, MSGBOX_NPC
	end

PointeRouge_Text_Chemist:
	.string "Pressure's steady on column two.\nNobody touch the red valves!$"

PointeRouge_EventScript_Yardman::
	msgbox PointeRouge_Text_Yardman, MSGBOX_NPC
	end

PointeRouge_Text_Yardman:
	.string "Tank cars in, tank cars out.\nThe yard never sleeps.$"

PointeRouge_EventScript_Lass::
	msgbox PointeRouge_Text_Lass, MSGBOX_NPC
	end

PointeRouge_Text_Lass:
	.string "Our street has the best gardens\nin the whole capital.$"

PointeRouge_EventScript_Twin::
	msgbox PointeRouge_Text_Twin, MSGBOX_NPC
	end

PointeRouge_Text_Twin:
	.string "Kingfisher's POKéMON fly so fast\nthey ripple the river!$"

PointeRouge_EventScript_Pokefan::
	msgbox PointeRouge_Text_Pokefan, MSGBOX_NPC
	end

PointeRouge_Text_Pokefan:
	.string "On windy days something huge\ncircles the truss bridge...$"

PointeRouge_EventScript_Shopper::
	msgbox PointeRouge_Text_Shopper, MSGBOX_NPC
	end

PointeRouge_Text_Shopper:
	.string "The Mart's stocked for the session.\nEvery lawmaker wants Potions.$"

PointeRouge_EventScript_Sailor::
	msgbox PointeRouge_Text_Sailor, MSGBOX_NPC
	end

PointeRouge_Text_Sailor:
	.string "SAILOR: The riverboat sails for\nCrescent City from this pier.$"

PointeRouge_EventScript_SignWest::
	msgbox PointeRouge_Text_SignWest, MSGBOX_SIGN
	end

PointeRouge_Text_SignWest:
	.string "POINTE ROUGE\nCapital on the Emerald River.$"

PointeRouge_EventScript_SignEast::
	msgbox PointeRouge_Text_SignEast, MSGBOX_SIGN
	end

PointeRouge_Text_SignEast:
	.string "POINTE ROUGE\nThe Capitol is across the river.$"

PointeRouge_EventScript_SignSouth::
	msgbox PointeRouge_Text_SignSouth, MSGBOX_SIGN
	end

PointeRouge_Text_SignSouth:
	.string "POINTE ROUGE\nNorth: the Capitol. South: Route 4.$"

PointeRouge_EventScript_SignCapitol::
	msgbox PointeRouge_Text_SignCapitol, MSGBOX_SIGN
	end

PointeRouge_Text_SignCapitol:
	.string "STATE CAPITOL\nObservation deck open to all.$"

@ --- mapgen: generated NPC scripts (end) ---
