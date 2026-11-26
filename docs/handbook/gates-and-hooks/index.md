---
title: Gates and hooks
type: concept
status: implemented
order: 40
description: This chapter explains how to add a lint script or a hook that works in every supported CLI.
---

# Gates and hooks

A gate checks a rule. A hook decides when to run a command, for example during a commit or at a CLI session event. A review agent can also invoke a gate from its instructions. See the [specification review example](../architecture/how-a-factory-run-works.md#follow-a-specification-review).

To change what a gate accepts, find the command in `packages/factory/scripts/` and its tests. Run the command directly on an example that should pass and one that should fail. To change when a command runs during a commit in this repository, start with the [pre-commit configuration](../../../.pre-commit-config.yaml). For hooks installed into other projects, start with [CLI integrations](../cli-integrations/index.md).

<!-- handbook-index:start -->

<!-- handbook-index:end -->
