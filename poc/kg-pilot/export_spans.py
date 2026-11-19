# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""Export the chat spans of one day for extraction. Written files are left out.

Each span gets a short id (S001, S002, ...) in time order; the file maps it to the span's external id.

Run: uv run --script export_spans.py [YYYY-MM-DD]   (default 2026-11-15)
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import asyncpg

DSN_APP = "postgresql://kg_app:app@127.0.0.1:55432/kg"


async def main() -> None:
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-11-15"
    con = await asyncpg.connect(DSN_APP)
    rows = await con.fetch(
        "select external_id, anchor ->> 'timestamp' as ts, anchor ->> 'role' as role, body from kg.node "
        "where kind = 'span' and not anchor ? 'file' and anchor ->> 'timestamp' like $1 "
        "order by anchor ->> 'timestamp', (anchor ->> 'block')::int, (anchor ->> 'chunk')::int", f"{day}%")
    await con.close()
    out = Path("out") / f"spans-{day}.jsonl"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i, r in enumerate(rows, 1):
            f.write(json.dumps({"span_id": f"S{i:03d}", "external_id": r["external_id"], "timestamp": r["ts"],
                                "role": r["role"], "text": r["body"]}, ensure_ascii=False) + "\n")
    print(f"{out}: {len(rows)} spans, {sum(len(r['body']) for r in rows)} characters")


if __name__ == "__main__":
    asyncio.run(main())
