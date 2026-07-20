---
name: source-research
description: Find sources for one bounded assignment and record them against the source-record artifact.
category: research
disable-model-invocation: false
---

# Source Research

This skill provides a capability for finding and documenting sources to answer one bounded research assignment. It does not control the workflow sequence — the playbook controls when source research occurs and how sources are used.

## Capability

Execute research for a single bounded assignment by finding sources and recording evidence for evaluation.

Each source record must document:

| Field                       | Purpose                                                  |
| --------------------------- | -------------------------------------------------------- |
| `source_identity`           | Stable identifying label for the source                  |
| `author_or_issuing_body`    | Person or organization who authored or issued it         |
| `publisher`                 | Organization that published or hosts the source          |
| `publication_date`          | When the source itself was published                     |
| `relevant_event_date`       | When the event the source describes took place           |
| `source_family`             | Lineage to identify copies vs. independent corroboration |
| `precise_evidence_location` | Exact locator of the evidence within the source          |
| `method`                    | How the source obtained or produced the evidence         |
| `limitations`               | Known weaknesses, biases, or gaps in this source         |
| `provenance`                | Chain of custody and how to re-verify                    |

## Output

The skill produces source-record artifacts validated against [`factory/rulebooks/schemas/research/source-record.schema.json`](../../rulebooks/schemas/research/source-record.schema.json).

Refer to [`factory/rulebooks/templates/research/source-record.md`](../../rulebooks/templates/research/source-record.md) for the template structure.

## Responsibility

This skill is **responsible for** finding sources and recording evidence: locating material, assessing provenance, identifying source families, noting limitations, and preserving the chain of custody.

This skill is **not responsible for** controlling workflow: that is the playbook's role. It is not responsible for planning research, proposing claims, designing tests, reviewing claims, or generating the report.
