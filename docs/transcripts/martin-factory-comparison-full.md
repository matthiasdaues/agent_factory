Here's the full comparison. Tenets grouped by theme:

────────────────────────────────────────────────────────────────────────────────

The Tenets Bob Martin Formulated

From the transcript, eight core processual ideas:

1. Don't steer; verify — Long prompts are unreliable ("lost in the middle").\
   Use automated checks instead of prose rules.
2. Creation ≠ validation — Agents write; deterministic tools judge. No agent\
   self-validation.
3. Multi-agent pipeline with clean context per role — Specifier → Coder →\
   Cleaner → Hardener → QA. Each agent is born, works, and dies. Fresh context\
   prevents trajectory drift.
4. Context window is a finite resource — Keep the prompt minimal. The smart\
   zone is the first ~150k tokens; everything after is diluted.
5. Cost of change has collapsed — Aggressive refactoring is now affordable.\
   Heavy upfront planning is expensive by comparison.
6. Impose values, not disciplines — TDD's values (tests exist, coverage\
   is high) remain valid; TDD's discipline (alternating lines) is a human\
   cognitive aid that makes no sense for agents.
7. Module structure is an attention budget — Deep modules with small\
   interfaces let models read the contract without reading the internals. (Cites\
   Ousterhout's A Philosophy of Software Design.)
8. Verify against observable state, not agent self-report — Watch for the\
   thrash pattern (context decay, circular fixes, giving up). Trust the gates,\
   not the agent's summary.

────────────────────────────────────────────────────────────────────────────────

How the Factory Maps to Each

### ✅ Already fully implemented

┌────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Tenet │ Factory mechanism │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Don't steer; verify │ validate skill; premerge-check; transition-lint pre-commit hook │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Creation ≠ validation │ Foundational Principle: "agents create; gates validate. No agent self-validation." │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Multi-agent pipeline │ feature-addition → requirements-agent → spec-review → architecture → planning → implementation → reconciliation → qa (6 │
│ │ roles) │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Context discipline │ handoff-format.md (hard phase-boundary flush); fresh-spawn rule for review-fix loops; caveman skill (Eichhorst's │
│ │ Principle) │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Agile over waterfall │ proposal.md lifecycle: draft → open → accepted → implemented; Epic 0 chains; wave-based incremental dispatch; YAGNI │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Impose values, not disciplines │ testing-strategy.md: mandates contract ownership and behavior-based case selection — not line-alternation mechanics │
├────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Verify against state, not │ dispatch-contract § Verify Sub-Agent Reports: explicit git cat-file -e, git branch --contains commands; envelope error │
│ report │ ≠ failure clause │
└────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

### ⚠️ Implemented at the documentation layer; not enforced mechanically

┌─────────────────────┬────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┐
│ Tenet │ Factory mechanism │ Gap │
├─────────────────────┼────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ Module structure = │ architecture.dsl (structurizr) as the │ No automated dependency-rule gate. Martin's "automated checker that forces dependency │
│ attention budget │ authoritative module boundary map; prose │ inversion or interface insertion on violation" is absent. The Factory describes │
│ │ is derived from DSL, not the source of │ architecture; it does not protect it mechanically. │
│ │ truth │ │
├─────────────────────┼────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤
│ Semantic │ testing-strategy.md layer model: linter → │ No cyclomatic complexity gate, no mutation testing, no coverage enforcement by │
│ deterministic gates │ contract test → integration → e2e smoke │ operator-flip. The Factory's linter layer is syntactic (formatting, schema, naming). │
│ │ │ Martin's quality gauntlet includes semantic checks (crappy analysis, mutation │
│ │ │ coverage). The validate skill needs a semantic-quality extension to close this. │
└─────────────────────┴────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────────────────────────

The One Genuine Gap

The Factory lacks semantic deterministic gates — automated checks that operate on code meaning, not just format.

Martin's key operational insight: agents are fast enough to run cyclomatic complexity scoring (crap analysis) and mutation testing (flip every < to >, every
== to !=, expect tests to fail) at machine speed. The Factory's validate skill currently handles linting, type checking, and formatting — it does not yet\
run radon, mutmut, deptrack, or equivalent tools against the committed code.

Adding a quality-gate skill that wraps these would make the Factory's verification model complete against Martin's standard — and close the one place where\
the Factory trusts agents to self-report on code quality.

────────────────────────────────────────────────────────────────────────────────
