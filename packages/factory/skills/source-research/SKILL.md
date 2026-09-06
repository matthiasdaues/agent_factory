---
name: source-research
description: Find sources for one bounded assignment and record them against the source-record artifact.
category: research
disable-model-invocation: false
---

# Source Research

Find and document sources for one bounded research assignment. The playbook controls when source research occurs and how sources are used; this skill covers how to find, assess, and record evidence.

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

The skill produces source-record artifacts validated against [`factory/rulebooks/schemas/research-source-record.schema.json`](../../rulebooks/schemas/research-source-record.schema.json).

Refer to [`factory/rulebooks/templates/research-source-record.md`](../../rulebooks/templates/research-source-record.md) for the template structure.
