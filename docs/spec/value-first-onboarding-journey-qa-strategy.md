# QA Strategy: value-first-onboarding-journey

Generated from:

- Feature spec: [value-first-onboarding-journey.feature](value-first-onboarding-journey.feature)
- Entity model: [entity-model.md](supplementary_specs/entity-model.md#value-first-onboarding-entities)
- Interface contracts: [interface-contracts.md](supplementary_specs/interface-contracts.md#value-first-onboarding-contracts)
- Charter layer bindings: [testing.yaml](../testing.yaml)
- Repository test infrastructure: `tests/conftest.py`, `tests/factory/`,
  `tests/integration/`, `packages/usage/tests/`, and `pyproject.toml`

## Feature

- Proposal trace:
  [value-first-onboarding-journey.md](../proposals/value-first-onboarding-journey.md)
- Gherkin trace:
  [value-first-onboarding-journey.feature](value-first-onboarding-journey.feature)
- Summary: Testing focuses on consent, integrity, rollback, read-only behavior,
  instruction-file preservation, sandbox isolation, and the measured path to a
  first result. Installer and update tests require real filesystem and
  subprocess boundaries. Pure classification and transition rules belong to
  contract tests.
- Rules in scope:
  - `Rule: Release maintainer publishes reproducible installation assets`
  - `Rule: Newcomer diagnoses installation readiness without changes`
  - `Rule: Newcomer controls each prerequisite fix`
  - `Rule: Newcomer installs a verified Factory release with explicit consent`
  - `Rule: Project maintainer updates an installation within its trust boundary`
  - `Rule: Newcomer receives project insight before advanced configuration`
  - `Rule: Newcomer sees gate value before choosing hooks`
  - `Rule: Newcomer completes one isolated task and chooses its outcome`
  - `Rule: Quality researcher measures the complete newcomer journey`

## Test Layers in Scope

| Layer                 | Status            | Charter binding                                                                                                                      | Feature-specific scope                                                                                                                                            | Owned contracts                   |
| --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| Deterministic linter  | available         | custom standalone scripts: `packages/usage/scripts/usage-contract-check`, `packages/factory/scripts/hook-subset`                     | Consumer hook configuration contains no source-only entries                                                                                                       | VFO-07-LN-01                      |
| Acceptance test       | planned           | Factory convention fallback; no Gherkin runner is declared                                                                           | Consent, cancellation, first-session ordering, and task outcome behavior                                                                                          | VFO-02-AC-01 through VFO-09-AC-01 |
| Contract test         | available         | pytest with mocks: `uv run pytest --tb=short --quiet tests/`                                                                         | Argument validation, readiness classification, consent policy, and lifecycle transitions                                                                          | VFO-02-CT-01 through VFO-08-CT-01 |
| Integration test      | partially covered | pytest with real filesystem and subprocesses: `uv run pytest --tb=short --quiet tests/`                                              | Release reproducibility, verified installation, update rollback, header preservation, gate cleanup, and sandbox isolation                                         | VFO-01-IT-01 through VFO-08-IT-03 |
| End-to-end smoke test | available         | pytest, declared as `end_to_end` in `docs/testing.yaml`: `uv run pytest --tb=short --quiet tests/factory/test_onboarding_journey.py` | One ready-host journey from preflight through first-session routing (ST-0293 scoped the journey to stop there; updating and the first task have their own owners) | VFO-09-E2-01                      |

The existing installer, updater, and context tests make the integration harness
available. They do not implement the new contracts in this feature.

## Contract Owners

| Contract                                                                               | Source scenario or gap                                                                                                      | Owner layer           | Test ID      | Test location                                               | Command                                                                            | State     |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------ | ----------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------- |
| Repeated release builds produce the same complete asset set and digest                 | `Scenario: Release build produces the required asset set`                                                                   | Integration test      | VFO-01-IT-01 | `tests/factory/test_build_release.py`                       | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Bootstrap rejects invalid source, version, and target combinations without writes      | `Scenario: Bootstrap requires one source and an explicit target`                                                            | Contract test         | VFO-02-CT-01 | `tests/factory/test_install_agent_factory.py`               | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Preflight classifies supported and unsupported hosts without writes                    | `Scenario: Supported host receives one readiness result`                                                                    | Contract test         | VFO-02-CT-02 | `tests/factory/test_install_agent_factory.py`               | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Each supported fix requires consent and related verification                           | `Scenario: Confirmed fix runs and is verified alone`                                                                        | Contract test         | VFO-03-CT-01 | `tests/factory/test_install_agent_factory.py`               | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Declined, blank, failed, or unsupported fixes never continue mutation                  | `Scenario: Declined or blank fix input stops the sequence`                                                                  | Acceptance test       | VFO-03-AC-01 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| Remote archive extraction requires a matching published digest                         | `Scenario: Missing or mismatched digest blocks extraction`                                                                  | Integration test      | VFO-04-IT-01 | `tests/factory/test_install_agent_factory.py`               | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Installation requires preview approval and emits an accurate receipt                   | `Scenario: Approved installation returns a verifiable receipt`                                                              | Acceptance test       | VFO-04-AC-01 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| Instruction discovery, injection, idempotence, and removal preserve user content       | `Scenario: Header installation and removal are reversible`                                                                  | Integration test      | VFO-04-IT-02 | `tests/factory/test_install_agent_factory.py`               | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| Update check performs no writes                                                        | `Scenario: Update check reports candidate changes without writing`                                                          | Integration test      | VFO-05-IT-01 | `tests/factory/test_update_factory.py`                      | `uv run pytest --tb=short --quiet tests/`                                          | planned   |
| Update verifies and stages before applying, then rolls back failed application         | `Scenario: Failed update restores the prior installation`                                                                   | Integration test      | VFO-05-IT-02 | `tests/factory/test_update_factory.py`                      | `uv run pytest --tb=short --quiet tests/`                                          | planned   |
| Source changes require an explicit option and separate consent                         | `Scenario: Source change requires separate consent`                                                                         | Acceptance test       | VFO-05-AC-01 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| First session reports observed evidence and one recommendation without writes          | `Scenario: First session reports evidence without changing the project`                                                     | Acceptance test       | VFO-06-AC-01 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| Configuration appears only before an action that needs it                              | `Scenario: Advanced configuration waits for a dependent action`                                                             | Contract test         | VFO-06-CT-01 | `tests/factory/test_value_first_routing.py`                 | `uv run pytest --tb=short --quiet tests/`                                          | planned   |
| Context capture explanation and cancellation precede the scan                          | `Scenario: Context capture can be deferred before scanning`                                                                 | Acceptance test       | VFO-06-AC-02 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| Consumer hook set omits ignored runtime triggers and `index-lint`                      | `Scenario: Consumer hook set omits source-only triggers`                                                                    | Deterministic linter  | VFO-07-LN-01 | `tests/factory/test_precommit_config_contract.py`           | `uv run pytest --tb=short --quiet tests/factory/test_precommit_config_contract.py` | available |
| Gate demonstration shows failure and success without target changes                    | `Scenario: Gate demonstration shows one failure-to-pass cycle`                                                              | Integration test      | VFO-07-IT-01 | `tests/factory/test_hook_demo.py`                           | `uv run pytest --tb=short --quiet tests/`                                          | blocked   |
| First-task approval controls sandbox creation                                          | `Scenario: First task preview requires approval`                                                                            | Acceptance test       | VFO-08-AC-01 | `tests/factory/test_onboarding_journey.py`                  | —                                                                                  | blocked   |
| Repository state selects detached worktree or plain sandbox                            | `Scenario: Repository with a commit uses a detached worktree`, `Scenario: Repository without a commit uses a plain sandbox` | Integration test      | VFO-08-IT-01 | `tests/factory/test_onboarding_sandbox.py`                  | `uv run pytest --tb=short --quiet tests/`                                          | available |
| Active-working-tree changes never enter the first-task sandbox                         | `Scenario: Repository with a commit uses a detached worktree`                                                               | Integration test      | VFO-08-IT-02 | `tests/factory/test_onboarding_sandbox.py`                  | `uv run pytest --tb=short --quiet tests/`                                          | available |
| Discard, retention, and production handoff apply only the selected outcome             | `Scenario: Newcomer retains selected reference artifacts`                                                                   | Integration test      | VFO-08-IT-03 | `tests/factory/test_onboarding_sandbox.py`                  | `uv run pytest --tb=short --quiet tests/`                                          | available |
| Complete safe journey checks consent, cancellation, installation, receipt, and routing | `Scenario: Automated journey checks the safe non-interactive path`                                                          | End-to-end smoke test | VFO-09-E2-01 | `tests/factory/test_onboarding_journey.py`                  | `uv run pytest --tb=short --quiet tests/factory/test_onboarding_journey.py`        | available |
| Moderated protocol records time, decisions, confusion, recovery, and next action       | `Scenario: Moderated session records newcomer comprehension`                                                                | Acceptance test       | VFO-09-AC-01 | `docs/testing/value-first-onboarding-usability-protocol.md` | manual protocol                                                                    | planned   |

### Spec marker convention

Pytest tests should carry the Rule scope identifier and layer marker:

```python
@pytest.mark.spec("VFO-05")
@pytest.mark.integration
def test_failed_update_restores_factory_tree_and_headers(): ...
```

The marker links each test to this table and supports mutation-test ownership.

## Boundary Cases

| Boundary case                                 | Source scenario or gap                                                   | Risk addressed                   | Owner layer      | Notes                          |
| --------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------- | ---------------- | ------------------------------ |
| Zero or two source selectors                  | `Scenario: Bootstrap requires one source and an explicit target`         | Ambiguous trust source           | Contract test    | Exit without writes            |
| `--version` with local source                 | `Scenario: Version selection is valid only for remote sources`           | Non-reproducible local semantics | Contract test    | Reject before preflight        |
| Target is root or user home                   | `Scenario: Unsafe target is rejected`                                    | Broad destructive write          | Contract test    | Reject resolved path           |
| Unsupported platform or architecture          | `Scenario: Unsupported host stops safely`                                | Partial unsupported installation | Contract test    | Explain incompatibility        |
| Blank consent input                           | `Scenario: Declined or blank fix input stops the sequence`               | Accidental mutation              | Acceptance test  | Treat as refusal               |
| Digest absent or mismatched                   | `Scenario: Missing or mismatched digest blocks extraction`               | Tampered or incomplete release   | Integration test | Refuse extraction              |
| Several detected interfaces with blank choice | `Scenario: Ambiguous interface selection does not select all interfaces` | Excess installation scope        | Acceptance test  | Ask again or stop              |
| External instruction-file symlink             | `Scenario: Instruction discovery preserves excluded and linked content`  | Write outside target             | Integration test | Report unchanged               |
| Instruction file without terminal newline     | `Scenario: Header installation and removal are reversible`               | Content corruption               | Integration test | Restore original newline state |
| Failure during staged update application      | `Scenario: Failed update restores the prior installation`                | Mixed-version installation       | Integration test | Restore tree and headers       |
| Context capture cancelled before scan         | `Scenario: Context capture can be deferred before scanning`              | Unapproved read or write         | Acceptance test  | Start no scan                  |
| Repository has no commit                      | `Scenario: Repository without a commit uses a plain sandbox`             | Invalid worktree command         | Integration test | Use plain sandbox              |
| Working tree contains uncommitted changes     | `Scenario: Repository with a commit uses a detached worktree`            | Leakage into demonstration       | Integration test | Sandbox starts at `HEAD`       |
| Retention not separately confirmed            | `Scenario: Newcomer retains selected reference artifacts`                | Silent project mutation          | Integration test | Copy nothing                   |

## Gap Findings

| Finding                                                                                                                                                                                                                                                                                        | Source                       | Severity | Recommended action                                                                  |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | -------- | ----------------------------------------------------------------------------------- |
| No acceptance-test layer or Gherkin runner is declared in `docs/testing.yaml`.                                                                                                                                                                                                                 | Charter and repository scan  | major    | Add the journey harness before implementing consent and session-ordering scenarios. |
| ~~No end-to-end layer is declared.~~ Resolved by ST-0293: `docs/testing.yaml` now declares `end_to_end`, backed by `tests/factory/test_onboarding_journey.py`.                                                                                                                                 | Charter and repository scan  | resolved | None.                                                                               |
| Planned release, bootstrap, and gate-demo scripts do not exist, so their tests are blocked.                                                                                                                                                                                                    | Proposal and repository scan | expected | Create each production entry point with its owning test.                            |
| ~~The deterministic-linter binding points to the usage contract checker, which cannot validate consumer hook contents.~~ Resolved by ST-0290: `packages/factory/scripts/hook-subset` is a Factory-owned hook-config validator, exercised by `tests/factory/test_precommit_config_contract.py`. | Charter fidelity check       | resolved | None.                                                                               |
| Existing installer and update tests provide usable real-filesystem infrastructure but do not cover remote release verification or recursive instruction headers.                                                                                                                               | Repository scan              | expected | Extend the existing integration suites when those contracts are implemented.        |

## Defect Severity Triage

| Impact on this feature                                                                                                       | Severity          | Expected action                                               |
| ---------------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------- |
| Unapproved mutation, unsafe target write, digest bypass, credential disclosure, write outside the target, or failed rollback | blocking          | Stop release and fix before merge.                            |
| Broken ready-host path, inaccurate receipt, missing reversal, sandbox leakage, or silent source-boundary change              | fix-in-same-story | Repair in the current story and rerun the owning journey.     |
| Time or decision budget missed, unclear term, inaccurate recommendation, or low-risk copy defect                             | defer             | Record evidence and schedule a focused onboarding correction. |

## Test Retention Policy

- Retain contract tests for pure parsing, classification, consent, and
  transition rules.
- Retain integration tests for filesystem preservation, subprocess behavior,
  checksums, staging, rollback, and worktree isolation.
- Retain one end-to-end ready-host journey. Remove lower-layer duplicates that
  assert the same journey ordering without owning a distinct failure mode.
- Keep one owner per contract under
  [testing-strategy.md](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md).
- Follow
  [Delete overlapping tests safely](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely)
  before removing overlap.
