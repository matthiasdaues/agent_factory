# 0017. Persisted defaults and adapter registry in .orchestrator/config.toml

**Status**: Accepted — resolves T-32. Persistence location confirmed and made explicit by [ADR-0021](0021-adapter-registry-discovery-and-precedence.md), which also clarifies that point 5's dictionary is no longer in the model-resolution path — only `model.conf` is.

## Context

The TUI addendum requires operator defaults that survive across invocations — `adapter`, `timeout`, `cap`, `auto_approve` (FR-Q) — and a runtime **adapter registry**: the locally available CLI adapters, their binary paths, and each adapter's tier→model dictionary (FR-R). Today these do not persist: defaults live only in `argparse` declarations, and the adapter is effectively hard-wired to Copilot.

Two questions compose. Where does this state live (T-32), and how is an effective setting resolved when a value may come from a menu selection, a CLI flag, a persisted default, or a built-in? The resolution must be **identical in direct mode and menu mode** (FR-Q3), or the two entry paths would diverge — the failure ADR-0016 exists to prevent.

### Where the state lives (Pugh Matrix)

Baseline **A**: transient flags only — no persistence; the operator re-enters settings every run. **B**: one `.orchestrator/config.toml` holding defaults, the adapter registry, and the per-adapter dictionaries. **C**: split state across dedicated files (a `config.toml` for defaults, a separate `adapters.toml`), or fold the registry into `model-matrix.conf`.

| Criterion                               | Weight | A: transient | B: one config.toml | C: split files |
| --------------------------------------- | ------ | ------------ | ------------------ | -------------- |
| Operability — settings persist (Q4)     | 3      | -1           | +1                 | +1             |
| Config integrity, atomic write (Q3)     | 2      | 0            | +1                 | 0              |
| One place to reason about (Q7)          | 2      | +1           | +1                 | -1             |
| Separation from operator-curated matrix | 2      | 0            | +1                 | -1             |
| **Weighted total**                      |        | **-1**       | **+9**             | **0**          |

B wins. Splitting the state (C) multiplies the files an operator must keep consistent and blurs the line between *operator inventory* (which adapters exist locally) and *operator-curated policy* (the model matrix, ADR-0009), which change on different cadences and by different hands. One `config.toml` keeps the operator's local, machine-specific state in a single atomically written file, distinct from the matrix that populates it.

## Decision

1. **One store, `.orchestrator/config.toml`**, behind two ports: `ConfigStore` (operator defaults) and `AdapterRegistry` (registered adapters, binary paths, and each adapter's `ModelDictionary`). Both are implemented by one TOML adapter.

2. **Atomic persistence.** Every write is write-to-temp-then-rename (VR-032). A failed persist leaves the prior configuration intact; the file is created only on the first successful persist, and its absence means built-in defaults (FR-Q5).

3. **`SettingsResolver` owns the precedence** `menu selection > CLI flag > config.toml > built-in default`, with no short-circuiting — a `None` at any layer falls through to the next (FR-Q3, VR-034). The resolver is shared by both entry paths, so effective settings are identical.

4. **Validation before persistence.** A submitted default must validate against its rule (`adapter` names a registered adapter, `timeout`/`cap` are positive integers, `auto_approve` is boolean); a malformed file or invalid stored value makes the orchestrator refuse the affected action and report the offending file and key (FR-Q4, FR-Q6, VR-033).

5. **The matrix populates the dictionaries, not the other way round.** The operator-curated model matrix (`[facts]`) is imported into each adapter's dictionary at startup and on `configure > model-matrix > edit`; runtime resolution reads only the dictionary (see ADR-0018).

6. **TOML parsing under the Python baseline is deferred (T-28)** — stdlib `tomllib` is 3.11+ while the baseline is 3.10+. The decision (raise the baseline, add a parser, or a constrained reader) is confined to this adapter and does not touch the core.

## Consequences

**Positive**

- Routine invocations stop re-entering common settings; the operator's local adapter inventory persists (Q4).
- One atomically written file is easy to reason about, back up, and diff; corruption fails loudly rather than running on garbage (Q3, R-8).
- The registry is the seam that finally lets adapters other than Copilot be selected at runtime, unblocking the multi-CLI goal (Q5).

**Negative / risks**

- `config.toml` couples three concerns (defaults, adapter inventory, dictionaries) in one file; the schema must keep them clearly separated to stay legible.
- The matrix→dictionary population step is a new startup responsibility that must stay idempotent and cheap.
- The TOML-baseline question (T-28) is a real dependency-policy decision left open, though it is well-isolated.
