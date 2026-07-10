---
id: FAGAN-0036
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/copilot.py#_invoke_interactive
status: resolved
traces: [BR-018, BR-020, VR-018, VR-020]
---

# Interactive adapter does not classify auth/config failures

**What is wrong:** The interactive adapter path (`_invoke_interactive()`) returns `auth_error=False` and `config_error=False` for every non-timeout exit because it does not inspect subprocess output. Auth/config failures in interactive mode are therefore misclassified as ordinary author failures and sent through retry logic instead of halting.

**Fix:** Capture or otherwise inspect interactive-process failure output and apply the same auth/config classification regex used by the captured (non-interactive) path. This may require capturing stderr while still passing through stdout to the terminal, e.g. via `tee` or a pty-based approach.
