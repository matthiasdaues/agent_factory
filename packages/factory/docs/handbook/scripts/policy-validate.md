---
title: policy-validate
type: reference
status: implemented
description: Check research artifacts against the evidence policy.
---

# policy-validate

## Name

`policy-validate` — Check research artifacts against the evidence policy.

## Synopsis

```text
.agent-factory/factory/scripts/policy-validate [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `paths`. artifact JSON files and/or directories of artifacts
- `--pipeline`. run schema -> policy -> semantic in order, stopping at the first failing stage
- `--quorum`
- `--schemas-dir`. directory holding the research JSON schemas

## See also

- [Command source](../../../scripts/policy-validate)
