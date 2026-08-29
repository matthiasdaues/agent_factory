---
id: RECON-0021
source: reconcile-spec
severity: major
category: defect
artifact: factory/scripts/backlog-lint#L53
status: resolved
traces: [ADR-0012, ST-0152]
---

# backlog-lint FACTORY_DEFAULT_QUALITY_GATES still includes mutation-analysis

**What is wrong:** `factory/scripts/backlog-lint` line 53 defines `FACTORY_DEFAULT_QUALITY_GATES = ("crap-score", "mutation-analysis", "dependency-check")` — a three-gate default. The amended ADR-0012 and `factory/agents/implementation-agent.md` (line 128) define the Factory hardcoded default as two gates: `crap-score` and `dependency-check`. The mismatch means backlog-lint flags stories that omit `mutation-analysis` from their `quality-gates` field as requiring a `notes:` justification, even though the implementation-agent would never run mutation-analysis by default.

**Fix:** Update `FACTORY_DEFAULT_QUALITY_GATES` in `factory/scripts/backlog-lint` to `("crap-score", "dependency-check")`. Keep `mutation-analysis` in `VALID_QUALITY_GATES` since projects can still declare it as a custom gate.
