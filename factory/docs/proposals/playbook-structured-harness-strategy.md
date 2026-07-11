# Structured Playbooks as a Deterministic Harness

**Status: proposal, not yet adopted.** This memo argues a direction and recommends a first step. It decides nothing.

## Problem

Today's playbooks in [`factory/playbooks/`](../../playbooks/) are prose runbooks. A human reads one, opens an AI-CLI session per step, and drives the phase chain by hand: requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa. The deterministic gates ([`spec-lint`](../../scripts/spec-lint), [`arch-lint`](../../scripts/arch-lint), [`backlog-lint`](../../scripts/backlog-lint)) run as pre-commit hooks and check whether an artifact is *valid*. None of them knows *which phase the run is in*, so none can catch an out-of-order move — architecture artifacts committed before the spec gate has passed, for example. Ordering is enforced only by the human following the prose. This memo asks how a structured playbook could close that gap without depending on an external orchestrator, for a human driving one session at a time.

The precedent already exists: [`greenfield-development.fsm.yml`](../../playbooks/greenfield-development.fsm.yml) declares states, gate conditions, and legal transitions in YAML. It is descriptive today — nothing reads it at commit time. The proposal is to make one such file *authoritative* and let a hook enforce it.

## 1. State-transition control via pre-commit

The missing piece is a single fact: **what state is this run in right now?** A hook cannot enforce ordering without it, and a human driving by hand needs it recorded somewhere durable, not held in an orchestrator's memory.

Proposal: commit a tiny **run-state marker** to the repo — one file, `docs/.playbook-state.yml`, holding the active playbook and the current state:

```yaml
playbook: greenfield-development
state: PHASE_1_GATE
```

A new pre-commit hook, `transition-lint`, then does four things:

1. Read the structured playbook and the marker to learn the current state and its legal successors.
2. Map each staged file to the state that declares it under `outputs:` (the globs already in the `.fsm.yml`).
3. If a staged file belongs to a state that is neither the current state nor a legal, entry-condition-satisfied successor, **block the commit** and name the offending path and the state it belongs to.
4. Advancing the marker is itself a commit, so the same hook validates that the transition it records is legal.

The human advances the marker with a one-line command — `factory/scripts/phase advance` — or the phase's reviewer agent writes it as its final workflow step. Either way the enforcement lives in the hook, which fires on every `git commit` regardless of who or what triggered it. No daemon, no orchestrator, no running process. This is exactly the property the task requires: it works for a human at a keyboard.

The existing gates stay as they are. `transition-lint` governs *ordering between* phases; `spec-lint` and friends govern *validity within* one. They compose.

Note on notation: [state-machine-notation.md](../../rulebooks/conventions/state-machine-notation.md) governs state machines embedded in specification prose (pseudocode as source of truth, Mermaid derived, enforced by `statemachine-lint` over `docs/spec/`). A playbook is a different artifact class — workflow orchestration, not spec content — and follows the YAML shape the `.fsm.yml` already set. The two conventions do not collide. A derived Mermaid view of the playbook is worth generating for human readers, but it is a nicety, not the source of truth.

## 2. Parseable handover artifacts

Today a phase hands off through free prose — spec-review-agent's [`## Handoff`](../../agents/spec-review-agent.md) section reads *"Spec review found N open findings. Address them."* A hook cannot parse that.

**Position: do not invent a parallel handover format, and do not overload findings frontmatter to carry it either.** The [finding-format.md frontmatter contract](../../rulebooks/conventions/finding-format.md#frontmatter-schema) already records the one machine-readable fact that decides a review phase's exit: how many findings are open. That contract stays the authority on defects. What it does *not* record is the run's position — which phase, which gate result, what comes next — and it should not, because a finding is about an *artifact*, not about a *run*.

So the handover artifact is the **run-state marker from section 1**, extended with a few fields the reviewer agent fills as its last step:

```yaml
playbook: greenfield-development
state: PHASE_1_GATE
gate: spec-lint
result: pass          # pass | fail
open_findings: 0      # derived by counting docs/findings/SPEC-*.md with status: open
next: PHASE_2_ARCHITECTURE
recorded_by: spec-review-agent
recorded_at: 2026-07-11
```

`open_findings` is *derived from* the existing findings files, never a second copy of them — the marker points at the findings mechanism, it does not replace it. This keeps one source of truth per fact: defects live in `docs/findings/`, run position lives in the marker.

The prose `## Handoff` sentence stays. It is for the human, and conversation is not the enemy — the structured record is a small byproduct the agent emits alongside its prose, not a replacement for it. A pre-commit routine (or a future harness) reads the marker; a person reads the sentence.

One unified marker beats one handover file per phase: fewer files, one schema to lint, and the run's whole history is a clean diff on a single path.

## 3. What changes, and the smallest first step

For **authors**, a playbook gains an enforced contract but keeps its shape. The `.fsm.yml` already carries `states`, `outputs`, `entry_conditions`, and `on`/`transitions`; the only genuinely new authoring is keeping `outputs:` globs honest, since the hook maps staged files through them. For **users**, one new habit: advance the marker (one command) at each phase boundary. The prose playbook stays readable and hand-drivable; nothing forces a user to adopt the machinery to keep working as they do today.

**Smallest viable first step:** do not convert all playbooks and do not write a new one. Make the *existing* [`greenfield-development.fsm.yml`](../../playbooks/greenfield-development.fsm.yml) enforcing, wired to a `transition-lint` hook that checks exactly one rule — architecture artifacts may not be committed while the spec gate is unpassed. Add the marker file and the `phase advance` command. Run one real greenfield pass by hand. If that single guardrail fires correctly and the marker stays out of the way, extend to the remaining transitions, then to other playbooks. If it proves fussy, we have spent one hook and one small file, not a rewrite of every runbook.

## Alternatives weighed

| Concern              | Recommended                                                            | Alternative                                           | Why recommended wins                                                                                       |
| -------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Ordering enforcement | YAML states + committed marker + `transition-lint` hook                | Convention only — human tracks phase in session notes | Convention-only cannot *block* an illegal commit; blocking is the whole ask. The hook cost is one script.  |
| Handover format      | One unified marker, `open_findings` derived from the findings contract | A separate structured handover file per phase         | One schema, one path, clean history; no duplication of the defect count that findings already own.         |
| Rollout              | Make the existing greenfield `.fsm.yml` enforcing, one rule first      | Convert every playbook to enforced YAML up front      | Proves the mechanism against real use for the price of one hook before committing the whole library to it. |

## Recommendation

Adopt a committed run-state marker plus a `transition-lint` pre-commit hook, driven by the YAML playbook shape the `.fsm.yml` already established. Make the handover artifact that same marker — extended with gate result and next state, with its open-findings count derived from the existing [finding-format.md](../../rulebooks/conventions/finding-format.md#frontmatter-schema) contract, never duplicating it. Prove it by making one existing playbook enforcing for one transition before touching the rest.
