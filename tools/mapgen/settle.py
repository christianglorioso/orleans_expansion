"""Build maps until no tileset asks for another piece: build, compose the tilesets that were asked, build again.

usage (from the decomp root):  python tools/mapgen/settle.py [map keys ...]   (default: every outdoor map)
Uses build_all's build.py runs, compose.py on each asked tileset's recipe (+ --register), at most 4 rounds.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

PY = [sys.executable, "-W", "ignore"]


def build(key):
    r = subprocess.run(PY + [os.path.join(HERE, "build.py"), os.path.join(HERE, "maps", key + ".json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=world.ROOT)
    t = (r.stdout + r.stderr)
    return r.returncode == 0, "transition tiles needed" in t, t


def main(keys):
    keys = keys or list(world.OUTDOOR)
    for rnd in range(4):
        ask = set()
        pb = os.path.join(HERE, "tilesets", "orleans_general.blends.json")
        before = os.path.getsize(pb) if os.path.exists(pb) else 0
        for k in keys:
            ok, asked, t = build(k)
            if not ok:
                print(f"{k}: FAILED\n" + "\n".join(t.strip().splitlines()[-6:]))
                continue
            if asked:
                spec = json.load(open(os.path.join(HERE, "maps", k + ".json"), encoding="utf-8"))
                ask.add(spec["tileset"])
        if (os.path.getsize(pb) if os.path.exists(pb) else 0) != before:   # the primary was asked for a piece (shared bridge, border cells)
            ask.add("orleans_general")
        if not ask:
            print(f"settled after {rnd + 1} round(s)")
            return
        print(f"round {rnd + 1}: composing {', '.join(sorted(ask))}")
        subprocess.run(PY + [os.path.join(HERE, "compose.py")] + [os.path.join(HERE, "tilesets", "recipes", a + ".json") for a in sorted(ask)]
                       + ["--register"], capture_output=True, cwd=world.ROOT)
        # every map on a recomposed tileset must be rebuilt (its ids may have moved)
        on = set()
        for k in world.OUTDOOR:
            spec = json.load(open(os.path.join(HERE, "maps", k + ".json"), encoding="utf-8"))
            if spec["tileset"] in ask or "orleans_general" in ask:
                on.add(k)
        keys = sorted(set(keys) | on)
    print("not settled")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
