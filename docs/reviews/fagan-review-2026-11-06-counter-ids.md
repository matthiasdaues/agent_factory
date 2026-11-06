---
type: fagan-review
title: Fagan review and bug hunt of the counter-ids implementation
date: 2026-11-06
status: pass
reviewer: qa-agent
findings_filed: 0
story: counter-ids
branch: feature/counter-ids
branch_base: 5e2c9b52c9353aa45a07230826fe6a60bbfaae8e
branch_head: d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b
---

# Fagan review and bug hunt of the counter-ids implementation

## Result

The Fagan inspection and the bug hunt found no new blocking defect and no new
`minor` finding. The code does what `counter-ids.feature` and BR-068 to BR-076
require. The open items of this QA run sit in the
[security review](security-review-2026-11-06-counter-ids.md): SEC-0007 blocks
the merge. Next, the Implementation Agent fixes SEC-0007, and the QA agent
checks the fix.

## Scope

The run covers `git diff dev...feature/counter-ids` at `d0a78a5c`:

- `packages/factory/scripts/next-id`
- `check_counter` and its call in `packages/factory/scripts/init-factory`
- `tests/factory/test_next_id.py`, `test_next_id_race.py`, `next_id_race.py`,
  `test_init_factory_counter.py`, `test_counter_ids_text.py`, and the new cases
  in `test_block_dangerous_git.py`
- the producer and rule texts that the code review already read

It checks them against `docs/spec/features/counter-ids.feature`, the QA
strategy `docs/spec/work/counter-ids-qa-strategy.md`, BR-068 to BR-076, the
`next-id` contract in `interface-contracts.md`, the Decisions table of
`counter-ids.md` up to DEC-25, ADR-0031, and ADR-0032. The classification
follows `finding-classification.md`, as the brief requires.

The run leaves out what earlier reviews recorded: IMPL-0004 to IMPL-0007 of the
code review, RECON-0025 to RECON-0029 and BUG-0117 of the reconciliation, and
T-0017 and T-0019.

## Acceptance test

`docs/testing.yaml` declares no Gherkin runner, so the Scenarios run as the
pytest tests that the QA strategy names. This run changed no test. So, as the
brief says, it did not start the suite. The run checked the Scenarios a second
way: it ran `next-id` from the branch head by hand against local bare
repositories, with a temporary `HOME`. The seed, the first claim of a prefix,
the four-digit form, the boundary `ST=9998` to `ST-9999`, the refused
arguments, and the clean exit of the throwaway directory behaved as the
Scenarios state.

## Fagan inspection

**Correctness.** `parse_seed` and `check_prefix` run before the remote is
contacted. `raise_line` keeps every other line, adds `start` plus one for a new
prefix, and writes a new token. The claim retries only on the two stale-lease
messages, and the seed uses the create-only lease. A claim prints its ID only
after `git push` exits 0. Each case of the error table in
`interface-contracts.md` names what the table asks for.

**Clean Architecture and SOLID.** The `Counter` protocol keeps the claim loop
apart from git, and the unit tests drive the loop through it. BUG-0117 already
records that the port has `read` and `push` and not `claim` and `seed`.

**YAGNI.** The run looked for abstractions without a user, options without a
caller, and early optimization. It found none. The `guarded` flag has two
callers, the claim and the seed. The `Counter` protocol has one adapter, but
DEC-11 asks for the port, and the tests use it.

**Maintainability and test coverage.** Every contract row of the QA strategy
has a test. The CID-10 tests and the QS-19 test carry no `spec` marker, which
RECON-0029 already records. All stories trace to `counter-ids.feature`, so the
`test-design-pass` check does not apply. The stories carry no `tests:` field,
so the run joined contracts to tests through the `spec` markers. The
testability probe in `backlog/epics-counter-ids.md` raised four red flags.
Three now have tests: the ten-stale-lease setup (CID-04-IT-01), QS-19
(`test_st_0369_eight_claims_at_once_all_get_their_own_id`), and BR-076
(`test_st_0370_password_server_gets_no_prompt` and the IMPL-0004 tests). The
fourth, the open exit code of CID-G02, stays open by decision, and the CID-10
tests assert only the message.

**Consistency.** `next-id` follows the pattern of the other standard-library
scripts: a `uv` script header, `argparse`, and `LC_ALL=C` for git. The
`init-factory` check follows the section pattern of `main`.

## Bug hunt

The hunt ran one cycle with the intent to break the code. It found no
`BUG` finding, so the run made no fix commit. A second cycle had nothing to
retest. The hunt tried these cases:

- empty `--remote`, an empty prefix, a seed number with a leading space, and a
  pair without a prefix: each fails with exit 1 and a message
- `--seed 0 ST=9998`, then claims of `ST` and `BUG`: `ST-9999` and `BUG-0001`,
  as BR-069 and BR-071 allow
- a remote with `receive.denyNonFastForwards=true`: the claim still succeeds,
  because git applies that setting only to `refs/heads/`
- a global `commit.gpgSign=true`: `git commit-tree` does not sign, so no
  signing prompt appears
- a remote URL with a credential: the credential appears in the message, which
  is SEC-0007
- a remote that asks for a password over HTTP: git calls `GIT_ASKPASS`, which
  is the question in the security review

## Notes

These observations need no change. They stay in this report only.

- **A relative `origin` URL fails from a subdirectory.** With
  `git remote add origin ../r.git`, `next-id ST` works at the top of the clone
  and fails in a subdirectory with git's message "'../r.git' does not appear
  to be a git repository". The throwaway git calls resolve the path from the
  current directory, while git in the clone resolves it from the top of the
  clone. `git clone` always stores an absolute path, and the message names the
  path, so the user sees the cause.
- **The `init-factory` warning says "does not answer" for any failure.** A
  remote that answers and refuses access gets the same words. The next line
  quotes git's message, so the user still sees the reason.
- **The time-limit message appears twice.** `RemoteCounter._timed_out` and
  `claim` build the same sentence. Both name the remote and the limit.
- **`test_init_factory_counter.py` keeps the developer's `HOME`.** A URL
  rewrite in the developer's global config reaches these tests. The tests use
  local bare repositories and a closed port, so no test reaches a real remote.
