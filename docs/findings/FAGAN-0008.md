---
id: FAGAN-0008
source: fagan-review
severity: major
category: defect
artifact: factory/agents/research-orchestrator.md:17
status: resolved
traces: [ST-0061, ST-0062, Survey Mode]
---

# Research Orchestrator has no complete survey-mode contract

**What is wrong:** The Research Orchestrator now selects and advances survey
mode, but its declared outputs and handoffs omit `research-survey-plan.md`,
`survey-report.md`, and `research-synthesizer`. Its completion criteria remain
entirely falsification-specific: they require votes, a frozen claim register,
and a final report validated against that register. A correct five-step survey
run therefore cannot satisfy the role's own declared contract.

**Fix:** Add the survey plan and report validation results to the declared
outputs, add `research-synthesizer` to the handoff targets, and make completion
criteria conditional on the selected mode. Preserve the existing
falsification-only register, vote, and final-report requirements.

**Resolution:** The Orchestrator now declares the survey plan and report
validation outputs and hands synthesis to `research-synthesizer`. Its completion
criteria separate the common audit record from survey source-resolution and
language checks and from falsification vote, register, and frozen-report checks.
A contract regression verifies the survey outputs, handoff, and release
criteria.
