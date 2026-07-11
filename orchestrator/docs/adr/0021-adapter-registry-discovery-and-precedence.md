# 0021. Adapter registry becomes the local, discovery-populated tier→model lookup

**Status**: Accepted — revises [ADR-0017](0017-config-and-adapter-registry-persistence.md) (point 5's populate direction) and [ADR-0020](0020-tier-everywhere-model-config-router.md) (`model.conf`'s role, not its `[policy]` removal); resolves [SPEC-0010](../findings/SPEC-0010.md) and T-31.

## Context

[SPEC-0010](../findings/SPEC-0010.md): three artifacts disagree on where the adapter registry persists. ADR-0017 already resolved this once — one `.orchestrator/config.toml`, behind `ConfigStore` and `AdapterRegistry` — but `interface-contracts.md`'s `Config` schema never gained the registry's fields, and `entity-model.md`'s "persisted alongside the configuration store" reads as a second file. That gap alone would close SPEC-0010. The project owner asked for more: a routine that starts a CLI, asks it for its model inventory, and writes the names into the registry — and, if the CLI's answer also signals a tier, folds `model.conf` and the registry into one lookup.

T-31 is still open: "mandatory or optional discovery capability?" FR-R8 already answers this in passing — auto-detect queries the adapter "if that adapter supports discovery; otherwise... report... and leave configuration unchanged." Optional, degrading gracefully. `CLIAdapter` (`ports.py`) has exactly one method, `invoke()`; no discovery method exists — the actual port-shape question T-31 named.

A full merge — delete `model.conf`, registry becomes the only file — is not available. `model.conf` (`factory/config/`, ADR-0020) is read directly by a human running `factory/` playbooks with no orchestrator process at all; no `.orchestrator/config.toml`, no `AdapterRegistry` object exists in that mode. Deleting it stops that workflow from working.

A second hazard, found reading ADR-0017 point 5 against FR-R7: FR-R7 ("add model"/"remove model") already writes straight into a `ModelDictionary`. Point 5 also writes into the same dictionary, from `model.conf`, "at startup." Nothing says which wins if both touch the same tier — a hand-added or discovered model can be silently overwritten by the next matrix import.

### Alternatives (Pugh Matrix)

**A**: status quo — no discovery, matrix import unconditionally overwrites. **B**: full merge — delete `model.conf`, the registry is the only file. **C**: precedence layering — `model.conf` stays the portable seed; the registry is the local override; import fills gaps only, never overwrites.

| Criterion                          | Weight | A: status quo | B: full merge | C: precedence layering |
| ---------------------------------- | ------ | ------------- | ------------- | ---------------------- |
| Closes SPEC-0010                   | 2      | 0             | +1            | +1                     |
| Works with no orchestrator running | 3      | +1            | -1            | +1                     |
| No clobber hazard                  | 2      | -1            | +1            | +1                     |
| Discovery-driven upkeep            | 2      | -1            | +1            | +1                     |
| Implementation cost (simplicity)   | 1      | +1            | +1            | 0                      |
| **Weighted total**                 |        | **0**         | **+4**        | **+9**                 |

C wins. B scores well everywhere except the one criterion that matters most here — it breaks a workflow this project explicitly supports. C gets everything B gets except a single merged file, in exchange for never breaking standalone use.

## Decision

1. **One persisted store, stated explicitly.** `AdapterRegistry`/`ModelDictionary` persist in `.orchestrator/config.toml`, alongside `Config`, as ADR-0017 already intended. `interface-contracts.md` gains the persistence line it was missing; `entity-model.md`'s "alongside" becomes "in the same store." Closes SPEC-0010.

2. **`CLIAdapter` gains one optional port method:** `discover_models() -> list[ModelCandidate] | None`. `None` means the adapter cannot self-report — the operator's `add model` (FR-R7) is the only path, exactly as FR-R8 already specifies. This resolves T-31: discovery is optional per-adapter by construction of the return type, not a feature flag.

3. **`ModelCandidate` carries `model_id` and an optional `tier_hint`.** No CLI is assumed to return a usable `tier_hint`. Where it's absent, the candidate is written with tier unset and the operator confirms one via the existing `add model` flow. Where present, it's written as a proposal the operator can accept as-is.

4. **`configure > cli > {adapter} > auto-detect` (FR-R8, already named)** calls `discover_models()`, writes each candidate into that adapter's `ModelDictionary`, and reports what it found.

5. **Precedence, not deletion.** `model.conf` stays the portable, git-tracked seed every project ships — the only tier→model source that works without an orchestrator process. `.orchestrator/config.toml`'s `ModelDictionary` is the local override layer. ADR-0017 point 5 is revised: matrix import fills a tier only where the dictionary doesn't already have one; it never overwrites an entry discovery or a manual `add model` already set.

6. **The practical merge.** At runtime the dictionary — not `model.conf` — is already what's read (ADR-0018 §3). After this decision it is also what stays current, with `model.conf` demoted to a first-run seed. Two files remain; one effective lookup.

## Consequences

**Positive**

- Closes SPEC-0010 outright and the silent-clobber hazard between matrix import and manual edits.
- Formalizes T-31 as a port-shape answer, not a policy statement.
- The standalone, no-orchestrator `factory/` workflow is untouched.

**Negative / risks**

- `discover_models()` is unimplemented for the one adapter that exists (Copilot); whether it can self-report models, let alone a tier signal, is unverified — this decision removes the port-shape ambiguity, it does not yet produce output.
- Two files instead of one is a real cost against a literal single-lookup merge — accepted, because the alternative breaks standalone use.

## Follow-up (not done in this pass)

- Implement `discover_models()` on `CLIAdapter` and the Copilot adapter; spike first — confirm Copilot can list models at all before assuming a `tier_hint` is possible.
- Wire `configure > cli > {adapter} > auto-detect` to call it.
- Add the persistence line to `interface-contracts.md`; fix `entity-model.md`'s "alongside" wording.
- Revise ADR-0017 point 5's prose to match the gap-fill precedence.

## Referenced from

- [SPEC-0010](../findings/SPEC-0010.md)
