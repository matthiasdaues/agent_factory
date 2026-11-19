# A1-SR-20: asyncpg API documentation and repository

```json
{
  "source_identity": "asyncpg API Reference, https://magicstack.github.io/asyncpg/current/api/index.html (documentation covering releases up to 0.32.0); repository MagicStack/asyncpg, release v0.32.0 notes, https://github.com/MagicStack/asyncpg",
  "author_or_issuing_body": "MagicStack Inc. (Elvis Pranskevichus and contributors)",
  "publisher": "MagicStack, documentation on GitHub Pages; repository on GitHub",
  "publication_date": "2026-10-06T00:00:00Z",
  "relevant_event_date": "2026-10-06",
  "source_family": "Primary: project documentation and release record of asyncpg.",
  "precise_evidence_location": "API Reference: Connection.add_listener, Connection.add_termination_listener, Connection.transaction, section Transactions, Pool section on release and setup; release notes of v0.32.0; repository metadata and release list from the GitHub API",
  "method": "Project documentation; repository data from the GitHub API.",
  "limitations": "publication_date is the date of release v0.32.0, the newest version the documentation mentions; the documentation page itself carries no date. The documentation does not say whether a listener receives notifications sent while its connection was down; the PostgreSQL rules of A1-SR-08 apply. Open issue count includes pull requests.",
  "provenance": "Documentation downloaded with curl on 2026-11-18 and converted with pandoc. Release notes and metadata from gh api repos/MagicStack/asyncpg, /releases and /commits?since=2024-11-18T00:00:00Z on 2026-11-18."
}
```

## Evidence

- add_listener: "Add a listener for Postgres notifications."
- add_listener, callback: "A callable or a coroutine function receiving the following arguments: connection: a Connection the callback is registered with; pid: PID of the Postgres server that sent the notification; channel: name of the channel the notification was sent to; payload: the payload."
- add_termination_listener: "Add a listener that will be called when the connection is closed."
- Transactions: "The most common way to use transactions is through an async with statement:" followed by `async with connection.transaction():`
- Transactions: "asyncpg supports nested transactions (a nested transaction context will create a savepoint.):"
- transaction(): "If not specified, the behavior is up to the server and session, which is usually read_committed."
- Pool: "Likewise, all notification and log listeners are removed, and asyncpg will issue a warning if there are any listener callbacks registered on a connection that is being released to the pool."
- Statement S12, asyncpg part: supported. asyncpg runs a block of statements in one transaction and delivers notifications to a callback. A listener must hold its own connection; releasing a pooled connection removes its listeners. A termination callback lets the application see a lost connection, and then it must reconnect and read the outbox (inferred from A1-SR-08).
- Release activity from 2024-11-18 to 2026-11-18: two releases, v0.31.0 (2025-11-24) and v0.32.0 (2026-10-06). v0.30.0 came on 2024-10-20. v0.32.0 notes: "Support PostgreSQL 19 (#1379)".
- Project health on 2026-11-18: not archived; licence Apache-2.0, so open source; last push 2026-10-08; 290 open issues and pull requests; 58 commits since 2024-11-18, of which Elvis Pranskevichus wrote 33.
- What the source shows: the listener, transaction and pool interfaces, and a slow but steady release rhythm.
- What the source does not show: named queries. asyncpg runs SQL strings; naming comes from aiosql (A1-SR-21).
