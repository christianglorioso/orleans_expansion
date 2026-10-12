"""Hook a map's scripts.inc into data/event_scripts.s (the expansion includes every map's scripts there by hand)."""
import os


def include_map_scripts(root, name):
    """Add `.include "data/maps/<name>/scripts.inc"` to data/event_scripts.s unless it's already there."""
    path = os.path.join(root, "data", "event_scripts.s")
    line = f'\t.include "data/maps/{name}/scripts.inc"\n'
    src = open(path, encoding="utf-8").read()
    if line.strip() in src:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(src.rstrip("\n") + "\n" + line)
    return True
