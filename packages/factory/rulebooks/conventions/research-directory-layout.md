---
title: Research Directory Layout
version: 1.0.0
---

# Research Directory Layout

## Problem

A flat `docs/research/` directory supports only one research effort at a time.
A second survey requires archiving the first, which blocks parallel or
overlapping research.

## Rule

- **MUST** place each research effort under its own slug directory:
  `docs/research/<slug>/`, where `<slug>` is the kebab-case topic name
  (e.g. `opencode-cli-integration`, `agent-zero`).
- **MUST** keep the same internal structure within each slug directory:
  `research-brief.json`, `research-brief.md`, `research-survey-plan.md`,
  `sources/*.md`, `survey-report.md` (survey mode) or `claims/*.md`,
  `reviews/*.md`, `votes/*.md`, `claim-register.md`, `final-report.md`
  (falsification mode).
- **MUST** pass the slug directory as the working root to every research
  agent and skill invocation so artifacts land in the right place.
- **MUST NOT** place research artifacts directly under `docs/research/`.

## Migration

Existing flat `docs/research/` artifacts move into a named slug directory
that matches their topic. No archiving needed — reorganise in place.

## Referenced from

- [research-survey.md](../../playbooks/research-survey.md)
- [research-topic.md](../../playbooks/research-topic.md)
