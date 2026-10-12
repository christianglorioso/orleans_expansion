"""The route landmarks' own art (sources/orleans_custom/route_landmarks.png + .json, made by make_route_landmarks.py, request
art_requests/route_landmarks.md) on the route tilesets. make_route_tilesets.py applies it to the shared route set
(tilesets/orleans_route.json + recipes/orleans_route.json, in place, idempotently) before it copies that set into the
variants, so every route tileset can place every landmark: the tilesets are demand-driven, so a piece costs tiles only on
the maps that place it.

The json carries the recipe source ("source": name `lmk`, overlay-only: the art is drawn over whatever ground it stands on)
and a prefab per piece ("prefabs": rows of {"overlay": "lmk:x_y"} cells with door / walk flags), ready to use. A route
placement asks for a piece by name (route_features.py); with_placeholders() in firstpass.py uses the real prefab as soon
as a tileset config has it, otherwise its stand-in.

SKIP: pieces the route tilesets leave as stand-ins for now: fallen_line, fallen_line_b want dry ground, which the Gulf
route set (Route 2) has no terrain for (the dry-country set's 'd' only exists on orleans_route_dry).
Nothing here imports build.py.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "sources", "orleans_custom", "route_landmarks.json")
SKIP = ("fallen_line", "fallen_line_b")


def load():
    return json.load(open(ART, encoding="utf-8")) if os.path.exists(ART) else None


def apply(r, c, skip=SKIP):
    doc = load()
    if not doc or "source" not in doc:
        return False
    r["sources"] = [s for s in r["sources"] if s["name"] != doc["source"]["name"]]
    r["sources"].append(json.loads(json.dumps(doc["source"])))
    c["prefabs"] = {k: v for k, v in c["prefabs"].items() if not v.get("_lmk")}  # a re-run replaces the last drawing's
    for name, pf in doc["prefabs"].items():
        if name in skip:
            continue
        c["prefabs"][name] = dict(json.loads(json.dumps(pf)), _lmk=True)
    return True
