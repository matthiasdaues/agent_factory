---
name: research-synthesis
description: Build a cited survey report from recorded source records while preserving uncertainty and evidence bounds.
category: research
---

# Research Synthesis

Turn recorded source records into a source-grounded survey report. The survey playbook controls when synthesis occurs and how the result is released; this skill covers how to write the report.

Read [factory-voice.md](../../rulebooks/conventions/factory-voice.md) now and hold every rule as a writing constraint. No prose reaches terminal output or a file until it passes all four gates and clears the final pass.

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

## Concept histories

Some briefs ask which concepts went through several rounds of formulation,
criticism, and reformulation. A history told in prose invites overstatement:
a step the record does not show, a criticism that came after the change it
supposedly drove, or a count that includes evaluations. So the history is
data, and a script checks it.

Write one file per concept, `histories/<concept-slug>.json`, against
[`research-concept-history.schema.json`](../../rulebooks/schemas/research-concept-history.schema.json):

- Each step is one new formulation, with its date, its record ID, and a quote
  copied word for word from the record file. The date is the record's
  `publication_date`, or its `relevant_event_date` when the record describes
  an earlier event; the script checks it against the record. A criticism, comparison,
  evaluation, or application is never a step of its own.
- `criticism` holds the criticism recorded against that formulation, with its
  own record, date, and quote, or `null` when no record documents one. Never
  fill a missing criticism from memory.
- Set `drove_next` to `true` only when the source presents the criticism as
  leading to the next formulation. A later assessment gets `false`.
- A quote is one contiguous passage of at least four words, taken from inside
  one double-quoted passage of the record's `Evidence` section. A researcher's
  note around the quotation marks is not the source's words and fails. An
  ellipsis is rejected; anchor two quotes instead. When a record holds no
  quoted words for a step, send the record back to source research.

Then run `.agent-factory/factory/scripts/concept-history-check <survey-root>`
and fix every `FAIL` line. The script applies the entry rule (at least three
formulations and two recorded criticisms) and computes the rank from the
records: first the share of anchors on primary records, then the share of
formulations followed by a recorded criticism, then the number of
formulations. Copy the output of
`concept-history-check --table <survey-root>` into the report unchanged. The
prose may explain each history, but it never states a count, a rank, or an
order the table does not show.

## Validation

Validate the completed report with `.agent-factory/factory/scripts/schema-validate` against
the survey-report schema. Check that every finding cites at least one recorded
source record and that uncertainty, gaps, and limitations remain explicit.
Where histories exist, `concept-history-check` must exit 0 and the report
table must equal its `--table` output.
