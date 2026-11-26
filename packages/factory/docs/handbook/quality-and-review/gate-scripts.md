---
title: Gate scripts
type: reference
status: implemented
order: 20
description: Each gate script, when it fires, what it checks, the command that runs it, and when tests run.
---

# Gate scripts

[Gates](gates.md) explains what a gate is and when each kind runs.

## Structural gates

| Gate                                          | Fires                                           | Checks                                                                                                                                                           |
| --------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.agent-factory/factory/scripts/spec-lint`    | After specification work                        | The core of the specification: references to business rules, entities, and glossary terms in the core files and `.feature` files; unique IDs; required artifacts |
| `.agent-factory/factory/scripts/arch-lint`    | After architecture work                         | The arc42 chapters exist and reference the Structurizr DSL; the ADR index is consistent; diagram file references resolve                                         |
| `.agent-factory/factory/scripts/backlog-lint` | After planning                                  | The YAML frontmatter schema, a dependency graph without cycles, and the values of priority and status                                                            |
| `.agent-factory/factory/scripts/concern-lint` | When `agent-context.md` changes                 | The section structure, the resolution of `Read:` and `Boundary:` paths, the concerns that stories name, and no leftover legacy YAML                              |
| `.agent-factory/factory/scripts/matrix-lint`  | When `.agent-factory/config/model.conf` changes | The syntax, the required fields, and valid mappings of tier to model                                                                                             |

```bash
.agent-factory/factory/scripts/spec-lint --spec-dir docs/spec/
.agent-factory/factory/scripts/arch-lint --docs-dir docs/arc42
.agent-factory/factory/scripts/backlog-lint --backlog-dir backlog/
.agent-factory/factory/scripts/matrix-lint --matrix .agent-factory/config/model.conf
```

## Semantic gates

| Gate               | Script                                              | Runs                                                    | Checks                                                                                                                                     |
| ------------------ | --------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Dependency check   | `.agent-factory/factory/scripts/dependency-check`   | After every story                                       | The module import directions match the declarations in `architecture.dsl`.                                                                 |
| Test design verify | `.agent-factory/factory/scripts/test-design-verify` | When the story has a Test Design or Prior Tests section | The story's test design is complete: its listed test modules exist, or each reachable Scenario has a test entry.                           |
| CRAP score         | `.agent-factory/factory/scripts/crap-score`         | When picked as a test guardrail                         | Composite structural risk, cyclomatic complexity weighted against coverage. The threshold applies to the composite score, not to coverage. |
| Mutation testing   | `.agent-factory/factory/scripts/mutation-testing`   | When picked as a test guardrail                         | Runs the mutation command from the `gates` section of `docs/testing.yaml` within its time limit.                                           |

## Pre-commit hooks

| Group        | Hooks                                                                                                                                    | On failure                           |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Formatter    | `mdformat` for Markdown                                                                                                                  | Fixes the style and stops the commit |
| Gate scripts | `link-check`, `mermaid-lint`, `spec-lint`, `arch-lint`, `backlog-lint`, `concern-lint`, `matrix-lint`, `statemachine-lint`, `index-lint` | Rejects the commit                   |

[Pre-commit hooks](pre-commit-hooks.md) explains how the hooks run.

## Test execution

> Rule summary: Tests run through the factory's test gates, not as bare agent commands.
> Source: [foundational-principles.md § Agentic Creation, Deterministic Validation](../../../rulebooks/conventions/foundational-principles.md#agentic-creation-deterministic-validation)

The tests run at three points:

1. **Pre-commit.** The tests of the changed files run.
2. **Pre-push.** The full suite runs.
3. **Phase advance.** The entry condition `tests_pass` checks the suite.

Git's option `--no-verify` skips the hooks of the first two points. [Commit through the pre-commit hooks](../../../rulebooks/conventions/git-workflow.md#commit-through-the-pre-commit-hooks--the-two-pass-rule) shows how a commit passes them.

> Rule summary: **MUST NOT** bypass a failing pre-commit hook (`--no-verify`, `core.hooksPath`); fix the hook.
> Source: [rules.md § Git workflow](../../../rulebooks/rules.md#git-workflow)

A project declares its test commands in `docs/testing.yaml`:

| Key                    | Runs                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `test_command`         | The full suite, in the gates and at the feature merge                                                              |
| `test_staged_command`  | The tests of the staged files                                                                                      |
| `test_changed_command` | The tests of the changed files. A story merge appends the changed paths, and the key falls back to `test_command`. |

> Rule summary: An agent may run `test_changed_command`, as declared or followed by changed paths. The agent guard does not allow `test_staged_command`, so agents cannot run it.
> Source: [charter-testing.yaml](../../../rulebooks/templates/charter-testing.yaml)
