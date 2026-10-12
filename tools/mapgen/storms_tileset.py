"""Storm's Edge's own pieces on top of the orleans_port tileset variant (make_town_tilesets.py calls apply() for
VARIANTS["orleans_port"]["addon"]). The variant stays demand-driven (compose keeps only what storms_edge.py places)
with the v2 palette packer.

Adds:
    terrain   '%' the substation yard's paving (Johto flagstone from the primary, no secondary tiles), '&' paving
              breaking up into the dirt road at the yard's gate (approach.py draws it), 'w' harbour water with no
              lily pads (the water autotile treats it as water)
    own art   (sources/orleans_custom/make_storms_art.py) the dark plank quay and long pier, the stilt row under
              the stilt houses, the substation's gantries, transformers, switch cabinets, fence wires and danger
              sign, the downed line, the drawbridge raised (leaves and barriers), the Pokemon Center's generator
              and the gym's bolt emblem
    brick     the substation hall: Brick City's hall made symmetric (its lower windows mirrored with hflip
              patches, the porch centred, steps on paving instead of grass)
    primary   the grey post-and-rail fence and a signpost (free: they live in the primary)
    props     barrel and crab trap from the shared props sheet
"""

ART = "tools/mapgen/sources/orleans_custom/"


def image(name, png, cells):
    return {"name": name, "type": "image", "image": ART + png, "transparent": [[255, 0, 255]], "overlay_only": True,
            "_comment": "Storm's Edge own art (make_storms_art.py), overlays.",
            "metatiles": [{"id": f"{x}_{y}", "bottom": [x, y]} for x, y in cells]}


def grid(x0, y0, w, h):
    return [(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)]


def ov(src, x, y, **kw):
    return dict({"overlay": f"{src}:{x}_{y}"}, **kw)


B = lambda i: f"brick:{i}"
# the substation hall, 9x9: Brick City hall pieces, the lower windows on the right mirrored from the left
SUBSTATION = [
    [B("220")] + [B("221")] * 7 + [B("223")],
    [B("228")] + [B("229")] * 7 + [B("237")],
    [B("22A")] + [B("22B")] * 7 + [B("233")],
    [B("238"), B("293"), B("294"), B("23A"), B("23A"), B("23A"), B("293"), B("294"), B("216")],
    [B("238"), B("29B"), B("29C"), B("23A"), B("23A"), B("23A"), B("29B"), B("29C"), B("216")],
    [B("238"), B("246"), B("247"), B("23A"), B("23A"), B("23A"), B("246"), B("247"), B("216")],
    [B("280"), B("284"), B("260"), B("2AC"), B("2AD"), B("2AE"), "patch:se_h260", "patch:se_h284", "patch:se_h280"],
    [B("281"), B("28A"), B("2A6"), B("2B4"), "patch:hall_door", B("2B6"), "patch:se_h2A6", "patch:se_h28A",
     "patch:se_h281"],
    [None, None, None, "patch:se_step_l", "patch:se_step", "patch:se_step_r", None, None, None],
]


def apply(r, c):
    # ---- recipe: own art, symmetric hall pieces, steps on paving, extra props
    r["sources"] += [
        image("seq", "storms_planks.png", grid(0, 0, 7, 4)),
        image("sst", "storms_stilt.png", grid(0, 0, 3, 1)),
        image("ssb", "storms_sub.png", grid(0, 0, 8, 4)),
        image("spl", "storms_poles.png", grid(0, 0, 3, 12)),
        image("sbr", "storms_bridge.png", grid(0, 0, 4, 4)),
        image("smi", "storms_misc.png", grid(0, 0, 3, 1)),
    ]
    r["patches"] += [{"id": f"se_h{i}", "lower": f"brick:{i}", "hflip": True} for i in ("260", "284", "280", "2A6", "28A", "281")]
    r["patches"] += [{"id": "se_step_l", "lower": "johto:1C1", "upper": "brick:2BC"},
                     {"id": "se_step", "lower": "johto:1C1", "upper": "brick:2BD"},
                     {"id": "se_step_r", "lower": "johto:1C1", "upper": "brick:2BE"}]
    props = next(s for s in r["sources"] if s["name"] == "props")
    have = {m["id"] for m in props["metatiles"]}
    props["metatiles"] += [m for m in ({"id": "barrel", "bottom": [5, 1]}, {"id": "trap", "bottom": [7, 1]})
                           if m["id"] not in have]
    # ---- builder config: terrain
    T, A = c["terrain"], c["autotile"]
    T["%"] = {"name": "the substation yard's paving (Johto flagstone, primary)", "tile": "1C1", "elev": 3,
              "autotile": "paved"}
    T["&"] = {"name": "paving breaking up into the dirt road (approach.py draws the paving over it)", "tile": "0D9",
              "elev": 3, "autotile": "path"}
    T["w"] = {"name": "harbour water (no lily pads)", "tile": "ekat:water_C", "elev": 1}
    A["paved"] = {"_comment": "Johto flagstone paving on grass (primary 1B8-1CA): the substation yard.",
                  "connects": "%&", "NW": "1B8", "N": "1B9", "NE": "1BA", "W": "1C0", "C": "1C1", "E": "1C2",
                  "SW": "1C8", "S": "1C9", "SE": "1CA", "iNW": "1BB", "iNE": "1BC", "iSW": "1C3", "iSE": "1C4"}
    A["path"]["connects"] = ":=&%"
    w = A["water"]
    w["connects"] = "~w"
    w["apply_on"] = w["apply_on"] + "w"
    w["smooth"] = "~w"
    for a in A.values():  # patches lay their borders over the yard's edge cells and the break-up cells too
        if a.get("kind") == "corners" and "apply_on" in a:
            a["apply_on"] += "".join(ch for ch in "%&" if ch not in a["apply_on"])
    # ---- prefabs
    P = c["prefabs"]
    rows = [[ov("seq", x, y) for x in range(3)] for y in range(4)]
    for k in ("waterlog", "snag_water", "cypress_water"):  # the harbour's water ('w') counts as their patch too
        P[k]["on_patch"] = "~w"
    P["quay"] = {"_comment": "Dark plank boardwalk (own art): rows and passable cells come from the spec.",
                 "rows": rows}
    hall = [list(row) for row in SUBSTATION]
    P["substation"] = {"_comment": "Storm's Edge gym, the substation hall (Brick City hall made symmetric), 9x9.",
                       "rows": hall, "door": [4, 7], "passable": [[3, 8], [4, 8], [5, 8]]}
    cab = P["cabin"]["rows"]
    P["stilt_house"] = {"_comment": "Stilt house: the Shady cabin over a stilt row (own art) standing in the water; "
                                    "steps down from the door to the quay.",
                        "rows": cab + [[ov("sst", 0, 0), ov("sst", 1, 0, walk=True), ov("sst", 2, 0)]],
                        "door": [1, 3], "passable": [[1, 4]]}
    for side in ("l", "r"):  # the right-hand pieces are the mirrored half of the sheet (cells 4..7)
        gx = 0 + 7 * (side == "r")
        tx = 1 + 4 * (side == "r")
        cx = 3 + 1 * (side == "r")
        P[f"gantry_{side}"] = {"_comment": "Lattice gantry with insulator strings (own art), 1x3.",
                               "rows": [[ov("ssb", gx, y)] for y in range(3)]}
        P[f"transformer_{side}"] = {"_comment": "Transformer with porcelain bushings (own art), 2x2.",
                                    "rows": [[ov("ssb", tx + i, 1 + j) for i in range(2)] for j in range(2)]}
        P[f"cabinet_{side}"] = {"_comment": "Switch cabinet (own art), 1x2.", "rows": [[ov("ssb", cx, 0)], [ov("ssb", cx, 1)]]}
        P[f"fence_wires_{side}"] = {"_comment": "The incoming line's wires over the top fence (own art).",
                                    "rows": [[ov("ssb", gx, 3)]]}
    P["fence_sign"] = {"_comment": "Danger sign on a fence panel (own art).", "rows": [[ov("ssb", 3, 2)]]}
    poles = []
    for y in range(12):
        poles.append([ov("spl", x, y) for x in range(3)])
    P["downed_line"] = {"_comment": "The downed line (own art), 3x12: empty cells are cut by storms_edge.py.",
                        "rows": poles}
    P["bridge_raised"] = {"_comment": "Drawbridge raised (own art): leaves 1x4 (x 0 west, 1 east), barriers 1x2 over "
                                      "the deck (x 2 west, 3 east). Swapped in by the map script (spec states).",
                          "rows": [[ov("sbr", x, y) for x in range(4)] for y in range(4)]}
    P["emblem"] = {"_comment": "The gym's bolt emblem (own art), placed over the hall's brick after the hall.",
                   "rows": [[ov("smi", 2, 0)]]}
    P["generator"] = {"_comment": "The Pokemon Center's generator (own art), 2x1.", "rows": [[ov("smi", 0, 0), ov("smi", 1, 0)]]}
    P["fence"] = {"_comment": "Grey post-and-rail fence piece (primary 0EC-0FD, 136): rows come from the spec.",
                  "rows": [["0ED"]]}
    P["sign"] = {"_comment": "Wooden signpost (primary 003).", "rows": [["003"]]}
    P["barrel"] = {"_comment": "Barrel (own art).", "rows": [[{"overlay": "props:barrel"}]]}
    P["trap"] = {"_comment": "Crab trap (own art).", "rows": [[{"overlay": "props:trap"}]]}
