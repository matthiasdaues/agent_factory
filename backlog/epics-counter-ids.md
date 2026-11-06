---
scope: global
---

# EPICs — Counter IDs

Proposal trace: [counter-ids.md](../docs/proposals/counter-ids.md)
Specification trace: [counter-ids.feature](../docs/spec/features/counter-ids.feature), [gaps report](../docs/spec/work/counter-ids-gaps.md), [interface-contracts.md § Counter IDs Contracts](../docs/spec/interface-contracts.md#counter-ids-contracts), [validation-rules.md § Counter IDs](../docs/spec/validation-rules.md#counter-ids-next-id-br-068br-078), [state-machines.md § Claim Lifecycle](../docs/spec/state-machines.md#claim-lifecycle)
Architecture trace: [ADR-0031](../docs/adr/0031-ids-come-from-one-git-ref-with-leased-pushes.md), [ADR-0032](../docs/adr/0032-agents-push-the-claim-ref-through-next-id.md), [arc42 § 5.11](../docs/arc42/05_building_block_view.md#511-level-2-component-view----id-allocation), [arc42 § 6.15](../docs/arc42/06_runtime_view.md#615-id-claim-with-a-stale-lease), [arc42 § 8.18](../docs/arc42/08_crosscutting_concepts.md#818-id-allocation), [QS-18 to QS-21](../docs/arc42/10_quality_requirements.md#qs-18-no-id-is-handed-out-twice)
QA strategy trace: [counter-ids-qa-strategy.md](../docs/spec/work/counter-ids-qa-strategy.md)

Dependency order: E1 starts alone with ST-0368. E2 and E3 start when ST-0368 is merged. Inside E1, ST-0369 and ST-0370 both wait for ST-0368, and ST-0371 waits for ST-0369. Inside E2, ST-0372 waits for ST-0374, because a producer may tell an agent to push the claim only after `rules.md` allows that push.

## Story waves

| Wave | Stories                                     | Merge order inside the wave                                                                                                                                                                                  |
| ---- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W1   | ST-0368                                     | —                                                                                                                                                                                                            |
| W2   | ST-0369, ST-0370, ST-0373, ST-0374, ST-0375 | ST-0369, then ST-0370, then ST-0373, because all three edit `tests/factory/test_next_id.py`. ST-0374 before ST-0373, because both edit `rules.md`. ST-0373 and ST-0374 also share `test_counter_ids_text.py` |
| W3   | ST-0371, ST-0372                            | any                                                                                                                                                                                                          |

ST-0371 is a manual check by the stakeholder. An agent cannot run it, because it pushes to GitHub.

Every story carries `quality-gates: []`, as the recent stories do, because the installed Factory is not yet updated for gates.

## Terms used in every EPIC

The [glossary](../docs/spec/glossary.md) defines each term. A short reminder:

- **Counter.** The ref `refs/ids/counters` on the remote `origin`. It points at the claim commit.
- **Claim commit.** A commit with no parent on the empty tree. Its message holds `start=<number>`, one line per ID prefix with the highest number claimed so far, such as `ST=1012`, and a random token line.
- **ID claim.** One call of `next-id <PREFIX>`. It reads the counter, raises the line of the prefix by one, pushes a new claim commit with a lease on the old SHA, and prints the ID.
- **ID prefix.** One of `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, `T`, and `ADR`. The list lives in `next-id`.
- **Seed.** `next-id --seed <number>`. It creates the counter once and refuses when the counter exists.
- **Stale lease.** The remote refuses a push because the ref no longer holds the SHA the push expected. git reports it as `stale info` or as `cannot lock ref … is at <sha> but expected <sha>`.
- **ID producer.** A skill, agent, convention, or playbook that tells its reader how to number a new indexed artifact.
- **Local bare repository.** A repository made with `git init --bare` in a temporary directory. Every test and every demo uses one as the remote, except ST-0371.

## Rules that hold for every EPIC

- Source edits go to `packages/factory/`, never to `.agent-factory/factory/`.
- No test and no demo, except ST-0371, touches the project's real remote. Tests pass a local bare repository as `origin` of a temporary clone or with `--remote`.
- `index-lint --check` passes after every story that changes an agent, skill, convention, or playbook. Such a story regenerates `INDEX.yaml` in the same commit (`Gap: CID-G08`).
- Tests carry `@pytest.mark.spec("CID-NN-XX-NN")` with the Test ID of their row in the [QA strategy](../docs/spec/work/counter-ids-qa-strategy.md#contract-owners). ST-0368 adds `CID-*` to the `spec` marker description in `pyproject.toml`.
- Agents do not run `uv run pytest` by hand, because the guardrail hook blocks it. The tests run through the commit hooks.
- No story plans a deferred item: other counter adapters, renaming existing IDs, numbers above 9999, or `next-id` for split-story letters.
- No story changes the guardrail hook `block-dangerous-git.sh` (DEC-16, DEC-22).

## Governance and risk

The proposal declares `assurance: elevated` and three risk domains. Each one has stories that carry it:

| Risk domain      | What goes wrong                                                                | Stories that guard it                                                                 |
| ---------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `data_integrity` | Two branches get the same ID, or a seed changes a counter in use               | ST-0368 (create-only seed, kept lines), ST-0369 (lease and retry, race test), ST-0371 |
| `operations`     | A claim hangs, retries a refusal that will not go away, or fails without cause | ST-0369 (one push on a refusal), ST-0370 (named causes, time limit), ST-0375          |
| `security`       | An agent pushes outside `next-id`, or a claim waits on a credential prompt     | ST-0370 (no prompts, BR-076), ST-0374 (the push exception as ADR-0032 states it)      |

Every story whose risk domain is `data_integrity` has `risk_level: high`.

## Choices made without the stakeholder

The brief ran in full auto mode. Each phase that asks for approval took the recommended option below. The stakeholder approves the backlog at playbook step 3.4.

| ID       | Phase           | Choice                                                                                                                                                                                                                    | Reason                                                                                                                                                                 |
| -------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CIDP-C01 | 1, EPIC slicing | Three EPICs: the `next-id` script itself (E1), the Factory files that tell agents to use it (E2), and the `init-factory` message (E3).                                                                                    | Each EPIC is one journey of the User. E2 and E3 change different files and run in parallel once `next-id` exists.                                                      |
| CIDP-C02 | 3, story slices | ST-0368 holds the seed and the claim together.                                                                                                                                                                            | A claim needs a seeded counter, and the User sees the result of a seed only through the next claim. Neither half can be shown alone.                                   |
| CIDP-C03 | 3, story slices | The stale-lease retry, the ten-lease limit, and the one-push refusal go to ST-0369. The remote failures and the prompt and time limits of BR-076 go to ST-0370.                                                           | ST-0369 is the outcome "parallel claims get different IDs". ST-0370 is the outcome "a failed claim names its cause". Both build on ST-0368 and do not need each other. |
| CIDP-C04 | 3, story slices | ST-0371 is a separate story with the stakeholder as actor. Its demo is the GitHub race run.                                                                                                                               | The brief asks for a story or a step that the stakeholder runs. A separate story keeps ST-0369 closable by a developer agent.                                          |
| CIDP-C05 | 3, story slices | CID-G01: ST-0369 tests ten stale leases, as the feature file states, with a `pre-receive` hook that moves the ref before each push. If git refuses that ref update, the test uses a `git` wrapper on `PATH` (`CID-QG01`). | The brief settles this. The proposal's `pre-receive` refusal is not a stale lease under DEC-23.                                                                        |
| CIDP-C06 | 3, story slices | QS-19 (eight parallel claims) is covered by a test in ST-0369. The QA strategy holds no row for it, so the story names the test without a Test ID.                                                                        | The brief asks to cover it or name the gap. The test-strategy agent owns the QA strategy and adds the row. Until then the gap is named here and in ST-0369.            |
| CIDP-C07 | 3, story slices | BR-076 (no prompts, 30 seconds per git call) is covered by ST-0370. The QA strategy holds no row for it either.                                                                                                           | BR-076 came from ATAM-0012 after the QA strategy. Same handling as CIDP-C06.                                                                                           |
| CIDP-C08 | 3, story slices | ST-0372 depends on ST-0374.                                                                                                                                                                                               | In manual mode, a producer that tells an agent to run `next-id` makes the agent push. `rules.md` must allow that push first.                                           |
| CIDP-C09 | 3, story slices | ST-0374 follows ADR-0032: a push outside `next-id` can set a line back, so the rule that agents claim only through `next-id` guards the counter.                                                                          | The brief settles this. DEC-22 and CID-G07 say such a push can only leave a gap, which ADR-0032 and arc42 8.18 correct.                                                |
| CIDP-C10 | 4, stories      | The open gaps CID-G02 to CID-G06 go into the Resolve Before Implementation sections of ST-0368 and ST-0375. The tests assert nothing on those cases, so the stories do not wait on the answers.                           | The proposal and the specification leave them open. A test that fixes one would decide for the stakeholder.                                                            |
| CIDP-C11 | 4, stories      | No story changes `docs/proposals/manual-mode-gates.md`, although the proposal lists it under `impact.boundaries`.                                                                                                         | No Completion Criterion names it, and its DEC-10 already takes IDs from this counter. The brief forbids changes outside the new backlog files.                         |

## Open items for the stakeholder

These are open, and the backlog plans around them:

- **Seed this project's own `origin`.** After E2 merges into `dev`, every producer in this repository runs `next-id`. The stakeholder runs `next-id --seed <number> ADR=<n>` once on `origin`, with a number above the highest ID in use, before the first session creates an indexed artifact. `init-factory` (ST-0375) prints the reminder. No story seeds, because the proposal leaves the seed to a person (DEC-17).
- **The race run on GitHub** (ST-0371) needs a scratch GitHub repository, because the race harness seeds `refs/ids/counters` and cannot run on a counter in use (`CID-QG03`).
- **The gaps CID-G02 to CID-G06** (CIDP-C10).

## E1: Claim unique IDs from one counter on the remote

### Why this EPIC exists

Today each session takes the next free number by looking at the files it can see. Two sessions on two branches see the same highest number, so both create `ST-0346`. Without a counter that every clone reaches, no branch can safely create a story, finding, todo entry, or ADR. This EPIC ships the script `next-id`: the User seeds the counter once, and every ID claim then returns a number that no other claim returns, or fails and names why.

### Actor Goals

- User seeds the counter once for a project
- User gets the next ID of an ID prefix from an ID claim
- User gets different IDs from two ID claims at the same time
- User sees a failed ID claim stop and name its reason
- User makes an ID claim on a named remote without a clone
- User keeps the clone unchanged by an ID claim
- Stakeholder checks the ID claim against GitHub

### Demo

1. Create a local bare repository at `/tmp/remote.git` and clone it to `/tmp/clone`.
2. In `/tmp/clone`, run `next-id --seed 1000 ADR=6`. It prints the lines `start=1000` and `ADR=0006` and exits `0`.
3. Run the seed again. It exits non-zero and names the remote and `refs/ids/counters`.
4. Run `next-id ST`. It prints `ST-1001`. Run `next-id ADR`. It prints `ADR-0007`.
5. Run `next-id XX`. It exits non-zero, prints no ID, and names `XX` and the list of ID prefixes.
6. Run `uv run python tests/factory/next_id_race.py --rounds 20`. It reports 40 different IDs and no skipped number.
7. Point `origin` at a URL that does not answer, and run `next-id ST`. It exits non-zero, prints no ID, and names the remote and git's error.
8. The stakeholder runs the race harness with `--remote` against a scratch GitHub repository. No number comes out twice.

### Scope

**In:**

- The script `packages/factory/scripts/next-id`, in Python like `init-factory` and `backlog-lint`. It holds the ID prefix list, the counter port with `claim` and `seed`, and the git-ref adapter (arc42 5.11).
- The seed: argument check before the remote is contacted (BR-069), four-digit padding (BR-070), and a push with the create-only lease, so a seed never changes a counter in use (BR-073).
- The claim in a throwaway bare repository that `next-id` deletes at every exit (BR-075). The claim raises the line of its prefix, gives a prefix without a line `start` plus one, keeps every other line, and writes a new token (BR-071). Claim commits carry the fixed identity `next-id <next-id@agent-factory.invalid>`.
- The remote from `--remote <url>`, or else from `git remote get-url origin`, so the clone's URL rewrites apply (BR-074).
- The leased push, the retry after a random wait of 0.1 to 1 second on a stale lease only, and the end after ten stale leases in a row (BR-072). Any other refusal ends the claim after one push.
- Each failure of the claim error table in [interface-contracts.md § next-id](../docs/spec/interface-contracts.md#packagesfactoryscriptsnext-id): exit non-zero, nothing on standard output, and the named cause on standard error.
- Git calls of a claim without prompts and with a time limit of 30 seconds each (BR-076).
- The race harness `tests/factory/next_id_race.py`, which the race test imports and the stakeholder runs against GitHub.

**Out:**

- Counter adapters for other backends, numbers above 9999, and renaming existing IDs. The proposal defers them.
- The Factory files that tell agents to run `next-id` (E2) and the `init-factory` message (E3).
- A config file. The counter needs none (DEC-18).

### Dependencies

None. E1 is the base of E2 and E3.

### Boundaries

- New script: `packages/factory/scripts/next-id` (components **next-id**, **Counter Port**, **Git-Ref Adapter** of arc42 5.11)
- Remote ref: `refs/ids/counters` on the remote
- Contracts: [interface-contracts.md § next-id](../docs/spec/interface-contracts.md#packagesfactoryscriptsnext-id), [§ Claim commit message](../docs/spec/interface-contracts.md#claim-commit-message)
- Rules: BR-068 to BR-076 in [validation-rules.md](../docs/spec/validation-rules.md#counter-ids-next-id-br-068br-078)
- Runtime: [Claim Lifecycle](../docs/spec/state-machines.md#claim-lifecycle), [arc42 § 6.15](../docs/arc42/06_runtime_view.md#615-id-claim-with-a-stale-lease)
- Tests: `tests/factory/` (new `test_next_id.py`, `test_next_id_race.py`, `next_id_race.py`), `pyproject.toml` (the `spec` marker description)

### Domain Rules

- A number for an ID prefix comes only from an ID claim on the remote.
- A failed claim stops and never guesses a number. It prints no ID.
- A seed never changes an existing counter.
- An ID claim keeps the line of every other ID prefix.
- Only a stale lease leads to a retry.
- An ID claim adds no ref and no object to the clone.
- Existing IDs keep their names.

### Size

4 stories.

### Building-Block Inventory

| Story   | Capability                                              | Tier     | Size | Goal                                                                                                                                                                       | Basis                                                                                                                                         |
| ------- | ------------------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-0368 | Seed a project's counter and claim the next ID from it  | strong   | L    | The User seeds the counter once, and each `next-id <PREFIX>` then prints the next ID of that prefix, on `origin` or on a `--remote`, and leaves the clone unchanged.       | No `next-id` exists. `poc/counters/ref-claim-race.sh` shows the lease. Adds the script with the seed, the claim, and the prefix check.        |
| ST-0369 | Get different IDs from claims that run at the same time | strong   | M    | Two or eight parallel ID claims all exit `0` with different IDs and no skipped number, and a claim that the remote refuses for another reason ends after one push.         | ST-0368 pushes once and fails on any refusal. Adds the stale-lease check, the retry loop, the ten-lease limit, and the race harness.          |
| ST-0370 | See a failed ID claim stop and name its cause           | standard | M    | A claim on a missing counter, an unreachable remote, a refused fetch, or a clone without `origin` exits non-zero within a bounded time, prints no ID, and names its cause. | ST-0368 exits non-zero without an ID on these cases. Adds the named causes of the error table, the prompt-free git calls, and the time limit. |
| ST-0371 | Check the race on a GitHub repository                   | economy  | S    | The stakeholder runs the race harness against a scratch GitHub repository and sees that no number comes out twice.                                                         | ST-0369 ships the harness. Adds the run, its recorded output, and the cleanup of the scratch counter.                                         |

### Testability Assessment

Every goal produces an observable result: the exit code of `next-id`, its standard output and standard error, and the claim commit message on the bare repository, read with `git log -1 --format=%B refs/ids/counters`. Tests instrument `next-id` as a subprocess against local bare repositories, the clone's `git for-each-ref` and `git cat-file --batch-all-objects` output, `TMPDIR`, and `pre-receive` hooks in the bare repository. Contract tests import `next-id` with `load_script` and replace the port and `time.sleep`. Two red flags remain. The ten-stale-lease setup is unchecked on git 2.34 (`CID-QG01`), so ST-0369 checks it first and has a fallback. QS-19 and BR-076 have no row in the QA strategy (CIDP-C06, CIDP-C07). The GitHub race needs a person and a scratch repository.

### Ownership Resolution

| Contract                                                                                                        | .feature Rule                                                                   | Owner   | Rationale                                                  |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------- | ---------------------------------------------------------- |
| CID-01-CT-01: the seed argument check, padding, and messages (BR-069)                                           | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the seed                                        |
| CID-01-IT-01: the seed creates the counter, and the next claims print `ST-1001`, `BUG-1001`, `ADR-0007`         | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the seed and the claim                          |
| CID-01-IT-02: a seed on a counter in use fails and leaves the ref at the same SHA                               | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the create-only lease                           |
| CID-01-IT-03: a wrong seed argument creates no ref                                                              | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the seed argument check                         |
| CID-01-IT-04: two seeds at the same time leave one claim commit                                                 | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the create-only lease                           |
| CID-01-IT-05: a seed without a remote or on an unreachable remote names the cause                               | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the seed's remote lookup                        |
| CID-01-IT-06: a seed keeps the names of the existing IDs                                                        | counter-ids.feature#User seeds the counter once for a project                   | ST-0368 | introduces the seed                                        |
| CID-02-CT-01: the message rewrite raises one line and keeps the others                                          | counter-ids.feature#User gets the next ID of an ID prefix from an ID claim      | ST-0368 | introduces the claim                                       |
| CID-02-IT-01 to CID-02-IT-05: the claim output, all ten prefixes, the fixed identity, URL rewrites, the ID form | counter-ids.feature#User gets the next ID of an ID prefix from an ID claim      | ST-0368 | introduces the claim                                       |
| CID-04-CT-01: a prefix outside the list is refused before any remote is read                                    | counter-ids.feature#User sees a failed ID claim stop and name its reason        | ST-0368 | introduces the prefix list                                 |
| CID-05-IT-01, CID-05-IT-02: `--remote` claims on that remote, also outside a clone                              | counter-ids.feature#User makes an ID claim on a named remote without a clone    | ST-0368 | introduces the remote lookup                               |
| CID-06-IT-01, CID-06-IT-02: no new ref or object in the clone; the throwaway repository is gone at every exit   | counter-ids.feature#User keeps the clone unchanged by an ID claim               | ST-0368 | introduces the throwaway repository                        |
| CID-03-CT-01: the retry loop, the ten-lease limit, and one push on another refusal                              | counter-ids.feature#User gets different IDs from two ID claims at the same time | ST-0369 | introduces the retry loop                                  |
| CID-03-CT-02: the stale-lease check reads `stale info` and `cannot lock ref`                                    | counter-ids.feature#User gets different IDs from two ID claims at the same time | ST-0369 | introduces the stale-lease check                           |
| CID-03-IT-01: the race test, 20 rounds, 40 different IDs                                                        | counter-ids.feature#User gets different IDs from two ID claims at the same time | ST-0369 | introduces the race harness                                |
| CID-04-IT-01: ten stale leases end the claim and name `ST` and `1001`                                           | counter-ids.feature#User sees a failed ID claim stop and name its reason        | ST-0369 | introduces the ten-lease limit                             |
| CID-04-IT-02: a `read-only` refusal ends the claim after one push                                               | counter-ids.feature#User sees a failed ID claim stop and name its reason        | ST-0369 | introduces the split between stale lease and other refusal |
| CID-04-IT-03 to CID-04-IT-06: missing counter, unreachable remote, no `origin`, refused fetch                   | counter-ids.feature#User sees a failed ID claim stop and name its reason        | ST-0370 | introduces the named causes                                |
| CID-11-AC-01: the race on GitHub hands out no number twice                                                      | counter-ids.feature#Stakeholder checks the ID claim against GitHub              | ST-0371 | the stakeholder's run of the harness                       |

QS-19 (eight parallel claims, owned by ST-0369) and BR-076 (prompts and time limit, owned by ST-0370) have no Test ID yet (CIDP-C06, CIDP-C07).

## E2: Number every new indexed artifact with next-id on any branch

### Why this EPIC exists

`next-id` helps only when the Factory tells its agents to use it. Today five files tell their reader to scan for the highest number, and three files require every indexed artifact on `dev`. So a code review in manual mode cannot file a finding on the story branch. This EPIC changes those files: every ID producer runs `next-id`, an indexed artifact may live on any branch, and an agent may push the counter through `next-id` without waiting for the human.

### Actor Goals

- User gets every new indexed artifact numbered by next-id
- User commits an indexed artifact on any branch
- User lets an agent push the counter through next-id in both modes

### Demo

1. In a scratch project whose `origin` is a local bare repository seeded with `next-id --seed 1000 ADR=6`, the User asks the agent to record the decision "Counter ref on the remote" with `write-adr`.
2. The agent runs `next-id ADR`, which prints `ADR-0007`, and saves `docs/adr/0007-counter-ref-on-the-remote.md`. In manual mode, the agent does not ask the human to push.
3. On the branch `feature/counter-ids`, the User asks the agent to file a code-review finding. The agent runs `next-id FAGAN`, gets `FAGAN-1001`, and commits `docs/findings/FAGAN-1001.md` on that branch.
4. The User reads `rules.md` § Branching. It allows indexed artifacts on any branch, and § Dispatch states the claim push by `next-id` as the one exception to the human's pushes.

### Scope

**In:**

- The five ID producer files of the proposal's § Producers tell their reader to run `next-id <PREFIX>` and to stop when it fails. None tells its reader to scan for the highest number.
- `write-adr` keeps the file form `docs/adr/NNNN-short-title.md` with the number from `next-id ADR`.
- `create-backlog-slice-story` keeps its letter scan for split stories and names no `next-id`.
- `rules.md` § Branching, `branching-policy.md`, and `planning-agent.md` allow indexed artifacts on any branch.
- `rules.md` § Dispatch states the claim push by `next-id` as an exception for manual mode, and § Git workflow states it for both modes.
- A contract test shows that the guardrail hook lets `next-id` pass.

**Out:**

- Any change to the guardrail hook (DEC-16, DEC-22). T-0017 tracks its gap.
- `next-id` for split-story letters (deferred).
- The ticket adapters of `project-agent-flows.md`, which ship with that proposal.

### Dependencies

E1 (ST-0368).

### Boundaries

- ID producers: `packages/factory/skills/create-backlog/SKILL.md`, `packages/factory/rulebooks/conventions/finding-format.md`, `packages/factory/playbooks/bug-fix.md`, `packages/factory/rulebooks/conventions/todo-format.md`, `packages/factory/skills/write-adr/SKILL.md`
- Kept as it is: `packages/factory/skills/create-backlog-slice-story/SKILL.md`
- Branching rules: `packages/factory/rulebooks/rules.md` (§ Branching, § Dispatch, § Git workflow), `packages/factory/rulebooks/conventions/branching-policy.md`, `packages/factory/agents/planning-agent.md`
- Hook: `packages/factory/config/hooks/block-dangerous-git.sh` (read, not changed)
- Catalog: `packages/factory/INDEX.yaml`
- Tests: `tests/factory/` (new `test_counter_ids_text.py`), `tests/factory/test_block_dangerous_git.py` (extend), `tests/factory/test_next_id.py` (extend)

### Domain Rules

- Every new indexed artifact takes its number from `next-id`.
- A split story keeps its letter from a scan.
- A failed `next-id` stops the producer step. The agent reports the message and never picks a number by hand.
- Agents push the counter only through `next-id` (ADR-0032).

### Size

3 stories.

### Building-Block Inventory

| Story   | Capability                                                   | Tier     | Size | Goal                                                                                                                                                            | Basis                                                                                                                                |
| ------- | ------------------------------------------------------------ | -------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| ST-0372 | Number a new story, finding, todo entry, or ADR with next-id | standard | M    | An agent that follows any of the five ID producer files names the new artifact with the ID that `next-id` printed, and a split story keeps its letter.          | Each file tells its reader to scan for the highest number. Replaces the scan with the `next-id` call and adds the text test.         |
| ST-0373 | Commit an indexed artifact on the branch where it is made    | standard | S    | The User and the agents commit a new story or finding on any branch, and two sessions on two branches get different IDs for the same prefix.                    | `rules.md`, `branching-policy.md`, and `planning-agent.md` require indexed artifacts on `dev`. Replaces that rule.                   |
| ST-0374 | Let an agent claim an ID without waiting for a push          | standard | S    | In manual and automated mode, an agent runs `next-id` and gets its ID, because `rules.md` states the claim push as the one exception and the hook lets it pass. | `rules.md` § Dispatch gives the human every push. The hook already passes `next-id`, untested. Adds the exception and the hook test. |

### Testability Assessment

The goals of ST-0372 to ST-0374 are text rules, so the observable result is the text of each file, read by pytest tests that look for the `next-id` call and the absence of the scan and dev-only wording. Tests also instrument the guardrail hook's exit code on three command texts, and two clones of one bare repository on two branches that each run `next-id IMPL`. The demo through an agent session is a manual walk-through, not a test. No red flag remains, as long as the text tests check the rule each file states and not one exact sentence.

### Ownership Resolution

| Contract                                                                                         | .feature Rule                                                                         | Owner   | Rationale                                   |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- | ------- | ------------------------------------------- |
| CID-07-LN-01: each ID producer tells its reader to run `next-id`, and none scans                 | counter-ids.feature#User gets every new indexed artifact numbered by next-id          | ST-0372 | introduces the `next-id` call in the files  |
| CID-07-LN-02: `write-adr` keeps `docs/adr/NNNN-short-title.md`                                   | counter-ids.feature#User gets every new indexed artifact numbered by next-id          | ST-0372 | changes `write-adr`                         |
| CID-07-LN-03: `create-backlog-slice-story` keeps its letter scan                                 | counter-ids.feature#User gets every new indexed artifact numbered by next-id          | ST-0372 | first story that could change it by mistake |
| CID-08-LN-01: the three branching files allow indexed artifacts on any branch                    | counter-ids.feature#User commits an indexed artifact on any branch                    | ST-0373 | introduces the any-branch rule              |
| CID-08-IT-01: two clones on two branches get different `IMPL` IDs and commit on their own branch | counter-ids.feature#User commits an indexed artifact on any branch                    | ST-0373 | first story that states the two-branch case |
| CID-09-LN-01: `rules.md` § Dispatch and § Git workflow state the exception                       | counter-ids.feature#User lets an agent push the counter through next-id in both modes | ST-0374 | introduces the exception                    |
| CID-09-CT-01: the guardrail hook exits 0 on three `next-id` command texts                        | counter-ids.feature#User lets an agent push the counter through next-id in both modes | ST-0374 | first story that relies on the hook passing |

## E3: Learn from init-factory how to seed the counter

### Why this EPIC exists

After the Factory is installed, every producer runs `next-id`, and `next-id` fails until a person seeds the counter. A User who installs the Factory and does not know this sees the first story fail. This EPIC makes `init-factory` look for the counter on `origin` and tell the User what to do, without seeding and without stopping the install.

### Actor Goals

- User learns from init-factory how to seed the counter

### Demo

1. In a project whose `origin` is a local bare repository without `refs/ids/counters`, the User runs `init-factory`. It prints "run `next-id --seed <number>` with a number above your highest ID". `origin` still holds no counter.
2. The User removes `origin` and runs `init-factory` again. It prints "add the remote `origin`, then run `next-id --seed <number>`".
3. The User points `origin` at a URL that does not answer and runs `init-factory`. It prints a warning that names the remote, finishes the install, and exits `0`.
4. The User restores `origin` and runs `next-id --seed 1000`. The next `next-id ST` prints `ST-1001`.

### Scope

**In:**

- `init-factory` asks `origin` whether `refs/ids/counters` exists and prints one of the three messages of [interface-contracts.md § init-factory counter check](../docs/spec/interface-contracts.md#init-factory-counter-check).
- The install finishes in each case.

**Out:**

- Seeding from `init-factory` (DEC-17).
- An exit code for a missing counter or a missing `origin`, and any output when the counter exists (`Gap: CID-G02`).

### Dependencies

E1 (ST-0368), so the message names a command that exists.

### Boundaries

- Script: `packages/factory/scripts/init-factory` (`main` and its report lines)
- Contract: [interface-contracts.md § init-factory counter check](../docs/spec/interface-contracts.md#init-factory-counter-check)
- Tests: `tests/factory/` (new `test_init_factory_counter.py`), next to `test_init_factory_rerun.py`

### Domain Rules

- `init-factory` never seeds and never writes `refs/ids/counters`.
- The install needs no counter, so no counter case stops it.

### Size

1 story.

### Building-Block Inventory

| Story   | Capability                                    | Tier     | Size | Goal                                                                                                                                         | Basis                                                                                                         |
| ------- | --------------------------------------------- | -------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| ST-0375 | See from init-factory how to seed the counter | standard | S    | `init-factory` prints the seed message, the remote message, or a warning that names the remote, and finishes the install in all three cases. | `init-factory` repairs `origin/HEAD` but never looks at `refs/ids/counters`. Adds the check and its messages. |

### Testability Assessment

The goal produces observable results: the report lines of `init-factory`, its exit code, `.agent-factory/install.json`, and the refs of the bare repository afterwards. Tests run `init-factory` as a subprocess on temporary projects, as `test_init_factory_rerun.py` does, with a bare repository, no `origin`, or a closed local port as `origin`. One red flag: the exit code for two of the cases is open (`CID-G02`), so the tests assert only the messages there.

### Ownership Resolution

| Contract                                                                                 | .feature Rule                                                             | Owner   | Rationale                    |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------- | ---------------------------- |
| CID-10-IT-01: a missing counter gives the seed message and leaves `origin` without a ref | counter-ids.feature#User learns from init-factory how to seed the counter | ST-0375 | introduces the counter check |
| CID-10-IT-02: a project without `origin` gives the remote message                        | counter-ids.feature#User learns from init-factory how to seed the counter | ST-0375 | introduces the counter check |
| CID-10-IT-03: an unreachable `origin` gives a warning, and the install exits 0           | counter-ids.feature#User learns from init-factory how to seed the counter | ST-0375 | introduces the counter check |
