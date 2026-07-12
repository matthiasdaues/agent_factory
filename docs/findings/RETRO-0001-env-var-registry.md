---
id: RETRO-0001
title: No env var registry — AF_SESSION_LOG provisioned ad-hoc
status: open
severity: minor
category: configuration
date: 2026-07-13
found_by: session-retrospective
tags: [retro, env-var, session-logging]
---

# RETRO-0001: No env var registry — AF_SESSION_LOG provisioned ad-hoc

`AF_SESSION_LOG` was declared in `factory/scripts/_session_log.py`, documented in `factory/docs/factory-guide.md` and `factory/docs/proposals/session-log-addendum.md`, but never provisioned by any mechanism until the orchestrator's `_provision_session_log()` was added late in the session.

**Fix:** Create `factory/docs/env-vars.md` listing every env var: name, purpose, who provisions it, who reads it, default value. Today only `AF_SESSION_LOG` exists. The registry prevents the same gap from recurring as the system grows.
