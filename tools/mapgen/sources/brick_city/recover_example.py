"""Recover the Brick City example map as a grid of source metatile ids by matching 16x16 cells."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, r"C:\Users\chris\orleans_expansion\orleans_expansion\tools\mapgen")
os.chdir(r"C:\Users\chris\orleans_expansion\orleans_expansion")
from render import Tilesets

M = json.load(open("tools/mapgen/tilesets/orleans_city.mapping.json"))["metatiles"]
brick = {k.split(":", 1)[1]: v for k, v in M.items() if k.startswith("brick:")}
ts = Tilesets("data/tilesets/primary/orleans_general", "data/tilesets/secondary/orleans_city")
cands = {}
for sid, mid in brick.items():
    try:
        cands[sid] = np.asarray(ts.metatile(mid).convert("RGB"), dtype=np.int32)
    except Exception as e:
        pass
ids = list(cands)
stack = np.stack([cands[i] for i in ids])  # n,16,16,3
ex = np.asarray(Image.open("tools/mapgen/sources/brick_city/example.png").convert("RGB"), dtype=np.int32)
H, W = ex.shape[:2]
best = None
for oy in range(16):
    for ox in range(16):
        # sample a few cells to score the offset
        err = 0
        for cy in range(2, 8):
            for cx in range(10, 20):
                y, x = oy + cy * 16, ox + cx * 16
                cell = ex[y:y + 16, x:x + 16]
                if cell.shape != (16, 16, 3):
                    continue
                err += ((stack - cell) ** 2).sum(axis=(1, 2, 3)).min()
        if best is None or err < best[0]:
            best = (err, ox, oy)
_, ox, oy = best
print("offset", ox, oy)
gw, gh = (W - ox) // 16, (H - oy) // 16
grid, errs = [], []
for cy in range(gh):
    row, erow = [], []
    for cx in range(gw):
        cell = ex[oy + cy * 16: oy + cy * 16 + 16, ox + cx * 16: ox + cx * 16 + 16]
        e = ((stack - cell) ** 2).sum(axis=(1, 2, 3))
        k = int(e.argmin())
        row.append(ids[k]); erow.append(int(e[k] / 768))
    grid.append(row); errs.append(erow)
json.dump({"offset": [ox, oy], "grid": grid, "err": errs}, open(sys.argv[1], "w"))
# render the recovered grid with labels
from PIL import ImageDraw
im = Image.new("RGB", (gw * 48, gh * 48))
for cy in range(gh):
    for cx in range(gw):
        im.paste(ts.metatile(brick[grid[cy][cx]]).resize((48, 48), Image.NEAREST), (cx * 48, cy * 48))
d = ImageDraw.Draw(im)
for cy in range(gh):
    for cx in range(gw):
        d.text((cx * 48 + 2, cy * 48 + 2), grid[cy][cx], fill=(0, 0, 0))
        d.text((cx * 48 + 1, cy * 48 + 1), grid[cy][cx], fill=(255, 255, 0))
        if errs[cy][cx] > 300:
            d.rectangle([cx * 48, cy * 48, cx * 48 + 47, cy * 48 + 47], outline=(255, 0, 0))
im.save(sys.argv[2])
print(gw, gh, "bad cells", sum(e > 300 for r in errs for e in r))
