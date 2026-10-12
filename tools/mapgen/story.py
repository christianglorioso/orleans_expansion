"""Splice the hand-written story scripts (tools/mapgen/story/<Map>.inc) into data/maps/<Map>/scripts.inc.

Each story file holds everything above the builders' generated NPC block: the map scripts, story events,
and the scripts of NPCs marked "custom" in the specs. The generated block is kept as it is.

A story file may write a metatile id as @@mt:<piece>@@ (e.g. @@mt:ph:40E@@): it is replaced by the id the tileset mapping
gives that piece (tilesets/orleans_interior.mapping.json, then orleans_building.mapping.json), so a recomposed tileset
never leaves a stale number in a script.

usage (from the decomp root): python tools/mapgen/story.py
"""
import glob
import json
import os
import re
import sys

BEGIN = "@ --- mapgen: generated NPC scripts (begin) ---"
HERE = os.path.dirname(os.path.abspath(__file__))
STORY = os.path.join(HERE, "story")
MAPPINGS = ("orleans_interior", "orleans_building")


def metatile_ids():
    ids = {}
    for name in reversed(MAPPINGS):  # earlier names win
        path = os.path.join(HERE, "tilesets", name + ".mapping.json")
        if os.path.exists(path):
            ids.update(json.load(open(path, encoding="utf-8"))["metatiles"])
    return ids


def resolve(text, ids, where):
    def sub(m):
        if m.group(1) not in ids:
            sys.exit(f"{where}: @@mt:{m.group(1)}@@ is not in the tileset mappings")
        return str(ids[m.group(1)])
    return re.sub(r"@@mt:([^@]+)@@", sub, text)


def main():
    ids = metatile_ids()
    for path in sorted(glob.glob(os.path.join(STORY, "*.inc"))):
        name = os.path.splitext(os.path.basename(path))[0]
        target = f"data/maps/{name}/scripts.inc"
        current = open(target, encoding="utf-8").read()
        generated = current[current.index(BEGIN):] if BEGIN in current else ""
        story = resolve(open(path, encoding="utf-8").read().rstrip("\n"), ids, path)
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(story + "\n\n" + generated)
        print(target)


if __name__ == "__main__":
    main()
