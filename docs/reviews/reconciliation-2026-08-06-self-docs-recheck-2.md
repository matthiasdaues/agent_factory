---
title: Reconciliation — Factory Self-Documentation (Second Repeat Pass)
date: 2026-08-06
scope: factory self-documentation (root README + referenced docs, factory/, orchestrator/)
source: reconcile
baseline: 8abf5cd (chore/reconcile-docs checkout, post RECON-0018)
reviewer: reconciliation-agent (separate session)
---

# Reconciliation Report — Factory Self-Documentation (Second Repeat Pass)

**Scope.** A second repeat-pass reconciliation of the Factory's *own*
self-documentation against the code-as-built, run fresh per
[review-loop-discipline.md](../../factory/rulebooks/conventions/review-loop-discipline.md):
re-verify every open `RECON` finding *and* rebuild the truth-map diff from
scratch to catch drift a prior pass or its fixes introduced. The
`docs/spec` and `docs/adr` flow-control specification surface was left alone
unless a genuine contradiction forced a change — none did this pass.

Targets reconciled:

1. Root `README.md` and root-level docs it references (`docs/concepts.md`,
   `docs/beginner-intro.md`, `docs/CONTEXT-MAP.md`).
2. `factory/` self-documentation (`factory/README.md`, `factory/docs/`).
3. `orchestrator/` self-documentation (`orchestrator/README.md`,
   `orchestrator/docs/**`, `orchestrator/docs/adr/`). `orchestrator/CONTEXT.md`
   was checked for again — it still does not exist, which matches
   `docs/CONTEXT-MAP.md`'s entry that links `orchestrator/README.md` instead.

**Method.** Rebuilt truth maps from code
(`factory/scripts/run-playbook`, `run-tests`, `schema-validate`,
`policy-validate`, `spec-lint`, `arch-lint`, `backlog-lint`, `matrix-lint`,
`update-factory`; `factory/config/pre-commit-config.yaml`;
`.pre-commit-config.yaml`; `orchestrator/src/agent_factory_orchestrator/cli.py`;
`orchestrator/pyproject.toml`; `factory/playbooks/*.md`) and diffed against
the prose claims in the in-scope docs. Re-verified file paths/existence,
command names and flags, behaviour claims, and architecture/ownership
statements. Re-ran the deterministic gates both to check the docs *about*
them and to confirm the documented invocation forms.

## Prior open finding — re-verified

| Finding                                                                                                                                                                                                                            | Status this pass | Action                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/findings/RECON-0017.md` — pre-push full-suite test gate documented (ADR-0003 + `factory/README.md` § Test execution hooks point 2) but never wired into `factory/config/pre-commit-config.yaml` or `.pre-commit-config.yaml` | **Still open**   | Re-verified: `grep -rn 'pre-push' .pre-commit-config.yaml factory/config/` returns nothing; no `stages: [pre-push]` entry and no `run-tests --full` entry exist in either config. `.pre-commit-config.yaml` has only a `pre-commit`-stage `run-tests --changed-only` hook. The code defect is unfixed. Finding left `status: open`; handed back to the implementation agent. |

## Discrepancy table (this pass)

No discrepancies found this pass. Every in-scope doc claim was re-verified
against code-as-built and matched.

## Spec files updated

None this pass. The in-scope self-documentation is accurate against the
code-as-built; no tracked edits required.

## Code defects filed

None this pass. `RECON-0017` (pre-push full-suite test gate) remains the one
outstanding code defect and is re-verified above; it is handed back to the
implementation agent.

## Observations (not filed, not edited)

Carried forward from the prior pass; each remains accurate and out of scope
for a documentation-reconciliation pass:

- **`docs/concepts.md` project tree** still lists
  `01_introduction_and_goals.md # ...through 12_glossary.md — the 12 arc42 chapters`, but only some arc42 chapters exist on disk. This describes
  the flow-control arc42 architecture surface, explicitly excluded from
  scope, and is a known intentional partial state (`arch-lint` is
  intentionally tolerant of missing chapters). Not edited. Reconciling it
  means writing architecture chapters, which is out of scope here.
- **`factory/playbooks/greenfield-development.fsm.yml`** still declares
  `audit.output_file: .orchestrator/audit.log`, while the orchestrator
  (`cli.py`, `AUDIT_LOG = Path(".agent-factory/audit.log")`) and
  `orchestrator/README.md` both use `.agent-factory/audit.log`. The FSM's
  declarative `audit` block is stale metadata the code does not read. Out of
  scope (playbook/FSM artifact, not self-documentation prose); flagged here
  for a future pass.
- **`orchestrator/docs/adr/0001`** still records "~120 lines" for the
  orchestrator's control flow; `cli.py` is now 350 lines. ADRs are historical
  decision records and are not amended for metric drift; left untouched.

## Verified accurate (no change this pass)

Re-confirmed against code-as-built; no edits needed:

- Root `README.md` — repo-layout claims, links to `factory/`,
  `orchestrator/`, `docs/concepts.md`, `docs/beginner-intro.md`,
  `docs/README.md`, the workflow-diagram asset
  (`docs/assets/images/workflow-diagram.svg` exists).
- `docs/concepts.md` — phase chain, research-workflow description,
  `update-factory` mention, `factory/config/` template labelling,
  orchestrator `.fsm.yml` description, project directory tree structure.
  (Project tree arc42 "01…through 12" claim excepted above.)
- `docs/beginner-intro.md` — all six playbook references resolve
  (`poc-spike`, `bug-fix`, `documentation-update`, `greenfield-development`,
  `brownfield-onboarding`, `feature-addition` all exist in
  `factory/playbooks/`); `INDEX.yaml` catalogue reference; two-modes framing;
  orchestrator `.fsm.yml` description.
- `docs/CONTEXT-MAP.md` — Usage Accounting (`usage/` absent, no code) and
  Factory API ("vision-stub only", `factory_api/` absent) claims accurate;
  orchestrator entry links `orchestrator/README.md` + `orchestrator/docs/adr/`
  and does not mention the absent `orchestrator/CONTEXT.md`.
- `factory/README.md` — `init-factory` footprint (8-step list),
  `update-factory` top-line, `run-playbook` `AF_ORCHESTRATOR_SOURCE` /
  `orchestrator-v0.1.0` default source (verified in
  `factory/scripts/run-playbook`: `DEFAULT_SOURCE` pinned to
  `git+...@orchestrator-v0.1.0#subdirectory=orchestrator`; console script
  `agent-factory-orchestrate` matches `pyproject.toml`
  `[project.scripts]`), `--cli claude|copilot` backends (verified in
  `cli.py` argparse, default `claude`), `run-tests --staged` agent loop
  (verified: `--staged` is `dest=mode`, default `--full`),
  framework auto-detection, ADR-0003/UC-09 links, Pi `run_agent` /
  `dispatch_wave` extensions.
- `factory/README.md` § Test execution hooks — point 3 ("before advancing to
  the QA phase") matches both playbook FSMs; point 2 (pre-push full suite)
  restates ADR-0003 correctly and is the subject of open `RECON-0017`.
- `factory/docs/factory-guide.md` — agents/skills/playbooks listings, all
  eleven `playbooks/*.md` links resolve, `run_agent`/`dispatch_wave` Pi
  extensions, runtime usage-capture pipeline, research validators
  (`schema-validate <artifact-file> <schema-file>` positional form verified
  against `schema-validate` `main`: `len(argv) != 2` two-positional contract;
  `policy-validate --pipeline <artifact-or-dir>...` form verified against
  `policy-validate` argparse: `paths` `nargs="+"`, `--pipeline`
  `store_true`), guardrail deny list, session logging, update-factory
  `--target`/`--source` workflow (flags verified against
  `factory/scripts/update-factory` argparse), linting examples
  (`spec-lint --spec-dir`, `arch-lint --docs-dir`, `backlog-lint --backlog-dir`,
  `matrix-lint --matrix` — all flag forms verified against script argparse).
- `orchestrator/README.md` — delegation model, `--from-state` / marker
  resume (verified in `cli.py`: `MARKER_PATH = .agent-factory/playbook-state.yml`), audit-log JSON shape (fields and
  `action` values `done`, `human-gate`, `halt`, `advance`, `retry` all
  present in `cli.py`), 18 tests in `test_run_playbook.py` (verified by
  test-function count), Files tree (50-file test suite verified by
  `ls orchestrator/tests/*.py | wc -l`; `src/` lists `__init__.py` and
  `cli.py`; `run_playbook.py` compatibility launcher present),
  `agent-factory-orchestrator` package name (verified in `pyproject.toml`),
  `backlog/` 6 stories, `orchestrator/docs/adr/0001` reference.
- `orchestrator/docs/05,06,09` and `orchestrator/docs/adr/0001` — consistent
  with `cli.py` (claude/copilot backends, exit-code dispatch, marker
  `.agent-factory/playbook-state.yml`, audit `.agent-factory/audit.log`,
  single-function `run_one_step` structure, `phase advance` / `phase retry` /
  `trigger` delegation). The `~120 lines` metric in ADR-0001 is historical;
  see Observations.

## Gates run

- `spec-lint --spec-dir docs/spec/` → 0 errors, 0 warnings, 18 info (exit 0).
- `arch-lint --docs-dir docs/` → 0 errors, 2 warnings (pre-existing DSL
  parse, exit 0).
- `backlog-lint --backlog-dir backlog/` → 0 errors, 1 warning (exit 0).
- `matrix-lint --matrix config/model.conf` → 0 errors, 0 warnings (exit 0).
- `mdformat --number --check` over all in-scope docs (less the absent
  `orchestrator/CONTEXT.md`) → clean (exit 0).

## Prior findings checked

`docs/findings/RECON-0001`–`RECON-0016` reviewed; none describe the
self-documentation surface (all `status: resolved`). `RECON-0017`
re-verified — still open (see table above). No new `RECON` finding filed
this pass; no new code defects.

## Commit

Report committed as
`docs: re-verify factory self-doc reconciliation pass (RECON-0017)`.
