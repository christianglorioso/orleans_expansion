"""in-memory preview of the feather pass (nothing written): python tools/mapgen/feather_preview.py <out_dir> <map_stem> [...]
Builds the map in memory with EDGE_FEATHER_ALL=1 and draws it with the tileset as it is on disk (pieces that are still pending - baked edge
cells, new props - show as the plain tile under them); border blocks drawn past the edges like the engine does."""
import os, sys, warnings
os.environ.setdefault("EDGE_FEATHER_ALL", "1")
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build
from render import Tilesets
from PIL import Image

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for key in sys.argv[2:]:
    build.MAPPING.clear()
    b = build.Builder(os.path.join(HERE, "maps", key + ".json"))
    b.draw()
    ts = Tilesets(b.ts["primary_dir"], b.ts["secondary_dir"])
    w, h = b.w, b.h
    border = [build.hx(n) & 0x3FF for n in (b.border_names or b.ts["border"])]
    M = 5
    im = Image.new("RGB", ((w + 2 * M) * 16, (h + 2 * M) * 16))
    for y in range(-M, h + M):
        for x in range(-M, w + M):
            if 0 <= x < w and 0 <= y < h:
                v = b.blocks[y][x] & 0x3FF
            else:
                v = border[(x & 1) + (y & 1) * 2]
            try:
                im.paste(ts.metatile(v).convert("RGB"), ((x + M) * 16, (y + M) * 16))
            except Exception:
                pass
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(os.path.join(out, f"{key}.png"))
    print("wrote", key, im.size)
