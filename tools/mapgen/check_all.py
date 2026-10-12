"""Run check.py on every Orleans outdoor map and print one line each (terrain seams, off-palette tiles, gameplay problems).

usage (from the decomp root): python tools/mapgen/check_all.py [out.txt]
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

out = []
for key in world.OUTDOOR:
    spec = os.path.join(HERE, "maps", key + ".json")
    r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "check.py"), spec],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=world.ROOT)
    t = r.stdout + r.stderr
    seams = re.search(r"terrain seams above 20: (\d+)", t)
    off = re.search(r"off-palette grass .*?: (\d+)", t)
    gp = re.search(r"gameplay problems: (\d+)", t)
    line = f"{key:16s} seams={seams.group(1) if seams else '?':>3} offpal={off.group(1) if off else '?':>3} gameplay={gp.group(1) if gp else '?':>3}"
    if r.returncode or not seams:
        line += "  FAILED: " + t.strip().splitlines()[-1][:150] if t.strip() else "  FAILED"
    print(line, flush=True)
    out.append(line)
    if gp and gp.group(1) != "0":
        for l in t.splitlines():
            if l.startswith("  ") and "problems" not in l and "seams" not in l:
                pass
if len(sys.argv) > 1:
    open(sys.argv[1], "w").write("\n".join(out) + "\n")
