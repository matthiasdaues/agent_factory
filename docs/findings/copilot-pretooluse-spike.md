# Copilot CLI `preToolUse` event surface spike

## Sources checked

- `factory/config/hooks/block-dangerous-git.sh`
- `factory/config/hooks/block-dangerous-git.json`
- `.github/hooks/pre-push`
- `factory/scripts/init-factory`
- `docs/spec/use_cases/UC-07-block-a-dangerous-git-command.md`
- `docs/spec/supplementary_specs/interface-contracts.md`
- `docs/spec/supplementary_specs/mechanized-dispatch.md`
- GitHub Copilot CLI docs and cached SDK package `1.0.80`

## 1. Event surface documentation

Copilot CLI exposes a hook surface that can fire before tool execution.
The public SDK handler is `onPreToolUse(input, invocation)`, where:

- `input.toolName` is the tool name
- `input.toolArgs` is the tool argument object
- `input.timestamp` and `input.workingDirectory` are also supplied

The underlying hook transport uses a `HookType` of `preToolUse` and carries
an opaque `input` payload.

In this repository, the existing hook pattern is:

- shell adapter under `factory/config/hooks/block-dangerous-git.sh`
- Copilot hook config under `factory/config/hooks/block-dangerous-git.json`
- repo hook wiring under `.github/hooks/`

`block-dangerous-git.sh` is the useful pattern: read JSON from stdin, use `jq`
to normalize runtime-specific fields, and emit allow/deny behavior without
needing the caller to know the CLI-specific payload shape.

## 2. JSON schema

The confirmed Copilot hook surface is not a single rigid JSON schema for all
tools; it is an SDK callback contract with a shared wrapper and tool-specific
`toolArgs`.

Confirmed fields:

- `toolName`
- `toolArgs`
- `timestamp`
- `workingDirectory`

Observed field access patterns from the SDK docs:

- Bash: `toolArgs.command`
- Read/edit file tools: `toolArgs.path`
- The write/permission prompt schema uses `fileName`, but that is a separate
  permission-request payload, not the `preToolUse` hook input

Repo-side Copilot wiring also uses lowercase `preToolUse` in JSON config, not
Claude Code's `PreToolUse`.

## 3. Feasibility assessment

Yes — `step-guard` can consume Copilot CLI `preToolUse` events with `jq`.
The file path is extractable from `toolArgs.path` for file tools, and shell
commands remain extractable from `toolArgs.command`.

The main difference from Claude Code is naming and nesting:

- Claude Code: `.claude/settings.json` uses `hooks.PreToolUse`
- Copilot CLI: the documented SDK handler uses `toolName` + `toolArgs`
- Copilot file tools are documented as `create` / `edit` in examples, not as a
  literal `Write` tool name
- Copilot hook config uses lowercase `preToolUse`

So the shared adapter is feasible, but it must normalize Copilot's tool names
and field paths before `step-guard` sees them.

## 4. Adapter requirements

Minimal adapter logic:

1. Read the Copilot hook JSON from stdin.
2. Match `toolName` against the tool class.
3. Normalize file tools:
   - `read` → read path from `toolArgs.path`
   - `edit` / `create` → write-class path from `toolArgs.path`
4. Normalize shell tools:
   - `bash` → command from `toolArgs.command`
5. Emit the normalized event shape that `step-guard` expects.

No extra adapter is needed for the event transport itself; the only required
work is field normalization and tool-name mapping.

## Conclusion

Copilot CLI exposes a usable `preToolUse` surface for `Read`, `Edit`, and the
file-creation/write path. `step-guard` can consume it with a small adapter
that normalizes `toolName` and extracts `toolArgs.path` / `toolArgs.command`
via `jq`.
