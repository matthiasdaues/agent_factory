# Factory vs. Martin: Tenets Compared

Comparing the Agent Factory's processual ideas against the principles Uncle Bob
Martin formulated in the 2026-08-20 Pocock/Martin podcast on agentic coding.

______________________________________________________________________

## 1. The Foundational Contract: Creation ≠ Validation

### Bob Martin

> *"Agents create; deterministic tools verify after the fact. The models treat
> your rules as Pirates-of-the-Caribbean guidelines — they *might* follow them."*

He identifies the core failure: long prose prompts get "lost in the middle" as
the context window grows. Rules at the start and end survive; rules in the
middle are gone. Steering by instruction is unreliable.

### Factory

**Agentic Creation, Deterministic Validation** — factory's foundational
principle, enforced across:

- Every `agent` frontmatter declares creation-only outputs; no agent self-validates.
- `factory/scripts/validate` runs linting, type checks, and test gates
  mechanically after agent creation.
- `transition-lint` pre-commit hook blocks commits that violate format,
  frontmatter, or naming rules.
- `factory/scripts/premerge-check` blocks merges on diff scope and stale base.

### Verdict

**Factory nails this**. The echo is exact. The one gap: the Factory's
deterministic tools are largely *syntactic* (formatting, naming, frontmatter
schema). Martin's gauntlet includes *semantic* gates — cyclomatic complexity,
mutation testing, dependency-rule checking — that operate on the code's
meaning. The Factory's `validate` skill could grow that dimension.

______________________________________________________________________

## 2. Multi-Agent Pipeline (Role Specialisation)

### Bob Martin

> *"Specifier → Coder → Cleaner → Hardener → QA. Each agent is born, does its
> task, and dies. The next one comes in with a clean context."*

Each role is narrowly scoped to stay within the attention budget (the "smart
zone" of the context window's first ~150k tokens, per Dex Hardy). The
specialist focus also keeps rules from being lost in the middle.

### Factory

The `feature-addition` playbook maps a pipeline of **six roles**:

| Martin pipeline | Factory equivalent                           | Notes                               |
| --------------- | -------------------------------------------- | ----------------------------------- |
| Specifier       | `requirements-agent`                         | Derives spec from accepted proposal |
| Coder           | `implementation-agent` → `developer-agent`   | Dispatches per-story, TDD, parallel |
| Cleaner         | `implementation-agent` (reconciliation role) | Cleans up context within story      |
| Hardener        | `reconciliation-agent`                       | Verifies spec/code alignment        |
| QA              | `qa-agent`                                   | Fagan inspection, security review   |

The Factory's pipeline is **longer and more review-heavy** than Martin's
minimal gauntlet (4–5 steps). It also explicitly separates `reconciliation-agent`
(bring docs back to code) from `qa-agent` (inspect the code itself) — a
refinement Martin doesn't spell out.

### Verdict

**Factory is richer** — it has more explicit review gates and separation of
review from creation. The trade-off is a longer cycle time. Martin's pipeline
favors speed over processual thoroughness; the Factory favors correctness over
throughput. Both agree: role specialisation is mandatory, not optional.

______________________________________________________________________

## 3. Context Window Discipline

### Bob Martin

> *"Trim the initial prompt to its absolute minimum. Keep the trajectory
> clean. The stuff in the middle of the context is just gone."*

"Trajectory" is Martin's term for the direction a context window is moving
toward — once set, it persists. Anything that contaminates the trajectory
(off-topic context, mixed concerns) degrades quality. Compartmentalisation by
module keeps the model focused.

### Factory

Three mechanisms enforce context discipline:

1. **`handoff-format.md`** — Outgoing agent writes a canonical current-state
   section; incoming agent reads it in a **fresh session** with bounded chunk
   reads. No transcript replay.

2. **Phase boundary hard stop** — Every transition in `feature-addition.md`
   requires a clean handoff *before* the next phase begins. Context is flushed
   at each boundary.

3. **`caveman` skill** — Ultra-compressed communication mode that strips filler,
   articles, pleasantries. Keeps transmissions short per **Eichhorst's
   Principle**.

4. **`fresh agent for review-fix loops`** — feature-addition § Approval Contract:
   *"spawn a fresh agent for the fix pass rather than resuming the original.
   The original agent's context contains the full grilling transcript, every
   prior tool call, and every file read; resuming it replays all of that."*

### Verdict

**Factory has the right instincts** but implements them differently. Martin
deals with context discipline by killing and respawning agents (per-step
death/rebirth). The Factory does it through session-boundary handoffs and
fresh-spawn rules — slightly heavier but equally effective. The Factory's
`caveman` skill is a direct expression of "short verified transmission beats
long unchecked one."

______________________________________________________________________

## 4. Cost-of-Change Collapse → Agile Over Upfront Planning

### Bob Martin

> *"The cost of change has plummeted. Why would you do heavy upfront planning?
> Just fiddle until it looks right."*

He argues that heavy spec-driven development repeats the waterfall failure of
the 1970s. The waterfall's flaw: the plan never matches reality, and you paid
twice (once to plan, once to fix the mismatch). With agents, incremental
agile — small steps with continuous feedback — is cheaper than ever.

### Factory

**YAGNI** and the **proposal lifecycle** encode the same tension:

- `proposal.md` goes through `draft → open → accepted → implemented` — each
  gate is a decision point, not a planning monolith.
- **Charter amendment check** (feature-addition § Step 0.1a) only happens when
  the feature genuinely requires it, not speculatively up front.
- **Epic 0 scheduling** — project setup runs first; feature work chains on it
  via dependency graph; no upfront master plan required.
- **Wave-based dispatch** — stories implement in small verified increments,
  each checkpointable, each independently mergeable.

### Verdict

**Factory and Martin agree completely here.** The Factory's proposal lifecycle
is a disciplined, traceable version of Martin's "fiddle until it looks right"
— disciplined because each increment is tracked, diffed, and verified; not
unstructured exploration.

______________________________________________________________________

## 5. Impose Values, Not Disciplines

### Bob Martin

> *"It is a mistake to impose a human discipline on an agent. It is not a
> mistake to impose human values on the agent."*

Example: TDD's *values* (tests exist, coverage is high, cyclomatic complexity
is bounded) remain valid. TDD's *discipline* (alternating line-by-line red/
green) is a human cognitive aid that makes no sense for an agent that can hold
a full function in its attention.

### Factory

The testing strategy encodes **values without prescribing mechanics**:

- `testing-strategy.md` states: *"Test count and coverage percentage are
  diagnostics, not quality targets."*
- It mandates **contract-owned testing** (one owner per observable contract) and
  **case selection by behavior** (equivalence classes, boundaries, failure
  modes) — these are values about *what* to test, not *how* to structure the
  test-while-coding loop.
- `developer-agent` says "Red-green TDD" as a workflow label but does not
  enforce line-alternation discipline; it enforces the *outcome* (working,
  tested code).

### Verdict

**Factory follows this tenet**. The testing-strategy conventions are values
(contract ownership, boundary coverage, no coverage theater) without mandating
a specific mechanical procedure. The TDD label in the developer-agent prompt is
a semantic shorthand for "write tests before or alongside code," not a
line-by-line ritual.

______________________________________________________________________

## 6. Module Structure as Attention Budget

### Bob Martin

> *"Compartmentalize nicely. A well-partitioned module with disciplined
> interfaces is something a human can grasp — so do the models, maybe at a
> slightly different threshold. Deep modules with small interfaces let models
> read the interface without reading the implementation."*

He cites John Ousterhout's *A Philosophy of Software Design*: deep modules
hide complexity behind a small surface area. For agents, this is a cognitive
compression trick — the model doesn't need to re-understand the internals if
the interface is self-documenting.

### Factory

**`brownfield-onboarding.md`** encodes this at the project level:

> *"MUST start onboarding by creating and filling `docs/arc42/architecture.dsl`
> from code before writing architecture prose."*
>
> *"MUST treat arc42 chapters 05, 06, and 07 as derived explanations of
> `architecture.dsl` views, not independent sources."*

The Factory's **structurizr DSL** is the machine-readable module boundary map —
the deep-module interface for agents. The `maintain-architecture` and
`model-structurizr-slice` skills enforce that module boundaries are explicit
and enforced, not prose descriptions of a mess.

The **dependency-inversion enforcement** in Martin's talk (a checker that
runs at the end and fixes violations by inverting a dependency or inserting
an interface) has no direct Factory equivalent — the Factory's architecture
tools describe the architecture, but there is no automated gate that detects
and auto-fixes dependency-rule violations.

### Verdict

**Factory has the documentation layer right** (DSL-first, prose-derived) but
is **missing the enforcement layer**. Martin's "automated architecture checker
that keeps module rules from being violated" is absent. This is a meaningful
gap for teams that want the Factory to actively protect architecture quality,
not just describe it.

______________________________________________________________________

## 7. Deterministic Gates as the Real Quality Mechanism

### Bob Martin

> *"If these things are fast, and they are, and if I can constrain them to do
> a good job, then I am not going to impose my slowness upon them. My bonus is
> reviewing the code at some level of detail. They are fast with code. I am slow
> with code."*

His operational model: agents do the work at machine speed; human's job is to
operate the gates, interpret the results, and make strategic decisions. The
gates (crap analysis, mutation testing, lint, test run) run deterministically
and their output is what the human trusts.

### Factory

**Layered gate model** (testing-strategy.md):

| Layer                 | What it gates                                       |
| --------------------- | --------------------------------------------------- |
| Deterministic linter  | Declarative structure, formatting, schema           |
| Contract test         | Pure behavior, parsing, policy, state transitions   |
| Integration test      | Boundaries: installation, persistence, subprocesses |
| End-to-end smoke test | Representative CLI/workflow journey                 |

Plus `factory/scripts/premerge-check` (stale base, diff scope), `handoff-lint`
(current state accuracy), `backlog-lint` (story format), `charter-lint` (charter
completeness).

### Verdict

**Factory's gate model is more systematic** than Martin's informal tool stack.
Where Martin composes a personal toolset (crap, mutation tester, his own
dependency checker), the Factory codifies gates into a layered strategy with
clear ownership per layer. The gap is again semantic depth: the Factory's
linter layer is syntactic; Martin's gates include semantic quality (cyclomatic
complexity, mutation coverage).

______________________________________________________________________

## 8. Verification Against Observable State, Not Agent Self-Report

### Bob Martin

> *"An agent's success report is a claim, not proof."*

He describes watching agents thrash, slow down, and eventually give up when
code gets messy — and then having them clean up the mess without trusting them
to report honestly on their own work.

### Factory

**dispatch-contract.md § Verify Sub-Agent Reports Against State**:

> *"Before treating a dispatched unit of work as done, verify it against
> observable state — the branch tip and `git log`, the actual test run, and
> the mechanical gates — never the self-report alone."*

Concrete enforcement:

```
git cat-file -e <sha>^{commit}     # SHA exists as a commit object
git branch --contains <sha>         # SHA lives on the expected branch
```

Plus `premerge-check` blocking merges from false reports, and the dispatch
ledger tracking `verify_base`, `premerge_check`, `commit_sha` for every story.

### Verdict

**Factory is the stricter implementation of this tenet.** Martin describes the
principle verbally; the Factory encodes it as mechanical protocol with
explicit shell commands. The `envelope error is not proof of failure` clause
(another dispatch-contract section) even accounts for the exact failure mode
where the agent completes but the handshake message is lost — showing the
Factory has learned this from live incidents.

______________________________________________________________________

## 9. Parallel Dispatch With Scope Caps

### Bob Martin

> *"You can run them in parallel. Three coders on my little laptop — it can
> support a lot more than three. When you focus the agents down to a single
> task, you're keeping the context window under control."*

He advocates parallel fan-out at the task level, with scope control per agent.

### Factory

**implementation-agent** implements exactly this:

- One feature branch + worktree **per story** — not per EPIC, not per sprint.
- File-overlap analysis: parallel-safe stories dispatch simultaneously; file-
  sharing stories dispatch serially in dependency order.
- **Wave cap** (default 6, not unlimited) — prevents spend-limit death and
  cascading mid-wave failures.
- **Scope cap**: whole-codebase dispatches are split into per-module rounds,
  each independently verifiable and mergeable.
- **Checkpointing**: commits between rounds so a resume loses only the last
  round, not the whole dispatch.

### Verdict

**Factory is more rigorous** — it has mechanised the heuristics Martin describes
verbally (parallel-safe grouping, context-window discipline per agent) and
added operational safeguards (wave cap, spend-gate cost estimation, ledger
tracking) that Martin only implies.

______________________________________________________________________

## 10. Software Fundamentals Still Matter

### Bob Martin

> *"Software is the most complicated thing humans have ever attempted. The
> fundamentals are the way we organize that complexity so it can be conceived
> by our models. The rules you throw away are the ones you'll pick up off the
> floor in a year and dust off."*

At every abstraction-layer step up (binary → assembly → compiler → AI), people
predicted fundamentals would stop mattering. They never do. Modularity, clean
interfaces, test discipline, cyclomatic complexity bounds — agents hit the same
walls humans do.

### Factory

**All of it.** The entire rulebook system is a codification of software
fundamentals:

- YAGNI, small steps, short precise prose
- Contract-owned testing, equivalence-class case selection
- Module-first architecture (structurizr DSL before prose)
- Phase-gate reviews (spec-review, architecture-review, Fagan inspection)
- Epic 0 before features; atomic branches; handoff with exact SHA recording

The Factory does not treat these as optional or situational — they are
**mechanically enforced** for certain rules (branching, dispatch, state
formats) and **discipline-enforced** for others (review loop, testing values,
architecture-first).

______________________________________________________________________

## Summary: Gap Map

| Bob Martin Tenet                                   | Factory status                                  | Gap?                                                         |
| -------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| Don't steer; verify deterministically              | ✅ Fully implemented                            | None                                                         |
| Role-specialised multi-agent pipeline              | ✅ Implemented (richer than Martin's)           | Semantic gate depth (mutation, complexity)                   |
| Context window discipline / trajectory control     | ✅ Implemented via handoffs + fresh-spawn rules | —                                                            |
| Cost-of-change collapse → agile over waterfall     | ✅ YAGNI + proposal lifecycle + waves           | —                                                            |
| Impose values, not human disciplines               | ✅ Testing strategy encodes values only         | —                                                            |
| Module structure as attention budget               | ✅ DSL-first, prose-derived architecture        | **No automated dependency-rule gate**                        |
| Deterministic gates are the real quality mechanism | ✅ Layered gate model (syntactic + contractual) | **Missing semantic gates** (cyclomatic complexity, mutation) |
| Verify against state, not agent self-report        | ✅ Mechanically enforced with git commands      | —                                                            |
| Parallel dispatch with scope caps                  | ✅ Wave model + ledger + scope cap + spend gate | —                                                            |
| Software fundamentals still matter                 | ✅ Entire rulebook system encodes this          | —                                                            |

### One Genuine Gap

The Factory lacks **semantic deterministic gates** — automated checks that
operate on code meaning, not just format. Martin's key insight is that agents
can run *crap analysis* (cyclomatic complexity + coverage scoring),
*mutation testing* (100% coverage enforced by flipping operators), and
*dependency-rule checking* (module A must not import module B) at machine
speed. The Factory's `validate` skill runs syntax and format checks; it does
not yet run semantic quality gates. Adding a `quality-gate` skill that wraps
tools like `radon`, `mutmut`, `deptrack`, or equivalent would close this
gap and make the Factory's verification model complete against Martin's
standard.

______________________________________________________________________

*Comparison produced by reading factory/rulebooks/rules.md, factory/rulebooks/conventions/foundational-principles.md, factory/rulebooks/conventions/review-loop-discipline.md, factory/rulebooks/conventions/testing-strategy.md, factory/rulebooks/conventions/dispatch-contract.md, factory/playbooks/feature-addition.md, factory/agents/implementation-agent.md, factory/agents/reconciliation-agent.md, and the transcript docs/transcripts/2026-08-20_pocock_martin_agentic_coding.txt.*
