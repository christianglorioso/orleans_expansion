"""The dry-country route variant (orleans_route_dry): the route set plus the shared dry-country art
(sources/orleans_custom/dry_country.png + .json, art_requests/dry_country.md), for Routes 15, 16, 17, 23 and 24
(Redfield's neighbours: sugar cane, pepper rows, dry hills, the salt flats). make_route_tilesets.py calls apply(r, c)
after copying the route set; the variant stays demand-driven (compose keeps only what the maps place), palette v2.

It reuses redfield_tileset's wiring of the dry set (the dry-on-grass dual-grid autotile "dry" with connects "dg:=Gq",
the road set on dry ground, cane = encounter grass, pepper rows, field trees, rocks, pieces that bring their own
grass reseated onto sand) and adds what the routes need:

    terrain   d dry ground, g tall dry grass (encounter grass), G sugarcane (walk-in encounter grass), q pepper rows (blocking), Q pepper (encounter),
              w cane wall (blocking), e red earth, v gully, s salt flat (the v2 dual-grid sets; Q pepper encounter), . grass (the green meadow the
              dry ground fades into where a route meets a green map), : road on dry ground, & / % the city approach
              (paving breaking up into dirt, laid over the green: the old Johto dirt path, autotile "path_g")
    prefabs   sign (reseated on sand), shrine (the stone on sand), field_tree, field_tree_l, rock, rock_l (the dry set's pieces);
              every building source's own grass (cabins, barns, the cave mouth) is redrawn over sand
Nothing here imports build.py.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import redfield_tileset as rf  # noqa: E402

GRASS_COLORS = rf.PEPPER_COLORS
SAND = "dry:0_0"


def apply(r, c):
    dry = rf.load("dry_country.json")
    if not dry or "terrain" not in dry:
        raise SystemExit("dry_country.json missing: the dry routes need the dry-country art set")
    T, A = c["terrain"], c["autotile"]
    # the old Johto dirt path on grass: kept for the city approach stretch ('&' and '%'), which lies in the green
    A["path_g"] = copy.deepcopy(A["path"])
    T["d"] = {"name": "dry ground", "tile": "ekat:grass", "elev": 3}
    T["q"] = {"name": "pepper rows", "tile": "ekat:grass", "elev": 3}
    rf.dry_terrain(r, c, dry)
    # the dirt of the approach joins the road on dry ground and the paving, whichever family each cell belongs to
    T["p"] = {"name": "road on grass (the approach's roads in the green meadow)", "tile": "0D9", "elev": 3,
              "autotile": "path_g"}
    A["path"]["connects"] = A["path_g"]["connects"] = ":=&%p"
    A["paved"]["connects"] = "%&"
    for a in A.values():  # water's bank pieces and the like also go on dry ground
        if "apply_on" in a and "." in a["apply_on"] and "d" not in a["apply_on"]:
            a["apply_on"] += "d"
    # ---- the v2 sets: dual-grid corner autotiles on dry ground ("patch inside, dry[0] outside"), each <prefix> (the fill:
    # a cell or a list) + <prefix>_N ... <prefix>_sTRBL; apply_on is dry ground plus the set's own character
    t = dry["terrain"]
    src = next(s for s in r["sources"] if s["name"] == "dry")
    have = {m["id"] for m in src["metatiles"]}

    def reg(cell, behavior=None, suffix=""):
        x, y = cell
        mid = f"{x}_{y}{suffix}"
        if mid not in have:
            m = {"id": mid, "bottom": [x, y]}
            if behavior:
                m["behavior"] = behavior
            src["metatiles"].append(m)
            have.add(mid)
        return f"dry:{mid}"
    for m in src["metatiles"]:  # v2: dry grass is tall dry grass, the encounter grass of the dry hills and the salt flats
        if "dry_grass" in t and m["id"] == "{}_{}".format(*t["dry_grass"]):
            m["behavior"] = "MB_TALL_GRASS"
    T["g"] = {"name": "tall dry grass (wild encounters)", "tile": f"dry:{t['dry_grass'][0]}_{t['dry_grass'][1]}", "elev": 3}
    T["q"] = {"name": "pepper rows (blocking)", "tile": T["q"]["tile"], "elev": 3, "collision": 1}
    T["Q"] = {"name": "pepper rows (wild encounters)", "elev": 3,
              "tile": reg(t["pepper"], "MB_TALL_GRASS", "q")}
    SETS = {"cane_wall": ("w", "w", "dw", 1, "the cane wall (blocking cane-field backdrop)"),
            "salt": ("s", "s", "ds", 0, "the salt flat"),
            "red_earth": ("e", "eqQ", "de", 0, "red earth"),
            "gully": ("v", "v", "dv", 0, "a dry gully"),
            "dry_grass": ("g", "g", "dg", 0, "tall dry grass (wild encounters)"),  # v3: a continuous fill with a ragged border
            "rock_wall": ("r", "r", "dr", 1, "rock wall (blocking bedrock cliff)")}   # last: its face extension goes over the rest
    for prefix, (ch, con, on, coll, name) in SETS.items():
        if prefix not in t:
            continue
        fill = t[prefix] if isinstance(t[prefix][0], list) else [t[prefix]]
        a = {"kind": "corners", "connects": con, "apply_on": on, "elev": 3, "C": [reg(c) for c in fill]}
        if coll:
            a["collision"] = 1
        for k in rf.CORNER_KEYS:
            a[k] = reg(t[f"{prefix}_{k}"])
        if prefix == "rock_wall":  # the face extension row under every south edge (make_dry_country.face_cells)
            a["face"] = {k: reg(t[f"rock_wall_{k}"]) for k in ("face", "face_l", "face_r", "face_il", "face_ir", "face_ilr",
                                                                "face_l_ir", "face_r_il")}
        A[prefix] = a
        T[ch] = {"name": name, "tile": a["C"][0], "elev": 3, **({"collision": 1} if coll else {})}
    A["dry"]["connects"] += "".join(ch for ch, *_ in SETS.values()) + "Q&"   # every set is dry underfoot to the green meadow
    # ---- the border beyond the map edge: dry ground, not water
    c["border"] = ["dry:0_0", "dry:1_0", "dry:2_0", "dry:3_0"]
    # ---- buildings and props that bring their own grass: redrawn over sand
    for s in r["sources"]:
        if s.get("rebase_ground"):
            s["rebase_ground"]["base"] = SAND
    P = c["prefabs"]
    r["patches"] += [
        {"id": "sign_dry", "reseat": "johto:003", "base": SAND, "colors": GRASS_COLORS, "behavior": "MB_NORMAL"},
        {"id": "shrine_stone_dry", "lower": SAND, "upper": "soul:291", "layer": "covered", "behavior": "MB_NORMAL"},
    ]
    P["sign_g"] = dict(P["sign"], _comment="Wooden signpost on grass (the green meadow where the dry ground fades).")
    P["sign"] = {"_comment": "Wooden signpost (primary 003) reseated on sand.", "rows": [["patch:sign_dry"]]}
    P["shrine"] = {"_comment": "Rootkin shrine marker: a weathered stone standing on dry ground.", "door": None,
                   "rows": [["patch:shrine_stone_dry"]]}
    # ---- the route mills' art (make_route_mills_art.py): route_mill (Route 17's sugar mills), drying_shed (Route 16's sheds)
    mills = rf.load("route_mills.json")
    if mills and mills.get("pieces"):
        rf.add_pieces(r, c, "rm", mills.get("png", "route_mills.png"), mills, "Route mills and drying sheds (own art): overlays.")
    # ---- own art overlays: field trees, rocks
    if dry.get("pieces"):
        rf.add_pieces(r, c, "dry_o", dry.get("png", "dry_country.png"), {"pieces": dry["pieces"]}, "Dry-country objects.")
