---
id: ATAM-0006
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0026-layout-migration-runs-inside-the-factory-update.md#decision
status: open
traces: [ADR-0026, ATAM-0004, DEC-10, QS-14, QS-15]
---

# The removal of a tracked file with uncommitted changes either blocks the migration or loses the changes

**What is wrong:** ADR-0026 removes each tracked file of the removal set with `git rm`, "also when it has uncommitted changes". The removal set is `actor-goal-list.md` and every `use_cases/` folder under `docs/` (`interface-contracts.md`, line 152). `git rm` refuses a file with uncommitted changes:

```text
error: the following file has local modifications:
    UC-01.md
(use --cached to keep the file, or -f to force removal)
```

So the script has two choices, and the architecture picks neither:

- Plain `git rm` fails. The migration fails, and every later update fails the same way. That breaks "no git state blocks the migration" (QS-14).
- `git rm -f` deletes the uncommitted changes. They exist nowhere else. ADR-0026 keeps an untracked file in the removal set for exactly this reason. If the script fails later, its undo restores the committed version only. Then `git status` differs from the state before the run, which breaks the response measure of QS-15.

**Fix:** Define the case in ADR-0026 and in the `Removes` row of `interface-contracts.md`. The rule for untracked files fits: a tracked file in the removal set with uncommitted changes stays in place, and the script lists it for the developer to delete. Add a scenario to `core-artifact-layout.feature` in the requirements fix pass.
