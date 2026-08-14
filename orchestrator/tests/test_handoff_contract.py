"""Acceptance tests for the validated phase handoff contract (ST-0065).

The tests exercise the user-visible CLI and installed Factory surfaces rather
than coupling to validator internals. They trace UC-11 and BR-037--BR-039/049.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_LINTER = _ROOT / "factory" / "scripts" / "handoff-lint"
_FORMAT = _ROOT / "factory" / "rulebooks" / "conventions" / "handoff-format.md"
_SKILL = _ROOT / "factory" / "skills" / "handoff" / "SKILL.md"
_INIT_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"

_loader = SourceFileLoader("init_factory_handoff_contract", str(_INIT_SCRIPT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = init_factory
_loader.exec_module(init_factory)


def _git(repo: Path, *args: str) -> str:
    """Run one deterministic local Git command and return its stdout."""
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    )
    return result.stdout.strip()


@pytest.fixture
def handoff_repo(tmp_path: Path) -> tuple[Path, str]:
    """Create a repository with one durable artifact and return its HEAD."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "story/ST-0065")
    _git(repo, "config", "user.email", "factory@example.invalid")
    _git(repo, "config", "user.name", "Agent Factory")
    artifact = repo / "docs" / "spec" / "prd.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("# Durable phase evidence\n")
    _git(repo, "add", "docs/spec/prd.md")
    _git(repo, "commit", "-m", "test fixture")
    return repo, _git(repo, "rev-parse", "HEAD")


def _valid_handoff(head: str) -> str:
    """Return the canonical lint-clean UC-11 handoff fixture."""
    return f"""# Phase Handoff

## Boundary

Outgoing phase: Requirements
Incoming phase: Specification review
Boundary: requirements -> review

## Repository state

Checkout: .
Branch: story/ST-0065
HEAD: {head}
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: clean
Retained work: none

## Decisions and open items

Decisions: The accepted proposal is the immutable design origin.
Open items: none

## Artifacts

- docs/spec/prd.md

## Gate and verification evidence

Gates: spec-lint passed with zero errors.
Verification: UC-11 acceptance scenarios passed.

## Next action

Start a fresh specification-review session; read this handoff first, then read
docs/spec/prd.md in bounded chunks and run spec-lint.

## Semantic review

Reviewer: pending assignment
Status: pending
Evidence: Compare this handoff with docs/spec/prd.md before phase closure.
"""


def _run_lint(handoff: Path, repo: Path) -> subprocess.CompletedProcess[str]:
    """Invoke handoff-lint through its public process boundary."""
    return subprocess.run(
        [str(_LINTER), str(handoff), "--repo-root", str(repo)],
        cwd=_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_UC_11_complete_handoff_passes_structural_lint_without_semantic_claim(
    handoff_repo: tuple[Path, str], tmp_path: Path
):
    """A complete restart contract passes but cannot certify losslessness."""
    repo, head = handoff_repo
    handoff = tmp_path / "HANDOFF.md"
    handoff.write_text(_valid_handoff(head))

    result = _run_lint(handoff, repo)

    assert result.returncode == 0, result.stderr
    assert "structurally valid" in result.stdout.lower()
    assert "semantic review" in result.stdout.lower()
    assert "does not" in result.stdout.lower()


def test_UC_11_lint_reports_every_detectable_defect_in_one_run(
    handoff_repo: tuple[Path, str], tmp_path: Path
):
    """BR-038 aggregates missing sections, fields, paths, and malformed data."""
    repo, _head = handoff_repo
    broken = """# Wrong Handoff

## Boundary

Outgoing phase: TBD
Boundary: invented -> nowhere

## Repository state

Checkout: .
Branch: wrong-branch
HEAD: ABC123
Upstream: none
Upstream SHA: 1234
Ahead: many
Behind: -1
Working tree: unknown

## Decisions and open items

Decisions: TBD

## Artifacts

- docs/missing.md

## Gate and verification evidence

Gates: TBD
"""
    handoff = tmp_path / "BROKEN-HANDOFF.md"
    handoff.write_text(broken)

    result = _run_lint(handoff, repo)

    assert result.returncode != 0
    report = result.stderr.lower()
    for expected in (
        "phase handoff title",
        "incoming phase",
        "next action",
        "semantic review",
        "retained work",
        "open items",
        "verification",
        "malformed head",
        "malformed upstream sha",
        "ahead",
        "behind",
        "missing referenced path",
    ):
        assert expected in report


def test_UC_11_machine_consumed_shas_require_exact_lowercase_40_hex(
    handoff_repo: tuple[Path, str], tmp_path: Path
):
    """Abbreviated and uppercase SHAs remain display-only, never contract data."""
    repo, head = handoff_repo
    handoff = tmp_path / "HANDOFF.md"
    handoff.write_text(_valid_handoff(head.upper()))

    result = _run_lint(handoff, repo)

    assert result.returncode != 0
    assert "malformed head" in result.stderr.lower()


def test_UC_11_declared_boundary_and_semantic_status_use_contract_values(
    handoff_repo: tuple[Path, str], tmp_path: Path
):
    """Malformed declared control fields are reported together."""
    repo, head = handoff_repo
    handoff = tmp_path / "HANDOFF.md"
    handoff.write_text(
        _valid_handoff(head)
        .replace("requirements -> review", "invented -> nowhere")
        .replace("Status: pending", "Status: maybe")
    )

    result = _run_lint(handoff, repo)

    assert result.returncode != 0
    assert "malformed boundary" in result.stderr.lower()
    assert "malformed semantic review status" in result.stderr.lower()


def test_UC_11_contract_defines_boundaries_restart_and_same_phase_exemption():
    """The canonical convention preserves the accepted proposal's boundary set."""
    contract = _FORMAT.read_text().lower()

    for boundary in (
        "requirements → review",
        "review → architecture",
        "architecture → review",
        "review → remedies",
        "remedies → planning",
        "planning → implementation",
    ):
        assert boundary in contract
    assert "must stop" in contract
    assert "fresh session" in contract
    assert "same phase" in contract
    assert "exempt" in contract


def test_UC_11_skill_preserves_dense_restart_contract_and_semantic_gate():
    """The CLI-neutral operation retains evidence and blocks premature closure."""
    skill = _SKILL.read_text().lower()

    for required in (
        "decisions",
        "open items",
        "artifact paths",
        "branch",
        "upstream",
        "gate",
        "verification",
        "next action",
        "40-character",
        "dense",
        "handoff-lint",
        "semantic review",
        "stop",
    ):
        assert required in skill
    assert "in-place transcript compaction" in skill


def test_UC_11_structural_lint_cannot_detect_undeclared_semantic_omission(
    handoff_repo: tuple[Path, str], tmp_path: Path
):
    """BR-049 assigns omitted-fact detection only to independent review."""
    repo, head = handoff_repo
    handoff = tmp_path / "HANDOFF.md"
    handoff.write_text(
        _valid_handoff(head).replace("immutable design origin", "origin")
    )

    result = _run_lint(handoff, repo)

    assert result.returncode == 0, result.stderr
    assert "semantic review" in result.stdout.lower()


@pytest.fixture
def installed_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Install Factory without unrelated runtime or hook provisioning."""
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: False
    )
    monkeypatch.setattr(init_factory, "pre_commit_install", lambda *_args: None)

    assert (
        init_factory.main(
            [
                "--target",
                str(tmp_path),
                "--source",
                str(_ROOT),
                "--project-name",
                "Handoff Consumer",
            ]
        )
        == 0
    )
    return tmp_path


@pytest.mark.parametrize(
    "skill_path",
    (
        ".claude/skills/handoff/SKILL.md",
        ".github/skills/handoff/SKILL.md",
        ".pi/skills/handoff/SKILL.md",
        ".agents/skills/handoff/SKILL.md",
    ),
)
def test_UC_11_installation_exposes_handoff_skill_for_every_supported_cli(
    installed_factory: Path, skill_path: str
):
    """All supported CLIs discover the one canonical handoff operation."""
    installed = installed_factory / skill_path

    assert installed.exists()
    assert installed.read_text() == _SKILL.read_text()
