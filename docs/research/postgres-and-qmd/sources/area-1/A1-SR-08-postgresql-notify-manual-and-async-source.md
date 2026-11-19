# A1-SR-08: PostgreSQL NOTIFY and LISTEN, manual and source file async.c

```json
{
  "source_identity": "PostgreSQL 18 manual: NOTIFY (https://www.postgresql.org/docs/current/sql-notify.html) and LISTEN (https://www.postgresql.org/docs/current/sql-listen.html); source file src/backend/commands/async.c at commit e3b7f6156916c2ffefb51c12a0576d8b095d5c26 (head of REL_18_STABLE on 2026-11-18)",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group (postgresql.org; git repository mirrored at github.com/postgres/postgres)",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-11-12",
  "source_family": "Primary: the PostgreSQL manual and the PostgreSQL source code. Same lineage as A1-SR-05 to A1-SR-07.",
  "precise_evidence_location": "NOTIFY: Description, paragraphs on transactions and ordering; Parameters, payload; Notes, queue. LISTEN: Description and Notes. async.c: header comment lines 16 to 123 (model as of 9.0), line 163 (NOTIFY_PAYLOAD_MAX_LENGTH), lines 1066 to 1071 (first LISTEN sets the queue pointer), lines 2129 to 2152 (tail computed from listening backends)",
  "method": "Manual text read directly; source file read directly at a fixed commit.",
  "limitations": "publication_date is the 18.7 release date for the manual; relevant_event_date is the last commit that changed async.c on REL_18_STABLE (82fa6b78dba1, 2025-11-12). The source was read, not run. The statement that a restarted listener misses notifications committed while it was away is inferred from the code and is marked so below. The PostgreSQL 19 version of async.c was not compared.",
  "provenance": "Manual pages downloaded with curl on 2026-11-18 and converted with pandoc. async.c downloaded with curl from https://raw.githubusercontent.com/postgres/postgres/e3b7f6156916c2ffefb51c12a0576d8b095d5c26/src/backend/commands/async.c on 2026-11-18. Re-verify with git show e3b7f615:src/backend/commands/async.c."
}
```

## Evidence

- NOTIFY: "Firstly, if a NOTIFY is executed inside a transaction, the notify events are not delivered until and unless the transaction is committed."
- NOTIFY: "So notification events are only delivered between transactions."
- NOTIFY: "It is also guaranteed that messages from different transactions are delivered in the order in which the transactions committed."
- NOTIFY: "If the same channel name is signaled multiple times with identical payload strings within the same transaction, only one instance of the notification event is delivered to listeners."
- NOTIFY, payload: "In the default configuration it must be shorter than 8000 bytes."
- NOTIFY, Notes: "If this queue becomes full, transactions calling NOTIFY will fail at commit."
- NOTIFY, Notes: "The queue is quite large (8GB in a standard installation) and should be sufficiently sized for almost every use case."
- LISTEN: "A session's listen registrations are automatically cleared when the session ends."
- LISTEN: "LISTEN takes effect at transaction commit."
- LISTEN: "This leads to the following rule for using LISTEN: first execute (and commit!) that command, then in a new transaction inspect the database state as needed by the application logic, then rely on notifications to find out about subsequent changes to the database state."
- async.c, lines 37 to 39: "Since notifications are not expected to survive database crashes, we can simply clean out the pg_notify data at any reboot, and there is no need for WAL support or fsync'ing."
- async.c, lines 59 to 65: "When the transaction is ready to commit, PreCommit_Notify() adds the pending notifications to the head of the queue."
- async.c, same passage: "This is done before marking the transaction as committed in clog." The comment goes on to say that an error while writing the notifications still rolls the transaction back (paraphrase).
- async.c, lines 1069 to 1071: "We set our pointer to the global tail pointer and then move it forward over already-committed notifications."
- async.c, line 163: `#define NOTIFY_PAYLOAD_MAX_LENGTH	(BLCKSZ - NAMEDATALEN - 128)`
- Statement S8: supported by the manual. A listener receives nothing from a rolled-back transaction. The source adds that a failure to write the queue rolls the transaction back.
- Statement S9: the manual states that a notification goes only to sessions that listen, and that registrations end with the session. The source shows that a new listener skips notifications that committed before it registered, and that the queue tail follows the slowest listener. Inferred: notifications committed while no session listens on the channel are never delivered, and a listener that restarts misses those committed during its absence. The queue does not survive a server restart.
- What the source shows: delivery at commit, ordering by commit, folding of duplicates, the 8000-byte payload limit, the queue size, and the loss of notifications without a listener.
- What the source does not show: an outbox. The manual only says that structured data can be passed through tables; the outbox pattern is in A1-SR-16 to A1-SR-18.
