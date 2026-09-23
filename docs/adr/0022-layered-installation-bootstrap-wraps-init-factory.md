---
id: 0022
status: proposed
evaluation: pugh-matrix
---

# Layered installation: bootstrap wraps init-factory

## Context

The value-first onboarding journey introduces a newcomer-facing installation path. The existing `init-factory` script handles project-level Factory setup: it copies the Factory tree, writes the install manifest, detects the test regime, and configures hooks. It assumes the host environment is ready (correct tools installed, Git repository present, network available) and runs without a preflight diagnosis or consent sequence.

A newcomer needs a broader scope: host diagnosis, prerequisite resolution, release download and verification, an installation preview with consent, and a receipt. Two structural options exist for where this broader scope lives.

## Decision

Wrap `init-factory` with a new `install-agent-factory` bootstrap script. The bootstrap owns preflight diagnosis, prerequisite fixes, release download and verification, consent gates, and the receipt. It delegates project-level setup to `init-factory` after consent.

| Criterion                             | Weight | Bootstrap wraps init-factory (baseline) | init-factory absorbs bootstrap |
| ------------------------------------- | ------ | --------------------------------------- | ------------------------------ |
| Safety: read-only preflight (QS-9)    | 3      | 0                                       | -1                             |
| Controllability: consent gate (QS-10) | 3      | 0                                       | -1                             |
| Clean Architecture (QS-3)             | 3      | 0                                       | -1                             |
| Simplicity / YAGNI                    | 2      | 0                                       | 0                              |
| Testability                           | 2      | 0                                       | -1                             |
| Compatibility: existing update path   | 2      | 0                                       | -1                             |
| **Weighted total**                    |        | **0**                                   | **-13**                        |

**Safety (weight 3, absorb scores -1):** The bootstrap's preflight is a separate, auditable phase that must complete before any mutation. Absorbing it into `init-factory` mixes diagnostic reads with setup writes in a single script, making it harder to verify that no writes occur during diagnosis.

**Controllability (weight 3, absorb scores -1):** The bootstrap owns the consent sequence as a distinct layer. `init-factory` currently runs without consent gates and is called by `update-factory` (ADR-0010). Adding consent to `init-factory` forces `update-factory` to either suppress it (introducing a mode flag that weakens the gate) or present consent on every update (breaking the existing contract).

**Clean Architecture (weight 3, absorb scores -1):** The bootstrap sits at the adapter layer, handling host-environment concerns (platform detection, tool installation, network, download). `init-factory` is a use-case-layer script focused on project setup. Absorbing adapter-layer concerns into the use case violates the dependency rule: the project setup script would depend on host-environment details it currently ignores.

**Simplicity (weight 2, scores tie at 0):** Both options require the same total logic. The bootstrap adds one script but keeps `init-factory` unchanged. Absorption avoids the new script but adds mode flags and conditional paths to an existing one.

**Testability (weight 2, absorb scores -1):** Two scripts with distinct responsibilities are independently testable. The bootstrap can be tested against a mock `init-factory`; `init-factory` can be tested without a host-diagnosis harness. Absorption couples both test concerns into a single test surface.

**Compatibility (weight 2, absorb scores -1):** `update-factory` calls `init-factory` after replace-and-reinstall (ADR-0010). Absorbing the bootstrap into `init-factory` means `update-factory` must suppress or repeat the preflight and consent sequence on every update, introducing a mode flag or a separate code path. The layered design leaves `update-factory` unchanged.

## Consequences

- `install-agent-factory` is the newcomer entry point. It runs standalone from a curl pipe or a local clone.
- `init-factory` remains the project-setup script, called by both `install-agent-factory` (first install) and `update-factory` (updates). Its interface does not change.
- `update-factory` continues to call `init-factory` directly (ADR-0010), bypassing the bootstrap's preflight and consent because the host environment was validated at first install.
- `build-release` produces both scripts (`install-agent-factory` and the archive containing `init-factory`) as release assets. The bootstrap's version is tied to the release it ships with.
- The bootstrap must record which release base it was fetched from, so `update-factory` can query the same base for updates.
