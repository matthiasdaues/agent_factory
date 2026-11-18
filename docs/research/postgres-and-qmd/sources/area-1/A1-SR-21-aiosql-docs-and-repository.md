# A1-SR-21: aiosql documentation, asyncpg adapter, and repository

```json
{
  "source_identity": "aiosql documentation sources docs/source/index.rst, defining-sql-queries.rst and versions.rst, and adapter aiosql/adapters/asyncpg.py, at commit d4c68265532647878d1732298fd1d63953527bba (head of main), https://github.com/nackjicholson/aiosql",
  "author_or_issuing_body": "William Vaughn (nackjicholson), Fabien Coelho (maintainer) and contributors",
  "publisher": "GitHub, repository nackjicholson/aiosql",
  "publication_date": "2026-11-15T00:00:00Z",
  "relevant_event_date": "2026-11-15",
  "source_family": "Primary: project documentation and source code of aiosql.",
  "precise_evidence_location": "index.rst: opening paragraphs, Usage, Why you might want to use this; defining-sql-queries.rst: Query Names, Operators; versions.rst: entries 13.1 to 16.2; asyncpg.py: class MaybeAcquire (lines 7 to 22), methods insert_update_delete and select_cursor (lines 98 to 120); LICENSE; repository data from the GitHub API",
  "method": "Project documentation and source code read at a fixed commit; repository data from the GitHub API.",
  "limitations": "publication_date is the date of release 16.2. The documentation says nothing about transactions; the transaction behaviour is inferred from the adapter code and is marked so. The GitHub licence field reads NOASSERTION; the LICENSE file and the README badge show a BSD 2-Clause licence.",
  "provenance": "Files downloaded with curl from raw.githubusercontent.com at commit d4c68265 on 2026-11-18. Metadata from gh api repos/nackjicholson/aiosql, /releases and /commits?since=2024-11-18T00:00:00Z on 2026-11-18."
}
```

## Evidence

- index.rst: "With aiosql you can organize your SQL statements in *.sql* files, load them into your python application as methods to call without losing the ability to use them as you would any other SQL file."
- defining-sql-queries.rst: "Name definitions are how aiosql determines the name of the methods that SQL code blocks are accessible by."
- index.rst, Why you might NOT want to use this: "You aren't comfortable writing SQL code." The same list names the search for an ORM as a reason against aiosql.
- asyncpg.py, MaybeAcquire: if the object passed in has an `acquire` method, such as an asyncpg pool, each query call acquires a connection and releases it afterwards; a plain connection is used as given.
- asyncpg.py, insert_update_delete: `return await connection.execute(sql, *parameters)`
- versions.rst, 16.2 on 2026-11-15: "minor doc consistency fixes". The same entry adds a driver adapter for aiopg (paraphrase, because the source puts the driver name in quotation marks).
- Statement S12, aiosql part: supported for named queries. Inferred from the adapter: aiosql opens no transaction of its own for writes. To write text, vector and edges in one transaction, the caller passes one asyncpg connection inside `connection.transaction()`. A pool passed to several calls would run each call on its own connection and in its own transaction. aiosql has no listener interface; listening stays with asyncpg (A1-SR-20).
- Release activity from 2024-11-18 to 2026-11-18: ten releases, from 13.1 (2025-01-23) to 16.2 (2026-11-15).
- Project health on 2026-11-18: not archived; last push 2026-11-15; no open issues; 122 commits since 2024-11-18, of which Fabien Coelho wrote 119. The project depends on one maintainer for most of its work. Licence BSD 2-Clause, so open source.
- What the source shows: SQL files with named queries turned into Python methods, the asyncpg adapter, and an active release rhythm.
- What the source does not show: a transaction helper or support for LISTEN.
