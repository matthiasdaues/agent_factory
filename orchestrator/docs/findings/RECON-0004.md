---
id: RECON-0004
source: reconcile-spec
severity: major
category: defect
artifact: orchestrator/src/orchestrator/cli.py#L2304,L2653
status: open
traces: []
---

# Two "Agent HQ" strings survived the ST-0065 rename in cli.py

**What is wrong:** ST-0065 (commit `ce71932`) renamed "Agent HQ" to "agent_factory" throughout `_tooling_root()` and `_resolve_agents_dir()`, fixing the `RuntimeError`/`ValueError` messages those functions raise. Two more "Agent HQ" strings in the same file were not caught: line 2304, inside the instruction-file template rendered by `_render_instruction_file` — written verbatim into real target projects' `CLAUDE.md`/`AGENTS.md` as "You are running inside the Agent HQ orchestrator." — and line 2653, an error message in `_resolve_agents_dir`'s fallback path ("...or check your Agent HQ installation."). The first is user-visible in every project `orchestrate init` sets up; the second is a support-facing error message pointing at a name that no longer means anything in this codebase.

**Fix:** Replace both occurrences with the current project name, consistent with ST-0065's rename elsewhere in the file — e.g. "You are running inside the agent_factory orchestrator." and "...or check your agent_factory installation." Grep the file (and the rest of `orchestrator/src/`) for any other literal "Agent HQ" occurrences before closing this out, since these two were missed by a story whose stated purpose was exactly this rename.
