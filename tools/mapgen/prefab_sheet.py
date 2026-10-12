"""Preview every building prefab of a tileset config on grass, to check colours, edges and doors.

usage (from the decomp root): python tools/mapgen/prefab_sheet.py <tileset config> <out.png> [prefab ...] [--blends]
(--blends: let the builder request overlay tiles, e.g. own-art buildings; then compose and run again)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = ("cypress", "knees", "log", "stump", "waterlog", "snag", "reeds", "shrine", "pier", "dock", "walk_")


def main(args):
    cfg_name, out = args[0], args[1]
    cfg = json.load(open(os.path.join(HERE, "tilesets", cfg_name + ".json"), encoding="utf-8"))
    names = [a for a in args[2:] if not a.startswith("--")] or [k for k in cfg["prefabs"] if not k.startswith(SKIP)]
    x, y, rowh, W = 1, 1, 0, 34
    placed = []
    for n in names:
        rows = cfg["prefabs"][n]["rows"]
        h, w = len(rows), len(rows[0])
        if x + w + 1 > W:
            x, y, rowh = 1, y + rowh + 2, 0
        placed.append({"prefab": n, "x": x, "y": y, "label": n})
        x += w + 2
        rowh = max(rowh, h)
    H = y + rowh + 2
    grid = [["."] * W for _ in range(H)]
    for b in placed:  # a street under every door
        d = cfg["prefabs"][b["prefab"]].get("door")
        for dx, dy in ([] if not d else d if isinstance(d[0], list) else [d]):
            for i in (0, 1):
                if b["y"] + dy + 1 < H:
                    grid[b["y"] + dy + 1][b["x"] + dx + i] = ":"
    key = f"_sheet_{cfg_name}"
    open(os.path.join(HERE, "maps", key + ".grid.txt"), "w").write("\n".join("".join(r) for r in grid) + "\n")
    spec = {"map": "Sheet", "map_const": "MAP_SHEET", "layout": "LAYOUT_SHEET", "layout_dir": "data/layouts/Sheet",
            "tileset": cfg_name, "grid": key + ".grid.txt", "edits": [], "buildings": placed, "objects": [],
            "items": [], "hidden_items": [], "signs": [], "exits": []}
    sp = os.path.join(HERE, "maps", key + ".json")
    json.dump(spec, open(sp, "w"), indent=1)
    flags = [] if "--blends" in args else ["--no-blends"]
    r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), sp, "--dry-run", "--preview", out] + flags,
                       capture_output=True, text=True)
    print((r.stdout + r.stderr).strip()[-600:])


if __name__ == "__main__":
    main(sys.argv[1:])
