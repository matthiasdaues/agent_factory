---
name: pugh-matrix
description: Evaluate multiple alternatives against weighted criteria in a Pugh Matrix, present for confirmation, return the completed matrix. Use when a decision has genuine alternatives worth formally comparing — not every decision needs this.
category: architecture
disable-model-invocation: true
---

# Pugh Matrix

Weighted-alternatives evaluation. Standalone technique, not tied to any one artifact — called by whatever agent or skill needs a formal comparison (typically before `write-adr`, but not exclusively).

## Step 1 — Build the matrix

```markdown
| Criterion              | Weight | Option A (baseline) | Option B | Option C |
|------------------------|--------|---------------------|----------|----------|
| [quality attribute 1]  | [1-3]  | 0                   | +1       | -1       |
| [quality attribute 2]  | [1-3]  | 0                   | -1       | +1       |
| …                      |        |                     |          |          |
| **Weighted total**     |        | **0**               | **+2**   | **-1**   |
```

Rules:

- **Baseline**: the most obvious or status-quo option, scored all zeros. Every other option is scored relative to it.
- **Criteria**: draw from the project's declared quality goals (e.g. `docs/10_quality_requirements.md` where arc42 is in use). Add **Clean Architecture**/**SOLID** criteria when the decision affects boundaries or contracts.
- **Weight**: 1 = nice to have, 2 = important, 3 = critical. Derive from quality-goal priorities.
- **Weighted total**: sum of (score × weight) per option. Highest wins — but the matrix informs, it doesn't decide. Call out any close scores or criteria where a small weight change would flip the result.
- **Minimum alternatives**: 2 (baseline + 1). More is fine.

## Step 2 — Present for confirmation

Show the matrix. Ask: _"Do these criteria and scores reflect your assessment?"_ Adjust and re-present until confirmed.

**Completion**: matrix confirmed, ready to hand to the calling skill/agent (typically embedded verbatim into an ADR's Context section by `write-adr`).
