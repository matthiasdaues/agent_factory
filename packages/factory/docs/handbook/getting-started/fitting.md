---
title: Fit the Factory to your project
type: concept
status: implemented
order: 20
description: See what discovery finds, what you confirm, and how the project gets its own configuration and gates.
---

# Fit the Factory to your project

Fitting turns an installer scan into a setup your team can use. The scan starts automatically. When you choose to fit the project, VIRGIL shows you what the Factory found and helps you decide what to configure.

```text
Discover the stack -> Confirm and fill gaps -> Configure the project
```

1. **Discover.** The installer looks for evidence of languages, frameworks, package managers, CI, linters, and tests. It records what it found and where it found it in `.agent-factory/config/project-context.json`. It can also seed the test configuration when it finds a clear test command.
2. **Confirm and fill gaps.** Tell VIRGIL what the scan missed or misunderstood. For example, a repo may have fast unit tests and a second suite that needs a running database. Confirm when each should run and where agents can read the team's conventions.
3. **Configure.** The [model matrix](../reference/model-matrix.md) maps model tiers to models for your CLI. [Agent context](../agent-context/what-agent-context-does.md) points agents to project knowledge. `docs/testing.yaml` records test commands, suites, and gate settings. Fitting also covers pre-commit hooks and the counter that supplies artifact IDs. VIRGIL saves progress so you can return to it.

## Fit the quality gates to the code

Once you know how the project tests, decide which [story gates](../quality-and-review/gates.md#semantic-gates) to enable. CRAP Score and mutation testing require project-specific setup. The installer scan gives you evidence for that setup, and the team decides whether to adopt each gate.

- **CRAP Score** stands for Change Risk Anti-Pattern score. The `crap-score` command combines a function’s branching complexity with how much of it the tests execute. A function with many paths and little coverage scores higher. The gate compares scores for changed functions with your project’s threshold. Use [`setup-crap-score`](../../../skills/setup-crap-score/SKILL.md) to try the measuring tools on real files and verify the threshold and timeout before enabling it.
- **Mutation testing** checks whether tests catch behavior changes. The tool makes a temporary change, such as replacing `amount > 0` with `amount >= 0`, then runs the tests. If a test fails, it caught the change. If all tests pass, the change survived and needs investigation. In this example, a test for zero could expose the difference. Choose a tool for each relevant language or suite and configure the project’s command and timeout in `docs/testing.yaml`. See the [mutation testing setup guidance](../../../rulebooks/references/mutation-testing-methodology.md).

The [implementation run](../quality-and-review/implementation-run.md#what-the-gates-add) shows when the dispatcher uses these settings.
