---
title: usage-capture
type: reference
status: implemented
description: Normalize and count tokens from a CLI transcript.
---

# usage-capture

## Name

`usage-capture` — Normalize and count tokens from a CLI transcript.

## Synopsis

```text
.agent-factory/factory/scripts/usage-capture [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `--cli`. claude-code | copilot | codex | pi
- `--transcript`. path to the CLI's own transcript file
- `--session`
- `--chain`. name of the measured transcript within the session, such as the stem of the CLI's transcript file; defaults to the agent or 'main'
- `--parent-session`
- `--depth`
- `--agent`
- `--model`
- `--provider`. provider identity qualifying native per-turn usage semantics
- `--branch`
- `--commit`
- `--exit-status`
- `--transcript-retention`
- `--delete-source`. delete --transcript after capture only when it is a regular, non-symlink file directly under .agent-factory/usage/.capture
- `--pending-marker`
- `--usage-generation`
- `--cleanup-owner`
- `--completion-status`

## See also

- [Command source](../../../scripts/usage-capture)
- [Workflow guide](../usage-capture/usage-capture.md)
