---
id: RECON-0018
source: reconcile-spec
review_class: code
category: defect
type: build
severity: note
basis:
  in_use: true
  harms_downstream: false
  fails_purpose: false
  raises_cost: false
rating:
override_by:
override_reason:
stop_confirmed_by:
stop_confirmed_reason:
artifact: packages/factory/config/pre-commit-config.yaml:19-20
status: resolved
owner: developer-agent
traces: [UC-09, ADR-0003]
---

# Canonical config omits the changed-only pre-commit test hook

**What is wrong:** `.agent-factory/factory/README.md`, UC-09, and ADR-0003 describe a
three-gate test regime whose pre-commit point runs
`.agent-factory/factory/scripts/run-tests --changed-only`. The repository's own merged
`.pre-commit-config.yaml` contains that hook, but the canonical
`.agent-factory/factory/config/pre-commit-config.yaml` installed into consumer projects does
not. Fresh consumers therefore receive the ST-0073 full-suite pre-push gate
without the documented fast pre-commit test gate.

**Why this severity:** `run-tests` no longer exists, and the Rule "Factory does not inject test hooks into pre-commit config" in the scope map replaced the three-gate regime. So the hook the finding asks for is out of scope and nothing remains to change.

**Fix:** Add a prefixed `run-tests --changed-only` hook to
`.agent-factory/factory/config/pre-commit-config.yaml`, scoped to source and test paths as
UC-09/BR-029 require. Cover fresh installation and merge idempotence, then
remove the temporary README caveat once all three documented gates are
installed.
