# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""Story E: the quote gate, tested on a throwaway database beside the pilot store.

Creates kg_gate, loads schema.sql, writes the exported spans as span nodes, runs
load_extractions.py twice, and drops kg_gate again. Each item prints PASS or FAIL.

Run: uv run --script test_quote_gate.py
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import asyncpg

from extraction_common import EXTRACTIONS, load_extraction, load_spans, quote_check

OWNER = "postgresql://owner:owner@127.0.0.1:55432/{db}"
APP = "postgresql://kg_app:app@127.0.0.1:55432/kg_gate"
SPANS = Path("out/spans-2026-11-15.jsonl")
failures = 0


def report(item: str, ok: bool, observed: str) -> None:
    global failures
    failures += not ok
    print(f"{item}: {'PASS' if ok else 'FAIL'} - {observed}", flush=True)


def load() -> str:
    run = subprocess.run([sys.executable, "load_extractions.py"], capture_output=True, text=True,
                         env={**os.environ, "KG_DSN": APP}, check=True)
    return run.stdout


async def main() -> None:
    admin = await asyncpg.connect(OWNER.format(db="kg"))
    await admin.execute("drop database if exists kg_gate")
    await admin.execute("create database kg_gate")
    try:
        owner = await asyncpg.connect(OWNER.format(db="kg_gate"))
        await owner.execute(Path("schema.sql").read_text(encoding="utf-8"))
        spans = load_spans(SPANS)
        await owner.executemany("insert into kg.node (kind, body, external_id) values ('span', $1, $2)",
                                [(s["text"], s["external_id"]) for s in spans.values()])

        expected = {name: sum(quote_check(d, spans) in ("exact", "whitespace")
                              for d in load_extraction(name)["decisions"]) for name in EXTRACTIONS}
        first = load()
        print(first, end="")
        loaded = dict(await owner.fetch(
            "select split_part(n.external_id, ':', 2), count(*) from kg.node n "
            "join kg.edge e on e.source_id = n.id and e.type = 'quotes' "
            "where n.kind = 'decision' group by 1"))
        for name in EXTRACTIONS:
            total = len(load_extraction(name)["decisions"])
            report(f"{name} load", loaded.get(name, 0) == expected[name],
                   f"{loaded.get(name, 0)} of {total} loaded, {expected[name]} expected")

        orphans = await owner.fetchval(
            "select count(*) from kg.node n where n.kind = 'decision' and not exists "
            "(select 1 from kg.edge e where e.source_id = n.id and e.type = 'quotes')")
        report("no decision without its edge", orphans == 0, f"{orphans} decisions without a quotes edge")

        bad = await owner.fetchval(
            "select count(*) from kg.edge e join kg.node s on s.id = e.source_id join kg.node t on t.id = e.target_id "
            "where e.type = 'quotes' and kg.quote_found(s.anchor ->> 'quote', t.body) = 'missing'")
        report("every loaded quote is in its span", bad == 0, f"{bad} edges with a missing quote")

        app = await asyncpg.connect(APP)
        src = await app.fetchval("select id from kg.node where kind = 'span' limit 1")
        nid = await app.fetchval("insert into kg.node (kind, body, anchor) values ('decision', 'probe', $1::jsonb) "
                                 "returning id", json.dumps({"quote": "a sentence nobody wrote"}))
        try:
            await app.execute("insert into kg.edge (source_id, target_id, type, status, asserted_by) "
                              "values ($1, $2, 'quotes', 'candidate', 'probe')", nid, src)
            report("direct insert is refused", False, "the edge was written")
        except asyncpg.exceptions.CheckViolationError as e:
            report("direct insert is refused", True, str(e))
        await app.close()

        before = await owner.fetchval("select count(*) from kg.edge")
        second = load()
        after = await owner.fetchval("select count(*) from kg.edge")
        report("second run adds nothing", after == before and second.count(" 0 added") == len(EXTRACTIONS), f"{after - before} edges added")
        await owner.close()
    finally:
        await admin.execute("drop database if exists kg_gate with (force)")
        await admin.close()
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    asyncio.run(main())
