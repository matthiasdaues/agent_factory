"""Integration tests: each gate checks the core at its new path (CAL-09-IT-01).

Rule `Project maintainer's gates check the core at its new paths` in
docs/spec/features/core-artifact-layout.feature, Scenario Outline `Each gate fails on a
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
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, requires_docker

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


# --- CAO-07-IT-01: the report names the architecture agent as owner ------------

FORBIDDEN_IMPORT = {
    "docs/spec/dependency-rules.dsl": "payments must_not_depend_on ledger\n",
    "src/payments/pay.py": "from ledger import post\n",
}


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAO_07_IT_01_dependency_check_names_architecture_agent_as_owner(
    new_layout_gates: Path, seeded: bool
) -> None:
    if seeded:
        write_files(new_layout_gates, FORBIDDEN_IMPORT)
    result = run_gate(
        new_layout_gates,
        "dependency-check",
        "--source-root",
        "src",
        "--story-id",
        "ST-0355",
    )
    rows = json.loads(
        (new_layout_gates / ".current-work/dependency-check/ST-0355.json").read_text()
    )
    assert json.loads(result.stdout) == rows
    failures = [row for row in rows if row["pass_fail"] == "fail"]
    passes = [row for row in rows if row["pass_fail"] == "pass"]
    assert all("owner" not in row for row in passes), rows
    if seeded:
        assert result.returncode == 1, result.stderr
        assert len(rows) == 1, rows
        assert failures[0]["rule_name"] == "payments must_not_depend_on ledger"
        assert failures[0]["violating_import"]["file"] == "payments/pay.py"
        assert failures[0]["owner"] == "architecture-agent"
    else:
        assert result.returncode == 0, result.stderr
        assert failures == []
        assert len(passes) == 1, rows


# --- ST-0326 -------------------------------------------------------------------

FEATURE_FILE = "docs/spec/features/core-artifact-layout.feature"

STATE_MACHINES = """\
# State Machines

## Article

```text
State: DRAFT
On Publish:
  ChangeState(PUBLISHED)

State: PUBLISHED
  # terminal — no outbound transitions
```

```mermaid
stateDiagram-v2
    DRAFT --> PUBLISHED : Publish
```
"""

SCOPE_AND_STATE_FILES = {
    FEATURE_FILE: (
        "# scope: global\n"
        "Feature: Core artifact layout\n\n"
        "  Rule: Project maintainer's gates check the core at its new paths\n\n"
        "    Scenario: A gate runs\n"
        "      Given a migrated project\n"
        "      When the project maintainer runs a gate\n"
        "      Then the gate exits 0\n"
    ),
    "docs/spec/state-machines.md": STATE_MACHINES,
    "docs/spec/entity-model.md": (
        "---\nscope: global\n---\n\n# Entity Model\n\n## Article\n\n"
        "| Field | Type |\n| ----- | ---- |\n| id    | UUID |\n"
    ),
    "docs/spec/work/todo.md": "# Todo\n\n- [ ] Read the [retro](../../reviews/retro.md).\n",
    "docs/reviews/retro.md": "# Retrospective\n",
}


@pytest.fixture
def scope_and_state_layout(new_layout_gates: Path) -> Path:
    """`new-layout-gates` plus the files of scope-lint, statemachine-lint, and link-check."""
    write_files(new_layout_gates, SCOPE_AND_STATE_FILES)
    dsl = new_layout_gates / "docs/spec/architecture.dsl"
    dsl.write_text("# scope: global\n" + dsl.read_text())
    return new_layout_gates


def scope_findings(result: subprocess.CompletedProcess) -> set[str]:
    """The paths that scope-lint names in its JSON report."""
    return {finding["path"] for finding in json.loads(result.stdout)["findings"]}


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_scope_lint_reads_feature_files_from_spec_features(
    scope_and_state_layout: Path, seeded: bool
) -> None:
    if seeded:
        feature = scope_and_state_layout / FEATURE_FILE
        feature.write_text(feature.read_text().split("\n", 1)[1])
    result = run_gate(scope_and_state_layout, "scope-lint", "--format", "json")
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode == 1, output
        assert scope_findings(result) == {FEATURE_FILE}
    else:
        assert result.returncode == 0, output


def test_CAL_09_scope_lint_checks_dsl_and_entity_model_at_new_paths(
    scope_and_state_layout: Path,
) -> None:
    """Without a scope declaration, the DSL and the entity model each give a finding."""
    dsl = scope_and_state_layout / "docs/spec/architecture.dsl"
    dsl.write_text(dsl.read_text().split("\n", 1)[1])
    write_files(scope_and_state_layout, {"docs/spec/entity-model.md": "# Entity Model\n"})
    result = run_gate(scope_and_state_layout, "scope-lint", "--format", "json")
    assert result.returncode == 1, result.stdout + result.stderr
    assert scope_findings(result) == {
        "docs/spec/architecture.dsl",
        "docs/spec/entity-model.md",
    }


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_statemachine_lint_reads_state_machines_from_spec(
    scope_and_state_layout: Path, seeded: bool
) -> None:
    if seeded:
        path = scope_and_state_layout / "docs/spec/state-machines.md"
        path.write_text(
            path.read_text().replace(
                "    DRAFT --> PUBLISHED : Publish\n",
                "    DRAFT --> PUBLISHED : Publish\n    DRAFT --> ARCHIVED : Archive\n",
            )
        )
    result = run_gate(
        scope_and_state_layout, "statemachine-lint", "--spec-dir", "docs/spec"
    )
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode == 1, output
        assert "SM-TRANS" in output
        assert "state-machines.md" in output
    else:
        assert result.returncode == 0, output
        assert "SM-NO-MERMAID" not in output


@pytest.mark.parametrize("seeded", [False, True], ids=["clean", "seeded-error"])
def test_CAL_09_link_check_reads_todo_from_spec_work(
    scope_and_state_layout: Path, seeded: bool
) -> None:
    if seeded:
        write_files(
            scope_and_state_layout,
            {"docs/spec/work/todo.md": "# Todo\n\n- [ ] Read [it](../../reviews/missing.md).\n"},
        )
    result = run_gate(scope_and_state_layout, "link-check", "docs/spec/work/todo.md")
    output = result.stdout + result.stderr
    if seeded:
        assert result.returncode == 1, output
        assert "missing.md" in output
    else:
        assert result.returncode == 0, output


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


# --- CAL-14-IT-01: every gate passes on the migrated factory repository --------
# Each gate runs by its own command, not through pre-commit, because
# .pre-commit-config.yaml has no hook for scope-lint, dependency-check, or
# structurizr and runs arch-lint with --no-validate.


def repository_markdown() -> list[str]:
    """Every tracked Markdown file under docs/, outside docs/~archive/."""
    listed = subprocess.run(
        ["git", "ls-files", "docs/*.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return [path for path in listed if not path.startswith("docs/~archive/")]


REPOSITORY_GATES = {
    "link-check": ("link-check",),
    # --no-validate: validation renders the diagrams into docs/assets/images
    # (T-0019). The container test below covers structurizr validate.
    "arch-lint": ("arch-lint", "--no-validate"),
    "dependency-check": ("dependency-check",),
    "spec-lint": ("spec-lint",),
    "statemachine-lint": ("statemachine-lint", "--spec-dir", "docs/spec"),
}

# scope-lint carries findings from before the migration (todo T-0010). The
# baseline is the content of story/ST-0343's parent, moved by the same
# migration script and checked against the same workstreams.
SCOPE_LINT_BASELINE = "2f1a955f"


@pytest.mark.spec("CAL-14")
@pytest.mark.parametrize("gate", REPOSITORY_GATES)
def test_CAL_14_gate_passes_on_the_factory_repository(gate: str) -> None:
    script, *args = REPOSITORY_GATES[gate]
    if gate == "link-check":
        args = repository_markdown()
    result = run_gate(REPO_ROOT, script, *args)
    assert result.returncode == 0, result.stdout + result.stderr


def git_output(root: Path, *args: str) -> str:
    """Run git in `root` and return its standard output."""
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=True
    ).stdout


def scope_lint_errors(root: Path) -> set[str]:
    """The ERROR lines that scope-lint prints when it runs from `root`."""
    output = run_gate(root, "scope-lint").stdout
    return {line for line in output.splitlines() if line.startswith("ERROR: ")}


@pytest.mark.spec("CAL-14")
def test_CAL_14_scope_lint_reports_no_finding_new_since_the_migration(
    tmp_path: Path,
) -> None:
    baseline = tmp_path / "baseline"
    baseline.mkdir()
    archive = subprocess.run(
        ["git", "archive", SCOPE_LINT_BASELINE, "backlog", "docs"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    ).stdout
    subprocess.run(["tar", "-x"], cwd=baseline, input=archive, check=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    for command in (
        ["git", "init", "-q"],
        ["git", "add", "-A"],
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"],
    ):
        subprocess.run(command, cwd=baseline, env=env, check=True)
    migration = run_gate(baseline, "migrate-spec-layout")
    assert migration.returncode == 0, migration.stdout + migration.stderr
    (baseline / ".agent-factory").symlink_to(REPO_ROOT / ".agent-factory")

    untracked = set(
        git_output(REPO_ROOT, "ls-files", "--others", "--exclude-standard").split()
    )
    new = sorted(
        line
        for line in scope_lint_errors(REPO_ROOT) - scope_lint_errors(baseline)
        if line.removeprefix("ERROR: ").split(" — ")[0] not in untracked
    )
    assert new == []


@requires_docker
@pytest.mark.container
@pytest.mark.spec("CAL-14")
def test_CAL_14_structurizr_validate_passes_on_the_factory_repository() -> None:
    result = run_gate(REPO_ROOT, "structurizr", "validate")
    assert result.returncode == 0, result.stdout + result.stderr
