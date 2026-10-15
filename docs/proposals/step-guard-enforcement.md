---
schema_version: 2
title: Step Guard Enforcement
status: draft
owner: Matthias Daues
created: 2026-10-15
updated: 2026-10-15
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - packages/factory/config/hooks/step-guard.sh
    - packages/factory/scripts/step-guard
    - packages/factory/scripts/dispatch_lib.py
    - packages/factory/scripts/init-factory
    - packages/factory/playbooks/feature-addition.md
    - packages/factory/rulebooks/rules.md
    - packages/factory/docs/factory-guide.md

governance:
  assurance: elevated
  risk_domains:
    - reliability
    - operations

estimate:
  as_of: 2026-10-15
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Step Guard Enforcement

## Primer

The primer is written once the open questions are decided.

## Summary

The step guard checks every read, write, and shell command an agent makes
against the step it is working on. It allows what the step's manifest
declares and denies the rest. Today the guard never runs. This proposal makes
it run for dispatched stories, with a manifest that lets a developer agent
read the code it needs and write only what its story declares.

## Motivation

`rules.md` requires every step to stay inside the inputs and outputs its
manifest declares, and the factory guide says the guard blocks anything
else. Neither is true today. The bug hunt of 2026-10-15 found five separate
reasons, any one of which keeps the guard from enforcing anything
([bug-hunt report § G-1](../reviews/bug-hunt-2026-10-15.md#g-1--the-step-guard-never-runs-and-its-denials-would-not-block),
[§ R-5](../reviews/bug-hunt-2026-10-15.md#r-5--step-manifests-are-missing-or-block-required-work)):

1. **The hook looks in the wrong place.** `step-guard.sh` looks for
   `factory/scripts/step-guard`, a layout that no longer exists, and exits 0.
2. **A denial does not block.** `step-guard` exits 1 on a denial. Claude Code
   blocks a tool call only on exit code 2.
3. **The guard never finds a manifest.** `dispatch_lib.write_manifest`
   writes to `.current-work/<feature>/<story>/current-step.yml`. The guard
   reads `.current-work/current-step.yml` in the current directory.
4. **A story manifest lists IDs, not paths.** Without explicit `inputs`, the
   manifest's read list is the story's `deps` and `traces`, such as
   `ST-0001`. A developer agent could not read `src/`.
5. **Paths do not match.** Claude Code passes absolute paths. The guard
   compares them with relative prefixes and glob patterns.

No tool writes a manifest for a playbook step that is not a dispatched
story, although `rules.md` requires one. The declarations in
`feature-addition.md` are therefore never enforced.

Switching on the guard by fixing only the first two reasons would block
correct work, so the five must change together.

## Design

The design is open. The questions below decide it.

## Scope

**In the first release:**

- Enforcement for dispatched stories in their worktrees, in Claude Code.

**Explicitly deferred (do NOT plan stories for these):**

- Enforcement for playbook steps that are not dispatched stories, until a
  tool writes their manifests.
- Codex, Copilot, and Pi adapters, until their blocking semantics are
  checked against the installed versions.

## Open Questions

- **Where does the guard find the manifest?** One option: the guard walks up
  from the current directory to the worktree root and reads
  `.current-work/<feature>/<story>/current-step.yml` for the branch checked
  out there. Another: `dispatch` writes the manifest to the flat path the
  guard reads.
- **What may a developer agent read?** One option: everything in the
  worktree except other stories' manifests and ledgers, so the guard limits
  writes only. Another: the story declares read globs, and planning must
  fill them.
- **How are paths compared?** The guard needs one rule for absolute paths,
  paths outside the worktree, and symbolic links.
- **What happens to `rules.md` § Step boundaries for playbook steps?** Either
  a tool writes their manifests, or the rule is limited to dispatched
  stories.
- **How does a denial reach the agent?** Claude Code shows the hook's stderr
  on exit code 2. The message must name the manifest and the declared
  pattern the path missed.

## Completion Criteria

- In a dispatched story's worktree, a write outside the story's declared
  outputs is blocked in Claude Code, and the agent sees which manifest and
  pattern denied it.
- A developer agent can read the code it needs for its story without a
  denial.
- Outside a dispatched story's worktree, the guard allows every call.
- `rules.md` and the factory guide describe exactly what the guard enforces.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by     | Decision                                                                                                                                  | Raised by         |
| ------ | ---------- | -------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| DEC-01 | 2026-10-15 | decision | Matthias Daues | Turning on the guard is a design task, not a bug fix. Until it is built, `rules.md` and the factory guide say the guard does not enforce. | Bug hunt G-1, R-5 |

## Review findings

| ID  | Pass | Severity | Check | Status | Finding | Resolution |
| --- | ---- | -------- | ----- | ------ | ------- | ---------- |

## Review passes

| Pass | Date | Reviewed commit | Disposition | Failed checks | Summary |
| ---- | ---- | --------------- | ----------- | ------------- | ------- |
