# Fagan Review — Pi `run_agent` Streaming

Scope: exact committed delta
`ba874ae9dcfeb062426d289bb5ee3ffda59c36ba..364101ba7f5144fd618f9bfad2c45f7adaca6826`.

All six changed files were inspected for correctness, Clean Architecture,
SOLID, maintainability, consistency, YAGNI, and alignment with UC-10 and its
interface contract.

| Finding                                                                                                                                                                                                      | Artifact                                     | Category | Severity |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- | -------- | -------- |
| Cancellation waits forever when a spawned child ignores `SIGTERM`; add bounded escalation, pipe teardown, staging cleanup, and a non-cooperative-child regression ([FAGAN-0010](../findings/FAGAN-0010.md)). | `factory/config/extensions/run-agent.ts:275` | Defect   | Major    |

The incremental JSONL parser handles arbitrary normal chunk boundaries,
ignores malformed and oversized events with bounded retained parser state,
keeps stderr and progress payloads bounded, performs one child spawn without
retry, flushes the complete capture file before handoff, and isolates
best-effort capture failure from the agent result. No unused abstraction,
premature optimization, or speculative generality was found.

## Remediation verification

FAGAN-0010 is resolved. A deterministic tracer proved the original
implementation hung beyond three seconds when a child and stdout-holding
descendant both ignored `SIGTERM`. The corrected implementation uses bounded
process-group escalation and pipe teardown, returns a distinct cancellation
diagnostic without retry, cleans staging, and terminates both recorded PIDs.
