---
title: Bug Hunt — BUG-0008 envelope recovery branch
review: bug-hunt
branch: bug/run-agent-envelope-recovery
tip: 477518d3fecae58b3249393c52abf0397318df74
merge-base: 04256d941ecba2245e01db4d2a3c42d1812cbee9
date: 2026-08-06
reviewer: qa-agent
---

# Bug Hunt — BUG-0008 envelope recovery branch

## Scope

Hunt over the full diff `04256d9…HEAD`: run the available test suites, break the
BUG-0008 envelope parser with edge cases, classify every failure as
branch-regression vs pre-existing vs environmental, and file confirmed bugs.
Retest against the merge-base in a throwaway worktree to distinguish
regressions from pre-existing/environmental failures.

## Cycle

1. **Hunt.** Ran the envelope suite (13 passed) and a 16-case parser probe
   (`factory/config/extensions/__tests__/__qa_probe.mjs`) covering unbalanced
   braces, multiple valid objects, braces/escapes inside strings, UTF-8/emoji,
   CRLF, unclosed fences, and every field-validation branch. Ran the full
   orchestrator suite (excluding two Python 3.11-only modules that cannot
   import under the local 3.10 venv): **579 passed, 7 failed**.
2. **Classify (baseline comparison).** Re-ran the failing tests at the merge-base
   `04256d9` in a throwaway worktree (`/tmp/qabase`, removed after).
3. **File.** Filed the two confirmed branch regressions as BUG-0009 and
   BUG-0010. Per the QA→Implementation handoff, fixes are deferred to the
   Implementation Agent (author/reviewer independence: QA is the reviewer here);
   findings are `status: open`.

## Failure classification (7)

| #   | Test                                                                                              | Verdict                                                                                                                                                                           | Filed            |
| --- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| 1   | `test_research_survey_playbook::test_FAGAN0009_design_records_the_implemented_schema_boundary`    | **Branch regression** — `_SURVEY_DESIGN` path stale after the branch moved the doc to `docs/proposals/implemented/` (commits `5f92617`/`e620890`). Passes at base, fails at HEAD. | BUG-0009 (Major) |
| 2   | `test_usage_capture_native_lifecycle_e2e::…[claude-code-drain]`                                   | **Branch regression** — drain branch reads verbatim `<session>.jsonl`; capture now writes `<cli>_<session>.jsonl` (ADR-0009). Passes at base, fails at HEAD.                      | BUG-0010 (Major) |
| 3   | `test_usage_capture_native_lifecycle_e2e::…[copilot-drain]`                                       | **Branch regression** — same as #2.                                                                                                                                               | BUG-0010         |
| 4   | `test_usage_capture_pi_e2e::test_human_shutdown_is_idempotent…`                                   | **Environmental (pre-existing)** — `shutdown is not a function`; pi 0.84.0 installed vs ADR-0004-pinned 0.80.8 `session_shutdown` shape. Fails at base too.                       | —                |
| 5   | `test_usage_capture_pi_e2e::test_linked_worktree_capture_uses_primary_checkout`                   | **Environmental (pre-existing)** — same pi `shutdown` skew. Fails at base too.                                                                                                    | —                |
| 6   | `test_usage_capture_pi_e2e::test_BUG_0005_UC_10_human_shutdown_captures_full_session_file_events` | **Environmental** — new test on this branch exercising the same `session_shutdown` capture shape that pi 0.84.0 does not expose. Likely passes under the pinned pi 0.80.8.        | —                |
| 7   | `test_usage_capture_pi_e2e::test_BUG_0006_UC_10_root_record_uses_model_conf_canonical_id`         | **Environmental** — same as #6.                                                                                                                                                   | —                |

The two collection errors (`test_generate_codex_agents.py`,
`test_init_factory_codex.py`) are environmental: `import tomllib` requires
Python 3.11+; the local venv is 3.10. Not branch defects.

## Notes

- 3 of the 7 failures are confirmed branch regressions (filed as 2 BUG
  findings; BUG-0010 covers two drain params). 4 are environmental — the pi
  `session_shutdown` extension-handler shape the e2e tests assume is not how pi
  0.84.0 exposes it; ADR-0004 pins 0.80.8. Recommend the CI/verified
  environment run the suite under the pinned pi 0.80.8 to confirm #4–#7 are
  green there and to harden the new pi-e2e tests against the installed version.
- The probe artifact `factory/config/extensions/__tests__/__qa_probe.mjs` is a
  throwaway QA instrument; remove it or fold its cases into `envelope.test.ts`
  (see FAGAN-0018).
- FAGAN-0016 (the BUG-0008 disclosure not extending to non-zero/no-message/cancel
  paths) was found by inspection, not by a failing test; it is recorded in the
  Fagan review, not here.

## Verification Evidence

- Envelope suite: 13 passed.
- Probe: 16/16 behaved as predicted; sibling mis-selection reproduced (→ FAGAN-0017).
- Orchestrator suite at HEAD: 579 passed, 7 failed (177 s).
- Baseline at `04256d9`: the FAGAN0009 and the 3 native_lifecycle params pass;
  the 2 `shutdown` pi-e2e tests fail (pre-existing skew).
- `run-tests --full` framework detection: no root marker in this repo → exit 2
  here; consumer repos with a root marker unaffected (FAGAN-0019).
