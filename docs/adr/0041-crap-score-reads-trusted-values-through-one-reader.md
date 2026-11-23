---
id: 0041
status: accepted
evaluation: none
---

# crap-score reads its trusted values through one reader

## Context

`crap-score` judges a story's code against a `threshold`, skips the files that the `exclude` list of each measure names, and accepts the functions that the exceptions register `docs/findings/exceptions.md` lists. The security review of 2026-11-22 found that the gate read `threshold` and `exclude` from the story head (T-0418). So a story could raise its own threshold or exclude its own file, and the merge would pass it. The register was already read from `dev`, but through its own code path.

The stakeholder settled the rule in DEC-67 of [crap-gate-setup.md](../proposals/crap-gate-setup.md#decisions): what counts as accepted is decided outside the story. DEC-67 also asked for a seam, because other workflows keep such values in a knowledge-graph store or in an issue tracker such as Jira. DEC-68 to DEC-72 settle the design of the reader. No second design was weighed, so this record has no matrix.

## Decision

1. **One reader returns every trusted value.** The reader, called the trusted gate source, is one interface inside `crap-score`. It returns the `threshold`, the `files` pattern and the `exclude` list per measure, the exceptions, and the notices that say where each value came from. The gate logic calls nothing else to reach a trusted value (DEC-72).
2. **The git ref of the integration branch is the only backend.** The reader reads `docs/testing.yaml` and the register from the tip commit of the local branch `refs/heads/<integration_branch>`, never from the folder. The key `integration_branch` of `docs/factory-settings.yaml` names the branch, and `dev` applies when the file or the key is missing (DEC-68). `crap-score` reads the key from the tree of the `--base` revision, which a story cannot change, and from the folder only with `--all` or `--settings-from-folder`. The value must be a local branch name: a tag, a remote ref, or a revision exits `2` (DEC-77). `crap-score` resolves `--base` once, with a local branch winning over a tag of the same name, and uses that commit for the diff and for the key (DEC-78).
3. **The commands of the measures still come from the story head.** `command` and `ready` run on the story's code (BR-136), and the code review and the scope check guard a change to them (DEC-75). Narrowing `files` drops code from the judgement as an added `exclude` pattern does, so `files` comes from the branch. A measure that the branch names and the story head lacks makes `crap-score` exit `2` (DEC-70). A measure that the branch does not name yet takes its `files` pattern and its `exclude` list from the story head, and the output marks it as not yet trusted (DEC-69, DEC-75).
4. **A missing source falls back to the folder and says so.** Without `docs/testing.yaml` on the branch, or without `gates.crap-score` there, the reader takes `threshold`, `files` and `exclude` from the folder and prints why (DEC-69). A missing ref of the default `dev` falls back the same way only with `--all` or `--settings-from-folder`, in the setup and the proof, and the reader then reads no register (DEC-13, DEC-81). With `--base` alone, a missing `dev` makes `crap-score` exit `2`, because a story agent could otherwise delete `dev` and be judged by its own values (DEC-81). A broken source makes `crap-score` exit `2` instead: an `integration_branch` that is not a non-empty string, a `docs/testing.yaml` on the branch that cannot be parsed, or a `gates.crap-score` there without `threshold` (DEC-74). A branch that `integration_branch` names explicitly never falls back: when it does not exist, or, with `--base`, when its tip is the judged `HEAD`, `crap-score` exits `2` and names the key and the branch (DEC-76, DEC-79).
5. **Only the proof reads uncommitted settings.** `gate-setup-proof` passes `--settings-from-folder`, so it checks the values the User has not committed yet. The register still comes from the integration branch. The first commit of the proof worktree holds `docs/factory-settings.yaml` of the working tree, so the proof reads the same branch, and with the option `crap-score` skips the check for a missing measure (DEC-73). `premerge-check`, `dispatch`, and the gate-check step never pass the option (DEC-71).

No plugin loading is built. A second backend is a new class behind the same interface.

## Consequences

- A story cannot change its own `threshold`, `files` pattern, `exclude` list, or register row. A change to these values reaches the gate only after it lands on the integration branch.
- A planned removal of a measure lands on the integration branch first, or every story that lacks the measure exits `2`.
- A knowledge-graph or Jira backend needs a new class and a way to choose it. The gate logic and its tests stay unchanged.
- `premerge-check` and `dispatch` keep their fixed `dev`. A project whose integration branch has another name sets `integration_branch` for the reader, and the other scripts still assume `dev`.
- A story cannot make itself its own trusted source through `integration_branch`. The key comes from the `--base` revision, not from the story head (DEC-77), and a named branch that is missing, or with `--base` one whose tip is the judged `HEAD`, exits `2` (DEC-76, DEC-79).
- A tag named like the feature branch cannot move the base, because the local branch wins (DEC-78).
- The first setup keeps working, and so do `--all` and the proof in a repository without `dev`, and the output names every value that did not come from the trusted source.
