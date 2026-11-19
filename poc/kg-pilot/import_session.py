# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30", "fastembed>=0.4"]
# ///
"""Import one Claude Code session as spans anchored to its messages.

Write and Edit calls to markdown files also become sources, one per file version,
anchored to the message that wrote them.

Run: uv run --script import_session.py <path-to-session.jsonl>

Claude Code keeps session files under ~/.claude/projects/<project>/<session-id>.jsonl.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from importlib.metadata import version
from pathlib import Path

import asyncpg
from fastembed import TextEmbedding

DSN_APP = "postgresql://kg_app:app@127.0.0.1:55432/kg"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_VERSION = f"fastembed-{version('fastembed')}"
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
GERMAN_WORDS = re.compile(r"\b(und|nicht|der|die|das|ist|ich|wir|mit|auf|für|eine?)\b", re.I)
MAX_CHUNK = 900


def text_blocks(record: dict) -> list[str]:
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return []


def chunks(text: str) -> list[str]:
    out, current = [], ""
    for para in re.split(r"\n\s*\n", text):
        if current and len(current) + len(para) > MAX_CHUNK:
            out.append(current)
            current = ""
        current = f"{current}\n\n{para}" if current else para
    if current:
        out.append(current)
    return [c.strip() for c in out if c.strip()]


def file_writes(record: dict) -> list[dict]:
    content = (record.get("message") or {}).get("content")
    if not isinstance(content, list):
        return []
    out = []
    for b in content:
        if not (isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Write", "Edit")):
            continue
        args = b.get("input") or {}
        path = str(args.get("file_path", ""))
        text = args.get("content") if b["name"] == "Write" else args.get("new_string")
        if path.endswith(".md") and isinstance(text, str) and text.strip():
            out.append({"tool": b["name"], "call": b.get("id"), "path": relative(path), "text": text})
    return out


def relative(path: str) -> str:
    marker = "/agent_factory/"
    if marker in path:
        return path.split(marker, 1)[1]
    return Path(path).name


def language(text: str) -> str:
    return "german" if len(GERMAN_WORDS.findall(text)) >= 3 else "english"


def read_session(path: Path):
    records, seen, parents, repeats, read = [], set(), {}, 0, 0
    for line in path.open(encoding="utf-8"):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict) or "uuid" not in record:
            continue
        read += 1
        uid = record["uuid"]
        if uid in seen:
            repeats += 1
            continue
        seen.add(uid)
        parents[uid] = record.get("parentUuid")
        if record.get("isSidechain") or record.get("type") not in ("user", "assistant"):
            continue
        records.append(record)
    return records, parents, seen, read, repeats


async def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: import_session.py <path-to-session.jsonl>")
    path = Path(sys.argv[1])
    started = time.time()
    records, parents, all_uuids, read, repeats = read_session(path)
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")
    session_id = path.stem
    before = await con.fetchval("select count(*) from node") + await con.fetchval("select count(*) from edge") \
        + await con.fetchval("select count(*) from embedding")
    span_of_message: dict[str, int] = {}
    async with con.transaction():
        await con.execute(
            "insert into node (kind, body, external_id, anchor) values ('source', $1, $2, $3::jsonb) "
            "on conflict (external_id) do nothing",
            f"Claude Code session {session_id}", f"session:{session_id}",
            json.dumps({"session": session_id, "file": path.name}))
        source = await con.fetchval("select id from node where external_id = $1", f"session:{session_id}")
        for record in records:
            uid = record["uuid"]
            for b, block in enumerate(text_blocks(record)):
                clean = REMINDER.sub("", block).strip()
                if len(clean) < 20:
                    continue
                for c, piece in enumerate(chunks(clean)):
                    external = f"{uid}:{b}:{c}"
                    anchor = {"session": session_id, "message_uuid": uid, "block": b, "chunk": c,
                              "timestamp": record.get("timestamp"), "role": record.get("type")}
                    nid = await con.fetchval(
                        "insert into node (kind, body, lang, external_id, anchor) values ('span', $1, $2, $3, $4::jsonb) "
                        "on conflict (external_id) do nothing returning id",
                        piece, language(piece), external, json.dumps(anchor))
                    if nid is None:
                        nid = await con.fetchval("select id from node where external_id = $1", external)
                    else:
                        await con.execute(
                            "insert into edge (source_id, target_id, type, status, asserted_by) "
                            "values ($1, $2, 'part_of', 'confirmed', 'import_session')", nid, source)
                    span_of_message.setdefault(uid, nid)
        # Written files: one source per Write or Edit call, linked to the writing message.
        writes = 0
        for record in records:
            uid = record["uuid"]
            for w in file_writes(record):
                external = f"write:{uid}:{w['call']}"
                anchor = {"session": session_id, "message_uuid": uid, "timestamp": record.get("timestamp"),
                          "tool": w["tool"], "tool_call": w["call"], "file": w["path"]}
                fid = await con.fetchval(
                    "insert into node (kind, body, external_id, anchor) values ('source', $1, $2, $3::jsonb) "
                    "on conflict (external_id) do nothing returning id",
                    f"{w['tool']} of {w['path']}", external, json.dumps(anchor))
                if fid is None:
                    continue
                writes += 1
                for c, piece in enumerate(chunks(w["text"])):
                    nid = await con.fetchval(
                        "insert into node (kind, body, lang, external_id, anchor) values ('span', $1, $2, $3, $4::jsonb) "
                        "returning id", piece, language(piece), f"{external}:{c}", json.dumps({**anchor, "chunk": c}))
                    await con.execute(
                        "insert into edge (source_id, target_id, type, status, asserted_by) "
                        "values ($1, $2, 'part_of', 'confirmed', 'import_session')", nid, fid)
                writer = uid
                while writer and writer not in span_of_message:
                    writer = parents.get(writer)
                if writer:
                    await con.execute(
                        "insert into edge (source_id, target_id, type, status, asserted_by) "
                        "values ($1, $2, 'written_in', 'confirmed', 'import_session')", fid, span_of_message[writer])
        # Reply edges: from a message's first span to the nearest imported ancestor's first span.
        existing = {(r["source_id"], r["target_id"]) for r in await con.fetch(
            "select source_id, target_id from edge where type = 'replies_to' and valid_to is null")}
        for uid, nid in span_of_message.items():
            parent = parents.get(uid)
            while parent and parent not in span_of_message:
                parent = parents.get(parent)
            if parent and (nid, span_of_message[parent]) not in existing:
                await con.execute(
                    "insert into edge (source_id, target_id, type, status, asserted_by) "
                    "values ($1, $2, 'replies_to', 'confirmed', 'import_session')", nid, span_of_message[parent])
    # Embeddings: skip nodes that have one; reuse the vector of identical text by content hash.
    missing = await con.fetch(
        "select n.id, n.body, n.content_hash from node n where n.kind = 'span' and not exists ("
        "select 1 from embedding e where e.node_id = n.id and e.model = $1 and e.model_version = $2)",
        MODEL_NAME, MODEL_VERSION)
    embed_started = time.time()
    reused = 0
    if missing:
        model = TextEmbedding(MODEL_NAME)
        by_hash: dict[bytes, str] = {}
        for r in await con.fetch(
                "select n.content_hash, e.vector::text from embedding e join node n on n.id = e.node_id "
                "where e.model = $1 and e.model_version = $2", MODEL_NAME, MODEL_VERSION):
            by_hash[r[0]] = r[1]
        to_embed = [r for r in missing if r["content_hash"] not in by_hash]
        reused = len(missing) - len(to_embed)
        vectors = list(model.embed([r["body"] for r in to_embed], batch_size=64))
        async with con.transaction():
            for r, v in zip(to_embed, vectors):
                text = "[" + ",".join(f"{x:.6f}" for x in v) + "]"
                by_hash[r["content_hash"]] = text
                await con.execute(
                    "insert into embedding (node_id, model, model_version, vector) values ($1, $2, $3, $4::vector)",
                    r["id"], MODEL_NAME, MODEL_VERSION, text)
            for r in missing:
                if r in to_embed:
                    continue
                await con.execute(
                    "insert into embedding (node_id, model, model_version, vector) values ($1, $2, $3, $4::vector) "
                    "on conflict do nothing", r["id"], MODEL_NAME, MODEL_VERSION, by_hash[r["content_hash"]])
    embed_seconds = time.time() - embed_started
    after = await con.fetchval("select count(*) from node") + await con.fetchval("select count(*) from edge") \
        + await con.fetchval("select count(*) from embedding")
    anchors = [r[0] for r in await con.fetch(
        "select distinct anchor ->> 'message_uuid' from node where kind = 'span' and anchor ->> 'session' = $1", session_id)]
    unknown = [a for a in anchors if a not in all_uuids]
    spans = await con.fetchval("select count(*) from node where kind = 'span' and anchor ->> 'session' = $1", session_id)
    await con.close()
    print(f"records read {read}, repeats dropped {repeats}, user and assistant messages kept {len(records)}")
    print(f"spans in store {spans}, rows added this run {after - before}, vectors computed {len(missing) - reused}, "
          f"reused by content hash {reused}, embedding took {embed_seconds:.1f}s, total {time.time() - started:.1f}s")
    print(f"span anchors {len(anchors)}, anchors not found in the session file {len(unknown)}")
    print(f"file versions added this run {writes}")
    print(f"model {MODEL_NAME}, version {MODEL_VERSION}")


if __name__ == "__main__":
    asyncio.run(main())
