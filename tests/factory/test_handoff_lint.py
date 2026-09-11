"""Public-command contract tests for handoff-lint."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "factory"
    / "scripts"
    / "handoff-lint"
)


def _repository(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test User"], check=True
    )
    artifact = repo / "proposal.md"
    artifact.write_text("# Accepted proposal\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "proposal.md"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "test fixture"],
        check=True,
        capture_output=True,
    )
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return repo, head


def _handoff(repo: Path, head: str, boundary: str) -> Path:
    handoff = repo / "handoff.md"
    handoff.write_text(
        f"""# Phase Handoff

## Boundary

Outgoing phase: proposal intake
Incoming phase: requirements
Boundary: {boundary}

## Repository state

Checkout: {repo}
Branch: master
HEAD: {head}
Upstream: none
Upstream SHA: none
Ahead: 0
Behind: 0
Working tree: handoff.md is untracked and owned by this handoff
Retained work: none

## Decisions and open items

Decisions: the accepted proposal enters requirements
Open items: none

## Artifacts

- proposal.md

## Gate and verification evidence

Gates: proposal review passed
Verification: accepted proposal inspected

## Next action

Derive the requirements artifacts from proposal.md.

## Semantic review

Reviewer: test reviewer
Status: passed
Evidence: compared against proposal.md
""",
        encoding="utf-8",
    )
    return handoff


def _run(repo: Path, handoff: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(handoff), "--repo-root", str(repo)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_proposal_intake_to_requirements_boundary_is_accepted(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head, "proposal intake -> requirements"))

    assert result.returncode == 0, result.stderr
    assert "structurally valid" in result.stdout


def test_unregistered_boundary_remains_rejected(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head, "proposal intake -> deployment"))

    assert result.returncode != 0
    assert "HO-BOUNDARY" in result.stderr
