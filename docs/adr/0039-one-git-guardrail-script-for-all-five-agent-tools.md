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

| Criterion                                                             | Weight | A: One rule set per tool (baseline) | B: One script, thin entries | C: One rule file, five interpreters |
| --------------------------------------------------------------------- | ------ | ----------------------------------- | --------------------------- | ----------------------------------- |
| Safety (QS-6): every tool refuses the same commands in the same forms | 3      | 0                                   | +1                          | 0                                   |
| Maintainability: a fix to a rule changes one file                     | 2      | 0                                   | +1                          | 0                                   |
| Testability (QS-3): the rules have one test suite                     | 2      | 0                                   | +1                          | 0                                   |
| Cost: one extra process per shell call in pi and OpenCode             | 1      | 0                                   | −1                          | 0                                   |
| **Weighted total**                                                    |        | **0**                               | **+6**                      | **0**                               |

B wins clearly. No change of weight within the scale brings A or C level with it.

The entries are these:

| Tool                        | Entry                                                                                          |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| Claude Code, Codex, Copilot | The native `PreToolUse` hook runs the script with the command JSON on standard input.          |
| pi                          | `config/extensions/block-dangerous-git.ts` passes each bash command to the script.             |
| OpenCode                    | `execute.before` of `config/plugins/agent-factory.ts` passes each shell command to the script. |

The pi extension and the OpenCode entry hold no rule of their own. They block the call when the script refuses it. The script finds the run of a folder from the folder's branch, so a ledger of another branch never counts.

## Consequences

- A rule changes in one file, and the test of each entry only checks that the entry passes the command and returns the answer.
- pi and OpenCode start one process per shell call.
- The script reads the command text and expands no variable. So `sub=return-story; dispatch $sub ST-0350` passes, as the feature file states (OI-11). The human watches a run and can undo any step that the guardrail lets through, except the two it refuses.
- The OpenCode entry needs a test in a real OpenCode session, not a mock (OI-07).
- [5.13](../arc42/05_building_block_view.md#513-level-2-component-view----run-lifecycle) lists the entries, and [6.25](../arc42/06_runtime_view.md#625-the-git-guardrail-in-every-agent-tool) shows a refusal.
