# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""Load both extractions as decision nodes with a candidate quotes edge to the cited span.

The database rejects a decision whose quote is not in its cited span; this script reports it.

Run: uv run --script load_extractions.py [spans.jsonl]
Set KG_DSN to load into another database.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from collections import Counter
from pathlib import Path

import asyncpg

from extraction_common import EXTRACTIONS, load_extraction, load_spans, quote_check

DSN_APP = os.environ.get("KG_DSN", "postgresql://kg_app:app@127.0.0.1:55432/kg")


async def main() -> None:
    spans = load_spans(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/spans-2026-11-15.jsonl"))
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")
    for name in EXTRACTIONS:
        extraction = load_extraction(name)
        added, rejected, checks = 0, [], Counter()
        async with con.transaction():
            for i, d in enumerate(extraction["decisions"], 1):
                check = quote_check(d, spans)
                checks[check] += 1
                if check == "unknown_span":
                    rejected.append(f"{i}: span {d.get('span_id')!r} is not in the spans file")
                    continue
                span = spans[d["span_id"].strip()]
                target = await con.fetchval("select id from node where external_id = $1", span["external_id"])
                anchor = {"extractor": extraction["extractor"], "span_id": span["span_id"],
                          "quote": d.get("quote", ""), "quote_check": check}
                try:
                    async with con.transaction():
                        nid = await con.fetchval(
                            "insert into node (kind, body, external_id, anchor) values ('decision', $1, $2, $3::jsonb) "
                            "on conflict (external_id) do nothing returning id",
                            d.get("statement", ""), f"extract:{name}:{i}", json.dumps(anchor))
                        if nid is None:
                            continue
                        await con.execute(
                            "insert into edge (source_id, target_id, type, status, asserted_by, evidence_span_id) "
                            "values ($1, $2, 'quotes', 'candidate', $3, $2)", nid, target, extraction["extractor"])
                except asyncpg.exceptions.CheckViolationError as e:
                    rejected.append(f"{i}: {e}")
                    continue
                added += 1
        print(f"{name}: {len(extraction['decisions'])} decisions, {added} added, {len(rejected)} rejected, "
              f"quote checks {dict(checks)}")
        for r in rejected:
            print(f"  rejected {r}")
    await con.close()


if __name__ == "__main__":
    asyncio.run(main())
