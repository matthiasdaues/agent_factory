# Rules

One-line rules, phrased as aphorisms or per **RFC 2119** (MUST / MUST NOT / SHOULD). Each links to the rulebook that expands on it — rationale, examples, and edge cases live there, not here. This file states *what*; the rulebook states *why* and *how*.

## Wisdom of the world

- Small is beautiful
- Small steps are better than big ones
- Quality is what satisfies a given use case
- Use simple language
- Keep it simple
- Better done than perfect

## Foundational principles

- **MUST** keep each skill/agent transmission short and independently verifiable — an LLM is a noisy channel; short, checked transmissions (compiler → tests → review) beat one long, unchecked one (Eichhorst's Principle).
- **MUST** build only what the specification requires, in the smallest verified step it allows (YAGNI).

## Coding

- placeholder for future rules

## Branching

- **MUST** create exactly one feature branch per story or bug — never per EPIC, sprint, or wave. → [branching-policy.md](conventions/branching-policy.md)
- **MUST** cut every feature branch from a dedicated invocation branch (itself cut from `main`), recording its origin commit as the branch root. → [branching-policy.md](conventions/branching-policy.md)
- **MUST** determine merge order from real file-overlap analysis, not a grouping label — file-disjoint branches merge in parallel, overlapping branches merge serially in dependency order. → [branching-policy.md](conventions/branching-policy.md)
- **MUST** run the full test suite after every merge, before the next. → [branching-policy.md](conventions/branching-policy.md)
- **MUST** track exactly two commit IDs per invocation — branch root and branch head. → [branching-policy.md](conventions/branching-policy.md)

## Commits

- **MUST** include the story or bug ID in parentheses on every implementation commit — `<type>: <description> (<ID>)`. → [commit-conventions.md](conventions/commit-conventions.md)

## Findings

- **MUST** file every Defect, and every finding at or above the review's blocking severity, as its own `docs/findings/<TAG>-NNNN.md`. → [finding-format.md](conventions/finding-format.md)
- **MUST** state both what is wrong and what to do in every finding. → [finding-format.md](conventions/finding-format.md)

## Markdown formatting

- **MUST** run `scripts/mdformat --number <path>` immediately after writing any markdown file — not deferred to `validate` or the pre-commit hook. → [markdown-formatting.md](conventions/markdown-formatting.md)

## Review loop discipline

- **MUST** on a repeat pass: re-run the deterministic check, verify each prior finding individually, and re-run the full inspection fresh — not just the old findings list. → [review-loop-discipline.md](conventions/review-loop-discipline.md)

## State machine notation

- **MUST** treat event-driven pseudocode as the single source of truth for state machines — Mermaid is derived, never authored first. → [state-machine-notation.md](conventions/state-machine-notation.md)
- **MUST** keep every `ChangeState(X)` in pseudocode and its Mermaid edge in exact correspondence — no mismatches. → [state-machine-notation.md](conventions/state-machine-notation.md)

## Versioning

- **MUST** keep the git tag and version file identical — no mismatches. → [versioning-policy.md](conventions/versioning-policy.md)
- **MUST NOT** tag feature branches, or apply release/pre-release tag formats on a non-main branch. → [versioning-policy.md](conventions/versioning-policy.md)
