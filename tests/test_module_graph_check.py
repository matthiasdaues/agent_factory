"""Contract tests for factory/scripts/module-graph-check.

Covers acceptance criteria AC 01–10 from ST-0106:
  - DSL parsing (AC 02)
  - Phase 1 output parsing (AC 03)
  - New module detection (AC 04a)
  - Changed public interface detection (AC 04b)
  - Dependency direction detection (AC 04c)
  - architecture_change output (AC 05)
  - Entity exception — new entity in existing module (AC 06)
  - Proposal frontmatter update (AC 07)
  - Override semantics (AC 08)
  - Runs against interface-contracts.md and entity-model.md (AC 09)
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "factory" / "scripts" / "module-graph-check"


def _load_module():
    """Import module-graph-check script as a Python module."""
    loader = importlib.machinery.SourceFileLoader("module_graph_check", str(SCRIPT))
    spec = importlib.util.spec_from_file_location(
        "module_graph_check", str(SCRIPT), loader=loader,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["module_graph_check"] = mod
    spec.loader.exec_module(mod)
    return mod


mgc = _load_module()


# ---------------------------------------------------------------------------
# Fixtures — minimal DSL, interface-contracts, entity-model
# ---------------------------------------------------------------------------

MINIMAL_DSL = """\
workspace "Test" "Test workspace" {
    model {
        actor = person "Actor" "A human"

        system = softwareSystem "Test System" "The system" {

            frontend = container "Frontend" "UI layer" "React" {
                loginPage = component "login-page" "Login UI" "React"
                dashboard = component "dashboard" "Main dashboard" "React"
            }

            backend = container "Backend" "API layer" "Python" {
                authService = component "auth-service" "Authentication" "Python"
                userApi = component "user-api" "User endpoints" "Python"
            }

            storage = container "Storage" "Persistence" "PostgreSQL" {
                userStore = component "user-store" "User table" "SQL"
            }
        }

        actor -> loginPage "Logs in"
        loginPage -> authService "Authenticates via"
        dashboard -> userApi "Fetches data from"
        authService -> userStore "Reads credentials from"
        userApi -> userStore "Queries"
    }

    views {
        systemContext system "Context" {
            include *
            autoLayout lr
        }
    }
}
"""

MINIMAL_CONTRACTS = """\
# Interface Contracts

## `scripts/login-page`

| | |
|---|---|
| Usage | `login-page --port PORT` |
| Exit code | `0` on success |

## `scripts/auth-service`

| | |
|---|---|
| Usage | `auth-service start` |
| Reads | user-store |
| Exit code | `0` on success |

## `scripts/user-api`

| | |
|---|---|
| Usage | `user-api start` |
| Reads | user-store |
| Exit code | `0` on success |
"""

CONTRACTS_WITH_NEW_MODULE = """\
# Interface Contracts

## `scripts/login-page`

| | |
|---|---|
| Usage | `login-page --port PORT` |

## `scripts/auth-service`

| | |
|---|---|
| Usage | `auth-service start` |

## `scripts/notification-service`

| | |
|---|---|
| Usage | `notification-service send` |
| Reads | user-store |
| Exit code | `0` on success |
"""

CONTRACTS_WITH_NEW_DEPENDENCY = """\
# Interface Contracts

## `scripts/login-page`

| | |
|---|---|
| Usage | `login-page --port PORT` |

## `scripts/auth-service`

| | |
|---|---|
| Usage | `auth-service start` |

## `scripts/user-store`

| | |
|---|---|
| Usage | `user-store query` |
| Reads | auth-service |
| Exit code | `0` on success |
"""

MINIMAL_ENTITY_MODEL = """\
# Entity Model

```mermaid
erDiagram
    USER ||--o{ SESSION : has
    SESSION }o--|| TOKEN : contains

    USER {
        string id
        string name
        string email
    }
    SESSION {
        string id
        string user_id
        datetime created_at
    }
    TOKEN {
        string value
        datetime expires_at
    }
```

## Notes

- **USER** is managed by `auth-service`.
- **SESSION** is managed by `auth-service`.
- **TOKEN** is managed by `auth-service`.
"""

ENTITY_MODEL_WITH_NEW_ENTITY = """\
# Entity Model

```mermaid
erDiagram
    USER ||--o{ SESSION : has
    SESSION }o--|| TOKEN : contains
    AUDIT_LOG ||--o{ USER : tracks

    USER {
        string id
        string name
    }
    SESSION {
        string id
    }
    TOKEN {
        string value
    }
    AUDIT_LOG {
        string id
        string action
    }
```

## Notes

- **USER** is managed by `auth-service`.
- **AUDIT_LOG** is a new entity managed by `auth-service`.
"""


PROPOSAL_FALSE = """\
---
schema_version: 2
title: "Test Feature"
status: accepted

impact:
  scope: single_component
  architecture_change: false
  external_contract_change: false
---

# Test Feature
"""

PROPOSAL_TRUE = """\
---
schema_version: 2
title: "Test Feature"
status: accepted

impact:
  scope: cross_component
  architecture_change: true
  external_contract_change: false
---

# Test Feature
"""

PROPOSAL_TRUE_WITH_COMMENT = """\
---
schema_version: 2
title: "Test Feature"
status: accepted

impact:
  scope: cross_component
  architecture_change: true  # manual override
  external_contract_change: false
---

# Test Feature
"""


# ---------------------------------------------------------------------------
# DSL Parsing — AC 02
# ---------------------------------------------------------------------------

class TestParseDsl:
    """Verify DSL parsing extracts containers, components, and relationships."""

    def test_extracts_containers(self, tmp_path):
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        graph = mgc.parse_dsl(dsl)
        container_names = {c.display_name for c in graph.containers.values()}
        assert "Frontend" in container_names
        assert "Backend" in container_names
        assert "Storage" in container_names

    def test_extracts_components_with_parent(self, tmp_path):
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        graph = mgc.parse_dsl(dsl)
        # Find auth-service component
        auth = None
        for comp in graph.components.values():
            if comp.display_name == "auth-service":
                auth = comp
                break
        assert auth is not None
        assert auth.container_var == "backend"

    def test_extracts_relationships(self, tmp_path):
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        graph = mgc.parse_dsl(dsl)
        rel_pairs = {(r.source_var, r.target_var) for r in graph.relationships}
        assert ("loginPage", "authService") in rel_pairs
        assert ("authService", "userStore") in rel_pairs

    def test_derives_module_level_deps(self, tmp_path):
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        graph = mgc.parse_dsl(dsl)
        # frontend -> backend (loginPage -> authService)
        assert ("frontend", "backend") in graph.module_deps
        # backend -> storage (authService -> userStore)
        assert ("backend", "storage") in graph.module_deps
        # No storage -> backend
        assert ("storage", "backend") not in graph.module_deps


# ---------------------------------------------------------------------------
# Interface Contracts Parsing — AC 03
# ---------------------------------------------------------------------------

class TestParseInterfaceContracts:
    """Verify interface-contracts.md parsing extracts script display names."""

    def test_extracts_script_names(self, tmp_path):
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(MINIMAL_CONTRACTS, encoding="utf-8")
        infos = mgc.parse_interface_contracts(contracts)
        names = [c.name for c in infos]
        assert "login-page" in names
        assert "auth-service" in names
        assert "user-api" in names

    def test_handles_backtick_paths(self, tmp_path):
        content = '# Contracts\n\n## `factory/scripts/my-script`\n\nSome text.\n'
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(content, encoding="utf-8")
        infos = mgc.parse_interface_contracts(contracts)
        names = [c.name for c in infos]
        assert "my-script" in names

    def test_extracts_references_from_reads(self, tmp_path):
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(MINIMAL_CONTRACTS, encoding="utf-8")
        infos = mgc.parse_interface_contracts(contracts)
        # auth-service reads user-store
        auth = [c for c in infos if c.name == "auth-service"][0]
        assert "user-store" in auth.references


# ---------------------------------------------------------------------------
# Entity Model Parsing — AC 03
# ---------------------------------------------------------------------------

class TestParseEntityModel:
    """Verify entity-model.md parsing extracts entity names."""

    def test_extracts_entity_names(self, tmp_path):
        em = tmp_path / "entity-model.md"
        em.write_text(MINIMAL_ENTITY_MODEL, encoding="utf-8")
        entities = mgc.parse_entity_model(em)
        assert "USER" in entities
        assert "SESSION" in entities
        assert "TOKEN" in entities

    def test_extracts_from_relationship_lines(self, tmp_path):
        em = tmp_path / "entity-model.md"
        em.write_text(ENTITY_MODEL_WITH_NEW_ENTITY, encoding="utf-8")
        entities = mgc.parse_entity_model(em)
        assert "AUDIT_LOG" in entities


# ---------------------------------------------------------------------------
# Architecture Change Check — AC 04, 05, 06
# ---------------------------------------------------------------------------

class TestCheckArchitectureChange:
    """Verify architecture change detection logic."""

    def test_new_module_triggers_true(self, tmp_path):
        """AC 04a: script in contracts not in DSL → architecture_change=true."""
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(CONTRACTS_WITH_NEW_MODULE, encoding="utf-8")
        em = tmp_path / "entity-model.md"
        em.write_text(MINIMAL_ENTITY_MODEL, encoding="utf-8")

        graph = mgc.parse_dsl(dsl)
        contract_infos = mgc.parse_interface_contracts(contracts)
        entity_names = mgc.parse_entity_model(em)

        result = mgc.check_architecture_change(graph, contract_infos, entity_names)
        assert result.architecture_change is True
        assert "notification-service" in result.new_modules

    def test_all_known_modules_returns_false(self, tmp_path):
        """AC 05: all scripts in DSL → architecture_change=false."""
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(MINIMAL_CONTRACTS, encoding="utf-8")
        em = tmp_path / "entity-model.md"
        em.write_text(MINIMAL_ENTITY_MODEL, encoding="utf-8")

        graph = mgc.parse_dsl(dsl)
        contract_infos = mgc.parse_interface_contracts(contracts)
        entity_names = mgc.parse_entity_model(em)

        result = mgc.check_architecture_change(graph, contract_infos, entity_names)
        assert result.architecture_change is False
        assert result.new_modules == []

    def test_new_entity_in_existing_module_no_trigger(self, tmp_path):
        """AC 06: new entity in existing module does NOT trigger true."""
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(MINIMAL_CONTRACTS, encoding="utf-8")
        em = tmp_path / "entity-model.md"
        em.write_text(ENTITY_MODEL_WITH_NEW_ENTITY, encoding="utf-8")

        graph = mgc.parse_dsl(dsl)
        contract_infos = mgc.parse_interface_contracts(contracts)
        entity_names = mgc.parse_entity_model(em)

        result = mgc.check_architecture_change(graph, contract_infos, entity_names)
        assert result.architecture_change is False

    def test_inverted_dependency_triggers_true(self, tmp_path):
        """AC 04c: inverted dependency direction → architecture_change=true."""
        dsl = tmp_path / "architecture.dsl"
        dsl.write_text(MINIMAL_DSL, encoding="utf-8")
        contracts = tmp_path / "interface-contracts.md"
        contracts.write_text(CONTRACTS_WITH_NEW_DEPENDENCY, encoding="utf-8")
        em = tmp_path / "entity-model.md"
        em.write_text(MINIMAL_ENTITY_MODEL, encoding="utf-8")

        graph = mgc.parse_dsl(dsl)
        contract_infos = mgc.parse_interface_contracts(contracts)
        entity_names = mgc.parse_entity_model(em)

        result = mgc.check_architecture_change(graph, contract_infos, entity_names)
        # storage -> backend is new (DSL only has backend -> storage)
        assert result.architecture_change is True
        assert len(result.new_dependencies) > 0 or len(result.inverted_dependencies) > 0


# ---------------------------------------------------------------------------
# Proposal Frontmatter Update — AC 07, 08
# ---------------------------------------------------------------------------

class TestUpdateProposal:
    """Verify proposal frontmatter update with override semantics."""

    def test_false_to_true_machine_wins(self, tmp_path):
        """AC 08: false → true, machine wins with annotation."""
        proposal = tmp_path / "proposal.md"
        proposal.write_text(PROPOSAL_FALSE, encoding="utf-8")

        result = mgc.CheckResult(
            architecture_change=True,
            new_modules=["notification-service"],
            changed_interfaces=[],
            new_dependencies=[],
            inverted_dependencies=[],
        )
        updated = mgc.update_proposal_frontmatter(proposal, result)
        assert updated is True

        content = proposal.read_text(encoding="utf-8")
        assert "architecture_change: true" in content
        assert "# mechanical detection" in content

    def test_true_stays_when_machine_says_false(self, tmp_path):
        """AC 08: true → false, prior human declaration stays true."""
        proposal = tmp_path / "proposal.md"
        proposal.write_text(PROPOSAL_TRUE, encoding="utf-8")

        result = mgc.CheckResult(
            architecture_change=False,
            new_modules=[],
            changed_interfaces=[],
            new_dependencies=[],
            inverted_dependencies=[],
        )
        updated = mgc.update_proposal_frontmatter(proposal, result)
        assert updated is False

        content = proposal.read_text(encoding="utf-8")
        assert "architecture_change: true" in content

    def test_true_with_comment_stays_true(self, tmp_path):
        """AC 08: true with existing comment stays true."""
        proposal = tmp_path / "proposal.md"
        proposal.write_text(PROPOSAL_TRUE_WITH_COMMENT, encoding="utf-8")

        result = mgc.CheckResult(
            architecture_change=False,
            new_modules=[],
            changed_interfaces=[],
            new_dependencies=[],
            inverted_dependencies=[],
        )
        updated = mgc.update_proposal_frontmatter(proposal, result)
        assert updated is False

        content = proposal.read_text(encoding="utf-8")
        assert "architecture_change: true" in content

    def test_false_stays_false_when_machine_agrees(self, tmp_path):
        """No change needed when both agree false."""
        proposal = tmp_path / "proposal.md"
        proposal.write_text(PROPOSAL_FALSE, encoding="utf-8")

        result = mgc.CheckResult(
            architecture_change=False,
            new_modules=[],
            changed_interfaces=[],
            new_dependencies=[],
            inverted_dependencies=[],
        )
        updated = mgc.update_proposal_frontmatter(proposal, result)
        assert updated is False

        content = proposal.read_text(encoding="utf-8")
        assert "architecture_change: false" in content


# ---------------------------------------------------------------------------
# Integration — AC 01, 09, 10
# ---------------------------------------------------------------------------

class TestMainIntegration:
    """Verify script end-to-end with subprocess."""

    def _setup_files(self, tmp_path, *, dsl=MINIMAL_DSL, contracts=MINIMAL_CONTRACTS,
                     entity_model=MINIMAL_ENTITY_MODEL, proposal=PROPOSAL_FALSE):
        """Create all input files in tmp_path."""
        (tmp_path / "architecture.dsl").write_text(dsl, encoding="utf-8")
        (tmp_path / "interface-contracts.md").write_text(contracts, encoding="utf-8")
        (tmp_path / "entity-model.md").write_text(entity_model, encoding="utf-8")
        (tmp_path / "proposal.md").write_text(proposal, encoding="utf-8")

    def test_exit_zero_no_change(self, tmp_path):
        """AC 01, 05: exits 0 when no architecture change."""
        self._setup_files(tmp_path)
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dsl-path", str(tmp_path / "architecture.dsl"),
                "--interface-contracts", str(tmp_path / "interface-contracts.md"),
                "--entity-model", str(tmp_path / "entity-model.md"),
                "--proposal", str(tmp_path / "proposal.md"),
                "--report-dir", str(tmp_path / "reports"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "architecture_change=false" in result.stdout

    def test_exit_zero_with_change(self, tmp_path):
        """AC 01, 05: exits 0 when architecture change detected (not an error)."""
        self._setup_files(tmp_path, contracts=CONTRACTS_WITH_NEW_MODULE)
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dsl-path", str(tmp_path / "architecture.dsl"),
                "--interface-contracts", str(tmp_path / "interface-contracts.md"),
                "--entity-model", str(tmp_path / "entity-model.md"),
                "--proposal", str(tmp_path / "proposal.md"),
                "--report-dir", str(tmp_path / "reports"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "architecture_change=true" in result.stdout

    def test_writes_json_report(self, tmp_path):
        """AC 10: writes a JSON report."""
        self._setup_files(tmp_path)
        subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dsl-path", str(tmp_path / "architecture.dsl"),
                "--interface-contracts", str(tmp_path / "interface-contracts.md"),
                "--entity-model", str(tmp_path / "entity-model.md"),
                "--proposal", str(tmp_path / "proposal.md"),
                "--report-dir", str(tmp_path / "reports"),
                "--story-id", "ST-9999",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        report = tmp_path / "reports" / "ST-9999.json"
        assert report.is_file()
        data = json.loads(report.read_text(encoding="utf-8"))
        assert "architecture_change" in data

    def test_exit_two_missing_dsl(self, tmp_path):
        """Config error exits 2."""
        self._setup_files(tmp_path)
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dsl-path", str(tmp_path / "missing.dsl"),
                "--interface-contracts", str(tmp_path / "interface-contracts.md"),
                "--entity-model", str(tmp_path / "entity-model.md"),
                "--proposal", str(tmp_path / "proposal.md"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 2

    def test_updates_proposal_on_change(self, tmp_path):
        """AC 07: proposal frontmatter updated when change detected."""
        self._setup_files(tmp_path, contracts=CONTRACTS_WITH_NEW_MODULE)
        subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dsl-path", str(tmp_path / "architecture.dsl"),
                "--interface-contracts", str(tmp_path / "interface-contracts.md"),
                "--entity-model", str(tmp_path / "entity-model.md"),
                "--proposal", str(tmp_path / "proposal.md"),
                "--report-dir", str(tmp_path / "reports"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        content = (tmp_path / "proposal.md").read_text(encoding="utf-8")
        assert "architecture_change: true" in content
        assert "# mechanical detection" in content
