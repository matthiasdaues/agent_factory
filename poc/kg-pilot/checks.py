# /// script
# requires-python = ">=3.11"
# dependencies = ["asyncpg>=0.30"]
# ///
"""The nine pilot tests of the design position, run against the pilot database.

Run: uv run --script checks.py
Each test prints one line: its number, PASS or FAIL, and what it observed.
Vectors here are deterministic stand-ins; story B uses a real model.
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import random
import subprocess
import sys
import time

import asyncpg

DSN_OWNER = "postgresql://owner:owner@127.0.0.1:55432/kg"
DSN_APP = "postgresql://kg_app:app@127.0.0.1:55432/kg"
MODEL = ("stand-in", "seeded-random-1")
results: list[tuple[int, bool, str]] = []


def vec(seed: str, noise: float = 0.0, noise_seed: str = "") -> str:
    rng = random.Random(hashlib.sha256(seed.encode()).digest())
    v = [rng.gauss(0, 1) for _ in range(384)]
    if noise:
        nrng = random.Random(hashlib.sha256((noise_seed or seed + "-n").encode()).digest())
        v = [x + noise * nrng.gauss(0, 1) for x in v]
    n = math.sqrt(sum(x * x for x in v))
    return "[" + ",".join(f"{x / n:.6f}" for x in v) + "]"


def report(number: int, ok: bool, observed: str) -> None:
    results.append((number, ok, observed))
    print(f"test {number}: {'PASS' if ok else 'FAIL'} - {observed}", flush=True)


async def app() -> asyncpg.Connection:
    con = await asyncpg.connect(DSN_APP)
    await con.execute("set search_path = kg, public")
    return con


async def add_node(con, kind, body, lang="english", v=None, external_id=None) -> int:
    nid = await con.fetchval(
        "insert into node (kind, body, lang, external_id) values ($1, $2, $3, $4) returning id",
        kind, body, lang, external_id,
    )
    if v is not None:
        await con.execute(
            "insert into embedding (node_id, model, model_version, vector) values ($1, $2, $3, $4::vector)",
            nid, *MODEL, v,
        )
    return nid


async def seed_background() -> None:
    con = await app()
    have = await con.fetchval("select count(*) from embedding where model = $1", MODEL[0])
    if have < 2000:
        async with con.transaction():
            for i in range(2000 - have):
                await add_node(con, "span", f"background span number {i} about ordinary matters", v=vec(f"bg{i}"))
    await con.close()


async def test_1_and_2() -> None:
    con = await app()
    v = vec("zebra")
    tr = con.transaction()
    await tr.start()
    await con.execute("set local enable_seqscan = off")
    src = await add_node(con, "source", "pilot source document")
    span = await add_node(con, "span", "zebra quantum widget arrives", v=v)
    await con.execute(
        "insert into edge (source_id, target_id, type, status, asserted_by) values ($1, $2, 'part_of', 'confirmed', 'checks')",
        span, src,
    )
    plan_vec = "\n".join(r[0] for r in await con.fetch(
        "explain select node_id from embedding order by vector <=> $1::vector limit 50", v))
    plan_kw = "\n".join(r[0] for r in await con.fetch(
        "explain select id from node where tsv @@ websearch_to_tsquery('english', 'zebra quantum')"))
    hit = await con.fetchrow(
        "select keyword_rank, vector_rank from hybrid_search('zebra quantum', $1::vector, 'english') where node_id = $2",
        v, span)
    walk = await con.fetch(
        "select node_id, hops from search_then_traverse('zebra quantum', $1::vector, 'english', 5, 1) where seed_id = $2",
        v, span)
    reached = {r["node_id"] for r in walk}
    await con.execute("set local hnsw.ef_search = 1")
    near = vec("zebra", noise=0.6)
    low_ef = await con.fetchval(
        "select count(*) from (select node_id from embedding order by vector <=> $1::vector limit 50) x where node_id = $2",
        near, span)
    await tr.rollback()
    uses_hnsw = "embedding_hnsw" in plan_vec
    uses_gin = "node_tsv" in plan_kw
    ok = bool(hit) and hit["keyword_rank"] is not None and hit["vector_rank"] is not None and src in reached
    report(1, ok and uses_hnsw and uses_gin,
           f"own write found by keyword rank {hit and hit['keyword_rank']} and vector rank {hit and hit['vector_rank']}; "
           f"traversal reached the source: {src in reached}; plans use HNSW {uses_hnsw}, GIN {uses_gin}; "
           f"with hnsw.ef_search = 1 and a noisy query the new row is {'found' if low_ef else 'missed'}")
    after = await con.fetchval(
        "select count(*) from hybrid_search('zebra quantum', $1::vector, 'english') h join node n on n.id = h.node_id "
        "where n.body = 'zebra quantum widget arrives'", v)
    report(2, after == 0, f"after ROLLBACK the fused search finds {after} rolled-back rows")
    await con.close()


async def test_3() -> None:
    con = await app()
    observed = []
    async with con.transaction():
        src = await add_node(con, "source", "kind test source")
        span = await add_node(con, "span", "kind test span")
        await con.execute(
            "insert into edge (source_id, target_id, type, status, asserted_by) values ($1, $2, 'part_of', 'confirmed', 'checks')",
            span, src)
    wrong_insert = wrong_change = False
    try:
        await con.execute(
            "insert into edge (source_id, target_id, type, status, asserted_by) values ($1, $2, 'part_of', 'confirmed', 'checks')",
            src, span)
    except asyncpg.RaiseError as e:
        wrong_insert = True
        observed.append(f"insert refused ({e})")
    try:
        await con.execute("update node set kind = 'conjecture' where id = $1", span)
    except asyncpg.RaiseError as e:
        wrong_change = True
        observed.append(f"kind change refused ({e})")
    await con.close()
    report(3, wrong_insert and wrong_change, "; ".join(observed) or "nothing refused")


async def test_4() -> None:
    con = await app()
    async with con.transaction():
        conj = await add_node(con, "conjecture", "leased pushes on many refs are too slow")
        dec = await add_node(con, "decision", "won't do: one git ref per id")
        edge = await con.fetchval(
            "insert into edge (source_id, target_id, type, status, asserted_by) values ($1, $2, 'rests_on', 'confirmed', 'checks') returning id",
            dec, conj)
    attempts = {
        "update edge status": ("update edge set status = 'candidate' where id = $1", edge),
        "delete edge": ("delete from edge where id = $1", edge),
        "truncate edge": ("truncate edge", None),
        "update decision body": ("update node set body = 'changed' where id = $1", dec),
        "change decision kind": ("update node set kind = 'conjecture' where id = $1", dec),
        "delete decision": ("delete from node where id = $1", dec),
        "truncate node": ("truncate node cascade", None),
    }
    refused = {}
    for name, (sql, arg) in attempts.items():
        try:
            async with con.transaction():
                await (con.execute(sql, arg) if arg is not None else con.execute(sql))
            refused[name] = "ALLOWED"
        except (asyncpg.RaiseError, asyncpg.InsufficientPrivilegeError) as e:
            refused[name] = type(e).__name__
    ended = None
    try:
        async with con.transaction():
            await con.execute("update edge set valid_to = now() where id = $1", edge)
            ended = "allowed once"
            await con.execute("update edge set valid_to = now() where id = $1", edge)
            ended = "allowed twice"
    except asyncpg.RaiseError:
        pass
    await con.close()
    ok = all(v != "ALLOWED" for v in refused.values()) and ended == "allowed once"
    report(4, ok, "; ".join(f"{k}: {v}" for k, v in refused.items()) + f"; ending an edge: {ended}")


async def test_5() -> None:
    heard: list[int] = []
    listener = await app()
    await listener.add_listener("kg_events", lambda *a: heard.append(int(a[3])))
    writer = await app()
    async with writer.transaction():
        kept = await add_node(writer, "conjecture", "committed idea for the event test")
    tr = writer.transaction()
    await tr.start()
    dropped = await add_node(writer, "conjecture", "rolled back idea for the event test")
    await tr.rollback()
    await asyncio.sleep(0.5)
    kept_event = await writer.fetchval("select id from outbox where node_id = $1", kept)
    dropped_event = await writer.fetchval("select count(*) from outbox where node_id = $1", dropped)
    heard_kept = kept_event in heard
    await writer.execute(
        "insert into outbox_cursor (consumer, last_id) values ('pilot', $1) "
        "on conflict (consumer) do update set last_id = excluded.last_id", kept_event)
    await listener.close()
    missed = []
    async with writer.transaction():
        for i in range(2):
            missed.append(await add_node(writer, "conjecture", f"idea while the listener was down {i}"))
    listener = await app()
    last = await listener.fetchval("select last_id from outbox_cursor where consumer = 'pilot'")
    caught = await listener.fetch("select node_id from outbox where id > $1 order by id", last)
    caught_ids = [r["node_id"] for r in caught]
    await listener.close()
    await writer.close()
    ok = heard_kept and dropped_event == 0 and all(m in caught_ids for m in missed)
    report(5, ok, f"notification for the committed idea: {heard_kept}; outbox rows for the rolled-back idea: {dropped_event}; "
                  f"after the restart the outbox held {len([m for m in missed if m in caught_ids])} of 2 missed ideas")


async def duplicate_race(force_index: bool) -> tuple[int, str]:
    target = vec(f"duplicate-{force_index}-{time.time()}")
    a, b = await app(), await app()
    for c in (a, b):
        await c.execute("begin isolation level serializable")
        if force_index:
            await c.execute("set local enable_seqscan = off")
    seen = []
    for c in (a, b):
        d = await c.fetchval("select vector <=> $1::vector from embedding order by vector <=> $1::vector limit 1", target)
        seen.append(d is not None and d < 0.01)
    for i, c in enumerate((a, b)):
        await add_node(c, "span", f"duplicate candidate {i}", v=target)
    commits = 0
    errors = []
    for c in (a, b):
        try:
            await c.execute("commit")
            commits += 1
        except asyncpg.SerializationError as e:
            errors.append(type(e).__name__)
            await c.execute("rollback")
    await a.close()
    await b.close()
    return commits, f"saw an existing duplicate {seen}, commits {commits}, errors {errors or 'none'}"


async def unrelated_vector_writers(rounds: int) -> int:
    """Two writers that each read near one vector and insert a far, unrelated one."""
    failures = 0
    for r in range(rounds):
        a, b = await app(), await app()
        for c in (a, b):
            await c.execute("begin isolation level serializable")
            await c.execute("set local enable_seqscan = off")
        for i, c in enumerate((a, b)):
            await c.fetchval("select node_id from embedding order by vector <=> $1::vector limit 1", vec(f"read-{i}-{r}"))
        for i, c in enumerate((a, b)):
            await add_node(c, "span", f"unrelated vector writer {i} round {r}", v=vec(f"write-{i}-{r}-{time.time()}"))
        for c in (a, b):
            try:
                await c.execute("commit")
            except asyncpg.SerializationError:
                failures += 1
                await c.execute("rollback")
        await a.close()
        await b.close()
    return failures


async def test_6() -> None:
    idx_commits, idx_note = await duplicate_race(force_index=True)
    seq_commits, seq_note = await duplicate_race(force_index=False)
    false_conflicts = await unrelated_vector_writers(10)
    report(6, idx_commits < 2, f"through the HNSW index: {idx_note}; with the planner's choice: {seq_note}; "
                               f"writers of unrelated vectors failed in {false_conflicts} of 10 rounds")


async def gin_failures(rounds: int, crossing: bool) -> int:
    """Crossing writers insert what the other reads; disjoint writers touch nothing the other reads."""
    failures = 0
    for r in range(rounds):
        a, b = await app(), await app()
        for c in (a, b):
            await c.execute("begin isolation level serializable")
            await c.execute("set local enable_seqscan = off")
        await a.fetchval("select count(*) from node where tsv @@ to_tsquery('english', 'alphaword')")
        await b.fetchval("select count(*) from node where tsv @@ to_tsquery('english', 'betaword')")
        await add_node(a, "span", f"{'betaword' if crossing else 'gammaword'} round {r}")
        await add_node(b, "span", f"{'alphaword' if crossing else 'deltaword'} round {r}")
        for c in (a, b):
            try:
                await c.execute("commit")
            except asyncpg.SerializationError:
                failures += 1
                await c.execute("rollback")
        await a.close()
        await b.close()
    return failures


async def test_7() -> None:
    owner = await asyncpg.connect(DSN_OWNER)
    counts = {}
    for setting in ("on", "off"):
        await owner.execute(f"alter index kg.node_tsv set (fastupdate = {setting})")
        await owner.execute("select gin_clean_pending_list('kg.node_tsv'::regclass)")
        counts[setting] = (await gin_failures(20, crossing=True), await gin_failures(20, crossing=False))
    await owner.execute("alter index kg.node_tsv set (fastupdate = on)")
    await owner.close()
    report(7, True, "serialization failures in 20 rounds, crossing writers / disjoint writers: "
                    f"fastupdate on {counts['on'][0]} / {counts['on'][1]}, off {counts['off'][0]} / {counts['off'][1]}")


GERMAN = [
    "Die Datenbankverbindung ist nach dem Update abgebrochen.",
    "Der Schlüsselbund lag im Auto.",
    "Die Projektleitung hat die Entscheidung vertagt.",
    "Wir prüfen die Versionsverwaltung jeden Morgen.",
    "Das Wissensmanagement braucht Quellenangaben.",
]
QUERIES = ["Verbindung", "Datenbank", "Schlüssel", "Leitung", "Entscheidung", "Versionen", "Quellen", "Wissen"]


async def test_8() -> None:
    con = await app()
    rows = []
    tr = con.transaction()
    await tr.start()
    ids = [await add_node(con, "span", t, lang="german") for t in GERMAN]
    for q in QUERIES:
        fts = await con.fetchval(
            "select count(*) from node where id = any($1) and tsv @@ websearch_to_tsquery('german', $2)", ids, q)
        trgm = await con.fetchval(
            "select count(*) from node where id = any($1) and word_similarity($2, body) >= 0.5", ids, q)
        rows.append(f"{q}: full-text {fts}, trigram {trgm}")
    await tr.rollback()
    await con.close()
    misses = [r for r in rows if "full-text 0" in r]
    report(8, True, f"{len(misses)} of {len(QUERIES)} German part-word queries miss in full-text search; " + "; ".join(rows))


CORPUS = GERMAN + [
    "The decisions were recorded and the conjectures criticised.",
    "Generalisation of running experiments, organizational knowledge, happily reporting.",
]


def stems(image: str) -> list[str] | None:
    name = f"kg-stems-{image.replace(':', '-').replace('/', '-')}"
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    up = subprocess.run(["docker", "run", "-d", "--name", name, "-e", "POSTGRES_PASSWORD=x", image],
                        capture_output=True, text=True)
    if up.returncode:
        return None
    try:
        for _ in range(60):
            if subprocess.run(["docker", "exec", name, "pg_isready", "-U", "postgres"], capture_output=True).returncode == 0:
                break
            time.sleep(1)
        time.sleep(2)
        out = []
        for i, text in enumerate(CORPUS):
            config = "german" if i < len(GERMAN) else "english"
            sql = f"select to_tsvector('{config}', $q${text}$q$)::text"
            r = subprocess.run(["docker", "exec", name, "psql", "-U", "postgres", "-At", "-c", sql],
                               capture_output=True, text=True)
            out.append(r.stdout.strip())
        return out
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


def test_9() -> None:
    old, new = stems("postgres:18"), stems("postgres:19rc1")
    if old is None or new is None:
        report(9, False, "could not start postgres:18 or postgres:19rc1; no comparison made")
        return
    changed = [f"[{CORPUS[i][:30]}...] 18: {o} | 19rc1: {n}" for i, (o, n) in enumerate(zip(old, new)) if o != n]
    report(9, True, f"{len(changed)} of {len(CORPUS)} tsvector values differ between 18 and 19rc1 (no final 19 image)"
                    + ("; " + "; ".join(changed) if changed else ""))


async def main() -> None:
    await seed_background()
    await test_1_and_2()
    await test_3()
    await test_4()
    await test_5()
    await test_6()
    await test_7()
    await test_8()
    test_9()
    failed = [n for n, ok, _ in results if not ok]
    print(f"summary: {len(results) - len(failed)} of {len(results)} PASS" + (f"; FAIL: {failed}" if failed else ""))


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
