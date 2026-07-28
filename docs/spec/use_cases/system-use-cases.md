# System Use Cases — Factory Flow Control

Technical requirements at the system's interfaces, expressed in **EARS** syntax (Ubiquitous / When / While / If-Then / Where). Each requirement is atomic. Requirements reference the persona use cases (UC-##) and business rules (BR-###) they derive from.

## Marker

- The marker shall live at `.agent-factory/playbook-state.yml`, git-ignored (UC-01, UC-02, UC-03, UC-05).
- Where the marker is absent, `transition-lint` shall treat the commit as ungoverned and exit `0` (UC-02, BR-001).
- Where the marker is absent, `phase advance` shall bootstrap it at the target playbook's root state (UC-01).
- The marker schema shall include `playbook`, `state`, `gate`, `result`, `open_findings`, `next`, `iteration`, `recorded_by`, and `recorded_at` (UC-01, [entity-model.md](../supplementary_specs/entity-model.md)).
- `recorded_at` shall be taken from the writing script's own process clock, never from an actor-supplied value (UC-01, BR-006).

## Phase-ordering gate (`transition-lint`)

- When a commit is staged, `transition-lint` shall map every staged file to the state whose `outputs:` glob matches it (UC-02).
- If a staged file's owning state differs from the marker's current state, then `transition-lint` shall report an error and cause the commit to fail (UC-02, BR-002).
- `transition-lint` shall not evaluate a state's `entry_conditions` (UC-02, BR-003).
- Where a staged file matches no state's `outputs:` glob, `transition-lint` shall treat it as ungoverned and not report a finding for it (UC-02).

## Phase advance (`phase advance`)

- When `phase advance` runs, it shall resolve the current state's forward transition from the playbook's `.fsm.yml` (UC-01).
- If the target state's `entry_conditions` are unmet, then `phase advance` shall refuse to advance and leave the marker unchanged (UC-01, BR-004).
- When `phase advance` succeeds, it shall reset the new state's `iteration` to `1` (UC-01, BR-005).
- Where a transition is conditional (`if`/`else`), `phase advance` shall treat the `if` branch as the sole forward path (UC-01, BR-007).

## Iteration cap (`phase retry`)

- When `phase retry` runs, it shall resolve the iteration limit against the loop-back target named in the current state's `else` transition (UC-03, BR-008).
- Where the FSM declares no `halt_conditions` entry for that state, `phase retry` shall apply `--default-max-iterations` (UC-03, BR-009).
- If the incremented iteration count exceeds the resolved limit, then `phase retry` shall refuse and leave the marker's iteration unchanged (UC-03, BR-010).
- When a retry is allowed, `phase retry` shall write the new iteration count and a fresh `recorded_at` (UC-03).

## Dispatch (`trigger`)

- When `trigger` resolves a target, it shall read agent and playbook data from `factory/INDEX.yaml`'s own source, not a separately maintained copy (UC-04).
- The background-mode permission allowlist shall never include `--dangerously-skip-permissions` or `--allow-all-tools` (UC-04, BR-011).
- The background-mode permission allowlist shall never include a bare interpreter wildcard (UC-04, BR-011).
- Where `--interactive` is given, `trigger` shall print the composed prompt rather than pass it programmatically to the launched session (UC-04, BR-013).
- When resolving one playbook step, `trigger` shall resolve it by agent name if given a name, or by 1-based index otherwise (UC-04, BR-014).
- If the named agent or playbook cannot be resolved, then `trigger` shall exit `2` without launching a subprocess (UC-04).

## Catalog generation (`index-lint`)

- `factory/INDEX.yaml` shall be generated exclusively by `index-lint`, never edited by hand (UC-06, BR-015).
- `index-lint` shall scan `agents/*.md`, `skills/*/SKILL.md`, `playbooks/*.md`, and `rulebooks/**/*.md` (excluding templates), computing `tokens` per entry and `total_tokens` for agents and playbooks (UC-06, FR-E1).
- When `index-lint` derives a playbook's agent sequence, it shall read the playbook's own `**Agent**: `x\`\` prose lines, not a separately maintained list (UC-06, BR-015).
- Where `--check` is given and the generated content differs from disk, `index-lint` shall exit `1` without writing (UC-06, BR-016).
- Where the generated content matches what is already on disk, `index-lint` shall write nothing (UC-06, BR-016).

## Resume decision (`run-step`)

- When a playbook has a companion `.fsm.yml`, `run-step` shall resolve the current agent from that state's `agent:` field (UC-05, BR-017).
- Where a playbook has no companion `.fsm.yml`, `run-step` shall resolve the current agent from `factory/INDEX.yaml`'s derived `agents:` list, in order (UC-05).
- If a state's declared outputs exist and its gate reports open findings, then `run-step` shall call `phase retry` before re-dispatching the same agent (UC-05, UC-03).
- If a state's declared outputs exist and its gate errors rather than reporting findings, then `run-step` shall stop and escalate to the actor (UC-05, BR-018).
- If a state's declared outputs exist, its gate passes clean, and no open findings remain, then `run-step` shall call `phase advance` (UC-05, UC-01).

## Guardrail hook (`block-dangerous-git.sh`)

- When a `PreToolUse` hook fires for a shell command, `block-dangerous-git.sh` shall read the command from either supported CLI's own JSON shape (UC-07, BR-019).
- If the command matches a pattern in the fixed dangerous-pattern list, then `block-dangerous-git.sh` shall exit `2` and report the matched pattern (UC-07, BR-019).
- Where the command matches no pattern in the list, `block-dangerous-git.sh` shall exit `0` (UC-07).

## Pi agent invocation (`run_agent`)

- When the caller invokes `run_agent`, the extension shall spawn a fresh `pi` subprocess and never role-play the agent in the caller's own session (UC-10, BR-030).
- The spawned child shall be granted project trust per spawn with `-a` (UC-10, BR-031).
- The spawned child shall receive the agent persona via `--append-system-prompt`, preserving Pi's own tool guidance and the project `AGENTS.md` (UC-10, BR-032).
- Where the child loads `.pi/extensions/`, the git-safety guardrail shall bind the child as it binds the parent (UC-10, BR-033).
- `run_agent` shall return structured JSON parsed from `--mode json` `message_end`, carrying final text and token usage (UC-10, BR-034).
- If the spawn depth recorded in `PI_RUN_AGENT_DEPTH` is at the bound, then `run_agent` shall refuse to spawn and return a depth-bound error (UC-10, BR-035).
- If the named agent file is absent, or no model resolves for `pi.<tier>` under `on_missing: halt`, then `run_agent` shall return an error result and launch no subprocess (UC-10).

## Installation (`init-factory`)

- When `init-factory` finds an unexpected file at a destination path, it shall stop the entire run before any later step executes (UC-08, BR-021).
- `init-factory` shall never modify `config/model.conf` once it exists at the target (UC-08, BR-022).
- Where `--target/factory` already exists, `init-factory` shall skip the copy step entirely (UC-08).
- Re-running `init-factory` against an already-initialized target shall report every step as already satisfied (UC-08).

## Usage capture attribution

- When capture receives an explicit model identifier from its invocation context, it shall persist that identifier (BR-036).
- Otherwise, where the CLI transcript exposes model identifiers, capture shall persist the latest non-empty identifier from that CLI's native model event (BR-036).
- Automated contract tests shall exercise model attribution for every CLI in the capture registry—Claude Code, GitHub Copilot CLI, Codex, and Pi (BR-036).
- The model-attribution fixture set shall equal the capture registry, so adding a supported CLI without a model-bearing fixture fails the contract test (BR-036).
- Where neither invocation context nor the transcript exposes a model identifier, `model` may remain null (BR-036).

## Referenced from

- [actor-goal-list.md](../actor-goal-list.md)
- [supplementary_specs/interface-contracts.md](../supplementary_specs/interface-contracts.md)
