PointeRouge_CapitolDeck_MapScripts::
	.byte 0

@ The observation deck's three telescopes hint at later areas (the high dry country, the river, the Basin).
PointeRouge_CapitolDeck_EventScript_TelescopeEast::
	msgbox PointeRouge_CapitolDeck_Text_TelescopeEast, MSGBOX_SIGN
	end

PointeRouge_CapitolDeck_EventScript_TelescopeRiver::
	msgbox PointeRouge_CapitolDeck_Text_TelescopeRiver, MSGBOX_SIGN
	end

PointeRouge_CapitolDeck_EventScript_TelescopeBasin::
	msgbox PointeRouge_CapitolDeck_Text_TelescopeBasin, MSGBOX_SIGN
	end

PointeRouge_CapitolDeck_Text_TelescopeEast:
	.string "A telescope aimed east. The high\n"
	.string "dry country shimmers with heat.\p"
	.string "Red dust hangs over the plains,\n"
	.string "thick as a wall.$"

PointeRouge_CapitolDeck_Text_TelescopeRiver:
	.string "A telescope aimed down the river.\n"
	.string "You can follow the Emerald River\p"
	.string "all the way back to CRESCENT CITY.$"

PointeRouge_CapitolDeck_Text_TelescopeBasin:
	.string "A telescope aimed far south. A\n"
	.string "storm sits over the Basin, where\p"
	.string "the rivers meet. It doesn't move.$"
