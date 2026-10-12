"""Recompose the Orleans primary and every outdoor secondary (in that order), regenerate the metatile labels, then settle all maps
(build / compose what is asked / build) -- the whole tileset side of a rebuild, after an edit to the primary or a shared recipe.

usage (from the decomp root):  python tools/mapgen/recompose_all.py [--no-settle]
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

PY = [sys.executable, "-W", "ignore"]
ROOT = world.ROOT


def main(args):
    layouts = json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"]
    used = {l["secondary_tileset"] for l in layouts if l and l.get("primary_tileset") == "gTileset_OrleansGeneral"
            and l["width"] * l["height"] > 1}
    rec = []
    for f in sorted(os.listdir(os.path.join(HERE, "tilesets", "recipes"))):
        r = json.load(open(os.path.join(HERE, "tilesets", "recipes", f), encoding="utf-8"))
        if r["kind"] == "secondary" and r["symbol"] in used and r.get("primary_mapping") == "orleans_general.mapping.json":
            rec.append(os.path.join(HERE, "tilesets", "recipes", f))
    prim = os.path.join(HERE, "tilesets", "recipes", "orleans_general.json")
    out = subprocess.run(PY + [os.path.join(HERE, "compose.py"), prim] + rec + ["--register"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", cwd=ROOT)
    for line in (out.stdout + out.stderr).splitlines():
        if line.startswith("gTileset_") or "Error" in line or "Traceback" in line or "limit" in line:
            print(line)
    if out.returncode:
        raise SystemExit("compose failed")
    subprocess.run(PY + [os.path.join(HERE, "gen_metatile_labels.py")], cwd=ROOT)
    if "--no-settle" not in args:
        subprocess.run(PY + [os.path.join(HERE, "settle.py")], cwd=ROOT)


if __name__ == "__main__":
    main(sys.argv[1:])
