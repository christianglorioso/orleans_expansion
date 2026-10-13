"""python tools/mapgen/feather_all.py [keys...]: in-memory feather summary for every outdoor map (nothing is written)"""
import concurrent.futures as cf
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import borders  # noqa: E402

keys = [a for a in sys.argv[1:] if not a.startswith("--")] or list(borders.STYLE)


def run(k):
    r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "feather_dbg.py"), k, "--brief"], capture_output=True, text=True)
    return r.stdout.strip() or f"{k} ERROR {r.stderr.strip().splitlines()[-1:]}"


with cf.ThreadPoolExecutor(4) as ex:
    for out in ex.map(run, keys):
        print(out)
