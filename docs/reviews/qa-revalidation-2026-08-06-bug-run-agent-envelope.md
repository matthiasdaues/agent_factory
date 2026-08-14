---
title: QA Re-validation — bug/run-agent-envelope-recovery defect fixes
review: qa-revalidation
branch: bug/run-agent-envelope-recovery
tip: 0fe8387fe65cc7953bd3d6f243f3a091dd6b37fd
base: 1e5b512875c728abe908b3edbbf08743f70c4466
merge-base: 04256d941ecba2245e01db4d2a3c42d1812cbee9
date: 2026-08-06
reviewer: qa-agent
---

# QA Re-validation — bug/run-agent-envelope-recovery defect fixes

## Scope

Repeat-pass verification of the four findings the prior QA pass filed open at
commit `1e5b512` (`FAGAN-0016`, `FAGAN-0017`, `BUG-0009`, `BUG-0010`), each
since fixed by a developer-agent. Focus is the fixes only; the branch diff
`04256d9…HEAD` is **not** re-reviewed. `BUG-0011` (dispatch-wave spawn-abort,
infra) is intentionally not fixed this pass and is left `open` and untouched.

The developer self-marked all four findings `status: resolved` at the fix
commits (`14a6d19`, `4cc1ec2`, `5cfdd35`). This pass independently confirms or
corrects each `resolved` marking by reading the fix and running the relevant
suite.

## Verdicts

| Finding    | Severity | Fix commit                                 | Verdict | Status               |
| ---------- | -------- | ------------------------------------------ | ------- | -------------------- |
| FAGAN-0016 | major    | `14a6d198af9ad2e1037b9f7dba5dfda3a49d4734` | PASS    | resolved (confirmed) |
| FAGAN-0017 | minor    | `14a6d198af9ad2e1037b9f7dba5dfda3a49d4734` | PASS    | resolved (confirmed) |
| BUG-0009   | major    | `4cc1ec2f30eac89bd59d7429d7c4455a88ff95ea` | PASS    | resolved (confirmed) |
| BUG-0010   | major    | `5cfdd351a505f3a3810547b853f0d5c785d3b45d` | PASS    | resolved (confirmed) |
| BUG-0011   | major    | —                                          | N/A     | open (intentional)   |

No new defects filed. One non-blocking **Suggestion** noted below (test
granularity for FAGAN-0016); suggestions stay in the report only per
[finding-format.md](../rulebooks/conventions/finding-format.md).

## FAGAN-0016 — commit disclosure on non-zero / no-message / cancel paths

**Verdict: PASS.** Commit `14a6d19` adds an `enrichWithChildCommits(cwd, headBefore, base)` helper that calls `childCommitsSince` and, when non-null,
spreads `freshChildCommits` + the "do not blindly re-dispatch" `note` onto the
error metadata. It is wired into exactly the two paths the finding names and
omitted from exactly the path the finding protects:

- `childResult.cancelled` → `cancellationResult(params.agent, enrichWithChildCommits(cwd, headBefore, {}))` — disclosed.
- `childResult.status !== 0 || !parsed` → `errorResult(..., enrichWithChildCommits(cwd, headBefore, { exitCode: childResult.status }))`
  — disclosed.
- `childResult.error` (spawn/process failure) →
  `errorResult(params.agent, \`failed to spawn pi: ${childResult.error}\`)`— **undisclosed**, as required (no child ran). Confirmed by reading the dispatch flow and`runPiStreamed`: the `error`field is set only in the synchronous spawn`try/catch`(child never started) or the`child.once("error")`outcome (process never produced a result); the cancel path returns before that branch and never sets`error\`.

`errorResult` and `cancellationResult` both spread `...metadata` into
`details`, so `freshChildCommits` + `note` reach the caller. `childCommitsSince`
and `gitLocalHead` are best-effort (try/catch → null), so disclosure never
throws on an error path. The existing `decoded.error` branch disclosure is
unchanged.

**Suite:** `node --experimental-strip-types --import ./envelope-loader.mjs --test ./envelope.test.ts` → **19 pass, 0 fail** (incl. the three new
`enrichWithChildCommits` cases). Run from
`factory/config/extensions/__tests__/`.

## FAGAN-0017 — prefer envelope-shaped record over rightmost sibling

**Verdict: PASS.** Commit `14a6d19` rewrites the balanced-brace last-resort
scan to collect **all** balanced records, then (1) return the first record
whose keys sort to exactly the four canonical fields
(`artifact_paths|disposition|finding_counts|next_action`; `ENVELOPE_FIELDS` is
pre-sorted, so `Object.keys(value).sort().join("|")` compares correctly), else
(2) fall back to the largest by raw-slice length. The doc comment now matches
the behaviour. This fixes the reported window: an envelope followed by a
larger non-envelope sibling now returns the envelope (verified by the new
`extractEnvelopeObject prefers envelope over larger sibling (FAGAN-0017)`
case); the reverse order and the no-envelope fall-back to the largest both
still hold (two further new cases). Structural validation in
`parseChildResultEnvelope` is unchanged — the scan only finds the object; it
does not relax the schema. The throwaway probe
`__tests__/__qa_probe.mjs` is gone; its sibling-mis-selection case is folded
into `envelope.test.ts`.

**Suite:** same envelope suite → **19 pass, 0 fail**.

## BUG-0009 — stale `_SURVEY_DESIGN` path

**Verdict: PASS.** Commit `4cc1ec2` updates `_SURVEY_DESIGN` to
`_ROOT / "docs" / "proposals" / "implemented" / "research-survey-mode.md"`,
matching where the branch moved the design doc. The old
`factory/docs/design/research-survey-mode.md` is absent; the new path exists.
`_FACTORY_GUIDE` (line 12) is unchanged and still resolves.

**Suite:** `uvx pytest orchestrator/tests/test_research_survey_playbook.py -v`
→ **8 passed, 0 failed**, incl.
`test_FAGAN0009_design_records_the_implemented_schema_boundary` (no
`FileNotFoundError`). (`uvx pytest` is the orchestrator README's documented
runner; `run-tests` detects no framework at this repo root — a known
monorepo limitation, ADR-0003 — and the bare `pytest`/`python -m pytest`
commands are guardrailed per BR-024.)

## BUG-0010 — drain e2e reads verbatim filename

**Verdict: PASS.** Commit `5cfdd35` changes the drain-branch read from
`observed / f"{session}.jsonl"` to `observed / f"{cli}_{session}.jsonl"`,
tracking ADR-0009's composite `<cli>_<session_id>` capture key. Verified the
e2e is genuine: `_gate_capture` runs the real `usage-capture`, whose
`session_path` writes `usage_dir / f"{_session_key(session_id)}.jsonl"` with
`_session_key = f"{filesystem_key(cli)}_{filesystem_key(session_id)}"`. For the
test's safe identifiers (`claude-code`, `copilot`, `*-removal-race`)
`filesystem_key` is the identity, so the capture's written name equals the
test's read name `f"{cli}_{session}.jsonl"`. The cancel param still asserts
`not observed.exists()` and never reads a file, so it is unaffected.

**Suite:** `uvx pytest "…::test_FAGAN0005_native_hook_removal_reaches_selected_terminal_state" -v` →
**3 passed**: `[claude-code-drain]`, `[codex-cancel]`, `[copilot-drain]`. Both
drain params pass. Running both full files together: 15 passed.

## BUG-0011 — dispatch-wave spawn abort (not in scope)

Left `open` and untouched, per instruction. `spawnPi` in
`factory/config/extensions/dispatch-wave.ts` still injects `ctx.signal` into
`spawn()` options, aborting children as "The operation was aborted"; the
`runPiStreamed` sibling correctly omits it. No change this pass.

## Suggestion (non-blocking, not filed)

`FAGAN-0016`'s added tests exercise `enrichWithChildCommits` in isolation
(the disclosure helper), not the `status !== 0 || !parsed` and `cancelled`
branches end-to-end. The harness stubs the pi API and cannot spawn a real
child, so a true "child commits then exits non-zero → result discloses"
integration assertion is not feasible in `envelope.test.ts`; the wiring is
verified here by reading the dispatch flow. A future branch could export the
dispatch handler (or inject a `runPiStreamed` seam) and assert the branch
metadata, so a refactor that drops the `enrichWithChildCommits` call would fail
a test rather than silently regress. Minor; not a defect in the fix.

## Completion

All four in-scope fixes verified; each `resolved` status confirmed. No new
defects filed. BUG-0011 remains open. Per the QA→Implementation handoff, with
zero open in-scope findings, the branch is QA-clean for its scoped fixes
(BUG-0011 excepted).
