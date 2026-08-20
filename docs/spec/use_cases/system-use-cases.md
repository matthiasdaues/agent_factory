# System Use Cases — Factory Specification

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
- `run_agent` shall parse structured JSON from `--mode json` `message_end`, persist the complete result in canonical tracked artifacts, and return the bounded BR-040 envelope with token usage (UC-10, BR-034, BR-040).
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

## Phase boundary and context control

- When work crosses a Factory phase boundary, the outgoing session shall produce a `handoff-lint`-clean handoff and stop before the next phase begins (UC-11, BR-038, BR-039).
- The Factory-owned `handoff` skill shall preserve every decision, open item, artifact path, exact 40-character SHA, branch/upstream state, gate result, verification result, and next action while compressing prose (UC-11, BR-037).
- If a handoff has a mechanically observable structural defect, contains a malformed declared full SHA, omits a required declared field, or references a missing declared path, then `handoff-lint` shall exit non-zero and report every detected defect (UC-11, BR-038).
- When `handoff-lint` passes, a designated Handoff Semantic Reviewer shall compare the handoff with outgoing phase artifacts, decisions, open items, and evidence before confirming losslessness (UC-11, BR-049).
- If semantic review finds an omitted or distorted material fact, then phase closure shall remain blocked until correction, repeated lint, and repeated semantic review pass (UC-11, BR-049).
- When a fresh session begins a phase, it shall read the handoff first and then read referenced large artifacts in bounded, on-demand chunks (UC-11, BR-041).
- Before a child returns to a parent, it shall persist its complete result in canonical tracked report and finding artifacts (UC-11, BR-040).
- A child result injected into a parent transcript shall contain only disposition, finding counts by severity, every result-artifact path, and a one-to-three-sentence next action (UC-11, BR-040).
- When a session ends, usage capture shall identify eligible turns as chronological top-level assistant model-response turns belonging to that session, excluding tool events, progress events, child-session turns, and synthetic aggregate records (UC-11, BR-042).
- Where every eligible turn has provider-reported input and cache-read token values, usage capture shall classify a turn as a cache miss exactly when input is greater than zero and cache read equals zero (UC-11, BR-042).
- Where cache capability is complete, cache-miss turn count shall equal the number of cache-miss turns (UC-11, BR-042).
- Where cache capability is complete, cache-miss input-token total shall equal the sum of provider-reported input across cache-miss turns (UC-11, BR-042).
- Where per-turn input is complete and at least two eligible turns exist, usage capture shall let `k = max(1, floor(N / 3))`, define early as the first `k` turns and late as the last `k` turns, and calculate the ratio as late mean input divided by early mean input (UC-11, BR-042).
- If any eligible turn lacks input, then all three derived metrics shall be null (UC-11, BR-042).
- If every eligible turn has input but any lacks cache-read tokens, then both cache-miss metrics shall be null (UC-11, BR-042).
- Where there are fewer than two eligible turns or early mean input is zero, late-versus-early input ratio shall be null (UC-11, BR-042).
- Where no eligible turns exist, all three derived metrics shall be null (UC-11, BR-042).
- Where eligible turns have complete cache fields but none is a miss, both cache-miss metrics shall be numeric zero (UC-11, BR-042).
- Usage capture shall store CLI, provider, and capability class (`full-cache`, `input-only`, or `unavailable`) with the derived metrics (UC-11, BR-042).
- Derived cache signals shall be retrospective only (UC-11, BR-042).
- While a session is live, derived cache signals shall not interrupt, stop, or otherwise control it (UC-11, BR-042).

## Dispatch safeguard assurance

- The accepted dispatch audit shall map base preflight, declared base SHA, nested-agent addressing, pre-merge diff checking, unattended permissions, and scope/checkpoint discipline to shipped contract, implementation, and automated evidence (FR-L1, BR-043).
- Machine-consumed base declarations and dispatch records shall use exact 40-character Git SHAs (FR-L2, BR-044).
- Automated evidence shall exercise wrong and stale bases before work, stale/out-of-scope/file-count-blowout/target-reverting diffs, resolvable nested reply addressing, and unattended argv and deny-list construction (FR-L2, BR-045, BR-046, BR-047).
- Where a mechanism already has complete contract, implementation, and automated evidence, the audit shall not create reimplementation work for it (FR-L3, BR-048).

## Architecture model sync (`bausteinsicht sync`)

- When `bausteinsicht sync` runs, it shall perform a forward sync propagating structural changes from the JSONC model to the draw.io diagram (UC-13, BR-050).
- When `bausteinsicht sync` runs, it shall perform a reverse sync carrying label and description text from the draw.io diagram back to the JSONC model (UC-13, BR-051).
- Reverse sync shall not create, delete, or rename elements or relationships in the JSONC model (UC-13, BR-051).
- All Bausteinsicht operations shall run inside a Docker container via the wrapper script (UC-13, UC-14, UC-15, UC-16, BR-053).
- Where `architecture.drawio` does not exist when `sync` runs, Bausteinsicht shall create an initial draw.io file from the JSONC model (UC-13).
- Where Docker is unavailable, the wrapper shall report the condition and exit non-zero without modifying any files (UC-13).

## Architecture model validation (`bausteinsicht validate`, `bausteinsicht lint`)

- When `bausteinsicht validate` runs, it shall check the JSONC model's internal consistency (schema, referential integrity) and structural consistency with the draw.io diagram (UC-14, BR-056).
- When `bausteinsicht lint` runs, it shall check architectural constraints declared in the JSONC model's `constraints` array (UC-14, BR-056).
- If any validation or constraint check fails, then the wrapper shall report every violation in one run and exit non-zero (UC-14).
- When `arch-lint` runs and `architecture.jsonc` exists, `arch-lint` shall delegate model checks to `bausteinsicht validate` and `bausteinsicht lint` before running its own Factory-specific checks (UC-14, BR-059).

## Architecture image export (`bausteinsicht export`)

- When `bausteinsicht export-all` runs, it shall render every view in the JSONC model to both PNG and SVG in `docs/assets/images/` (UC-15, BR-057).
- When `bausteinsicht export-png` or `export-svg` runs, it shall render to the single requested format only (UC-15).
- If a view references elements that do not exist in the model, then the wrapper shall report the broken reference and exit non-zero (UC-15).

## Architecture migration (`bausteinsicht import`)

- When `bausteinsicht import` runs, it shall read the specified Structurizr DSL file and produce `architecture.jsonc` and `architecture.drawio` (UC-16, BR-058).
- If `architecture.jsonc` already exists at the target path, then `import` shall refuse and exit non-zero without writing any files (UC-16).
- If the DSL file has syntax errors, then `import` shall report the errors and exit non-zero without writing any files (UC-16).
- `import` shall not delete the source `.dsl` file; deletion is a manual actor step after verification (UC-16, BR-058).

## Architecture pre-commit validation

- The architecture pre-commit hook shall fire only when `.jsonc` or `.drawio` files appear in the staging area (UC-17, BR-055).
- If `architecture.jsonc` is staged without `architecture.drawio`, or vice versa, then the hook shall reject the commit and name the missing file (UC-17, BR-054).
- When both files are co-staged, the hook shall run `bausteinsicht validate` and reject the commit if validation fails (UC-17, BR-056).
- Where no `.jsonc` or `.drawio` files are staged, the architecture hook shall be a no-op (UC-17, BR-055).

## Architecture structural change summary (`bausteinsicht diff`)

- When `bausteinsicht diff` runs, it shall produce a human-readable structural change summary suitable for PR descriptions (SF-04).

## Referenced from

- [actor-goal-list.md](../actor-goal-list.md)
- [supplementary_specs/interface-contracts.md](../supplementary_specs/interface-contracts.md)
