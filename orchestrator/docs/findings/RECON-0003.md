---
id: RECON-0003
source: reconcile-spec
severity: major
category: defect
artifact: orchestrator/.pre-commit-config.yaml#L36-L62
status: open
traces: [ADR-0001]
---

# orchestrator/.pre-commit-config.yaml out of sync with its own template

**What is wrong:** The file's own header states "Both configs MUST define the same hooks. Keep them in sync," referring to `orchestrator/pre-commit-config.yaml` (the template copied by `orchestrate init`). ST-0066 fixed the template's `arch-lint`, `backlog-lint`, `matrix-lint`, and `statemachine-lint` hooks to invoke `factory/scripts/<name>` and `config/model-matrix.conf`, but explicitly scoped `orchestrator/.pre-commit-config.yaml` (the dev config) out of that story. The dev config's four gate hooks still invoke bare `scripts/arch-lint`, `scripts/backlog-lint`, `scripts/matrix-lint --matrix orchestrator/model-matrix.conf`, and `scripts/statemachine-lint` — none of which resolve, since no bare `scripts/` directory exists anywhere in the repository (only `factory/scripts/`). Running the file's own documented usage line, `pre-commit run -c orchestrator/.pre-commit-config.yaml --all-files`, fails on all four hooks with command-not-found. This is a real functional break, not just stale prose, and it postdates root `.pre-commit-config.yaml`'s own successful merge in ST-0067, which fixed the equivalent `-orchestrator`-suffixed hooks in the root file to use `factory/scripts/<name>`.

**Fix:** Update the four gate hooks in `orchestrator/.pre-commit-config.yaml` to mirror the already-fixed `orchestrator/pre-commit-config.yaml` template and the `-orchestrator`-suffixed hooks in root `.pre-commit-config.yaml`: `entry: python3 factory/scripts/arch-lint --docs-dir orchestrator/docs --no-validate`, `entry: python3 factory/scripts/backlog-lint --backlog-dir orchestrator/backlog`, `entry: python3 factory/scripts/matrix-lint --matrix orchestrator/model-matrix.conf`, `entry: python3 factory/scripts/statemachine-lint --spec-dir orchestrator/docs/spec`. Separately, decide and record whether this dev-only config (invoked only via explicit `-c`, never auto-discovered) should keep existing at all now that its hooks are fully duplicated inside the merged root file with `-orchestrator` suffixes — if it stays, its header comment should say what it is for that the root file doesn't already cover.
