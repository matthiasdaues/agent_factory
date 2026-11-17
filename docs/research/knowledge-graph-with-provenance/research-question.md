# Research Question: Knowledge Graph With Provenance

## Origin

The stakeholder talked to a practitioner of knowledge management. The
practitioner does not keep knowledge as large summarized documents. The
practitioner splits conversation transcripts, emails, Slack messages, and
Teams messages into single ideas and concepts. Each idea links to related
ideas and to the source message it came from. This research calls that
structure a **knowledge graph with provenance**: provenance is the link from
an idea back to its source object.

## Question

How could the Agent Factory proposal process evolve into an idea generation
and concept formulation process? That process has access to every idea
already discussed and to every decision taken on an idea, such as do, won't
do, defer, or accept.

## What the stakeholder wants at the end

A set of design options for that evolved process, grounded in what the
factory already records and in what existing methods and tools do. The
research does not change factory code, skills, or proposals.

## Settled for this research

- The term is "knowledge graph with provenance".
- The approach is improvised: four parallel investigators, then one
  synthesis. It does not follow the `research-survey` playbook steps.
- Each investigator may read anything in the repository and writes only its
  own output file. No investigator edits any other file.

## Investigators

| ID  | Angle                                      | Runs on             | Output                            |
| --- | ------------------------------------------ | ------------------- | --------------------------------- |
| A   | Where ideas and decisions live in the repo | Claude Sonnet       | `sources/internal-inventory.md`   |
| B   | External methods and tools                 | Claude Sonnet       | `sources/external-survey.md`      |
| C   | Splitting sources into linked ideas        | Claude Sonnet       | `sources/extraction-pipeline.md`  |
| D   | Independent process design                 | Codex `gpt-6-astra` | `sources/codex-process-design.md` |
