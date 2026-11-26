---
title: migrate-usage-transcripts
type: reference
status: implemented
description: Convert older usage transcripts to the current storage layout.
---

# migrate-usage-transcripts

## Name

`migrate-usage-transcripts` — Convert older usage transcripts to the current storage layout.

## Synopsis

```text
.agent-factory/factory/scripts/migrate-usage-transcripts [<arguments> ...]
```

Use `--help` for argument values and defaults supported by your installed version.

## Arguments and options

- `target`. project root
- `--apply`. change files; default is a dry run
- `--session`. migrate only this session ID
- `--verbose`. print one line per session

## See also

- [Command source](../../../scripts/migrate-usage-transcripts)
