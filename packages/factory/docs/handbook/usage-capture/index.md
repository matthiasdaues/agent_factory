---
title: Usage capture
type: concept
status: implemented
order: 100
description: What the usage runtime records about token use, and where it keeps the records.
---

# Usage capture

The factory records how many tokens each session uses. This chapter explains what it records and how to configure it. It also covers the usage add-on, which reads the records. The add-on is optional, and the factory runs without it.

<!-- handbook-index:start -->

## Concepts

- [How usage capture works](usage-capture.md): How the factory records the token use of each session, where it stores records and transcripts, and how capture stays out of your way.
- [The usage add-on](usage-add-on.md): What the optional usage add-on analyses, what it leaves alone, and which pages explain its use.

## How-to guides

- [Configure transcript retention](configure-transcript-retention.md): Choose whether usage capture stores transcript text or only the token totals.
- [Migrate old usage transcripts](migrate-usage-transcripts.md): Convert the transcript store of version 1.13.0 or earlier, which kept a full copy per capture.
- [Install the usage add-on](install-usage-add-on.md): Install the optional usage add-on into a project and check that it can read your records.
- [Query usage views](query-usage-views.md): Query the six usage views from the command line, read per-tool token use, and save the views to a DuckDB file.
- [Explore usage in the browser](explore-usage-in-the-browser.md): Open the usage views in the bundled SQL explorer or in the DuckDB UI, and start DuckDB from the command line.

## Reference

- [Usage capture reference](usage-capture-reference.md): The capture trigger and the accounting rule of each CLI, and the test file that owns each capture contract.
- [Session log](session-log.md): The optional audit log of gate runs, its record fields, and the session-reconcile command that compares it with git.
- [Usage add-on reference](usage-add-on-reference.md): The six published views, the options and output formats of usage-query, and the Python API of the usage add-on.

<!-- handbook-index:end -->
