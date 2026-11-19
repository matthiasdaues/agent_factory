# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30", "fastembed>=0.4"]
# ///
"""Ask the store a question: fused search, then one hop along live edges.

Run: uv run --script ask.py "What was decided about the run lifecycle?" [german|english]
"""

from __future__ import annotations

import asyncio
import json
import sys
from importlib.metadata import version

import asyncpg
from fastembed import TextEmbedding

DSN_APP = "postgresql://kg_app:app@127.0.0.1:55432/kg"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


async def main() -> None:
    question = sys.argv[1]
    config = sys.argv[2] if len(sys.argv) > 2 else "english"
    vector = next(iter(TextEmbedding(MODEL_NAME).embed([question])))
    text = "[" + ",".join(f"{x:.6f}" for x in vector) + "]"
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")
    rows = await con.fetch(
        "select w.seed_id, w.node_id, w.hops, w.score, n.kind, n.body, n.anchor "
        "from search_then_traverse($1, $2::vector, $3::regconfig, 10, 1, $4) w join node n on n.id = w.node_id "
        "order by w.score desc, w.seed_id, w.hops, w.node_id",
        question, text, config, MODEL_NAME)
    await con.close()
    print(f"question: {question} ({config}); model {MODEL_NAME}, fastembed-{version('fastembed')}")
    for r in rows:
        anchor = json.loads(r["anchor"])
        where = f"{anchor.get('timestamp', '')} {anchor.get('message_uuid', '')}" if r["kind"] == "span" else r["kind"]
        indent = "  " * r["hops"]
        body = " ".join(r["body"].split())[:140]
        print(f"{indent}{'hit' if r['hops'] == 0 else 'hop'} {r['score']:.4f} {where} | {body}")


if __name__ == "__main__":
    asyncio.run(main())
