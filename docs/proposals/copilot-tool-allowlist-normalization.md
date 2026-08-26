---
schema_version: 2
title: "Copilot Tool Allowlist Normalization"
status: draft
owner: agent-factory
created: 2026-08-26
updated: 2026-08-26
supersedes:

impact:
  scope: internal
  architecture_change: false
  external_contract_change: false
  boundaries:
    - .github/agents/*.md
    - factory/agents/*.md
    - factory/scripts/init-factory

governance:
  assurance: standard
  risk_domains:
    - operations

estimate:
  as_of: 2026-08-26
  basis: judgment
  confidence: high
  human_review_hours: 1
  normalized_tokens: 5000
---

# Proposal: Copilot Tool Allowlist Normalization

## Summary

When the implementation-agent dispatches developer-agent subagents in a
GitHub Copilot CLI session, Copilot emits repeated warnings:

```
Unknown tool name in the tool allowlist: "create"
Unknown tool name in the tool allowlist: "edit"
Unknown tool name in the tool allowlist: "grep"
```

The warnings appear once per spawned subagent. Root cause: the Copilot
model infers tool restrictions for child agents and guesses short names
("create", "edit", "grep") that do not match Copilot's registered tool
name registry. The developer-agent definition carries no `tools:`
frontmatter, so the model fills the gap with hallucinated names. The
subagents still run — with unrestricted tool access instead of the
intended narrower scope.

## Problem

1. **Silent scope failure.** The tool allowlist is meant to constrain
   what the subagent can touch. Because every name is rejected as
   unknown, the constraint is never applied — the subagent runs with
   full tool access. This defeats the purpose of step-guard's
   read/write isolation.

2. **Log noise.** Six subagents × three unknown names = eighteen
   warnings per dispatch run, obscuring real diagnostics.

3. **Cross-CLI divergence.** Claude Code, Pi, and Codex each have
   different native tool names. The canonical agent definitions in
   `factory/agents/` are CLI-neutral today — they carry no `tools:`
   key. Adding Copilot-specific tool names to the canonical definition
   would break that neutrality.

## Proposed Solution

Add a `tools` mapping to each CLI projection's agent definition at
init-factory time. The canonical definition stays CLI-neutral; the
generated per-CLI copy gets the correct tool names for that CLI.

### Concrete changes

1. **Extend `init-factory`** to inject a `tools:` frontmatter key when
   generating `.github/agents/*.md` from `factory/agents/*.md`. The
   tool names are resolved from a CLI-specific mapping table:

   | Canonical role | Copilot tool name   |
   | -------------- | ------------------- |
   | read           | `read_file`         |
   | write          | `write_file`        |
   | edit           | `edit`              |
   | search         | `search_files`      |
   | terminal       | `run_in_terminal`   |

   Only tools the agent's workflow actually requires are listed.

2. **Developer-agent allowlist** (Copilot projection):

   ```yaml
   tools:
     - read_file
     - write_file
     - edit
     - search_files
     - run_in_terminal
   ```

3. **Validate tool names** in `index-lint` by checking each
   `.github/agents/*.md` `tools:` entry against the known Copilot tool
   registry. Unknown names fail the lint.

### What this does NOT do

- Does not change canonical `factory/agents/*.md` definitions.
- Does not add tool restrictions for Claude Code or Pi (those CLIs
  enforce scope through step-guard hooks, not tool allowlists).
- Does not require a new script — `init-factory` already generates
  per-CLI agent copies.

## Alternatives Considered

| Alternative                                  | Verdict  | Reason                                                        |
| -------------------------------------------- | -------- | ------------------------------------------------------------- |
| Instruct implementation-agent not to restrict | rejected | Discards a useful defence-in-depth layer                      |
| Add `tools:` to canonical definitions        | rejected | Breaks CLI neutrality; different CLIs have different names     |
| Ignore the warnings                          | deferred | Acceptable short-term; the scope failure is the real concern  |

## Acceptance Criteria

1. A Copilot dispatch run produces zero "Unknown tool name" warnings.
2. Developer-agent subagents run with only the declared tool set.
3. `index-lint` rejects unknown tool names in `.github/agents/` files.
4. Canonical `factory/agents/` files remain free of CLI-specific keys.
