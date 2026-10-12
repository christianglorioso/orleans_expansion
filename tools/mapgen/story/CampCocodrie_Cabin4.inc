CampCocodrie_Cabin4_MapScripts::
	.byte 0

@ The okra (cook-off ingredient): the gardener says to pick it from the patch behind the cabin (CampCocodrie.inc, OkraPatch1/2).
CampCocodrie_Cabin4_EventScript_Gardener0::
	lock
	faceplayer
	goto_if_set FLAG_CAMP_OKRA, CampCocodrie_Cabin4_EventScript_Done
	setflag FLAG_CAMP_OKRA_ASKED
	msgbox CampCocodrie_Cabin4_Text_Ask, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Cabin4_EventScript_Done:
	msgbox CampCocodrie_Cabin4_Text_Done, MSGBOX_DEFAULT
	release
	end

CampCocodrie_Cabin4_Text_Ask:
	.string "GARDENER: Okra for the cook-off?\n"
	.string "Help yourself. The patch is out\p"
	.string "back, north of the cabin. Pick\n"
	.string "the small ones. The big ones\p"
	.string "go woody.$"

CampCocodrie_Cabin4_Text_Done:
	.string "GARDENER: Small ones, mind. Big ones\n"
	.string "go woody. I'll say it forever.$"
