"""Compare rater pairs with each other and with the filed rating.

Usage: python3 -I compare.py <run-dir> <rater,rater> [<rater,rater> ...]

Example: python3 -I compare.py run-1 A1,A2 B1,B2 C1,C2
         python3 -I compare.py run-2 K1,K2 T1,T2

Reads <run-dir>/out/<RATER>.jsonl and key/answer-key.tsv next to this script.
"""

import csv
import json
import sys
from pathlib import Path

SPIKE = Path(__file__).resolve().parent
FIELDS = ("severity", "blocking", "review_class", "category", "type", "basis")


def load(run, rater):
    p = run / "out" / f"{rater}.jsonl"
    if not p.exists():
        return {}
    return {d["id"]: d for d in (json.loads(l) for l in p.open() if l.strip())}


def blocks(cat, sev):
    return cat in ("defect", "risk") and sev in ("critical", "major")


def cell(d):
    return f"{d.get('review_class', '?')}/{d.get('category', '?')}/{d.get('severity', '?')}"


def main():
    run = Path(sys.argv[1])
    pairs = [tuple(p.split(",")) for p in sys.argv[2:]]
    key = {
        r[0]: r
        for r in csv.reader((SPIKE / "key/answer-key.tsv").open(), delimiter="\t")
    }
    for a, b in pairs:
        da, db = load(run, a), load(run, b)
        agree, n = dict.fromkeys(FIELDS, 0), 0
        print(f"\n== {a} / {b}")
        print(f"{'id':11} {'filed':16} {a:28} {b:28} same severity")
        for i in sorted(set(da) | set(db)):
            x, y, k = da.get(i, {}), db.get(i, {}), key[i]
            if x and y:
                n += 1
                for f in FIELDS:
                    agree[f] += x.get(f) == y.get(f)
            same = "yes" if x.get("severity") == y.get("severity") else "NO"
            print(f"{i:11} {k[2] + '/' + k[3]:16} {cell(x):28} {cell(y):28} {same}")
        print(f"pairs compared: {n}")
        for f, v in agree.items():
            print(f"  {f:12} agreement {v}/{n}")
        flips = sum(
            blocks(key[i][2], key[i][3]) != bool(d.get("blocking"))
            for d_ in (da, db)
            for i, d in d_.items()
        )
        print(
            f"  blocking differs from the filed rating in {flips}/{len(da) + len(db)} ratings"
        )
        for r, d_ in ((a, da), (b, db)):
            for i, d in d_.items():
                if d.get("rule_gap"):
                    print(f"  rule gap {r} {i}: {d['rule_gap']}")


if __name__ == "__main__":
    main()
