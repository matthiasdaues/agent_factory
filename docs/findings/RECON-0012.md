---
id: RECON-0012
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/remove-factory
status: resolved
traces: [ST-0044, ADR-0007]
---

# Factory removal races detached Pi usage persistence

**What is wrong:** Pi now stages a completed stream and detaches
`usage-capture`, while `remove-factory` deletes `.agent-factory/` without
coordinating with in-flight capture. Removal can delete the staged source before
the detached process reads it, losing pending usage. If the detached process
has already read the source, it can finish after removal and recreate
`.agent-factory/usage/`, leaving Factory-owned telemetry behind after the
remover reported success. Existing cleanup tests cover guarded source deletion
and ordinary removal separately, not their concurrency boundary.

**Fix:** Define and implement an uninstall protocol for pending detached
captures, such as a local pending-capture registry plus a bounded cleanup
barrier. `remove-factory` must explicitly drain or cancel registered captures,
remove their staged inputs, and prevent any later recreation of Factory paths.
Add a gated installed-path regression that starts a detached Pi capture, runs
`remove-factory`, releases the capture, and proves both the chosen pending-usage
disposition and the absence of post-removal path resurrection.

**Resolution:** `init-factory` now creates a generation state and pending
registry. Pi atomically snapshots lifecycle state into a visible hard-link token
before replacing its contents with durable registration metadata, and the
detached worker moves its marker from pending to committing before the final
persistence decision. Default removal transitions to `drain`, allowing every
eligible pre-transition registration to commit. Explicit `cancel` discards
pending registrations without signalling PIDs; already-committing work must
settle before teardown. Both modes are bounded. A timeout restores `active` and
returns nonzero before uninstall mutations.

Six installed concurrency regressions prove successful drain, timeout
restoration, explicit cancel without resurrection, registration rejection
under the removal fence, malformed/stale registry path safety, and bounded
abort while a commit marker remains. Successful uninstall still deletes only
the manifest-owned Factory footprint and preserves unrelated project files.
