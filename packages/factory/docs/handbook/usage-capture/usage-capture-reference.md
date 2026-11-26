---
title: Usage capture reference
type: reference
status: implemented
order: 40
description: The capture trigger and the accounting rule of each CLI, and the test file that owns each capture contract.
---

# Usage capture reference

[How usage capture works](usage-capture.md) explains the pipeline.

## Triggers and accounting per CLI

| CLI                | Human or root trigger              | Child trigger                                          | Accounting rule                                                                                                                                                        |
| ------------------ | ---------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code        | `Stop` in `.claude/settings.json`  | `SubagentStop`                                         | The latest cumulative root record leaves out the children's internal messages and usage. Add each distinct child record once.                                          |
| GitHub Copilot CLI | `agentStop` under `.github/hooks/` | `subagentStop` for supported custom agents             | Select the latest cumulative root snapshot. It includes the children, so child records only attribute usage. The built-in `general-purpose` agent sends no child hook. |
| Codex              | `Stop` in `.codex/hooks.json`      | `SubagentStop`                                         | The latest cumulative root snapshot includes the children, so child records only attribute usage.                                                                      |
| Pi                 | `session_shutdown` extension       | Inline at each child of `run_agent` or `dispatch_wave` | The root leaves out the spend of separate subprocesses. Add every distinct descendant record once.                                                                     |

Claude Code `Stop` records are cumulative snapshots of the main transcript. `SubagentStop.transcript_path` points to the main transcript, so capture reads the required `agent_transcript_path` instead. That file holds the child's internal messages and the provider usage per message. The text of a task and its result can appear in both records, because it entered both model contexts. That is real normalized usage, not a duplicate of the totals.

## Test ownership

Each test file owns one layer and one contract boundary. A new capture case goes into the file that owns its boundary. A new file appears only for behaviour of a new layer.

> Rule summary: A regression strengthens the existing owner before it creates another case.
> Source: [testing-strategy.md § One contract, one owner](../../../rulebooks/conventions/testing-strategy.md#one-contract-one-owner)

| Test file                                    | Layer                 | Contract boundary                                                                                                                                   |
| -------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_usage_capture.py`                      | Unit and component    | Transcript parsing, normalization, aggregation, record reservation, and storage primitives                                                          |
| `test_usage_capture_e2e.py`                  | Installed shared path | A configured hook reaches the shared capture runtime and writes a normalized record                                                                 |
| `test_usage_capture_copilot_e2e.py`          | Copilot adapter       | Copilot hook payloads, accounting with a root that includes the children, and child attribution                                                     |
| `test_usage_capture_codex_e2e.py`            | Codex adapter         | Codex hook payloads, installation gated by trust, and accounting with a root that includes the children                                             |
| `test_usage_capture_pi_e2e.py`               | Pi adapter            | The handoff from extension to bootstrap, descendant aggregation, ownership by the supervisor, and cleanup after a failure                           |
| `test_usage_capture_native_lifecycle_e2e.py` | Shared lifecycle      | Detached registration, drain and cancel, the generation fence, cleanup of accepted workers, and races with an uninstall, across the native adapters |
| `test_init_factory_usage_capture.py`         | Installation          | The assets of each CLI, permissions, runtime provisioning, idempotency, and the capability probes                                                   |
| `test_remove_factory.py`                     | Removal               | Exact removal of the factory's hooks, the policy for pending captures, and the project's own configuration kept                                     |

The table records ownership, not a target number of tests. End-to-end tests with distinct contracts still have their place when they run shared lower-level code.
