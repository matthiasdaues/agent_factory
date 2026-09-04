# Factory Guide

What's inside `factory/`, and how its pieces fit together. New here? The [Getting Started](#getting-started) section below walks you through your first session, by hand, one step at a time.

## Getting Started

### Who this is for

You have an idea for something to build. You have an AI coding assistant — a tool like Claude Code or GitHub Copilot CLI that reads and writes files and runs commands in a terminal. What you do not yet have is a *way of working* with it that produces code you would trust in production.

That is the whole problem Agent Factory solves. You do not need to be a professional software engineer to follow along. You do need to be willing to read what the assistant proposes and say yes or no to each step.

### The one idea to hold onto

**You are the boss. The assistant does the work. You approve each step.**

Everything else is detail. Agent Factory never runs off and builds the whole thing while you look away. It works in small, visible moves, and it stops to show you each one. If a move looks wrong, you say so, and it tries again. This is deliberate: an AI is a fast but noisy worker, and the cure for noise is frequent, cheap checking — by a tool, a test, or you.

### The four words you will keep hearing

Agent Factory hands your assistant four kinds of things. Learn these four words and the rest of this guide stops feeling foreign.

| Word         | Plain meaning                                                                    | Everyday analogy                                   |
| ------------ | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Agent**    | One *job* — "write the requirements," "review the architecture," "fix one bug."  | A specialist you hire for one task.                |
| **Skill**    | One *how-to* an agent follows to do a job well.                                  | The written procedure the specialist works from.   |
| **Playbook** | A *recipe* — which agents to run, in what order, for a common situation.         | The plan for the whole job, start to finish.       |
| **Gate**     | An *automatic check* that catches mistakes before you waste time reviewing them. | The quality inspector who won't let bad work pass. |

You never memorise the full list. Your assistant reads a catalogue — [`INDEX.yaml`](../INDEX.yaml) — and picks the right agent or skill for what you asked. Your job is to know *that these things exist* so you understand what the assistant is doing when it says "I'll use the requirements agent now."

### Two ways to run it (manual mode only)

Agent Factory runs in **manual mode**: you drive a playbook yourself, one step at a time. Each step ends with a set of defined artifacts — a specification, an architecture document, a slice of code — and those artifacts are the visible marker that the step is done. You read them, decide whether the work is good, and start the next step. Nothing moves without you.

### Why two agents, not one

The single most important habit Agent Factory builds in is this: **the worker and the checker are never the same agent.**

When one agent writes a specification, a *different* agent reviews it — in a fresh session, without ever seeing the first agent's reasoning. It sees only the finished document, the way a stranger would. This is the same reason you don't approve your own expense report or review your own pull request. You cannot catch the mistake you cannot see, because the same blind spot that made it hides it.

You are what makes this real. When the requirements, architecture, or developer agent finishes and hands you its artifacts, you open a **second, clean session** and start the matching reviewer there — pointed at those artifacts and nothing else. The blank session is the isolation: the reviewer cannot lean on a conversation it never had. Author then reviewer, write then check — a fresh window between the two.

### Your very first session

Do the setup once, following [`factory/README.md`](../README.md) — it lists the handful of tools you need and the one script that wires everything up. When it is done, open your AI assistant in your project folder and say hello. It should greet you back with four options:

- **A — I'm new here — show me around.** The assistant walks you through the basics, section by section, answering questions as you go.
- **B — I want to start something.** Opens a menu of situations — spike, new project, feature, bug fix, research — and picks the right playbook for you.
- **C — I want to run an agent or playbook directly.** For when you know the factory well enough to name what you want.
- **D — I just want to talk something through.** Open conversation — no structure, no artifacts, just thinking out loud until the idea finds its shape.

If you have been here before (the assistant checks for signs of prior work — a completed spike, a charter, earlier playbook outputs), it will acknowledge what you have done and offer to skip ahead.

When you're ready, the assistant can run `poc-spike` — the training-wheels playbook. No specification, no architecture, no formal checks. One idea, turned into one small thing you can run, in minutes. It exists so you can watch an agent and your assistant work together *before* you commit to anything real. What you throw away here cost you almost nothing.

Watch what happens:

1. The assistant reads the playbook and tells you the steps it plans to take.
2. It writes a small amount of code — and shows it to you.
3. It runs it, and you see the result.
4. You react. "Yes, keep going," or "No, that's not what I meant."

That back-and-forth *is* Agent Factory. Everything larger is the same loop, with more rigour bolted on.

At any point you can ask the assistant "where am I?" or "what do I do next?" and it will reorient you.

### The bigger picture: five phases

When you graduate from spikes to real work, Agent Factory drives your assistant through five phases, in order. Think of it as a production line that turns a rough idea into finished code:

1. **Requirements** — What are we actually building, and for whom? The assistant interviews you, sometimes stubbornly, until the answer is clear and written down.
2. **Architecture** — How will it be shaped? The big structural decisions, made on purpose and recorded, before any code locks them in.
3. **Planning** — The work broken into a backlog of small, independent stories.
4. **Implementation** — Each story built test-first: the test comes before the code, so the code has something to prove itself against.
5. **Quality** — Independent review, a security pass, and a hunt for the bugs the earlier steps missed.

Each phase has an author and a reviewer, and you approve the handover between them. You do not have to run all five. Most real tasks — a bug fix, a small feature, a documentation cleanup — use a shorter playbook that touches only the phases it needs.

### Which playbook, when

Once the first spike feels comfortable, pick the recipe that matches your situation. You do not choose the agents yourself; the playbook does. You just choose the playbook.

| You want to…                                           | Start with               |
| ------------------------------------------------------ | ------------------------ |
| See whether a rough idea works at all                  | `poc-spike`              |
| Fix one reported bug                                   | `bug-fix`                |
| Bring the docs back in line with the code              | `documentation-update`   |
| Build a brand-new project properly, start to finish    | `greenfield-development` |
| Add Agent Factory to code that already exists          | `brownfield-onboarding`  |
| Add a feature to a project the factory already manages | `feature-addition`       |

The full list, with a sentence on each, lives in [§ Playbooks](#playbooks) below.

### Three habits that keep you safe

1. **Read before you approve.** The assistant will always show you its move. Slow down enough to actually read it. Your "yes" is the last gate, and it is the one that matters most.
2. **Let the gates do their job.** When a check blocks a commit or a test fails, that is the system working, not the system breaking. Fix the cause; don't route around the alarm.
3. **One small step at a time.** Resist "just build the whole thing." Small, checked steps are how the noise gets corrected before it compounds. This is not slower in the end — it is how you avoid the day-long detour.

### Where to go next

- Set up the tooling: [`factory/README.md`](../README.md)
- Run your first spike: `poc-spike`

You do not need anything else to start. Run one `poc-spike`, watch the loop, and come back for the rest when you are curious. The factory rewards learning by doing.

**Everything below is reference material. You don't need it yet.**

## Agent Context

`docs/agent-context/` is a routing switchboard that connects agents to a project's own knowledge. It is not a knowledge base — it tells agents where to look, never what they will find there. Think of it as a stable endpoint: the structure changes slowly, but the content beneath it grows with the project.

### How it works

The system has two layers. Layer 2 consists of three index files — `stack.yaml` (what the project is built with), `workflow.yaml` (how to build, test, and deploy it), and `governance.yaml` (what rules apply). Layer 1 is `reading-guides.yaml`, a concern-based routing table that tells agents which index-file sections are relevant to a given topic (backend, testing, architecture, packaging, and so on).

### Field states

Every field in an index file is in one of three states:

- **Valued** — the field carries a `name:` (a display label) and optionally a `source:` (the authoritative document). Early fields may have only `name:` before source documents exist; mature fields carry both.
- **Deferred** — the field carries `deferred: "<reason>"`. A conscious choice to postpone, not a defect.
- **Absent** — the key does not exist, meaning the concept does not apply to this project.

`null` is never valid — it is always a lint error.

### How VIRGIL sets it up

During project setup, VIRGIL walks through a structured interview concern by concern. Each question maps to an index file and a suggested key. The operator confirms which keys are relevant, provides values (and source pointers when documents already exist), defers what is not yet decided, and skips what does not apply. Only confirmed keys are created — the structure is tailored to the project, not a one-size-fits-all template.

### What you control

The top-level key schema (stack, workflow, governance) and lint rules belong to the factory. Everything below the top level — second-level keys, their values, and their source pointers — belongs to the project owner. You can add keys, rename them, remove them, and customize the reading guide's concerns. The factory proposes; you decide.

### Keeping it current

`update-context` is the skill that writes to index files after initial setup. When you add a key or change a source pointer, it asks which reading-guide concern the key belongs to and updates the routing table immediately. The reconciliation agent compares your index files against the factory's current interview guide during regular passes and surfaces new suggested keys that your project has not been asked about yet — suggestions, not errors.

## Agents

An agent is one job — "write requirements," "review the architecture," "implement one story." Each agent is a single markdown file in `factory/agents/`, read by your AI CLI at the start of a session.

Most phases have two agents: an **author** and a **reviewer**. The author produces an artifact (a spec, an architecture doc, code). The reviewer checks it in a separate session, without seeing the author's reasoning — only the artifact itself. This catches mistakes a self-review would miss, the same way a second pair of eyes catches things you can't see in your own pull request.

In addition to the phase-chain agents, several **Phase 0 utility agents** support the work without belonging to a specific phase:

- **chat-agent** — open-ended conversation that helps an idea find its shape. Starts formless and coalesces into the right next step: a feature proposal, a research brief, a spike, or just a finished conversation.
- **kit-manager** — sets up agent context (`docs/agent-context/`), runs a structured interview to fill gaps, and accepts ad-hoc reference material. See [Agent Context](#agent-context).
- **coaching-agent** — runs retrospectives, extracts action items, and tracks process improvements across sessions.
- **proposal-review-agent** — reviews a feature proposal for clarity, feasibility, and planning readiness. Consultative on drafts, adversarial on open proposals.

These agents form a natural pipeline from idea to feature delivery. A typical flow: **chat-agent** explores an idea → the `draft-proposal` skill crystallizes it into a proposal → **proposal-review-agent** pressure-tests the proposal → the `feature-addition` playbook delivers the feature through the phase chain.

The full list, grouped by phase, is in [`factory/INDEX.yaml`](../INDEX.yaml). Each entry includes a `tokens` field (tiktoken cl100k_base token count of the agent's prompt text) and a `total_tokens` field (body + referenced skills + referenced rulebooks) for context window budget planning.

### Running an agent in a separate session

The author/reviewer split depends on each agent running in its own session, so the reviewer sees only the artifact, never the author's reasoning. How that separate session is created depends on the CLI:

- **Claude Code and GitHub Copilot CLI** spawn subagents natively: the parent session dispatches an agent and reads back its result.
- **Codex** generates native custom agents under `.codex/agents/`. Spawn those agents through Codex's subagent mechanism; do not read the canonical Markdown and role-play it in the parent thread.
- **Pi** has no native subagent. `init-factory` installs a project-local extension, `.pi/extensions/run-agent.ts`, that registers a `run_agent` tool. Calling it spawns a genuinely separate `pi` subprocess with the chosen agent's markdown as its system prompt and returns the child's result. Under Pi, run a factory agent by calling `run_agent` — not by reading the agent file and acting it out in the current session, which would leak the author's reasoning into the review.

`run_agent` resolves the child's model from `config/model.conf` — the `pi.<tier>` row for the agent's declared tier — unless an explicit model id is passed, and it bounds nested spawns with a recursion-depth cap. The git-safety guardrail extension loads in the child too, so a spawned agent stays governed by the same guardrail as its parent. See [ADR-0004](../../docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md).

For parallel work, a second Pi extension, `.pi/extensions/dispatch-wave.ts`, registers a `dispatch_wave` tool — the port of `implementation-agent`, which under Claude Code relies on the native Agent tool's `isolation: "worktree"` and simultaneous subagent spawns. Given one caller-planned, file-disjoint wave, `dispatch_wave` cuts a feature branch in its own git worktree per item, spawns each agent there in parallel, and — unless told not to — runs `premerge-check` before merging each finished branch into the target. It does not plan the wave: output-file overlap and dependency ordering stay with the calling agent, exactly as `implementation-agent` documents. `premerge-check` runs against the wave's frozen base, so a sibling merge advancing the target never falsely flags a later branch as stale.

### Codex operation

`init-factory` installs Codex repository skills individually under
`.agents/skills/`, generates native custom-agent TOML under `.codex/agents/`,
and links the catalog, playbooks, rulebooks, and scripts under `.codex/`. Read
`.codex/INDEX.yaml` first. Native subagents run as separate threads, preserving
the author/reviewer boundary.

Factory-generated agents do not pin a model, reasoning level, sandbox, or
approval policy. They inherit the parent session's permissions and cannot
expand them; a narrower custom-agent policy would still take precedence.
Configure Codex's native parallel-agent limit with
`agents.max_concurrent_threads_per_session`. Parallelism does not replace the
Factory's dependency, output-overlap, and worktree-isolation rules.

Project trust and hook activation are deliberate user decisions. After
initialization, trust the project, open `/hooks`, review the installed
`PreToolUse`, `Stop`, and `SubagentStop` commands, and approve them. The
installer reports this step but cannot approve it for you. New or changed hook
definitions remain inactive until reviewed again.

## Runtime usage capture

Agent Factory records runtime token usage for Claude Code, GitHub Copilot CLI,
Codex, and Pi. Every capture site calls the same
`factory/scripts/usage-capture` pipeline: a CLI-specific transcript normalizer,
the fixed `tiktoken cl100k_base` comparison tokenizer, and an append-only JSONL
logging adapter. One record is appended to
`.agent-factory/usage/<session-key>.jsonl`; the exact text that was tokenized is
copied beneath `.agent-factory/usage/transcripts/` and linked through
`transcript_ref`. The existing `/.agent-factory/` ignore rule covers the whole
runtime area.

Initialization explicitly asks for a project name; non-interactive automation
passes `--project-name`. The installer generates a stable UUID and writes both
values to the git-ignored `config/project.json`. Every usage record contains
the non-null `project_id` and `project_name`; rerunning initialization preserves
them.

`init-factory` prepares the tokenizer at its explicit trusted installation
boundary before wiring capture hooks. It installs exact hash-verified wheels
into the owner-only `.agent-factory/usage-runtime` with builds and Python
downloads disabled. Set `UV_OFFLINE=1` for an offline initialization; capture is
enabled only when every verified artifact is already available. A missing or
invalid artifact leaves unrelated Factory setup intact and reports capture as
unavailable. Lifecycle hooks never run uv or consult its cache. Re-running init
re-verifies the committed dependency set; `remove-factory` deletes the runtime
after pending captures from every adapter settle.

Session and record identifiers are opaque data. Existing bounded lowercase
identifiers retain their familiar filenames; unsafe, platform-specific, Unicode,
or oversized values use fixed digest-based filesystem keys while their original
values remain in the JSON record. Capture rejects symlinked storage components
and never overwrites an existing transcript copy.

Usage storage is private by construction: Factory-owned runtime directories use
`0700` and files use `0600`, with existing safe owned paths repaired regardless
of umask. Configure copied text with
`init-factory --usage-transcript-retention full|omit`, override temporarily via
`AGENT_FACTORY_USAGE_TRANSCRIPT_RETENTION`, or pass the capture CLI option.
`omit` preserves all token totals and audit context but stores only an empty
evidence placeholder marked `content-omitted`. On platforms where owner-only
mode semantics cannot be enforced, omission is automatic. Invalid values also
fail closed to omission.

Records and evidence remain until their session is manually deleted or
`remove-factory` runs; no automatic TTL is applied. Pi's owner-only staging copy
is deleted immediately after processing. Regex redaction and disabling token
accounting are not supported.

Concurrent captures for one session reserve transcript paths atomically and
probe forward when another process already owns a candidate. Record IDs can
therefore contain gaps after a crashed capture. Their numeric reservation
sequence, rather than JSONL line order, determines cumulative snapshot order.

`project_id`, `project_name`, `normalized_input`, `normalized_output`, and the
derived total are always present. Provider `reported_*` fields and
`usage_granularity` are nullable when the transcript contains no provider
breakdown. Capture is best-effort: direct
invocation reports errors on stderr and returns success, while native lifecycle
adapters may suppress those errors too. Capture failure never changes session
completion or a tool result. `remove-factory` removes Factory-owned hook assets
and exact merged entries while preserving project-owned configuration.

| CLI                | Human/root trigger                 | Child trigger                                      | Accounting rule                                                                                                                                            |
| ------------------ | ---------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Claude Code        | `Stop` in `.claude/settings.json`  | `SubagentStop`                                     | The latest cumulative root excludes child internals and usage. Add each distinct child record once.                                                        |
| GitHub Copilot CLI | `agentStop` under `.github/hooks/` | `subagentStop` for supported custom agents         | Select the latest cumulative root snapshot. It is inclusive; child records are attribution only. The built-in `general-purpose` agent emits no child hook. |
| Codex              | `Stop` in `.codex/hooks.json`      | `SubagentStop`                                     | The latest cumulative root snapshot is inclusive; child records are attribution only.                                                                      |
| Pi                 | `session_shutdown` extension       | Inline at each `run_agent` / `dispatch_wave` child | The root excludes separate subprocess spend. Add every distinct descendant record once.                                                                    |

Codex project command hooks remain inactive until their current definitions are
trusted. After `init-factory`, open Codex's `/hooks` UI and approve the installed
project hooks. `init-factory` reports this activation step on fresh installs and
re-runs. Wiring the files does not activate them: Codex skips a new or changed
hook definition until it is reviewed and trusted again.

Pi human sessions capture once at graceful `session_shutdown`. Inline child
capture disables the child's shutdown extension, preventing duplicate records.
`run_agent` and `dispatch_wave` attach nesting depth and the active parent
session id. The shared resolver prefers Pi's active session file, then the
explicit child-session environment, then a process-stable fallback. Pi totals
add the human/root record and every distinct descendant exactly once because a
separate Pi subprocess's model calls are not included in its parent's provider
or normalized totals. Boundary task/result text can occur in both records
because both model invocations consumed it.

All processes in a Pi invocation tree inherit one validated canonical usage
root: the consumer project's primary checkout, derived from Git's shared common
directory. Captures therefore remain under the primary checkout even when a
nested agent runs inside a disposable dispatch worktree. An inherited root is
accepted only when it agrees with the independently derived checkout and its
Factory installation; invalid values fall back to repository derivation.
Pi writes the completed stream to that root's private capture scratch directory
as a durable handoff, then launches a Factory-owned capture supervisor through
the provisioned Python runtime with no interactive standard streams. Tokenization and record persistence
therefore do not delay human shutdown or `run_agent` / `dispatch_wave` results.
The supervisor waits outside the measured lifecycle and solely removes the
validated pending/committing marker, private completion status, and staged
source after the capture child terminates. Capture child failures retain a
bounded diagnostic in the private usage-control tree;
diagnostics contain no transcript text. Explicit uninstall cancellation is
benign and no supervisor failure recreates removed Factory paths. Only the local
durable staging write remains synchronous. Abrupt supervisor or host shutdown
can still lose an in-flight best-effort capture.

Pi uses a small Node bootstrap only until the provisioned Python supervisor
writes a private acceptance handshake. This closes the interpreter-disappears
startup window: pre-accept launcher failure or timeout cleans the validated
registration and records a bounded diagnostic, while cancel/removal stays quiet
and cannot recreate paths. After acceptance the bootstrap exits; Python remains
the only full capture supervisor.

Claude, Codex, and Copilot hooks use the same lifecycle. Before returning they
register and privately snapshot the provider transcript, then leave
normalization and persistence to the detached supervisor. Snapshot time is
O(transcript size); no tokenization or persistence blocks the hook. Standalone
Codex does not require Node.

`remove-factory` coordinates with detached captures from every adapter. Its default
`--pending-usage=drain` waits up to `--pending-timeout` seconds for every
capture registered before removal to commit; timeout restores the active
installation and exits nonzero without uninstalling. Explicit
`--pending-usage=cancel` discards registered-but-not-committing captures. A
generation fence prevents new registration after removal owns the project, and
late workers cannot recreate `.agent-factory`. No PIDs are signalled. Completed
usage and transcripts remain part of the traceless Factory footprint and are
deleted by a successful uninstall.

The registration fence relies on same-volume file hard links: each pending
token atomically snapshots lifecycle state before its metadata replaces the
token contents. `init-factory` probes this capability. If the project filesystem
does not provide it, setup for Claude, Copilot, Codex, and other Pi assets still
completes, but init and Pi runtime report that race-safe Pi usage capture is
unavailable rather than falling back to an unsafe fence.

Claude `Stop` records are cumulative snapshots of the main transcript. For
session totals, select the latest root record and add each distinct
`SubagentStop` record once. Claude's `SubagentStop.transcript_path` points to
the main transcript; Agent Factory instead captures the required
`agent_transcript_path`, which contains the child's internal messages and
per-message provider usage. Boundary task and result text can occur in both
records because it entered both model contexts; that is real normalized usage,
not aggregation duplication.

The architecture rationale is recorded in
[ADR-0007](../../docs/adr/0007-normalize-runtime-usage-through-cli-adapters.md).

### Usage-capture test ownership

Each test file owns one layer and contract boundary. Add a case to the existing
owner first. Create another file only when the new behavior belongs to a new
layer; if a regression duplicates a lower-level case, replace the overlap or
state the distinct end-to-end boundary it protects.

| Test file                                    | Layer                 | Unique contract boundary                                                                                                     |
| -------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `test_usage_capture.py`                      | Unit and component    | Transcript parsing, normalization, aggregation, record reservation, and persistence primitives                               |
| `test_usage_capture_e2e.py`                  | Installed shared path | A configured hook reaches the shared capture runtime and writes a normalized record                                          |
| `test_usage_capture_copilot_e2e.py`          | Copilot adapter       | Copilot hook payloads, inclusive-root accounting, and child-attribution behavior                                             |
| `test_usage_capture_codex_e2e.py`            | Codex adapter         | Codex hook payloads, trust-gated installation, and inclusive-root accounting                                                 |
| `test_usage_capture_pi_e2e.py`               | Pi adapter            | Extension/bootstrap handoff, descendant aggregation, supervisor ownership, and failure cleanup                               |
| `test_usage_capture_native_lifecycle_e2e.py` | Shared lifecycle      | Detached registration, drain/cancel, generation fencing, accepted-worker cleanup, and uninstall races across native adapters |
| `test_init_factory_usage_capture.py`         | Installation          | CLI-specific assets, permissions, runtime provisioning, idempotency, and capability probes                                   |
| `test_remove_factory.py`                     | Removal               | Exact Factory-owned hook stripping, pending-capture policy, and preservation of project-owned configuration                  |

The map documents ownership, not a target test count. Contract-distinct
end-to-end tests remain appropriate even when they exercise shared lower-level
code.

## Skills

A skill is a how-to — a reusable procedure an agent (or you, directly) invokes to do one well-defined thing: run a structured interview, write an ADR, run a security review. Each skill is a folder in `factory/skills/` holding a `SKILL.md`. Agents call skills; skills don't call agents.

Notable skills by concern:

| Concern         | Skills                                                                                                                                                                     |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Idea-to-feature | `draft-proposal` (crystallize an idea into a proposal), `capture-vision` (six-facet vision capture), `grilling` / `grill-me` / `grill-with-docs` (pressure-test a design)  |
| Specification   | `derive-feature` (Gherkin `.feature` files with Rule-per-actor-goal), `qa-strategy-from-spec` (per-feature QA strategy), `scope-map-migration` (track Rules across slices) |
| Onboarding      | `reverse-map` (build a scope map from code, tests, and other sources), `guided-tour` (mid-session reorientation for newcomers and active playbook runs)                    |
| Quality gates   | `crap-score` (composite structural risk), `mutation-analysis` (mutation testing), `dependency-check` (dependency vulnerability scan)                                       |
| Implementation  | `run-step` (execute a single step manifest within step isolation)                                                                                                          |

The full list is also in [`factory/INDEX.yaml`](../INDEX.yaml), with token counts per skill.

## Playbooks

A playbook is a step-by-step recipe in `factory/playbooks/` for a specific situation — which agents to run, in what order, with what to check in between. Pick the one that matches what you're doing; don't run the full phase chain when a smaller playbook fits.

### Beginner playbooks

Start with these. Small blast radius, few steps, nothing to set up first:

| Playbook                                                          | For                                                                                                                                                                                           |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`poc-spike.md`](../playbooks/poc-spike.md)                       | "Does this basic idea even work?" No spec, no architecture, no checks — one file, thrown away by default. The fastest way to see an agent and your CLI work together.                         |
| [`technical-poc.md`](../playbooks/technical-poc.md)               | A real technical risk question, usually comparing two or more candidate approaches. Heavier than `poc-spike` (multiple candidates, a Pugh Matrix, feeds an ADR), lighter than the full chain. |
| [`bug-fix.md`](../playbooks/bug-fix.md)                           | Fixing one reported defect. Four steps: file the bug, fix it with tests, QA validates, mark resolved.                                                                                         |
| [`documentation-update.md`](../playbooks/documentation-update.md) | Syncing docs with code after they've drifted. Two steps: reconcile, validate.                                                                                                                 |

### Onboarding playbooks

Greenfield and brownfield are **onboarding playbooks** — they bring a project to the point where `feature-addition` can take over. Both converge on the same three anchor files: a scope map, an `architecture.dsl`, and `docs/CONTEXT.md`. The difference is where they start and how far they go.

| Playbook                                                              | Starts from                                             | Terminal condition                                                                              |
| --------------------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [`greenfield-development.md`](../playbooks/greenfield-development.md) | A brand-new project with no code or docs.               | Scope map (all Rules `deferred`), `architecture.dsl`, arc42 prose.                              |
| [`brownfield-onboarding.md`](../playbooks/brownfield-onboarding.md)   | An existing codebase with no spec or architecture docs. | Scope map (Rules backfilled `implemented`), reverse-engineered `architecture.dsl`, arc42 prose. |

Brownfield has two stages. **Stage 1** produces the three anchor files — architecture DSL, scope map (via the `reverse-map` skill), and `CONTEXT.md` — and then offers an explicit exit. The user can start `feature-addition` from this lightweight baseline. **Stage 2** (opt-in) goes deeper: full specification extraction, component resolution, ATAM review, and reconciliation.

After either playbook completes (or after brownfield Stage 1), all feature work enters through `feature-addition`.

### Feature delivery and other full-chain playbooks

Once a project has been onboarded, these playbooks drive feature delivery and other structured work through some or all of the five-phase chain (requirements → architecture → planning → implementation → quality — see [docs/arc42/concepts.md § The phase chain](../../docs/arc42/concepts.md#the-phase-chain)):

| Playbook                                                        | For                                                                                                                                                                                                   |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`feature-addition.md`](../playbooks/feature-addition.md)       | Adding a feature to a managed project from an accepted proposal. Declared impact routes the required specification and architecture work. Owns the gate-check loop and mechanical architecture check. |
| [`refactoring.md`](../playbooks/refactoring.md)                 | Restructuring code without changing behaviour, with a measured baseline and a safety net.                                                                                                             |
| [`architecture-review.md`](../playbooks/architecture-review.md) | Reviewing existing architecture documentation against quality attributes.                                                                                                                             |

### The research workflow

Separate from the idea → production chain, research has two modes selected by
the shared brief:

- **Survey** is the default when `mode` is omitted or set to `survey`.
  [`research-survey.md`](../playbooks/research-survey.md) plans bounded source
  gathering and produces a cited synthesis. Choose it for landscape,
  discovery, and "what exists?" questions where coverage and a sourced
  overview matter more than claim verdicts.
- **Falsification** is selected only by `mode: falsification`.
  [`research-topic.md`](../playbooks/research-topic.md) tests a small number of
  contestable, consequential claims through independent research, refutation,
  review, and voting. A surviving claim is not proved; it has only withstood
  the defined tests.

Both modes are driven by the phase-6 **Research** agents and their
`research-*` skills. Every artifact passes schema validation, policy where
applicable, then semantic review before the next step begins.

A survey can identify claims that deserve stronger scrutiny, but it does not
silently change modes. Select entries from
`candidates_for_deeper_falsification_study`, write a **new research brief** for
the bounded claims with `mode: falsification`, and start
`research-topic.md`. The survey report remains source context, not evidence
that those claims already earned a falsification verdict.

## Playbook phase gates

Playbooks above are prose: nothing stops staging an architecture file before the spec gate clears except the human remembering the playbook's own instructions. An optional structured harness, layered on top, catches phase-boundary mistakes mechanically instead.

A playbook can ship a `.fsm.yml` alongside its `.md` in `factory/playbooks/` — a state machine describing each phase's `outputs:` file globs and the `entry_conditions` required to advance into it. Only [`greenfield-development.fsm.yml`](../playbooks/greenfield-development.fsm.yml) exists today. This is opt-in, not a default every playbook must adopt.

| Component                          | What it does                                                                                                         |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `.current-work/playbook-state.yml` | Local, git-ignored marker recording which state the project is currently in.                                         |
| `factory/scripts/transition-lint`  | Pre-commit gate. Blocks staging a file whose `outputs:` glob belongs to a state other than the marker's current one. |
| `factory/scripts/phase advance`    | Subcommand that checks the next state's `entry_conditions` and, if satisfied, advances the marker.                   |

`transition-lint` deliberately does not evaluate `entry_conditions` — by its own docstring, it "governs ordering *between* phases," not within one, and "does not evaluate a state's `entry_conditions`" because "that is `phase advance`'s job." It only checks whether a staged file belongs to the current state, naming the offending path and pointing at `phase advance` when a file belongs to a later one. This is a deliberate design choice, not a gap: condition-checking lives in one place only.

`phase advance` reads the next state's `entry_conditions`, evaluates each against a small `gate_conditions` library, and refuses — non-zero exit, marker unchanged — if any is unmet. Implemented condition types: `file_exists`, `files_exist`, `no_open_findings`, and `script_exit_zero` (stubbed to always pass in this proof of concept). On success it writes the marker with `recorded_at` taken from `phase advance`'s own process clock, never agent-supplied.

If the marker file is absent, both tools are no-ops — a project not using the harness sees no behavior change.

See [Structured Playbooks as a Deterministic Harness](../../docs/proposals/playbook-structured-harness-strategy.md) for the full design rationale and the proof of concept's scope. The harness now has its own full specification — actors, use cases, entity model, and business rules — at [docs/spec/prd.md](../../docs/spec/prd.md).

## Proposals

A proposal is the seed brief that opens a feature-addition — the design origin the Planning phase turns into a backlog. Proposals live in the repository-root `docs/proposals/`, one markdown file per feature, written to the [proposal template](../rulebooks/templates/proposal.md). Its versioned frontmatter records lifecycle, impact, governance, and dated forecasts for active human-review hours and normalized AI tokens. Forecasts remain distinct from append-only actuals and provider billing. Its body records the summary, motivation, design, explicit in-scope / deferred split, open questions, and completion criteria. Clarification and grilling amend this artifact directly: `draft` becomes reviewable `open`, stakeholder acceptance authorizes downstream work, and material planning changes require reacceptance. A proposal is a design *origin*, not a runtime artifact — a shipped agent's `inputs:` must never reference it. See [feature-addition.md](../playbooks/feature-addition.md) for the lifecycle and routing gates.

The `draft-proposal` skill crystallizes an explored idea into a proposal file. It runs in the current session with the stakeholder present, fills the template from conversation context, pressure-tests the result via `grilling`, and gates on completeness before setting `status: open`. The `proposal-review-agent` then reviews the open proposal in a separate session — consultative on drafts, adversarial on open proposals — using eight structured checks (testable criteria, sharp scope, decomposable design, consistent impact, existing boundaries, genuine questions, justified timing, plausible estimate).

## Rulebooks

A rulebook is a cross-cutting convention that applies across agents and skills — commit message format, how to cross-reference other documents, ADR style, branch scoping. [`factory/rulebooks/rules.md`](../rulebooks/rules.md) states each rule in one line; the matching file in `factory/rulebooks/conventions/` carries the reasoning, examples, and edge cases. Agents and skills cite these rules rather than restating them.

Rulebooks are grouped by kind, one directory per kind. `index-lint` derives each rulebook's `category` from its parent directory:

| Directory                                   | Holds                                                                                       | In `INDEX.yaml`? |
| ------------------------------------------- | ------------------------------------------------------------------------------------------- | ---------------- |
| [`conventions/`](../rulebooks/conventions/) | The prose conventions above, plus the four research **policies** (`research-*.md`)          | Yes              |
| [`templates/`](../rulebooks/templates/)     | Fill-in skeletons for artifacts — ADRs, and the ten `research-*.md` artifact templates      | Yes              |
| [`schemas/`](../rulebooks/schemas/)         | JSON-Schema data contracts (`research-*.schema.json`) the research validators check against | No — see below   |

The research feature adds files across all three, marked by a `research-` filename prefix rather than a per-feature subtree (see [ADR-0006](../../docs/adr/0006-research-flat-storage-and-validation-pipeline.md)). Two points are deliberate, not drift:

- The four **research policies** live under `conventions/`, so `index-lint` catalogs them with `category: conventions` even though their own frontmatter reads `category: policies` — a label describing their nature. There is no `policies/` directory.
- `schemas/` is a genuinely new category of rulebook: machine-readable data, not prose. Its `.schema.json` files are intentionally **absent** from `INDEX.yaml`, because `index-lint` scans Markdown frontmatter only. The validators resolve them by path, never by catalog name.

## Linting and gating

A gate is a deterministic script — no LLM judgement involved — that catches a provable defect before a reviewer agent spends time on it: a broken cross-reference, a missing required section, an inconsistent ID. Cheap, reproducible, no false positives.

| Gate                           | Fires at                 | What it checks                                                                                                                            |
| ------------------------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/spec-lint`    | Phase 1 → 2 boundary     | Specification coverage: traceability across PRD, actor-goals, `.feature` files, and supplementary specs; ID uniqueness; required sections |
| `factory/scripts/arch-lint`    | Phase 2 → 3 boundary     | arc42 chapters exist and cross-reference the Structurizr DSL, ADR index consistency, diagram file references                              |
| `factory/scripts/backlog-lint` | Phase 3 → 4 boundary     | YAML frontmatter schema, dependency graph acyclicity, priority and status values                                                          |
| `factory/scripts/matrix-lint`  | `config/model.conf` edit | Syntax, required fields, valid tier/model mappings                                                                                        |

In manual mode (driving each agent by hand, one session at a time), the reviewer agent for that phase runs its gate as its first step. Run any gate yourself the same way:

```bash
factory/scripts/spec-lint --spec-dir docs/spec/
factory/scripts/arch-lint --docs-dir docs/arc42
factory/scripts/backlog-lint --backlog-dir backlog/
factory/scripts/matrix-lint --matrix config/model.conf
```

These scripts are stdlib-only Python — no install needed to run them.

### Research artifact validation

The research workflow adds two more deterministic validators, stdlib-only in the same spirit but invoked on demand by the research skills and agents (and by you), not wired to a phase boundary. They implement the first two stages of a fixed three-stage validation order — **schema → policy → semantic** — that splits validation by whether a machine can decide it:

| Stage        | Tool                                | Checks                                                                                                              |
| ------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1 — schema   | `factory/scripts/schema-validate`   | One JSON artifact against one JSON Schema: required fields, types, enums, identifier patterns, timestamps           |
| 2 — policy   | `factory/scripts/policy-validate`   | The enforceable half of the research policies across artifacts: role separation, references, quorum, claim versions |
| 3 — semantic | a qualified human or agent reviewer | Evidence support, source independence, test severity, claim atomicity — the judgment no script makes                |

```bash
factory/scripts/schema-validate <artifact-file> <schema-file>
factory/scripts/policy-validate --pipeline <artifact-or-dir>...   # runs stage 1, then stage 2, stopping at the first failure
```

An artifact must pass stage 1, then stage 2, then stage 3 before the next playbook step begins. The schemas live in [`factory/rulebooks/schemas/`](../rulebooks/schemas/). See [ADR-0006](../../docs/adr/0006-research-flat-storage-and-validation-pipeline.md) and [`research-topic.md` § The Validation Gate](../playbooks/research-topic.md).

### Semantic quality gates

Three semantic gates fire between a developer's commit and merge, enforced by the gate-check loop in `feature-addition`:

| Gate              | Script                              | What it checks                                                                                                                                     |
| ----------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| CRAP score        | `factory/scripts/crap-score`        | Composite structural risk (cyclomatic complexity weighted against coverage). The gate threshold is on the composite score, not on coverage itself. |
| Mutation analysis | `factory/scripts/mutation-analysis` | Mutation testing — verifies that tests detect injected faults, not just that they run.                                                             |
| Dependency check  | `factory/scripts/dependency-check`  | Dependency vulnerability scan against known advisories.                                                                                            |

A project can override which gates apply at the story, house-rules, or factory-default level (resolved in that priority order). The gate-check loop allows a maximum of three fix iterations per tier and escalates to tier+1 on failure, with a ceiling of six total developer spawns per story.

### Step isolation

Per-step manifests at `.current-work/<feature-branch>/<story-branch>/current-step.yml` declare each step's inputs, outputs, and `max_input_tokens`. The `factory/scripts/step-guard` hook enforces these boundaries — an agent that reads a file not in its manifest or exceeds its token budget is blocked before the read completes.

### Mechanized dispatch

The `factory/scripts/dispatch` script owns the git state, ledger, and branch/worktree lifecycle for implementation. The LLM sequences script calls; the scripts own state transitions. The dispatcher maintains a machine-readable ledger at `.current-work/<feature-branch>/dispatch-ledger.yaml` tracking every story's preparation, dispatch, verification, and merge state. Key subcommands:

- `dispatch init` — initialize the dispatch ledger for a feature branch.
- `dispatch prepare-wave` / `dispatch prepare-story` — create story branches and worktrees, record the declared base SHA, and run `verify-base`.
- `dispatch verify-story <story-id> --sha <sha>` — confirm the reported commit object exists on the expected branch.
- `dispatch merge-story <story-id>` — run `premerge-check`, merge, and run post-merge tests.
- `dispatch close-wave <wave>` — append a closeout record with completed, blocked, and next-ready stories.

Every story in a wave must reach a terminal state (merged or explicitly blocked/failed) before the next wave launches. The tier rubric in [dispatch-contract.md](../rulebooks/conventions/dispatch-contract.md) is the single authoritative source for economy/standard/strong tier assignment.

### Pre-commit hooks

Agent Factory adds pre-commit hooks to `.pre-commit-config.yaml`. This is the one tracked file the install modifies (besides a `.gitignore` block). Every hook id starts with `agent_factory_hook-`, so the block is easy to find, easy to audit, and safe to remove.

The hooks fall into two groups. Formatters — `mdformat` for Markdown, `ruff` for Python — auto-fix style on commit. Gate scripts — `link-check`, `mermaid-lint`, `spec-lint`, `arch-lint`, `backlog-lint`, `statemachine-lint`, `index-lint`, `transition-lint` — reject a commit when a deterministic check fails.

#### Nothing is installed into your project

The formatters need external tools, but the hooks never install them into your project tree, your virtualenv, or your global Python packages. They run through `uvx`, which downloads an ephemeral, pinned copy into its own cache (`~/.cache/uv/` or `$UV_CACHE_DIR`) the first time and reuses it afterward. Your `site-packages`, your `node_modules`, your carefully curated tool versions: untouched.

If you already have `ruff` installed globally, `uvx` ignores it. It runs its own pinned version (`ruff@0.16.5` at the time of writing), so the hook produces the same result on every machine regardless of what each developer has installed. The same applies to `mdformat`. This is the same zero-local-install pattern `factory/scripts/structurizr` uses for its Docker dependency.

The gate scripts (`spec-lint`, `arch-lint`, `backlog-lint`, and the rest) are stdlib-only Python. They need nothing beyond the Python interpreter already on your PATH — no pip install, no requirements file, no build step.

#### Your teammates can commit without the factory

The `.pre-commit-config.yaml` is tracked, so everyone who clones the repo gets the hook definitions. But `factory/` itself is git-ignored — it exists only on machines where `init-factory` has run. A colleague who has never heard of Agent Factory does not have it.

Every hook that calls a `factory/scripts/*` gate is wrapped in a one-line bash guard:

```bash
bash -c '[ -d factory ] || exit 0; exec factory/scripts/<gate> "$@"' --
```

If `factory/` is not there, the hook exits 0 — a silent pass. Pre-commit moves on to the next hook. Your colleague commits normally, with no error, no warning, and no trace that Agent Factory was ever involved. The `mdformat` and `ruff` hooks carry the same guard, so even the formatters stay quiet when the factory directory is absent.

This is deliberate. The `.pre-commit-config.yaml` is tracked because it must survive clones and branch switches. The `factory/` directory is untracked because it is local tooling, not project source. The guard bridges the two: hooks exist in the config for anyone who has the factory, and vanish for anyone who does not.

#### Your existing hooks are preserved

If your project already has a `.pre-commit-config.yaml`, `init-factory` splices the `agent_factory_hook-` block in at the top of your `repos:` list. It does not rewrite, reorder, or touch your own hooks. `remove-factory` strips exactly that block — your hooks remain byte-for-byte as they were.

If you have no `.pre-commit-config.yaml`, `init-factory` creates one containing only the factory hooks.

#### First commit after setup

The `mdformat` and `ruff` hooks auto-fix formatting. If your first commit fails because "files were modified by this hook," that is the formatters doing their job on files that did not yet match the project style. Re-stage and commit again:

```bash
git add -u
git commit -m "<same message>"
```

This is a one-time cost per file. After that first pass, the hooks modify only files you change — and only their formatting, never their content.

## CLI safety guardrails

`init-factory` also installs a git-safety guardrail that blocks a fixed list of dangerous git invocations before they run. Claude Code, GitHub Copilot CLI, and Codex use the shared shell script through their native `PreToolUse` hook paths. Pi uses a project-local extension under `.pi/extensions/` that enforces the same deny list when loaded. Two groups:

- **Commands that discard or overwrite work or history**: `git push`, `git reset --hard`, `git clean -f`/`-fd`, `git branch -D`, `git checkout .`, `git restore .`, and bare `push --force` / `reset --hard` fragments anywhere in a longer command line.
- **Standalone branch creation**: `git branch <name>`, `git switch -c/-C`, and `git checkout -b/-B`. Every new branch is created atomically with its linked worktree via `git worktree add -b <branch> <path> <base>`, then verified with `git worktree list --porcelain`.
- **Commands that bypass this repo's own commit gates**: `--no-verify`, `git commit -n`, reassigning `core.hooksPath`, `pre-commit uninstall`, and `SKIP=...` environment overrides on `git commit` or `pre-commit`.

One script serves the three hook-based CLIs: it reads the shell command from
each runtime's supported `PreToolUse` JSON shape, and Claude Code, GitHub
Copilot CLI, and Codex treat exit code 2 as "deny."

The guardrail is installed automatically for every project — not opt-in, not a
skill you invoke by hand. `init-factory` symlinks the script into
`.claude/hooks/`, `.github/hooks/`, and `.codex/hooks/`, then wires each
runtime's hook configuration: `.claude/settings.json` for Claude Code,
`.github/hooks/block-dangerous-git.json` for Copilot CLI, and
`.codex/hooks.json` for Codex. For Pi, `init-factory` symlinks
`.pi/extensions/block-dangerous-git.ts` to the canonical Factory extension;
Pi auto-discovers it once the project is trusted. The generated local runtime
directories and only the Factory-owned GitHub entries are ignored; GitHub
Actions workflows remain untouched. This state is recreated by `init-factory`
in every clone.

**Pi caveat:** this is not as strong as the native Claude/Copilot hook path. Pi loads project-local extensions only after project trust resolves, and non-interactive runs may ignore them unless trust is already saved or the run is explicitly approved. For stronger Pi enforcement, install the same extension globally under `~/.pi/agent/extensions/`, pass it via `pi -e`, or run Pi in a sandbox/container. See Pi's own [Extensions](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/extensions.md), [Security](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/security.md), and [Containerization](https://github.com/earendil-works/pi-mono/blob/main/packages/coding-agent/docs/containerization.md) docs for the underlying model.

Treat it as a backstop, not a security boundary. It catches an accidental or under-pressure bypass — a background agent routing around a failing gate, for instance — not a determined one. A user with shell access outside the CLI, or anyone who edits the CLI's own configuration, can always route around it.

## Session logging

Session logging is an opt-in, append-only audit trail of gate-script runs. It exists to reconcile what an agent claims it did in a session against what actually happened on disk — not to replace or gate anything by default.

**Enable it.** Set the `AF_SESSION_LOG` environment variable to a log-file path before running gates. `factory/scripts/_session_log.py` reads it fresh on each run: unset, logging is a no-op and nothing is written; set, it appends one line per wrapped run to that path, creating the parent directory if needed.

**What gets recorded.** Each JSON Lines entry has: `ts` (UTC timestamp from the script's own process clock, not agent-supplied), `script` (the gate's name), `argv` (its invocation arguments), `exit_code`, and `files_changed` (a `git status --porcelain` diff taken before and after the run — the ground truth for what moved on disk). A `summary` field is added when the wrapped gate supplies one (`spec-lint` folds in its `--format json` error/warning/info counts).

**Current scope.** Only `spec-lint` is instrumented today. No other gate writes to the log yet.

**Reconcile.** `factory/scripts/session-reconcile` compares the log against real git state: `--log` points at the log file (default `.current-work/session-log.jsonl`), `--base`/`--head` bound the commit range to diff (omit `--base` to check the working tree alone). It reports three finding codes: `RECON-UNEXPLAINED` (error) — a working-tree change no logged run or commit accounts for; `RECON-DRIFT` (warning) — a run logged a change that is now neither committed nor present in the working tree; `RECON-STALE` (warning) — `docs/spec/` changed but `spec-lint` never ran this session. Exit code is the error-finding count, unless `--report-only`.

The log file lives under `.current-work/`, which is gitignored — local machine state, not portable, not meant to be reviewed.

See [docs/proposals/session-log-addendum.md](../../docs/proposals/session-log-addendum.md) for the full design rationale.

## Using this in an existing repo

`init-factory` works the same way against a repo that already has its own history, `.gitignore`, and `.pre-commit-config.yaml`. Run it from inside that repo:

```bash
cd /path/to/existing-project
/path/to/agent_factory/factory/scripts/init-factory
```

Two promises govern the whole install: it never disturbs what the project already owns, and everything it adds can be removed without a trace. Concretely, against an existing repo:

- **`.gitignore`** — adds a single marker-delimited block headed `agent_factory related`, listing exactly the footprint it introduces. It never rewrites or duplicates what's already there, and it preserves your file's exact bytes (down to a missing final newline). Under `.github/` it ignores the specific entries it adds, one by one — never the whole directory, so your `.github/workflows/` stay tracked.
- **`.pre-commit-config.yaml`** — the one tracked change. If the file doesn't exist, it's created carrying just Agent Factory's block. If it exists, `init-factory` hands off to `factory/scripts/merge-precommit-config`, which splices the `- repo: local` block — every hook id prefixed `agent_factory_hook-` — in at the top of your `repos:` list, leaving your own hooks untouched. An inert `.pre-commit-config.yml` is never touched; pre-commit only auto-reads `.yaml`.
- **Orientation files** — if you already have a `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, or root `AGENTS.md`, a marker-fenced orientation block is prepended to your file. For Claude Code it is a single `@`-include directive; for Copilot CLI, Pi, and Codex the full orientation content is inlined between markers. Your own content is preserved below the block, and `remove-factory` strips it on uninstall.
- **Everything else** — your `docs/`, your scripts, your configuration — is left alone. `init-factory` never touches a file or directory it didn't create.

The script is idempotent: run it again any time, and anything already correctly in place is skipped. It records what it did in `.agent-factory/factory-install.json`, and a re-run reads that manifest so it never loses track of what it owns. If it finds something it can't safely work around, it stops immediately and names the exact path — it never partially applies a run.

**Removing it again.** `factory/scripts/remove-factory` reverses the whole install from the manifest — deleting the git-ignored footprint, stripping the `agent_factory related` `.gitignore` block, stripping orientation blocks from existing orientation files, and removing the `agent_factory_hook-` pre-commit block while leaving your own hooks in place — back to a clean `git status`. A repo that had its own `.gitignore`, pre-commit config, orientation file, or workflows gets them all back byte-for-byte.

**Updating it again.** When your `agent_factory` checkout gets newer and you want the installed project to match, run `factory/scripts/update-factory`. It replaces the installed `factory/` with a fresh copy of the current checkout, then re-runs the *sourced* `init-factory` so every derived step comes up to date too — regenerated Codex adapters, re-verified symlinks, re-merged guardrail/usage hook wiring, and a re-run `pre-commit install`:

```bash
/path/to/agent_factory/factory/scripts/update-factory --target /path/to/existing-project \
    --source /path/to/agent_factory
```

`--source` is optional on installs created after the field was recorded: `init-factory` stores the checkout it copied from (`factory_source`) in `.agent-factory/factory-install.json`, and `update-factory` reads that as its default. Only `factory/` is replaced — the project's own files, the `.gitignore`/`.pre-commit-config.yaml` edits, and the `.agent-factory/` usage-tracking transcripts and lifecycle state are all preserved. You can also run the installed copy from inside the project with `--source` if you no longer have the original checkout path in the manifest.

If the sourced `init-factory` stops on a collision, `update-factory` rolls the refresh back: the old `factory/` is moved aside (not deleted) and restored in place, so the project is never left without a `factory/` and dangling runtime symlinks. Resolve the reported collision and re-run `update-factory` to finish.

To trigger the install conversationally instead of from a shell, use the `init-factory` skill (`factory/skills/init-factory/SKILL.md`): it confirms the target with you, runs the script, and relays its output.

## Troubleshooting

**`init-factory: STOPPED — <path> already exists and is not a symlink to <dest>`**
Something real is already at that path. Move, rename, or remove it, then re-run `init-factory`.

**`merge-precommit-config` reports it cannot merge your `.pre-commit-config.yaml`**
This happens when the file has no top-level `repos:` list in block style, or its existing hooks aren't indented at 2 spaces. Merge Agent Factory's hooks in by hand: copy the `- repo: local` block from `factory/config/pre-commit-config.yaml` into your file's `repos:` list.

**`uvx: command not found`**
Install `uv` — see [factory/README.md § Prerequisites](../README.md#prerequisites). Every gate, and `pre-commit` itself, runs through `uvx`.

**`docker info` fails, or diagram export fails**
Start Docker Desktop (macOS) or the Docker daemon (Linux). This only blocks `factory/scripts/structurizr` — nothing else needs Docker.

**Your first commit fails, or modifies files you didn't touch**
Expected — the `mdformat` and `ruff` hooks auto-fix formatting on commit. Re-stage and commit again:

```bash
git add -u
git commit -m "<same message>"
```

**`factory/` looks out of date after you update your `agent_factory` checkout**
`init-factory` only copies `factory/` in once. To bring an installed project up to date, run `factory/scripts/update-factory` (see “Updating it again” above) instead of re-running `init-factory`.

**Symlinks don't work on Windows**
Agent Factory targets macOS and Linux only. Both rely on native, git-tracked symlinks, which Windows doesn't support the same way.

## Referenced from

- [factory/README.md](../README.md)
- [docs/spec/prd.md § Problem Statement](../../docs/spec/prd.md#1-problem-statement)
