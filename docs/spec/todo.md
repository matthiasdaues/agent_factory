# Todo

## T-0001 — openwebui.ts: API key typed as slash-command argument

- status: resolved
- source: fagan-review (docs/reviews/fagan-review-2026-08-19-openwebui.md), answered 2026-08-19 (repeat pass)

`/register <name> <baseUrl> [apiKey]` takes the key as a typed command argument (openwebui.ts:347–367, external target). Author-absent question: confirm the typed command line containing the key is excluded from pi's session transcripts and command history. If it is persisted anywhere, key entry should move to a prompt-based flow. Resolve by checking pi's session persistence or asking the author.

**Resolution:** answered by the author on the 2026-08-19 repeat pass. The positional `apiKey` is now optional; omitting it prompts via `ctx.ui.input()` (verified to exist, `dist/core/extensions/types.d.ts:74`), with a headless guard (`!ctx.hasUI` → usage error). The header recommends the prompt path. The positional form remains available as an accepted risk; its transcript exposure inside pi was not independently confirmed.

## T-0002 — openwebui.ts: re-register drops the selected model

- status: resolved
- source: fagan-review (docs/reviews/fagan-review-2026-08-19-openwebui.md), answered 2026-08-19 (repeat pass)

`/register` unregisters the provider, re-discovers, and re-registers (openwebui.ts:281–283, external target). Author-absent question: what is the intended behavior when the session's currently selected model disappears from the new model list? Resolve by confirming pi's behavior on provider model-list shrink (graceful fallback vs. stuck selection) and documenting it in the extension header.

**Resolution:** answered by the author on the 2026-08-19 repeat pass. `/register` now checks `ctx.model` after re-registration and warns when the currently selected model is no longer offered: "pick a new one with /model". The behavior is documented in the extension header.

## T-0003 — Mechanized dispatch: cancellation semantics during a running step

- status: resolved
- source: root-cause cross-reference (RC-1 from [root-cause-2026-08-21-implementation-baseline-failures.md](../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

The step manifest and guard design in [mechanized-dispatch.md](supplementary_specs/mechanized-dispatch.md) assumes a clean agent lifecycle (manifest written, agent runs, manifest removed). Agent death without cleanup is covered (`dispatch clear-manifest --force`), but signal and cancellation semantics during a running step — what happens if the parent dispatcher is killed, the user sends SIGINT, or the subagent times out mid-write — are not specified. The QA strategy has no cancellation test for dispatch subcommands.

**Action:** specify cancellation semantics in the dispatch spec and add at least one cancellation scenario to the QA strategy's integration layer.

**Resolution:** addressed by adding the Interruption Safety cross-cutting invariant to the spec. Every dispatch subcommand must either complete atomically or leave the ledger in a state that Subcommand Idempotency can resume from. Abort signals are explicitly optional — callers may omit them, callees must not assume they exist. Six scenarios cover pre-write interruption, partial-write resumption, merge-story interruption, omitted signal, active signal, and pre-aborted signal. The QA strategy adds six integration tests in `tests/test_dispatch_interruption_integration.py`.

## T-0004 — Mechanized dispatch: "validators must not mutate" not stated as invariant

- status: resolved
- source: root-cause cross-reference (RC-4 from [root-cause-2026-08-21-implementation-baseline-failures.md](../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

The spec's `dispatch verify-story` uses `git cat-file -e` and `git branch --contains` (both non-mutating), and `dispatch merge-story` runs `premerge-check` (also non-mutating). The principle "validators must not mutate working-tree or index state" is implicit but not stated as a cross-cutting invariant. An implementer could reasonably add a checkout or reset inside a verification command.

**Action:** state the invariant explicitly in the spec's cross-cutting concerns or guard specification.

**Resolution:** addressed by adding the Verification Immutability cross-cutting invariant to the spec. Dispatch subcommands that verify state must not modify the working tree, index, or HEAD. Four scenarios cover verify-story index immutability, verify-story working-tree immutability, premerge-check staging prohibition, and escalation-check state immutability. The QA strategy adds four integration tests in `tests/test_dispatch_immutability_integration.py`.

## T-0005 — Mechanized dispatch: spawn-success verification before mark-dispatched

- status: resolved
- source: root-cause cross-reference (RC-6 from [root-cause-2026-08-21-implementation-baseline-failures.md](../reviews/root-cause-2026-08-21-implementation-baseline-failures.md))

`dispatch mark-dispatched` assumes the subagent has been spawned when called, but the spec does not specify how the dispatcher confirms that spawning succeeded. If the subagent process fails to start (resource exhaustion, bad config, model unavailable), the story enters DISPATCHED with no running agent.

**Action:** specify a spawn-verification precondition for `mark-dispatched` — at minimum, confirm the subagent process ID or tool-call acknowledgment exists before marking.

**Resolution:** addressed by adding the DISPATCHING intermediate state to the story lifecycle. `mark-dispatching` records intent to spawn (PREPARED → DISPATCHING). `mark-dispatched` requires the story to be in DISPATCHING state and the subagent spawn to have returned an acknowledgment (DISPATCHING → DISPATCHED). Spawn failure from DISPATCHING transitions to FAILED via `mark-failed --class environment`.
