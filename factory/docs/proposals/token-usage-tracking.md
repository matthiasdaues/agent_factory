# Feature Request: Token Usage Tracking

## Summary

Add runtime token-usage tracking to Agent Factory. Every agent run — whether a
human started the session or the orchestrator dispatched it — appends one record
of what that run actually consumed. The record measures spend with a single,
CLI- and model-independent tokenizer so that runs are directly comparable across
CLIs and across models. The release captures and persists these records;
it does not read, aggregate, or present them.

A captured record answers a question the factory cannot answer today: *what did
this run actually cost, and how does that compare to the same work under a
different CLI or model?*

## Motivation

The factory already counts tokens **statically**: `INDEX.yaml` carries the
`tiktoken cl100k_base` size of each agent, skill, and rulebook prompt, computed
by `index-lint`, for context-window planning. It has no record of **runtime
actuals** — how many tokens a real run burned. Live counters exist inside each
CLI, but they are thrown away when the run ends, and each CLI reports them
differently (Pi exposes a full input/output/cache breakdown in `message_end`;
Claude Code's Agent tool returns only an aggregate `subagent_tokens`). Parallel
sub-agent dispatch, where spend concentrates, is entirely invisible after the
fact.

Two needs follow:

1. **Observability of real spend**, attributed to the unit of work (agent,
   phase, playbook, story, and — critically — create-review loop and iteration).
2. **Comparability** across CLIs and models, on one yardstick, so a Haiku run
   under Pi and a Sonnet run under Claude Code can be measured against each
   other.

Budget *enforcement* — blocking a run that exceeds a ceiling — is a natural
later layer built on this data. It is out of scope here. You cannot enforce a
budget you do not first measure.

## Core Principles

- **Normalized measurement, not provider accounting.** The comparable metric is
  produced by tokenizing the run's own text with one fixed method, independent
  of whatever the CLI reports. Provider-reported numbers are kept alongside, but
  only for real-cost reconciliation, never for comparison.
- **Capture is local and free.** Tokenizing is a deterministic operation in a
  plain script — it never sends text to a model, so it adds no LLM spend. It
  runs after a run completes, over the transcript already written to disk.
- **Capture never breaks a run.** The capture path is best-effort. A failure to
  record must not fail, block, or slow the work it measures.
- **Factory-owned and CLI-agnostic.** Because human-started and
  orchestrator-started sessions alike must be captured, capture cannot live in
  the orchestrator. It is a factory asset that every CLI can invoke.

## The Usage Record

One record is emitted per agent invocation (one LLM session). Fields, grouped:

**Correlation**

| Field                  | Meaning                                                      |
| ---------------------- | ------------------------------------------------------------ |
| `cli`                  | `claude-code \| copilot \| codex \| pi`                      |
| `session_id`           | the CLI session's identifier                                 |
| `parent_session_id`    | parent run, for building the sub-agent spend tree (nullable) |
| `depth`                | nesting depth (`PI_RUN_AGENT_DEPTH`)                         |
| `run_start`, `run_end` | ISO-8601 bounds; duration is derivable                       |

**Loop**

| Field       | Meaning                                                                          |
| ----------- | -------------------------------------------------------------------------------- |
| `loop_id`   | groups every run — create plus each review iteration — for one target (nullable) |
| `loop_role` | `create \| review \| null` (null = one-shot, not in a loop)                      |
| `iteration` | pass number through the loop (nullable)                                          |

Assigned by the orchestrator from the phase-gate and findings state. Aligns with
the `review-loop-discipline` convention. Answers "what did the create-review
loop for X cost across all its iterations."

**What ran**

| Field               | Meaning                                                                                                         |
| ------------------- | --------------------------------------------------------------------------------------------------------------- |
| `agent`             | agent / persona name                                                                                            |
| `skill`             | skill(s) the session ran — a context field, nullable; tokens are attributed to the session, not split per skill |
| `phase`, `playbook` | workflow position (nullable)                                                                                    |
| `story_id`          | unit of work (e.g. `ST-0018`)                                                                                   |
| `model`             | resolved model id                                                                                               |

**Spend**

| Field                                                                              | Meaning                                                                     |
| ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `normalized_input`, `normalized_output`, `normalized_total`                        | our tokenizer over the run text — **the comparable metric**; always present |
| `reported_input`, `reported_output`, `reported_cache_read`, `reported_cache_write` | provider-reported; nullable; for real-cost reconciliation only              |
| `usage_granularity`                                                                | `full \| aggregate` — whether the reported breakdown is trustworthy         |

**Outcome**

| Field                      | Meaning                                                                                       |
| -------------------------- | --------------------------------------------------------------------------------------------- |
| `exit_status`              | did we pay for a failed run                                                                   |
| `branch`                   | work branch                                                                                   |
| `base_commit`, `commit_id` | `git diff base_commit..commit_id` reconstructs **what was written** (nullable when no commit) |
| `transcript_ref`           | `{ path, span? }` — link to **what happened** (reasoning and tool trace)                      |

The record stores integers and references, never text: the git diff stays in
git, and the transcript is persisted separately and linked.

## Tokenization Strategy

- **One fixed tokenizer: `tiktoken cl100k_base`** — chosen not for
  Anthropic-accuracy (it is GPT's) but as a neutral, fixed yardstick, and
  because `INDEX.yaml`'s static counts already use it. Reusing it makes static
  estimate and runtime actual comparable on the same scale.
- **Full-transcript scope.** The tokenizer measures the entire run — system
  prompt, every turn, tool inputs and outputs, thinking — not just the boundary
  prompt and final output. The intermediate tool-result mass is exactly where
  spend varies between CLIs and runs; measuring only the tips would under-count
  badly and unevenly.
- **One transcript read yields both counts.** Parsing a transcript gives the
  text to tokenize (`normalized_*`) and, where the transcript records per-message
  `usage` (Claude Code's `.jsonl` does), the provider breakdown (`reported_*`)
  at `full` granularity. The Agent tool's aggregate `subagent_tokens` is not
  needed when the transcript file is available.

## Persistence

- **Append-only JSONL**, one record per line, at
  `.agent-factory/usage/<session_id>.jsonl`, **git-ignored** (runtime telemetry:
  append-only, unbounded, and noise in history). POSIX `O_APPEND` makes
  concurrent appends atomic, so parallel dispatch — many sub-agents writing at
  once — is safe with no locking.
- **The tokenized transcript is persisted** as a copy under
  `.agent-factory/usage/transcripts/<session_id>/<record_id>.jsonl`, and
  `transcript_ref` points at it. This keeps the audit link from dangling when a
  CLI cleans up its own scratch transcript. Storage is local, ignored, and
  prunable by session.
- **Behind a logging-adapter seam.** Capture sites hand a record to an adapter;
  the JSONL adapter appends the line and persists the transcript copy. A future
  PostgreSQL adapter, served by a dedicated logging service, replaces the JSONL
  adapter in one place without touching any capture site.

## The Capture Tool

A single, factory-owned, standalone Python script:
`factory/scripts/usage-capture` — self-bootstrapping via a PEP 723 shebang
(`tiktoken`), in the style of `index-lint` and `schema-validate`. Every capture
site invokes it uniformly:

```
usage-capture --cli pi --transcript <path> --session <id> --agent <name> \
              --model <m> --loop-role review --iteration 2 --commit <sha> ...
```

It has two swappable internal seams around a fixed tokenizer:

1. **Transcript normalizer** (per CLI) — parses that CLI's transcript into one
   plain text stream: Pi's JSON events, Claude Code's `.jsonl`, later Copilot's.
2. **Logging adapter** (per backend) — JSONL now, PostgreSQL later.

A standalone script, rather than an orchestrator module, is the lower-friction
seam: capture sites are polyglot (Pi extensions are TypeScript and already shell
out to `resolve-model` this way; the orchestrator is Python; a Copilot hook is
something else again), so one CLI-invokable entrypoint gives every caller one
uniform way in. The orchestrator may still `import` the underlying module for
in-process use.

## Capture Triggers, per CLI

The script is uniform; the trigger is necessarily CLI-specific. Each hands
`usage-capture` a transcript path and context.

| CLI                | Human-started session                      | Sub-agent / dispatched                       |
| ------------------ | ------------------------------------------ | -------------------------------------------- |
| Claude Code        | `Stop` hook (settings.json)                | `SubagentStop` hook                          |
| GitHub Copilot CLI | `agentStop` hook (`.github/hooks`)         | `subagentStop` hook                          |
| Codex              | `Stop` hook (`.codex/hooks.json`)          | `SubagentStop` hook                          |
| Pi                 | session-end / `message_end` extension hook | `run_agent` / `dispatch_wave` call it inline |

Both hook kinds receive the transcript path and session id, so both human and
dispatched sessions are covered within a CLI.

Copilot accounting is inclusive at the root. The parent `agentStop` transcript
contains child activity, so its normalized and reported totals include that
activity. `subagentStop` records provide attribution drill-down; an aggregator
must use root records for total spend and must not add child records again. The
built-in `general-purpose` agent emits no `subagentStop`, but its spend is still
captured inside the inclusive parent record.

**Rollout order:** Claude Code `Stop` + `SubagentStop` established the shared
capture core and first adapter. Complete the remaining supported CLIs in this
priority order: GitHub Copilot CLI, Codex, then Pi. The script remains
CLI-agnostic: each rollout adds a normalizer and native trigger, not a rewrite.
The orchestrator is a launch path, not a fifth transcript format; the CLI it
launches owns capture so the orchestrator must not create duplicate records.

## Scope

**In the release:**

- The `usage-capture` script: normalizer interface, normalizers for Claude
  Code, GitHub Copilot CLI, Codex, and Pi,
  `cl100k_base` tokenizer, JSONL logging adapter, transcript persistence.
- The full usage record as specified.
- Native human-session and sub-agent capture wired up for all four supported
  CLIs.

**Explicitly deferred:**

- Reading, aggregation, and presentation of the data — no reporter ships yet.
- Dollar-cost math (a later layer over `reported_*` × `model` × a rate table).
- The PostgreSQL adapter and its logging service.
- Budget enforcement.

## Design Details

- **`record_id`** uniquely identifies a record and names its transcript copy;
  derived from `session_id` plus a per-session sequence (or a UUID).
- **Retention** of transcripts is manual and per-session for now; pruning
  policy is deferred with the rest of the read side.
- **Failure is silent to the run:** capture errors are logged to stderr and
  swallowed; the measured run is never affected.

## Open Questions

- Confirm the exact `record_id` scheme (session-sequence vs. UUID).
- Confirm the exact Pi human-session event that provides the completed
  transcript or event stream without double-counting agent output.
- ~~Confirm the `.agent-factory/usage/` path against the existing init-factory
  ignore manifest~~ — resolved (ST-0040): it already falls under the existing
  `/.agent-factory/` line, no new ignore entry needed.

## Completion Criteria

The release is complete when:

- `factory/scripts/usage-capture` exists and, given a transcript and context,
  writes a well-formed record to `.agent-factory/usage/<session_id>.jsonl` and
  persists the linked transcript copy.
- Records carry `normalized_*` counts produced by `cl100k_base` over the full
  transcript, with `reported_*` populated where the transcript provides it.
- Claude Code, GitHub Copilot CLI, Codex, and Pi sessions — human and sub-agent
  or dispatched — are captured automatically through their native lifecycle
  surfaces.
- Each CLI has an end-to-end test proving the installed trigger produces the
  same canonical record and transcript-copy contract.
- Capture never fails, blocks, or slows the run it measures.
- The path is git-ignored and concurrent appends from parallel dispatch do not
  corrupt the file.

## Guiding Rule

Measure every run on one honest, neutral yardstick — the same method regardless
of CLI or model — and never let the act of measuring change what is measured.
