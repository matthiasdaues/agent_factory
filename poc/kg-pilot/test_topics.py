# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""Story F: the topic route, tested against the pilot store after load_topic.py.

Each item prints PASS or FAIL.

Run: uv run --script test_topics.py <path-to-session.jsonl>
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import asyncpg

DSN_APP = "postgresql://kg_app:app@127.0.0.1:55432/kg"
TODAY = "What was decided about the run lifecycle?"
OLD = "What was decided about the dispatch process?"
OTHER = "What was decided about the release process?"
failures = 0


def report(item: str, ok: bool, observed: str) -> None:
    global failures
    failures += not ok
    print(f"{item}: {'PASS' if ok else 'FAIL'} - {observed}", flush=True)


def key_numbers_by_decision() -> dict[str, set[int]]:
    mapping = json.loads(Path("out/pool-map.json").read_text(encoding="utf-8"))
    judgement = json.loads(Path("out/judgement.json").read_text(encoding="utf-8"))
    found: dict[str, set[int]] = {}
    for m in judgement["matches"]:
        for pid in m["pool_ids"]:
            who = mapping[pid]
            found.setdefault(f"extract:{who['extractor']}:{who['index']}", set()).add(m["number"])
    return found


async def route(con, question: str) -> list[asyncpg.Record]:
    return await con.fetch(
        "select r.name, d.external_id, s.external_id as span from topic_route($1) r "
        "join node d on d.id = r.decision_id left join node s on s.id = r.span_id", question)


async def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: test_topics.py <path-to-session.jsonl>")
    uuids = set()
    for line in Path(sys.argv[1]).open(encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and "uuid" in record:
            uuids.add(record["uuid"])
    keys = key_numbers_by_decision()
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")

    today = await route(con, TODAY)
    covered = set().union(*(keys.get(r["external_id"], set()) for r in today)) if today else set()
    report("1. today's name finds the decisions", len(covered) == 20,
           f"{len(today)} decisions through {today[0]['name'] if today else 'no name'!r}, key decisions {len(covered)} of 20")

    old = await route(con, OLD)
    same = {r["external_id"] for r in old} == {r["external_id"] for r in today}
    report("2. the old name finds the same decisions", bool(old) and same,
           f"{len(old)} decisions through {old[0]['name'] if old else 'no name'!r}, same set: {same}")

    other = await route(con, OTHER)
    report("3. a question naming neither finds no topic", not other, f"{len(other)} decisions")

    resolves = sum(1 for r in today if r["span"] and r["span"].split(":", 1)[0] in uuids)
    report("4. every decision's span is a message of the session", resolves == len(today) > 0,
           f"{resolves} of {len(today)}")

    names = await con.fetch(
        "select n.body, count(q.id) as quotes, bool_and(quote_found(n.anchor ->> 'quote', s.body) <> 'missing') as ok "
        "from node n left join edge q on q.source_id = n.id and q.type = 'quotes' left join node s on s.id = q.target_id "
        "where n.kind = 'name' group by n.body order by n.body")
    report("5. each name quotes the span that first uses it", len(names) == 2 and all(r["quotes"] == 1 and r["ok"] for r in names),
           ", ".join(f"{r['body']!r}: {r['quotes']} quote" for r in names))
    await con.close()

    run = subprocess.run([sys.executable, "load_topic.py"], capture_output=True, text=True, check=True)
    report("6. a further load adds nothing", "; 0 rows added" in run.stdout, run.stdout.strip().splitlines()[-1])
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    asyncio.run(main())
