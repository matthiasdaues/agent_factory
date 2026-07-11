# 0021. model.conf is read directly at resolution time; the adapter registry stays a separate local cache

**Status**: Accepted — revises [ADR-0017](0017-config-and-adapter-registry-persistence.md) (point 5's "runtime reads the dictionary" claim) and [ADR-0020](0020-tier-everywhere-model-config-router.md) (states explicitly what "the router" means at resolution time); resolves [SPEC-0010](../findings/SPEC-0010.md) and T-31.

## Context

[SPEC-0010](../findings/SPEC-0010.md): three artifacts disagree on where the adapter registry persists. ADR-0017 already resolved this once — one `.orchestrator/config.toml`, behind `ConfigStore` and `AdapterRegistry` — but `interface-contracts.md`'s `Config` schema never gained the registry's fields, and `entity-model.md`'s "persisted alongside the configuration store" reads as a second file.

The project owner asked for more, floating a further simplification: make `model.conf` the sole persistent store of available models, so only models with a configured tier are ever assignable. Reading the code against that question surfaced two things worth acting on:

- `ModelResolver` had two live paths. The deprecated `resolve()` — still wired into `phase_runner.py` — read `model.conf` directly. The ADR-0018-compliant `resolve_agent_tier()` read `AdapterRegistry`'s `ModelDictionary` instead, itself populated from `model.conf` at startup (`populate_adapter_dictionaries_from_matrix`). Two resolution paths, reading two different things that were supposed to agree.
- `AdapterRegistry`'s per-adapter `ModelDictionary` is real, tested, wired functionality — `configure > cli > {adapter} > add model` / `remove model` (FR-R7) write into it directly, independent of `model.conf`. A full merge that deletes the registry's model-dictionary role would touch that working subsystem; a full merge that deletes `model.conf` breaks the `factory/` playbook workflow, which reads it with no orchestrator process running at all.

### Alternatives (Pugh Matrix)

**A**: status quo — two resolution paths, registry as intended source of truth. **B**: full merge — delete `model.conf`, registry is the only file. **C**: precedence layering — registry becomes the local override, `model.conf` a seed, import fills gaps only. **D**: `model.conf` is what `ModelResolver` reads, full stop; the registry keeps its existing, separate role (menu-mode display, `add model`/`auto-detect` management) untouched.

| Criterion                            | Weight | A: status quo | B: full merge | C: precedence layering | D: read model.conf directly |
| ------------------------------------ | ------ | ------------- | ------------- | ---------------------- | --------------------------- |
| Closes SPEC-0010                     | 2      | 0             | +1            | +1                     | +1                          |
| Works with no orchestrator running   | 3      | +1            | -1            | +1                     | +1                          |
| One resolution path, not two         | 2      | -1            | +1            | +1                     | +1                          |
| Discovery wired to affect resolution | 2      | -1            | +1            | +1                     | 0                           |
| Implementation cost (simplicity)     | 1      | +1            | +1            | 0                      | +1                          |
| **Weighted total**                   |        | **0**         | **+4**        | **+9**                 | **+11**                     |

D wins. It closes the same gap C does, at less cost, because it does not try to keep two stores in sync at all — resolution reads one file. It scores lower than C on exactly one thing: a future discovery routine writing into the registry would not, by itself, change what gets resolved. That is an honest, accepted gap, not an oversight — see Follow-up.

## Decision

1. **One persisted store, stated explicitly.** `AdapterRegistry`/`ModelDictionary` persist in `.orchestrator/config.toml`, alongside `Config`, as ADR-0017 already intended. `interface-contracts.md` gains the persistence line it was missing; `entity-model.md`'s "alongside" becomes "in the same store." Closes SPEC-0010.

2. **`ModelResolver` reads `model.conf` directly.** One method, `resolve_tier(tier, explicit_model=None)`, replaces the deprecated `resolve()` and `resolve_agent_tier()`/`resolve_story_classification()`. It takes an already-known tier — an agent's own frontmatter, or (ADR-0020) a story's own `tier` — and looks it up in `model.conf`'s `[facts]` for the active CLI. No `AdapterRegistry` dependency anywhere in the resolution path. `phase_runner.py`, previously wired to the deprecated path, now resolves the phase's author and reviewer independently, each from its own declared tier — closing the ADR-0018 migration gap this decision surfaced.

3. **The registry keeps its existing, separate role, unchanged.** `AdapterRegistry`'s `ModelDictionary` still backs `configure > cli > {adapter}`'s `list models` / `add model` / `remove model` / `auto-detect`, and still gets populated from `model.conf` at menu-mode startup (`populate_adapter_dictionaries_from_matrix`, unconditional overwrite, as before) — purely for the TUI's pick-list and its `★` default marker. It is not read at resolution time, so nothing in this subsystem needed to change to implement points 1–2.

4. **T-31 stays open, narrowed.** "Mandatory or optional discovery capability?" is unaffected by this decision — `CLIAdapter` still has only `invoke()`; no `discover_models()` method exists yet. Deferred to Follow-up, along with the open question it now carries: when discovery lands, does it write into `model.conf` (making it live for resolution immediately) or into the registry (matching today's `add model`, but inert for resolution until also copied to `model.conf`)? This ADR does not decide that — a future one should, once discovery is real enough to make the tradeoff concrete.

## Consequences

**Positive**

- Closes SPEC-0010 outright.
- One resolution path instead of two silently-competing ones — the actual bug behind SPEC-0009 (`phase_runner.py` never having migrated to agent-tier resolution) is fixed as a side effect.
- Zero risk to the registry's existing, tested `add model`/`auto-detect` functionality — untouched.
- Matches the "least fuss" direction explicitly given: no precedence engineering, no gap-fill logic, no second store to keep in sync.

**Negative / risks**

- A model added via `configure > cli > {adapter} > add model` has no effect on resolution until the same tier/model is also added to `model.conf` by hand. This is a real, visible seam — the TUI's model-management commands and the thing that actually picks a model are, for now, two different surfaces. Acceptable because `model.conf` editing already has its own `configure > model-matrix > edit` path; not acceptable indefinitely if the registry's commands are kept around only to mislead.
- Discovery (T-31/FR-R8), once built, still needs to decide where it writes — deferred, not solved, by this decision.

## Follow-up (not done in this pass)

- Add the persistence line to `interface-contracts.md`; fix `entity-model.md`'s "alongside" wording. *(Done as part of this same pass — see interface-contracts.md § Adapter Registry and entity-model.md.)*
- Decide `discover_models()`'s target (`model.conf` vs. the registry) before implementing it — a follow-up ADR, not assumed here.
- Consider whether `configure > cli > {adapter} > add model` should be repointed at `model.conf` directly, closing the two-surface seam named above, once discovery's target is decided.

## Referenced from

- [SPEC-0010](../findings/SPEC-0010.md)
