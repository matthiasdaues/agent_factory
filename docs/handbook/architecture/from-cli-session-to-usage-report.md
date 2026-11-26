---
title: From CLI session to usage report
type: concept
status: implemented
order: 10
description: Trace token counts from CLI events through capture and analysis.
---

# From CLI session to usage report

Usage tracking starts in the CLI integration. The optional usage add-on reads the records that capture has written. When investigating a total, first check the record for the session, then check how the add-on combines it with other records.

1. A CLI hook or extension invokes capture on an event such as a session or subagent stop. The wiring depends on the CLI. For example, the [Codex capture hook](../../../packages/factory/config/hooks/capture-codex-usage.sh) invokes the capture runtime, and Codex requires you to trust the installed hook definitions.
2. [Usage capture](../../../packages/factory/scripts/usage-capture) interprets the CLI transcript. It counts input and output text with the common `cl100k_base` tokenizer. The `normalized_*` fields support comparisons across CLIs. The separate `reported_*` fields hold provider counts when available.
3. Capture appends records under `.agent-factory/usage/` as JSON Lines. When transcript retention is set to `omit`, capture keeps counts and audit context without saving transcript text. A session binding can also supply workstream context for a record.
4. The add-on in `packages/usage/` validates the records, selects the latest snapshots, and presents totals through query views. It applies a rule for each CLI. For example, a Codex root snapshot already includes child usage. A Pi total adds the root and distinct descendants.

| What you see                                         | Where to look                                                                                                                                                              |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| No usage record appears                              | Check whether your CLI ran the configured hook or extension, then check the capture runtime. In Codex, check hook trust first.                                             |
| A record has surprising counts                       | Check the CLI normalizer and whether you are reading normalized or provider counts.                                                                                        |
| A report total differs from the records you added up | Check snapshot selection and child accounting in [accounting.py](../../../packages/usage/src/usage/accounting.py).                                                         |
| A query or export fails                              | Start with the [add-on structure](usage-add-on-structure.md) and run the [diagnostic query from source](run-usage-add-on-from-source.md#run-the-usage-add-on-from-source). |

For trigger and accounting details, see the [usage capture reference](../../../packages/factory/docs/handbook/usage-capture/usage-capture-reference.md#triggers-and-accounting-per-cli). For the next stage, see [the usage add-on pipeline](usage-add-on.md).
