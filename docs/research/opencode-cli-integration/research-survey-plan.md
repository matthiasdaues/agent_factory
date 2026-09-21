# Research Survey Plan — OpenCode CLI Integration

## Research Question

What extension points does OpenCode CLI expose (configuration, system prompts, agent/tool definitions, subagent dispatch, MCP support), and how do they map to the Agent Factory multi-CLI integration pattern?

## Bounded Questions

1. **Configuration directory and files** — Where does OpenCode look for project-level config? What format?
2. **System prompt / custom instructions** — Can projects inject instructions at session start? How?
3. **Tool protocol** — What tools does it expose? File read/write, bash, MCP support?
4. **Agent/skill definitions** — Does it support custom agent types or skill definitions? Format?
5. **Subagent dispatch** — Can it spawn isolated sessions or parallel workers?
6. **Session management** — Conversation persistence, context, session state?

## Search Angles

- OpenCode's official documentation site (opencode.ai/docs/)
- OpenCode's GitHub repository (github.com/opencode-ai/opencode, github.com/anomalyco/opencode)
- Community documentation and reverse-engineering efforts
- GitHub issues for capability gaps and feature requests
- The factory's existing multi-CLI integration code (SR-0001)

## Source Targets

| Target                                    | Purpose                                    |
| ----------------------------------------- | ------------------------------------------ |
| opencode.ai/docs/config/                  | Full config reference                      |
| opencode.ai/docs/agents/                  | Agent definition format                    |
| opencode.ai/docs/rules/                   | AGENTS.md / CLAUDE.md handling             |
| opencode.ai/docs/skills/                  | Skill system                               |
| opencode.ai/docs/permissions/             | Permission model                           |
| opencode.ai/docs/mcp-servers/             | MCP integration                            |
| opencode.ai/docs/cli/                     | CLI commands and flags                     |
| GitHub issues #12472                      | Claude Code hooks compatibility status     |
| GitHub issues #18100, #17870, #9280       | Subagent depth, model inheritance, nesting |
| factory/scripts/init-factory              | Factory's wiring pipeline                  |
| .agent-factory/factory/rulebooks/rules.md | Factory's CLI integration rules            |

## Stop Conditions

- All six bounded questions are answered with cited evidence.
- A mapping table covers every factory integration point.
- Gaps and blockers are identified with source references.
- No further sources are likely to change the findings materially.

## Assignments

| ID  | Agent              | Task                                          | Output                  |
| --- | ------------------ | --------------------------------------------- | ----------------------- |
| A1  | researcher         | OpenCode config, rules, agents, skills docs   | SR-0004 through SR-0006 |
| A2  | researcher         | OpenCode CLI, MCP, permissions, subagent docs | SR-0007 through SR-0011 |
| A3  | researcher         | Prompt assembly pipeline                      | SR-0012                 |
| A4  | researcher (prior) | Factory multi-CLI integration pattern         | SR-0001 (pre-existing)  |
