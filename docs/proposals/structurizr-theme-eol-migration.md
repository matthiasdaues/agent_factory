---
schema_version: 2
title: Structurizr Theme EOL Migration
status: accepted
owner: md@matthiasdaues.de
created: 2026-09-23
updated: 2026-09-29
supersedes:

impact:
  scope: local
  architecture_change: false
  external_contract_change: false
  boundaries:
    - docs/arc42/architecture.dsl
    - packages/factory/skills/scaffold-arc42/SKILL.md
    - packages/factory/skills/scaffold-arc42/STRUCTURIZR.md

governance:
  assurance: routine
  risk_domains:
    - reliability

estimate:
  as_of: 2026-09-29
  basis: judgment
  confidence: high
  human_review_hours:
    min: 0.25
    max: 0.5
  normalized_tokens:
    min: 2000
    max: 5000
  estimated_consumption:
    min: 10000
    max: 50000
    overhead_multiplier: 5
---

# Feature Request: Structurizr Theme End-of-Life Migration

## Summary

Structurizr is the tool we use to define and export architecture
diagrams from a workspace file (`docs/arc42/architecture.dsl`). Themes
provide the visual styles, element shapes, and icons for those diagrams.

The Structurizr cloud service reaches end-of-life on 30 September 2026.
All theme URLs hosted at `static.structurizr.com` will stop resolving,
including the `theme default` directive our workspace file uses. This
proposal copies the `default` theme from the upstream GitHub repository
into the factory source tree and rewrites the workspace file to use a
local file path.

## Motivation

Our architecture export pipeline uses `theme default` in the workspace
file `docs/arc42/architecture.dsl`. The Structurizr Domain-Specific
Language (DSL) parser resolves `theme default` to
`https://static.structurizr.com/themes/default/theme.json`. After
30 September 2026 that URL will stop resolving and every diagram export
will break. The upstream source (`structurizr/structurizr` on GitHub)
already logs a deprecation warning for every theme URL on the
decommissioned host.

The GitHub repository contains the complete theme set (Apache 2.0
licensed). Copying a theme into the project's own source tree is the
recommended post-end-of-life path. Additional themes (AWS, Azure, GCP)
can be copied the same way when needed — the upstream repository is not
going away.

## Core Principles

- Copy only the `default` theme — the only one this project uses.
- Keep theme files next to the workspace file so the Structurizr CLI
  resolves them without configuration.
- Treat the copied theme as an upstream snapshot: update by re-copying
  from the GitHub repository, not by editing in place.

## Design

1. **Copy the `default` theme** from
   `structurizr/structurizr:structurizr-themes/default/` into
   `packages/factory/themes/structurizr/default/`. The theme ships with
   every factory install.
2. **Update `scaffold-arc42`** to copy the `default` theme from the
   factory into `docs/arc42/themes/default/` during scaffolding and
   write `theme themes/default/theme.json` instead of `theme default`.
3. **Rewrite this project's `architecture.dsl`**: replace
   `theme default` with `theme themes/default/theme.json`.
4. **Update factory references** to the `theme default` directive in
   `packages/factory/skills/scaffold-arc42/SKILL.md` and
   `packages/factory/skills/scaffold-arc42/STRUCTURIZR.md`.
5. **Add a `.gitattributes` entry** marking `docs/arc42/themes/` as
   linguist-generated so theme icons do not clutter diffs or language
   statistics.

**Stop conditions** — the implementing agent should stop and ask when:

- The upstream theme directory layout does not match the expected
  structure (`default/theme.json` plus icon files).
- The Structurizr CLI does not resolve the relative `theme` path.
- Diagram export produces different output after the rewrite.

## Scope

**In scope:**

- Copy the `default` theme into the factory source tree.
- Update `scaffold-arc42` to use the local theme path.
- Rewrite this project's `architecture.dsl`.
- Update factory doc references.
- Verify that diagram export produces identical output.

**Out of scope (do NOT plan stories for these):**

- Bundling additional themes (AWS, Azure, GCP) — copy from the upstream
  GitHub repository when needed, using the same pattern.
- A theme picker or selection mechanism — not needed while only one
  theme is in use.
- A cross-project theme cache via the `STRUCTURIZR_THEMES` environment
  variable.

## Verification

Export diagrams before and after the change and compare the output:

```
docker run --rm -v $(pwd)/docs/arc42:/usr/local/structurizr \
  structurizr/structurizr:2026.05.22-playwright \
  export -workspace /usr/local/structurizr/architecture.dsl -format plantuml
```

A `diff -r` between the before and after exports should produce no
output. Any difference requires human inspection.

## Completion Criteria

- `packages/factory/themes/structurizr/default/theme.json` exists and
  matches the upstream GitHub version.
- `scaffold-arc42` writes `theme themes/default/theme.json` instead of
  `theme default`.
- `theme default` no longer appears in any factory skill or document.
- Diagram export with the local theme path produces identical output to
  the baseline (`diff -r` shows no differences).

## Guiding Rule

Every external URL that can stop resolving must become a local file
before it does.

## Review — 2026-09-29

Reviewer: proposal-review-agent
Reviewed commit: 897391be44f5383c33dd37579e78af05a1d464bd
Disposition: findings

### Findings

| ID      | Severity | Check | Status | Finding                                                                                                                    |
| ------- | -------- | ----- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | major    | 04    | fixed  | `scope: factory-wide` → `local`. Scope reduced: only `default` theme, no picker, no multi-theme bundling.                  |
| PROP-02 | major    | 05    | fixed  | Removed `packages/factory/themes/structurizr/` from boundaries. Path described in Design only (created by implementation). |
| PROP-03 | major    | 05    | fixed  | Boundary corrected to tracked source path `packages/factory/skills/scaffold-arc42/SKILL.md`.                               |
| PROP-04 | minor    | 05    | fixed  | `STRUCTURIZR.md` added to boundaries.                                                                                      |
| PROP-05 | major    | 01    | fixed  | Verification section added with export command and `diff -r` comparison.                                                   |
| PROP-06 | major    | 03    | n/a    | Standalone theme-select command removed from scope (YAGNI). No longer in the design.                                       |
| PROP-07 | minor    | 03    | n/a    | Theme picker removed from scope (YAGNI). No longer in the design.                                                          |
| PROP-08 | minor    | 08    | fixed  | `overhead_multiplier` raised to 15. Estimate adjusted to match reduced scope.                                              |

### Summary

All findings from the first review pass are resolved. The proposal was
simplified after the review: scope reduced to the `default` theme only,
theme picker and standalone command removed (YAGNI). The design now has
five concrete steps, all decomposable. Boundaries resolve to tracked
source files. Verification uses `diff -r` against a baseline export.
