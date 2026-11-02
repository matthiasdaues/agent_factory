"""Integration tests: each gate checks the core at its new path (CAL-09-IT-01).

Rule `Project maintainer's gates check the core at its new paths` in
docs/spec/core-artifact-layout.feature, Scenario Outline `Each gate fails on a
deliberate error at the new path`.

Every gate runs as a subprocess with its default paths, from the root of the
fixture `new-layout-gates`. Each gate has one test function with a clean case
and a seeded-error case. A story that adds a gate adds its own test function
and writes its own extra files with `write_files`; it does not change the
base fixture or another gate's test.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR, requires_docker

# --- Fixture `new-layout-gates` ------------------------------------------------

THEME = """\
{
  "name": "default",
  "elements": [{ "tag": "Element", "background": "#ffffff" }]
}
"""

ARCHITECTURE_DSL = """\
workspace "Payments" {
    model {
        payments = softwareSystem "payments" {
            api = container "API" {
                checkout = component "Checkout"
            }
            db = container "Database" {
                store = component "Store"
            }
        }
        checkout -> store "Reads from"
    }
    views {
        container payments "Containers" {
            include *
        }
        theme ../assets/themes/default/theme.json
    }
}
"""

CHAPTER_5 = """\
# 5. Building Block View

## 5.1 Containers

The software system payments has two containers: API and Database.

## 5.2 Components

| Component | Container | Responsibility       |
| --------- | --------- | -------------------- |
| Checkout  | API       | Takes payments.      |
| Store     | Database  | Keeps payment data.  |
"""

DEPENDENCY_RULES = """\
# The API must not reach into the database module.
payments.api must_not_depend_on payments.db
"""

BASE_FILES = {
    "docs/spec/architecture.dsl": ARCHITECTURE_DSL,
    "docs/assets/themes/default/theme.json": THEME,
    "docs/arc42/05_building_block_view.md": CHAPTER_5,
    "docs/spec/dependency-rules.dsl": DEPENDENCY_RULES,
    "src/payments/__init__.py": "",
    "src/payments/db.py": "def connect():\n    return None\n",
    "src/payments/api.py": "def pay():\n    return None\n",
}


def write_files(root: Path, files: dict[str, str]) -> None:
    """Write each relative path of `files` under `root`."""
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


@pytest.fixture
def new_layout_gates(tmp_path: Path) -> Path:
    """The fixture `new-layout-gates`: a project in the new layout without errors."""
    root = tmp_path / "new-layout-gates"
    write_files(root, BASE_FILES)
    return root


def run_gate(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    """Run a factory gate from the fixture root with its default paths."""
    path = SOURCE_SCRIPTS_DIR / script
    command = [str(path), *args]
    if path.read_text(encoding="utf-8").startswith("#!/usr/bin/env -S uv"):
        command = [sys.executable, str(path), *args]
    env = {k: v for k, v in os.environ.items() if not k.startswith("STRUCTURIZR_")}
    return subprocess.run(
        command, cwd=root, env=env, capture_output=True, text=True, timeout=300
    )


# --- arch-lint -----------------------------------------------------------------


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_arch_lint_reads_dsl_from_spec_and_chapter5_from_arc42(
    new_layout_gates: Path, seeded: bool
) -> None:
    if seeded:
        dsl = new_layout_gates / "docs/spec/architecture.dsl"
        dsl.write_text(
            dsl.read_text().replace(
                'store = component "Store"',
                'store = component "Store"\n                refunds = component "Refunds"',
            )
        )
    result = run_gate(new_layout_gates, "arch-lint", "--no-validate")
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode == 1, output
        assert "component 'Refunds' is in architecture.dsl but not in chapter 5" in output
    else:
        assert result.returncode == 0, output
        assert "ARCH-COUPLE" not in output
        assert "ARCH-MISSING" not in output


# --- structurizr validate ------------------------------------------------------


@requires_docker
@pytest.mark.container
@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_structurizr_validate_reads_dsl_from_spec(
    new_layout_gates: Path, seeded: bool
) -> None:
    if seeded:
        dsl = new_layout_gates / "docs/spec/architecture.dsl"
        dsl.write_text(
            dsl.read_text().replace(
                'checkout -> store "Reads from"', 'checkout -> ledger "Reads from"'
            )
        )
    result = run_gate(new_layout_gates, "structurizr", "validate")
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode != 0, output
        assert '"ledger" does not exist' in output
    else:
        assert result.returncode == 0, output


# --- dependency-check ----------------------------------------------------------


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_dependency_check_reads_rules_from_spec(
    new_layout_gates: Path, seeded: bool
) -> None:
    if seeded:
        write_files(
            new_layout_gates,
            {"src/payments/api.py": "from payments.db import connect\n"},
        )
    result = run_gate(
        new_layout_gates,
        "dependency-check",
        "--source-root",
        "src",
        "--story-id",
        "ST-0325",
    )
    report = new_layout_gates / ".current-work/dependency-check/ST-0325.json"
    rows = json.loads(report.read_text())
    outcomes = {row["pass_fail"] for row in rows}
    if seeded:
        assert result.returncode == 1, result.stderr
        assert "fail" in outcomes
    else:
        assert result.returncode == 0, result.stderr
        assert outcomes == {"pass"}


# --- ST-0327 ---

SPEC_LINT_FILES = {
    "docs/spec/scope-map.md": "# Scope Map\n",
    "docs/spec/entity-model.md": (
        "# Entity Model\n\n```mermaid\nerDiagram\nMERCHANT {\n  string name\n}\n```\n"
    ),
    "docs/spec/validation-rules.md": (
        "# Validation Rules\n\n- **BR-001**: A payout is positive.\n"
    ),
    "docs/spec/features/payments.feature": (
        "Feature: Payments\n  # BR-001\n  Scenario: Merchant receives a payout\n"
    ),
}


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_spec_lint_reads_validation_rules_from_spec(
    new_layout_gates: Path, seeded: bool
) -> None:
    write_files(new_layout_gates, SPEC_LINT_FILES)
    if seeded:
        rules = new_layout_gates / "docs/spec/validation-rules.md"
        rules.write_text(rules.read_text() + "\nA payout follows BR-099.\n")
    result = run_gate(new_layout_gates, "spec-lint")
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode == 1, output
        assert "TRACE002" in output
        assert "BR-099" in output
    else:
        assert result.returncode == 0, output
        assert "[ERROR" not in output
