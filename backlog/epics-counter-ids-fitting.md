---
scope: global
---

# EPICs — Counter IDs Fitting

Proposal trace: [counter-ids-fitting.md](../docs/proposals/counter-ids-fitting.md)
Specification trace: [counter-ids-fitting.feature](../docs/spec/features/counter-ids-fitting.feature), [gaps report](../docs/spec/work/counter-ids-fitting-gaps.md), [interface-contracts.md § Counter IDs Contracts](../docs/spec/interface-contracts.md#counter-ids-contracts), [validation-rules.md § Counter IDs fitting](../docs/spec/validation-rules.md#counter-ids-fitting-br-096br-108), [state-machines.md § Move Lifecycle](../docs/spec/state-machines.md#move-lifecycle), [entity-model.md § Counter IDs Fitting Entities](../docs/spec/entity-model.md#counter-ids-fitting-entities)
Architecture trace: [ADR-0033](../docs/adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md), [arc42 § 5.11](../docs/arc42/05_building_block_view.md#511-level-2-component-view----id-allocation), [arc42 § 6.16](../docs/arc42/06_runtime_view.md#616-move-of-a-local-counter-to-origin), [arc42 § 8.18](../docs/arc42/08_crosscutting_concepts.md#818-id-allocation), [QS-22](../docs/arc42/10_quality_requirements.md#qs-22-a-move-hands-out-no-id-twice), [QS-23](../docs/arc42/10_quality_requirements.md#qs-23-a-second-counter-on-origin-shows-at-the-move)
QA strategy trace: [counter-ids-fitting-qa-strategy.md](../docs/spec/work/counter-ids-fitting-qa-strategy.md)

Dependency order: E1 and E3 start at once, with ST-0376 and ST-0383. E2 starts when ST-0376 and ST-0377 are merged, because the local counter needs the seed step and the seed command. Inside E1, ST-0377 waits for ST-0376, and ST-0378 waits for ST-0377 and ST-0379. Inside E2, ST-0380 waits for ST-0379, and ST-0381 and ST-0382 wait for ST-0380. Inside E3, ST-0384 waits for ST-0383, and ST-0385 waits for ST-0384.

## Story waves

| Wave | Stories          | Merge order inside the wave                                                                                                                         |
| ---- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| W1   | ST-0376, ST-0383 | any; ST-0376 edits `next-id` tests, ST-0383 edits the rulebooks and `test_counter_ids_text.py`                                                      |
| W2   | ST-0377, ST-0384 | ST-0377 first, because both regenerate `packages/factory/INDEX.yaml`                                                                                |
| W3   | ST-0379, ST-0385 | ST-0379 first, because both may regenerate `packages/factory/INDEX.yaml`                                                                            |
| W4   | ST-0378, ST-0380 | any; ST-0378 edits `init-factory`, ST-0380 edits `next-id`                                                                                          |
| W5   | ST-0381, ST-0382 | any; ST-0381 edits `next-id` and `test_next_id_move.py`, ST-0382 edits `session-menu.md`, `test_fitting_text.py`, and `test_block_dangerous_git.py` |

Every story carries `quality-gates: []`, as the recent stories do, because the CRAP and mutation gates cannot run yet (T-0402).

## Terms used in every EPIC

The [glossary](../docs/spec/glossary.md#counter-ids-vocabulary) defines each term. A short reminder:

- **Counter.** The ref `refs/ids/counters` on the remote that `next-id` resolves. It points at the claim commit.
- **Claim commit.** A commit with no parent on the empty tree. Its message holds `start=<number>`, one line per ID prefix with the highest number claimed so far, such as `ST=0012`, and a random token line.
- **ID claim.** One call of `next-id <PREFIX>`. It raises the line of the prefix by one, pushes a new claim commit with a lease on the old one, and prints the ID.
- **ID prefix.** One of the twelve prefixes in `PREFIXES` of `next-id`: `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, `T`, `ADR`, `ARCH`, and `QA`.
- **Seed.** `next-id --seed <number> [<PREFIX>=<n> …]`. It creates the counter once and refuses when the counter exists.
- **Seed command.** The one line that `next-id --plan-seed` prints, such as `next-id --seed 0 ST=375 ADR=32`. The entity model calls it the seed plan.
- **ID in use.** An ID that `--plan-seed` counts from a file name, the `id` field of a register line, or a todo heading. Body text never counts.
- **Fitting.** The guided setup in `virgil.md` § Fitting. Each step sets one fitting key in `.agent-factory/config/project-context.json`. The seed step is step 4, and its key is `fitting.counter_seeded`.
- **Local counter.** The counter in the `.git` of the project's main repository, for a project without `origin`. The git setting `agent-factory.counterRemote` holds the path of that repository.
- **Marker commit.** The commit that `next-id --move-to-origin` leaves at the local counter. Its message is the one line `moved=<remote>`, and its parent is the claim commit C that the move carries.
- **ID producer.** A Factory file that tells its reader to create an indexed artifact. The proposal calls it a requestor.
- **Local bare repository.** A repository made with `git init --bare` in a temporary directory. Every test and every demo uses one as `origin`.

## Rules that hold for every EPIC

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No test and no demo touches this project's real remote. Each uses local bare repositories, local clones, and worktrees in a temporary directory, as [§ Test setup](../docs/spec/work/counter-ids-fitting-qa-strategy.md#test-setup) of the QA strategy defines.
- No test prints a remote URL or a git config. A failing path asserts the redacted form, such as `https://***@host/demo.git`.
- Tests carry `@pytest.mark.spec("CIF-NN-XX-NN")` with the Test ID of their row in the [QA strategy](../docs/spec/work/counter-ids-fitting-qa-strategy.md#contract-owners). ST-0376 adds `CIF-*` to the `spec` marker description in `pyproject.toml`.
- Agents do not run `uv run pytest` by hand, because the guardrail hook blocks it. The tests run through the commit hooks.
- `index-lint --check` passes after every story that changes an agent, skill, convention, or playbook. Such a story regenerates `packages/factory/INDEX.yaml` in the same commit.
- No story changes the guardrail hook `block-dangerous-git.sh`.
- No story plans a deferred item: re-seeding a counter that exists, or IDs on branches that are neither local nor fetched.
- A failed `next-id` exits non-zero, prints nothing on standard output, and names its cause on standard error, as the Failure row of [interface-contracts.md § next-id](../docs/spec/interface-contracts.md#packagesfactoryscriptsnext-id) states.

## Governance and risk

The proposal declares `assurance: elevated` and two risk domains. Each one has stories that carry it:

| Risk domain      | What goes wrong                                                                                                      | Stories that guard it                                                                                                                              |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data_integrity` | A seed starts a sequence below an ID in use, a move hands out a number twice, or a seed or move overwrites a counter | ST-0376 (counting rules), ST-0379 (one local counter for all worktrees), ST-0380 (marker, create-only push), ST-0381 (race, interrupted move)      |
| `operations`     | The fitting never finishes, a fitting key flips between runs, a claim fails without a next step, or a move hangs     | ST-0377 (six keys), ST-0378 (key derivation, unreachable remote), ST-0380 (named causes, no prompts), ST-0382 (the offer and the collision report) |

Every story whose risk domain is `data_integrity` has `risk_level: high`.

## Choices made without the stakeholder

The brief ran in full auto mode. Each phase that asks for approval took the recommended option below. The stakeholder approves the backlog at playbook step 3.4.

| ID       | Phase           | Choice                                                                                                                                                                                                                                                                                                                                                                            | Reason                                                                                                                                                                                                          |
| -------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CIFP-C01 | 1, EPIC slicing | Three EPICs: the seed in the fitting (E1), the local counter and its move (E2), and the literal prefix in each ID producer (E3).                                                                                                                                                                                                                                                  | Each EPIC is one journey. E1 serves the User who sets up a project with `origin`. E2 serves the User without `origin`. E3 serves every agent that creates an indexed artifact and shares no file with E1 or E2. |
| CIFP-C02 | 3, story slices | ST-0376 ships `--plan-seed` alone, and it owns CIF-01-IT-01 and CIF-03-IT-01.                                                                                                                                                                                                                                                                                                     | A User can run `next-id --plan-seed` and then the printed command without VIRGIL. Both tests check `next-id` behaviour, and ST-0376 makes them true first.                                                      |
| CIFP-C03 | 3, story slices | The seed step (ST-0377) and the key derivation in `init-factory` (ST-0378) are two stories.                                                                                                                                                                                                                                                                                       | The User walks the step in a session, and `init-factory` derives the key on a later run. Each outcome shows alone, and VIRGIL sets the key in the step, so ST-0377 does not need ST-0378.                       |
| CIFP-C04 | 3, story slices | Gap CIF-G06: the setting `agent-factory.counterRemote` stays when the User declines the seed.                                                                                                                                                                                                                                                                                     | A second walk of the step sets the same value. While no counter exists, a claim fails with "counter missing", which names the real cause. SPEC-0061 reads the gap the same way.                                 |
| CIFP-C05 | 3, story slices | Gap CIF-G10: `--plan-seed` also counts the file names, register lines, and todo headings in the working tree of the current worktree.                                                                                                                                                                                                                                             | A seed below an ID in use hands out a number twice, which the QA strategy rates `blocking`. A seed above it costs one gap in a sequence.                                                                        |
| CIFP-C06 | 3, story slices | Gap CIF-G09: the pairs of the seed command follow the order of `PREFIXES` in `next-id`.                                                                                                                                                                                                                                                                                           | The order is fixed and needs no second list. Tests still compare the pairs as a set.                                                                                                                            |
| CIFP-C07 | 3, story slices | Gap CIF-G04 and PROP-09: `packages/factory/config/session-menu.md` holds the session-start check for the move, before the menu.                                                                                                                                                                                                                                                   | Every session that reaches the menu reads that one file. The four `AGENTS.*.md` files would need four copies. The check unblocks CIF-09-LN-01.                                                                  |
| CIFP-C08 | 3, story slices | Gap CIF-G08 and SPEC-0063: a refused or failed move exits non-zero, and the tests assert it.                                                                                                                                                                                                                                                                                      | The Failure row of `next-id`, the Move Lifecycle, and QS-23 all state non-zero.                                                                                                                                 |
| CIFP-C09 | 3, story slices | CIF-QG01, SPEC-0062, and ATAM-0015: the move starts again at most ten times after a stale lease on C, and every git call of the move runs without prompts and with the 30-second limit of BR-076.                                                                                                                                                                                 | Ten is the limit of a claim (BR-072). VIRGIL runs the move in an agent shell, where a prompt hangs. The seed keeps its prompts, because BR-076 states that, and only the stakeholder can change it.             |
| CIFP-C10 | 3, story slices | SPEC-0065: `--plan-seed` writes the seed command or the in-use message on standard output and each name warning on standard error.                                                                                                                                                                                                                                                | VIRGIL reads one line from standard output. A warning there would break the command.                                                                                                                            |
| CIFP-C11 | 3, story slices | SPEC-0066: an ADR counts by a file name `docs/adr/NNNN-*.md`, and a todo heading counts when the line starts with `## T-NNNN`, with or without a title after it.                                                                                                                                                                                                                  | This project's todo headings carry titles, such as `## T-0020 — A claim can still open a credential dialog`. A rule that needs a bare heading would miss them and seed `T` too low.                             |
| CIFP-C12 | 3, story slices | Gap CIF-G01 and PROP-06: ST-0378 replaces the two `init-factory` hints with hints that name fitting step 4 and `next-id --plan-seed`, and ST-0377 changes "X/5" and "all five fitting steps" in `session-menu.md`. ST-0378 records the changed hints as a spec-feedback row and does not edit `interface-contracts.md`.                                                           | The old hints tell the User to pick one number above the highest ID, which the per-prefix seed replaces. The specification belongs to the domain-modeling agent.                                                |
| CIFP-C13 | 3, story slices | E3 has three stories: the table (ST-0383), the literal prefix in the nineteen files of the proposal's table (ST-0384), and `next-id T` in every other todo writer (ST-0385). CIF-17-CT-01 has one owner, ST-0383, which builds the text checker; ST-0384 and ST-0385 add their failing case to it.                                                                                | The three Rules CIF-14, CIF-15, and CIF-16 are three outcomes. One checker function keeps one contract with one owner.                                                                                          |
| CIFP-C14 | 3, story slices | ST-0383 removes the line "Allocate `NNNN` with `next-id <TAG>`" from `finding-format.md`, the `finding-format.md` row from `docs/spec/work/counter-ids-qa-strategy.md` (lines 36 and 91, "five" producers), and `finding-format.md` from `PRODUCERS` in `tests/factory/test_counter_ids_text.py`. Until ST-0384 merges, `finding-format.md` points reviewers to `id-prefixes.md`. | The brief names these follow-ups for the CIF-16 story. Both stories ship on one feature branch, so no release carries the gap.                                                                                  |
| CIFP-C15 | 3, story slices | ATAM-0017: the collision message of the move prints the `key=value` lines of both claim commits.                                                                                                                                                                                                                                                                                  | A human then sees whether every line on `origin` is at or above the line of C. The message stays a message, and nothing else changes.                                                                           |
| CIFP-C16 | 3, story slices | SPEC-0061 and ATAM-0016, first half: a move without the setting, without `origin`, or without a local counter changes nothing, exits non-zero, and names the missing piece.                                                                                                                                                                                                       | CIFP-C04 makes a set setting without a counter a real state, and BR-106 offers the move in it.                                                                                                                  |
| CIFP-C17 | 4, stories      | ST-0382, the offer at the session start, is should-have. Every other story is must-have.                                                                                                                                                                                                                                                                                          | No Completion Criterion names the offer. A User can run `next-id --move-to-origin` by hand once ST-0380 ships.                                                                                                  |
| CIFP-C18 | 4, stories      | The restart limit and the interrupted move have no row in the QA strategy. ST-0381 names their tests without a Test ID.                                                                                                                                                                                                                                                           | The test-strategy agent owns the QA strategy and adds the rows. Until then, the gap is named here and in ST-0381.                                                                                               |

## Minor register lines and proposal rows

The brief lets minor rows that touch behaviour become acceptance criteria. These are planned:

| Row       | Planned in       | What the story does                                                                    |
| --------- | ---------------- | -------------------------------------------------------------------------------------- |
| SPEC-0061 | ST-0380, ST-0381 | Results for a move without the setting, `origin`, or a local counter, and for a marker |
| SPEC-0062 | ST-0381          | The limit of ten restarts (CIFP-C09)                                                   |
| SPEC-0063 | ST-0380          | A refused or failed move exits non-zero (CIFP-C08)                                     |
| SPEC-0065 | ST-0376          | The command on standard output, the warnings on standard error (CIFP-C10)              |
| SPEC-0066 | ST-0376          | ADR file names and titled todo headings count (CIFP-C11)                               |
| ATAM-0015 | ST-0380, ST-0381 | No prompts and the time limit for the move; the restart limit (CIFP-C09)               |
| ATAM-0016 | ST-0380, ST-0381 | A move that reads no counter or a marker (CIFP-C16); the fitting key half is left      |
| ATAM-0017 | ST-0380          | The collision message prints the lines of both claim commits (CIFP-C15)                |
| PROP-06   | ST-0377, ST-0378 | The stale hints of `init-factory` and the "X/5" of `session-menu.md` (CIFP-C12)        |
| PROP-09   | ST-0382          | `session-menu.md` holds the offer (CIFP-C07)                                           |

These are left, with the reason:

| Row       | Reason                                                                                                                                                                          |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0064 | A text fix in `interface-contracts.md`, owned by the domain-modeling agent. No behaviour changes.                                                                               |
| SPEC-0067 | A register line deleted by a fix can hold the highest ID of a prefix. The case needs that before the first seed, which is rare. ST-0376 names it as an accepted limit.          |
| SPEC-0068 | `todos.md` and its writers number `T` in other forms. T-0008 tracks the merge of the two lists. ST-0385 names them as out of scope.                                             |
| SPEC-0069 | The word "tag" in the feature file and BR-108 is a glossary question for the domain-modeling agent.                                                                             |
| SPEC-0070 | Missing glossary terms, owned by the domain-modeling agent.                                                                                                                     |
| ATAM-0015 | The seed half: BR-076 keeps git's prompts for the seed. Only the stakeholder can change that rule.                                                                              |
| ATAM-0016 | The fitting key half: `git ls-remote` sees a marker as a counter. Reading the message needs a fetch, and the state lasts only until the move finishes. The stakeholder decides. |
| PROP-07   | The records: the architecture pass already set `architecture_change: true`, and the proposal is not part of this backlog.                                                       |
| PROP-08   | How a human resolves a collision. ATAM-0017 gives the human both sets of lines. The manual steps stay open for the stakeholder.                                                 |

## Open items for the stakeholder

- **The choices above,** especially CIFP-C04 (the setting stays after a decline), CIFP-C05 (the working tree counts), and CIFP-C12 (the wording of the new `init-factory` hints).
- **How a human resolves a collision** (PROP-08, CIF-G03). ST-0382 reports it, and no story plans the resolution.
- **Prompts and a time limit for the seed** (ATAM-0015, seed half), and **a marker counted as a seeded counter** (ATAM-0016, key half).

## E1: Seed the counter in the fitting so every sequence continues

### Why this EPIC exists

Every ID claim fails until the counter exists, and today nothing in the fitting creates it. In this project the human seeded by hand with one start of 400, so `ST` and `BUG` jumped to 0401. This EPIC adds `next-id --plan-seed`, which reads the highest number of each prefix from the branches, and fitting step 4, where VIRGIL shows that command and runs it after the User confirms. Each sequence then continues where it stands, and the fitting finishes only when the counter exists.

### Actor Goals

- User confirms the seed of the counter in a fitting step
- User walks the seed step in a greenfield project
- User sees the fitting finished only when all six fitting keys are true
- next-id --plan-seed prints one seed command from the highest number of each ID prefix
- next-id --plan-seed counts an old file name by its number and warns about it
- next-id --plan-seed checks the remote before it plans a seed
- init-factory derives counter_seeded from the remote that next-id uses

### Demo

1. Create a local bare repository `/tmp/demo-origin.git` and a clone `/tmp/demo` with `backlog/ST-0375.md` and `docs/adr/0032-agents-push-the-claim-ref-through-next-id.md` on `dev`, and `backlog/ST-0380.md` on `feature/fitting`.
2. In `/tmp/demo`, run `next-id --plan-seed`. It prints `next-id --seed 0 ST=380 ADR=32` and exits `0`. `git for-each-ref` shows the same refs as before.
3. Open a session and walk the fitting. After step 3, "Decide on hooks", VIRGIL starts step 4, "Seed the ID counter", shows the same command, and says that it creates `refs/ids/counters` on `origin` once.
4. Confirm. VIRGIL runs the command and sets `fitting.counter_seeded` to `true`. `next-id ST` prints `ST-0381`, and `next-id BUG` prints `BUG-0001`.
5. Run `init-factory`. `fitting.counter_seeded` stays `true`, and `fitting.status` is `fitted`.
6. Run `next-id --plan-seed` again. It prints that the counter is in use on the remote and exits `0`.

### Scope

**In:**

- `next-id --plan-seed [--remote <url>]`: it checks the remote as a claim does, counts the IDs in use on every local branch, every remote-tracking branch, and the working tree, and prints one seed command with one pair per prefix (BR-098 to BR-101, CIFP-C05, CIFP-C06).
- The counting rules: file names in `backlog/`, `docs/findings/`, and `docs/adr/`, the `id` field of register lines, and `## T-NNNN` headings with or without a title; never body text. An old name counts by its number and gets a warning on standard error (BR-100, CIFP-C10, CIFP-C11).
- Fitting step 4 in `virgil.md` § Fitting, after step 3: VIRGIL runs `--plan-seed`, shows the command, says what it does, runs it after the User confirms, and sets the key. A decline, an unreachable remote, and a counter in use each end the step as BR-104 states. A greenfield project walks step 0 and step 4 (DEC-06).
- `_fitting_status` in `init-factory` needs six true keys for `fitted`. The four `AGENTS.*.md` files list six keys and count six steps, and `session-menu.md` shows "X/6" and reruns six steps.
- `init-factory` derives `counter_seeded` on every run from `agent-factory.counterRemote`, else `origin`, with `git ls-remote`, also for a greenfield project. An unreachable remote leaves the key as it is (BR-105). Its two counter hints name step 4 and `next-id --plan-seed` (CIFP-C12).

**Out:**

- Re-seeding a counter that exists, and IDs on branches that are neither local nor fetched. The proposal defers both.
- The no-`origin` branch of step 4, which E2 adds with the local counter.
- Prompts and a time limit for the seed (ATAM-0015, seed half).

### Dependencies

None. ST-0378 waits for ST-0379 of E2, because its hint for a project without `origin` names the step that keeps the counter in the project's own repository.

### Boundaries

- Script: `packages/factory/scripts/next-id` (component **next-id**, the operation `inspect` of the **Counter Port**, arc42 5.11)
- Agent: `packages/factory/agents/virgil.md` § Fitting (component **virgil**)
- Script: `packages/factory/scripts/init-factory` (`_fitting_status`, `_derive_fitting_keys`, `_reconcile_project_context`, `check_counter`)
- Orientation files: `packages/factory/config/AGENTS.claude.md`, `AGENTS.codex.md`, `AGENTS.copilot.md`, `AGENTS.pi.md`; menu: `packages/factory/config/session-menu.md`
- Contracts: [interface-contracts.md § `next-id --plan-seed`](../docs/spec/interface-contracts.md#next-id---plan-seed), [§ `init-factory` counter check](../docs/spec/interface-contracts.md#init-factory-counter-check)
- Rules: BR-098 to BR-101, BR-104, BR-105
- Tests: `tests/factory/` (new `test_next_id_plan_seed.py`, new `test_fitting_text.py`; extend `test_next_id_redaction.py`, `test_init_factory.py`, `test_init_factory_counter.py`, `test_housekeeping_about.py`), `pyproject.toml`

### Domain Rules

- A seed pair holds the highest number in use of its prefix, never the count.
- Body text never counts as an ID in use.
- An old file name never blocks the seed and never lowers it unnoticed.
- `--plan-seed` changes no ref and no file.
- VIRGIL runs a seed only after the User confirms the shown command.
- `fitting.status` is `fitted` only when all six keys are `true`.
- `init-factory` never seeds and never resets the key on an unreachable remote.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                       | Tier     | Size | Goal                                                                                                                                                                      | Basis                                                                                                                                                                                       |
| ------- | ---------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0376 | Print a seed command that continues every ID sequence            | strong   | L    | The User runs `next-id --plan-seed` and gets one seed command with the highest number in use of each prefix, or a message that the counter is in use, and no ref changes. | `next-id` has `claim` and `seed`, the prefix list, the remote lookup, and the redaction. Adds the mode, the counting rules, and the warnings.                                               |
| ST-0377 | Seed the counter in fitting step 4 after confirming the command  | standard | M    | The User walks fitting step 4, sees the seed command with what it does, and VIRGIL runs it only after the User confirms; the fitting then counts six keys.                | `virgil.md` has steps 0 to 3 and five keys. `_fitting_status` checks five keys. The four `AGENTS.*.md` files and `session-menu.md` count five. Adds step 4 and the sixth key everywhere.    |
| ST-0378 | See init-factory derive counter_seeded from the counter's remote | standard | M    | Each `init-factory` run sets `counter_seeded` from the remote that `next-id` would use, leaves it on an unreachable remote, and prints hints that name step 4.            | `check_counter` asks only `origin` and prints the old hints. `_reconcile_project_context` skips a greenfield cache. Adds the remote order, the key, the greenfield path, and the new hints. |

### Testability Assessment

Every goal of `next-id --plan-seed` and `init-factory` has an observable result: the exit code, standard output and standard error of `next-id`, the key in `.agent-factory/config/project-context.json`, and `git for-each-ref` of the clone and the bare repository before and after each call. Tests run both scripts as subprocesses on local bare repositories and clones, and contract tests import `next-id` with `load_script` for the counting rules. The seed step is agent text, so text tests check what `virgil.md` tells VIRGIL to do, and the walk through a session is a manual demo. Two red flags are settled by choices: the working tree (CIFP-C05) and the stream of the warnings (CIFP-C10).

### Ownership Resolution

| Contract                                                                                              | .feature Rule                                                                                                     | Owner   | Rationale                                             |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------- |
| CIF-05-CT-01: the counting rules of the plan                                                          | counter-ids-fitting.feature#next-id --plan-seed prints one seed command from the highest number of each ID prefix | ST-0376 | introduces the counting                               |
| CIF-05-IT-01: every local and remote-tracking branch, one command, exit 0, no ref changed             | counter-ids-fitting.feature#next-id --plan-seed prints one seed command from the highest number of each ID prefix | ST-0376 | introduces the mode                                   |
| CIF-06-CT-01: the classification of a file name                                                       | counter-ids-fitting.feature#next-id --plan-seed counts an old file name by its number and warns about it          | ST-0376 | introduces the name match                             |
| CIF-06-IT-01: the warning for `ATAM-0014-some-title.md` only                                          | counter-ids-fitting.feature#next-id --plan-seed counts an old file name by its number and warns about it          | ST-0376 | introduces the warnings                               |
| CIF-07-IT-01 to CIF-07-IT-03: in use, no remote, unreachable remote                                   | counter-ids-fitting.feature#next-id --plan-seed checks the remote before it plans a seed                          | ST-0376 | introduces the remote check of the mode               |
| CIF-01-IT-01: the printed command, run as printed, creates the counter and the next claim continues   | counter-ids-fitting.feature#User confirms the seed of the counter in a fitting step                               | ST-0376 | first to make the printed command runnable (CIFP-C02) |
| CIF-03-IT-01: an empty repository gets `next-id --seed 0`, and the first claim prints `ST-0001`       | counter-ids-fitting.feature#User walks the seed step in a greenfield project                                      | ST-0376 | first to print the empty seed (CIFP-C02)              |
| CIF-01-LN-01, CIF-01-LN-02: step 4 after step 3, and what VIRGIL does in it                           | counter-ids-fitting.feature#User confirms the seed of the counter in a fitting step                               | ST-0377 | introduces the step                                   |
| CIF-03-LN-01: a greenfield project walks step 0 and step 4                                            | counter-ids-fitting.feature#User walks the seed step in a greenfield project                                      | ST-0377 | introduces the step                                   |
| CIF-04-CT-01: `_fitting_status` with six keys                                                         | counter-ids-fitting.feature#User sees the fitting finished only when all six fitting keys are true                | ST-0377 | introduces the sixth key                              |
| CIF-04-LN-01: the four orientation files list six keys                                                | counter-ids-fitting.feature#User sees the fitting finished only when all six fitting keys are true                | ST-0377 | introduces the sixth key                              |
| CIF-13-CT-01: `init-factory` reads with `git ls-remote` only                                          | counter-ids-fitting.feature#init-factory derives counter_seeded from the remote that next-id uses                 | ST-0378 | introduces the derivation                             |
| CIF-13-IT-01 to CIF-13-IT-03: the five rows and greenfield, no ref changed, unreachable keeps the key | counter-ids-fitting.feature#init-factory derives counter_seeded from the remote that next-id uses                 | ST-0378 | introduces the derivation                             |

## E2: Keep the counter in the project's own repository until origin exists

### Why this EPIC exists

A project without `origin` cannot seed, so every ID claim fails and every producer stops. This EPIC lets the project's own `.git` hold the counter, which all worktrees and local clones share. The git setting `agent-factory.counterRemote` points `next-id` at it. Once `origin` exists, `next-id --move-to-origin` carries the counter there without handing out a number twice, and refuses when `origin` already holds a counter, so a second counter shows.

### Actor Goals

- VIRGIL points next-id at the project's own repository when origin is missing
- ID Producer claims an ID from the local counter in a project without origin
- next-id --move-to-origin moves the local counter to an origin without a counter
- next-id --move-to-origin leaves both counters as they are when origin holds one or the push fails
- next-id --move-to-origin hands out no number twice while ID claims run during the move
- VIRGIL offers to move a local counter to origin at the session start

### Demo

1. Create the project `/tmp/demo` with `git init` and no `origin`, and a second worktree `/tmp/demo-feature`.
2. Walk fitting step 4 in `/tmp/demo-feature`. VIRGIL sets `agent-factory.counterRemote` to `/tmp/demo`, runs `next-id --plan-seed`, shows `next-id --seed 0`, and runs it after the User confirms.
3. In `/tmp/demo-feature`, run `next-id ST`. It prints `ST-0001`. In `/tmp/demo`, run `next-id ST`. It prints `ST-0002`.
4. Add `origin` as a new local bare repository `/tmp/demo-origin.git` and start a session. VIRGIL offers to move the counter. Confirm.
5. VIRGIL runs `next-id --move-to-origin`. `/tmp/demo-origin.git` holds `refs/ids/counters`, the local counter holds the marker `moved=/tmp/demo-origin.git`, and the setting is gone. `next-id ST` prints `ST-0003`.
6. In a local clone `/tmp/demo-clone` whose `origin` is `/tmp/demo`, run `next-id ST`. It exits non-zero, names `/tmp/demo-origin.git` as the remote that holds the counter, and does not mention `--seed`.

### Scope

**In:**

- The remote order of `next-id` for a claim, a seed, and `--plan-seed`: `--remote`, then `agent-factory.counterRemote`, then `origin` (BR-096).
- The no-`origin` branch of step 4 in `virgil.md`: VIRGIL sets the setting to the parent of `git rev-parse --git-common-dir` before `--plan-seed`.
- `next-id --move-to-origin`: the read of C, the marker with a lease on C, the create-only push, the removal of the setting, and the restore of C when the push fails (BR-102). Every git call runs without prompts and with the time limit (CIFP-C09).
- The marker: a claim and `--plan-seed` that read it fail and name its remote, never `--seed` (BR-097).
- The collision: a counter on `origin` refuses the move, and the message names both counters with their lines (CIFP-C15).
- A move without the setting, `origin`, or a local counter changes nothing and names the missing piece (CIFP-C16).
- The race: a claim before the marker makes the move read again, at most ten times (BR-103, CIFP-C09).
- The interrupted move: a second move takes C from the marker's parent and finishes (DEC-14).
- The offer in `session-menu.md` and the report of a collision (BR-106, CIFP-C07).

**Out:**

- How a human resolves a collision (PROP-08).
- Any change to `block-dangerous-git.sh`. A test checks that it lets the move pass.

### Dependencies

E1: ST-0376 for `--plan-seed`, and ST-0377 for step 4.

### Boundaries

- Script: `packages/factory/scripts/next-id` (`resolve_remote`, `RemoteCounter.read`, the new move; components **next-id**, **Counter Port** `move`, **Git-Ref Adapter**)
- Local ref: `refs/ids/counters` in the `.git` of the project's main repository; git setting `agent-factory.counterRemote` in `.git/config`
- Agent: `packages/factory/agents/virgil.md` § Fitting, step 4; menu: `packages/factory/config/session-menu.md`
- Hook: `packages/factory/config/hooks/block-dangerous-git.sh` (read, not changed)
- Contracts: [interface-contracts.md § next-id](../docs/spec/interface-contracts.md#packagesfactoryscriptsnext-id), [§ Marker commit message](../docs/spec/interface-contracts.md#marker-commit-message), [§ `next-id --move-to-origin`](../docs/spec/interface-contracts.md#next-id---move-to-origin)
- Rules: BR-096, BR-097, BR-102, BR-103, BR-106; runtime: [Move Lifecycle](../docs/spec/state-machines.md#move-lifecycle), arc42 6.16 and 6.16.1, QS-22, QS-23
- Tests: `tests/factory/` (extend `test_next_id.py`, `test_next_id_plan_seed.py`, `test_fitting_text.py`, `test_block_dangerous_git.py`; new `test_next_id_move.py`)

### Domain Rules

- One project has one counter at a time: the local counter or the counter on `origin`.
- The setting exists only while the counter is local.
- A clone without `origin` and without the setting never starts a counter by accident.
- No ID claim lands on the local counter after the marker.
- A move never overwrites a counter on `origin`.
- A message that reads a marker never advises a seed.
- An interrupted move loses no claimed number.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                                                  | Tier     | Size | Goal                                                                                                                                                                                | Basis                                                                                                                                                                              |
| ------- | --------------------------------------------------------------------------- | -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0379 | Seed and claim IDs from the project's own repository without origin         | standard | M    | In a project without `origin`, step 4 seeds the counter in the project's own `.git`, and every worktree claims from it; a clone without the setting still fails and names `origin`. | `resolve_remote` reads `--remote`, then `origin`. Step 4 of ST-0377 has no branch for a missing `origin`. Adds the setting to the order and the branch to step 4.                  |
| ST-0380 | Move the local counter to origin, or see why the move was refused           | strong   | L    | The User runs `next-id --move-to-origin` and the counter moves to an empty `origin`, or the move changes nothing and names the reason; a claim on the marker names the new remote.  | No move exists, and `RemoteCounter.read` knows no marker. Adds the move, the marker, the restore, the collision message, and the marker failure for claims and `--plan-seed`.      |
| ST-0381 | Keep every number unique when claims run during a move or a move is cut off | strong   | M    | A claim that lands before the marker reaches `origin` with the move, and a second move after a cut-off finishes the first without a seed.                                           | ST-0380 sets the marker with a lease on C and stops on a stale lease. Adds the restart with its limit, the resume from the marker's parent, and the forced race and cut-off tests. |
| ST-0382 | Accept VIRGIL's offer to move the counter at the session start              | standard | S    | When the setting is set and `origin` exists, VIRGIL offers the move at the session start, runs it after the User confirms, and reports a collision by naming both counters.         | `session-menu.md` has no counter check. The hook lets `next-id` commands pass, untested for the move. Adds the check, the report, and the hook test.                               |

### Testability Assessment

The goals of `next-id` have observable results: the exit code and messages, the SHA and message of `refs/ids/counters` in the project's `.git` and in the bare repository, the parent of the marker, and the output of `git config agent-factory.counterRemote`. Tests run `next-id` as a subprocess in a project, its second worktree, and a local clone, with a made-up `origin` URL rewritten to a local bare repository by `url.<path>.insteadOf`. The race and the cut-off need a seam: the move must keep its read of the local counter and its push as functions that a test wraps with `load_script`, as the QA strategy asks. The offer is agent text, so a text test checks `session-menu.md`; CIFP-C07 unblocks that test. The restart limit and the cut-off have no Test ID yet (CIFP-C18).

### Ownership Resolution

| Contract                                                                                  | .feature Rule                                                                                                                 | Owner   | Rationale                                       |
| ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------- |
| CIF-08-CT-01: the order `--remote`, setting, `origin`                                     | counter-ids-fitting.feature#ID Producer claims an ID from the local counter in a project without origin                       | ST-0379 | introduces the setting in the order             |
| CIF-08-IT-01 to CIF-08-IT-03: the local claim, three counters, no `origin` and no setting | counter-ids-fitting.feature#ID Producer claims an ID from the local counter in a project without origin                       | ST-0379 | introduces the local counter                    |
| CIF-02-LN-01: `virgil.md` sets the setting before `--plan-seed`                           | counter-ids-fitting.feature#VIRGIL points next-id at the project's own repository when origin is missing                      | ST-0379 | introduces the no-`origin` branch               |
| CIF-02-IT-01: the seed lands in the main `.git`, and a second worktree claims             | counter-ids-fitting.feature#VIRGIL points next-id at the project's own repository when origin is missing                      | ST-0379 | introduces the local counter                    |
| CIF-10-CT-01: the marker message and its reader                                           | counter-ids-fitting.feature#next-id --move-to-origin moves the local counter to an origin without a counter                   | ST-0380 | introduces the marker                           |
| CIF-10-IT-01: the move to an empty `origin`                                               | counter-ids-fitting.feature#next-id --move-to-origin moves the local counter to an origin without a counter                   | ST-0380 | introduces the move                             |
| CIF-11-IT-01, CIF-11-IT-02: the collision and the refused push                            | counter-ids-fitting.feature#next-id --move-to-origin leaves both counters as they are when origin holds one or the push fails | ST-0380 | introduces the create-only push and the restore |
| CIF-08-IT-04: a claim in a local clone reads the marker                                   | counter-ids-fitting.feature#ID Producer claims an ID from the local counter in a project without origin                       | ST-0380 | introduces the marker                           |
| CIF-07-IT-04: `--plan-seed` reads the marker                                              | counter-ids-fitting.feature#next-id --plan-seed checks the remote before it plans a seed                                      | ST-0380 | introduces the marker                           |
| CIF-12-IT-02: a claim after the marker fails                                              | counter-ids-fitting.feature#next-id --move-to-origin hands out no number twice while ID claims run during the move            | ST-0380 | first to make the marker refuse a claim         |
| CIF-12-IT-01: a claim between the read and the marker makes the move read again           | counter-ids-fitting.feature#next-id --move-to-origin hands out no number twice while ID claims run during the move            | ST-0381 | introduces the restart                          |
| No Test ID: ten restarts end the move; a second move finishes a cut-off move (CIFP-C18)   | counter-ids-fitting.feature#next-id --move-to-origin hands out no number twice while ID claims run during the move            | ST-0381 | introduces the limit and the resume             |
| CIF-09-LN-01: `session-menu.md` offers the move and reports a collision                   | counter-ids-fitting.feature#VIRGIL offers to move a local counter to origin at the session start                              | ST-0382 | introduces the offer                            |
| CIF-09-IT-01: the guardrail hook exits 0 for `next-id --move-to-origin`                   | counter-ids-fitting.feature#VIRGIL offers to move a local counter to origin at the session start                              | ST-0382 | first story whose agent runs the move           |

## E3: Name the one ID prefix at each step that creates an artifact

### Why this EPIC exists

Today `finding-format.md` tells a reviewer to claim "`next-id <TAG>`" and lists the tags in a table, so the reviewer must pick its prefix. A wrong pick does not fail: `next-id BUG` hands out a valid number for a finding that should be `FAGAN`, and that number is gone. This EPIC writes the literal claim, such as `next-id FAGAN`, into each file that creates an indexed artifact, collects all twelve prefixes in one table, and adds a text test that fails when a file or the table drifts from `next-id`.

### Actor Goals

- ID Producer names the literal ID prefix at each step that creates an indexed artifact
- ID Producer that adds a todo entry names next-id T
- User finds every ID prefix in one table in id-prefixes.md
- User sees the text test fail when an ID producer or the prefix table drifts from next-id

### Demo

1. Open `packages/factory/rulebooks/conventions/id-prefixes.md`. It lists twelve prefixes. The `RECON` row names a drift finding and `reconcile-spec` and `reconciliation-agent`.
2. In a scratch project whose `origin` is a seeded local bare repository, ask the agent to run `fagan-review` on a file with a defect. The agent runs `next-id FAGAN` and writes the finding under the printed ID.
3. Ask the agent to run `reconcile-spec` on a project with one drifted rule and one code defect. The agent runs `next-id RECON` for the drift and `next-id BUG` for the defect.
4. Ask the agent to run `retrospective`. It runs `next-id T` for each action item and follows `todo-format.md`.
5. Delete `next-id FAGAN` from a copy of `fagan-review/SKILL.md` and run the commit hooks. The text test fails and names the file and `FAGAN`.

### Scope

**In:**

- The new convention `id-prefixes.md` with one row per prefix of `next-id`: the prefix, the kind of artifact, and the ID producer files (BR-108).
- Pointers to it in `rules.md`, `branching-policy.md`, and `finding-format.md`. `finding-format.md` keeps one row per finding prefix with the review that files it and gains the `RECON` row.
- The literal `next-id <PREFIX>` at each creating step of the nineteen files in the proposal's table, one prefix per kind of artifact (BR-107, DEC-10). `create-backlog-stories` names `next-id ST`, and `retrospective` names `next-id T` and `next-id ST`.
- `next-id T` and a pointer to `todo-format.md` at every other step that adds a `todo.md` entry.
- The text checker: a function that takes the paths it reads and fails on a dropped prefix, a todo writer without `next-id T`, or a table that differs from `PREFIXES` (BR-108).
- The follow-ups of CIFP-C14.

**Out:**

- `docs/spec/work/todos.md` and its writers (SPEC-0068, T-0008).
- A check of new file names. No tool in the proposal checks that a new file carries only the prefix and the number (DEC-12).
- `create-backlog-slice-story`, which keeps its letter scan.

### Dependencies

None. E3 changes only Factory text and its text tests.

### Boundaries

- New convention: `packages/factory/rulebooks/conventions/id-prefixes.md`
- Rulebooks: `packages/factory/rulebooks/rules.md`, `rulebooks/conventions/branching-policy.md`, `rulebooks/conventions/finding-format.md`, `rulebooks/conventions/todo-format.md`
- ID producers: the files of the proposal's [§ Each requestor names its prefix](../docs/proposals/counter-ids-fitting.md#each-requestor-names-its-prefix) and every file that points to `todo-format.md` at a step that adds an entry
- Contract: [interface-contracts.md § `id-prefixes.md` table](../docs/spec/interface-contracts.md#id-prefixesmd-table)
- Rules: BR-107, BR-108
- Catalog: `packages/factory/INDEX.yaml`
- Tests: `tests/factory/test_counter_ids_text.py` (extend); QA strategy of counter-ids: `docs/spec/work/counter-ids-qa-strategy.md` (CIFP-C14)

### Domain Rules

- The kind of artifact decides the prefix, not the file.
- A file that creates two kinds names one prefix at each of the two steps.
- No file asks an agent to choose a prefix from a list.
- A file that only links to `todo.md` is no ID producer.
- A thirteenth prefix means two changes: the list in `next-id` and the table in `id-prefixes.md`.

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                        | Tier     | Size | Goal                                                                                                                                                                                        | Basis                                                                                                                                                                            |
| ------- | ----------------------------------------------------------------- | -------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0383 | Find every ID prefix and its producers in id-prefixes.md          | standard | S    | A User or agent finds all twelve prefixes, with their kind and producer files, in one table that the three rulebooks point to, and the text test fails when the table and `next-id` differ. | `finding-format.md` lists nine tags without `RECON` in its claim line and names `next-id <TAG>`. No table of all prefixes exists. Adds the table, the pointers, and the checker. |
| ST-0384 | Claim the literal ID prefix at each step that creates an artifact | standard | L    | An agent that follows any of the nineteen ID producer files runs `next-id` with the one prefix of the artifact it creates, and the text test fails when a file drops it.                    | `create-backlog`, `write-adr`, `bug-fix`, and `todo-format` name their prefix. The review files name none. Adds the literal claim to each file and the dropped-prefix case.      |
| ST-0385 | Name next-id T at every step that adds a todo entry               | economy  | S    | Every file that points to `todo-format.md` at a step that adds an entry names `next-id T`, and the text test fails for a todo writer without it.                                            | `create-backlog-make-concrete` and `report-format.md` point to `todo-format.md` without `next-id T`. Adds the claim and the pointer-based case of the checker.                   |

### Testability Assessment

The goals are text rules, so the observable result is the text of each file, read by pytest tests in `tests/factory/test_counter_ids_text.py`, and the failure of the checker on broken copies in `tmp_path`. The checker takes the paths it reads, so no test edits a file of `packages/factory/`. One red flag remains: a text test can check that a file holds `next-id FAGAN`, but not that the call stands at the step that creates the finding. The story review checks the place, and the demo through an agent session shows it.

### Ownership Resolution

| Contract                                                                                                        | .feature Rule                                                                                                        | Owner   | Rationale                         |
| --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------- | --------------------------------- |
| CIF-16-LN-01: twelve rows, each with kind and producer files that exist                                         | counter-ids-fitting.feature#User finds every ID prefix in one table in id-prefixes.md                                | ST-0383 | introduces the table              |
| CIF-16-LN-02: the three rulebooks point to `id-prefixes.md`                                                     | counter-ids-fitting.feature#User finds every ID prefix in one table in id-prefixes.md                                | ST-0383 | introduces the pointers           |
| CIF-16-LN-03: `finding-format.md` keeps the review per prefix and a `RECON` row                                 | counter-ids-fitting.feature#User finds every ID prefix in one table in id-prefixes.md                                | ST-0383 | changes `finding-format.md`       |
| CIF-17-CT-01: the checker fails on a dropped prefix, a todo writer without `next-id T`, or a table that differs | counter-ids-fitting.feature#User sees the text test fail when an ID producer or the prefix table drifts from next-id | ST-0383 | introduces the checker (CIFP-C13) |
| CIF-14-LN-01: each of the 22 producer rows names `next-id <PREFIX>`, none `next-id <TAG>`                       | counter-ids-fitting.feature#ID Producer names the literal ID prefix at each step that creates an indexed artifact    | ST-0384 | introduces the literal claims     |
| CIF-14-LN-02: `reconcile-spec` names `next-id RECON` and `next-id BUG` at two steps                             | counter-ids-fitting.feature#ID Producer names the literal ID prefix at each step that creates an indexed artifact    | ST-0384 | introduces the literal claims     |
| CIF-15-LN-01: every todo writer found by the pointer names `next-id T`                                          | counter-ids-fitting.feature#ID Producer that adds a todo entry names next-id T                                       | ST-0385 | introduces the pointer rule       |
| CIF-15-LN-02: `write-prd` needs no `next-id T`                                                                  | counter-ids-fitting.feature#ID Producer that adds a todo entry names next-id T                                       | ST-0385 | introduces the pointer rule       |
