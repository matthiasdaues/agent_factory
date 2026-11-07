---
id: 0035
status: accepted
evaluation: pugh-matrix
---

# Guard the human fields in every CLI

## Context

Some values in a finding only the stakeholder may write: a non-null
`override_by`, `override_reason`, `stop_confirmed_by`, or
`stop_confirmed_reason`, and the status `waived`. These are the human fields.
Take a headless run that a `critical` finding stops. The orchestrator tries to
write `stop_confirmed_by: human` into the finding file to finish the run. If
the edit goes through, the run continues, and nobody has run the damage
checks. `finding-lint` checks that the fields hold text, but it cannot tell
who wrote them. So the hook `guard-human-fields` refuses an agent call that
sets a human field (DEC-42), and it must run in every CLI the Factory
supports: Claude Code, Codex, Copilot CLI, Pi, and OpenCode (DEC-51).

The hooks that exist today left three gaps:

- Claude Code had no guard entry for `MultiEdit` and `NotebookEdit`.
- A patch call names its paths inside the patch text, so a path check on the
  call alone misses them. Codex, Copilot CLI, and Pi have `apply_patch`, and
  OpenCode has `patch`.
- OpenCode had no Factory plugin on `dev`. The OpenCode CLI feature defines
  the full plugin `packages/factory/config/plugins/agent-factory.ts`, but it
  has not shipped.

[ADR-0019](0019-v2-plugin-as-opencode-enforcement-boundary.md) makes the
OpenCode V2 plugin the place where every Factory control runs in OpenCode,
through `execute.before` and the other plugin hooks. So the OpenCode gap had
three answers: write the plugin now with the guard only, wait for the
OpenCode CLI feature, or ship a separate plugin for the guard alone.

## Decision

`guard-human-fields` is one hook script in `packages/factory/config/hooks/`.
Each CLI calls it from its own hook for edit, write, and shell calls (DEC-61):

| CLI         | Entry point                                                                               | Calls guarded                                                  |
| ----------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Claude Code | `PreToolUse` entries in `.claude/settings.json`                                           | `Edit`, `MultiEdit`, `Write`, `NotebookEdit`, `Bash`           |
| Codex       | `PreToolUse` entries in `.codex/hooks.json`                                               | `Edit`, `Write`, `apply_patch`, `Bash`                         |
| Copilot CLI | `preToolUse` entries in a hook file under `.github/hooks/`, as `step-guard.json` does     | `edit`, `apply_patch`, `write_file`, `create`, `bash`          |
| Pi          | The `tool_call` event of a project-local extension                                        | `edit`, `write`, `write_file`, `create`, `apply_patch`, `bash` |
| OpenCode    | `execute.before` of the Factory plugin `packages/factory/config/plugins/agent-factory.ts` | `edit`, `write`, `patch`, `shell`, `execute`                   |

A patch call names its paths inside the patch text: `apply_patch` in Codex,
Copilot CLI, and Pi, and `patch` in OpenCode. So in every CLI the guard reads
the paths and the removed and added lines from the patch text. It refuses a
patch that it cannot parse when the raw text names a guarded path. The
OpenCode tool `execute` runs JavaScript that can call the other tools, so the
guard checks that JavaScript as the text of a shell call. Pi and OpenCode block the call when the guard script is
missing, so a broken install refuses the edit. The Pi extension
`step-guard.ts` lets a call through in that case. The guard does not.

This feature writes the first version of the OpenCode plugin, and that
version holds only the guard. `init-factory` accepts the CLI name `opencode`
and links the plugin into `.opencode/plugins/`.

| Criterion                                                                         | Weight | Wait for the OpenCode feature (baseline) | Guard-only first plugin | Separate guard plugin |
| --------------------------------------------------------------------------------- | ------ | ---------------------------------------- | ----------------------- | --------------------- |
| Safety (QS-7, QS-25): an OpenCode agent cannot write a human field                | 3      | 0                                        | +1                      | +1                    |
| Clean Architecture: the rule stays in one script, and each CLI adds only an entry | 2      | 0                                        | 0                       | 0                     |
| Simplicity: the scope this feature adds to the installer and the plugin           | 2      | 0                                        | −1                      | −1                    |
| One Factory plugin file in OpenCode later                                         | 2      | 0                                        | 0                       | −1                    |
| **Weighted total**                                                                |        | **0**                                    | **+1**                  | **−1**                |

The guard-only first plugin wins by one point. A higher weight on the scope
criterion would tie it with waiting. Waiting leaves every OpenCode agent free
to write human fields until the OpenCode CLI feature ships.

This decision builds on ADR-0019. It neither supersedes nor amends it: the
guard runs through `execute.before` of the V2 plugin, as ADR-0019 sets for
every control, and it fails closed, as QS-7 asks. ADR-0019 keeps its status.

## Consequences

- One guard rule runs behind five entry points, so a fix to the rule changes
  one script. Each entry point needs its own test, because each CLI passes the
  call in its own shape.
- The OpenCode CLI feature extends `agent-factory.ts` instead of creating it.
  Its stories add the Permission Enforcer and the other components to the
  same file and keep the guard. `init-factory` already accepts `opencode`
  when that feature starts.
- The OpenCode test FC-18-LN-03 can run once the first plugin exists.
- The guard checks the text of each call, as `block-dangerous-git.sh` does.
  An agent that hides the field name gets past it, for example with a field
  name built from pieces in a script, a `cp` of a prepared file, or
  `git checkout <ref> -- <file>`. The design for that class is deferred to
  the gate-evidence proposal.
- `init-factory` writes the entries of Claude Code, Codex, Copilot CLI, and
  Pi beside the `step-guard` entries. `update-factory` runs `init-factory`
  of the new release, so a project installed earlier gets the missing
  entries.
- The OpenCode tool names come from the OpenCode tools documentation
  (`opencode.ai/docs/tools`), read on 2026-11-07. OpenCode exposes `patch`
  only for some GPT models and `edit` and `write` for the others. The
  guard covers all five tools, so the model choice does not matter.
- A broken Pi or OpenCode install refuses every guarded edit until the guard
  script is back. The refusal names the missing script.
- [5.12](../arc42/05_building_block_view.md#512-level-2-component-view----finding-classification)
  lists the entry points, [6.18](../arc42/06_runtime_view.md#618-the-guard-refuses-a-human-field)
  shows a refusal, and QS-25 in
  [chapter 10](../arc42/10_quality_requirements.md#qs-25-no-agent-writes-a-human-field)
  sets the measure.
