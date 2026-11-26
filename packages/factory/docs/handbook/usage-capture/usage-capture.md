---
title: How usage capture works
type: concept
status: implemented
order: 10
description: How the factory records the token use of each session, where it stores records and transcripts, and how capture stays out of your way.
---

# How usage capture works

You want to know how many tokens a session or a playbook run consumed. Agent Factory records the runtime token use of Claude Code, GitHub Copilot CLI, Codex, and Pi. Every capture site calls the same pipeline, `.agent-factory/factory/scripts/usage-capture`. The pipeline has three parts: a normalizer for the transcript of each CLI, the fixed comparison tokenizer tiktoken `cl100k_base`, and a logging adapter that only appends JSONL.

## Records and transcripts

Each capture appends one record to `.agent-factory/usage/<session-key>.jsonl`. The session key holds the time of the session's first capture and stays the same for the whole session.

Each transcript of a session forms a chain: the main transcript is one chain, and each subagent transcript is one more. The record names its chain in the field `chain`. Each chain is stored once, under `.agent-factory/usage/transcripts/<session-key>/`:

- `<chain>.jsonl` holds the tokenized text.
- `<chain>.structured.jsonl` holds the CLI's own transcript.

A capture appends only the bytes that are new since the last capture of the chain. Its `transcript_ref` holds the half-open byte range of its own turn, in `byte_range` and `structured_byte_range`. Bytes 0 to `end` hold the transcript as it stood at that capture. When the CLI rewrites a transcript, for example by compaction, the capture starts a new chain file `<chain>.2.jsonl`. The existing ignore rule `/.agent-factory/` covers the whole runtime area. [Migrate old usage transcripts](migrate-usage-transcripts.md) converts the stores of version 1.13.0 and earlier, which kept a full copy per capture.

Every record holds `project_id`, `project_name`, `normalized_input`, `normalized_output`, and the derived total. The provider fields `reported_*` and `usage_granularity` are null when the transcript holds no provider breakdown. [Usage capture reference](usage-capture-reference.md) lists the trigger and the accounting rule of each CLI.

## Project identity

Initialization asks for a project name, and automation passes it with `--project-name`. The installer generates a stable UUID and writes both values to the git-ignored `.agent-factory/config/project.json`. [Files that init-factory creates](../reference/local-configuration.md) describes that file. A new run of initialization keeps both values.

## The tokenizer runtime

`init-factory` prepares the tokenizer before it wires the capture hooks. It installs exact wheels with checked hashes into the owner-only folder `.agent-factory/usage/runtime`, with builds and Python downloads turned off. With `UV_OFFLINE=1`, the initialization runs offline, and capture is turned on only when every checked artifact is already available.

A missing or invalid artifact leaves the rest of the factory setup intact, and the installer reports capture as unavailable. Lifecycle hooks never run uv or read its cache. A new run of init checks the committed dependency set again. `remove-factory` deletes the runtime after the pending captures of every adapter finish.

## Storage safety

Session and record identifiers are opaque data. A short lowercase identifier keeps its familiar filename. An unsafe, platform-specific, Unicode, or oversized value gets a fixed filesystem key built from a digest, and its original value stays in the JSON record. Capture refuses storage paths with a symlink in them, and it never changes bytes that a record already points at.

Usage storage is private. The factory's runtime folders get mode `0700` and its files mode `0600`, whatever the umask, and capture repairs existing safe paths it owns. [Configure transcript retention](configure-transcript-retention.md) explains how to store no transcript text at all.

Records and transcripts stay until you delete their session by hand or `remove-factory` runs. No automatic expiry applies. Pi's owner-only staging copy is deleted right after processing. Capture supports no regex redaction, and token counting cannot be turned off.

## Concurrent captures

Two captures of one session can run at the same time. Each takes the session lock, a file lock on `transcripts/<session-key>/.lock`, before it reserves a record. So the record sequence counts up without gaps and gives the order of the captures. A capture that crashes after its chain append leaves bytes that no record points at. The next capture of the chain cuts them off before it appends. The usage analysis keeps the latest snapshot per `(cli, session_id, chain)`.

## Capture never blocks the session

Capture is best effort. A direct call reports errors on stderr and still returns success, and the native lifecycle adapters may hide those errors too. A failed capture never changes how a session ends or what a tool returns.

Claude Code, Codex, and Copilot hooks share one lifecycle. Before a hook returns, it registers the capture and takes a private snapshot of the provider transcript. A detached supervisor then normalizes and stores it. The snapshot takes time in proportion to the size of the transcript, and no tokenization or storage blocks the hook. The hooks of these three CLIs run no Node code. Only Pi capture uses Node, as the bootstrap below describes.

Codex project hooks stay inactive until you trust their current definitions. After `init-factory`, open Codex's `/hooks` view and approve the installed project hooks. `init-factory` reports this step on a fresh installation and on each new run. Writing the files does not turn them on: Codex skips a new or changed hook definition until you review and trust it again.

## Pi

A human session under Pi captures once, at a graceful `session_shutdown`. A child that `run_agent` or `dispatch_wave` starts captures inline, and its own shutdown extension is turned off, so no record appears twice. Both tools attach the nesting depth and the session id of the active parent. A shared resolver finds the session: first Pi's active session file, then the child-session environment, then a fallback that stays the same for the process.

A separate Pi subprocess's model calls are not part of its parent's provider totals or normalized totals. So a Pi total adds the human or root record and every distinct descendant record exactly once. The text of a task and its result can appear in both records, because both model calls consumed it.

All processes of one Pi call tree share one checked usage root: the project's primary checkout, found through Git's shared common folder. So captures land under the primary checkout even when a nested agent runs in a throwaway dispatch worktree. An inherited root counts only when it agrees with the checkout found independently and with its factory installation. An invalid value falls back to the root found from the repository.

Pi writes the finished stream to the private capture scratch folder of that root, as a durable handoff. Then it starts a factory-owned capture supervisor through the provisioned Python runtime, with no interactive standard streams. So tokenization and storage never delay a human shutdown or the result of `run_agent` or `dispatch_wave`. Only the local durable staging write stays synchronous.

The supervisor waits outside the measured lifecycle. After the capture child ends, it alone removes the checked pending or committing marker, the private completion status, and the staged source. A failed capture child leaves a short diagnostic in the private usage control tree, and the diagnostic holds no transcript text. When an uninstall cancels a capture with `--pending-usage=cancel`, the supervisor stops without an error, and it creates no removed factory path again. When the supervisor or the host shuts down abruptly, an in-flight capture can still be lost.

A small Node bootstrap runs only until the Python supervisor writes a private acceptance handshake. This closes the window at startup in which the interpreter could disappear. When the launcher fails or times out before the acceptance, the bootstrap cleans up the checked registration and records a short diagnostic. A cancellation or removal stays quiet and cannot create paths again. After the acceptance, the bootstrap exits, and Python stays the only capture supervisor.

## Removal and pending captures

`remove-factory` coordinates with the detached captures of every adapter. Its default `--pending-usage=drain` waits up to `--pending-timeout` seconds for every capture registered before the removal to commit. When the time runs out, it restores the active installation and exits non-zero without uninstalling. `--pending-usage=cancel` discards registered captures that have not started to commit.

A generation fence stops new registrations once the removal owns the project, and late workers cannot create `.agent-factory` again. `remove-factory` sends no signal to any process. Finished usage records and transcripts belong to the factory's footprint, and a successful uninstall deletes them. `remove-factory` removes the factory's hook assets and its exact merged entries, and it keeps the project's own configuration.

The registration fence relies on hard links on the same volume. Each pending token takes an atomic snapshot of the lifecycle state before its metadata replaces the token's contents. `init-factory` tests whether the project filesystem supports this. When it does not, the setup of Claude Code, Copilot, Codex, and the other Pi assets still completes. Init and the Pi runtime then report that race-safe Pi usage capture is unavailable, instead of falling back to an unsafe fence.

The ADR "Normalize runtime usage through CLI adapters" (ADR-0007) in the Agent Factory repository records the reasons for this design.
