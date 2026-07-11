# Interface Contracts — Factory Flow Control

Command-line contract for every script this specification covers: inputs, flags, outputs, and exit codes. All scripts are stdlib-only Python 3.8+; none requires a virtualenv.

## `factory/scripts/transition-lint`

|               |                                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `transition-lint [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--format text\|json] [--report-only]`                    |
| Reads         | `.agent-factory/playbook-state.yml` (or `--marker`); `git diff --cached --name-only`; the marker's playbook `.fsm.yml`             |
| Writes        | Nothing — read-only                                                                                                                |
| Exit code     | Count of error-severity findings (`0` = clean), unless `--report-only` (always `0`)                                                |
| Finding codes | `TL-NOMARKER` (info), `TL-MARKER` (error — missing `playbook`/`state`), `TL-NOFSM` (error), `TL-STATE` (error), `TL-ORDER` (error) |

See [UC-02](../use_cases/UC-02-block-an-out-of-phase-commit.md).

## `factory/scripts/phase advance`

|               |                                                                                                        |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Usage         | `phase advance [--by NAME] [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--playbook NAME]`  |
| Reads         | The marker (if present); the target `.fsm.yml`; `docs/findings/**` (for `no_open_findings` conditions) |
| Writes        | The marker, only on success                                                                            |
| Exit code     | `0` on success; `1` on refusal (unmet conditions, terminal state, missing FSM)                         |
| stdout/stderr | Success message to stdout; refusal message (with every unmet condition) to stderr                      |

See [UC-01](../use_cases/UC-01-advance-a-playbook-phase.md).

## `factory/scripts/phase retry`

|               |                                                                                                    |
| ------------- | -------------------------------------------------------------------------------------------------- |
| Usage         | `phase retry [--repo-root DIR] [--marker PATH] [--playbooks-dir DIR] [--default-max-iterations N]` |
| Reads         | The marker (required — errors if absent); the target `.fsm.yml`'s `halt_conditions`                |
| Writes        | The marker, only when the retry is allowed                                                         |
| Exit code     | `0` allowed; `1` no marker; `2` cap exceeded                                                       |
| stdout/stderr | Success message to stdout; refusal (with cap and any declared `message`) to stderr                 |

See [UC-03](../use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md).

## `factory/scripts/trigger`

|                 |                                                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage           | `trigger agent <name> [--background\|--interactive] [--cli claude\|copilot] [--cwd DIR]`                                                                |
|                 | `trigger playbook <name> --step <agent-name-or-index> [--background\|--interactive] [...]`                                                              |
|                 | `trigger list`                                                                                                                                          |
| Reads           | `factory/INDEX.yaml`'s source data (via `index-lint`'s loaders); `config/model.conf` (via `matrix-lint`'s parser); the resolved agent's definition file |
| Writes          | Nothing of its own — the dispatched CLI subprocess writes whatever its own session produces                                                             |
| Exit code       | The invoked CLI's own exit code (`--background`); `0` after printing launch instructions (`--interactive`); `2` on a resolution error                   |
| Default `--cli` | `claude`                                                                                                                                                |

See [UC-04](../use_cases/UC-04-dispatch-an-agent-via-trigger.md).

## `factory/scripts/index-lint`

|           |                                                                                                    |
| --------- | -------------------------------------------------------------------------------------------------- |
| Usage     | `index-lint [--agents-dir DIR] [--skills-dir DIR] [--playbooks-dir DIR] [--out PATH] [--check]`    |
| Reads     | `factory/agents/*.md`, `factory/skills/*/SKILL.md`, `factory/playbooks/*.md` frontmatter and prose |
| Writes    | `factory/INDEX.yaml` (or `--out`), unless `--check` or content is unchanged                        |
| Exit code | `0` if up to date (now or already); `1` in `--check` mode if it was stale                          |
| stderr    | One `[WARNING]` line per agent missing `phase-name` or skill missing `category`                    |

See [UC-06](../use_cases/UC-06-regenerate-the-catalog.md).

## `factory/config/hooks/block-dangerous-git.sh`

|            |                                                                                                           |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| Invocation | `PreToolUse`/`preToolUse` hook, both CLIs; command JSON on stdin                                          |
| Reads      | `.tool_input.command` (Claude Code) or `.toolArgs.command` (Copilot CLI), via `jq`                        |
| Writes     | Deny reason to stderr; `{"permissionDecision":"deny","permissionDecisionReason":"..."}` to stdout on deny |
| Exit code  | `0` allow; `2` deny (both CLIs' shared convention)                                                        |

See [UC-07](../use_cases/UC-07-block-a-dangerous-git-command.md).

## `factory/scripts/init-factory`

|               |                                                                                                                                                                             |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage         | `init-factory [--source DIR] [--target DIR]`                                                                                                                                |
| Reads         | The source checkout's `factory/`; the target's existing `.gitignore`, `.claude/settings.json`, `.pre-commit-config.yaml`, `config/model.conf`, if present                   |
| Writes        | `factory/` (copy, once), `.gitignore` (merge), `.claude/`, `.github/` (symlinks + settings), `config/model.conf` (copy, once), `.pre-commit-config.yaml` (symlink or merge) |
| Exit code     | `0` on success, including a clean no-op re-run; `1` on any collision or unsupported existing state                                                                          |
| stdout/stderr | One `init-factory: <line>` report line per step; `init-factory: STOPPED — <reason>` on collision                                                                            |

See [UC-08](../use_cases/UC-08-initialize-agent-factory-into-a-project.md).

## Referenced from

- [entity-model.md](entity-model.md)
- [validation-rules.md](validation-rules.md)
- [use_cases/system-use-cases.md](../use_cases/system-use-cases.md)
