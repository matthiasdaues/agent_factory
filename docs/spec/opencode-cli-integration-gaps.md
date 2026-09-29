# Gaps Report: opencode-cli-integration

Generated: 2026-09-21
Source: docs/proposals/opencode-cli-integration.md

## Actor-Goal Matrix

| Actor              | Goal                                              | Rule                                                                      | Status    |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------------------------- | --------- |
| Project maintainer | Install Factory for OpenCode CLI                  | Rule: Project maintainer installs Factory for OpenCode CLI                | specified |
| Project maintainer | Update an existing OpenCode integration           | Rule: Project maintainer updates an existing OpenCode integration         | specified |
| Project maintainer | Remove Factory OpenCode files cleanly             | Rule: Project maintainer removes Factory OpenCode files cleanly           | specified |
| Project maintainer | Run OpenCode alongside other Factory CLIs         | Rule: Project maintainer runs OpenCode alongside other Factory CLIs       | specified |
| OpenCode user      | Enter Factory through plugin-injected orientation | Rule: OpenCode user enters Factory through plugin-injected orientation    | specified |
| OpenCode user      | Discover agents and skills through native paths   | Rule: OpenCode user discovers agents and skills through native paths      | specified |
| Factory plugin     | Enforce permissions and step boundaries           | Rule: Factory plugin enforces permissions and step boundaries             | specified |
| Factory plugin     | Capture completed session usage                   | Rule: Factory plugin captures completed session usage                     | specified |
| Factory plugin     | Isolate child sessions in worktrees               | Rule: Factory plugin isolates child sessions in Factory-managed worktrees | specified |
| Fitting operator   | Configure OpenCode model tiers                    | Rule: Fitting operator configures OpenCode model tiers                    | specified |

## Missing Rules

No missing Rules. All actor-goal pairs from the proposal have a corresponding Rule.

## Rules Without Scenarios

No Rules without Scenarios. Every Rule has at least one Scenario.

## Ambiguous Wording

| Location | Step Text | Issue | Suggested Fix                 |
| -------- | --------- | ----- | ----------------------------- |
| —        | —         | —     | No ambiguous wording detected |

## Open Questions From Proposal

The proposal carries four open questions that affect specification completeness. None blocks the planning phase, but each may require scenario revision after empirical testing against the target OpenCode version.

1. **`execute.before` denial contract** — The `execute.before` hook's return type is `void | Promise<void>` in the official documentation, but the cc-safety-net plugin demonstrates denial by returning `Tool.Error`. If this mechanism is not a stable API contract, the plugin's pre-tool denial scenarios may need an alternative implementation path. Affects: Rule "Factory plugin enforces permissions and step boundaries."

2. **Permission hooks in child sessions** — Whether `permission.hook("evaluate")` fires for child sessions is undocumented. If it does not, the scenario "Child sessions inherit session-scoped restrictions" may need a different enforcement mechanism. Affects: Rule "Factory plugin enforces permissions and step boundaries."

3. **Tool removal persistence** — Whether tool removal via `context` hook persists across turns or is re-evaluated per turn is undocumented. If per-turn, the plugin must re-apply restrictions on every context assembly. The scenario "Tool removal restricts the active agent's tool set" assumes the plugin handles either case. Affects: Rule "Factory plugin enforces permissions and step boundaries."

4. **Claude Code compatibility and skill discovery** — When `OPENCODE_DISABLE_CLAUDE_CODE=1` disables compatibility mode, `.claude/skills/` discovery may be suppressed. If so, the scenario "Skills are discoverable under .agents/skills/" already covers the correct path, but the installer must verify that skills are placed at `.agents/skills/` and not at `.claude/skills/`. Affects: Rule "OpenCode user discovers agents and skills through native paths."

5. **Pre-release version handling** — The version check compares against `1.18.31` as a minimum. Whether a pre-release suffix (e.g. `1.18.31-beta`) passes or fails the check is unspecified. The implementation must decide whether to accept pre-release versions of a supported release or reject them. Affects: Rule "Project maintainer installs Factory for OpenCode CLI."

## Deferred Scope

The following capabilities are explicitly deferred in the proposal and excluded from this specification. No Rules, Scenarios, or stories are planned for them.

- Operating-system sandboxing
- Remote workspace provisioning
- OpenCode Desktop support
- MCP-based adapter
- Built-in task tracking (TaskCreate/TaskUpdate equivalent)
- Built-in workflow orchestration (Workflow tool equivalent)
- Built-in persistent cross-session memory
