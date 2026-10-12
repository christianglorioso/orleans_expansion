"""build.py on every Orleans outdoor spec as it stands (no generator is re-run): refreshes every map.bin after a tileset
recompose. Prints one line per map and any 'tiles needed' messages.   usage: python tools/mapgen/build_all.py [keys...]"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

keys = [a for a in sys.argv[1:] if not a.startswith("--")] or list(world.OUTDOOR)
asked = []
for k in keys:
    r = subprocess.run([sys.executable, "-W", "ignore", os.path.join(HERE, "build.py"), os.path.join(HERE, "maps", k + ".json")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=world.ROOT)
    t = (r.stdout + r.stderr).strip().splitlines()
    msg = [l for l in t if "needed" in l or "Error" in l or "Traceback" in l or "pruned" in l or "unknown" in l]
    print(f"{k:16s} {'ok' if r.returncode == 0 else 'FAILED'} {t[-1][:100] if t else ''}")
    for l in msg:
        print("      ", l[:200])
    if any("needed" in l for l in msg):
        asked.append(k)
print("maps that asked for more tiles:", asked or "none")
