StormsEdge_LighthouseGallery_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, StormsEdge_LighthouseGallery_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, StormsEdge_LighthouseGallery_OnLoad
	.byte 0

@ Legendary lair, batch 2 (the lighthouse stair (always)); lairs.py builds this map from the approved mock (tile_review/set_pieces/lairs/batch2/zapdos_mock.json).
@ The legendary is the old route static, moved here with its script and flag: hidden below story 45 (FLAG_PG_*, cleared by the epilogue), retired only on a
@ catch, a 2-bar boss (setbossbattle), rolled when it is talked to, the guaranteed victory catch is the engine's.

StormsEdge_LighthouseGallery_OnTransition:
	setflag FLAG_TEMP_1
	call StormsEdge_LighthouseGallery_EventScript_PGSetup
	end

@ The way out is the hatch (10, 12), the arrival cell too: a trigger (a plain warp event on a normal cell never fires), armed by FLAG_TEMP_1; stepping off and on again leaves
StormsEdge_LighthouseGallery_EventScript_Exit::
	lockall
	applymovement OBJ_EVENT_ID_PLAYER, StormsEdge_LighthouseGallery_Movement_FaceDown
	waitmovement 0
	warp MAP_STORMS_EDGE_LIGHTHOUSE, 4, 3
	waitstate
	end

StormsEdge_LighthouseGallery_Movement_FaceDown:
	face_down
	step_end

StormsEdge_LighthouseGallery_OnLoad:
	call_if_set FLAG_STORMS_EDGE_GRID_RESTORED, StormsEdge_LighthouseGallery_EventScript_StateLanternLit
	end

@ --- post-game (moved here from the route when the batch-2 lairs were built) ---

@ OnTransition: hidden below story 45; at 45 and above the legendary shows until it is caught
StormsEdge_LighthouseGallery_EventScript_PGSetup:
	call_if_lt VAR_ORLEANS_STORY, 45, StormsEdge_LighthouseGallery_EventScript_PGHide
StormsEdge_LighthouseGallery_EventScript_PGSetupDone:
	return

StormsEdge_LighthouseGallery_EventScript_PGHide:
	setflag FLAG_PG_ZAPDOS
	return

StormsEdge_LighthouseGallery_EventScript_PgZapdos::
	lock
	faceplayer
	playmoncry SPECIES_ZAPDOS, CRY_MODE_ENCOUNTER
	msgbox StormsEdge_LighthouseGallery_Text_PGZapdos, MSGBOX_DEFAULT
	waitmoncry
	setbossbattle 2, BOSS_NO_FORM_CHANGE, 110
	setwildbattle SPECIES_ZAPDOS, 60
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, StormsEdge_LighthouseGallery_EventScript_PgZapdosDone
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, StormsEdge_LighthouseGallery_EventScript_PgZapdosStill
	release
	end

StormsEdge_LighthouseGallery_EventScript_PgZapdosStill:
	msgbox StormsEdge_LighthouseGallery_Text_PGStillZapdos, MSGBOX_DEFAULT
	release
	end

StormsEdge_LighthouseGallery_EventScript_PgZapdosDone:
	setflag FLAG_PG_ZAPDOS
	removeobject LOCALID_STORMS_EDGE_LIGHTHOUSE_GALLERY_PG_ZAPDOS
	release
	end

StormsEdge_LighthouseGallery_Text_PGZapdos:
	.string "ZAPDOS stands before you,\n"
	.string "crackling with stored lightning.$"

StormsEdge_LighthouseGallery_Text_PGStillZapdos:
	.string "ZAPDOS shakes itself off,\n"
	.string "still standing its ground.$"

@ --- end post-game ---

@ --- mapgen: generated NPC scripts (begin) ---

StormsEdge_LighthouseGallery_EventScript_StateLanternLit::
	setmetatile 8, 4, 0x251, TRUE
	setmetatile 9, 4, 0x252, TRUE
	setmetatile 10, 4, 0x253, TRUE
	setmetatile 11, 4, 0x254, TRUE
	setmetatile 8, 5, 0x255, TRUE
	setmetatile 9, 5, 0x256, TRUE
	setmetatile 10, 5, 0x257, TRUE
	setmetatile 11, 5, 0x258, TRUE
	setmetatile 8, 6, 0x259, TRUE
	setmetatile 9, 6, 0x25A, TRUE
	setmetatile 10, 6, 0x25B, TRUE
	setmetatile 11, 6, 0x25C, TRUE
	setmetatile 8, 7, 0x25D, TRUE
	setmetatile 9, 7, 0x25E, TRUE
	setmetatile 10, 7, 0x25F, TRUE
	setmetatile 11, 7, 0x260, TRUE
	return

@ --- mapgen: generated NPC scripts (end) ---
