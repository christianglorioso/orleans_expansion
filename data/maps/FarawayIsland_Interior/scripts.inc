FarawayIsland_Interior_MapScripts::
	.byte 0

FarawayIsland_Interior_EventScript_HideMewWhenGrassCut::
	lockall
	fadescreenswapbuffers FADE_TO_BLACK
	setflag FLAG_HIDE_MEW
	removeobject LOCALID_FARAWAY_ISLAND_MEW
	fadescreenswapbuffers FADE_FROM_BLACK
	msgbox FarawayIsland_Interior_Text_TheFeelingOfBeingWatchedFaded, MSGBOX_DEFAULT
	closemessage
	releaseall
	end

FarawayIsland_Interior_Text_TheFeelingOfBeingWatchedFaded::
	.string "The feeling of being watched faded…$"
