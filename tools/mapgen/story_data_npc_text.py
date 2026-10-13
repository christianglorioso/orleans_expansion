"""Proper lines for interior NPCs whose text was a leaked spec note (map-pass stage 2, NPC sprite / text pass 2026-10-13).

The mockup markers' notes ("tells the day's weather in each region...", "gives a Spicy Berry blend") became the generated NPC
text. story_overlay merges these over the generated people by index (the order of the room's markers): {room key: {index: text}}.
House style: 2 lines per box, 36 characters per line at most, backslash-n between lines, backslash-p for the next box. No designer notes,
no promises of events that do not exist, nothing from the post-game.
"""

TEXTS = {
    # ------------------------------------------------------------------ Land's End (story 33 to 37: the Gulf is strange, the pavilion rains)
    "lands_end_house_1": {0: "The boats go out at dawn, storm or\\nnot. The shrimp don't wait for us."},
    "lands_end_house_2": {0: "The herons on Route 20 nest in the\\nold pilings. Don't startle them."},
    "lands_end_house_4": {0: "The temple stood on dry land when\\nmy grandfather was young.\\pThen the Gulf came up to meet it.\\nNobody remembers who asked it to."},
    "lands_end_house_5": {0: "I've wanted a CLAMPERL since I was\\na boy. My RELICANTH misses the deep."},
    "lands_end_lookout": {0: "I've logged every storm since I was\\na boy. None sat still like this one."},
    "lands_end_marine_supply": {1: "The DROWNED TEMPLE's door won't open\\nfor just anyone. It wants a song."},
    "lands_end_pokecenter": {2: "Last stop before the open Gulf.\\nStock up. Nothing sells out there."},
    "lands_end_weather_station": {
        0: "Rain on the Gulf coast, sun in the\\ncane country. Pack for both.\\pRain teams love it here. Sun teams\\nlike REDFIELD better.",
        1: "The pressure drops every time the\\nGulf glows. The charts don't lie.",
    },
    # ------------------------------------------------------------------ Redfield (story 30 to 36: cane, peppers, the dry country going to dust)
    "redfield_bottling_works": {1: "Taste the new blend? TAMATO BERRY,\\nground fine. Hot enough for you?"},
    "redfield_house_1": {0: "The pepper rows love this heat. The\\nhotter the sun, the hotter the jar."},
    "redfield_house_2": {0: "Something glows in the mill yard at\\ndusk. Mama says don't look."},
    "redfield_pokecenter": {2: "Heading north? The dry country is\\nturning to dust. Take water."},
    "redfield_shotgun_house_1": {0: "The cane fields were greener before\\nthe storm. They'll be green again.",
                                 1: "I want a CHARMANDER more than\\nanything. I'd name him Pepper!"},
}


def merge(interior):
    """Add TEXTS to story_overlay.INTERIOR (existing entries keep their other fields and their other texts)."""
    for key, texts in TEXTS.items():
        interior.setdefault(key, {}).setdefault("texts", {}).update(texts)
