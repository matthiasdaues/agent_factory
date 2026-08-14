---
id: RECON-0018
source: reconcile-spec
severity: major
category: defect
artifact: factory/config/pre-commit-config.yaml
status: open
traces: [UC-09, ADR-0003]
---

# Canonical config omits the changed-only pre-commit test hook

**What is wrong:** `factory/README.md`, UC-09, and ADR-0003 describe a
three-gate test regime whose pre-commit point runs
`factory/scripts/run-tests --changed-only`. The repository's own merged
`.pre-commit-config.yaml` contains that hook, but the canonical
`factory/config/pre-commit-config.yaml` installed into consumer projects does
not. Fresh consumers therefore receive the ST-0073 full-suite pre-push gate
without the documented fast pre-commit test gate.

**Fix:** Add a prefixed `run-tests --changed-only` hook to
`factory/config/pre-commit-config.yaml`, scoped to source and test paths as
UC-09/BR-029 require. Cover fresh installation and merge idempotence, then
remove the temporary README caveat once all three documented gates are
installed.
