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
