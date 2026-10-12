"""Run every smoke test in tools/playtest/tests against the current ROM and print a pass/fail table.

    python tools/playtest/run_all.py                 # all tests, current pokeemerald.gba
    python tools/playtest/run_all.py t00 t02        # only tests whose file name starts with these
    python tools/playtest/run_all.py --rom path.gba --run mytag

Each test is tests/<name>.py exposing run(bot, t). Outputs: tools/playtest/out/<run>/<test>/ (PNGs, contact sheet,
result.json) and out/<run>/results.json. Exit code 1 if anything failed.
"""
import argparse
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bot import Bot, ROM, OUT, GameCrash, contact_sheet, rom_sha1  # noqa: E402

TESTS = Path(__file__).resolve().parent / "tests"


class T:
    """collects checks for one test"""

    def __init__(self):
        self.checks, self.notes, self.bugs = [], [], []

    def check(self, name, cond, detail=""):
        self.checks.append({"name": name, "ok": bool(cond), "detail": str(detail)})
        return bool(cond)

    def note(self, text):
        self.notes.append(str(text))

    def bug(self, text):
        """a real game problem the bot saw (shows in the table even if the test carries on)"""
        self.bugs.append(str(text))


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_one(path, run, rom):
    name = path.stem
    t = T()
    out = OUT / run / name
    t0 = time.time()
    status, err, b = "PASS", None, None
    try:
        mod = load(path)
        b = Bot(out_dir=out, rom=rom)
        mod.run(b, t)
        if not all(c["ok"] for c in t.checks):
            status = "FAIL"
    except GameCrash as e:
        status, err = "CRASH", traceback.format_exc()
        t.bug("GAME CRASH: %s" % e)
    except Exception:
        status, err = "ERROR", traceback.format_exc()
        if b:
            try:
                b.shot("error_state")
            except Exception:
                pass
    shots = b.shots if b else []
    sheets = []
    if b:
        per = 48
        for i in range(0, len(shots), per):
            p = out / ("contact%s.png" % ("" if len(shots) <= per else "_%d" % (i // per + 1)))
            contact_sheet(shots[i:i + per], p, cols=6 if len(shots) <= 24 else 8)
            sheets.append(str(p))
        try:
            b.close()
        except Exception:
            pass
    res = {"test": name, "status": status, "seconds": round(time.time() - t0, 1), "checks": t.checks,
           "notes": t.notes, "bugs": t.bugs, "error": err, "shots": len(shots), "contact_sheets": sheets}
    (out / "result.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="*")
    ap.add_argument("--rom", default=str(ROM))
    ap.add_argument("--run", default=None)
    a = ap.parse_args()
    sha = rom_sha1(a.rom)[:8]
    run = a.run or time.strftime("%Y%m%d_%H%M%S") + "_" + sha
    files = sorted(p for p in TESTS.glob("t*.py") if not a.tests or any(p.stem.startswith(x) for x in a.tests))
    print("ROM %s (sha1 %s)  run %s" % (a.rom, sha, run))
    results = []
    for p in files:
        r = run_one(p, run, a.rom)
        results.append(r)
        ok = sum(c["ok"] for c in r["checks"])
        print("%-8s %-22s %2d/%-2d checks  %5.1fs  %s" % (r["status"], r["test"], ok, len(r["checks"]), r["seconds"],
                                                         ("; ".join(r["bugs"])[:90]) if r["bugs"] else ""))
        for c in r["checks"]:
            if not c["ok"]:
                print("           FAILED: %s  %s" % (c["name"], c["detail"]))
        if r["error"]:
            print("           " + r["error"].strip().splitlines()[-1])
    (OUT / run).mkdir(parents=True, exist_ok=True)
    (OUT / run / "results.json").write_text(json.dumps({"rom": a.rom, "sha1": sha, "results": results}, indent=1))
    bad = [r for r in results if r["status"] != "PASS"]
    print("\n%d/%d tests passed. Output: %s" % (len(results) - len(bad), len(results), OUT / run))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
