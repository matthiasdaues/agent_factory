---
title: Fagan Review — update-factory
date: 2026-08-05
base: dabb4a90ceb2025c5752f6be00461528ffcebe5b6
head: 47628e3efd7a1e93ec959502576f782c1875d7b6
disposition: fail
---

# Fagan Review — update-factory

## Scope

Inspected the full diff of `feat/update-factory` (tip `47628e3`) against `dev`
(`dabb4a9`): eight files, +498/-5.

- `factory/scripts/update-factory` (new, 172 lines) — the remove-and-reinstall
  refresh script.
- `factory/scripts/init-factory` — records `factory_source` in the install
  manifest and updates two docstring/log strings.
- `orchestrator/tests/test_update_factory.py` (new, 11 tests).
- `docs/adr/0010-refresh-installed-factory-by-remove-and-reinstall.md` (new
  ADR) and `docs/09_architecture_decisions.md` index + summary.
- `docs/concepts.md`, `docs/spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md`,
  `factory/docs/factory-guide.md` — documentation updates.

`docs/CONTEXT.md` does not exist, so there was no project glossary against which
to check terminology drift. The relevant spec is
[UC-08](../spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md); the
design rationale is in [ADR-0010](../adr/0010-refresh-installed-factory-by-remove-and-reinstall.md).

Every changed file was inspected for correctness, Clean Architecture, SOLID,
maintainability, consistency, and YAGNI. No unused abstraction, premature
optimization, or speculative generality was found: update-factory is a thin
orchestrator that deliberately reuses init-factory's wiring rather than
re-implementing it.

## Correctness

- **Remove-and-reinstall logic.** update-factory resolves `--source` from the
  flag or the manifest's `factory_source`, validates that `source/factory/`
  is a directory, refuses a non-directory `target/factory`, removes
  `target/factory/`, then delegates to the sourced init-factory. The flow is
  correct and matches ADR-0010.
- **Source resolution.** init-factory now sets
  `install["factory_source"] = str(source_root)` and `write_manifest` emits
  it; `load_prior_manifest` does not copy the field back, but `main` always
  sets it fresh, so an update re-records the new source. Correct.
- **`.agent-factory/` preservation (code).** update-factory only `rmtree`s
  `target/factory/`. The re-run init's `initialize_usage_lifecycle` is
  create-if-absent plus permission repair, and `provision_usage_runtime` swaps
  the `usage-runtime` venv (not `usage/` transcripts). So usage data survives
  in the production path — verified by reading init-factory, not by the suite
  (see FAGAN-0012).
- **`factory_source` rot.** The recorded path is absolute and can go stale if
  the checkout is moved; `--source` is the documented override. Matches the
  ADR consequence.

## Clean Architecture / SOLID

- update-factory is a single-responsibility orchestrator; `_run_init` is a
  clean, monkeypatchable delegation seam. Dependency direction is correct:
  update depends on init's contract, not its internals. No SOLID violation
  found.

## Maintainability

- Naming is clear and cyclomatic complexity is low. Test coverage of
  update-factory's own contract (validation, source resolution, removal,
  delegation boundary, preservation-via-stub, error cases) is good. The two
  maintainability gaps are filed as FAGAN-0012 and FAGAN-0013: the central
  preservation guarantee and the real subprocess seam are not exercised
  end-to-end.

## Consistency

- The script header (What/When/By, Usage, Exit code) matches init-factory and
  remove-factory. The test file reuses the `SourceFileLoader` loading pattern
  from `test_remove_factory.py`. Two minor deviations are filed: the
  failure-path recovery gap (FAGAN-0014) and the corrupt-manifest message
  inconsistency with remove-factory (FAGAN-0015).

## Findings

| Finding                                                                                                            | Artifact                                        | Category   | Severity |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ---------- | -------- |
| [FAGAN-0012](../findings/FAGAN-0012.md) Preservation guarantee asserted by a test that bypasses the real reinstall | `orchestrator/tests/test_update_factory.py:191` | Defect     | Major    |
| [FAGAN-0013](../findings/FAGAN-0013.md) Real `_run_init` subprocess delegation seam is never exercised             | `orchestrator/tests/test_update_factory.py:46`  | Suggestion | Minor    |
| [FAGAN-0014](../findings/FAGAN-0014.md) Failure path leaves the project without a factory/ and no recovery note    | `factory/scripts/update-factory:140`            | Suggestion | Minor    |
| [FAGAN-0015](../findings/FAGAN-0015.md) Corrupt manifest reported as "no manifest found"                           | `factory/scripts/update-factory:53`             | Suggestion | Minor    |

## Verification

- `python3 -m pytest orchestrator/tests/test_update_factory.py -q`: 11 passed.
- Code-path analysis of init-factory (`copy_factory`, `load_prior_manifest`,
  `write_manifest`, `provision_usage_runtime`, `initialize_usage_lifecycle`,
  `ensure_symlink`) confirms the remove-and-reinstall flow and `.agent-factory/`
  preservation in the production path.

## Disposition

Fail. FAGAN-0012 (Major defect in the test artifact) must return to the
Implementation Agent: add an update round-trip test that drives the real
init-factory (with only its networked steps stubbed) and asserts
`.agent-factory/` usage state genuinely survives. The three Minor suggestions
(FAGAN-0013 through FAGAN-0015) can be addressed in the same pass. Re-submit
for QA once FAGAN-0012 is resolved.
