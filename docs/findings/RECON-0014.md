---
id: RECON-0014
source: reconcile-spec
severity: major
category: defect
artifact: docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md; docs/adr/0005-openrouter-model-discovery-for-model-conf.md; docs/adr/0006-research-flat-storage-and-validation-pipeline.md; docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md; docs/09_architecture_decisions.md#decision-index
status: resolved
traces: [ADR-0004, ADR-0005, ADR-0006, ADR-0007]
---

# ADRs 0004–0007 are marked `proposed` but the code fully implements and depends on them

**What is wrong:** Four ADRs carry `status: proposed` in their own frontmatter
and in the `docs/09_architecture_decisions.md` Decision Index, yet the
code-as-built ships, exercises, and depends on every decision they record. In
Nygard's status model "proposed" means a decision has not yet been adopted; a
decision that is implemented and load-bearing for the running system is
`accepted`. The status field therefore no longer tells the truth about the
codebase.

- **ADR-0004** (`proposed`) — "Pi runs a factory agent by spawning a separate
  `pi` subprocess." Implemented and in active use: `factory/config/extensions/ run-agent.ts` and `dispatch-wave.ts` are installed by `init-factory` into
  `.pi/extensions/`, register the `run_agent` and `dispatch_wave` tools, and
  are the documented dispatch path under Pi (factory-guide § Running an agent
  in a separate session; UC-10).
- **ADR-0005** (`proposed`) — "OpenRouter tiers curated into `model.conf`;
  discovery is a separate offline aid." Implemented: `factory/scripts/ openrouter-discover` ships with `--list`/`--suggest`/`--check`, and
  `config/model.conf` carries the curated `pi.*` tier rows the ADR describes.
- **ADR-0006** (`proposed`) — "Research: flat prefixed rulebook storage and a
  schema → policy → semantic validation pipeline." Implemented: flat
  `research-*` files exist across `factory/rulebooks/{conventions,templates, schemas}/`, and `factory/scripts/schema-validate` and `policy-validate`
  (with `--pipeline`) implement stages 1 and 2.
- **ADR-0007** (`proposed`) — "Normalize runtime usage through CLI adapters
  into local append-only records." Implemented and reconciled across four
  prior RECON passes: `factory/scripts/usage-capture` plus the Claude, Copilot,
  Codex, and Pi adapters are installed and tested (RECON-0006 through
  RECON-0012, all resolved).

The Decision Index in `docs/09_architecture_decisions.md` mirrors the same
four `proposed` statuses (lines 14–17), and the § Key Decisions prose already
describes them as established ("ADR-0004 establishes…", "ADR-0007 establishes
one CLI-agnostic runtime usage pipeline…") — the prose and the code say
"accepted" while the status field says "proposed".

**Fix:** Set `status: accepted` in the frontmatter of
`docs/adr/0004-…`, `0005-…`, `0006-…`, and `0007-…`, and update the Status
column for those four rows in `docs/09_architecture_decisions.md`'s Decision
Index from `proposed` to `accepted`. If any decision is genuinely still
contingent (e.g. awaiting a ratification the team has not held), annotate the
ADR body with that contingency rather than leaving the status field
contradicting the shipped code. No code change is required.

## Resolution

Set ADR-0004 through ADR-0007 to `accepted` and updated the decision index to
the same status.

## Verification

A fresh scan found no `proposed` status for ADR-0004 through ADR-0007 in either
their frontmatter or the decision index. `arch-lint` completed with 0 errors
and the two pre-existing parse warnings.
