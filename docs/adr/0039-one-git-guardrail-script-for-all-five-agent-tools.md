---
id: 0039
status: proposed
evaluation: pugh-matrix
---

# One git guardrail script for all five agent tools

## Context

The git guardrail runs before every shell command an agent issues. It refuses the commands that destroy work or skip a gate. The run lifecycle adds two refusals: an agent may not run `dispatch return-story` or `dispatch close --drop`, because both destroy work and are always the human's decision.

The Factory supports five agent tools: Claude Code, Codex, Copilot CLI, pi, and OpenCode. Claude Code, Codex, and Copilot CLI call `config/hooks/block-dangerous-git.sh` from their native `PreToolUse` hook. pi uses its own TypeScript copy, `config/extensions/block-dangerous-git.ts`, which holds its own rules and has drifted from the script. OpenCode has no git guardrail.

Take an agent in pi that issues `bash -c "dispatch close --drop"`. Whether pi refuses it depends on a second rule set that nobody keeps in step with the script. Three options were weighed:

- **A: One rule set per tool** (baseline). Each tool keeps or gets its own rules.
- **B: One script, thin entries.** Every tool calls `block-dangerous-git.sh`. pi's extension and OpenCode's plugin pass the command to the script and return its answer, as `guard-human-fields` does under [ADR-0035](0035-guard-human-fields-in-every-cli.md).
- **C: One rule file, five interpreters.** A shared data file lists the patterns, and each tool's own code matches commands against it.

Option C keeps the patterns in one place, but the matching does not fit into data. Finding a `dispatch` call after `&&`, after `;`, or inside `bash -c` takes code, and five copies of that code drift the way pi's copy did.

## Decision

Option B.

| Criterion                                                                       | Weight | A: One rule set per tool (baseline) | B: One script, thin entries | C: One rule file, five interpreters |
| ------------------------------------------------------------------------------- | ------ | ----------------------------------- | --------------------------- | ----------------------------------- |
| Controllability (QS-29): every tool refuses the same commands in the same forms | 3      | 0                                   | +1                          | 0                                   |
| Maintainability: a fix to a rule changes one file                               | 2      | 0                                   | +1                          | 0                                   |
| Testability (QS-3): the rules have one test suite                               | 2      | 0                                   | +1                          | 0                                   |
| Cost: one extra process per guarded call in pi and OpenCode                     | 1      | 0                                   | −1                          | 0                                   |
| **Weighted total**                                                              |        | **0**                               | **+6**                      | **0**                               |

B wins clearly. No change of weight within the scale brings A or C level with it.

The entries are these:

| Tool                        | Entry                                                                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claude Code, Codex, Copilot | The native `PreToolUse` hook runs the script with the command JSON on standard input.                                                                  |
| pi                          | `config/extensions/block-dangerous-git.ts` passes each bash command to the script.                                                                     |
| OpenCode                    | `execute.before` of `config/plugins/agent-factory.ts` passes the command of each `shell` call and the JavaScript of each `execute` call to the script. |

The pi extension and the OpenCode entry hold no rule of their own. They block the call when the script refuses it. The script finds the run of a folder from the folder's branch, so a ledger of another branch never counts.

## Consequences

- A rule changes in one file, and the test of each entry only checks that the entry passes the command and returns the answer.
- pi starts one process per bash call, and OpenCode one per `shell` or `execute` call.
- OpenCode's `execute` tool runs JavaScript that can start a process, as the guard of [ADR-0035](0035-guard-human-fields-in-every-cli.md) already assumes. So the entry passes that JavaScript to the script as command text, and the guardrail holds in all five tools without an accepted gap.
- The script reads the command text and expands no variable. So `sub=return-story; dispatch $sub ST-0350` passes, as the feature file states (OI-11). The human watches a run and can undo any step that the guardrail lets through, except the two it refuses.
- The OpenCode entry needs a test in a real OpenCode session, not a mock (OI-07). The User starts it through the manual pre-commit hook `run-opencode-session-test`, and it checks a `shell` call and an `execute` call.
- [5.13](../arc42/05_building_block_view.md#513-level-2-component-view----run-lifecycle) lists the entries, and [6.25](../arc42/06_runtime_view.md#625-the-git-guardrail-in-every-agent-tool) shows a refusal.
