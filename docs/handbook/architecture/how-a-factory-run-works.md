---
title: How a Factory run works
type: concept
status: implemented
order: 10
description: Follow a specification review from the playbook to the reviewer and its checks.
---

# How a Factory run works

When you open an AI coding CLI in a project with Agent Factory installed, the CLI reads its project orientation. The orientation points it to the installed Factory under `.agent-factory/factory/`. The installer creates the wiring for the selected CLIs. In this repository, edit the source under `packages/factory/` and refresh the installation to try your change.

## Follow a specification review

1. The [feature-addition playbook](../../../packages/factory/playbooks/feature-addition.md) describes the work from proposal through implementation. An agent definition declares what files the agent needs and gives the AI instructions for its role. A skill gives the AI a procedure it can reuse across tasks. Rulebooks define conventions the procedures follow.
2. The [intent command](../../../packages/factory/scripts/intent) can list which agents are ready to run. It uses the [eligibility engine](../../../packages/factory/engine/eligibility.py) to evaluate declared inputs against files in the repository. Agent metadata therefore affects both what the AI sees and what the code can check.
3. The [specification reviewer](../../../packages/factory/agents/spec-review-agent.md) uses the [specification inspection skill](../../../packages/factory/skills/inspect-spec/SKILL.md). It runs [spec-lint](../../../packages/factory/scripts/spec-lint) for structural checks, then reads the specification for issues such as ambiguity or inconsistent requirements. A passing lint result covers the rules implemented by the script. The reviewer records issues that require interpretation.

## Find the source for your change

| If you want to change                                          | Start here                                                             |
| -------------------------------------------------------------- | ---------------------------------------------------------------------- |
| What an agent reads, writes, or considers during review        | `packages/factory/agents/`                                             |
| A procedure several agents can follow                          | `packages/factory/skills/`                                             |
| The order of work or who acts next                             | `packages/factory/playbooks/`                                          |
| A shared rule or template                                      | `packages/factory/rulebooks/`                                          |
| What a check accepts or reports                                | The command in `packages/factory/scripts/` and the tests that cover it |
| How a CLI starts an agent, runs a hook, or loads configuration | [CLI integrations](../cli-integrations/index.md)                       |

The top-level Factory `INDEX.yaml` is generated from source metadata. See [Agents and skills](../agents-and-skills/index.md) for the authoring and verification route. If you have yet to try a source change in the installed copy, follow the [first-change tutorial](../getting-started/from-clone-to-a-passing-test-run.md).
