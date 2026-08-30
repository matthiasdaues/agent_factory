---
title: Reconciliation — Factory Self-Documentation (Repeat Pass)
date: 2026-08-06
scope: factory self-documentation (root README + referenced docs, factory/, orchestrator/)
source: reconcile
baseline: 50b307f (chore/reconcile-docs checkout, post RECON-0017)
reviewer: reconciliation-agent (separate session)
---

# Reconciliation Report — Factory Self-Documentation (Repeat Pass)

**Scope.** A repeat-pass reconciliation of the Factory's *own*
self-documentation against the code-as-built. Same target set as the
2026-08-06 self-docs pass, run fresh per
[review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md):
re-verify every open `RECON` finding *and* rebuild the truth-map diff from
scratch to catch drift the prior pass or its fixes introduced. The
`docs/spec` and `docs/adr` flow-control specification surface was left alone
unless a genuine contradiction forced a change.

Targets re-reconciled:

1. Root `README.md` and root-level docs it references (`docs/arc42/concepts.md`,
   `docs/arc42/beginner-intro.md`, `docs/arc42/CONTEXT-MAP.md`).
2. `factory/` self-documentation (`factory/README.md`, `factory/docs/`).
3. `orchestrator/` self-documentation (`orchestrator/README.md`,
   `orchestrator/docs/**`, `orchestrator/docs/adr/`). `orchestrator/CONTEXT.md`
   was checked for again — it still does not exist, which matches
   `docs/arc42/CONTEXT-MAP.md`'s current (post-prior-pass) entry that links
   `orchestrator/README.md` instead.

**Method.** Rebuilt truth maps from code (`factory/scripts/`,
`factory/config/`, `factory/playbooks/*.fsm.yml`, `orchestrator/src/`,
`orchestrator/pyproject.toml`, `.pre-commit-config.yaml`) and diffed against
the prose claims in the in-scope docs. Re-verified file paths/existence,
command names and flags, behaviour claims, and architecture/ownership
statements. Re-ran the deterministic gates both to check the docs *about*
them and to confirm the documented invocation forms.

## Prior open finding — re-verified

| Finding                                                                                                                                                                                             | Status this pass | Action                                                                                                                                                                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/findings/RECON-0017.md` — pre-push full-suite test gate documented (ADR-0003 + `factory/README.md`) but never wired into `factory/config/pre-commit-config.yaml` or `.pre-commit-config.yaml` | **Still open**   | Re-verified: `grep -n 'pre-push\|stages' factory/config/pre-commit-config.yaml .pre-commit-config.yaml` returns no `pre-push`-stage entry and no `run-tests --full` entry. The code defect is unfixed. Finding left `status: open`; handed back to the implementation agent. |

## Discrepancy table (this pass)

| #   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Artifact                                            | Category | Severity | Disposition                                                                                                                                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- | -------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `factory/README.md` § Test execution hooks, point 3 said FSM entry conditions check `tests_pass` "before advancing to QA or DONE states." As-built, `tests_pass` gates the Implementation→Gate/QA transition only — neither `greenfield-development.fsm.yml` nor `bug-fix.fsm.yml` lists `tests_pass` in `DONE`'s `entry_conditions`. The "DONE" clause is a behaviour-claim drift. (The prior pass recorded this as an observation and left it; this pass corrects it.) | `factory/README.md` (Test execution hooks, point 3) | Defect   | Minor    | **Fixed** — point 3 now reads "before advancing to the QA phase," matching the FSM comments ("before advancing to QA", "before QA starts") and both playbook FSMs. |

No new code defects found this pass; no new `RECON` finding filed.

## Spec files updated

- `factory/README.md` — § Test execution hooks point 3: dropped the incorrect
  "or DONE states" clause so the phase-advance-gate description matches the
  `tests_pass` gating actually declared in `greenfield-development.fsm.yml`
  (PHASE_4_IMPLEMENTATION exit → PHASE_4_GATE; PHASE_5_QUALITY entry) and
  `bug-fix.fsm.yml` (IMPLEMENT_FIX exit → QA_VALIDATION). `DONE`'s
  `entry_conditions` do not include `tests_pass` in either FSM.

## Code defects filed

None this pass. `RECON-0017` (pre-push full-suite test gate) remains open and
is re-verified above; it is the outstanding code defect for the
implementation agent.

## Observations (not filed, not edited)

- **`docs/arc42/concepts.md` project tree** still lists
  `01_introduction_and_goals.md # ...through 12_glossary.md — the 12 arc42 chapters`, but only `05`, `06`, `08`, `09`, `12` exist on disk. This
  describes the flow-control arc42 architecture surface, explicitly excluded
  from scope, and is a known intentional partial state (`arch-lint` is
  intentionally tolerant of missing chapters). Not edited, consistent with
  the prior pass. Reconciling it means writing architecture chapters, which
  is out of scope for a documentation-reconciliation pass.
- **`factory/playbooks/greenfield-development.fsm.yml`** still declares
  `audit.output_file: .orchestrator/audit.log`, while the orchestrator
  (`orchestrator/src/agent_factory_orchestrator/cli.py`, `AUDIT_LOG = Path(".current-work/audit.log")`) and `orchestrator/README.md` both use
  `.current-work/audit.log`. The FSM's declarative `audit` block is stale
  metadata the code does not read. Out of scope (playbook/FSM artifact, not
  self-documentation prose); flagged here for a future pass, as in the prior
  report.
- **`orchestrator/docs/adr/0001`** still records "~120 lines" for the
  orchestrator's control flow; `cli.py` is now 350 lines. ADRs are historical
  decision records and are not amended for metric drift; left untouched, as
  in the prior pass.

## Verified accurate (no change this pass)

Re-confirmed against code-as-built; no edits needed:

- Root `README.md` — repo-layout claims, links to `factory/`,
  `orchestrator/`, `docs/arc42/concepts.md`, `docs/arc42/beginner-intro.md`, the
  workflow-diagram asset (`docs/assets/images/workflow-diagram.svg` exists).
- `docs/arc42/concepts.md` — phase chain, research-workflow description,
  `update-factory` mention, `factory/config/` template labelling,
  orchestrator `.fsm.yml` description. (Project tree arc42 claim excepted
  above.)
- `docs/arc42/beginner-intro.md` — all six playbook references resolve
  (`poc-spike`, `bug-fix`, `documentation-update`, `greenfield-development`,
  `brownfield-onboarding`, `feature-addition` all exist in
  `factory/playbooks/`); `INDEX.yaml` catalogue reference; two-modes framing;
  orchestrator `.fsm.yml` description.
- `docs/arc42/CONTEXT-MAP.md` — Usage Accounting (`usage/` absent, no code) and
  Factory API ("vision-stub only", `factory_api/` absent) claims accurate;
  orchestrator entry links `orchestrator/README.md` + `orchestrator/docs/adr/`
  and no longer mentions the dead `ai_tooling` term or
  `orchestrator/CONTEXT.md`.
- `factory/README.md` — `init-factory` footprint (8-step list),
  `update-factory` top-line (prior fix intact), `run-playbook`
  `AF_ORCHESTRATOR_SOURCE` / `orchestrator-v0.1.0` default source (verified
  in `factory/scripts/run-playbook`), `--cli claude|copilot` backends,
  `run-tests --staged` agent loop, framework auto-detection, ADR-0003/UC-09
  links, Pi `run_agent`/`dispatch_wave` extensions.
- `factory/docs/factory-guide.md` — agents/skills/playbooks listings, all
  six beginner/full-chain playbook links resolve, `run_agent`/`dispatch_wave`
  Pi extensions, runtime usage-capture pipeline, research validators
  (`schema-validate <artifact> <schema>` positional form;
  `policy-validate --pipeline <artifact-or-dir>...` form, both verified
  against script argparse), guardrail deny list, session logging,
  update-factory `--target`/`--source` workflow (flags verified against
  `factory/scripts/update-factory`), linting examples
  (`spec-lint --spec-dir`, `arch-lint --docs-dir`, `backlog-lint --backlog-dir`, `matrix-lint --matrix` — all flag forms verified against
  script argparse; prior fix intact).
- `orchestrator/README.md` — delegation model, `--from-state` / marker
  resume, audit-log JSON shape (fields and `action` values `done`,
  `human-gate`, `halt`, `advance`, `retry` match `cli.py`), 18 tests in
  `test_run_playbook.py` (verified by test-function count), Files tree
  (50-file test suite verified by `ls orchestrator/tests/*.py | wc -l`,
  `src/` lists `__init__.py` and `run_playbook.py`), `agent-factory-orchestrator`
  package name (verified in `pyproject.toml`), `backlog/` 6 stories,
  `orchestrator/docs/adr/0001`.
- `orchestrator/docs/05,06,09` and `orchestrator/docs/adr/0001` — consistent
  with `cli.py` (claude/copilot backends, exit-code dispatch, marker
  `.current-work/playbook-state.yml`, audit `.current-work/audit.log`,
  `run_one_step` single-function structure, `phase advance`/`phase retry`/`trigger` delegation). The `~120 lines` metric in ADR-0001 is
  historical; see Observations.

## Gates run

- `spec-lint --spec-dir docs/spec/` → 0 errors, 0 warnings, 18 info.
- `arch-lint --docs-dir docs/` → 0 errors, 2 warnings (pre-existing DSL parse).
- `backlog-lint --backlog-dir backlog/` → 0 errors, 1 warning.
- `matrix-lint --matrix config/model.conf` → 0 errors.
- `mdformat --number factory/README.md` → clean (no reformatting beyond the
  one-line edit).

## Prior findings checked

`docs/findings/RECON-0001`–`RECON-0016` reviewed; none describe the
self-documentation surface. `RECON-0017` re-verified — still open (see
table above). One new doc drift corrected; no new code defects filed.

## Commit

Correction committed as
`docs: fix tests_pass gate phrasing in factory README (RECON-0018)`.
