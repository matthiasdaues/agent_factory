---
id: FAGAN-0012
source: fagan-review
severity: major
category: defect
artifact: orchestrator/tests/test_update_factory.py:191
status: open
traces: [ADR-0010]
---

# Preservation guarantee asserted by a test that bypasses the real reinstall

**What is wrong:** `test_agent_factory_usage_tracking_survives_update` docstring
states the user-facing guarantee — "update replaces only factory/ and never
removes .agent-factory/ usage transcripts or lifecycle state" — but the
autouse `_isolate_install` fixture monkeypatches `update_factory._run_init`
with a plain `shutil.copytree` mirror. The real
`init-factory` reinstall (the step that could touch `.agent-factory/` — it
calls `provision_usage_runtime`, `initialize_usage_lifecycle`, and rewrites the
manifest) never runs in this test. The test therefore proves only that
update-factory's own `shutil.rmtree(target_factory)` spares `.agent-factory/`,
which is trivially true; it does not prove the guarantee holds through the
real sourced init-factory that the production path actually invokes. A later
change to init-factory that deleted usage data would pass this suite.

**Fix:** Add at least one test that drives the real reinstall through update:
stop patching `update_factory._run_init`, and instead patch only
init-factory's heavy/networked steps (`provision_usage_runtime`,
`initialize_usage_lifecycle`, `pre_commit_install`) at the init-factory
module level, then assert `.agent-factory/usage/` transcripts and
`usage-control/state.json` survive a full update round trip.
