# A3-SR-11: Matrix Specification v1.12, room versions 1, 3 and 4, event IDs

```json
{
  "source_identity": "Matrix Specification v1.12, 'Room Version 1', 'Room Version 3', 'Room Version 4'; https://spec.matrix.org/v1.12/rooms/v1/, https://spec.matrix.org/v1.12/rooms/v3/, https://spec.matrix.org/v1.12/rooms/v4/",
  "author_or_issuing_body": "Matrix.org Foundation, Spec Core Team",
  "publisher": "Matrix.org Foundation (spec.matrix.org)",
  "publication_date": "2024-10-01T00:00:00Z",
  "relevant_event_date": "2019-01-01",
  "source_family": "Primary. Matrix specification lineage. The three pages belong to one spec release and are recorded as one source.",
  "precise_evidence_location": "rooms/v1: section 'Event IDs'; rooms/v3: 'Client considerations' and 'Event IDs'; rooms/v4: 'Client considerations' and 'Event IDs'",
  "method": "Specification text. Each room version page states its rules and the reason it departs from the previous version.",
  "limitations": "The release date of v1.12 is not printed on the fetched pages; publication_date is set to 1 October 2024 from memory of the release month and should be checked. relevant_event_date 2019-01-01 stands for the introduction of room versions 3 and 4 and is approximate. The Matrix Spec Change proposals behind versions 3 and 4 were not read.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URLs above."
}
```

## Evidence

- rooms/v1, Event IDs: "An event has exactly one event ID. Event IDs in this room version have the format: $opaque_id:domain"
- rooms/v1, Event IDs: "The domain is used only for namespacing to avoid the risk of clashes of identifiers between different homeservers. There is no implication that the room or event in question is still available at the corresponding homeserver."
- rooms/v3, Event IDs: "In other room versions (namely version 1 and 2) the event ID is a distinct field from the remainder of the event, which must be tracked as such. This leads to complications where servers receive multiple events with the same ID in either the same or different rooms where the server cannot easily keep track of which event it should be using."
- rooms/v3, Event IDs: "The event ID is the reference hash of the event encoded using Unpadded Base64, prefixed with $."
- rooms/v3, Client considerations: "Clients should be treating event IDs as opaque identifiers and should not be attempting to parse them into a usable form, just like with other room versions."
- rooms/v4, Event IDs: "Room version 3 generated event IDs that were difficult for client implementations which were not encoding the event ID to function in those rooms. It additionally raised concern due to the / character being interpreted differently by some reverse proxy software, and generally made administration harder."
- rooms/v4: the event ID uses "a variation of Unpadded Base64 which replaces the 62nd and 63rd characters with - and _ instead of using + and /."
- Shows: three dated formulations of the chat event identifier, each with the stated problem that led to the next.
- Does not show: how many servers met duplicate event IDs, or the exact dates of each change.
