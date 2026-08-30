---
id: RECON-0020
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/phase#L259
status: resolved
traces: [UC-09, ADR-0003, ST-0151]
---

# Phase script does not resolve charter:test_command notation

**What is wrong:** The `evaluate_condition` function in `factory/scripts/phase` (lines 259-288) takes the `script` field from the gate condition and passes it directly to `subprocess.run(script.split(), ...)`. The FSM YAML files (`greenfield-development.fsm.yml`, `bug-fix.fsm.yml`) now declare `script: "charter:test_command"` with `charter_file: docs/charter/testing.yaml`, but the phase script has no logic to detect the `charter:` prefix, read the `charter_file` field, parse the YAML, and resolve the actual test command. The literal string `charter:test_command` is passed to subprocess, which fails with OSError because no such executable exists.

**Fix:** Add charter resolution logic to `evaluate_condition` in `factory/scripts/phase`: when the `script` field starts with `charter:`, read `charter_file` from the condition dict, parse the YAML, extract the named field (e.g. `test_command`), and run that resolved command instead. Fail with a clear message when the charter file is absent or the field is missing, per the feature specification's Scenarios "Phase advance blocks when charter is absent" and "Phase advance blocks when test_command is missing."
