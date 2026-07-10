---
id: FAGAN-0005
source: fagan-review
severity: critical
category: defect
artifact: src/orchestrator/adapters/copilot.py#_invoke_interactive
status: resolved
traces: [UC-01, FR-B2]
---

# Interactive mode ignores composed prompt

**What is wrong:** In interactive mode, `_invoke_interactive()` launches bare `copilot` without the `-p` flag and without feeding the composed prompt. The agent definition, project context, and findings — all composed by `PromptComposer` — are never delivered to the agent. The interactive session starts with no context.

**Fix:** Feed the composed prompt to the interactive session. Options: write the prompt to a temp file and pass it via a CLI flag, pipe it to stdin before handing over the terminal, or use `copilot` with `-p` in interactive mode if supported.
