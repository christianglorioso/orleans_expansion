CampCocodrie_Smokehouse_MapScripts::
	.byte 0

@ The andouille (cook-off ingredient): stoke the smoker's fire door (bg event at (5, 5), stand at (5, 6)), then ask the smoker.
CampCocodrie_Smokehouse_EventScript_FireDoor::
	lockall
	goto_if_set FLAG_CAMP_FIRE_STOKED, CampCocodrie_Smokehouse_EventScript_FireHot
	setflag FLAG_CAMP_FIRE_STOKED
	msgbox CampCocodrie_Smokehouse_Text_FireStoked, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Smokehouse_EventScript_FireHot:
	msgbox CampCocodrie_Smokehouse_Text_FireHot, MSGBOX_DEFAULT
	releaseall
	end

CampCocodrie_Smokehouse_EventScript_Smoker0::
	lock
	faceplayer
	goto_if_set FLAG_CAMP_ANDOUILLE, CampCocodrie_Smokehouse_EventScript_SmokerDone
	goto_if_set FLAG_CAMP_FIRE_STOKED, CampCocodrie_Smokehouse_EventScript_SmokerGives
	msgbox CampCocodrie_Smokehouse_Text_SmokerAsk, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Smokehouse_EventScript_SmokerGives:
	setflag FLAG_CAMP_ANDOUILLE
	msgbox CampCocodrie_Smokehouse_Text_SmokerGives, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Smokehouse_EventScript_SmokerDone:
	msgbox CampCocodrie_Smokehouse_Text_SmokerDone, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Smokehouse_Text_FireStoked:
	.string "You haul the smoker's door open and\n"
	.string "feed the fire. Pecan wood. The\p"
	.string "sausages sigh and start to sweat.$"

CampCocodrie_Smokehouse_Text_FireHot:
	.string "The smoker's roaring now. Sausages\n"
	.string "hang in the haze, glistening.$"

CampCocodrie_Smokehouse_Text_SmokerAsk:
	.string "SMOKER: The fire's gone low and my\n"
	.string "knees are gone lower.\p"
	.string "Stoke the smoker, kid, and I'll\n"
	.string "give you a ring of andouille for\p"
	.string "the brothers' pot. The door's on\n"
	.string "the front.$"

CampCocodrie_Smokehouse_Text_SmokerGives:
	.string "SMOKER: That's a fire! Here. The\n"
	.string "best andouille in the region.\p"
	.string "{PLAYER} received the ANDOUILLE!\n"
	.string "Tell the brothers it's from me.$"

CampCocodrie_Smokehouse_Text_SmokerDone:
	.string "SMOKER: The andouille's theirs now.\n"
	.string "I just smoke. They cook.$"

@ --- mapgen: generated NPC scripts (begin) ---


@ --- mapgen: generated NPC scripts (end) ---
