---
id: FAGAN-0027
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/cli.py#build_parser / src/orchestrator/loop_policy.py
status: resolved
traces: [VR-002]
---

# --cap accepts zero/negative values violating VR-002

**What is wrong:** The `--cap` CLI argument accepts any integer including zero and negative values. VR-002 requires "a positive integer (default 3)." A `--cap 0` causes the loop to halt immediately on any first-pass failure.

**Fix:** Add `choices` or a custom type validator in `argparse` that enforces `cap >= 1`, or validate in `LoopPolicy.__init__()`.
