---
id: 0026
status: accepted
evaluation: none
---

# Layout migration runs inside the factory update

## Context

[ADR-0025](0025-core-artifact-layout-under-docs-spec.md) moves a project's
specification core into `docs/spec/`. Installed projects still have the old
paths. The factory's scripts and hooks of the new version read only the new
paths, so a project that updates the factory must also move its files. No
script reads both layouts (DEC-11).

[ADR-0023](0023-update-transaction-with-approval-staging-and-rollback.md)
defines the update transaction: approval, download and verification,
staging, application, rollback, and receipt. ADR-0023 states that
`update-factory` does not delegate to `init-factory`. The script does
delegate: after it applies the staged tree, it runs the new version's
`init-factory`, and it rolls back the factory tree when `init-factory` exits
non-zero. The layout migration builds on this step.

The accepted proposal [core-artifact-layout.md](../proposals/core-artifact-layout.md)
settles the options. The rejected options are:

- **A separate confirmation for the move.** The developer would approve the
  update and then the move. Declining the move would leave new scripts on an
  old layout. The approval of the update covers the move (DEC-04, replaced by
  DEC-17).
- **The old `update-factory` runs the migration.** The old version does not
  know the script. The first update that ships the layout would then not
  move the files. The new version's `init-factory` runs it (DEC-17).
- **The migration on every `init-factory` run.** A first install would move
  files that the project owns, such as its own `docs/CONTEXT.md`. The script
  runs only on an update (PROP-25).
- **The script stops on two vocabularies.** A project with a chapter 12 and a
  `CONTEXT.md` would block its update. The script keeps both as sections and
  lists the duplicate terms (DEC-18).
- **The script folds routing into `agent-context.md`.** A context map names
  bounded contexts, and turning them into domain concerns needs judgment. The
  skill `capture-context --fold-context-map` does it with the developer
  present (DEC-08, DEC-13).

`evaluation: none`, because the proposal decided each point and no open
alternative is left to weigh.

## Decision

The script `migrate-spec-layout` moves an installed project into the core
artifact layout. `init-factory` runs it as its last step on an update. The
developer approves the update as a whole at the approval step of ADR-0023 and
is not asked about the move. Declining the update means no update (DEC-17).

**Version test.** `init-factory` reads the `factory_version` of the prior
install record `.agent-factory/install.json` before it writes anything to
that file. `init-factory` runs the script when the prior version is older
than the layout release `1.4.0`, the constant `LAYOUT_RELEASE` of
`init-factory` (CAL-G02).

The comparison follows the precedence rules of Semantic Versioning 2.0.0.
Major, minor, and patch compare as numbers, so `1.4.0` is older than
`1.10.0`. A prerelease is older than its release, so `1.4.0-rc` is older than
`1.4.0`. A missing `factory_version`, the value `unknown`, or a value that is
not a semantic version counts as older.

Only a project without `install.json` is a first install: `init-factory` moves
nothing, lists each old path it finds, and names `migrate-spec-layout` as a
command the developer can run. A later run at the same version moves nothing.

**What the script changes.** It moves each file of the proposal's path table
and removes the use-case files. A file's git state decides the command, and
no git state blocks the migration:

- A tracked file moves with `git mv`, also when it has uncommitted changes.
  Git then records a rename, and the changes stay in the working tree.
- An untracked or an ignored file moves with a plain file move. Git has no
  record of it to keep.
- A tracked file without uncommitted changes that the path table removes is
  removed with `git rm`.
- A file that the path table removes stays in place when it is untracked,
  ignored, or tracked with uncommitted changes, staged or unstaged. The
  script lists it for the developer to delete. `git rm` refuses a tracked
  file with uncommitted changes, and `git rm -f` or a plain removal would
  lose content that exists nowhere else. The script never uses `git rm -f`.
- Before its first change, the script checks the state of the repository.
  During a merge or a rebase, or while another git process holds the index
  lock, it changes nothing, names the state, and exits non-zero. The update
  then rolls back, and the developer runs it again after finishing or
  aborting the merge or rebase.

It rewrites local
Markdown links to old paths and the relative links inside moved files. It
moves glossary terms from chapter 12 and from each `CONTEXT.md` with a
`## Language` section into `docs/spec/glossary.md`. It sets the `files:`
value of each hook in the factory's `agent_factory_hook-*` block of
`.pre-commit-config.yaml` and the `theme` line of the DSL. It lists every
other occurrence of an old path and every duplicate term, and exits 0. It
commits nothing. It names two follow-up steps:
`capture-context --fold-context-map` and the cleanup of duplicate terms.

**Self-undo and rollback.** When the script fails partway, it undoes every
change it made and exits non-zero. `git status` then shows no change against
the state before the run. `init-factory` writes the new `factory_version` into
`install.json` only after the script exits 0. So after a failure the record
keeps the prior version. `init-factory` reports that the project keeps its old layout, names the
fix (run the update again), and exits non-zero.

`update-factory` then restores the prior factory tree, the install
manifest, and the instruction headers, as for any failed `init-factory`. The
project keeps its old layout and its old factory version, so its scripts and
hooks match its layout.

**Supported updaters.** The layout release supports updates only from an
installed `update-factory` `v1.1.0-rc` or later, the first release with this
rollback. A project on an older release updates to 1.3.x first. The release
notes say so. No check enforces this. The factory is pre-alpha, so the
stakeholder cut the handling of older updaters instead of extending it.

**Stakeholder decisions of 2026-11-02.**

- `update-factory` before `v1.1.0-rc` is not supported, and neither is the
  old install record `.agent-factory/factory-install.json` (ATAM-0003
  revisited; ATAM-0005 is out of scope).
- A tracked file in the removal set with uncommitted changes stays and is
  listed; the script never runs `git rm -f` (ATAM-0006, SPEC-0028).
- The version comparison follows Semantic Versioning 2.0.0 precedence, as
  the version test states (SPEC-0029).
- QS-15 covers only supported updaters, and the QA strategy cites the
  closed gaps CAL-G17 and CAL-G18 by their Scenarios (M-07).

This decision amends ADR-0023 in one point: `update-factory` runs the new
version's `init-factory` after application, and a failure of `init-factory`
triggers the rollback. All other steps of ADR-0023 stay as they are.

## Consequences

**Easier:** one approval moves the factory and the project together, so
after an update scripts, hooks, and files agree about paths. A failed
migration leaves the project as it was. Uncommitted work and untracked files
never block the migration. The developer reviews the moves with
`git status` and commits them like any other change.

**Harder:** `init-factory` gains a version test and a step that changes
project files during an update. `migrate-spec-layout` must undo every kind of
change it makes. The update rollback does not restore project files, so the
script's own undo carries that duty. A project on a release before
`v1.1.0-rc` must update to 1.3.x first, and nothing checks that it did. A file
in the removal set with uncommitted changes stays until the developer deletes
it. The script keeps a copy
of each untracked or ignored file it moves until it exits, because git holds
no copy for the undo. A merge, a rebase, or a held index lock stops the
update until the developer resolves it. Old paths outside Markdown links and
outside the factory hook block stay for the developer to fix from the list.
