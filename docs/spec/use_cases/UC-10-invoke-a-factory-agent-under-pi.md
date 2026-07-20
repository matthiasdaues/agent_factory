# UC-10 — Invoke a Factory Agent Under Pi (`run_agent`)

Realizes: AG-10

## Primary Actor

CLI-Invoked Agent — a conversational Pi session, acting for the Human Operator.

## Stakeholders & Interests

- **Human Operator** — wants to run a factory agent from a Pi conversation and receive its result, without Pi's lack of a subagent concept collapsing the agent into in-context role-play in the current session.
- **CLI-Invoked Agent (caller)** — wants to call one named, schema'd tool and get the subagent's result back as data, without composing a subprocess invocation or managing its lifecycle.
- **Pi Subagent Session (spawned)** — wants the agent persona, project orientation, skills, and the git-safety guardrail all loaded, in a fresh context that never saw the caller's reasoning, so author/reviewer independence holds.

## Trigger

The calling Pi session invokes the model-callable tool `run_agent(agent, task, model?)`, registered by the project-local extension `.pi/extensions/run-agent.ts`.

## Preconditions

- Pi has trusted the project and loaded `.pi/extensions/run-agent.ts`.
- `factory/agents/<agent>.md` exists.
- `config/model.conf` declares a model for the agent's tier under the `pi` CLI, or `on_missing` permits proceeding without one.
- `pi` is on `PATH`.

## Main Success Scenario

1. The caller invokes `run_agent` with an `agent` name and a `task` string.
2. The extension resolves `factory/agents/<agent>.md`.
3. The extension resolves the model: the `model` argument if given, else `config/model.conf` `pi.<agent-tier>` (the tier read from the agent's own frontmatter), honoring `on_missing`.
4. The extension spawns a separate `pi` subprocess in the project directory — ephemeral (`--no-session`), project trust granted (`-a`), JSON event stream (`--mode json`), the resolved `--model`, the agent file appended as the system prompt (`--append-system-prompt`), and the `task` as the single prompt (`-p`).
5. The child loads the project `AGENTS.md`, the factory skills, and the guardrail extension — a full factory citizen in a context that never received the caller's conversation.
6. The child runs to completion; the extension reads its `message_end` event, extracts the final text and token usage, and returns them as the tool result.

## Extensions

- **2a. The named agent does not exist**
  - 2a1. The tool returns an error result naming the missing `factory/agents/<agent>.md`; no subprocess spawns.
- **3a. No model is configured for `pi.<tier>` and `on_missing: halt`**
  - 3a1. The tool returns an error result reporting the unresolved tier; no subprocess spawns.
- **4a. The spawn would exceed the recursion depth bound**
  - 4a1. The extension reads the spawn-depth environment variable it sets on each child; beyond the fixed bound it refuses to spawn and returns an error, so a child cannot fan out unbounded nested subagents (BR-035).
- **6a. The child exits non-zero or emits no `message_end`**
  - 6a1. The tool returns an error result carrying the child's exit code and the tail of its stderr, never a silent empty string.

## Postconditions

- **Success Guarantee**: the caller receives the subagent's final text and token usage from a `pi` session that never received the caller's conversation; the child saved no session state.
- **Minimal Guarantee**: on any resolution, recursion, or spawn error, no partial session is left running and the tool returns a diagnostic result.

## Business Rules

- **BR-030**: `run_agent` always spawns a fresh `pi` subprocess, never in-context role-play, because author/reviewer independence requires the reviewer never see the author's reasoning.
- **BR-031**: the child is granted project trust per spawn with `-a`, for determinism, rather than relying on saved trust in `~/.pi/agent/trust.json`.
- **BR-032**: the child layers the agent persona with `--append-system-prompt`, not `--system-prompt`, keeping Pi's own tool guidance and the project `AGENTS.md`.
- **BR-033**: the child inherits the git-safety guardrail, since it loads `.pi/extensions/`; subagents are bound by the same dangerous-command block and the single sanctioned `factory/scripts/run-tests --staged` allow.
- **BR-034**: `run_agent` returns structured JSON parsed from `--mode json` `message_end`, exposing token usage and tool-call detail, not only final text.
- **BR-035**: a fixed recursion-depth bound caps nested `run_agent` spawns; the parent records depth in an environment variable the child reads.

## Activity Diagram

```mermaid
flowchart TD
    A[run_agent(agent, task, model?)] --> B{agent file exists?}
    B -->|no| C[Error result, no spawn]
    B -->|yes| D[Resolve model: arg > pi.tier > on_missing]
    D --> E{model resolved or on_missing permits?}
    E -->|no, halt| F[Error result, no spawn]
    E -->|yes| G{depth within bound?}
    G -->|no| H[Error result, no spawn — BR-035]
    G -->|yes| I[Spawn pi --no-session -a --mode json --model m --append-system-prompt agent -p task]
    I --> J{child exits 0 with message_end?}
    J -->|no| K[Error result: exit code + stderr tail]
    J -->|yes| L[Return final text + token usage]
```

## Acceptance Criteria

```gherkin
Feature: Invoke a factory agent under Pi via run_agent

  Scenario: A known agent runs in a separate session and returns its result
    Given ".pi/extensions/run-agent.ts" is loaded in a trusted project
    And "spec-review-agent" exists in factory/agents/
    And config/model.conf declares a model for its tier under pi
    When the caller invokes run_agent with agent "spec-review-agent" and a task
    Then a separate pi subprocess runs the agent persona over the task
    And the child session never received the caller's conversation
    And run_agent returns the child's final text and token usage

  Scenario: An unknown agent is rejected before any subprocess spawns
    When the caller invokes run_agent with agent "does-not-exist"
    Then run_agent returns an error naming the missing agent file
    And no subprocess is launched

  Scenario: No configured model halts before spawning
    Given config/model.conf has no model for the agent's tier under pi
    And on_missing is halt
    When the caller invokes run_agent for that agent with no model argument
    Then run_agent returns an error reporting the unresolved tier
    And no subprocess is launched

  Scenario: The recursion depth bound stops runaway nesting
    Given the spawn-depth environment variable is already at the bound
    When a child invokes run_agent again
    Then run_agent refuses to spawn and returns a depth-bound error

  Scenario: The spawned child is bound by the git-safety guardrail
    Given a spawned agent session under -a
    When it attempts "git push"
    Then the guardrail blocks the command
    And "factory/scripts/run-tests --staged" is still permitted
```

## Referenced from

- [actor-goal-list.md](../actor-goal-list.md)
- [factory/config/extensions/run-agent.ts](../../../factory/config/extensions/run-agent.ts)
- [supplementary_specs/interface-contracts.md](../supplementary_specs/interface-contracts.md)
- [factory/docs/proposals/pi-invocation-layer.md](../../../factory/docs/proposals/pi-invocation-layer.md)
