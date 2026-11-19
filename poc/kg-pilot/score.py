# /// script
# requires-python = ">=3.11"
# ///
"""Score both extractors against the answer key, using the blind judgement.

Run: uv run --script score.py <path-to-session.jsonl> [spans.jsonl]
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from extraction_common import EXTRACTIONS, load_extraction, load_spans, quote_check


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: score.py <path-to-session.jsonl> [spans.jsonl]")
    uuids = set()
    for line in Path(sys.argv[1]).open(encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and "uuid" in record:
            uuids.add(record["uuid"])
    spans = load_spans(Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out/spans-2026-11-15.jsonl"))
    key = json.loads(Path("answer-key.json").read_text(encoding="utf-8"))["decisions"]
    mapping = json.loads(Path("out/pool-map.json").read_text(encoding="utf-8"))
    judgement = json.loads(Path("out/judgement.json").read_text(encoding="utf-8"))
    matched_by = defaultdict(set)  # (extractor, index) -> key numbers
    found = defaultdict(set)  # extractor -> key numbers
    for m in judgement["matches"]:
        for pid in m["pool_ids"]:
            who = mapping[pid]
            matched_by[(who["extractor"], who["index"])].add(m["number"])
            found[who["extractor"]].add(m["number"])
    report = {}
    for name in EXTRACTIONS:
        extraction = load_extraction(name)
        ds = extraction["decisions"]
        checks = Counter(quote_check(d, spans) for d in ds)
        resolves = sum(1 for d in ds if (s := spans.get(str(d.get("span_id", "")).strip()))
                       and s["external_id"].split(":", 1)[0] in uuids)
        matching = sum(1 for i in range(1, len(ds) + 1) if matched_by.get((name, i)))
        report[name] = {
            "extractor": extraction["extractor"],
            "decisions": len(ds),
            "key_found": f"{len(found[name])} of {len(key)}",
            "key_missed": sorted(set(range(1, len(key) + 1)) - found[name]),
            "precision": f"{matching} of {len(ds)} match a key decision",
            "quotes_exact": f"{checks['exact']} of {len(ds)}",
            "quotes_whitespace_only": checks["whitespace"],
            "quotes_missing": checks["missing"],
            "anchors_resolve": f"{resolves} of {len(ds)}",
            "seconds": extraction.get("seconds"),
        }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    Path("out/score.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
