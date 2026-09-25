---
schema_version: 2
title: Structurizr Theme EOL Migration
status: draft
owner: md@matthiasdaues.de
created: 2026-09-23
updated: 2026-09-23
supersedes:

impact:
  scope: local
  architecture_change: false
  external_contract_change: false
  boundaries:
    - docs/arc42/architecture.dsl

governance:
  assurance: routine
  risk_domains:
    - reliability

estimate:
  as_of: 2026-09-23
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
    overhead_multiplier: 10
    playbook: feature-addition
---

# Feature Request: Structurizr Theme EOL Migration

## Summary

The Structurizr cloud service reaches end-of-life on 30 September 2026.
All theme URLs hosted at `static.structurizr.com` will stop resolving,
including the `theme default` directive our `architecture.dsl` uses.
This proposal vendors the required themes from the upstream GitHub
repository and rewrites the DSL to use local file paths.

## Motivation

Our architecture export pipeline uses `theme default` in
`docs/arc42/architecture.dsl`. The Structurizr DSL parser hardcodes
`theme default` to `https://static.structurizr.com/themes/default/theme.json`.
After 30 September 2026 that URL will 404 and every diagram export will
break. The upstream source (`structurizr/structurizr` on GitHub) already
logs a deprecation warning for every theme URL on the dying host.

The GitHub repository contains the complete theme set (16 themes,
Apache 2.0 licensed) including three 2025-era themes that were never
published to the static host. Vendoring from GitHub is the sanctioned
post-EOL path.

## Core Principles

- Vendor only the themes this project actually uses — not the full
  5,500-file tree.
- Keep theme files next to the DSL so the Structurizr CLI auto-discovers
  them without environment variables or wrapper scripts.
- Treat vendored themes as upstream snapshots: update by re-copying, not
  by editing in place.

## Design

1. **Copy the `default` theme** from
   `structurizr/structurizr:structurizr-themes/default/` into
   `docs/arc42/themes/default/`.
2. **Rewrite `architecture.dsl`**: replace `theme default` with
   `theme themes/default/theme.json` (relative path, resolved by the
   CLI).
3. **Update factory docs** that teach the `theme default` directive
   (`scaffold-arc42/SKILL.md`, any STRUCTURIZR reference) to use the
   local-path form.
4. **Add a `.gitattributes` entry** marking `docs/arc42/themes/` as
   binary / linguist-vendored so theme icons do not pollute diffs or
   language statistics.

## Scope

**In the first release:**

- Vendor the `default` theme locally.
- Rewrite `architecture.dsl` to use the local path.
- Update factory skill and doc references.
- Verify diagram export produces identical output.

**Explicitly deferred (do NOT plan stories for these):**

- Vendoring additional cloud-provider themes (AWS, Azure, GCP) — vendor
  on first use.
- A central cross-project theme cache via `STRUCTURIZR_THEMES` — not
  needed while only one project uses Structurizr.
- Scraping `icons.json` variants from the static host — they are not in
  the GitHub repo and are not required for diagram export.

## Open Questions

- Should `docs/arc42/themes/` be committed as-is, or stored in Git LFS
  given the binary icon PNGs? The default theme alone is small; LFS adds
  setup cost.

## Completion Criteria

- `theme default` no longer appears in `architecture.dsl`.
- `docs/arc42/themes/default/theme.json` exists and matches the upstream
  GitHub version.
- Diagram export with the project's Structurizr Docker image
  (`structurizr/structurizr:2026.05.22-playwright`) succeeds and
  produces visually identical SVGs.
- No factory skill or doc references `theme default` as a recommended
  directive.

## Guiding Rule

Every external URL that can die must become a vendored local file before
it dies.
