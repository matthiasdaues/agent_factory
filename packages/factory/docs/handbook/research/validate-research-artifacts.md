---
title: Validate a research artifact
type: how-to
status: implemented
order: 20
description: Run the schema check and the policy check on a research artifact before its semantic review.
---

# Validate a research artifact

A research artifact passes three stages in a fixed order before the next playbook step begins: schema, policy, and semantic. A machine decides the first two, and a person or an agent decides the third:

| Stage        | Tool                                             | Checks                                                                                                            |
| ------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| 1 — schema   | `.agent-factory/factory/scripts/schema-validate` | One JSON artifact against one JSON Schema: required fields, types, enums, identifier patterns, timestamps         |
| 2 — policy   | `.agent-factory/factory/scripts/policy-validate` | The checkable half of the research policies across artifacts: role separation, references, quorum, claim versions |
| 3 — semantic | a qualified human or agent reviewer              | Evidence support, independence of sources, severity of tests, atomic claims: the judgement no script makes        |

The two scripts are stdlib-only Python. The research skills and agents call them on demand, and so can you. No activity boundary runs them.

1. Check one artifact against its schema. The schemas live in [`.agent-factory/factory/rulebooks/schemas/`](../../../rulebooks/schemas/).

   ```bash
   .agent-factory/factory/scripts/schema-validate <artifact-file> <schema-file>
   ```

2. Run stage 1 and then stage 2 in one call. The pipeline stops at the first failure.

   ```bash
   .agent-factory/factory/scripts/policy-validate --pipeline <artifact-or-dir>...
   ```

3. Hand the artifact to its reviewer for the semantic stage.

[`research-topic.md` § The Validation Gate](../../../playbooks/research-topic.md#the-validation-gate) describes the gate in the playbook. The ADR "Research flat storage and validation pipeline" (ADR-0006) in the Agent Factory repository explains the order of the stages.
