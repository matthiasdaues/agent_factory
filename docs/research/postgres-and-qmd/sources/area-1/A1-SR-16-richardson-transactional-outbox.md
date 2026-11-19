# A1-SR-16: Chris Richardson, Pattern: Transactional outbox, with Polling publisher and Transaction log tailing

```json
{
  "source_identity": "Chris Richardson, 'Pattern: Transactional outbox', https://microservices.io/patterns/data/transactional-outbox.html; with the linked pages 'Pattern: Polling publisher' (/patterns/data/polling-publisher.html) and 'Pattern: Transaction log tailing' (/patterns/data/transaction-log-tailing.html)",
  "author_or_issuing_body": "Chris Richardson",
  "publisher": "microservices.io, run by Chris Richardson",
  "publication_date": "2017-01-01T00:00:00Z",
  "relevant_event_date": "2017-01-01",
  "source_family": "Primary: the pattern description by the author who catalogued it under this name. The outbox records A1-SR-17 and A1-SR-18 cite the pattern and build on it.",
  "precise_evidence_location": "Transactional outbox: sections Context, Forces, Solution, Result context, Related patterns. Polling publisher: Solution and Resulting context. Transaction log tailing: Solution and Resulting context",
  "method": "Pattern catalogue entry: context, problem, forces, solution, and consequences.",
  "limitations": "Only the year is known: the page's metadata gives copyrightYear 2017, so the date is set to 1 January 2017. The page is a living document with a 2026 footer; later edits cannot be dated. The page does not say who first used the pattern. The site promotes the author's books and training; only the pattern text is used.",
  "provenance": "Downloaded with curl on 2026-11-18 and converted with pandoc. copyrightYear read from the page's JSON-LD block. Re-verify at the URLs above or in the Internet Archive."
}
```

## Evidence

- Context: "But without using 2PC, sending a message in the middle of a transaction is not reliable."
- Solution: "The solution is for the service that sends the message to first store the message in the database as part of the transaction that updates the business entities. A separate process then sends the messages to the message broker."
- Result context, benefit: "Messages are guaranteed to be sent if and only if the database transaction commits"
- Result context, drawback: "Potentially error prone since the developer might forget to publish the message/event after updating the database."
- Result context, issue: "The Message relay might publish a message more than once."
- Result context, issue: "As a result, a message consumer must be idempotent, perhaps by tracking the IDs of the messages that it has already processed."
- Polling publisher, Solution: "Publish messages by polling the database’s outbox table."
- Polling publisher, drawback: "Tricky to publish events in order"
- Transaction log tailing, Solution: "Tail the database transaction log and publish each message/event inserted into the outbox to the message broker."
- Transaction log tailing, drawbacks: "Requires database specific solutions" and "Tricky to avoid duplicate publishing"
- Statement S9: supported as a pattern. An outbox table written in the same transaction keeps each event until a relay reads it, so events survive a listener restart. In the sketch, NOTIFY only wakes the relay. The pattern does not name NOTIFY; that use is the sketch's own.
- What the source shows: the first formulation of the outbox with two relay variants and their stated drawbacks: duplicates, ordering with polling, and database-specific log tailing.
- What the source does not show: how to remove rows from the outbox table, or how a relay learns of new rows without polling.
