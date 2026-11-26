---
title: Usage capture
type: concept
status: implemented
order: 100
description: What the usage runtime records about token use, and where it keeps the records.
---

# Usage capture

The factory records how many tokens each session uses. This chapter explains what it records and how to configure it.

<!-- handbook-index:start -->

## Concepts

- [How usage capture works](usage-capture.md): How the factory records the token use of each session, where it stores records and transcripts, and how capture stays out of your way.

## How-to guides

- [Configure transcript retention](configure-transcript-retention.md): Choose whether usage capture stores transcript text or only the token totals.
- [Migrate old usage transcripts](migrate-usage-transcripts.md): Convert the transcript store of version 1.13.0 or earlier, which kept a full copy per capture.

## Reference

- [Usage capture reference](usage-capture-reference.md): The capture trigger and the accounting rule of each CLI, and the test file that owns each capture contract.
- [Session log](session-log.md): The optional audit log of gate runs, its record fields, and the session-reconcile command that compares it with git.

<!-- handbook-index:end -->
