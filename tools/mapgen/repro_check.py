"""Reproducibility check: every outdoor map's generator output must equal the committed terrain.

usage (from the decomp root):  python tools/mapgen/repro_check.py [map_spec.json ...]
For each spec in tools/mapgen/maps (all Orleans outdoor maps) it runs build.py's Builder in memory (nothing is written) and compares the
metatile words with the committed data/layouts/<Map>/map.bin. A difference means a later run of the generator (build_all, rebuild_world,
a rebuild by someone who does not know) would silently change the terrain: usually an event the story overlay added (an item, an object, a
trigger) now steers borders.py / band_rules.py. Fix the event (move it, or mark a trigger line "gate": True), regenerate, commit the bin.
Exit code 1 if any map drifts.
"""
import glob
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def specs():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "maps", "*.json"))):
        b = os.path.basename(f)
        if f.endswith((".detected.json", ".base.json")) or b.startswith("_") or "_proposal" in b or "_fortree" in b or "_swampy" in b:
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        if isinstance(d, dict) and "map" in d and "objects" in d and "layout_dir" in d:
            out.append(f)
    return out


def one(f):
    """build one spec in this process (a fresh interpreter per map: the builder's tileset caches are shared state, so maps built one after
    another in a process pick up each other's pending overlay tiles); returns (drift description or None)"""
    import warnings
    warnings.filterwarnings("ignore")
    import build
    try:
        b = build.Builder(f)
        b.draw()
        flat = b.flat()
    except Exception as e:  # a generator that cannot run is also a finding
        return "ERROR", f"{os.path.basename(f)}: {e}"
    path = os.path.join(os.getcwd(), b.spec["layout_dir"].replace("/", os.sep), "map.bin")
    raw = open(path, "rb").read()
    have = struct.unpack(f"<{len(raw) // 2}H", raw)
    if len(have) != len(flat):
        return "DRIFT", f"{b.spec['map']}: size {len(have)} words committed, {len(flat)} generated"
    diff = [(i % b.w, i // b.w, have[i], flat[i]) for i in range(len(flat)) if have[i] != flat[i]]
    if diff:
        return "DRIFT", f"{b.spec['map']}: {len(diff)} cells differ, first {[(x, y, hex(a), hex(c)) for x, y, a, c in diff[:4]]}"
    return "ok", b.spec["map"]


def main(argv):
    import subprocess
    if argv and argv[0] == "--one":
        kind, msg = one(argv[1])
        print(f"{kind}|{msg}")
        return 0
    bad = 0
    files = argv or specs()
    for f in files:
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.abspath(__file__), "--one", f], capture_output=True, text=True)
        line = [l for l in r.stdout.splitlines() if "|" in l and l.split("|")[0] in ("ok", "DRIFT", "ERROR")]
        kind, msg = line[-1].split("|", 1) if line else ("ERROR", f"{os.path.basename(f)}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no output'}")
        print(f"{kind:6s} {msg}")
        bad += kind != "ok"
    print(f"{len(files)} maps, {bad} drifting")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
