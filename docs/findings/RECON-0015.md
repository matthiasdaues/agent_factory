---
id: RECON-0015
source: reconcile-spec
severity: minor
category: defect
artifact: docs/adr/0005-openrouter-model-discovery-for-model-conf.md#context
status: resolved
traces: [ADR-0005]
---

# ADR-0005 Context says only `copilot.*` rows exist, but `model.conf` ships `copilot.*`, `codex.*`, and `pi.*`

**What is wrong:** ADR-0005 was set to `status: accepted` in commit
`086d491` (RECON-0014), but its **Context** section was not refreshed. It
still reads:

> Only `copilot.*` rows exist today. Adding Pi means adding `pi.economy`,
> `pi.standard`, and `pi.strong`.

That framing no longer describes the code-as-built. `config/model.conf`
`[facts]` now contains three CLI tier blocks: `copilot.*`, `codex.*`
(added in `1bf179b`), and `pi.*` (present before this delta and re-pointed
to Qwen/GLM in the same commit). An accepted, load-bearing ADR whose
Context says "only `copilot.*` exist today" misdescribes the implemented
state to any user reading it. The Decision body itself (curate Pi
tiers statically in `model.conf`, discovery is a separate offline aid)
remains accurate; only the Context paragraph is stale. It also omits that
`codex.*` rows exist and follow the same curated-tier router pattern.

This is a delta-scoped reconciliation finding: the delta (`1bf179b`,
`086d491`) both added `codex.*` rows to `model.conf` and flipped ADR-0005
to `accepted`, so the ADR body now contradicts the very file the decision
governs.

**Fix:** Update ADR-0005's **Context** paragraph to state that
`config/model.conf` carries curated tier rows for `copilot.*`, `codex.*`,
and `pi.*`, with `pi.*` routed through OpenRouter per this decision and
`codex.*`/`copilot.*` resolved directly by their native runtimes. Remove
the "only `copilot.*` rows exist today / Adding Pi means adding" future
tense, since the addition it describes is already shipped. No code change
is required; `config/model.conf` is correct.
