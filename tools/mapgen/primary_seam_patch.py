"""Seams review (2026-10-14): put the art agent's primary seam-band pieces B (rocks awash + cypress knee on water) and D (Johto path on
dry ground) into gTileset_OrleansGeneral WITHOUT re-composing the primary, so every existing metatile id, tile and palette stays
byte-identical (a re-compose re-packs the palettes: the committed data is not a fixed point of compose, measured: recomposing HEAD
alone changes the render of 31 of 36 maps).

usage (from the decomp root):  python tools/mapgen/primary_seam_patch.py        (idempotent)

  1. frees the shared pieces no built map places and whose tiles no secondary reuses (tilesets/primary_drop_names.json, measured on
     the built maps): their metatile slots are zeroed and their exclusive tiles become free tile slots;
  2. appends the pss:* pieces (tilesets/primary_seam_art/primary_seam_art.json + .png): the bottom layer is the existing water_C /
     dry:0_0 bottom, the top layer's 8x8 tiles are written into free tile slots (or share an identical existing tile) in the
     primary palette each fits, in new metatile ids after the last existing one; attributes: behaviour + layer type COVERED;
  3. updates tilesets/orleans_general.mapping.json (names, tile-content table the secondaries reuse tiles by).
The same pieces are in the primary recipe (make_primary_recipe.py), so a later full compose carries them too."""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, HERE)
import compose  # noqa: E402

PRIM = "data/tilesets/primary/orleans_general"
MAPPING = os.path.join(HERE, "tilesets", "orleans_general.mapping.json")
ART = os.path.join(HERE, "tilesets", "primary_seam_art")
DROP = os.path.join(HERE, "tilesets", "primary_drop_names.json")
COVERED = 1


def read_pal(i):
    lines = open(f"{PRIM}/palettes/{i:02d}.pal").read().split()
    return [tuple(int(x) for x in lines[3 + 3 * k:6 + 3 * k]) for k in range(16)]


def main():
    mp = json.load(open(MAPPING))
    names = mp["metatiles"]
    raw = bytearray(open(f"{PRIM}/metatiles.bin", "rb").read())
    attrs = bytearray(open(f"{PRIM}/metatile_attributes.bin", "rb").read())
    tiles_im = Image.open(f"{PRIM}/tiles.png")
    pal_png = tiles_im.getpalette()
    W = tiles_im.size[0] // 8
    tiles = np.array(tiles_im, dtype=np.uint8)
    pals = [read_pal(i) for i in range(6)]
    spec = json.load(open(os.path.join(ART, "primary_seam_art.json")))
    art = Image.open(os.path.join(ART, "primary_seam_art.png")).convert("RGBA")
    want = {k: v for k, v in spec["pieces"].items() if v["spec"] in ("B", "D")}
    beh = compose.behavior_ids()

    def tile_idx(t):
        x, y = (t % W) * 8, (t // W) * 8
        return tiles[y:y + 8, x:x + 8]

    def entry_words(mid):
        return list(struct.unpack_from("<8H", raw, mid * 16))

    # ---- 1. free what nobody uses
    drop = json.load(open(DROP))["names"]
    secondary_tiles = set()
    import glob
    for sd in glob.glob("data/tilesets/secondary/orleans_*"):
        r = open(sd + "/metatiles.bin", "rb").read()
        for i in range(len(r) // 16):
            for v in struct.unpack_from("<8H", r, i * 16):
                if (v & 0x3FF) < 512:
                    secondary_tiles.add(v & 0x3FF)
    gone = 0
    for n in drop:
        j = names.pop(n, None)
        mp["sig"].pop(n, None)
        if j is not None and not any(names[o] == j for o in names):
            raw[j * 16:j * 16 + 16] = bytes(16)
            attrs[j * 2:j * 2 + 2] = bytes(2)
            gone += 1
    # pss pieces from an earlier run are rebuilt below
    for n in [n for n in names if n.startswith("pss:")]:
        j = names.pop(n)
        raw[j * 16:j * 16 + 16] = bytes(16)
        attrs[j * 2:j * 2 + 2] = bytes(2)
    n_mt = len(raw) // 16
    while n_mt and not any(raw[(n_mt - 1) * 16:n_mt * 16]):
        n_mt -= 1                                      # trailing empty slots are not part of the table
    raw = raw[:n_mt * 16]
    attrs = attrs[:n_mt * 2]
    live = set(secondary_tiles) | {0}
    for i in range(n_mt):
        live |= {v & 0x3FF for v in entry_words(i)}
    # tile slots no metatile and no secondary uses (tile 0 is the blank)
    free = [t for t in range(1, 512) if t not in live]
    # ---- 2. the new pieces
    for tmap_key in [k for k, v in mp["tiles"].items() if v[0] in free]:
        mp["tiles"].pop(tmap_key)
    for h in [h for h, v in mp["content"].items() if v[0] in free]:
        mp["content"].pop(h)
    known = {}
    for t in range(1, 512):
        if t in live:
            idx = tile_idx(t)
            for hf in (0, 1):
                for vf in (0, 1):
                    f = idx[:, ::-1] if hf else idx
                    f = f[::-1] if vf else f
                    known.setdefault(f.tobytes(), (t, hf, vf))
    added_tiles = 0
    new_ids = {}
    for key, p in want.items():
        base = names[p["bottom"]] if p["bottom"] in names else None
        if base is None:
            raise SystemExit(f"base {p['bottom']} of pss:{key} is not in the primary")
        bottom = entry_words(base)[:4]
        cx, cy = p["top_cell"]
        cell = np.array(art.crop((cx * 16, cy * 16, cx * 16 + 16, cy * 16 + 16)))
        top = []
        for q, pal_no in enumerate(p["palettes"]):
            ox, oy = (q % 2) * 8, (q // 2) * 8
            quad = cell[oy:oy + 8, ox:ox + 8]
            idx = np.zeros((8, 8), np.uint8)
            opaque = (quad[..., 3] > 0) & ~np.all(quad[..., :3] == (255, 0, 255), axis=-1)      # magenta = transparent
            if not opaque.any():
                top.append(0)
                continue
            lookup = {c: k for k, c in enumerate(pals[pal_no]) if k}
            for y in range(8):
                for x in range(8):
                    if opaque[y, x]:
                        c = tuple(int(v) for v in quad[y, x, :3])
                        if c not in lookup:
                            raise SystemExit(f"pss:{key}: colour {c} is not in primary palette {pal_no}")
                        idx[y, x] = lookup[c]
            hit = known.get(idx.tobytes())
            if hit:
                t, hf, vf = hit
            else:
                if not free:
                    raise SystemExit("no free primary tile slot left")
                t, hf, vf = free.pop(0), 0, 0
                x0, y0 = (t % W) * 8, (t // W) * 8
                tiles[y0:y0 + 8, x0:x0 + 8] = idx
                for h in (0, 1):
                    for v in (0, 1):
                        f = idx[:, ::-1] if h else idx
                        f = f[::-1] if v else f
                        known.setdefault(f.tobytes(), (t, h, v))
                px = tuple(None if i == 0 else compose.gba_color(pals[pal_no][i]) for i in idx.reshape(-1))
                for h in (0, 1):
                    for v in (0, 1):
                        mp["content"].setdefault(compose.tile_hash(compose.flip(px, h, v)), [t, h, v, pal_no])
                added_tiles += 1
            top.append(t | (hf << 10) | (vf << 11) | (pal_no << 12))
        mid = len(raw) // 16
        raw += struct.pack("<8H", *bottom, *top)
        attrs += struct.pack("<H", beh[p["behavior"]] | (COVERED << 12))
        names["pss:" + key] = mid
        new_ids[key] = mid
    if len(raw) // 16 > 512:
        raise SystemExit("metatile table over 512")
    open(f"{PRIM}/metatiles.bin", "wb").write(raw)
    open(f"{PRIM}/metatile_attributes.bin", "wb").write(attrs)
    out = Image.fromarray(tiles, "P")
    out.putpalette(pal_png)
    out.save(f"{PRIM}/tiles.png")
    json.dump(mp, open(MAPPING, "w"), indent=0)
    print(f"freed {gone} pieces; added {len(new_ids)} pss pieces (ids {min(new_ids.values())}-{max(new_ids.values())}) and {added_tiles} tiles; "
          f"{len([t for t in range(1, 512) if t not in live]) - added_tiles - 0} ... free tile slots left: {len(free)}; metatiles {len(raw) // 16}/512")


if __name__ == "__main__":
    main()
