---
name: source-research
description: Find sources for one bounded assignment and record them against the source-record artifact.
category: research
---

# Source Research

Find and document sources for one bounded research assignment. The playbook controls when source research occurs and how sources are used; this skill covers how to find, assess, and record evidence.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.
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

The skill produces source-record artifacts validated against [`.agent-factory/factory/rulebooks/schemas/research-source-record.schema.json`](../../rulebooks/schemas/research-source-record.schema.json).

Refer to [`.agent-factory/factory/rulebooks/templates/research-source-record.md`](../../rulebooks/templates/research-source-record.md) for the template structure.

## Record file

Write one source per file, so each record can be checked and cited on its own:

- Name the file by its record ID and a short slug, such as
  `sources/area-2/A2-SR-05-rdf-star-report.md`, or `sources/SR-0005.md` in a
  survey without areas. The assignment's output names the folder and the ID
  prefix.
- Start with a heading, then one fenced `json` block with exactly the ten
  schema fields. `publication_date` is an ISO 8601 date-time; where only a
  year or month is known, use the first day and say so in `limitations`.
- `source_family` starts with "Primary" or "Secondary" and then names the
  lineage. `concept-history-check` reads that first word.
- Follow with an `Evidence` section that holds the quotes and their exact
  locations. Put the source's own words in straight double quotes, and keep
  your notes outside them. Mark a quote that came through a summarizing fetch
  tool as a paraphrase. A later concept history may anchor only on words that
  stand inside double quotes in this section.

Run `.agent-factory/factory/scripts/source-record-check <your folder>` and fix
every `FAIL` line before you report.
