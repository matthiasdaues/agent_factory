[back to index](README.md)

# 6. Runtime View

## 6.1 Advance a playbook phase (UC-01)

Derived from dynamic view `PhaseAdvance` in [`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant HO as humanOperator
    participant PC as phaseCli
    participant MK as marker
    participant FS as fsmDefinition
    participant FD as findings

    HO->>PC: Runs phase advance
    PC->>MK: Reads current state, or bootstraps at the FSM root
    PC->>FS: Resolves forward transition + target's entry_conditions
    PC->>FD: Evaluates no_open_findings conditions
    alt every entry condition met
        PC->>MK: Writes state/iteration=1/recorded_at=now
        PC-->>HO: advanced <from> -> <to>, exit 0
    else one or more unmet
        PC-->>HO: every unmet condition named, marker unchanged, exit 1
    end
```

Full scenario, extensions, and business rules: [docs/spec/use_cases/UC-01-advance-a-playbook-phase.md](spec/use_cases/UC-01-advance-a-playbook-phase.md).

## 6.2 Block an out-of-phase commit (UC-02)

Derived from dynamic view `BlockOutOfPhaseCommit` in [`architecture.dsl`](architecture.dsl).

```mermaid
sequenceDiagram
    participant GP as gitPreCommit
    participant TL as transitionLint
    participant MK as marker
    participant FS as fsmDefinition

    GP->>TL: Fires at commit time, staged files as input
    TL->>MK: Reads current playbook + state
    alt no marker
        TL-->>GP: TL-NOMARKER (info), exit 0
    else marker present
        TL->>FS: Reads outputs: globs per state
        loop each staged file
            Note over TL: owner = state whose outputs: glob matches the file
        end
        alt every staged file ungoverned or owned by current state
            TL-->>GP: 0 error findings, exit 0 — commit proceeds
        else a staged file owned by another state
            TL-->>GP: TL-ORDER naming the file, exit non-zero — commit blocked
        end
    end
```

Full scenario, extensions, and business rules: [docs/spec/use_cases/UC-02-block-an-out-of-phase-commit.md](spec/use_cases/UC-02-block-an-out-of-phase-commit.md).

## 6.3 Retry a phase within the iteration cap (UC-03)

Short sequence — no dedicated DSL dynamic view; `phase retry` uses the same `phaseCli` → `marker`/`fsmDefinition` relationships as §6.1, just a different subcommand.

```mermaid
sequenceDiagram
    participant Actor as humanOperator or orchestratorAsTrigger
    participant PC as phaseCli
    participant MK as marker
    participant FS as fsmDefinition

    Actor->>PC: Runs phase retry
    PC->>MK: Reads current state
    PC->>FS: Resolves loop-back target (else transition, or current state)
    PC->>FS: Resolves iteration limit (halt_conditions, or --default-max-iterations)
    Note over PC: iteration += 1
    alt iteration <= limit
        PC->>MK: Writes iteration + fresh recorded_at
        PC-->>Actor: "<state>: retry <n>/<limit> recorded", exit 0
    else iteration > limit
        PC-->>Actor: cap reached + declared message, exit 2 — marker NOT written
    end
```

Full scenario, extensions, and business rules: [docs/spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md](spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md).

## 6.4 Resume and dispatch (UC-05, UC-04)

Derived from dynamic view `ResumeAndDispatch` in [`architecture.dsl`](architecture.dsl). This is the mechanism that makes a crashed session, a closed terminal, or a fresh session safe to resume: every fact is re-derived from disk, never trusted from a persisted status.

```mermaid
sequenceDiagram
    participant HO as humanOperator
    participant RS as runStep
    participant MK as marker
    participant CAT as catalog
    participant PC as phaseCli
    participant TR as trigger
    participant CA as cliInvokedAgent

    HO->>RS: Invokes to find out what to do next
    RS->>MK: Reads to resolve current playbook + state
    RS->>CAT: Reads fsm: field, and agents: as the fallback ordering
    Note over RS: Checks the state's outputs: glob against disk, runs its gate
    alt outputs missing
        RS->>TR: Dispatches the resolved agent (fresh start)
    else outputs exist, gate clean, no open findings
        RS->>PC: Calls advance
        Note over RS: Repeats from resolving the new state's agent
    else outputs exist, gate reports open findings
        RS->>PC: Calls retry
        alt cap not hit
            RS->>TR: Re-dispatches the same agent
        else cap hit
            RS-->>HO: Stop, escalate — do not re-dispatch
        end
    else outputs exist, gate errors (not findings)
        RS-->>HO: Stop, escalate — an error is not "findings to address"
    end
    TR->>CA: Dispatches: background subprocess or interactive session
    CA-->>TR: Exit code (background) — no failure classification
```

Full scenario, extensions, and business rules: [docs/spec/use_cases/UC-05-resume-an-interrupted-playbook-run.md](spec/use_cases/UC-05-resume-an-interrupted-playbook-run.md), [docs/spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md](spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md).

## 6.5 Gate outcome decision (flowchart)

Not a DSL view — a decision table rendered as a flowchart, matching [`run-step` § Step 3](../factory/skills/run-step/SKILL.md#step-3-decide-fresh-start-resume-mid-step-or-already-done).

```mermaid
flowchart TD
    A[Check state's outputs: glob against disk] --> B{Outputs exist?}
    B -->|No| C[Fresh start: run author agent's Step 1]
    B -->|Yes| D[Run the phase's own gate]
    D --> E{Gate result?}
    E -->|Clean, no open findings| F[phase advance, then resolve next state]
    E -->|Open findings| G[phase retry]
    G --> H{Cap hit?}
    H -->|No| I[Re-dispatch same agent]
    H -->|Yes| J[Stop, escalate to actor]
    E -->|Errors, not findings| J
```

## Referenced from

- [docs/spec/use_cases/system-use-cases.md](spec/use_cases/system-use-cases.md)
