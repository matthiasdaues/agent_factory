# A1-SR-18: Gunnar Morling, The Wonders of Postgres Logical Decoding Messages, 2023

```json
{
  "source_identity": "Gunnar Morling, 'The Wonders of Postgres Logical Decoding Messages', InfoQ, 6 March 2023, https://www.infoq.com/articles/wonders-of-postgres-logical-decoding-messages/",
  "author_or_issuing_body": "Gunnar Morling (Decodable at the time); reviewed by Srini Penchikala",
  "publisher": "InfoQ (C4Media)",
  "publication_date": "2023-03-06T00:00:00Z",
  "relevant_event_date": "2023-03-06",
  "source_family": "Primary: the author's own article. Same author as A1-SR-17; it criticises the table-based outbox of A1-SR-16 and A1-SR-17.",
  "precise_evidence_location": "Opening paragraph; section The Outbox Pattern, paragraphs 1 to 3 and the paragraph after the pg_logical_emit_message example",
  "method": "Design article with examples run against PostgreSQL.",
  "limitations": "Only the day is given. The article describes a variant that needs logical decoding and a CDC tool, so it adds components to the stack. Debezium's outbox router did not support this variant when the article was written, by the article's own words. The PostgreSQL manual page for pg_logical_emit_message was not read for this record.",
  "provenance": "Downloaded with curl (browser user agent) on 2026-11-18 and converted with pandoc. Re-verify at the URL above."
}
```

## Evidence

- Opening: "Let me tell you about pg_logical_emit_message()! It’s a Postgres function that allows you to write messages to the write-ahead log (WAL) of the database."
- The Outbox Pattern: "Instead of inserting outbox events in a dedicated outbox table, the idea is to emit them just as logical decoding messages to the WAL."
- The Outbox Pattern: "What makes the route via logical decoding messages compelling is that it avoids any housekeeping needs."
- The Outbox Pattern: "Unlike with an outbox table, there’s no need to remove messages after they have been consumed from the transaction log."
- The Outbox Pattern: "messages must never be modified after being added to the outbox, which might happen by accident with a table-based approach."
- After the example: "This creates a transactional message (i.e., it would not be emitted if the transaction aborts, e.g., because of a constraint violation of another record inserted in the same transaction)."
- After the example: "However, this SMT doesn’t yet support using logical decoding messages as the outbox format."
- What the source shows: the third formulation. It criticises the outbox table for its housekeeping and for rows that can be changed by accident, and moves the events into the write-ahead log.
- What the source does not show: how a consumer reads old events again once the log is consumed. For a store whose events must stay readable, the table-based outbox of A1-SR-16 keeps them; this variant does not.
