---
title: Release
type: concept
status: implemented
order: 80
description: This chapter explains versioning, the changelog, and tags.
---

# Release

If your change affects a release, check the [version bump rules](../../../packages/factory/rulebooks/conventions/versioning-policy.md#version-bump-triggers) and record the user-visible change in the [changelog](../../../packages/factory/CHANGELOG.md). The [versioning policy](../../../packages/factory/rulebooks/conventions/versioning-policy.md#git-tag-must-match-version-file) explains how the tag and `VERSION` file agree. Check the [branch-specific tag rules](../../../packages/factory/rulebooks/conventions/versioning-policy.md#branch-specific-tag-format) before preparing a tag.

A release tag identifies the source used to build that release. If you maintain a fork, record the upstream tag or commit alongside the changes you carry. See [Manage a fork and its Factory installs](../workflow/source-management.md).

For release packaging, start with [build-release](../../../packages/factory/scripts/build-release).

<!-- handbook-index:start -->

<!-- handbook-index:end -->
