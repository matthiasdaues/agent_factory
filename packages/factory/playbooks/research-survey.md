---
title: Research Survey Playbook
category: orchestration
type: runbook
scenario: research-survey
version: 1.1.0
---

# Research Survey Playbook

Operational procedure for source-grounded survey research, from a validated
brief to a validated cited synthesis. It gathers what credible recorded
sources say without applying the conjecture, refutation, voting, or
claim-register machinery of falsification mode.

The procedure has exactly five steps. Every artifact passes schema validation,
policy where applicable, and semantic review before progression. A failed
stage blocks progression and the gate restarts at schema validation after the
artifact is corrected.

## Working Root

All artifact paths in this playbook are relative to a per-topic slug
directory: `docs/research/<slug>/`. The slug is the kebab-case topic name
(e.g. `agent-zero`, `opencode-cli-integration`). Every agent and skill
invocation receives this directory as its working root. See
[research-directory-layout.md](../rulebooks/conventions/research-directory-layout.md).

Run the commands below from the project root. Pass the topic directory or
its source folder to the scripts.

## Inputs

- `research-brief.md` — a shared research brief whose mode is omitted or
  explicitly `survey`.

## Outputs

- `research-survey-plan.md` — bounded questions, search angles, source targets,
  assignments, and stop conditions.
- `sources/**/<ID>-SR-<n>-<slug>.md` — one source record per file, with
  provenance and limitations. An assignment may add an area index beside its
  record folder.
- `histories/*.json` — one concept history per file, only when the brief asks
  which concepts went through several rounds of formulation and criticism.
- `survey-report.md` — cited findings, uncertainties, evidence gaps,
  limitations, and candidates for deeper study.

## Research Capability Preflight

Before planning or gathering sources, apply the
[research assignment contract](../rulebooks/conventions/dispatch-contract.md#research-assignment-contract).
Required source access must be available; otherwise block the survey run.

Every source-gathering assignment declares `agent`, Factory `tier`, bounded
`task`, a unique `output` path, and `independent_session: false`. Dispatch a
bounded wave when the active CLI supports it. If parallel fan-out is
unavailable, preserve the same assignments and unique output paths and run
them sequentially.

Survey fallback changes scheduling only. It does not permit two assignments to
share an output or allow missing source access.

## Procedure

### Step 1 — Validate the Brief

**Agent**: `research-orchestrator`\
**Input**: `research-brief.md`\
**Output**: validated survey brief, or a blocker

Confirm that the brief conforms to `research-brief.schema.json`. The `mode`
field must be omitted or equal `survey`; a falsification brief belongs in
`research-topic.md`. Semantically confirm that the question is bounded and its
scope, source requirements, freshness needs, and completion criteria are
usable.

**Gate**: schema validation, policy where applicable, then semantic review
must pass. Failure blocks progression to Step 2.

### Step 2 — Plan the Survey

**Agent**: `researcher`\
**Skill**: `research-planning`\
**Input**: validated survey brief\
**Output**: `research-survey-plan.md`

Create bounded questions, search angles, source targets, unique assignments,
and stop conditions. Validate the plan against
`research-survey-plan.schema.json`.

**Gate**: schema validation, policy where applicable, then semantic review
must pass. Failure blocks progression to Step 3.

### Step 3 — Gather Sources

**Agent**: `researcher`\
**Skill**: `source-research`\
**Input**: validated survey plan and its assignments\
**Output**: `sources/*.md`

Dispatch the plan's logical assignments under the portable contract above.
Record every material source against `research-source-record.schema.json`,
including provenance, precise evidence location, method, and limitations.
Each record is its own file, named by its record ID, with the schema fields in
one `json` block ([source-research](../skills/source-research/SKILL.md#record-file)).

**Gate**: `.agent-factory/factory/scripts/source-record-check docs/research/<slug>/sources/` exits
0, applicable source policy passes, then semantic review passes. Each
researcher runs the check with its own source folder as the argument before it reports. Failure blocks
progression to Step 4.

### Step 4 — Synthesise the Findings

**Agent**: `research-report-writer` (survey mode)\
**Skill**: `research-synthesis`\
**Input**: validated plan and recorded `sources/*.md`\
**Output**: `survey-report.md`

Build findings only from the recorded sources. Every finding declares
`source_record_refs`; the report also preserves uncertainties, evidence gaps,
limitations, and `candidates_for_deeper_falsification_study`. Validate its
shape against `research-survey-report.schema.json`.

When the brief asks for concept histories, the writer records each history as
`histories/<concept>.json` against `research-concept-history.schema.json`.
`.agent-factory/factory/scripts/concept-history-check` checks every quote,
date, and entry rule and computes the rank. The report copies the table that
`concept-history-check --table docs/research/<slug>/` prints and never states a count or a rank of
its own ([research-synthesis](../skills/research-synthesis/SKILL.md#concept-histories)).

**Gate**: schema validation, `concept-history-check` where histories exist,
policy where applicable, then semantic review must pass. Failure blocks
progression to Step 5.

### Step 5 — Validate the Report

**Agent**: `research-orchestrator`\
**Input**: `survey-report.md`, `sources/*.md`\
**Output**: validation result

First validate the report against `research-survey-report.schema.json`, and
rerun `source-record-check` and, where histories exist,
`concept-history-check`. Then resolve every finding's `source_record_refs` to
a recorded source from this survey and confirm that the cited records support
the finding within their stated bounds. Reject invented references and
unsupported synthesis.

For a concept history, the script has already settled quotes, dates, counts,
and ranks. The semantic review judges only what a script cannot: whether each
quote shows what its step claims, whether a step is a new formulation, and
whether a criticism marked `drove_next` is one the source presents as leading
to the next formulation. The report table must match the script output.

The semantic review also rejects falsification-only status language. A survey
finding must not be described as having "survived refutation", been "admitted",
or become a "validated claim"; those verdicts require the separate
falsification workflow.

**Gate**: schema validation, policy where applicable, then semantic review
must pass. Failure blocks progression and release. Only a passing report
completes the survey.
