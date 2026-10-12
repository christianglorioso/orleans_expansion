"""One build at a time: anything that writes data/ (a town generator, build.py, compose, rebuild_world) holds this
lock while it runs, so two agents never write data/layouts/layouts.json or a tileset at once.

usage (from the decomp root):
  python tools/mapgen/buildlock.py acquire <who>   waits until the lock is free, then takes it (prints "acquired")
  python tools/mapgen/buildlock.py release <who>   gives it back (only if <who> holds it)
  python tools/mapgen/buildlock.py status          who holds it, and since when
A lock older than 45 minutes counts as abandoned and is taken over.
"""
import json
import os
import sys
import time

LOCK = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".build.lock")
STALE = 45 * 60


def held():
    try:
        return json.load(open(LOCK))
    except (OSError, ValueError):
        return None


def acquire(who):
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, json.dumps({"who": who, "since": time.time()}).encode())
            os.close(fd)
            print("acquired")
            return
        except FileExistsError:
            h = held()
            if h and time.time() - h.get("since", 0) > STALE:
                print(f"taking over a stale lock from {h.get('who')}")
                os.remove(LOCK)
                continue
            time.sleep(5)


def release(who):
    h = held()
    if h and h.get("who") == who:
        os.remove(LOCK)
        print("released")
    else:
        print(f"not held by {who} ({h})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "acquire":
        acquire(sys.argv[2])
    elif cmd == "release":
        release(sys.argv[2])
    else:
        h = held()
        print("free" if not h else f"held by {h['who']} for {int(time.time() - h['since'])} s")
