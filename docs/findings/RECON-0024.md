---
id: RECON-0024
source: reconcile
severity: major
category: defect
artifact: docs/spec/scope-map.md
status: resolved
traces: [test-design.feature]
---

# Scope-map test-design rows still marked specified after implementation

**What is wrong:** All 15 scope-map rows sourced from `test-design.feature` remain at status `specified` with empty Feature Link columns, despite all 8 implementation stories (ST-0182 through ST-0189) having been merged to `dev`. The scope map is a descriptive record of reality; these rows should reflect the implemented state and point at the implementing artifacts.

**Fix:** Update all 15 rows to `implemented` and populate their Feature Link columns with the paths to the implementing code (skills, agents, scripts, rulebooks, and configuration files).
