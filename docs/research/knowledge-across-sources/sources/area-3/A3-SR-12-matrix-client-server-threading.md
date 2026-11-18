# A3-SR-12: Matrix Specification v1.12, Client-Server API, threading and rich replies

```json
{
  "source_identity": "Matrix Specification v1.12, Client-Server API, module 'Threading' and section 'Threaded read receipts'; https://spec.matrix.org/v1.12/client-server-api/",
  "author_or_issuing_body": "Matrix.org Foundation, Spec Core Team",
  "publisher": "Matrix.org Foundation (spec.matrix.org)",
  "publication_date": "2024-10-01T00:00:00Z",
  "relevant_event_date": "2022-09-01",
  "source_family": "Primary. Matrix specification lineage, same release as A3-SR-11.",
  "precise_evidence_location": "Client-Server API, module 'Threading' marked '[Added in v1.4]', subsection 'Fallback for unthreaded clients'; section 'Threaded read receipts'",
  "method": "Specification text with JSON examples.",
  "limitations": "publication_date is approximate, as in A3-SR-11. relevant_event_date stands for spec v1.4; the month is from memory and is approximate. The threading proposal (MSC3440) and its review thread were not read, so the criticism that shaped the model is a gap.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URL above."
}
```

## Evidence

- Threading: "[Added in v1.4]" and "Threads allow users to visually branch their conversations in a room. Typically mostly used when a room is discussing multiple topics, threads provide more organisation of communication that traditional rich replies can’t always offer."
- Threading: "It is not possible to create a thread from an event which itself is the child of an event relationship" and "It is therefore also not possible to nest threads."
- Threading: "Unlike rich reply chains, all events in a thread reference the thread root instead of the most recent message."
- Fallback: "events sent by clients which understand threads SHOULD include rich reply metadata to attempt to form a reply chain representation of the conversation. This representation is not ideal for heavily threaded rooms"
- Threaded read receipts: an event is in a thread if it has a rel_type of m.thread or a parent that references the root, and "a maximum of 3 hops is recommended to cover indirect relationships."
- Shows: Matrix has two reply structures side by side: a reply chain to the previous message and a flat thread that points to its root.
- Does not show: the history of rich replies before v1.4, or why nesting was ruled out.
