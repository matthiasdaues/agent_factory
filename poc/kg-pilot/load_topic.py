# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""Story F: one topic with its old and new name, linked to the decisions about it.

Each name is a node with a names edge to the topic and a quotes edge to the earliest
span that uses it, so the quote gate checks it. The decisions about the topic are the
Claude-extracted decisions the blind judge matched to a key decision; their about
edges stay candidates.

Run: uv run --script load_topic.py
Set KG_DSN to load into another database. Safe to run twice.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import asyncpg

DSN_APP = os.environ.get("KG_DSN", "postgresql://kg_app:app@127.0.0.1:55432/kg")
TOPIC = {"key": "run-lifecycle", "body": "Run lifecycle"}
# (name as stored, text as the earliest span writes it)
NAMES = [("Dispatch process", "dispatch process"), ("Run Lifecycle", "Run Lifecycle")]
EXTRACTOR = "claude"


def judged_decisions() -> list[int]:
    mapping = json.loads(Path("out/pool-map.json").read_text(encoding="utf-8"))
    judgement = json.loads(Path("out/judgement.json").read_text(encoding="utf-8"))
    return sorted({mapping[pid]["index"] for m in judgement["matches"] for pid in m["pool_ids"]
                   if mapping[pid]["extractor"] == EXTRACTOR})


async def edge(con, source, target, type_, status, by, evidence=None) -> int:
    if await con.fetchval("select 1 from edge where source_id = $1 and target_id = $2 and type = $3 "
                          "and valid_to is null", source, target, type_):
        return 0
    await con.execute("insert into edge (source_id, target_id, type, status, asserted_by, evidence_span_id) "
                      "values ($1, $2, $3, $4, $5, $6)", source, target, type_, status, by, evidence)
    return 1


async def node(con, kind, body, external_id, anchor) -> int:
    await con.execute("insert into node (kind, body, external_id, anchor) values ($1, $2, $3, $4::jsonb) "
                      "on conflict (external_id) do nothing", kind, body, external_id, json.dumps(anchor))
    return await con.fetchval("select id from node where external_id = $1", external_id)


async def main() -> None:
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")
    added = 0
    async with con.transaction():
        before = await con.fetchval("select count(*) from node")
        topic = await node(con, "topic", TOPIC["body"], f"topic:{TOPIC['key']}", {})
        for n, (name, quote) in enumerate(NAMES, 1):
            span = await con.fetchrow(
                "select id, external_id, anchor ->> 'timestamp' as ts from node where kind = 'span' "
                "and strpos(body, $1) > 0 and anchor ? 'timestamp' order by anchor ->> 'timestamp', id limit 1", quote)
            if span is None:
                raise SystemExit(f"no span uses {quote!r}")
            anchor = {"quote": quote, "first_span": span["external_id"], "timestamp": span["ts"]}
            nid = await node(con, "name", name, f"name:{TOPIC['key']}:{n}", anchor)
            added += await edge(con, nid, topic, "names", "confirmed", "story-f")
            added += await edge(con, nid, span["id"], "quotes", "confirmed", "story-f", span["id"])
            print(f"name {name!r}: first used {span['ts']} in span {span['external_id']}")
        decisions = judged_decisions()
        for i in decisions:
            row = await con.fetchrow(
                "select n.id, q.target_id from node n join edge q on q.source_id = n.id and q.type = 'quotes' "
                "where n.external_id = $1", f"extract:{EXTRACTOR}:{i}")
            if row is None:
                raise SystemExit(f"decision extract:{EXTRACTOR}:{i} is not loaded")
            added += await edge(con, row["id"], topic, "about", "candidate", "judgement:out/judgement.json",
                                row["target_id"])
        added += await con.fetchval("select count(*) from node") - before
    await con.close()
    print(f"topic {TOPIC['body']!r}: {len(NAMES)} names, {len(decisions)} decisions; {added} rows added this run")


if __name__ == "__main__":
    asyncio.run(main())
