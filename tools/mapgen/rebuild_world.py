"""Rebuild every generated outdoor map and relink the interiors, in the right order.

usage (from the decomp root): python tools/mapgen/rebuild_world.py [map keys...] [--clean-blends]
  0. --clean-blends: empty the town/route tilesets' blends files first, so they hold only what today's maps
     ask for (old layouts leave stale transition and overlay tiles that waste the tile budget)
  1. firstpass.py --blends   (each map requests the transition and overlay tiles it needs), and the
     vertical-slice maps on the route tileset request theirs too
  2. compose the town and route tilesets those maps use (--register)
  3. firstpass.py            (build with the tiles now present)
  4. rebuild the vertical-slice maps that share the route tileset (Route 1)
  5. build_interior.py       (link every door to its room, rebuild first-pass exteriors)
Crescent City and Pointe Rouge have their own generators (crescent.py, pointe.py); run those separately.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = [sys.executable, "-W", "ignore"]
TILESETS = ["orleans_harbor", "orleans_camp", "orleans_hollow", "orleans_port", "orleans_capital", "orleans_route",
            "orleans_river", "orleans_route_b", "orleans_route_dry", "orleans_route_farm", "orleans_gulf", "orleans_offshore", "orleans_coast"]
SLICE_ON_ROUTE = ["route_1"]


def run(args, show=("problems: ", "Error", "Traceback", "needed", "skipped (")):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in (r.stdout + r.stderr).splitlines():
        if any(s in line for s in show) and "problems: 0" not in line:
            print("   ", line)
    if r.returncode:
        raise SystemExit(f"failed: {' '.join(args[-3:])}")


def main(args):
    keys = [a for a in args if not a.startswith("--")]
    if "--clean-blends" in args:
        for t in TILESETS:
            bf = os.path.join(HERE, "tilesets", f"{t}.blends.json")
            if os.path.exists(bf):
                with open(bf + ".new", "w") as f:
                    json.dump([], f)
                os.replace(bf + ".new", bf)
        # compose straight away, so the mappings forget the old tiles and step 1 asks for everything it needs
        run(PY + [os.path.join(HERE, "compose.py")] + [os.path.join(HERE, "tilesets", "recipes", t + ".json")
                                                         for t in TILESETS], show=("needed", "Error", "Traceback"))
        print("0. blends files emptied and tilesets recomposed without them")
    fp = PY + [os.path.join(HERE, "firstpass.py")] + keys
    print("1. requesting transition tiles")
    run(fp + ["--blends"])
    for k in SLICE_ON_ROUTE:
        run(PY + [os.path.join(HERE, "build.py"), os.path.join(HERE, "maps", k + ".json"), "--dry-run"])
    print("2. composing", ", ".join(TILESETS))
    run(PY + [os.path.join(HERE, "compose.py")] + [os.path.join(HERE, "tilesets", "recipes", t + ".json") for t in TILESETS]
        + ["--register"], show=("needed", "Error", "Traceback"))
    print("3. building")
    run(fp)
    # a map can still ask for a tile (e.g. a crossing laid in the second dock pass): compose once more if so
    import glob
    specs = [p for p in glob.glob(os.path.join(HERE, "maps", "*.json"))
             if json.load(open(p, encoding="utf-8")).get("_comment", "").startswith("FIRST PASS")]
    asked = False
    for p in specs:
        r = subprocess.run(PY + [os.path.join(HERE, "build.py"), p, "--dry-run"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        asked |= "transition tiles needed" in r.stdout
    if asked:
        print("3b. composing again for late requests, then building")
        run(PY + [os.path.join(HERE, "compose.py")] + [os.path.join(HERE, "tilesets", "recipes", t + ".json")
                                                         for t in TILESETS] + ["--register"],
            show=("needed", "Error", "Traceback"))
        run(fp)
    print("4. the vertical slice's route maps")
    for k in SLICE_ON_ROUTE:
        run(PY + [os.path.join(HERE, "build.py"), os.path.join(HERE, "maps", k + ".json")])
    print("5. linking interiors")
    run(PY + [os.path.join(HERE, "build_interior.py")], show=("Error", "Traceback"))
    print("done")


if __name__ == "__main__":
    main(sys.argv[1:])
