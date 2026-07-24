---
id: RECON-0006
source: reconcile-spec
severity: major
category: defect
artifact: factory/config/extensions/capture-usage.ts
status: resolved
traces: [ST-0044]
---

# Pi child records can lose their human parent session

**What is wrong:** `run-agent.ts` and `dispatch-wave.ts` read the parent session
id from `PI_AGENT_FACTORY_SESSION_ID`, but the human-session capture extension
only derives a session id inside its `session_shutdown` callback. It does not
establish that id for tools launched during the session. A child launched from
a normal human Pi session can therefore be persisted without the
`parent_session_id` required to build the spend tree. The current test only
checks that the source contains `parentSessionId`; it does not execute either
tool and inspect the resulting record.

**Fix:** Obtain the active Pi session id at the `run_agent` and `dispatch_wave`
tool boundary, or establish it in shared session context before tools run. Add
executable installed-path tests for both tools that persist child records and
assert their actual `parent_session_id` and `depth` values.

## Analysis

The defect is at the Pi tool boundary. Both invocation extensions currently
read only `PI_AGENT_FACTORY_SESSION_ID`; a normal interactive Pi parent does
not set that environment variable, even though its active session id is
available from `ctx.sessionManager.getSessionFile()`. The shutdown extension
derives the same id too late to help already-spawned children.

Implement one shared session-id resolver in `pi-usage.ts`. It will prefer the
active session file id, then the explicit environment id used by spawned Pi
children, and finally a process-stable generated fallback. `capture-usage.ts`,
`run-agent.ts`, and `dispatch-wave.ts` will use that resolver so the parent id
at tool execution and the eventual human-root id are identical.

Modify:

- `factory/config/extensions/pi-usage.ts`
- `factory/config/extensions/capture-usage.ts`
- `factory/config/extensions/run-agent.ts`
- `factory/config/extensions/dispatch-wave.ts`
- `orchestrator/tests/test_usage_capture_pi_e2e.py`

The regression tests will install Factory into temporary consumer projects,
load the installed TypeScript extensions, execute their registered
`run_agent` and `dispatch_wave` tool entrypoints with a synthetic active Pi
session, stub only their external subprocess boundaries, and inspect the
persisted usage JSONL. Each child record must contain the active human
`parent_session_id` and `depth: 1`. This exercises the public installed path
instead of asserting source text.

No new business rule or architecture boundary is introduced. The change makes
the existing parent/depth usage contract executable and removes the obsolete
source-inspection test.

## Resolution

The shared Pi usage bridge now resolves an active session id from the tool
context's session manager, the explicit child-session environment, or a
process-stable fallback. Human shutdown capture and both invocation tools use
that same resolver.

Installed-path regression tests execute the registered `run_agent` and
`dispatch_wave` tools in consumer-project fixtures and verify the persisted
child records contain `parent_session_id: pi-human-parent` and `depth: 1`.
