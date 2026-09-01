"""Integration tests for factory/scripts/test-design-verify.

Covers ST-0188 acceptance criteria (test-design.feature Rule 14,
Scenarios 1-8 — QA strategy IDs TD-IT-01 through TD-IT-05):

  - Gate resolves the trace -> scope-map -> .feature -> Scenario chain
    (Scenario 1)
  - Gate exits 0 when every reachable Scenario has an assertion (Scenario 2)
  - Gate exits 1 and reports the missing Scenario when one lacks an
    assertion (Scenario 3)
  - Gate accepts valid waivers (Scenario 4)
  - Gate rejects waivers naming a non-existent test module (Scenario 5)
  - Gate validates non-owning stories' Prior Tests entries (Scenario 6)
  - Gate exits 0 with no findings when a story has neither section
    (Scenario 7)
  - Gate exits 2 on configuration error — unresolvable trace ID
    (Scenario 8)

Each test builds its own minimal story file, scope-map.md, and .feature
file under tmp_path, matching a fixture story that traces contract DOM-01.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent.parent
    / "factory"
    / "scripts"
    / "test-design-verify"
)


def _load_module():
    """Import test-design-verify as a Python module for unit-level checks
    on its internal resolution and validation functions."""
    loader = importlib.machinery.SourceFileLoader("test_design_verify_mod", str(SCRIPT))
    spec = importlib.util.spec_from_file_location(
        "test_design_verify_mod", str(SCRIPT), loader=loader
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["test_design_verify_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


tdv = _load_module()


# ---------------------------------------------------------------------------
# Fixture builders — minimal scope-map, .feature file, story files
# ---------------------------------------------------------------------------

FEATURE_TEXT = """\
Feature: Domain contracts

  Rule: Domain enforces entity uniqueness
    # @src/domain.py::Entity

    Scenario: Entity uniqueness is enforced on creation
      Given an entity with a duplicate key
      When the entity is created
      Then the creation is rejected
"""

SCOPE_MAP_TEXT = """\
# Scope Map — Fixture

| Rule                                  | Status    | Confidence | Sources                      | Feature Link |
| -------------------------------------- | --------- | ---------- | ----------------------------- | ------------- |
| Domain enforces entity uniqueness      | specified |            | [DOM-01](domain.feature)      |               |
"""


def _write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    """Write scope-map.md and domain.feature under tmp_path/spec. Returns
    (scope_map_path, spec_dir)."""
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir()
    scope_map_path = tmp_path / "scope-map.md"
    scope_map_path.write_text(SCOPE_MAP_TEXT, encoding="utf-8")
    (spec_dir / "domain.feature").write_text(FEATURE_TEXT, encoding="utf-8")
    return scope_map_path, spec_dir


def _write_story(
    tmp_path: Path,
    *,
    story_id: str = "ST-0200",
    traces: str = "[DOM-01]",
    body: str = "",
) -> Path:
    story_path = tmp_path / f"{story_id}.md"
    story_path.write_text(
        f"""---
id: {story_id}
epic: Fixture epic
title: Fixture story
tier: standard
status: pending
deps: []
traces: {traces}
outputs: []
quality-gates: []
---

# Fixture story

## Demo

n/a

## Acceptance Criteria

- n/a

{body}
""",
        encoding="utf-8",
    )
    return story_path


def _run_gate(
    tmp_path: Path,
    story_path: Path,
    scope_map_path: Path,
    spec_dir: Path,
    *,
    repo_root: Path | None = None,
    story_id: str | None = None,
) -> subprocess.CompletedProcess[str]:
    args = [
        sys.executable,
        str(SCRIPT),
        "--story",
        str(story_path),
        "--scope-map",
        str(scope_map_path),
        "--spec-dir",
        str(spec_dir),
        "--repo-root",
        str(repo_root or tmp_path),
        "--report-dir",
        str(tmp_path / "reports"),
    ]
    if story_id:
        args += ["--story-id", story_id]
    return subprocess.run(args, capture_output=True, text=True)


def _report(tmp_path: Path, story_id: str) -> dict:
    report_path = tmp_path / "reports" / f"{story_id}.json"
    return json.loads(report_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Scenario 1 — resolves the trace-to-scenario chain
# ---------------------------------------------------------------------------


def test_gate_resolves_trace_to_scenario_chain(tmp_path: Path) -> None:
    """The gate reads traces:, looks up scope-map.md, reads the .feature
    file, and collects the Scenarios under the matching Rule."""
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    scope_rows = tdv.parse_scope_map(scope_map_path.read_text(encoding="utf-8"))

    resolved = tdv.resolve_trace("DOM-01", scope_rows, spec_dir)

    assert resolved.trace_id == "DOM-01"
    assert resolved.feature_path == spec_dir / "domain.feature"
    assert resolved.rule_text == "Domain enforces entity uniqueness"
    assert resolved.scenarios == ["Entity uniqueness is enforced on creation"]


# ---------------------------------------------------------------------------
# Scenario 2 — passes when all owned contracts have assertions
# ---------------------------------------------------------------------------


def test_gate_passes_when_all_owned_contracts_have_assertions(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Test Design

- **Contract:** `Entity uniqueness is enforced on creation` (domain.feature Rule 1, Scenario 1) -- risk class: `critical`

Given an entity with a duplicate key
When the entity is created
Then the creation is rejected
Forbidden a duplicate entity being persisted
"""
    story_path = _write_story(tmp_path, body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "ST-0200")
    assert report["passed"] is True
    assert report["findings"] == []


# ---------------------------------------------------------------------------
# Scenario 3 — fails when an owned contract lacks an assertion
# ---------------------------------------------------------------------------


def test_gate_fails_when_owned_contract_lacks_assertion(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Test Design

(no scenarios recorded here)
"""
    story_path = _write_story(tmp_path, body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )

    assert result.returncode == 1
    report = _report(tmp_path, "ST-0200")
    assert report["passed"] is False
    assert len(report["findings"]) == 1
    finding = report["findings"][0]
    assert finding["kind"] == "missing_assertion"
    assert finding["scenario"] == "Entity uniqueness is enforced on creation"
    assert "Entity uniqueness is enforced on creation" in result.stderr


# ---------------------------------------------------------------------------
# Scenario 4 — accepts valid waivers
# ---------------------------------------------------------------------------


def test_gate_accepts_valid_waiver(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)

    # The named test module must exist relative to --repo-root.
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_domain.py").write_text(
        "def test_entity_uniqueness():\n    assert True\n", encoding="utf-8"
    )

    body = """\
#### Test Design

> Waiver: DOM-01 -- owned by tests/test_domain.py::test_entity_uniqueness
"""
    story_path = _write_story(tmp_path, body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "ST-0200")
    assert report["passed"] is True
    assert report["findings"] == []


# ---------------------------------------------------------------------------
# Scenario 5 — rejects waivers naming a non-existent module
# ---------------------------------------------------------------------------


def test_gate_rejects_waiver_with_nonexistent_module(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Test Design

> Waiver: DOM-01 -- owned by tests/test_domain.py::test_entity_uniqueness
"""
    story_path = _write_story(tmp_path, body=body)

    # No tests/ directory created -- the named module does not exist.
    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )

    assert result.returncode == 1
    report = _report(tmp_path, "ST-0200")
    assert report["passed"] is False
    kinds = {f["kind"] for f in report["findings"]}
    assert "invalid_waiver" in kinds
    assert "invalid_waiver" in result.stderr


def test_gate_waiver_then_passes_once_module_created(tmp_path: Path) -> None:
    """Demo flow: an invalid waiver fails the gate; creating the named test
    module and rerunning makes it pass -- exercises the same invalid-waiver
    path as a regression check on the fix."""
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Test Design

> Waiver: DOM-01 -- owned by tests/test_domain.py::test_entity_uniqueness
"""
    story_path = _write_story(tmp_path, body=body)

    first = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )
    assert first.returncode == 1

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_domain.py").write_text(
        "def test_entity_uniqueness():\n    assert True\n", encoding="utf-8"
    )

    second = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0200"
    )
    assert second.returncode == 0, second.stderr


# ---------------------------------------------------------------------------
# Scenario 6 — validates non-owning story Prior Tests entries
# ---------------------------------------------------------------------------


def test_gate_validates_prior_tests_entry_resolves(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_domain.py").write_text(
        "def test_entity_uniqueness():\n    assert True\n", encoding="utf-8"
    )

    body = """\
#### Prior Tests

- `Entity uniqueness is enforced on creation` -- owned by ST-0180 at
  `tests/test_domain.py::test_entity_uniqueness`
"""
    story_path = _write_story(tmp_path, body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0201"
    )

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "ST-0201")
    assert report["passed"] is True


def test_gate_matches_prior_tests_entry_keyed_by_trace_id(tmp_path: Path) -> None:
    """A Prior Tests bullet may key on the trace ID itself rather than the
    scenario title -- the format the test-design skill emits at step 9
    (`- DOM-01 -- owned by ST-0180 at \\`tests/test_domain.py::...\\``)."""
    scope_map_path, spec_dir = _write_fixture(tmp_path)

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_domain.py").write_text(
        "def test_entity_uniqueness():\n    assert True\n", encoding="utf-8"
    )

    body = """\
#### Prior Tests

- DOM-01 -- owned by ST-0180 at `tests/test_domain.py::test_entity_uniqueness`
"""
    story_path = _write_story(tmp_path, body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0201"
    )

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "ST-0201")
    assert report["passed"] is True


def test_gate_rejects_prior_tests_entry_that_does_not_resolve(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Prior Tests

- `Entity uniqueness is enforced on creation` -- owned by ST-0180 at
  `tests/test_domain.py::test_entity_uniqueness`
"""
    story_path = _write_story(tmp_path, body=body)

    # No tests/ directory -- the module referenced does not exist.
    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0201"
    )

    assert result.returncode == 1
    report = _report(tmp_path, "ST-0201")
    assert report["passed"] is False
    kinds = {f["kind"] for f in report["findings"]}
    assert "invalid_prior_test" in kinds or "missing_assertion" in kinds


# ---------------------------------------------------------------------------
# Scenario 7 — skips stories with no test-design output
# ---------------------------------------------------------------------------


def test_gate_skips_story_without_test_design_output(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    story_path = _write_story(tmp_path, body="")

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0202"
    )

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "ST-0202")
    assert report["passed"] is True
    assert report["skipped"] is True
    assert report["findings"] == []


# ---------------------------------------------------------------------------
# Scenario 8 — exits with code 2 on configuration error
# ---------------------------------------------------------------------------


def test_gate_exits_2_on_unresolvable_trace_id(tmp_path: Path) -> None:
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = """\
#### Test Design

- **Contract:** `Entity uniqueness is enforced on creation` (domain.feature Rule 1, Scenario 1)
"""
    story_path = _write_story(tmp_path, traces="[NOPE-99]", body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0203"
    )

    assert result.returncode == 2
    report = _report(tmp_path, "ST-0203")
    assert report["passed"] is False
    assert report["config_errors"]
    assert "NOPE-99" in report["config_errors"][0]
    assert "NOPE-99" in result.stderr


def test_gate_exits_2_when_shorthand_rule_missing_from_scope_map(
    tmp_path: Path,
) -> None:
    """The <feature>.feature/Rule-<NN> shorthand still requires a matching
    scope-map entry -- a Rule number beyond what the scope map has
    catalogued is a configuration error, not a silent pass."""
    scope_map_path, spec_dir = _write_fixture(tmp_path)
    body = "#### Test Design\n\n(irrelevant)\n"
    story_path = _write_story(tmp_path, traces="[domain.feature/Rule-02]", body=body)

    result = _run_gate(
        tmp_path, story_path, scope_map_path, spec_dir, story_id="ST-0204"
    )

    assert result.returncode == 2
    report = _report(tmp_path, "ST-0204")
    assert report["config_errors"]


# ---------------------------------------------------------------------------
# Additional coverage: the real Rule-NN shorthand against this repo's own
# scope-map.md and test-design.feature -- a regression check that the
# resolution chain works against the actual artifacts it was designed for.
# ---------------------------------------------------------------------------


def test_gate_resolves_real_repo_rule_shorthand() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    scope_map_path = repo_root / "docs" / "spec" / "scope-map.md"
    spec_dir = repo_root / "docs" / "spec"

    scope_rows = tdv.parse_scope_map(scope_map_path.read_text(encoding="utf-8"))
    resolved = tdv.resolve_trace("test-design.feature/Rule-14", scope_rows, spec_dir)

    assert (
        resolved.rule_text
        == "Test-design-verify gate validates test-design completeness"
    )
    assert "Gate resolves trace-to-scenario chain" in resolved.scenarios
    assert "Gate exits with code 2 on configuration error" in resolved.scenarios
    assert len(resolved.scenarios) == 8
