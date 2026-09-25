# QA Strategy: opencode-cli-integration

Generated from:

- Feature spec: `docs/spec/opencode-cli-integration.feature`
- Entity model: `docs/spec/supplementary_specs/entity-model.md`
- Interface contracts: `docs/spec/supplementary_specs/interface-contracts.md`
- Charter layer bindings: `docs/testing.yaml`
- Repo test infrastructure: `tests/conftest.py`, `tests/factory/`, `tests/integration/`

## Feature

- Proposal trace: `docs/proposals/opencode-cli-integration.md`
- Gherkin trace: `docs/spec/opencode-cli-integration.feature`
- Summary: This feature adds OpenCode V2 as a fifth Factory CLI target. QA must verify that the installer correctly detects, creates, updates, and removes OpenCode files; that the V2 plugin enforces permissions, step boundaries, and fail-closed behavior; that usage capture works without double-counting; that worktree isolation delegates correctly to Factory scripts; and that model configuration halts on missing tiers. The integration touches the existing installer, model resolver, and usage pipeline, so regression on those paths is a primary risk.
- Rules in scope:
  - `Rule: Project maintainer installs Factory for OpenCode CLI`
  - `Rule: Project maintainer updates an existing OpenCode integration`
  - `Rule: Project maintainer removes Factory OpenCode files cleanly`
  - `Rule: Project maintainer runs OpenCode alongside other Factory CLIs`
  - `Rule: OpenCode user enters Factory through plugin-injected orientation`
  - `Rule: OpenCode user discovers agents and skills through native paths`
  - `Rule: Factory plugin enforces permissions and step boundaries`
  - `Rule: Factory plugin captures completed session usage`
  - `Rule: Factory plugin isolates child sessions in Factory-managed worktrees`
  - `Rule: Fitting operator configures OpenCode model tiers`

## Test Layers in Scope

| Layer                 | Status    | Charter binding                                                                    | Feature-specific scope                                                                                                                                                                                    | Owned contracts       |
| --------------------- | --------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| Deterministic linter  | available | `packages/usage/scripts/usage-contract-check` (custom standalone scripts)          | Validate generated `.opencode/INDEX.yaml` structure, `AGENTS.md` table format, `model.conf` entry syntax                                                                                                  | OCI-01 through OCI-03 |
| Contract test         | planned   | `uv run pytest --tb=short --quiet tests/` (pytest, mock infrastructure)            | init-factory OpenCode detection, version check, file creation, idempotency; model.conf parsing with opencode entries; plugin permission rule evaluation; usage record contract compliance                 | OCI-04 through OCI-18 |
| Integration test      | planned   | `uv run pytest --tb=short --quiet tests/` (pytest, real filesystem and subprocess) | Full init-factory run with OpenCode markers, update, removal, coexistence with Pi and Codex; remove-factory reversal; plugin worktree strategy delegation                                                 | OCI-19 through OCI-28 |
| Acceptance test       | out       | n/a                                                                                | No Gherkin runner configured in the project; acceptance criteria are verified through contract and integration tests                                                                                      | n/a                   |
| End-to-end smoke test | blocked   | n/a                                                                                | Requires a supported OpenCode CLI executable. One representative journey: install, start session, deny an unsafe command, capture usage, run child in worktree. Blocked until OpenCode is available in CI | OCI-29                |

## Contract Owners

| Contract                                         | Source scenario or gap                                                       | Owner layer           | Test ID      | Test location                                | Command                            | State   |
| ------------------------------------------------ | ---------------------------------------------------------------------------- | --------------------- | ------------ | -------------------------------------------- | ---------------------------------- | ------- |
| Generated INDEX.yaml has valid structure         | Scenario: Explicit CLI selection installs OpenCode                           | Deterministic linter  | OCI-01-LN-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| AGENTS.md CLI table includes OpenCode row        | Scenario: AGENTS.md CLI table includes OpenCode                              | Deterministic linter  | OCI-02-LN-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| model.conf entry syntax valid for opencode tiers | Scenario: model.conf gains OpenCode entries for three tiers                  | Deterministic linter  | OCI-03-LN-01 | `tests/factory/test_opencode_model.py`       | `uv run pytest --tb=short --quiet` | planned |
| Auto-detection from .opencode/ directory         | Scenario: Auto-detection selects OpenCode when its markers exist             | Contract test         | OCI-04-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Auto-detection from opencode.json                | Scenario: Auto-detection selects OpenCode from opencode.json                 | Contract test         | OCI-04-CT-02 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Auto-detection from opencode.jsonc               | Scenario: Auto-detection selects OpenCode from opencode.jsonc                | Contract test         | OCI-04-CT-03 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Unsupported version stops installation           | Scenario: Installer rejects an unsupported OpenCode version                  | Contract test         | OCI-05-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Supported version proceeds                       | Scenario: Installer accepts a supported OpenCode version                     | Contract test         | OCI-05-CT-02 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| CLI not installed stops installation             | Scenario: Installer rejects when OpenCode is not installed                   | Contract test         | OCI-05-CT-03 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Idempotent installation                          | Scenario: Repeated installation produces no additional changes               | Contract test         | OCI-06-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| User file preservation during install            | Scenario: Installer preserves user-owned files under .opencode/              | Contract test         | OCI-07-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Install manifest records OpenCode paths          | Scenario: Explicit CLI selection installs OpenCode                           | Contract test         | OCI-08-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| Plugin permission rule ordering                  | Scenario: Plugin applies ordered allow, ask, and deny rules                  | Contract test         | OCI-09-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Pre-tool hook denies read outside manifest       | Scenario: Pre-tool hook rejects a read outside the step manifest             | Contract test         | OCI-10-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Pre-tool hook denies write outside manifest      | Scenario: Pre-tool hook rejects a write outside the step manifest            | Contract test         | OCI-10-CT-02 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Dangerous Git command denied                     | Scenario: Dangerous Git command is denied before shell execution             | Contract test         | OCI-11-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Review agent gets read-only permissions          | Scenario: Review agent receives read-only permissions                        | Contract test         | OCI-12-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Plugin never broadens a denial                   | Scenario: Plugin never broadens a configured denial                          | Contract test         | OCI-13-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Tool removal restricts agent tool set            | Scenario: Tool removal restricts the active agent's tool set                 | Contract test         | OCI-14-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Plugin fails closed on init failure              | Scenario: Plugin fails closed on initialization failure                      | Contract test         | OCI-15-CT-01 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Plugin fails closed on manifest failure          | Scenario: Plugin fails closed on manifest loading failure                    | Contract test         | OCI-15-CT-02 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Plugin fails closed on permission failure        | Scenario: Plugin fails closed on permission evaluation failure               | Contract test         | OCI-15-CT-03 | `tests/factory/test_opencode_plugin.py`      | `uv run pytest --tb=short --quiet` | planned |
| Usage record follows existing contract           | Scenario: Completed root session produces a usage record                     | Contract test         | OCI-16-CT-01 | `tests/factory/test_opencode_usage.py`       | `uv run pytest --tb=short --quiet` | planned |
| Child usage not double-counted                   | Scenario: Child usage is not counted twice                                   | Contract test         | OCI-17-CT-01 | `tests/factory/test_opencode_usage.py`       | `uv run pytest --tb=short --quiet` | planned |
| Usage failure does not block session             | Scenario: Usage capture failure does not block the session                   | Contract test         | OCI-18-CT-01 | `tests/factory/test_opencode_usage.py`       | `uv run pytest --tb=short --quiet` | planned |
| Full install creates expected file tree          | Scenario: Explicit CLI selection installs OpenCode                           | Integration test      | OCI-19-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Update preserves user files                      | Scenario: Update refreshes Factory-owned OpenCode files                      | Integration test      | OCI-20-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| remove-factory removes OpenCode entries          | Scenario: remove-factory removes Factory-owned OpenCode entries              | Integration test      | OCI-21-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Pi+Codex+OpenCode coexistence                    | Scenario: Pi, Codex, and OpenCode coexist with one root AGENTS.md            | Integration test      | OCI-22-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Add OpenCode to existing multi-CLI               | Scenario: Adding OpenCode to an existing multi-CLI project                   | Integration test      | OCI-23-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Agents discoverable under .opencode/agents/      | Scenario: Agents are discoverable under .opencode/agents/                    | Integration test      | OCI-24-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Skills discoverable under .agents/skills/        | Scenario: Skills are discoverable under .agents/skills/                      | Integration test      | OCI-25-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| Generated agent defs carry model field           | Scenario: Generated agent definitions carry OpenCode-specific fields         | Integration test      | OCI-26-IT-01 | `tests/integration/test_opencode_install.py` | `uv run pytest --tb=short --quiet` | planned |
| model.conf opencode entries parsed correctly     | Scenario: Fitting presents OpenCode model identifiers in provider/model form | Integration test      | OCI-27-IT-01 | `tests/integration/test_opencode_model.py`   | `uv run pytest --tb=short --quiet` | planned |
| Missing model tier halts                         | Scenario: Missing model mapping halts                                        | Integration test      | OCI-28-IT-01 | `tests/integration/test_opencode_model.py`   | `uv run pytest --tb=short --quiet` | planned |
| Documentation records OpenCode support           | Scenario: Documentation records OpenCode support                             | Contract test         | OCI-29-CT-01 | `tests/factory/test_opencode_install.py`     | `uv run pytest --tb=short --quiet` | planned |
| End-to-end smoke with live OpenCode              | Gap: no live OpenCode in CI                                                  | End-to-end smoke test | OCI-30-E2-01 | `tests/integration/test_opencode_e2e.py`     | `opencode` CLI required            | blocked |

### Spec marker convention

Projects that use pytest should carry the scope ID as a marker:

```python
@pytest.mark.spec("OCI-04")
@pytest.mark.contract
def test_autodetect_selects_opencode_from_dotdir(): ...
```

The marker enables traceability from test to contract-owner table and supports mutation-testing classification joining mutants to contracts.

## Boundary Cases

| Boundary case                                  | Source scenario or gap                                            | Risk addressed                               | Owner layer      | Notes                                                 |
| ---------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------- | ---------------- | ----------------------------------------------------- |
| Version string exactly 1.18.31 (minimum)       | Scenario: Installer accepts a supported OpenCode version          | Off-by-one in version comparison             | Contract test    | Verify boundary passes                                |
| Version string 1.18.30 (one below minimum)     | Scenario: Installer rejects an unsupported OpenCode version       | Off-by-one in version comparison             | Contract test    | Verify boundary rejects                               |
| Version string with pre-release suffix         | Gap: version format with pre-release                              | Unexpected version format parsed incorrectly | Contract test    | Decide whether 1.18.31-beta passes or fails           |
| Empty .opencode/ directory (user-owned)        | Scenario: Installer preserves user-owned files under .opencode/   | Install overwrites user config               | Contract test    | Only Factory paths should be created                  |
| .opencode/ exists with user plugins            | Scenario: Installer preserves user-owned files under .opencode/   | User plugins removed during install          | Contract test    | .opencode/plugins/ must not clobber user plugins      |
| opencode --version not found on PATH           | Scenario: Installer rejects when OpenCode is not installed        | Installer crashes instead of reporting       | Contract test    | Verify graceful failure with installation instruction |
| Step manifest missing during tool call         | Scenario: Plugin fails closed on manifest loading failure         | Plugin allows unchecked access               | Contract test    | Verify denial, not pass-through                       |
| Permission hook error during evaluation        | Scenario: Plugin fails closed on permission evaluation failure    | Plugin silently allows                       | Contract test    | Verify denial on error                                |
| Child session with no parent run ID            | Scenario: Child usage is not counted twice                        | Double-counted usage                         | Contract test    | Verify ancestry validation                            |
| Worktree creation fails mid-dispatch           | Scenario: Plugin fails closed on worktree creation failure        | Child starts without isolation               | Contract test    | Verify dispatch denied                                |
| All three model tiers missing                  | Scenario: Missing model mapping halts                             | Agent dispatched without model               | Integration test | Verify halt for each tier independently               |
| model.conf has opencode entry with empty value | Gap: empty model identifier                                       | Model resolver accepts empty string          | Integration test | Verify halt or error                                  |
| remove-factory with partial install manifest   | Scenario: remove-factory removes Factory-owned OpenCode entries   | Partial cleanup leaves orphan files          | Integration test | Verify only recorded paths are removed                |
| Three CLIs installed then one removed          | Scenario: Pi, Codex, and OpenCode coexist with one root AGENTS.md | Removing one CLI damages others              | Integration test | Verify other CLIs unaffected                          |

## Gap Findings

| Finding                                                | Source                        | Severity | Recommended action                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------ | ----------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Acceptance test layer not available                    | Charter / repo scan           | minor    | The project has no Gherkin runner. Acceptance criteria are covered by contract and integration tests. Add a Gherkin runner if acceptance-level testing is desired in a later release                                                                                                       |
| End-to-end smoke test blocked                          | Repo scan                     | minor    | Requires OpenCode CLI in the CI environment. When available, add a conditional CI job that runs `OCI-29-E2-01`                                                                                                                                                                             |
| Charter declares no acceptance_test or e2e_smoke layer | Charter (`docs/testing.yaml`) | info     | Charter `layers` section has `deterministic_linter`, `contract_test`, and `integration_test`. The absence of acceptance and e2e layers is intentional for this project; Factory convention fallback applies for the QA strategy                                                            |
| Four open questions in proposal                        | Proposal open questions       | minor    | Questions about `execute.before` denial contract, permission hooks in child sessions, tool removal persistence, and skill discovery after disabling Claude Code compatibility. Resolve during implementation by testing against the target OpenCode version. May require scenario revision |

## Defect Severity Triage

| Impact on this feature                                                                                                 | Severity          | Expected action                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------ |
| Plugin allows a tool invocation that should be denied (permission bypass, step-boundary bypass, dangerous Git command) | blocking          | Stop release, fix before merge. A safety invariant failure is the highest-risk defect for this feature |
| Installation overwrites or removes user-owned files under .opencode/                                                   | blocking          | Stop release, fix before merge. User data loss is unacceptable                                         |
| Usage record double-counts child session usage or fails to capture root session usage                                  | fix-in-same-story | Repair in current story or QA loop. Incorrect usage data undermines operational trust                  |
| Installer proceeds on unsupported OpenCode version                                                                     | fix-in-same-story | Repair in current story. Version gate is a core safety control                                         |
| Plugin fails open (allows on error instead of denying)                                                                 | blocking          | Stop release. Fail-closed is a design invariant                                                        |
| Generated agent definition missing model field                                                                         | fix-in-same-story | Repair in current story. Missing model causes runtime dispatch failure                                 |
| Documentation omits plugin trust model                                                                                 | defer             | File finding or backlog follow-up. Documentation gap does not block functionality                      |
| Minor copy in orientation text                                                                                         | defer             | File finding. Low risk, no functional impact                                                           |

## Test Retention Policy

- Surviving owner per major contract: contract tests own permission enforcement, step-boundary checks, usage capture, and version validation. Integration tests own filesystem operations (install, update, remove, coexistence).
- Expected overlap to remove later: contract tests and integration tests may both exercise auto-detection logic. When integration tests cover all three markers with real filesystem operations, contract-test equivalents that mock the filesystem for detection only can be removed if the integration test proves it catches the same faults.
- Consolidation rule: keep one owner per contract per [testing-strategy.md](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md).
- Deletion protocol: follow [testing-strategy.md § Delete overlapping tests safely](../../.agent-factory/factory/rulebooks/conventions/testing-strategy.md#delete-overlapping-tests-safely).
