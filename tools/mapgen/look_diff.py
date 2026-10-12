"""Compare every Orleans outdoor map with how it looked at a git revision (default HEAD): same cells, redrawn with the tilesets
of that revision and with today's, pixel by pixel.  For the edges pass: the maps must look the same, grass and water exactly.

usage (from the decomp root):
    python tools/mapgen/look_diff.py [--rev HEAD] [--out DIR] [map keys ...]

Prints per map: cells that differ at all, cells with a channel step > 12 and the largest step, and (by the revision's mapping
names) the steps on plain grass / water cells, which must be 0. --out writes <key>_look.png (old | new | where they differ).
"""
import json
import os
import struct
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402
from render import Tilesets  # noqa: E402

ROOT = world.ROOT


def git_show(rev, path, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, cwd=ROOT)
    if r.returncode:
        return False
    open(dest, "wb").write(r.stdout)
    return True


def checkout_dir(rev, path, dest):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, path], capture_output=True, text=True, cwd=ROOT).stdout.split()
    for f in out:
        git_show(rev, f, os.path.join(dest, os.path.relpath(f, path)))


def main(args):
    rev = args[args.index("--rev") + 1] if "--rev" in args else "HEAD"
    outdir = args[args.index("--out") + 1] if "--out" in args else None
    keys = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in ("--rev", "--out"))] or list(world.OUTDOOR)
    tmp = tempfile.mkdtemp(prefix="look_")
    recipes = {}
    for f in os.listdir(os.path.join(HERE, "tilesets", "recipes")):
        r = json.load(open(os.path.join(HERE, "tilesets", "recipes", f), encoding="utf-8"))
        recipes[r["symbol"]] = (r["kind"], r["dir"], f[:-5])
    layouts = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "data/layouts/layouts.json")))["layouts"] if l}
    old_cache = {}
    for key in keys:
        spec = json.load(open(os.path.join(HERE, "maps", key + ".json"), encoding="utf-8"))
        l = layouts[spec["layout"]]
        pk, pd, pn = recipes[l["primary_tileset"]]
        sk, sd, sn = recipes[l["secondary_tileset"]]
        for kind, d in ((pk, pd), (sk, sd)):
            if (kind, d) not in old_cache:
                checkout_dir(rev, f"data/tilesets/{kind}/{d}", os.path.join(tmp, kind, d))
                old_cache[(kind, d)] = True
        mp = {}
        for n in (pn, sn):
            p = os.path.join(tmp, "map_" + n + ".json")
            if not os.path.exists(p):
                git_show(rev, f"tools/mapgen/tilesets/{n}.mapping.json", p)
            mp[n] = json.load(open(p))["metatiles"]
        inv = {}
        for n in mp.values():
            for k, v in n.items():
                inv.setdefault(v, k)
        inv_new = {}
        for n in (pn, sn):
            for k, v in json.load(open(os.path.join(HERE, "tilesets", n + ".mapping.json")))["metatiles"].items():
                inv_new.setdefault(v, k)
        old = Tilesets(os.path.join(tmp, pk, pd), os.path.join(tmp, sk, sd))
        new = Tilesets(os.path.join(ROOT, "data/tilesets", pk, pd), os.path.join(ROOT, "data/tilesets", sk, sd))
        bo = os.path.join(tmp, "bin_" + key)
        git_show(rev, l["blockdata_filepath"], bo)
        ob = open(bo, "rb").read()
        nb = open(os.path.join(ROOT, l["blockdata_filepath"]), "rb").read()
        w, h = l["width"], l["height"]
        if len(ob) != len(nb):
            print(f"{key:16s} size changed at {rev}; skipped")
            continue
        o_blocks, n_blocks = struct.unpack(f"<{len(ob) // 2}H", ob), struct.unpack(f"<{len(nb) // 2}H", nb)
        img = Image.new("RGB", (w * 16 * 3, h * 16)) if outdir else None
        diff = big = renamed = 0
        moved = {}
        worst = gw = 0
        for i, (a, b) in enumerate(zip(o_blocks, n_blocks)):
            x, y = i % w, i // w
            ia, ib = old.metatile(a & 0x3FF), new.metatile(b & 0x3FF)
            da, db = list(ia.getdata()), list(ib.getdata())
            steps = max(max(abs(p - q) for p, q in zip(u, v)) for u, v in zip(da, db))
            name = inv.get(a & 0x3FF, "")
            if name != inv_new.get(b & 0x3FF, ""):
                renamed += 1
                moved[(name, inv_new.get(b & 0x3FF, ""))] = moved.get((name, inv_new.get(b & 0x3FF, "")), 0) + 1
            if steps:
                diff += 1
                worst = max(worst, steps)
                if steps > 12:
                    big += 1
                if name in ("ekat:grass", "ekat:water_C"):
                    gw = max(gw, steps)
            if img:
                img.paste(ia, (x * 16, y * 16))
                img.paste(ib, (w * 16 + x * 16, y * 16))
                if steps:
                    img.paste(Image.new("RGB", (16, 16), (255, 0, 255) if steps > 12 else (255, 200, 0)), (2 * w * 16 + x * 16, y * 16))
        print(f"{key:16s} {diff:5d}/{len(o_blocks):5d} cells differ, {big:5d} by > 12, largest step {worst:3d}; plain grass/water step {gw}; {renamed} cells are a different piece")
        if renamed and "--names" in args:
            for (a, b), n in sorted(moved.items(), key=lambda kv: -kv[1])[:8]:
                print(f"      {n:4d}  {a} -> {b}")
        if img:
            os.makedirs(outdir, exist_ok=True)
            img.save(os.path.join(outdir, key + "_look.png"))


if __name__ == "__main__":
    main(sys.argv[1:])
