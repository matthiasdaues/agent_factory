# Rules

One-line rules, phrased as aphorisms or per **RFC 2119** (MUST / MUST NOT / SHOULD). Each section links to the rulebook that expands on its rules — rationale, examples, and edge cases live there, not here. This file states *what*; the rulebook states *why* and *how*.

## Wisdom of the world

- Small is beautiful
- Small steps are better than big ones
- Quality is what satisfies a given use case
- Use simple language
- Keep it simple
- Better done than perfect

## Foundational principles

→ [foundational-principles.md](conventions/foundational-principles.md)

- **MUST** write short, precise prose following plain English by Strunk & White, or "Gutes Deutsch" by Wolf Schneider, depending on language.
- **MUST** keep each skill/agent transmission short and independently verifiable (Eichhorst's Principle).
- **MUST** separate agentic creation from deterministic validation — agents create artifacts; unavoidable hooks trigger scripts that validate against predefined, state-dependent criteria.
- **MUST** build only what the specification requires, in the smallest verified step it allows (YAGNI).

## Proposals

→ [proposal.md template](templates/proposal.md), [feature-addition.md](../playbooks/feature-addition.md)

- **MUST** open a feature-addition from a proposal written to the [proposal template](templates/proposal.md) at `docs/proposals/<name>.md` — the design origin the Planning phase consumes.
- **MUST** clarify or grill a feature proposal in place; a decision-complete
  interview may move it from `draft` to `open`, but only stakeholder approval
  may move it to `accepted`.
- **MUST** enter specification, architecture, or planning work from an
  `accepted` proposal and route those phases from its declared impact.
- **MUST NOT** reference a `docs/proposals/*` file in a shipped agent's `inputs:` — a proposal is a design origin, not a runtime artifact; point `inputs:` at tracked, shipped artifacts (the playbook, policies, schemas it consumes).

## Coding

- placeholder for future rules

## Testing

→ [testing-strategy.md](conventions/testing-strategy.md)

- **MUST** give each observable contract one owning test layer and strengthen that owner before adding overlap.
- **MUST** select test cases by equivalence class, boundary, or distinct failure mode — never to meet a cosmetic count or fixed coverage percentage.
- **MUST NOT** duplicate a deterministic linter's rule in pytest.
- **MUST** prove a surviving owner detects a representative fault before deleting overlapping tests.

## Branching

→ [branching-policy.md](conventions/branching-policy.md)

- **MUST** create exactly one feature branch per story or bug — never per EPIC, sprint, or wave.
- **MUST** cut every feature branch from a dedicated invocation branch (itself cut from `main`), recording its origin commit as the branch root.
- **MUST** determine merge order from real file-overlap analysis, not a grouping label — file-disjoint branches merge in parallel, overlapping branches merge serially in dependency order.
- **MUST** run the full test suite after every merge, before the next.
- **MUST** track exactly two commit IDs per invocation — branch root and branch head.
- **MUST** run `factory/scripts/verify-base` as a worktree-isolated subagent's first tool call, against its target branch and its declared base SHA; halt on any non-zero exit before reading, editing, or committing anything.
- **MUST** run `factory/scripts/premerge-check` on a finished branch before merging it; a non-zero exit blocks the merge until investigated.

## Dispatch

→ [dispatch-contract.md](conventions/dispatch-contract.md)

- **MUST** give any sub-agent a resolvable instance ID to report back to, never the parent's agent-type name.
- **MUST NOT** block indefinitely on a sub-agent's reply — do the work yourself if it declines or doesn't respond.
- **MUST** split a whole-codebase dispatch into smaller, independently mergeable dispatches rather than run it as one.
- **MUST** checkpoint a long-running dispatch with commits between rounds.
- **MUST** verify a sub-agent's reported result against observable state (git, tests, gates) before treating the work as done — the mechanical gates, not the self-report, are authoritative.

## Commits

→ [commit-conventions.md](conventions/commit-conventions.md)

- **MUST** include the story or bug ID in parentheses on every implementation commit — `<type>: <description> (<ID>)`.

## Git workflow

→ [git-workflow.md](conventions/git-workflow.md)

- **MUST** issue git as a lone command — never chained after `cd` or another command (the working directory persists; the guardrail mis-parses compound lines).
- **MUST** run `factory/scripts/premerge-check <target> <branch>` before `git merge <branch>` — the merge is blocked without the resulting `.agent-factory/premerge-check-ok` marker.
- **MUST NOT** bypass a failing pre-commit hook (`--no-verify`, `core.hooksPath`); fix the hook. Discard with `git checkout HEAD -- <path>`, not `git checkout .`.
- **SHOULD** commit through the hooks with the two-pass sequence — `add` → `commit`; on "files were modified by this hook", `add -u` → recommit — or use `factory/scripts/commit-safe`.
- **MUST** remove a clean worktree and safely delete its merged branch after its target passes verification, unless the branch remains a named active review base.
- **MUST** use full 40-character SHAs in machine-consumed gates, markers, dispatch records, and handoffs; abbreviated SHAs are display-only.

## Handoffs

→ [handoff-format.md](conventions/handoff-format.md)

- **MUST** put one authoritative current-state section before optional historical context.
- **MUST** record exact local and upstream tips plus ahead/behind counts; decorated branch labels and approximate counts are insufficient.
- **MUST** replace or move superseded instructions instead of leaving them mixed with current open work.

## Cross-references

→ [cross-reference-format.md](conventions/cross-reference-format.md)

- **MUST** write every reference to another artifact in this repo (ADR, finding, todo entry, rulebook, skill, agent, spec document) as a full markdown link — never a bare ID, code span, or parenthetical.
- **MUST** anchor every cross-reference to the specific section where the target has one.

## Findings

→ [finding-format.md](conventions/finding-format.md)

- **MUST** file every Defect, and every finding at or above the review's blocking severity, as its own `docs/findings/<TAG>-NNNN.md`.
- **MUST** state both what is wrong and what to do in every finding.

## Markdown formatting

→ [markdown-formatting.md](conventions/markdown-formatting.md)

- **MUST** run `scripts/mdformat --number <path>` immediately after writing any markdown file — not deferred to `validate` or the pre-commit hook.

## Review loop discipline

→ [review-loop-discipline.md](conventions/review-loop-discipline.md)

- **MUST** re-run the deterministic check on every repeat review pass.
- **MUST** verify each prior finding individually on a repeat review pass.
- **MUST** re-run the full inspection fresh on a repeat review pass — not just the prior findings list.

## State machine notation

→ [state-machine-notation.md](conventions/state-machine-notation.md)

- **MUST** treat event-driven pseudocode as the single source of truth for state machines — Mermaid is derived, never authored first.
- **MUST** keep every `ChangeState(X)` in pseudocode and its Mermaid edge in exact correspondence — no mismatches.

## Todos

→ [todo-format.md](conventions/todo-format.md)

- **MUST** file every deferred decision or unresolved question as an entry in `docs/spec/todo.md` — not left implicit in conversation.

## Versioning

→ [versioning-policy.md](conventions/versioning-policy.md)

- **MUST** keep the git tag and version file identical — no mismatches.
- **MUST NOT** tag feature branches, or apply release/pre-release tag formats on a non-main branch.

## Referenced from

- [foundational-principles.md](conventions/foundational-principles.md)
- [branching-policy.md § Project-Specific Rules](conventions/branching-policy.md#project-specific-rules)
- [dispatch-contract.md § Project-Specific Rules](conventions/dispatch-contract.md#project-specific-rules)
- [commit-conventions.md § Story/Bug ID Required](conventions/commit-conventions.md#storybug-id-required)
- [cross-reference-format.md § Rule](conventions/cross-reference-format.md#rule)
- [finding-format.md § When to file](conventions/finding-format.md#when-to-file)
- [markdown-formatting.md § Rule](conventions/markdown-formatting.md#rule)
- [review-loop-discipline.md § Rule](conventions/review-loop-discipline.md#rule)
- [state-machine-notation.md § Canonical Format](conventions/state-machine-notation.md#canonical-format)
- [versioning-policy.md § Git Tag Must Match Version File](conventions/versioning-policy.md#git-tag-must-match-version-file)
