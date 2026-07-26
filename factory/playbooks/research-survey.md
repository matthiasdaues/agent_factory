---
title: Research Survey Playbook
category: orchestration
type: runbook
scenario: research-survey
version: 0.1.0
---

# Research Survey Playbook

Portable dispatch contract for source gathering in survey mode. The
mode-specific planning, synthesis, validation, and completion workflow is
defined separately by the survey-mode story.

## Research Capability Preflight

Before planning or gathering sources, apply the
[research assignment contract](../rulebooks/conventions/dispatch-contract.md#research-assignment-contract).
Required source access must be available; otherwise block the survey run.

Every source-gathering assignment declares `agent`, Factory `tier`, bounded
`task`, a unique `output` path, and `independent_session: false`. Dispatch a
bounded wave when the active CLI supports it. If parallel fan-out is
unavailable, preserve the same assignments and unique output paths and run
them sequentially.

Survey fallback changes scheduling only. It does not permit two assignments to
share an output or allow missing source access.
