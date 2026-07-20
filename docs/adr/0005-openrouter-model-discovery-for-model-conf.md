---
id: 0005
status: proposed
evaluation: none
---

# OpenRouter tiers are curated into `model.conf`; discovery is a separate offline aid

## Context

`config/model.conf` is an operator-curated, per-CLI tier router: a tier (`economy`, `standard`, `strong`) either has a concrete model configured for the active CLI or it does not, and `on_missing = halt` stops a run rather than guess. Only `copilot.*` rows exist today. Adding Pi means adding `pi.economy`, `pi.standard`, and `pi.strong`.

Pi is being pointed at OpenRouter, which exposes hundreds of models across many providers through one endpoint, `https://openrouter.ai/api/v1/models`, each row carrying an ID, context length, and per-token pricing. Two questions follow: what concrete model does each Pi tier resolve to, and how does an operator discover and keep those choices current as OpenRouter's catalog churns?

The tempting move is to resolve tiers live — query OpenRouter at spawn time and pick, say, the cheapest model above some capability bar. That would make every `run_agent` spawn depend on a network round-trip and a catalog that changes underneath identical runs. It is surprising enough to be worth recording why the project does *not* do that.

## Decision

**Runtime resolution stays static and offline.** Pi tiers are curated into `model.conf` as ordinary rows — `pi.economy`, `pi.standard`, `pi.strong` — resolved by the same `matrix-lint` parser, under the same `on_missing = halt`, that already serves `copilot.*` and `trigger`. No agent spawn ever calls the network to pick a model. This is the direct application of two standing principles: `model.conf` is an *operator-curated* router (not an auto-selector), and the project resolves flow-control state deterministically from files, never from a live external source.

**Discovery is a separate operator tool, off the hot path.** A stdlib-only script, `factory/scripts/openrouter-discover`, queries the OpenRouter catalog to *assist* curation. It:

- lists models sorted by price, filterable by max price and minimum context length, so an operator can see the field;
- suggests a tier mapping — a cheap model for `economy`, a mid-tier for `standard`, a frontier model for `strong` — as a starting point the operator edits, never an auto-commit;
- checks the `pi.*` rows currently in `model.conf` against the live catalog and reports any ID that no longer exists (`--check`, non-zero exit on drift), so catalog churn surfaces on demand rather than as a spawn-time failure.

The network dependency, the API key (`OPENROUTER_API_KEY`), and the catalog's volatility are all confined to this one occasionally-run tool. The runtime path stays offline and reproducible.

### Rejected alternatives

- **Hand-maintain the rows with no tooling.** Workable, but leaves the operator reading a web catalog of hundreds of models by eye and gives no way to detect when a curated ID silently disappears. The discovery script is cheap and removes both problems; rejected as false economy.
- **Resolve tiers live against the OpenRouter API at spawn time.** Always current, but it puts a network round-trip and a moving catalog on the path of every agent spawn — non-deterministic runs, a new failure mode when OpenRouter is unreachable, and a direct violation of the deterministic-resolution principle `model.conf` exists to uphold. Rejected. Currency is an occasional-curation concern, met by `openrouter-discover --check`, not a per-spawn one.

There is no genuine third contender once "runtime must stay deterministic and offline" is held fixed, so no Pugh Matrix applies (`evaluation: none`).

## Consequences

**Positive**

- Every Pi agent spawn resolves its model offline, deterministically, exactly as `copilot.*` and `trigger` already do — one resolution mechanism, one parser, no new hot-path dependency.
- Operators get real help curating and validating tier rows against a large, churning catalog, without that machinery ever touching a run.
- `openrouter-discover --check` gives a deterministic gate for "do the configured Pi models still exist," runnable in CI or before a batch of runs.

**Negative / risks**

- Curated rows can go stale between discovery runs; a retired OpenRouter model ID stays in `model.conf` until `--check` or a failed spawn surfaces it. The mitigation is process (run `--check`), not enforcement.
- The discovery script depends on OpenRouter's catalog JSON shape and endpoint; a breaking change there breaks discovery (but not the runtime path).
- Tier "suggestions" encode a price/capability heuristic that will not match every operator's judgment — deliberately advisory, edited by hand, never authoritative.

## Referenced from

- [09_architecture_decisions.md](../09_architecture_decisions.md)
- [config/model.conf](../../config/model.conf)
- [docs/spec/prd.md § FR-J](../spec/prd.md#4-functional-requirements)
- [docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md](0004-pi-subagent-invocation-via-subprocess-spawn.md)
