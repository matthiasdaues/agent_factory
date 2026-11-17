---
title: Orchestration Envelope PoC
status: active
proposal: docs/proposals/factory-orchestration.md
created: 2026-09-22
---

# Orchestration Envelope PoC

**Question:** Can a Factory activity's invocation be described as a portable envelope and translated through a runtime-specific adapter into a valid CLI command for OpenCode?

**Success condition:** A test creates an envelope for a known agent (e.g. `validate`), passes it through an OpenCode adapter, and the adapter produces a well-formed command line with correct model ID, instruction path, and tool permissions. The adapter result carries enough structure for a fence run to identify the agent and its declared outputs.

**Out of scope:** Actually invoking OpenCode. Property matrix research. Runtime configuration files. Isolation. Multi-runtime support. The `orchestrate` CLI command. Schema validation of the envelope.
