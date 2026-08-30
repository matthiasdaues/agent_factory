---
id: COPILOT-PRETOOLUSE-SPIKE
title: Copilot CLI `PreToolUse` surface for step-guard
status: resolved
source: spike
created: 2026-08-26
---

# Copilot CLI `PreToolUse` event surface spike

## Sources checked

- `factory/config/hooks/block-dangerous-git.sh`
- `factory/config/hooks/block-dangerous-git.json`
- `.github/hooks/block-dangerous-git.sh`
- GitHub Docs: `content/copilot/how-tos/copilot-sdk/hooks/pre-tool-use.md`
- GitHub Docs: `content/copilot/how-tos/copilot-sdk/features/hooks.md`
- VS Code Copilot SDK source: `src/vs/platform/agentHost/node/copilot/copilotAgentSession.ts`
- VS Code Copilot SDK source: `src/vs/platform/agentHost/node/copilot/copilotToolDisplay.ts`
- `docs/proposals/superseded/artifact-pipeline-discipline.md`

## 1. Event envelope

Copilot CLI exposes a `preToolUse` hook with a JSON payload that includes:

```json
{
  "timestamp": 1234567890,
  "cwd": "/repo/root",
  "toolName": "read_file",
  "toolArgs": {
    "path": "docs/spec/prd.md"
  }
}
```

The documented input fields are `timestamp`, `cwd`, `toolName`, and
`toolArgs`. The repo's existing hook adapter already demonstrates that the
payload is consumed through `toolArgs` rather than Claude Code's `tool_input`.

## 2. Schema for Read, Edit, Write

For the file-oriented tools, the hook surface is the same shape and the file
path sits at `toolArgs.path`:

| Tool call | `toolName` example       | `toolArgs` shape  | File path field |
| --------- | ------------------------ | ----------------- | --------------- |
| Read      | `read_file` or `view`    | `{ "path": "…" }` | `toolArgs.path` |
| Edit      | `edit`                   | `{ "path": "…" }` | `toolArgs.path` |
| Write     | `write_file` or `create` | `{ "path": "…" }` | `toolArgs.path` |

The VS Code Copilot SDK source confirms that file tools resolve edit paths from
`toolArgs.path`, and that edit tracking treats `edit` / `create` as file tools.

## 3. jq-extractable path

Yes. The path is extractable with `jq` as:

```bash
jq -r '.toolArgs.path'
```

That is sufficient for read/write guardrails that need the target path before
allowing the tool call.

## 4. Differences from Claude Code

The shared adapter still needs normalization because the hook payloads are not
isomorphic:

- Claude Code uses `PreToolUse`; Copilot CLI uses lowercase `preToolUse` in
  its hook config.
- Claude Code guardrail payloads route through `tool_input`; Copilot CLI uses
  `toolArgs`.
- Claude Code examples in this repository read file paths from
  `.tool_input.file_path`; Copilot CLI file tools expose `toolArgs.path`.
- Tool naming differs: Copilot docs show `read_file` / `write_file`, while the
  SDK source also treats `view`, `edit`, and `create` as file tools.
- Copilot's hook input includes `cwd`; the adapter should not rely on a Claude
  Code-only field name.

## 5. Feasibility conclusion

Shared adapter approach: **feasible**.

`step-guard` can consume Copilot CLI `PreToolUse` events after a small
normalization layer maps the file-tool names and extracts `toolArgs.path`.
No new transport is required; the only work is adapter logic for field and tool
name normalization.
