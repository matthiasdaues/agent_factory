---
title: The usage add-on
type: concept
status: implemented
order: 50
description: What the optional usage add-on analyses, what it leaves alone, and which pages explain its use.
---

# The usage add-on

You have recorded usage and now want to read it. The usage add-on does that. It is optional, and the factory runs without it. Capture works the same whether or not you install the add-on.

The add-on reads the JSONL records that capture writes to `.agent-factory/usage/`. It checks every record against the usage-record contract, tests the ancestry of sessions, and publishes six views over the result. You query the views from a command line, from Python, or from a browser.

The add-on never captures data, never rewrites a record, and reads only local files. Its analysis needs no network connection. Installing the add-on and its dependencies downloads software, and so does the first run of the DuckDB UI. The browser UI runs on localhost for the length of one session. It is never a gate and never holds the authoritative data. The repository supplies no dashboard formulas and no saved charts.

To start, [install the add-on](install-usage-add-on.md). [Query the views](query-usage-views.md) from the command line, or [explore them in the browser](explore-usage-in-the-browser.md). The [add-on reference](usage-add-on-reference.md) lists the views, the options, the output formats, and the Python API.
