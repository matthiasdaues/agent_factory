# Fagan Review Report — Research Survey — 2026-07-26

## Scope

- Branch: `dev`.
- Implementation range:
  `3cd1f35e3cb884f7a99fabba06a9659f14652333..ade350086158f6422626f2d11bcd4c4c9a59fbc8`.
- QA remediation commits:
  `58ac1a7a45fe2f32509036cf91cb1995de8645f0` and
  `35cd0e71449898683d5e7b91d8fed3f45765c87c`.
- Specification basis: `ST-0060` through `ST-0064`, the survey-mode design,
  dispatch contract, research validation architecture, and the existing
  falsification contracts.
- Explicitly excluded: `HANDOFF.md` and all operator/restored paths named in the
  QA assignment.

## Changed-file coverage

Every file in the implementation range was inspected against correctness,
Clean Architecture, SOLID, maintainability, and consistency:

- Stories: `backlog/ST-0060.md` through `backlog/ST-0064.md`.
- Discovery and roles: `factory/INDEX.yaml`,
  `factory/agents/research-orchestrator.md`, and
  `factory/agents/research-synthesizer.md`.
- Design and guidance:
  `factory/docs/design/research-cli-portability-audit.md`,
  `factory/docs/design/research-survey-mode.md`,
  `factory/docs/factory-guide.md`, and
  `factory/docs/proposals/research-workflow-efficiency-and-atomicity.md`.
- Workflow contracts: `factory/playbooks/research-survey.md`,
  `factory/playbooks/research-topic.md`, and
  `factory/rulebooks/conventions/dispatch-contract.md`.
- Schemas and templates: the changed research brief contract and the new survey
  plan and report schemas and templates.
- Skills: `factory/skills/research-planning/SKILL.md` and
  `factory/skills/research-synthesis/SKILL.md`.
- Acceptance tests: all five changed `test_research_*survey*` and
  `test_research_cli_portability.py` files.

## Finding table

| Finding                                                                                                                                                                                                                 | Artifact                                         | Category | Severity |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | -------- | -------- |
| The mode-aware Orchestrator omitted survey outputs, the synthesizer handoff, and survey completion criteria; declare those contracts while preserving the falsification-only register requirements.                     | `factory/agents/research-orchestrator.md:17`     | Defect   | Major    |
| The implemented survey design still said "not yet implemented" and claimed reuse of the falsification final-report schema; record the dedicated survey contracts and unchanged falsification boundary.                  | `factory/docs/design/research-survey-mode.md:3`  | Defect   | Major    |
| The end-to-end resolver accepted traversal, absolute, and symlink references outside the survey run; canonically contain every reference below this run's `source-records/` directory and cover all three escape forms. | `orchestrator/tests/test_research_survey_e2e.py` | Defect   | Major    |

Filed as `FAGAN-0008`, `FAGAN-0009`, and `BUG-0001`; all are resolved and
verified.

## Five focus areas

**Correctness.** The brief defaults to survey, explicit falsification remains
separate, survey artifacts use dedicated schemas, every finding carries source
references, and all five survey steps retain their declared validation gates.
The three defects above were corrected. The final source resolver now proves
that cited records belong to the run rather than merely existing somewhere on
disk.

**Clean Architecture.** The shared brief and source-record contracts remain
common infrastructure; survey planning/synthesis and falsification
claim/reporting remain separate capabilities. CLI invocation mapping stays in
the dispatch contract rather than leaking into research semantics.

**SOLID.** Planning selects a mode-specific output contract, the Research
Synthesizer owns source-grounded report creation, and the Orchestrator retains
administrative validation and dispatch responsibilities. No remaining SOLID
violation was found.

**Maintainability.** Schema, capability, playbook, installed-surface, and
end-to-end tests cover distinct public seams. The containment regression names
`BUG-0001` and covers relative traversal, absolute paths, and symlink escape.
The generated index description now reflects both planning modes.

**Consistency.** Agent frontmatter, design status, completion criteria,
playbooks, templates, schemas, tests, and generated catalog now describe the
same two-mode workflow. Markdown numbering and generated index metadata are
current.

## YAGNI check

No YAGNI violation remains. Dedicated survey plan/report schemas and a separate
synthesis role are required to avoid weakening falsification invariants. No
unused abstraction, speculative extension point, or premature optimization was
introduced.

## Verification

- Bug red state: 3 failures for traversal, absolute-path, and symlink escapes.
- Bug green state: the same 3 cases passed after canonical containment.
- Complete research regression: 170 passed.
- Full orchestrator regression: 467 passed in 145.72 seconds with warnings as
  errors.
- Final independent hunt cycle: 48 changed survey acceptance tests passed in
  1.90 seconds; zero new bugs found.
- Ruff check/format, spec-lint, arch-lint, backlog-lint, statemachine-lint, and
  index-lint passed. Arch-lint retained two pre-existing parse warnings and
  backlog-lint retained one pre-existing `ST-0013` warning.

The first sandboxed dependency resolutions failed because network access was
restricted, and the first statemachine-lint attempt used a read-only default uv
cache. Approved dependency resolution and a `/tmp` cache rerun passed; neither
was a product failure.

## Done-check

- [x] Every changed file inspected against all five focus areas.
- [x] Specification and Gherkin-style acceptance criteria explicitly checked.
- [x] Findings categorized, actionable, filed, fixed, and resolved.
- [x] YAGNI explicitly checked.
- [x] Full regression passed.
- [x] A complete final hunt cycle found zero new bugs.

## Conclusion

Fagan review passes. No open QA defect remains.
