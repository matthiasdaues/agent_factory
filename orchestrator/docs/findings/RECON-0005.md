---
id: RECON-0005
source: reconcile-spec
severity: minor
category: defect
artifact: src/orchestrator/approval_service.py#L41,L66,L70; src/orchestrator/cli.py#L518-519,L1002-1006; src/orchestrator/adapters/adapter_detect.py#L4-15
status: open
traces: []
---

# Stale PhaseRunner/CLIAdapter/CopilotAdapter references survive in code comments after the collapse

**What is wrong:** the commits that deleted `PhaseRunner`, `CLIAdapter`, and `CopilotAdapter` (`ac7752d`, `5f19288`, `4e269e8`) removed the logic but left several comments and docstrings describing it, now misleading:

- `approval_service.py:41` — "`which PhaseRunner persists as `phase.last_reviewed_cycle`" — `PhaseRunner`no longer exists or persists anything;`ApprovalService\` and (during execution) factory's scripts are what write this field now.
- `approval_service.py:66,70` — "terminal for the state machine (`PhaseRunner.run_phase` returns immediately on it)" and "`PhaseRunner` treats `GATING` as a resume point" — same, `PhaseRunner` is gone; the state machine these lines describe is now driven by factory.
- `cli.py:518-519` — `build_manage_run_dispatch`'s comment block says `resume` "needs the full `_Runtime` (adapter, model resolver, phase runner), built lazily through the injected `build_runtime` factory." Neither `_Runtime` nor `build_runtime` exist anywhere in this file (confirmed by grep) — this describes machinery that isn't just deleted, it's a name with zero other occurrences in the codebase. The function immediately below this comment (`manage-run.resume`'s branch) just prints a "moved to factory" message; the comment no longer describes what the code does.
- `cli.py:1002-1006` — `_default_cli_model_discovery`'s docstring reasons from "`ports.py`'s `CLIAdapter` protocol declares only `invoke(...)`" and "the one concrete adapter this codebase ships (`CopilotAdapter`) implements no such method either." Both `CLIAdapter` and `CopilotAdapter` are deleted; the docstring's justification for always returning `None` no longer holds even though the `None` return itself is still the right behavior (no adapter in this codebase can be queried for models).
- `adapters/adapter_detect.py:4-15` — the module docstring's entire justification for the `KNOWN_ADAPTER_BINARIES` allowlist rests on "this codebase ships exactly one concrete `CLIAdapter` implementation today — `CopilotAdapter` (`adapters/copilot.py`)." That file and the `CLIAdapter` port are both deleted; the allowlist itself still functions (used by `configure > cli-list > auto-detect`) but its stated rationale is now false.

**Fix:** update each comment/docstring to describe current reality without inventing new mechanism: (1) in `approval_service.py`, replace `PhaseRunner`-attributed claims with "factory's execution scripts" or simply describe the field/state without naming the deleted class; (2) in `cli.py:518-519`, delete the `_Runtime`/`build_runtime` sentence entirely — the function below needs no runtime construction, it only prints a message; (3) in `cli.py:1002-1006`, rephrase to say no adapter this codebase can invoke exposes model discovery, without citing the deleted `CLIAdapter` protocol or `CopilotAdapter`; (4) in `adapter_detect.py`, rewrite the allowlist's rationale to state plainly that no concrete adapter-invocation code lives in this codebase today (that moved to factory), so `KNOWN_ADAPTER_BINARIES` is maintained by hand against known CLI binary names rather than derived from a local adapter implementation.
