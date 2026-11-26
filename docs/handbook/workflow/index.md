---
title: Workflow
type: concept
status: implemented
order: 70
description: This chapter explains how a change travels from proposal to merge.
---

# Workflow

If you are proposing a feature, start with the [feature-addition playbook](../../../packages/factory/playbooks/feature-addition.md) and its proposal. If you are fixing a reported problem, start with the finding and the [bug-fix playbook](../../../packages/factory/playbooks/bug-fix.md). If a backlog story already describes the work, use its scope and checks to guide your change.

Before editing, find the feature or story branch for the work and check the [branching policy](../../../packages/factory/rulebooks/conventions/branching-policy.md#branch-per-unit-of-work). Run the focused checks from [Testing](../testing/index.md), then take the change through the review and merge steps for its playbook. The [pre-merge check policy](../../../packages/factory/rulebooks/conventions/branching-policy.md#pre-merge-diff-check) explains what must pass before a merge.

If you work through a fork or distribute a patched Factory, read [Manage a fork and its Factory installs](source-management.md).

<!-- handbook-index:start -->

## Concepts

- [Manage a fork and its Factory installs](source-management.md): Keep upstream, fork changes, and project installations traceable.

<!-- handbook-index:end -->
