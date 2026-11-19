# /// script
# requires-python = ">=3.11"
# ///
"""Pool both extractions under neutral ids, in a fixed random order, for the blind judge.

Writes out/pool.json (what the judge reads) and out/pool-map.json (which extractor wrote which id).

Run: uv run --script make_pool.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from extraction_common import EXTRACTIONS, load_extraction


def main() -> None:
    items = [(name, i, d["statement"]) for name in EXTRACTIONS
             for i, d in enumerate(load_extraction(name)["decisions"], 1)]
    random.Random(20261119).shuffle(items)
    pool = [{"pool_id": f"P{n:03d}", "statement": s} for n, (_, _, s) in enumerate(items, 1)]
    mapping = {f"P{n:03d}": {"extractor": name, "index": i} for n, (name, i, _) in enumerate(items, 1)}
    Path("out/pool.json").write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path("out/pool-map.json").write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
    print(f"out/pool.json: {len(pool)} statements")


if __name__ == "__main__":
    main()
