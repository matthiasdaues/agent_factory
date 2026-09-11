---
title: Consult Review — Deterministic Factory Engine Proposal
date: 2026-09-11
reviewer: proposal-review-agent
reviewed_commit: ef844121a41212b9256183673c4f13e42266575c
proposal: docs/proposals/deterministic-factory-engine.md
disposition: findings
stance: consult (draft proposal)
---

# Consult Review — Deterministic Factory Engine

**Reviewed commit:** `ef844121a41212b9256183673c4f13e42266575c`
**Proposal status at review:** `draft`
**Stance:** consultative — observations and suggestions to strengthen the proposal before it moves to `open`.

## Overall Assessment

The proposal is well-structured and unusually thorough for a draft. The motivation is grounded in concrete codebase evidence (line counts, drift inventory, test coverage gaps). The design decomposes cleanly into ordered steps with explicit entry conditions. The scope boundary between first-release and deferred work is sharp, with entry conditions that prevent premature extraction. ADR-0002 alignment is correctly preserved.

The proposal is close to decision-complete. Four areas need attention before it can support story decomposition without re-deriving the design.

## Filed Findings (Major)

| ID                                    | Severity | Artifact             | Summary                                                       |
| ------------------------------------- | -------- | -------------------- | ------------------------------------------------------------- |
| [PROP-0021](../findings/PROP-0021.md) | major    | estimate frontmatter | Decomposition basis with all-unknown ranges is contradictory  |
| [PROP-0022](../findings/PROP-0022.md) | major    | Design section 2     | 23 existing in-process tests have no specified migration path |
| [PROP-0023](../findings/PROP-0023.md) | major    | Design section 3     | `assess_staged_paths` FlowResult semantics undefined          |
| [PROP-0024](../findings/PROP-0024.md) | major    | Design section 3     | `StateMachine` model omits per-state `outputs` globs          |

## Additional Observations (Minor — Not Filed)

### 1. `engine/__init__.py` contents unspecified

The proposal lists `packages/factory/engine/__init__.py` as a boundary file but does not describe its contents. If it is an empty package marker, say so. If it re-exports from `flow_control`, specify what. A Planning agent will need to know whether this file has implementation work or is boilerplate.

### 2. init-factory listed as boundary file but not modified

`packages/factory/scripts/init-factory` appears in `impact.boundaries` and is exercised by the smoke test, but the proposal describes no changes to it. The file copies `packages/factory/` wholesale, so `engine/` is included automatically. Clarify in the boundary list or a footnote that this file is test-exercised-only, not modified.

### 3. Boundary test could enforce stdlib-only imports

The AST boundary test checks that engine does not import from `scripts`, `config`, or other Factory areas. The Core Principles also state that `engine/flow_control` depends only on the Python standard library. The test could additionally fail on third-party imports (anything not in `sys.stdlib_module_names` on 3.10+). This is a minor hardening opportunity, not a gap.

### 4. `FlowProblem` mirrors `Finding` — note the correspondence

The proposed `FlowProblem` (code, severity, artifact, message) is field-for-field identical to transition-lint's `Finding` dataclass. This correspondence should be noted in the design so an implementer knows the mapping is intentional, not coincidental. The adapter's `Finding` output format (the `line()` method, JSON serialization) remains adapter-owned.

### 5. Rollback granularity could be sharper

The failure/rollback section says "revert the adapter redirection" if the smoke test fails. Since the design redirects one adapter at a time (step 4), specify whether a smoke-test failure reverts both adapters or only the most recently redirected one.

### 6. `conftest.py` sys.path side effect is safe but wide

The `sys.path.insert(0, str(SCRIPTS_DIR))` in conftest.py affects all 411 in-process test loads, not just the two scripts in scope. Verified that `_session_log.py` exists in tracked source at `packages/factory/scripts/_session_log.py`, so transitive imports will resolve correctly. No action needed, but worth noting that this change has test-suite-wide reach.

### 7. Subprocess characterization test isolation

The proposal specifies subprocess tests for both adapters but does not mention how they avoid interference with the real repository's `.current-work/playbook-state.yml` marker. The existing `test_transition_lint.py` uses `tmp_path` fixtures for isolation. The new subprocess tests should use `--repo-root` and `--marker` to point at temporary directories, which the CLI already supports. Worth noting explicitly to prevent a Planning agent from generating tests that write to the real marker.

## Strengths Worth Preserving

- **Characterization-before-extraction** principle prevents premature sharing of similar-looking code.
- **Entry conditions on later extractions** (table in Design section 9) prevent scope creep across proposals.
- **Dead-command cleanup separated** (section 10) keeps the structural change clean.
- **Guiding Rule** is a strong one-sentence decision filter.
- **Demonstration section** makes reviewer verification concrete and implementation-independent.

## Recommendation

Address the four filed findings. The estimate gap (PROP-0021) is the quickest to resolve — even rough ranges help Planning estimate story points. The test migration path (PROP-0022) and FlowResult semantics (PROP-0023, PROP-0024) require design decisions that affect story decomposition. Once resolved, this proposal is ready for `open` status and adversarial review.
