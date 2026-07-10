---
id: FAGAN-0057
source: fagan-review
severity: minor
category: defect
artifact: orchestrator/src/orchestrator/adapters/prompt_composer.py:_call_to_action
status: resolved
traces: [ADR-0014]
---

# Loopback CTA references "findings listed above" when no findings section exists

**What is wrong:** The author-loopback template says "Address the findings listed above, then re-execute your workflow." However, after a gate-failure retry (non-zero exit, clean tree), `compose()` is called with `findings=None` and `iteration > 0`. The resulting prompt has no "Findings from Prior Iteration" section, yet the CTA tells the agent to address nonexistent findings.

**Fix:** Gate-failure retries should either: (a) pass a synthetic finding describing the gate failure so the findings section exists, or (b) add a gate-failure-specific CTA template: "Your prior attempt failed the working-tree gate. Re-execute your workflow and ensure all changes are committed."
