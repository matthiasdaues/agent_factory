---
title: Fagan Code Inspection — BUG-0008 envelope recovery + ST-0073 pre-push gate
review: fagan-review
branch: bug/run-agent-envelope-recovery
tip: 477518d3fecae58b3249393c52abf0397318df74
merge-base: 04256d941ecba2245e01db4d2a3c42d1812cbee9
date: 2026-08-06
reviewer: qa-agent
---

# Fagan Code Inspection — BUG-0008 envelope recovery + ST-0073 pre-push gate

## Scope

Primary: the BUG-0008 fix in `factory/config/extensions/run-agent.ts` (tip
commit `477518d`, +151 lines) — `extractEnvelopeObject`, the unchanged strict
`parseChildResultEnvelope` validation, `gitLocalHead` / `childCommitsSince`
commit disclosure, and `factory/config/extensions/__tests__/envelope.test.ts`
(13 cases). Secondary: ST-0073 pre-push gate —
`factory/config/pre-commit-config.yaml`, `factory/scripts/init-factory`
(`pre_commit_install` hook-type install), and
`orchestrator/tests/test_init_factory_prepush_hook.py`. Verified against
`docs/findings/BUG-0008.md`, UC-10, BR-040, and ADR-0004.

Five focus areas: Correctness, Clean Architecture, SOLID, Maintainability,
Consistency.

## Summary

The BUG-0008 fix achieves its stated goal for the parse-failure case and does
not relax the envelope schema. `extractEnvelopeObject` (whole message → fenced
blocks → balanced-brace scan) correctly recovers bare/fenced/prose-wrapped
envelopes; `parseChildResultEnvelope`'s structural validation (exactly four
canonical fields, disposition, severity counts, artifact paths, one-to-three
sentence `next_action`) is byte-identical to the pre-fix version, so malformed
objects are still rejected — confirmed by a 13-case probe covering the
validation branches. Child-commit disclosure (`gitLocalHead` before dispatch,
`childCommitsSince` on decode error) is correct and safe across detached HEAD
and repo-absent cases, and does not mask genuine spawn/status failures (BR-040
preserved). Two defects stand: the disclosure is not extended to adjacent
failure paths (FAGAN-0016, Major), and the balanced-brace scan's "largest"
heuristic is really "rightmost closing brace" and can discard a valid leading
envelope (FAGAN-0017, Minor). ST-0073 is correctly wired and tested.

## Finding table

| Finding                                                                                                                                                                                                                                                                                                                                                                                                                | Artifact                                                         | Category   | Severity |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ---------- | -------- |
| [FAGAN-0016] BUG-0008 commit disclosure is not applied to non-zero-exit, no-message, or cancel paths; extend `childCommitsSince` to those branches.                                                                                                                                                                                                                                                                    | factory/config/extensions/run-agent.ts:160                       | Defect     | Major    |
| [FAGAN-0017] `extractEnvelopeObject` keeps the rightmost record, not the largest; a valid leading envelope followed by a larger sibling is discarded — prefer an envelope-shaped record or correct the comment + add a regression test.                                                                                                                                                                                | factory/config/extensions/run-agent.ts:336                       | Defect     | Minor    |
| [FAGAN-0018] `envelope.test.ts` (13 cases) covers happy paths + one field-validation case + git helpers, but skips the recovery heuristic's riskiest edges: unbalanced braces, multiple *valid* objects (sibling mis-selection), UTF-8/emoji, CRLF, and the field-validation branches (bad disposition, non-integer/negative counts, duplicate/empty paths, 4-sentence / unpunctuated `next_action`). Add these cases. | factory/config/extensions/__tests__/envelope.test.ts             | Suggestion | Minor    |
| [FAGAN-0019] `run-tests --full` detects a framework by a *repo-root* marker (`pyproject.toml`/`package.json`/…). The factory's own repo has no root marker (tests live in `orchestrator/`), so the ST-0073 gate exits 2 ("no framework detected") and is non-functional *here*; consumer repos with a root marker are unaffected. Pre-existing `run-tests` limitation, not a ST-0073 wiring defect.                    | factory/scripts/run-tests; factory/config/pre-commit-config.yaml | Question   | Minor    |

Filed findings: FAGAN-0016 (Major), FAGAN-0017 (Minor). FAGAN-0018 and FAGAN-0019
are Minor/Suggestion and stay in this report per
[finding-format.md § When to file](../rulebooks/conventions/finding-format.md#when-to-file).

## Focus-area notes

- **Correctness.** Recovery order is sound and the schema is unchanged (tip
  diff swaps only the top `JSON.parse(text.trim())` → `extractEnvelopeObject`;
  every validation branch is identical). The balanced-brace scan's string and
  escape handling is correct: braces/quotes inside strings do not break parsing
  (probe cases 2/2b), and unbalanced braces yield `undefined` → error (cases
  1/1b/1c) with no false recovery. Defect: rightmost-vs-largest selection
  (FAGAN-0017).
- **Clean Architecture / SOLID.** The pure parser functions are exported and
  unit-tested without spawning `pi` (stub loader); `dispatch-wave.ts` reuses
  the same `parseChildResultEnvelope` / `validateChildResultArtifacts`, so the
  fix benefits both invocation paths with one implementation (DRY, SRP).
  Disclosure is transport metadata on the error result, outside the four-field
  envelope — consistent with report-format § Child-result envelope.
- **Maintainability.** `gitLocalHead` / `childCommitsSince` are best-effort
  (`null` on any failure, never a hard gate), matching the BUG-0008 "disclosure,
  not a gate" posture. Comment nit: the `extractEnvelopeObject` JSDoc has a
  stray `)` in "2. each fenced code block)".
- **Consistency.** ST-0073's hook uses the `agent_factory_hook-` removal-key
  prefix, `stages: [pre-push]`, `pass_filenames: false`, `always_run: true`, and
  a fixed `entry` string — matching UC-09/BR-026. `init-factory` now installs
  both `pre-commit` and `pre-push` hook types; `test_init_factory_prepush_hook`
  asserts the exact `uvx pre-commit install --hook-type …` argv, propagation,
  and idempotence. All three prepush tests pass.

## Verification Evidence

- Envelope suite: `node --experimental-strip-types --import ./__tests__/envelope-loader.mjs --test ./__tests__/envelope.test.ts` → 13 passed.
- Probe (`__qa_probe.mjs`, 16 cases): unbalanced braces → error; braces/quotes
  in strings → parsed; sibling mis-selection reproduced; emoji/CRLF/unclosed-fence/nested → correct; field validation (4 sentences, no terminal punctuation, empty counts, duplicate paths, extra field, bad disposition) → all rejected.
- BUG-0008 validation-body unchanged: confirmed via `git show 477518d -- factory/config/extensions/run-agent.ts` — only the `JSON.parse` → `extractEnvelopeObject` swap; the four-field/disposition/counts/paths/next_action checks are identical.
- ST-0073: `uv run pytest tests/test_init_factory_prepush_hook.py tests/test_child_result_envelope.py -q` → 10 passed.
- Probe artifact `factory/config/extensions/__tests__/__qa_probe.mjs` is a throwaway QA instrument, not a tracked test; remove it or fold its cases into `envelope.test.ts` (FAGAN-0018).
