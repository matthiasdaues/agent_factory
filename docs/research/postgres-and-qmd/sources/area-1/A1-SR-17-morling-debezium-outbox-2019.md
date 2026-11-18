# A1-SR-17: Gunnar Morling, Reliable Microservices Data Exchange With the Outbox Pattern, 2019

```json
{
  "source_identity": "Gunnar Morling, 'Reliable Microservices Data Exchange With the Outbox Pattern', Debezium blog, 19 February 2019, https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/",
  "author_or_issuing_body": "Gunnar Morling (Red Hat, Debezium project lead at the time)",
  "publisher": "Debezium project, debezium.io",
  "publication_date": "2019-02-19T00:00:00Z",
  "relevant_event_date": "2019-02-19",
  "source_family": "Primary: the author's own description of an outbox implemented with log-based change data capture on PostgreSQL. Builds on the pattern of A1-SR-16; A1-SR-18 is the same author's later variant.",
  "precise_evidence_location": "Sections The Issue of Dual Writes; The Outbox Table; An Implementation Based on Change Data Capture; the paragraph on persist() and remove(); the consumer section on duplicates",
  "method": "Design article with an example implementation (order and shipment services, Debezium Postgres connector, Kafka).",
  "limitations": "Written by the lead of the tool it describes, so its claims about overhead are a vendor view and are not used as evidence of performance. Only the day is given, no time. The article targets Kafka as the broker, not WebSocket clients.",
  "provenance": "Downloaded with curl on 2026-11-18 and converted with pandoc. Re-verify at the URL above."
}
```

## Evidence

- Dual writes: "The reason being that we cannot have one shared transaction that would span the service’s database as well as Apache Kafka, as the latter doesn’t support to be enlisted in distributed (XA) transactions."
- Outbox table: "When receiving a request for placing a purchase order, not only an INSERT into the PurchaseOrder table is done, but, as part of the same transaction, also a record representing the event to be sent is inserted into that outbox table."
- CDC: "As opposed to any polling-based approach, event capture happens with a very low overhead in near-realtime."
- CDC: "So we are able to capture the event added to the outbox table by means of CDC, but when looking at the contents of the table itself, it will always be empty."
- CDC: "This means that no additional disk space is needed for the table (apart from the log file elements which will automatically be discarded at some point) and also no separate house-keeping process is required to stop it from growing indefinitely."
- Consumer: "Propagating the event UUID as a Kafka message header allows for an efficient detection and exclusion of duplicates in the consumer."
- Note: the article calls the pipeline at-least-once and has the consumer drop duplicates by event ID. The source puts the phrase in quotation marks, so it is recorded here as a paraphrase.
- What the source shows: the second formulation. It criticises polling and replaces the relay with log tailing of the PostgreSQL write-ahead log, inserting and deleting the outbox row in the same transaction.
- What the source does not show: an outbox for a store that must keep its events. Here the outbox row is deleted at once and the broker keeps the history, which differs from the sketch.
