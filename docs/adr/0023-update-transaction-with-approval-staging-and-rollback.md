---
id: 0023
status: accepted
evaluation: none
---

# Update transaction with approval, staging, and rollback

## Context

ADR-0010 introduced `update-factory` as a remove-and-reinstall command that calls `init-factory` to refresh the installed Factory tree. ADR-0022 added a layered installation bootstrap (`install-agent-factory`) that wraps `init-factory` with preflight, consent, and verification. ADR-0022 states that `update-factory` continues to call `init-factory` directly, bypassing the bootstrap's preflight and consent because the host environment was validated at first install.

The accepted [value-first onboarding feature](../spec/value-first-onboarding-journey.feature) and the [update-factory interface contract](../spec/supplementary_specs/interface-contracts.md#update-factory) require behaviors that contradict this bypass:

- A normal update requires confirmation before download or mutation.
- The complete replacement is downloaded, verified, and staged before application.
- Application failure restores the previous Factory tree and instruction headers.
- Modified Factory-owned files stop the update unless the user selects the existing preservation flow.
- A different source selector or remote URL requires an explicit option and separate confirmation.
- The receipt records the selected source, resolved version, remote digest, and changed paths.

The remove-and-reinstall mechanism from ADR-0010 already moves aside the old Factory tree and restores it on failure. That rollback design is sound. The gap is that `update-factory` performs no approval before mutation and no staging between verification and application. The layered design from ADR-0022 remains correct for first installation. Only the claim that updates bypass consent is wrong. Tools, network, local files, and the selected release source can change after installation.

`evaluation: none` because the feature contract leaves no alternative: the specified behaviors are required, and the existing rollback mechanism already demonstrates the correct shape.

## Decision

Supersede ADR-0010 and ADR-0022 with a single decision that preserves the layered first-install entry point and defines the update transaction.

**First installation** remains unchanged from ADR-0022: `install-agent-factory` owns preflight, prerequisite fixes, release verification, consent, and the receipt. It delegates project-level setup to `init-factory` after approval.

**Update transaction** (`update-factory`) becomes a seven-step transaction:

1. **Check mode** (`--check`): reports installed and candidate versions, source, digest, local modifications, and planned header changes without writing. This step exists for both normal updates and source changes.
2. **Approval**: a normal update requires confirmation before download or mutation. The preview shows the source, current and candidate versions, and planned effects.
3. **Download and verification**: the complete replacement is downloaded and verified against `SHA256SUMS` before extraction. A failed digest check aborts the update with no changes.
4. **Staging**: the verified replacement is staged alongside the current installation. The staged state includes the Factory tree, derived interface files, hook configuration, and instruction header edits. Nothing is applied yet.
5. **Application**: the staged replacement is applied atomically. The previous Factory tree is moved aside (not deleted) before application, as in ADR-0010.
6. **Rollback**: if application fails, the previous Factory tree and instruction headers are restored. The rolled-back state is reported.
7. **Receipt**: the receipt records the selected source, immutable version or local revision, remote digest when applicable, and changed paths.

**Local-change policy**: modified Factory-owned files stop the update before staging. The user may select the existing preservation flow to proceed.

**Source-boundary consent**: a different source selector or remote URL requires a separate `--source` option and its own confirmation step. No automatic fallback crosses the source boundary.

**Relationship to init-factory**: `update-factory` no longer delegates to `init-factory` for the replacement. It owns the full transaction. `init-factory` retains its existing interface for first installation (called by `install-agent-factory`) and for component-level operations (`--add`, `--update`, `--remove` for usage).

## Consequences

**Easier**: the update path satisfies the feature contract. Approval prevents unintended mutations. Staging catches verification failures before they replace a working installation. Rollback handles application failures. Source-boundary consent prevents silent trust-boundary changes. The receipt provides traceability.

**Harder**: `update-factory` is a more complex transaction than the original remove-and-reinstall. The staging step requires temporary disk space alongside the current installation. The local-change check adds a preflight read of Factory-owned files. The source-boundary consent adds a second confirmation path.
