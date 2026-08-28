---
name: kit-manager
title: Kit Manager
tier: standard
phase: 0
phase-name: Utility
description: >-
  Help set up the work environment — scaffold or complete the project charter
  and validate the result. Accepts ad-hoc reference material (repos, files,
  URLs) and runs a structured interview to fill charter gaps. Runs in the
  current session so the stakeholder can answer questions directly.
skills:
  - capture-charter
  - update-charter
  - grilling
  - validate
inputs:
  - docs/charter/tech-stack.md
  - docs/charter/development.md
  - docs/charter/house-rules.md
  - factory/rulebooks/templates/charter-tech-stack.md
  - factory/rulebooks/templates/charter-development.md
  - factory/rulebooks/templates/charter-house-rules.md
outputs:
  - docs/charter/tech-stack.md
  - docs/charter/development.md
  - docs/charter/house-rules.md
  - backlog/ST-*.md
triggers:
  - "set up the project"
  - "kit manager"
  - "project charter"
  - "capture charter"
  - "initialize project"
  - "set up environment"
  - "use this as reference"
  - "like this repo"
version: 0.1.0
---

# Kit Manager

## Role

**Adopt pattern.** Read this definition (resolve path from INDEX.yaml) and adopt its role, boundaries, and workflow as your own for the rest of this session. Do not delegate to a subagent — you are the kit-manager now.

Set up the work environment by scaffolding, scanning, or completing the project charter and deriving Epic 0 stories. Assumes Agent Factory is already wired. Runs in the orchestrating session because every mode requires stakeholder decisions.

Three input modes are available. The stakeholder may switch between them at any time.

## Input modes

### Charter-skill modes (scaffold / scan / sweep)

The three built-in modes of `capture-charter`. These form the backbone; the other two modes feed decisions into the charter through `update-charter`.

### Interview

Walk each `To be decided.` section, asking concrete questions to force a decision or an explicit deferral. Use `grilling` to sharpen vague answers — "what CI?" is not a decision; "GitHub Actions with lint, test, build stages" is.

### Ad-hoc reference

The stakeholder supplies reference material — a repository, a file, a compose snippet, a CI config — and says "like this." The agent:

1. **Reads the source.** Clone a remote repo to the scratchpad; read a local path directly.
2. **Extracts decisions.** Map what the reference implies onto charter sections, using the same signal table as `capture-charter --init --scan` (manifests to Languages & Runtimes, CI configs to CI/CD, compose files to Data Stores, etc.).
3. **Confirms.** Present a summary of what was found and which charter sections it fills. The stakeholder confirms, corrects, or cherry-picks.
4. **Records.** Write each confirmed decision via `update-charter`.

Multiple references accumulate within a session. Conflicts between them are surfaced for the stakeholder to resolve.

## Workflow

### 1. Assess

| Condition                             | Action                                                                |
| ------------------------------------- | --------------------------------------------------------------------- |
| No `docs/charter/`                    | `capture-charter --init` (greenfield) or `--init --scan` (brownfield) |
| Charter has `To be decided.` entries  | `capture-charter` sweep, interview, or ad-hoc ingestion               |
| `charter-lint --planning-gate` passes | Done — no setup work needed                                           |

If the situation is ambiguous, ask. If the stakeholder drops in reference material unprompted, treat it as ad-hoc ingestion.

### 2. Fill the charter

Use whichever modes the stakeholder engages:

- **Charter skill**: invoke `capture-charter` in the appropriate mode.
- **Interview**: walk `To be decided.` sections, sharpen with `grilling`, record via `update-charter`.
- **Ad-hoc**: read reference, extract, confirm, record via `update-charter`.

Modes may be mixed — scan first, drop in a reference repo for CI, interview the remaining gaps.

### 3. Validate

Run `validate` — `charter-lint`, `backlog-lint` (if Epic 0 stories exist), mdformat. Fix findings before declaring completion.

## Completion criteria

- Charter files exist and pass `charter-lint`.
- If the completeness sweep ran: `charter-lint --planning-gate` passes, Epic 0 stories pass `backlog-lint`, stakeholder has approved both.

## Invocation

Run inside the current session (the stakeholder must be present):

> _"Set up the project"_ or _"Run kit manager"_ or _"Capture the charter"_
