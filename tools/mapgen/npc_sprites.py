"""Resolve OBJ_EVENT_GFX_* ids to their PNG + palette and render contact sheets.

usage (from the decomp root):
  python tools/mapgen/npc_sprites.py gallery OUT.png [NAME ...]   every (or the named) people sprite, labelled
  python tools/mapgen/npc_sprites.py sheet OUT.png                the interior NPC assignment, by map (tile_review/npc_sprites_sheet.png)
  python tools/mapgen/npc_sprites.py palettes                     OBJ palette tags per interior (limit: 16 slots, see gen3_limits.py)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.getcwd()
B = "src/data/object_events/"


def _read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8", errors="ignore").read()


def resolve():
    ptr = _read(B + "object_event_graphics_info_pointers.h")
    info = _read(B + "object_event_graphics_info.h")
    pics = _read(B + "object_event_pic_tables.h")
    gfx = _read(B + "object_event_graphics.h")
    sprpal = _read("src/event_object_movement.c")
    png = {m.group(1): m.group(2) for m in re.finditer(r'(gObjectEventPic_\w+)\[\]\s*=\s*INCGFX_U(?:16|32)\("([^"]+)"', gfx)}
    paln = {m.group(1): m.group(2) for m in re.finditer(r'(gObjectEventPal_\w+)\[\]\s*=\s*INCGFX_U16\("([^"]+)"', gfx)}
    tagpal = {m.group(2): m.group(1) for m in re.finditer(r"\{(gObjectEventPal_\w+),\s*(OBJ_EVENT_PAL_TAG_\w+)\}", sprpal)}
    pict = {}
    for m in re.finditer(r"sPicTable_(\w+)\[\]\s*=\s*\{(.*?)\};", pics, re.S):
        mm = re.search(r"overworld_\w+\((gObjectEventPic_\w+)", m.group(2))
        if mm:
            pict[m.group(1)] = mm.group(1)
    infos = {}
    for m in re.finditer(r"const struct ObjectEventGraphicsInfo (\w+)\s*=\s*\{(.*?)\n\};", info, re.S):
        b = m.group(2)
        im = re.search(r"\.images\s*=\s*sPicTable_(\w+)", b)
        pt = re.search(r"\.paletteTag\s*=\s*(\w+)", b)
        w = re.search(r"\.width\s*=\s*(\d+)", b)
        h = re.search(r"\.height\s*=\s*(\d+)", b)
        infos[m.group(1)] = (im.group(1) if im else None, pt.group(1) if pt else None, int(w.group(1)) if w else 16, int(h.group(1)) if h else 32)
    out = {}
    for m in re.finditer(r"\[(OBJ_EVENT_GFX_\w+)\]\s*=\s*&(\w+)", ptr):
        i = infos.get(m.group(2))
        if not i or not i[0]:
            continue
        p = png.get(pict.get(i[0], ""))
        pal = paln.get(tagpal.get(i[1], ""))
        out[m.group(1)] = {"png": p, "pal": pal, "tag": (i[1] or "").replace("OBJ_EVENT_PAL_TAG_", ""), "w": i[2], "h": i[3]}
    return out


def frame(info, scale=3):
    """Facing-down standing frame as an RGBA image, drawn with the palette its tag loads."""
    from PIL import Image
    im = Image.open(os.path.join(ROOT, info["png"]))
    if im.mode != "P":
        im = im.convert("P")
    if info["pal"]:
        rows = open(os.path.join(ROOT, info["pal"])).read().split()[3:]
        vals = list(map(int, rows))
        pal = []
        for i in range(0, 48, 3):
            pal += vals[i:i + 3]
        im.putpalette(pal + [0] * (768 - len(pal)))
    w, h = info["w"], info["h"]
    rgba = im.crop((0, 0, w, h)).convert("RGBA")
    px = rgba.load()
    bg = im.getpixel((0, 0))
    idx = im.crop((0, 0, w, h)).load()
    for y in range(h):
        for x in range(w):
            if idx[x, y] == 0:
                px[x, y] = (0, 0, 0, 0)
    return rgba.resize((w * scale, h * scale), Image.NEAREST)


def gallery(out, names):
    from PIL import Image, ImageDraw
    g = resolve()
    names = names or [n for n, i in g.items() if "/people/" in (i["png"] or "") and not n.endswith("_FRLG")]
    cw, ch = 110, 124
    cols = 10
    sheet = Image.new("RGB", (cols * cw, ((len(names) + cols - 1) // cols) * ch), (222, 214, 190))
    d = ImageDraw.Draw(sheet)
    for k, n in enumerate(names):
        x, y = (k % cols) * cw, (k // cols) * ch
        f = frame(g[n])
        sheet.paste(f, (x + (cw - f.width) // 2, y + 4), f)
        d.text((x + 3, y + 104), n.replace("OBJ_EVENT_GFX_", "")[:18], fill=(0, 0, 0))
    sheet.save(out)
    print(len(names), "sprites ->", out)


TOWNS = ("IsleMarais", "GrandOak", "OldWater", "StormsEdge", "CrescentCity", "PointeRouge", "CampCocodrie", "LutinsHollow", "Redfield",
         "LandsEnd")


def interiors():
    """[(map name, [(role, graphics id)])] for every Orleans interior map, in town order."""
    out = []
    for t in TOWNS:
        for d in sorted(os.listdir(os.path.join(ROOT, "data", "maps"))):
            if not d.startswith(t + "_"):
                continue
            m = json.load(open(os.path.join(ROOT, "data", "maps", d, "map.json"), encoding="utf-8"))
            if m.get("map_type") != "MAP_TYPE_INDOOR":
                continue
            pre = "LOCALID_" + m["id"][4:] + "_"
            ppl = [(re.sub(r"\d+$", "", o["local_id"][len(pre):] if o["local_id"].startswith(pre) else o["local_id"]).lower().replace("_", " "),
                    o["graphics_id"]) for o in m.get("object_events", [])]
            out.append((d, ppl))
    return out


def palettes():
    import gen3_limits as g3
    gfx = g3.load_gfx_palettes()
    worst = []
    for name, ppl in interiors():
        tags = {g3.palette_tag(gfx, gid) for _, gid in ppl}
        worst.append((len(tags) + len(g3.FIXED_PALETTES), name, sorted(tags)))
    worst.sort(reverse=True)
    for n, name, tags in worst[:8]:
        print(f"{n:2d}/16  {name}: {', '.join(tags)}")
    bad = [w for w in worst if w[0] > 16]
    print("npc_sprites palettes:", "FAIL" if bad else "ok", f"({len(worst)} interiors, worst {worst[0][0]} of 16 OBJ palettes)")
    return 1 if bad else 0


def sheet(out):
    from PIL import Image, ImageDraw
    g = resolve()
    ints = interiors()
    S = 2
    cw = 40
    W = 1700
    cells = []
    for name, ppl in ints:
        cells.append((name, ppl))
    # pack cells into rows
    rows, row, x = [], [], 0
    for name, ppl in cells:
        w = max(len(ppl) * cw, 150) + 14
        if x + w > W:
            rows.append(row)
            row, x = [], 0
        row.append((name, ppl, w))
        x += w
    rows.append(row)
    rh = 118
    img = Image.new("RGB", (W, len(rows) * rh + 34), (222, 214, 190))
    d = ImageDraw.Draw(img)
    d.text((8, 8), "Orleans interior NPC sprites (from tools/mapgen/build_interior.py SPRITE_BY_KIND / SPRITE_OVERRIDES), label = role", fill=(0, 0, 0))
    for r, row in enumerate(rows):
        x = 4
        y = 30 + r * rh
        for name, ppl, w in row:
            d.rectangle((x, y, x + w - 8, y + rh - 6), outline=(150, 140, 120))
            d.text((x + 3, y + 2), name, fill=(120, 0, 0))
            for k, (role, gid) in enumerate(ppl):
                label = role[:9]
                px = x + 3 + k * cw
                info = g.get(gid)
                if info and info["png"]:
                    f = frame(info, S)
                    img.paste(f, (px + (cw - f.width) // 2, y + 16), f)
                else:
                    d.rectangle((px + 6, y + 40, px + 30, y + 64), outline=(80, 80, 80))
                    d.text((px + 8, y + 46), gid.replace("OBJ_EVENT_GFX_SPECIES(", "")[:5], fill=(80, 80, 80))
                d.text((px, y + 86 + (k % 2) * 10), label, fill=(0, 0, 0))
            x += w
    img.save(out)
    print(len(ints), "interiors ->", out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["gallery"]:
        gallery(a[1], ["OBJ_EVENT_GFX_" + n for n in a[2:]])
    elif a[:1] == ["sheet"]:
        sheet(a[1])
    elif a[:1] == ["palettes"]:
        sys.exit(palettes())
