[back to index](README.md)

# 10. Quality Requirements

## 10.1 Quality Tree

```
Factory Flow Control
├── Determinism
│   ├── Gate ownership never depends on judgement (transition-lint)
│   └── Advance/refuse is a pure function of files on disk (phase advance)
├── Resumability
│   ├── No persisted execution status — re-derived every time (run-step)
│   └── A crash between commands leaves nothing to reconcile
├── Safety
│   ├── Two independent layers deny the same dangerous commands
│   └── Never a blanket permission bypass in background dispatch
├── CLI-agnosticism
│   ├── Same mechanisms for a human, orchestrator/, and a dispatched agent
│   └── trigger is the only CLI-aware mechanism
└── Simplicity
    ├── Zero third-party dependencies per gate script
    └── Adding a mechanism adds one stdlib script, not a library upgrade
```

Priority order and rationale: [01_introduction_and_goals.md § 1.2 Quality Goals](01_introduction_and_goals.md#12-quality-goals).

## 10.2 Quality Scenarios

Derived from the acceptance criteria in [docs/spec/use_cases/](spec/use_cases/system-use-cases.md).

| #    | Scenario                                                                                                                                                                                                | Quality attribute    | Source                                                                                      |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------- |
| QS-1 | A file belonging to a later playbook state is staged. `transition-lint` reports `TL-ORDER` naming the file and exits non-zero, blocking the commit.                                                     | Determinism          | [UC-02](spec/use_cases/UC-02-block-an-out-of-phase-commit.md#acceptance-criteria)           |
| QS-2 | `phase advance` is run with an unmet entry condition. It reports every unmet condition by name and reason, and the marker is left byte-for-byte unchanged.                                              | Determinism          | [UC-01](spec/use_cases/UC-01-advance-a-playbook-phase.md#acceptance-criteria)               |
| QS-3 | A session crashes mid-phase. A fresh `run-step` invocation, with no memory of the crash, dispatches the correct next action — fresh start, resume, advance, or escalate.                                | Resumability         | [UC-05](spec/use_cases/UC-05-resume-an-interrupted-playbook-run.md#acceptance-criteria)     |
| QS-4 | A review loop hits its configured cap. `phase retry` refuses (exit `2`), the marker's iteration is left unchanged, and the actor is told to escalate rather than looping again.                         | Resumability, Safety | [UC-03](spec/use_cases/UC-03-retry-a-phase-within-the-iteration-cap.md#acceptance-criteria) |
| QS-5 | An agent session attempts `git push --force`. The `PreToolUse` hook denies it (exit `2`) before the command runs, naming the matched pattern.                                                           | Safety               | [UC-07](spec/use_cases/UC-07-block-a-dangerous-git-command.md#acceptance-criteria)          |
| QS-6 | The same `trigger playbook <name> --step <agent>` invocation dispatches the correct agent under `--cli claude` and under `--cli copilot`, each with its own allowlist syntax, same resolved model tier. | CLI-agnosticism      | [UC-04](spec/use_cases/UC-04-dispatch-an-agent-via-trigger.md#acceptance-criteria)          |
| QS-7 | Every gate script runs on a bare Python 3.8+ interpreter with no `pip install` step.                                                                                                                    | Simplicity           | [docs/spec/prd.md § 5 Constraints](spec/prd.md#5-constraints)                               |

## 10.3 Priorities for evaluation

An architecture review ([architecture-review-agent](../factory/agents/architecture-review-agent.md)) should weigh trade-offs in this order:

1. **Determinism over convenience.** A gate that sometimes needs judgement is not a gate — push it back to an agent's own workflow instead of softening the check.
2. **Resumability over persisted shortcuts.** Any temptation to cache "what step are we on" outside the marker/outputs/gate triad should be rejected — see [08_crosscutting_concepts.md § 8.2](08_crosscutting_concepts.md#82-observable-state-resumability).
3. **Safety over dispatch convenience.** A wider allowlist that makes `trigger` more convenient is not worth relaxing BR-011/BR-012's evidence-only-what's-observed standard.
4. **Simplicity over completeness.** New mechanisms should stay zero-dependency even where a library would be less code — matches this repo's existing zero-dependency convention across every `*-lint` script.

## Referenced from

- [docs/spec/use_cases/system-use-cases.md](spec/use_cases/system-use-cases.md)
