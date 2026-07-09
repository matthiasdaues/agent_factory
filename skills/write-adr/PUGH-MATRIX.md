# Pugh Matrix

Disclosed reference for the `write-adr` skill.

## Format

```markdown
| Criterion              | Weight | Option A (baseline) | Option B | Option C |
|------------------------|--------|---------------------|----------|----------|
| [quality attribute 1]  | [1-3]  | 0                   | +1       | -1       |
| [quality attribute 2]  | [1-3]  | 0                   | -1       | +1       |
| …                      |        |                     |          |          |
| **Weighted total**     |        | **0**               | **+2**   | **-1**   |
```

## Scale

| Score | Meaning                                     |
| ----- | ------------------------------------------- |
| +1    | Better than the baseline                    |
| 0     | Same as the baseline (or _is_ the baseline) |
| -1    | Worse than the baseline                     |

## Rules

- **Baseline**: pick the most obvious or status-quo option as the baseline (all zeros). Every other option is scored relative to it.
- **Criteria**: draw from `docs/10_quality_requirements.md` quality goals. Add Clean Architecture and SOLID criteria where the decision affects boundaries or contracts (e.g., Dependency Inversion, Interface Segregation).
- **Weight**: 1 = nice to have, 2 = important, 3 = critical. Derive from the quality goal priorities.
- **Weighted total**: sum of (score × weight) per option. Highest wins — but the matrix informs, it doesn't decide. Call out any close scores or criteria where a small change in weight would flip the result.
- **Minimum alternatives**: 2 (baseline + 1). More is fine.
