---
id: RECON-0006
source: reconcile-spec
severity: major
category: defect
artifact: factory/config/extensions/capture-usage.ts
status: open
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
