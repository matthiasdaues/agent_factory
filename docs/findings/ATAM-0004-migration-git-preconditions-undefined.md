---
id: ATAM-0004
source: atam-review
severity: medium
category: defect
artifact: docs/adr/0026-layout-migration-runs-inside-the-factory-update.md#decision
status: open
traces: [ADR-0026, DEC-06, DEC-17]
---

# The migration does not define what happens to files git does not track

**What is wrong:** ADR-0026 (line 64) moves each file of the path table with `git mv` and removes the use-case files with `git rm`. Neither the architecture nor the specification says what happens when one of these files is untracked or ignored. They also do not cover a repository that is in the middle of a merge or rebase, or one whose index is locked.

`git mv` refuses an untracked file with `fatal: not under version control`. Agents often leave files like this in `docs/spec/`, for example a new gaps report or a draft feature file that nobody has added yet. Under DEC-17 the script then fails partway, undoes its changes, and the whole update rolls back. Each later update fails the same way. The developer sees only `update-factory: the sourced init-factory did not complete`. Nothing names the file that blocked the move.

So a common working-tree state blocks the update with no clear reason. The self-undo then also has to reverse a partial run that a check before the first change could have prevented.

**Fix:** Define in ADR-0026 how the script treats each git state of a path-table file:

- tracked: `git mv`;
- untracked: a plain move, or a refusal;
- ignored: a plain move, or left in place.

Add a check that runs before the first change. When the script refuses, it exits non-zero before it changes anything. It names each blocking file and the command that clears it, so the developer can fix the state and run the update again. Add the chosen behavior to the `migrate-spec-layout` contract in `interface-contracts.md` and a scenario to `core-artifact-layout.feature`.
