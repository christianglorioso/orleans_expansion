"""Source vs. generated drift lint (audit phase 3, S1): every generated script must be exactly what its source produces, so a regeneration
changes nothing and the in-game text is the text in the source.

usage (from the decomp root):  python tools/mapgen/gen_drift_check.py [--fast] [--no-interiors]
Exit code 1 if anything drifts. Nothing is written to the tree (the outdoor and interior generators run against a scratch copy).

  A. trainers   story_data_chN.TRAINERS -> the block between the `route trainers` markers in story/<Map>.inc, trainers/orleans_chN.party,
                PARTNERS -> src/data/battle_partners.party (gen_route_trainers.py, partners.py)
  B. splice     story/<Map>.inc (+ @@mt:..@@ resolved) is the head of data/maps/<Map>/scripts.inc (story.py)
  C. outdoors   the generated NPC / sign block of scripts.inc and map.json events of every outdoor spec (build.py with the story overlay)
  D. interiors  scripts.inc, map.json and map.bin of every interior room (build_interior.py)
--fast runs only A and B (story_lint.py calls that).

If it reports drift, the SOURCE is the thing to fix (story_data_*.py, story_overlay.py, the specs' generators, interior_rooms*.py), then rerun
the generator (gen_route_trainers.py <ch> / story.py / build.py <spec> / build_interior.py <room>); never edit data/maps/*/scripts.inc by hand.
"""
import difflib
import glob
import importlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
GEN_BEGIN = "@ --- mapgen: generated NPC scripts (begin) ---"


def diff(have, want, n=3, what=""):
    d = [l for l in difflib.unified_diff(have.splitlines(), want.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
    return [f"      {l[:150]}" for l in d[:n]] + ([f"      ... {len(d) - n} more lines"] if len(d) > n else [])


def rd(path):
    return open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")


# ------------------------------------------------------------------------------------------------------------ A. trainers
def check_trainers():
    import gen_route_trainers as g
    import partners
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "story_data_ch*.py"))):
        ch = os.path.basename(path)[len("story_data_"):-3]
        try:
            data = importlib.import_module("story_data_" + ch)
        except Exception as e:  # noqa: BLE001
            out.append(f"A {ch}: story_data_{ch}.py does not import: {e}")
            continue
        trainers = getattr(data, "TRAINERS", None)
        if trainers:
            maps = []
            for t in trainers:
                if t["m"] not in maps:
                    maps.append(t["m"])
            for m in maps:
                p = os.path.join(HERE, "story", m + ".inc")
                body = rd(p) if os.path.exists(p) else ""
                want = g.script_block(m, [t for t in trainers if t["m"] == m])
                a, b = body.find(g.BEGIN), body.find(g.END)
                have = body[a:b + len(g.END) + 1] if a >= 0 and b >= 0 else ""
                if have.strip() != want.strip():
                    out.append(f"A {ch}: story/{m}.inc trainer block differs from story_data_{ch}.TRAINERS (rerun gen_route_trainers.py {ch})")
                    out += diff(have.strip(), want.strip())
            pf = os.path.join(HERE, "trainers", f"orleans_{ch}.party")
            extra = getattr(data, "EXTRA_PARTIES", None) or getattr(data, "CAMP_PARTIES", [])
            want = "".join(g.party_block(t) for t in trainers) + "".join(g.party_block(t) for t in extra)
            if not os.path.exists(pf) or rd(pf) != want:
                out.append(f"A {ch}: trainers/orleans_{ch}.party differs from story_data_{ch} (rerun gen_route_trainers.py {ch})")
        if getattr(data, "PARTNERS", None):
            pp = os.path.join(ROOT, "src", "data", "battle_partners.party")
            text = rd(pp)
            if partners.rendered(data.PARTNERS, text) != text:
                out.append(f"A {ch}: src/data/battle_partners.party differs from story_data_{ch}.PARTNERS (rerun gen_route_trainers.py {ch})")
                out += diff(text, partners.rendered(data.PARTNERS, text))
    # the party sources (trainers/*.party, hand-written or generated) -> src/data/trainers.party + the opponents.h aliases (orleans_trainers.py)
    import orleans_trainers as ot
    secs = ot.read_sources()
    slots = ot.assigned_slots(secs)
    if slots is None:
        out.append("A trainers: orleans_trainers.py has no free Hoenn slot left")
    else:
        opp, party = ot.render(secs, slots)
        for what, path, want in (("opponents.h", ot.OPP, opp), ("trainers.party", ot.PARTY, party)):
            have = rd(os.path.join(ROOT, path))
            if have != want:
                out.append(f"A trainers: {path} differs from trainers/*.party (rerun orleans_trainers.py)")
                out += diff(have, want)
    return out


# ------------------------------------------------------------------------------------------------------------ B. splice
def check_splice():
    import story
    out = []
    ids = story.metatile_ids()
    for path in sorted(glob.glob(os.path.join(story.STORY, "*.inc"))):
        name = os.path.splitext(os.path.basename(path))[0]
        target = os.path.join(ROOT, "data", "maps", name, "scripts.inc")
        if not os.path.exists(target):
            out.append(f"B {name}: story/{name}.inc has no data/maps/{name}/scripts.inc")
            continue
        cur = rd(target)
        generated = cur[cur.index(story.BEGIN):] if story.BEGIN in cur else ""
        want = story.resolve(rd(path).rstrip("\n"), ids, path) + "\n\n" + generated
        if cur != want:
            out.append(f"B {name}: data/maps/{name}/scripts.inc differs from story/{name}.inc (run story.py)")
            out += diff(cur, want)
    return out


# ------------------------------------------------------------------------------------------------------------ C. outdoors
def outdoor_one(spec):
    """one fresh interpreter per spec (the builder's tileset caches are shared state); prints `ok|...` or `DRIFT|...` lines"""
    import shutil
    import tempfile
    import warnings
    warnings.filterwarnings("ignore")
    import build
    import story
    build.include_map_scripts = lambda *a, **k: None
    story.splice = lambda *a, **k: False
    b = build.Builder(spec)
    b.draw()
    name = b.spec["map"]
    tmp = tempfile.mkdtemp()
    d = os.path.join(tmp, "data", "maps", name)
    os.makedirs(d)
    for f in ("map.json", "scripts.inc"):
        shutil.copy(os.path.join(ROOT, "data", "maps", name, f), d)
    b.write_events(tmp)
    msgs = []
    for f in ("map.json", "scripts.inc"):
        have, want = rd(os.path.join(ROOT, "data", "maps", name, f)), rd(os.path.join(d, f))
        if have != want:
            msgs.append(f"C {name}: data/maps/{name}/{f} differs from what build.py generates from the spec + story overlay")
            msgs += diff(have, want)
    shutil.rmtree(tmp, ignore_errors=True)
    print("RESULT|" + ("DRIFT" if msgs else "ok") + "|" + "\n".join(msgs))


def check_outdoors():
    import repro_check
    out = []
    for f in repro_check.specs():
        r = subprocess.run([sys.executable, "-W", "ignore", os.path.abspath(__file__), "--outdoor-one", f], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=ROOT)
        line = [l for l in r.stdout.split("RESULT|")[-1:]] if "RESULT|" in r.stdout else None
        if not line:
            tail = (r.stderr.strip().splitlines() or ["no output"])[-1]
            out.append(f"C {os.path.basename(f)}: generator failed: {tail}")
            continue
        kind, _, msg = line[0].partition("|")
        if kind != "ok":
            out += msg.rstrip("\n").split("\n")
    return out


# ------------------------------------------------------------------------------------------------------------ D. interiors
def interiors_run():
    """build_interior.build() for every room with its file writes redirected into a scratch directory (reads of files it has
    rewritten are served from there), then compare the room's map.json, scripts.inc and map.bin with the tree"""
    import builtins
    import shutil
    import tempfile
    import warnings
    warnings.filterwarnings("ignore")
    os.chdir(ROOT)
    import build_interior as bi
    tmp = tempfile.mkdtemp()
    real_open = builtins.open

    def scratch(path):
        return os.path.join(tmp, os.path.relpath(os.path.abspath(path), ROOT))

    def fake_open(path, mode="r", *a, **k):
        if isinstance(path, (str, os.PathLike)) and os.path.abspath(path).startswith(ROOT):
            if any(c in mode for c in "wa+"):
                os.makedirs(os.path.dirname(scratch(path)), exist_ok=True)
                return real_open(scratch(path), mode, *a, **k)
            if os.path.exists(scratch(path)):
                return real_open(scratch(path), mode, *a, **k)
        return real_open(path, mode, *a, **k)

    bi.open = fake_open
    bi.os = type(os)("os")
    bi.os.__dict__.update(os.__dict__)
    real_makedirs = os.makedirs
    bi.os.makedirs = lambda p, *a, **k: real_makedirs(scratch(p) if os.path.abspath(p).startswith(ROOT) else p, exist_ok=True)
    bi.include_map_scripts = lambda *a, **k: None
    out = []
    for room in bi.ROOMS:
        name = room["map"]
        try:
            dw = bi.door_warp_index(room["exterior_spec"], room["exterior_cfg"], room["door_label"]) if room.get("door_label") else [None]
            grid, exits = bi.build(room, dw)
        except Exception as e:  # noqa: BLE001
            out.append(f"D {name}: build_interior failed: {type(e).__name__}: {e}")
            continue
        for rel in (f"data/maps/{name}/map.json", f"data/maps/{name}/scripts.inc"):
            real, mine = os.path.join(ROOT, rel), scratch(os.path.join(ROOT, rel))
            if not os.path.exists(mine):
                continue
            have, want = rd(real), rd(mine)
            if have != want:
                out.append(f"D {name}: {rel} differs from what build_interior.py generates (interior_rooms*.py / story_overlay.py)")
                out += diff(have, want)
        lid = room.get("layout") or None
        for rel in [os.path.relpath(p, tmp).replace("\\", "/") for p in glob.glob(os.path.join(tmp, "data", "layouts", "*", "map.bin"))]:
            real = os.path.join(ROOT, rel)
            if real_open(real, "rb").read() != real_open(os.path.join(tmp, rel), "rb").read():
                out.append(f"D {name}: {rel} differs from what build_interior.py generates")
            os.remove(os.path.join(tmp, rel))
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def main(argv):
    if argv and argv[0] == "--outdoor-one":
        outdoor_one(argv[1])
        return 0
    os.chdir(ROOT)
    problems = check_trainers() + check_splice()
    if "--fast" not in argv:
        problems += check_outdoors()
        if "--no-interiors" not in argv:
            problems += interiors_run()
    for p in problems:
        print(p)
    n = sum(1 for p in problems if re.match(r"^[A-D] ", p))
    print(f"gen_drift_check: {n} drifting sources" if n else "gen_drift_check: source and generated output agree")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
