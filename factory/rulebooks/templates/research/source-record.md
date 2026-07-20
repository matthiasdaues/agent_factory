---
title: Source Record Template
version: 1.0.0
---

# Source Record Template

Skeleton for a single source-record JSON artifact — the evidence unit of the
falsification-driven research playbook (Procedure Step 4). Validated by
`factory/scripts/schema-validate` against
[source-record.schema.json](../../schemas/research/source-record.schema.json).

## Fields

```json
{
  "source_identity": "",
  "author_or_issuing_body": "",
  "publisher": "",
  "publication_date": "",
  "relevant_event_date": "",
  "source_family": "",
  "precise_evidence_location": "",
  "method": "",
  "limitations": "",
  "provenance": ""
}
```

### source_identity

Stable identifying label for the source — title, filing number, URL, or
similar.

### author_or_issuing_body

The person or organisation who authored or issued the source.

### publisher

The organisation that published or hosts the source.

### publication_date

When the source itself was published. ISO 8601 date-time (e.g.
`2026-07-01T00:00:00Z`).

### relevant_event_date

When the event the source describes took place — may predate publication.
ISO 8601 date (e.g. `2026-06-15`).

### source_family

The lineage this source belongs to. Two records citing the same underlying
wire report, press release, or upstream filing share a `source_family`, so
policy can tell copies apart from independent corroboration.

### precise_evidence_location

Exact locator of the evidence within the source — section, table, timestamp,
or line number.

### method

How the source obtained or produced the evidence.

### limitations

Known weaknesses, biases, or gaps in this source's evidence.

### provenance

Chain of custody: how this record was obtained and how to re-verify it.

## Referenced from

- [source-record.schema.json](../../schemas/research/source-record.schema.json)
