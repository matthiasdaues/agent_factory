---
id: FAGAN-0001
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/ports.py#CLIAdapter.invoke
status: resolved
traces: [FR-K2, FR-K3, VR-023]
---

# Resolved model never passed to adapter invocation

**What is wrong:** `ModelResolver` resolves a concrete model per the matrix/classification/`--model` precedence, but `CLIAdapter.invoke(prompt, cwd, timeout_s)` has no model parameter. `PhaseRunner` logs the resolved model but never passes it to the adapter. The `CopilotAdapter` uses only its constructor-time `model`. Matrix-based per-invocation model selection is therefore completely ineffective — the system always uses the global `--model` or the adapter default.

**Fix:** Add a `model: Optional[str]` parameter to `CLIAdapter.invoke()` and `InvocationResult`, or create an `InvocationRequest` DTO. Update `PhaseRunner` to pass the resolved model on every author/reviewer call. Update `CopilotAdapter` to use the per-call model. Add end-to-end tests asserting the final CLI command contains the expected model flag.
