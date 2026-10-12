"""Fail if any map / story script uses an OBJ_EVENT_GFX_* id whose gObjectEventGraphicsInfoPointers entry is NULL.

Why: in this Emerald-mode build (IS_FRLG is 0) the FRLG-only block of src/data/object_events/object_event_graphics_info_pointers.h is
compiled out, so those ids point at NULL. An object event using one gets a garbage sprite and the game resets a few frames after the
map (re)loads (the Route 3 post-battle crash: OBJ_EVENT_GFX_COOLTRAINER_M). Run from the decomp root:  python tools/mapgen/gfx_null_check.py
"""
import glob
import re
import sys

ROOT = "."
hdr = open(f"{ROOT}/include/constants/event_objects.h", errors="ignore").read()
names = []
for line in hdr.splitlines():
    m = re.match(r"\s*(OBJ_EVENT_GFX_\w+)\s*,", line)
    if m:
        names.append(m.group(1))
set_names = set()
depth_off = 0   # >0 while inside an "#if IS_FRLG" block (compiled out here)
for line in open(f"{ROOT}/src/data/object_events/object_event_graphics_info_pointers.h", errors="ignore"):
    s = line.strip()
    if s.startswith("#if"):
        depth_off += 1 if (depth_off or s.startswith("#if IS_FRLG")) else 0
    elif s.startswith("#endif") and depth_off:
        depth_off -= 1
    elif not depth_off:
        m = re.search(r"\[(OBJ_EVENT_GFX_\w+)\]", line)
        if m:
            set_names.add(m.group(1))
null = {n for n in names if n not in set_names}
bad = {}
files = [f for f in glob.glob(f"{ROOT}/data/maps/*/map.json") if "_Frlg" not in f]
files += glob.glob(f"{ROOT}/data/maps/*/scripts.inc") + glob.glob(f"{ROOT}/tools/mapgen/**/*.py", recursive=True)
files += glob.glob(f"{ROOT}/tools/mapgen/**/*.inc", recursive=True)
for f in files:
    for g in set(re.findall(r"OBJ_EVENT_GFX_\w+", open(f, errors="ignore").read())):
        if g in null:
            bad.setdefault(g, []).append(f)
for g, fs in sorted(bad.items()):
    print("NULL graphics info:", g, "used in", ", ".join(fs[:5]))
print("gfx_null_check:", "FAIL" if bad else "ok", f"({len(null)} NULL ids, {len(files)} files)")
sys.exit(1 if bad else 0)
