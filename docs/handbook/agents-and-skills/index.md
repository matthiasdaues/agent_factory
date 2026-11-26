---
title: Agents and skills
type: concept
status: implemented
order: 30
description: This chapter explains how to write an agent, a skill, or a playbook.
---

# Agents and skills

Decide whether you are changing a role, a reusable procedure, or the order of work. Edit the corresponding file in `agents/`, `skills/`, or `playbooks/` under `packages/factory/`. The [specification review example](../architecture/how-a-factory-run-works.md#follow-a-specification-review) shows all three in use.

Run `packages/factory/scripts/index-lint` from the repository root after changing source metadata. Review the generated index diff, then refresh the installed copy as in the [first-change tutorial](../getting-started/from-clone-to-a-passing-test-run.md). Try the affected role or procedure in the CLI where people use it, and check the expected result or output file.

For the structure of a skill, see the [skill-authoring rules](../../../packages/factory/rulebooks/conventions/skill-authoring.md).

<!-- handbook-index:start -->

<!-- handbook-index:end -->
