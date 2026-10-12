CampCocodrie_DancePorch_MapScripts::
	.byte 0

@ The zydeco band plays only at night (OrleansSvc_IsNight). After the sixth badge (the hollow's verse) the band gives the Exploudite, once
@ (bag-full safe: the flag is set after the stone is in the bag).
CampCocodrie_DancePorch_EventScript_ZydecoBand0::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_EXPLOUDITE, CampCocodrie_DancePorch_EventScript_BandDone
	special OrleansSvc_IsNight
	goto_if_eq VAR_RESULT, FALSE, CampCocodrie_DancePorch_EventScript_BandDay
	goto_if_unset FLAG_BADGE06_GET, CampCocodrie_DancePorch_EventScript_BandEarly
	msgbox CampCocodrie_DancePorch_Text_BandGives, MSGBOX_DEFAULT
	giveitem ITEM_EXPLOUDITE
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_EXPLOUDITE
	release
	end

CampCocodrie_DancePorch_EventScript_BandDay:
	msgbox CampCocodrie_DancePorch_Text_BandDay, MSGBOX_DEFAULT
	release
	end

CampCocodrie_DancePorch_EventScript_BandEarly:
	msgbox CampCocodrie_DancePorch_Text_BandEarly, MSGBOX_DEFAULT
	release
	end

CampCocodrie_DancePorch_EventScript_BandDone:
	msgbox CampCocodrie_DancePorch_Text_BandDone, MSGBOX_DEFAULT
	release
	end

CampCocodrie_DancePorch_Text_BandDay:
	.string "BAND: We play at night. The\naccordion gets lonesome by day.$"

CampCocodrie_DancePorch_Text_BandEarly:
	.string "BAND: Tonight we play for the\nbrothers. Play louder after a hard\p"
	.string "verse. Ask us once you have six.$"

CampCocodrie_DancePorch_Text_BandGives:
	.string "BAND: Six verses! Then the night is\nours to play. Here, a stone we\p"
	.string "kept for someone who earned the\nloudest song.\p"
	.string "EXPLOUDITE. Hold it, and let your\nPOKéMON shout.$"

CampCocodrie_DancePorch_Text_BandDone:
	.string "BAND: The loudest song in the\nregion. Tonight and every night.$"

