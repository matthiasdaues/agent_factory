---
id: 0028
status: accepted
evaluation: none
---

# Declared review and a core list check ownership

## Context

[ADR-0027](0027-split-the-requirements-agent-by-artifact-family.md) gives each
core artifact one producer. Nothing yet checks that this stays true. Today
eight core files have no review: the spec-review agent declares only the
feature files and the scope map as required inputs, and nothing reviews the
dependency rules, the schemas, or the area specs.

A check built only on `INDEX.yaml` cannot find a missing producer, because an
artifact that no agent declares never appears there. Output patterns also
differ in form: one agent declares `docs/spec/features/{name}.feature`, another
reads `docs/spec/features/*.feature`. Wide patterns such as the lector agent's
`docs/**/*.md` match every Markdown core file.

The accepted proposal
[core-artifact-ownership.md](../proposals/core-artifact-ownership.md) settles
the mechanism (DEC-01, DEC-20, DEC-22, DEC-25, DEC-29, DEC-31, DEC-32,
DEC-34), and the
[gaps report](../spec/work/core-artifact-ownership-gaps.md) settles its field
names (CAO-G05, CAO-G06, CAO-G12, CAO-G14). The rejected options are:

- **A review without a declaration.** A review that lives only in a playbook
  step cannot be checked, and the eight unreviewed files show the result
  (DEC-01).
- **A sample path derived from the pattern.** The test would need a fixed
  replacement rule for `*`, `**`, and `{name}`. A stored `sample_path` needs
  none (CAO-G05).
- **An `index-lint` reviewer check without the core list.** It would derive its
  own sample paths, and the two checks could disagree (CAO-G06).
- **A narrower lector pattern.** The lector agent edits every document, so a
  narrow pattern would cut its job. A declaration with `edits: wording` keeps
  the job and marks that it changes no meaning (DEC-32).

`evaluation: none`, because the proposal decided each point and no open
alternative is left to weigh.

## Decision

Each output declaration of a core or seam artifact carries `reviewed_by:`, a
list of agent names, `stakeholder`, or both. The producer declares who confirms
its work, so producer and review stand in one place. A reviewer declares the
artifact as a required input, or as a context input when a project may lack it.

`packages/factory/rulebooks/core-artifacts.yaml` is the single source for the
set of core and seam artifacts. Each entry holds `path_pattern`,
`sample_path`, `family`, and `optional`.

Two checks read the list and match by sample path. A placeholder such as
`{name}` matches like `*` inside one path segment.

- The ownership contract test fails when a sample path matches no producing
  output pattern, more than one, or a declaration without `reviewed_by:`. It
  skips declarations with `edits: wording`.
- `index-lint` carries `reviewed_by:` and `edits:` into `INDEX.yaml`. In
  `--check` mode it fails on a reviewer that is neither an agent nor
  `stakeholder`, or that lacks the artifact as a required or context input.

The single-producer rule holds for core and seam files only. Working output,
reports, and findings may have several writers, each declaring the path.

## Consequences

- A change to an agent definition that breaks ownership fails the test suite or
  `index-lint --check` before it merges.
- A new core artifact needs an entry in the core list. Without one, nothing
  checks its producer.
- The contract test checks producer and review only. Gates for
  `entity-model.md`, `schemas/*`, and `testing.yaml` stay missing (DEC-08).
- Every glossary term now needs the stakeholder. Agents other than the
  domain-modeling agent write term candidates to
  `docs/spec/work/term-candidates.md` instead of the glossary.
- A finding names its owner in an `owner:` field, and the orchestrator routes it
  there instead of to the author of the reviewed phase.
