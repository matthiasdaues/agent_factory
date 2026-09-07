---
title: Commit Message Template
version: 1.0.0
---

# Commit Message Template

Skeleton for a commit message. Governed by [commit-conventions.md](../conventions/commit-conventions.md) (type, description, ID) and [versioning-policy.md](../conventions/versioning-policy.md) (breaking-change footer).

## Standard commit

```
<type>: <description> (<ID>)
```

See [commit-conventions.md § ID Formats](../conventions/commit-conventions.md#id-formats) for `<type>` and `<ID>` by context.

## Breaking change

```
<type>: <description> (<ID>)

BREAKING CHANGE: <what changed and how to migrate>
```

## Referenced from

- [commit-conventions.md § Story/Bug ID Required](../conventions/commit-conventions.md#storybug-id-required)
- [versioning-policy.md § Breaking Changes](../conventions/versioning-policy.md#breaking-changes)
