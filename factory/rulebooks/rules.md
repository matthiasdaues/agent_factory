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
- **MUST** build only what the specification requires, in the smallest verified step it allows (YAGNI).

## Coding

- placeholder for future rules

## Branching

→ [branching-policy.md](conventions/branching-policy.md)

- **MUST** create exactly one feature branch per story or bug — never per EPIC, sprint, or wave.
- **MUST** cut every feature branch from a dedicated invocation branch (itself cut from `main`), recording its origin commit as the branch root.
- **MUST** determine merge order from real file-overlap analysis, not a grouping label — file-disjoint branches merge in parallel, overlapping branches merge serially in dependency order.
- **MUST** run the full test suite after every merge, before the next.
- **MUST** track exactly two commit IDs per invocation — branch root and branch head.

## Commits

→ [commit-conventions.md](conventions/commit-conventions.md)

- **MUST** include the story or bug ID in parentheses on every implementation commit — `<type>: <description> (<ID>)`.

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
- [commit-conventions.md § Story/Bug ID Required](conventions/commit-conventions.md#storybug-id-required)
- [cross-reference-format.md § Rule](conventions/cross-reference-format.md#rule)
- [finding-format.md § When to file](conventions/finding-format.md#when-to-file)
- [markdown-formatting.md § Rule](conventions/markdown-formatting.md#rule)
- [review-loop-discipline.md § Rule](conventions/review-loop-discipline.md#rule)
- [state-machine-notation.md § Canonical Format](conventions/state-machine-notation.md#canonical-format)
- [versioning-policy.md § Git Tag Must Match Version File](conventions/versioning-policy.md#git-tag-must-match-version-file)
