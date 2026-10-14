"""Seams review helper (2026-10-14): python tools/mapgen/seam_edit.py <route_key> '<json list of [char, x, y, w, h]>'
Adds grid rectangles to world_edges.json (the data a firstpass regeneration keeps, wedge.apply_to_spec) and mirrors them into the committed
spec's "edits" (the spec build.py / repro_check read), so the two never disagree.  Idempotent."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wedge  # noqa: E402


def write_edges(d, key):
    """world_edges.json keeps the layout of the committed file: only this key's block is re-written (at its sorted position)"""
    raw = open(wedge.EDGES, encoding="utf-8", newline="").read()
    old = json.loads(raw)
    block = json.dumps(d[key], indent=1, sort_keys=True).replace("\n", "\n ")
    entry = ' "%s": %s' % (key, block)
    marker = '\n "%s": {'
    if key in old:
        keys = sorted(old)
        start = raw.index(marker % key) + 1
        nxt = keys[keys.index(key) + 1] if keys.index(key) + 1 < len(keys) else None
        end = raw.index(marker % nxt) + 1 if nxt else raw.rindex("\n}")
        raw = raw[:start] + entry + ("," if nxt else "") + "\n" + raw[end:]
    else:
        later = [k for k in sorted(old) if k > key]
        if later:
            at = raw.index(marker % later[0]) + 1
            raw = raw[:at] + entry + ",\n" + raw[at:]
        else:
            at = raw.rindex("\n}")
            raw = raw[:at] + ",\n" + entry + raw[at:]
    json.loads(raw)
    with open(wedge.EDGES, "w", encoding="utf-8", newline="") as f:
        f.write(raw)


def add(key, edits):
    d = wedge.load()
    e = d.setdefault(key, {})
    e.setdefault("edits", [])
    for r in edits:
        if list(r) not in e["edits"]:
            e["edits"].append(list(r))
    e.setdefault("drop", [])
    e.setdefault("dropped", [])
    write_edges(d, key)
    sp = os.path.join(HERE, "maps", key + ".json")
    spec = json.load(open(sp, encoding="utf-8"))
    spec = wedge.apply_to_spec(spec, key)
    with open(sp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    add(sys.argv[1], json.loads(sys.argv[2]))
