---
id: FAGAN-0019
source: fagan-review
severity: major
category: defect
artifact: /home/matthiasdaues/.pi/agent/extensions/openwebui.ts:40
status: resolved
---

# CONFIG_PATH hardcodes ~/.pi/agent and ignores PI_CODING_AGENT_DIR

**What is wrong:** `CONFIG_PATH` is built from `join(homedir(), ".pi", "agent", "openwebui.json")`. Pi documents `PI_CODING_AGENT_DIR` as overriding the config directory (default `~/.pi/agent`). When that variable is set, `/register` persists to — and every load reads from — a location pi itself no longer treats as the agent dir, so the config is misplaced and the completion message prints the wrong path. The header claim "persists it to ~/.pi/agent/openwebui.json" then holds only by accident.

**Fix:** Resolve the agent directory as `process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent")` and build `CONFIG_PATH` from it.

**Resolution (repeat pass 2026-08-19):** Fixed as claimed. `AGENT_DIR = process.env.PI_CODING_AGENT_DIR ?? join(homedir(), CONFIG_DIR_NAME, "agent")` with `CONFIG_DIR_NAME` imported as a value from `@earendil-works/pi-coding-agent` — verified against the installed package (`dist/index.js` re-exports it; `dist/config.js:394` defines it as `".pi"`). This replicates pi's `getAgentDir()` except tilde expansion of the env value (`expandTildePath`), a residual divergence recorded as suggestion S10 in the repeat report.
