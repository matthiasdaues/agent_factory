---
name: research-synthesis
description: Build a cited survey report from recorded source records while preserving uncertainty and evidence bounds.
category: research
disable-model-invocation: false
---

# Research Synthesis

This skill provides a capability to turn recorded source records into a
source-grounded survey report. It does not control workflow sequence — the
survey playbook controls when synthesis occurs and how the result is released.

## Input

Use only source records produced for the validated survey plan. Read each
record's precise evidence location, provenance, and limitations before using
it. A finding without a recorded source record must be omitted.

## Output

Create a survey report conforming to
[`research-survey-report.schema.json`](../../rulebooks/schemas/research-survey-report.schema.json)
and [`research-survey-report.md`](../../rulebooks/templates/research-survey-report.md).
Each finding has a bounded title and summary plus non-empty `source_record_refs`
that identify every source record supporting it.

The report must include:

- `uncertainties` where the available sources are thin, mixed, or unclear;
- `evidence_gaps` for evidence gaps: questions the recorded sources do not
  cover;
- `limitations` that bound the scope, freshness, method, or quality of the
  sources; and
- `candidates_for_deeper_falsification_study` for questions needing a separate,
  more demanding study.

## Validation

Validate the completed report with `factory/scripts/schema-validate` against
the survey-report schema. Check that every finding cites at least one recorded
source record and that uncertainty, gaps, and limitations remain explicit.

## Responsibility

This skill is responsible for source-grounded synthesis and clear reporting of
its bounds. It is not responsible for gathering sources, choosing the survey's
scope, or controlling the playbook sequence.
