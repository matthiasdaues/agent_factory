# Research Survey Plan — Agent Zero

## Research Question

What is Agent Zero (the open-source autonomous agent framework), what are its architecture, capabilities, and extension points, and how could it integrate with or complement the Agent Factory workflow?

## Bounded Questions

1. **Core architecture** — What is Agent Zero's agent loop, tool system, memory subsystem, and knowledge base? How does the main execution cycle work?
2. **Multi-agent capabilities** — How does Agent Zero handle agent delegation, inter-agent communication, and agent isolation? What is the subordinate agent model?
3. **Configuration model** — How are agents, tools, prompts, and behaviors configured? What files and formats does Agent Zero use?
4. **Extension points** — What mechanisms exist for custom tools, custom agents, custom prompts, and MCP server integration? How are they registered and discovered?
5. **Factory integration mapping** — How do Agent Zero concepts (agents, tools, memory, instruments, prompts) map to Agent Factory concepts (skills, agents, playbooks, dispatch, INDEX.yaml, role separation, gate validation)?
6. **Blockers and risks** — What architectural mismatches, missing capabilities, or integration risks exist for using Agent Zero within or alongside Agent Factory?

## Search Angles

- Agent Zero GitHub repository (frdel/agent-zero) — README, documentation, wiki
- Agent Zero Python source code — agent loop, tool registration, configuration loading, memory system
- Agent Zero example configurations and custom tool/instrument definitions
- Community technical write-ups, blog posts, and YouTube walkthroughs with verifiable technical detail
- Agent Factory's existing multi-CLI integration code and rules.md for the target integration pattern

## Source Targets

| Target                                                    | Purpose                                                  |
| --------------------------------------------------------- | -------------------------------------------------------- |
| github.com/frdel/agent-zero — README.md                   | Project overview, architecture summary, feature list     |
| Agent Zero source: `python/helpers/`, `python/tools/`     | Tool system, agent loop internals                        |
| Agent Zero source: `python/extensions/`, `instruments/`   | Extension points, instrument registration                |
| Agent Zero source: configuration files, settings          | Configuration model and format                           |
| Agent Zero documentation or wiki pages                    | Official docs on setup, customization, MCP               |
| Community technical blog posts / reviews                  | Independent architecture analysis, real-world usage      |
| Agent Factory `.agent-factory/factory/rulebooks/rules.md` | Factory's CLI integration pattern for mapping comparison |

## Assignments

| ID  | Agent      | Tier    | Task                                                                                                                            | Output                    | Independent Session |
| --- | ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------- |
| A1  | researcher | economy | Agent Zero core architecture: agent loop, memory, tool system, knowledge base. Search the GitHub repo, README, and source code. | SR-0001, SR-0002, SR-0003 | false               |
| A2  | researcher | economy | Agent Zero extension points: custom tools, custom agents, MCP support, configuration model and formats.                         | SR-0004, SR-0005          | false               |
| A3  | researcher | economy | Agent Zero multi-agent capabilities, community technical analysis, and Factory integration mapping.                             | SR-0006, SR-0007          | false               |

## Stop Conditions

- All six bounded questions are answered with cited evidence from recorded sources.
- A mapping table covers every Factory integration point and its Agent Zero equivalent or gap.
- Blockers and risks for integration are identified with source references.
- No further sources are likely to change the findings materially.
