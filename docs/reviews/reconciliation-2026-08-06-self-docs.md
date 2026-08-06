---
title: Reconciliation — Factory Self-Documentation vs Code-as-Built
date: 2026-08-06
scope: factory self-documentation (root README + referenced docs, factory/, orchestrator/)
source: reconcile
baseline: 46d84c8 (chore/reconcile-docs checkout)
reviewer: reconciliation-agent (separate session)
---

# Reconciliation Report — Factory Self-Documentation

**Scope.** The Factory's *own* self-documentation, not the `docs/spec` or
`docs/adr` flow-control specification surface (left alone unless a genuine
contradiction forced it). Targets reconciled against the code-as-built:

1. Root `README.md` and root-level docs it references (`docs/concepts.md`,
   `docs/beginner-intro.md`, `docs/CONTEXT-MAP.md`, `docs/README.md`).
2. `factory/` self-documentation (`factory/README.md`, `factory/docs/`).
3. `orchestrator/` self-documentation (`orchestrator/README.md`,
   `orchestrator/docs/**`, `orchestrator/docs/adr/`).

`orchestrator/CONTEXT.md` was checked for — it does not exist (see RECON
discrepancy 1 below).

**Method.** Built truth maps from code (`factory/scripts/`, `factory/config/`,
`factory/playbooks/*.fsm.yml`, `orchestrator/src/`, `orchestrator/pyproject.toml`,
`.pre-commit-config.yaml`, `docs/adr/`, `docs/spec/use_cases/`) and diffed against
the prose claims in the in-scope docs. Verified file paths/existence, command
names and flags, behaviour claims, and architecture/ownership statements. Ran
the deterministic gates (`spec-lint`, `arch-lint`, `backlog-lint`,
`matrix-lint`) both to check the docs *about* them and to confirm the
documented invocation forms.

## Discrepancy table

| #   | Finding                                                                                                                                                                                                                                                                                     | Artifact                                | Category | Severity | Disposition                                                                                                                                 |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | CONTEXT-MAP links to `../orchestrator/CONTEXT.md` (removed) and calls the orchestrator "the `ai_tooling` agent chain" — a dead term two generations stale.                                                                                                                                  | `docs/CONTEXT-MAP.md:7`                 | Defect   | Major    | **Fixed** — entry now links `orchestrator/README.md` + `orchestrator/docs/adr/` and drops `ai_tooling`.                                     |
| 2   | `factory/README.md` top line says "you re-run `init-factory` to update it," contradicting ADR-0010 and the README's own "use the update script instead."                                                                                                                                    | `factory/README.md:3`                   | Defect   | Minor    | **Fixed** — now says run `update-factory`.                                                                                                  |
| 3   | `factory/docs/factory-guide.md` § Linting and gating gives manual-mode examples for 3 of 4 gates as bare positionals (`spec-lint docs/spec/`, `backlog-lint backlog/`, `matrix-lint config/model.conf`) that the scripts reject — they require `--spec-dir`/`--backlog-dir`/`--matrix`.     | `factory/docs/factory-guide.md`         | Defect   | Major    | **Fixed** — examples corrected to the flag forms, all verified to run.                                                                      |
| 4   | `orchestrator/README.md` Files tree implies a single test file (`tests/ └── test_run_playbook.py # 18 tests`) and omits `__init__.py` from `src/`. The suite is now 50 files; `src/` has `__init__.py`.                                                                                     | `orchestrator/README.md` (Files)        | Defect   | Minor    | **Fixed** — tree now notes the 50-file suite and lists `__init__.py`.                                                                       |
| 5   | Pre-push full-suite test gate is documented (ADR-0003 + `factory/README.md` § Test execution hooks) but never wired into either `factory/config/pre-commit-config.yaml` or `.pre-commit-config.yaml`. ADR-0003 is accepted/unsuperseded; the README correctly restates the intended design. | `factory/config/pre-commit-config.yaml` | Defect   | Major    | **Code defect filed** → `docs/findings/RECON-0017.md`. Docs left aligned with ADR-0003 (the intended truth); configuration is what drifted. |

## Observations (not filed, not edited)

- **`docs/README.md` arc42 ToC** lists all 12 chapters, but only
  `05`, `06`, `08`, `09`, `12` exist on disk (`01`, `02`, `03`, `04`, `07`,
  `10`, `11` are absent). This is the flow-control arc42 architecture surface,
  explicitly excluded from scope, and is a known long-standing partial state
  (`arch-lint` is intentionally tolerant of missing chapters). Not edited;
  reconciling it means writing architecture chapters, which is out of scope.
- **`factory/playbooks/greenfield-development.fsm.yml`** declares
  `audit.output_file: .orchestrator/audit.log`, but the orchestrator
  (`orchestrator/src/agent_factory_orchestrator/cli.py`) hardcodes
  `.agent-factory/audit.log`, which is what `orchestrator/README.md` documents.
  The FSM's declarative `audit` block is stale metadata the code does not read.
  Out of scope (playbook/FSM artifact, not self-documentation prose); flagged
  here for a future pass.
- **`factory/README.md` § Test execution hooks** says FSM entry conditions check
  `tests_pass` "before advancing to QA or DONE states." As-built, `tests_pass`
  gates the Implementation→Gate transition and entry to `PHASE_5_QUALITY` (QA),
  not `DONE`. Minor imprecision left untouched because it sits inside the
  section covered by RECON-0017; correcting it in isolation would understate
  the larger gap.

## Verified accurate (no change)

- Root `README.md` — repo-layout claims, links to `factory/`, `orchestrator/`,
  `docs/concepts.md`, `docs/beginner-intro.md`, the workflow-diagram asset
  (`docs/assets/images/workflow-diagram.svg` exists).
- `docs/concepts.md` — project directory tree, phase chain, research-workflow
  description, `update-factory` mention, `factory/config/` template labelling.
- `docs/beginner-intro.md` — all six playbook references resolve; orchestrator
  `.fsm.yml` description; two-modes framing.
- `docs/CONTEXT-MAP.md` — Usage Accounting (`usage/` absent, no code) and
  Factory API ("vision-stub only") claims still accurate.
- `factory/README.md` — `init-factory` footprint, `run-playbook`
  `AF_ORCHESTRATOR_SOURCE` / `orchestrator-v0.1.0` tag (tag exists), `--cli claude|copilot` backends, `run-tests --staged` agent loop, framework
  auto-detection, ADR-0003/UC-09 links.
- `factory/docs/factory-guide.md` — agents/skills/playbooks listings,
  `run_agent`/`dispatch_wave` Pi extensions, runtime usage-capture pipeline,
  research validators (`schema-validate`/`policy-validate` positional forms),
  guardrail deny list, session logging, update-factory workflow.
- `orchestrator/README.md` — delegation model, `--from-state` / marker resume,
  audit-log JSON shape (fields and `action` values match `cli.py`), 18 tests
  in `test_run_playbook.py`, `orchestrator-v0.1.0` package name
  (`agent-factory-orchestrator`), `backlog/` 6 stories, `docs/adr/0001`.
- `orchestrator/docs/05,06,09` and `orchestrator/docs/adr/0001` — consistent
  with `cli.py` (claude/copilot backends, exit-code dispatch, marker/FSM/audit).
  Note: ADR-0001's "~120 lines" snapshot has grown to 350 lines; ADRs are
  historical decision records and are not amended for metric drift.

## Gates run

- `spec-lint --spec-dir docs/spec/` → 0 errors, 0 warnings, 18 info.
- `arch-lint --docs-dir docs/` → 0 errors, 2 warnings (pre-existing DSL parse).
- `backlog-lint --backlog-dir backlog/` → 0 errors, 1 warning.
- `matrix-lint --matrix config/model.conf` → 0 errors.
- `mdformat --number` on all four edited files → clean.

## Prior findings checked

`docs/findings/RECON-0001`–`RECON-0016` reviewed; none describe the
self-documentation surface reconciled here, so no re-resolution was required.
One new code defect filed: `RECON-0017`.

## Commit

Corrections committed as `docs: reconcile factory self-documentation with code-as-built (RECON-0017)`.
