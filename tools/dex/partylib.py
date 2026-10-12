"""Minimal reader for .party files (enough for validation)."""
import re


def parse(path):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    out = []
    for blk in re.split(r"^=== (TRAINER_\w+) ===\n", txt, flags=re.M)[1:]:
        pass
    parts = re.split(r"^=== (TRAINER_\w+) ===\n", txt, flags=re.M)
    for i in range(1, len(parts), 2):
        const, body = parts[i], parts[i + 1]
        head, _, rest = body.partition("\n\n")
        tr = dict(const=const, header=head, mons=[])
        for mb in re.split(r"\n\n+", rest.strip("\n")):
            lines = [l for l in mb.split("\n") if l.strip()]
            if not lines:
                continue
            first = lines[0]
            m = re.match(r"^(?:(.+?) \()?([^()@]+?)\)?(?: \((M|F)\))?(?: @ (.+))?$", first)
            mon = dict(header=first, moves=[], fields={})
            sp = first
            item = None
            if " @ " in sp:
                sp, item = sp.split(" @ ", 1)
            gender = None
            g = re.search(r" \((M|F)\)$", sp)
            if g:
                gender = g.group(1)
                sp = sp[:g.start()]
            nick = None
            n = re.match(r"^(.*) \(([^()]+)\)$", sp)
            if n:
                nick, sp = n.group(1), n.group(2)
            mon.update(species=sp.strip(), item=item, gender=gender, nick=nick)
            for l in lines[1:]:
                if l.startswith("- "):
                    mon["moves"].append(l[2:].strip())
                elif ":" in l:
                    k, v = l.split(":", 1)
                    mon["fields"][k.strip()] = v.strip()
            tr["mons"].append(mon)
        out.append(tr)
    return out
