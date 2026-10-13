"""Planning mockups for building interiors, drawn in the same style as ../orleans_maps/*.png so that
extract.py can read them later (36 px per tile, frame colour (91,83,70), key colours below).

usage (from the decomp root): python tools/mapgen/interiors.py [out_dir]
    default out_dir: ../orleans_maps/interiors
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PITCH = 36
HEADER = (47, 74, 58)
PAGE = (250, 247, 238)
FRAME = (91, 83, 70)
INK = (40, 40, 40)

# interior key colours (also registered in extract.py's TERRAIN table)
KEY = {
    "wall":    ((112, 92, 74), "Wall"),
    "wood":    ((226, 205, 166), "Wood floor"),
    "tile":    ((232, 232, 224), "Tile floor"),
    "mud":     ((176, 150, 116), "Mud / storm damage"),
    "water":   ((166, 207, 234), "Water"),
    "counter": ((171, 121, 82), "Counter / table"),
    "rug":     ((196, 98, 88), "Rug / mat"),
    "bed":     ((154, 176, 206), "Bed / cot"),
    "shelf":   ((134, 108, 92), "Shelves / cabinet"),
    "plant":   ((126, 184, 96), "Planter / bed"),
    "hedge":   ((78, 132, 70), "Hedge"),
    "grass":   ((150, 206, 170), "Grass floor"),
    "sand":    ((222, 198, 128), "Sand path"),
    "flowers": ((232, 140, 160), "Flowers"),
    "statue":  ((150, 150, 160), "Gym statue"),
    "stool":   ((150, 110, 70), "Stool"),
    "glass":   ((198, 228, 238), "Glass wall"),
    "stage":   ((205, 170, 110), "Stage / platform"),
    "thatch":  ((184, 158, 92), "Thatch / woven wall"),
    "metal":   ((150, 156, 164), "Machinery / metal"),
    "stone":   ((205, 198, 186), "Stone floor"),
    "tomb":    ((120, 118, 128), "Tomb / crypt wall"),
    "moss":    ((120, 152, 108), "Moss curtain"),
    "carpet":  ((150, 72, 92), "Carpet"),
    "screen":  ((62, 72, 92), "Screen / display"),
    "tank":    ((96, 170, 210), "Tank / aquarium"),
    "exit":    ((70, 70, 70), "Door mat (exit)"),
}
MARK = {
    "npc": ((46, 134, 193), "N", "Key NPC"),
    "item": ((224, 168, 0), "i", "Item"),
    "event": ((211, 84, 0), "!", "Story event"),
    "hidden": ((154, 123, 46), "?", "Hidden item"),
    "trainer": ((192, 57, 43), "T", "Trainer"),
    "mega": ((169, 50, 38), "M", "Mega Stone"),
    "heal": ((214, 96, 120), "+", "Healing"),
    "shop": ((70, 110, 190), "$", "Shop"),
    "push": ((120, 90, 60), "P", "Pushable planter"),
    "switch": ((40, 150, 160), "S", "Switch / puzzle"),
    "service": ((92, 104, 124), "s", "Service"),
}


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE, F_SUB, F_H, F_TXT, F_LBL, F_MK = font(44, True), font(22), font(28, True), font(21), font(15, True), font(18, True)


def room(w, h, floor="wood", door=None, door_w=1):
    """Basic room: 2-tile back wall, 1-tile side walls, bottom wall with a door mat."""
    shapes = [("wall", 0, 0, w, h), (floor, 1, 2, w - 2, h - 3)]
    dx = door if door is not None else w // 2 - (door_w // 2)
    shapes.append(("exit", dx, h - 1, door_w, 1))
    return shapes


def draw(spec, out):
    w, h = spec["size"]
    mw, mh = w * PITCH, h * PITCH
    side = 760
    W = max(mw + 40 + side, 1500)
    H = 140 + max(mh + 60, 2400)
    im = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 126], fill=HEADER)
    d.text((32, 18), spec["title"], fill=(250, 247, 238), font=F_TITLE)
    d.text((34, 78), spec["subtitle"], fill=(214, 226, 214), font=F_SUB)
    tag = "Pokémon Orleans · interior planning layout · grid = 10 tiles"
    d.text((W - 24 - d.textlength(tag, font=F_SUB), 80), tag, fill=(214, 226, 214), font=F_SUB)

    ox, oy = 0, 140
    base = room(w, h, spec.get("floor", "wood"), spec.get("door"), spec.get("door_w", 1)) if not spec.get("custom_room") else []
    used = set()
    for kind, x, y, rw, rh, *lab in base + spec["shapes"]:
        used.add(kind)
        d.rectangle([ox + x * PITCH, oy + y * PITCH, ox + (x + rw) * PITCH - 1, oy + (y + rh) * PITCH - 1], fill=KEY[kind][0])
    # faint 10-tile grid, then the frame
    for gx in range(10, w, 10):
        d.line([(ox + gx * PITCH, oy), (ox + gx * PITCH, oy + mh)], fill=(150, 140, 125), width=1)
    for gy in range(10, h, 10):
        d.line([(ox, oy + gy * PITCH), (ox + mw, oy + gy * PITCH)], fill=(150, 140, 125), width=1)
    d.rectangle([ox, oy, ox + mw, oy + mh], outline=FRAME, width=3)
    # labels for shapes
    for kind, x, y, rw, rh, *lab in base + spec["shapes"]:
        if lab:
            cx, cy = ox + (x + rw / 2) * PITCH, oy + (y + rh / 2) * PITCH
            lines = lab[0].split("\n")
            for i, line in enumerate(lines):
                tw = d.textlength(line, font=F_LBL)
                ty = cy - 9 * len(lines) + i * 18
                d.text((cx - tw / 2, ty), line, fill=(255, 255, 255) if kind in ("wall", "counter", "shelf", "rug", "hedge", "exit") else INK, font=F_LBL)
    # exits
    for ex in spec.get("exits", []):
        x, y, label = ex
        cx, cy = ox + (x + 0.5) * PITCH, oy + (y + 1) * PITCH
        d.polygon([(cx - 16, cy + 2), (cx + 16, cy + 2), (cx, cy + 22)], fill=(30, 40, 50))
        tw = d.textlength(label, font=F_LBL)
        d.rounded_rectangle([cx - tw / 2 - 10, cy - 34, cx + tw / 2 + 10, cy - 10], 11, fill=(45, 52, 62))
        d.text((cx - tw / 2, cy - 33), label, fill=(255, 255, 255), font=F_LBL)
    # markers
    used_marks = set()
    for k, (kind, x, y, text) in enumerate(spec["markers"], 1):
        used_marks.add(kind)
        col, sym, _ = MARK[kind]
        cx, cy = ox + (x + 0.5) * PITCH, oy + (y + 0.5) * PITCH
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=col, outline=(255, 255, 255), width=2)
        d.text((cx - d.textlength(sym, font=F_MK) / 2, cy - 12), sym, fill=(255, 255, 255), font=F_MK)
        d.ellipse([cx + 6, cy - 26, cx + 26, cy - 6], fill=(30, 40, 50))
        n = str(k)
        d.text((cx + 16 - d.textlength(n, font=F_LBL) / 2, cy - 25), n, fill=(255, 255, 255), font=F_LBL)

    # side panel: key, points of interest, notes
    sx, sy = mw + 40, 150
    d.text((sx, sy), "Key", fill=HEADER, font=F_H)
    sy += 46
    for kind in KEY:
        if kind not in used:
            continue
        d.rectangle([sx, sy, sx + 34, sy + 24], fill=KEY[kind][0], outline=(120, 110, 95))
        d.text((sx + 48, sy - 2), KEY[kind][1], fill=INK, font=F_TXT)
        sy += 34
    for kind in MARK:
        if kind not in used_marks:
            continue
        col, sym, name = MARK[kind]
        d.ellipse([sx + 4, sy, sx + 28, sy + 24], fill=col)
        d.text((sx + 16 - d.textlength(sym, font=F_LBL) / 2, sy + 2), sym, fill=(255, 255, 255), font=F_LBL)
        d.text((sx + 48, sy - 2), name, fill=INK, font=F_TXT)
        sy += 34
    sy += 16
    d.text((sx, sy), "Points of interest", fill=HEADER, font=F_H)
    sy += 46
    for k, (kind, x, y, text) in enumerate(spec["markers"], 1):
        sy = wrap(d, sx, sy, f"{k}.  {text}", W - sx - 30, F_TXT)
    sy += 16
    d.text((sx, sy), "Notes", fill=HEADER, font=F_H)
    sy += 46
    for note in spec["notes"]:
        sy = wrap(d, sx, sy, "• " + note, W - sx - 30, F_TXT) + 6
    im = im.crop((0, 0, W, max(sy + 20, oy + mh + 60)))
    im.save(out)
    return im


def wrap(d, x, y, text, width, f):
    words, line = text.split(), ""
    for wd in words:
        t = (line + " " + wd).strip()
        if d.textlength(t, font=f) > width and line:
            d.text((x, y), line, fill=INK, font=f)
            y += 28
            line = "   " + wd
        else:
            line = t
    d.text((x, y), line, fill=INK, font=f)
    return y + 30


# ---------------------------------------------------------------------------------------------
# The interiors. Coordinates are tiles inside the room (0,0 = top-left of the back wall).

def house(title, sub, markers, notes, extra=(), floor="wood", size=(11, 9), furnished=True, rootkin=False, mat=None):
    w, h = size
    shapes = [("shelf", 1, 1, 2, 1, "shelves"), ("counter", 4, 4, 3, 2, "table"), ("rug", w // 2 - 1, h - 3, 3, 1)] if furnished else []
    if rootkin:  # thatched back wall and woven mats instead of a table
        mx, my, mw = mat or (2, h - 4, w - 4)
        shapes = [("thatch", 1, 0, w - 2, 2)] + ([("rug", mx, my, mw, 1, "woven mat")] if mat is not False else [])  # mat=False: none
        notes = list(notes) + ["Rootkin interior: plank floor, woven mats, thatch above the back wall. "
                               "Exterior: Rootkin stilt hut (3x4); the door is the ladder."]
    return {"title": title, "subtitle": sub, "size": size, "floor": floor, "shapes": shapes + list(extra),
            "markers": markers, "notes": notes, "exits": [(w // 2, h - 1, "Exit")]}


# the gym's hedge maze (# = hedge), placed with maze(x, y, rows)
MAZE = [
    "#########.#########",
    "#...#.........#...#",
    "#.#.###.###.###.#.#",
    "#.#...#.....#...#.#",
    "#.###.#.###.#.###.#",
    "#.#...#.....#...#.#",
    "#.#.###.###.###.#.#",
    "#.#.#.........#.#.#",
    "#.#.#.#######.#.#.#",
    "#.#.#.........#.#.#",
    "#.#.###.###.###.#.#",
    "#.#.............#.#",
    "#.###############.#",
    "#.................#",
    "#########.#########",
]


def maze(x0, y0, rows, kind="hedge"):
    return [(kind, x0 + x, y0 + y, 1, 1) for y, r in enumerate(rows) for x, c in enumerate(r) if c == "#"]


INTERIORS = {
    # ---------------- Isle Marais ----------------
    "isle_marais_shelter": {
        "title": "Fais Do-Do Dance Hall: Shelter", "subtitle": "Isle Marais · key building · the opening's hub",
        "size": (22, 15), "door": 10, "door_w": 1,
        "shapes": [
            ("stage", 6, 2, 10, 2, "stage → supply table"),
            ("counter", 7, 4, 8, 1, "supply table"),
            ("counter", 1, 3, 3, 1, "nurse"), ("bed", 1, 4, 1, 2), ("bed", 3, 4, 1, 2),
            ("counter", 16, 2, 5, 1, "field station: the three starter balls"), ("shelf", 19, 3, 2, 2, "PC /\nlab kit"),
            ("bed", 3, 7, 1, 2), ("bed", 5, 7, 1, 2), ("bed", 7, 7, 1, 2),
            ("bed", 14, 7, 1, 2), ("bed", 16, 7, 1, 2), ("bed", 18, 7, 1, 2),
            ("bed", 3, 10, 1, 2), ("bed", 5, 10, 1, 2), ("bed", 16, 10, 1, 2), ("bed", 18, 10, 1, 2),
            ("rug", 9, 7, 4, 4, "dance\nfloor"),
            ("counter", 1, 12, 2, 1, "hot\nfood"),
        ],
        "markers": [
            ("npc", 6, 9, "Mother: Running Shoes and PokéNav (the player's cot is next to hers)"),
            ("npc", 18, 5, "Professor Lafayette's field station (Pokédex is given on Route 1)"),
            ("event", 3, 13, "Rita's recruiters at the door: hot food and the snake-symbol pamphlet"),
            ("npc", 13, 12, "Fisherman: Old Rod"),
            ("heal", 2, 5, "Volunteer nurse: heals the party (the town has no Pokémon Center)"),
            ("shop", 11, 5, "Supply table: Potions and Poké Balls (the shelter's shop)"),
            ("event", 5, 1, "Battered accordion on the wall; someone plays it in the evening"),
            ("event", 13, 10, "Morning-after cutscene: neighbours, the call for help"),
        ],
        "notes": [
            "Cots fill the dance floor; the stage is now the supply table.",
            "After gym 6 the shelter closes: cots go, the hall holds its first dance (Fais Do-Do Ribbon).",
            "Post-game: festival layout with a band on the stage.",
            "Exterior: the wooden barn (6x5) north of the square; one door, so one exit tile.",
        ],
        "exits": [(10, 14, "Exit to Isle Marais")],
    },
    "isle_marais_players_house": house(
        "Player's House", "Isle Marais · key building · repaired (the storm-damaged state comes later)",
        [("npc", 3, 5, "Mother (when not at the shelter): later the player can rest here"),
         ("event", 2, 3, "TV: the weather channel, still talking about the storm"),
         ("item", 8, 4, "Bedside: the player's bag and a Potion")],
        ["Small family home: kitchen counter, table, TV, the player's bed and a bookshelf.",
         "Shown repaired for now; the damaged and half-repaired versions are later variants of the same room.",
         "Exterior: Shady Forest house with an ivy gable (5x5), south of the square."],
        extra=[("shelf", 1, 1, 2, 1, "TV"), ("counter", 4, 1, 3, 1, "kitchen"), ("shelf", 7, 1, 1, 1),
               ("counter", 4, 4, 3, 2, "table"), ("bed", 8, 2, 2, 2, "bed"), ("rug", 4, 6, 3, 1)], furnished=False),
    "isle_marais_church": {
        "title": "Church", "subtitle": "Isle Marais · the town church",
        "size": (15, 14), "door": 6, "door_w": 3, "floor": "tile",
        "shapes": [("stage", 5, 2, 5, 2, "altar"), ("shelf", 11, 2, 2, 1, "candles"), ("shelf", 2, 2, 2, 1, "candles"),
                   ("counter", 2, 6, 4, 1, "pew"), ("counter", 9, 6, 4, 1, "pew"),
                   ("counter", 2, 8, 4, 1, "pew"), ("counter", 9, 8, 4, 1, "pew"),
                   ("counter", 2, 10, 4, 1, "pew"), ("counter", 9, 10, 4, 1, "pew"),
                   ("rug", 6, 4, 3, 9, "aisle")],
        "markers": [("npc", 7, 4, "Priest: talks about the town coming back together"),
                    ("npc", 12, 4, "Bell ringer: rings the bell every hour"),
                    ("npc", 3, 12, "Parishioner: lights a candle for the people still away")],
        "notes": ["A quiet place with optional dialogue about the town and the storm.",
                  "Exterior: the Brick City church (6x7) with double doors. The aisle and the exit mat are three wide, centred under the altar."],
        "exits": [(7, 13, "Exit to Isle Marais")],
    },
    "isle_marais_tarp_house": house(
        "House (north-east)", "Isle Marais · neighbours",
        [("npc", 4, 6, "Neighbour: asks the player to check on the levee crew"),
         ("npc", 8, 6, "Child: trades a Poké Ball for a Pokémon seen on Route 1 (draft)"),
         ("item", 9, 2, "Item: Antidote")],
        ["Ordinary family home.", "Exterior: Shady Forest house with an ivy gable (5x5), north-east of the square."],
        extra=[("bed", 8, 2, 2, 2, "bed")]),
    "isle_marais_house_w": house(
        "House (west)", "Isle Marais · neighbours · the cabin west of the church path",
        [("npc", 4, 5, "Old fisherman: stories about the shrimp boats"),
         ("event", 7, 3, "Window: view of the channel")],
        ["Exterior: Shady Forest cabin (3x4)."], size=(9, 8)),
    "isle_marais_house_e": house(
        "House (east)", "Isle Marais · neighbours · the cabin by the barn path",
        [("npc", 3, 5, "Mother and baby: the baby only sleeps when the accordion plays"),
         ("item", 6, 2, "Item: Oran Berry")],
        ["Small, tidy, mostly undamaged.", "Exterior: Shady Forest cabin (3x4)."], size=(9, 8)),
    "isle_marais_house_tilted": house(
        "House (east-most)", "Isle Marais · neighbours · the east-most cabin",
        [("npc", 3, 5, "Owner: a retired shrimper who tells stories about the old boats"),
         ("item", 6, 2, "Item: Super Potion")],
        ["Ordinary small home.", "Exterior: Shady Forest cabin (3x4)."], size=(9, 8)),

    "isle_marais_players_house_damaged": house(
        "Player's House (storm-damaged)", "Isle Marais · variant · the opening (not livable)",
        [("event", 6, 6, "First visit: the watermark on every wall; mother's photo frame on the floor"),
         ("hidden", 2, 6, "Hidden item in the mud: Potion"),
         ("event", 2, 3, "TV (dead)")],
        ["Storm state: mud across the floor, furniture shoved against the walls, puddles.",
         "Used from the opening until gym 4; same room as the repaired version, so warps don't change."],
        extra=[("shelf", 1, 1, 2, 1, "TV"), ("counter", 4, 3, 3, 2, "table\n(tipped)"), ("mud", 1, 5, 4, 2),
               ("water", 7, 5, 2, 2), ("bed", 8, 2, 2, 2, "bed"), ("rug", 4, 6, 3, 1)], furnished=False),
    "isle_marais_players_house_patched": house(
        "Player's House (patched)", "Isle Marais · variant · gym 4 to gym 8",
        [("npc", 3, 5, "Mother: fixing up the house between shifts at the shelter"),
         ("event", 7, 6, "Tarp over the broken window; new boards on the floor")],
        ["Half repaired: the mud is gone, new floorboards (light), a tarp over one window, the bed still bare.",
         "The player can't rest here yet; that unlocks with the repaired version after gym 8."],
        extra=[("shelf", 1, 1, 2, 1, "TV"), ("counter", 4, 1, 3, 1, "kitchen"), ("counter", 4, 4, 3, 2, "table"),
               ("bed", 8, 2, 2, 2, "bed"), ("stage", 6, 6, 3, 1, "new boards"), ("water", 9, 1, 1, 1)], furnished=False),
    "isle_marais_dance_hall": {
        "title": "Fais Do-Do Dance Hall", "subtitle": "Isle Marais · variant · after gym 6 (the shelter closes)",
        "size": (22, 15), "door": 10, "door_w": 1,
        "shapes": [
            ("stage", 6, 2, 10, 2, "band stage"),
            ("rug", 6, 6, 10, 5, "dance floor"),
            ("counter", 1, 3, 3, 1, "drinks"), ("counter", 18, 3, 3, 1, "food"),
            ("counter", 1, 7, 2, 1, "table"), ("counter", 1, 10, 2, 1, "table"),
            ("counter", 19, 7, 2, 1, "table"), ("counter", 19, 10, 2, 1, "table"),
        ],
        "markers": [
            ("npc", 11, 4, "Accordion player: the first dance since the storm"),
            ("event", 9, 8, "Dancer: gives the Fais Do-Do Ribbon"),
            ("npc", 3, 5, "Mother: back home, here for the dance"),
            ("npc", 18, 5, "Professor Lafayette: packed up the field station"),
        ],
        "notes": ["Same room as the shelter: cots gone, stage back to a band stage, tables round the edge.",
                  "Exterior: the wooden barn (6x5) north of the square; one door."],
        "exits": [(10, 14, "Exit to Isle Marais")],
    },
    "isle_marais_festival": {
        "title": "Fais Do-Do Dance Hall: Festival", "subtitle": "Isle Marais · variant · post-game",
        "size": (22, 15), "door": 10, "door_w": 1,
        "shapes": [
            ("stage", 6, 2, 10, 2, "full band"),
            ("rug", 6, 6, 10, 5, "dance floor"),
            ("counter", 1, 3, 3, 1, "gumbo"), ("counter", 18, 3, 3, 1, "king cake"),
            ("counter", 1, 7, 2, 1, "table"), ("counter", 1, 10, 2, 1, "table"),
            ("counter", 19, 7, 2, 1, "table"), ("counter", 19, 10, 2, 1, "table"),
            ("plant", 1, 12, 2, 1, "garlands"), ("plant", 19, 12, 2, 1, "garlands"),
        ],
        "markers": [
            ("npc", 11, 4, "Band: Whismur, Loudred and Exploud join the music"),
            ("npc", 8, 8, "Jayden: a truce at the party"),
            ("npc", 13, 8, "Wren: the Rootkin come to the festival"),
            ("event", 2, 5, "Festival reward (draft)"),
        ],
        "notes": ["Post-game celebration in the same room; garlands and festival food.",
                  "The Whismur line is the dex's music group (design doc)."],
        "exits": [(10, 14, "Exit to Isle Marais")],
    },

    # ---------------- Grand Oak ----------------
    "grand_oak_pokecenter": {
        "title": "Pokémon Center", "subtitle": "Grand Oak · standard layout",
        "size": (15, 10), "door": 7, "floor": "tile",
        "shapes": [("counter", 5, 3, 5, 1, "counter"), ("shelf", 12, 2, 2, 1, "PC"),
                   ("counter", 1, 6, 2, 2, "table"), ("counter", 12, 6, 2, 2, "table"), ("rug", 6, 7, 3, 2)],
        "markers": [("heal", 7, 2, "Nurse Joy: heals the party"), ("npc", 12, 3, "PC (storage)"),
                    ("npc", 2, 5, "Traveller: Magnolia's gym uses Grassy Terrain; bring Bug, Flying or Poison types"),
                    ("npc", 11, 7, "Volunteer: the shelter in Isle Marais still needs supplies")],
        "notes": ["Standard Pokémon Center; reuse the vanilla interior tileset (gTileset_PokemonCenter)."],
        "exits": [(7, 9, "Exit to Grand Oak")],
    },
    "grand_oak_mart": {
        "title": "Poké Mart", "subtitle": "Grand Oak · standard layout",
        "size": (11, 8), "door": 5, "floor": "tile",
        "shapes": [("counter", 1, 3, 3, 1, "counter"), ("shelf", 5, 4, 4, 1, "shelves"), ("shelf", 5, 2, 4, 1, "shelves")],
        "markers": [("shop", 2, 2, "Clerk: Poké Balls, Potions, Antidotes, Paralyze Heal, Repel"),
                    ("npc", 7, 6, "Shopper: Rita's people bought out all the Super Potions")],
        "notes": ["Standard Mart; reuse the vanilla interior tileset (gTileset_Shop)."],
        "exits": [(5, 7, "Exit to Grand Oak")],
    },
    "grand_oak_gym": {
        "title": "Grand Oak Gym: Glass Conservatory", "subtitle": "Gym 1 · Magnolia (Grassy Terrain) · the hedge maze",
        "size": (21, 26), "door": 10, "floor": "grass",
        "shapes": [
            ("glass", 0, 0, 21, 2, "glass roof and walls"),
            ("glass", 0, 2, 1, 23), ("glass", 20, 2, 1, 23),
            ("stage", 8, 2, 5, 3, "Magnolia's dais"),
            ("flowers", 3, 3, 3, 2), ("flowers", 15, 3, 3, 2),
            *maze(1, 7, MAZE),
            ("sand", 1, 22, 19, 3, "entrance"),
            ("statue", 8, 22, 1, 2), ("statue", 12, 22, 1, 2),
        ],
        "markers": [
            ("npc", 13, 23, "Gym guide: 'Magnolia's waiting at the heart of the maze!'"),
            ("trainer", 13, 18, "Trainer: Gardener (Bug and Grass Pokémon)"),
            ("trainer", 12, 10, "Trainer: Aroma Lady"),
            ("npc", 10, 2, "Magnolia (Grassy Terrain): Roselia (iris form), Bonsly (cypress form), Tangela"),
        ],
        "notes": [
            "A mirrored hedge maze (HnS Celadon gym hedges) from the entrance plaza up to Magnolia's dais.",
            "Both trainers stand on the route to the leader.",
            "Reward: the first verse, a Grass TM and the Garden Shears (Cut replacement).",
            "Exterior: the glass greenhouse (10x7, own art) at the head of the fountain garden; one glass door.",
        ],
        "exits": [(10, 25, "Exit to Grand Oak")],
    },
    "grand_oak_nursery": house(
        "Garden Nursery (Berries)", "Grand Oak · berries and seeds",
        [("shop", 5, 3, "Nursery owner: one free Berry a day; explains planting"),
         ("npc", 2, 6, "Helper: soft soil plots outside the nursery (later)"),
         ("item", 9, 6, "Item: Miracle Seed? (if not used as the hidden item outside)")],
        ["Rows of potted berry plants; seed shelves on the back wall.", "Exterior: Shady Forest house with an ivy gable (5x5)."],
        extra=[("plant", 1, 4, 2, 2), ("plant", 8, 4, 2, 2), ("plant", 8, 2, 2, 1)], floor="tile", size=(11, 9)),
    "grand_oak_house_sw1": house(
        "House (south-west)", "Grand Oak · townsfolk",
        [("npc", 4, 5, "Grandmother: remembers when the magnolias were planted"), ("npc", 7, 6, "Grandson: wants a Bonsly")],
        ["Gentle dialogue about the storm.", "Exterior: Shady Forest cabin (3x4)."]),
    "grand_oak_house_sw2": house(
        "House (south-centre)", "Grand Oak · townsfolk",
        [("npc", 5, 5, "Woman: sells sugarcane to Crescent City; the road east is blocked by the storm hedge"),
         ("item", 9, 2, "Item: Pecha Berry")],
        ["Points the player toward the Garden Shears and Route 2.", "Exterior: Shady Forest cabin (3x4)."]),
    "grand_oak_house_se": house(
        "House (south-east)", "Grand Oak · townsfolk",
        [("npc", 4, 5, "Man: one of Rita's recruits, unsure about the pamphlet"),
         ("event", 8, 2, "The snake-symbol pamphlet on the table")],
        ["Small foreshadowing of Team Blacksnake recruiting among the displaced.", "Exterior: Shady Forest cabin (3x4)."]),

    # ---------------- The Old Water ----------------
    "old_water_healer": house(
        "Healer's House", "The Old Water · the Rootkin's Pokémon Center",
        [("heal", 5, 3, "Healer: heals the party with herbal remedies"), ("npc", 9, 4, "Apprentice: tends the patients; names the herbs drying overhead")],
        ["Herbs hang from the rafters; remedies in jars and baskets; a kettle on the hearth; two patients' bedrolls. No PC here."],
        extra=[("shelf", 2, 1, 2, 1, "herbs"), ("shelf", 7, 1, 2, 1, "herbs"), ("shelf", 1, 2, 1, 2, "remedies"),
               ("rug", 1, 5, 2, 2, "kettle"), ("bed", 7, 3, 2, 1, "bedroll"), ("bed", 7, 5, 2, 1, "bedroll")],
        rootkin=True, mat=False),
    "old_water_song_house": {
        "title": "Song House", "subtitle": "The Old Water · the round hall where the telling is kept",
        "size": (19, 14), "door": 9,
        "shapes": [("thatch", 1, 0, 17, 2), ("wall", 1, 2, 2, 1), ("wall", 16, 2, 2, 1), ("wall", 1, 3, 1, 1), ("wall", 17, 3, 1, 1),
                   ("wall", 1, 11, 1, 2), ("wall", 17, 11, 1, 2), ("wall", 2, 12, 1, 1), ("wall", 16, 12, 1, 1),
                   ("shelf", 5, 0, 2, 2, "verse 1"), ("shelf", 7, 0, 2, 2, "verse 2"), ("shelf", 10, 0, 2, 2, "verse 3"), ("shelf", 12, 0, 2, 2, "verse 4"),
                   ("stage", 4, 1, 1, 2, "orb\n(blue)"), ("stage", 9, 1, 1, 2, "Tupelo's seat"), ("stage", 14, 1, 1, 2, "orb\n(red)"),
                   ("rug", 8, 6, 3, 3, "fire\npit"),
                   ("stool", 6, 6, 1, 1), ("stool", 6, 8, 1, 1), ("stool", 12, 6, 1, 1), ("stool", 12, 8, 1, 1),
                   ("stool", 8, 10, 1, 1), ("stool", 10, 10, 1, 1),
                   ("shelf", 1, 6, 1, 2), ("shelf", 17, 6, 1, 2)],
        "markers": [("npc", 9, 2, "Tupelo the Storykeeper, in his chair: sings the first verse (trust event)"),
                    ("npc", 7, 7, "Wren: introduces the player to Tupelo"),
                    ("event", 6, 2, "Painted verses behind Tupelo: each verse the player brings back is painted on the wall"),
                    ("event", 4, 3, "Blue and red orbs kept either side of the verses (post-gym-8 quest)")],
        "notes": ["More wall panels light up as verses are gathered.", "Care note: the Rootkin and their customs are invented; no real sacred practices.", "Exterior: the round thatched song house (5x5, own art); the door is the top of the steps."],
        "exits": [(9, 13, "Exit to the Old Water")],
    },
    "old_water_trader": house(
        "Trader's House", "The Old Water · the Rootkin's shop",
        [("shop", 5, 3, "Trader: barters Berries and Balls for items found in the bayou"), ("npc", 2, 6, "Child: collects shiny shells")],
        ["Sells a small, swamp-themed stock (Net Ball, Dive Ball later).", "Baskets hang on the back wall; jars and baskets of stock along both side walls; wares laid out on the counter."],
        extra=[("shelf", 3, 1, 5, 1, "baskets"), ("counter", 3, 4, 5, 1, "trade counter"), ("shelf", 1, 2, 1, 3), ("shelf", 9, 2, 1, 3)],
        rootkin=True, mat=False),
    "old_water_carver": house(
        "Carver's Workshop", "The Old Water · cypress carving",
        [("npc", 5, 3, "Carver: carves the cypress-wood charm (Mega Evolution) after gym 6"),
         ("event", 3, 4, "Cypress logs drying by the wall")],
        ["Workbench with a half-carved charm, log pile, a canoe being carved, finished paddles on the wall."],
        extra=[("shelf", 4, 1, 3, 1, "paddles"), ("counter", 3, 4, 5, 1, "workbench"), ("stage", 1, 2, 2, 2, "logs"),
               ("counter", 9, 2, 1, 3, "canoe")],
        rootkin=True, mat=False),
    "old_water_tupelo": house(
        "Tupelo's House", "The Old Water · the Storykeeper's home",
        [("npc", 4, 4, "Tupelo (when not in the song house): small talk about the water"),
         ("item", 6, 3, "Item: a carved whistle? (story keepsake, draft)")],
        ["Simple and quiet: his own painting of the first verse on the wall, a bedroll, the hearth and a stool, his jars and baskets."],
        extra=[("shelf", 2, 0, 2, 2, "verse 1"), ("bed", 5, 2, 2, 1, "bedroll"), ("rug", 1, 4, 2, 2, "kettle"),
               ("stool", 3, 5, 1, 1), ("shelf", 7, 4, 1, 2)],
        size=(9, 8), rootkin=True, mat=False),
    "old_water_rest_house": house(
        "Rest House", "The Old Water · beds for guests",
        [("heal", 4, 2, "Host: rest here for a full heal (sleeping cutscene)")],
        ["Four guest bedrolls, two each side; the player can rest between key visits."],
        extra=[("bed", 1, 3, 2, 1), ("bed", 6, 3, 2, 1), ("bed", 1, 5, 2, 1), ("bed", 6, 5, 2, 1),
               ("shelf", 1, 1, 1, 1, "baskets"), ("shelf", 7, 1, 1, 1, "baskets")], size=(9, 8), rootkin=True, mat=False),
    "old_water_wren": house(
        "Wren's House", "The Old Water · Wren and her partner",
        [("npc", 4, 5, "Wren: friendly battles after the trust event; post-game rematches"),
         ("npc", 5, 4, "Wren's starter (the third rescued Pokémon)"),
         ("event", 1, 2, "Later: Own Tempo Rockruff from Wren (midpoint visit)")],
        ["A half-mended fishing net on the wall; bedrolls for Wren and her partner; baskets and jars either side."],
        extra=[("shelf", 3, 1, 3, 1, "net"), ("bed", 1, 3, 2, 1), ("bed", 6, 3, 2, 1),
               ("shelf", 1, 5, 1, 1), ("shelf", 7, 5, 1, 1)], size=(9, 8), rootkin=True, mat=False),
    "old_water_canoe_docks": house(
        "Canoe Docks", "The Old Water · the boatman's hut",
        [("npc", 4, 5, "Boatman: canoe back to Route 1's boat landing"),
         ("event", 3, 3, "Later: the player's own boat unlocks routes in stages (draft)")],
        ["Canoes and paddles stored along the walls.", "Canoe travel replaces Surf for reaching the village early on."],
        extra=[("counter", 1, 2, 1, 3, "canoe"), ("counter", 7, 2, 1, 3, "canoe"), ("shelf", 3, 1, 3, 1, "paddles"),
               ("shelf", 1, 6, 1, 1), ("shelf", 7, 6, 1, 1)],
        size=(9, 8), rootkin=True, mat=False),
}

# the rest of the game (towns after the vertical slice), in their own module
from interiors_world import GROUPS as WORLD_GROUPS, world  # noqa: E402
INTERIORS.update(world(house, maze))

GROUPS = [("Isle Marais", "isle_marais_"), ("Grand Oak", "grand_oak_"), ("The Old Water", "old_water_")]


def contact_sheet(out_dir, images, groups, title, subtitle, filename):
    thumbs = []
    for group, prefix in groups:
        row = [(k, im) for k, im in images if k.startswith(prefix)]
        thumbs.append((group, row))
    tw = 460
    rows_h = []
    for group, row in thumbs:
        hs = [int(im.height * tw / im.width) for _, im in row]
        rows_h.append(max(hs) if hs else 0)
    cols = min(max(len(r) for _, r in thumbs), 4)
    H = 140
    layout = []
    for (group, row), rh in zip(thumbs, rows_h):
        n_lines = (len(row) + cols - 1) // cols
        layout.append((group, row, rh, n_lines))
        H += 60 + n_lines * (rh + 30)
    W = cols * (tw + 20) + 20
    sheet = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 110], fill=HEADER)
    d.text((24, 18), title, fill=(250, 247, 238), font=F_TITLE)
    d.text((26, 74), subtitle, fill=(214, 226, 214), font=F_SUB)
    y = 130
    for group, row, rh, n_lines in layout:
        d.text((20, y), group, fill=HEADER, font=F_H)
        y += 50
        for i, (k, im) in enumerate(row):
            t = im.resize((tw, int(im.height * tw / im.width)), Image.LANCZOS)
            x = 20 + (i % cols) * (tw + 20)
            yy = y + (i // cols) * (rh + 30)
            sheet.paste(t, (x, yy))
        y += n_lines * (rh + 30) + 10
    sheet.save(os.path.join(out_dir, filename))


def main(args):
    out_dir = args[0] if args else os.path.join("..", "orleans_maps", "interiors")
    os.makedirs(out_dir, exist_ok=True)
    images = []
    for i, (key, spec) in enumerate(INTERIORS.items(), 1):
        path = os.path.join(out_dir, f"{i:02d}_{key}.png")
        images.append((key, draw(spec, path)))
        print(path)
    slice_ = [(k, im) for k, im in images if any(k.startswith(p) for _, p in GROUPS)]
    contact_sheet(out_dir, slice_, GROUPS, "Interiors: vertical slice",
                  f"{len(slice_)} interior mockups · Isle Marais, Grand Oak, the Old Water", "00_interiors_overview.png")
    for group, prefix in WORLD_GROUPS:  # one overview sheet per town for the rest of the game
        rooms = [(k, im) for k, im in images if k.startswith(prefix)]
        contact_sheet(out_dir, rooms, [(group, prefix)], f"Interiors: {group}",
                      f"{len(rooms)} interior mockups", f"00_overview_{prefix.rstrip('_')}.png")


if __name__ == "__main__":
    main(sys.argv[1:])
