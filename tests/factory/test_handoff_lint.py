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


def _handoff(
    repo: Path,
    head: str,
    boundary: str = "architecture-agent -> architecture-review-agent",
    *,
    title: str = "# Handoff",
    outgoing: str = "Outgoing activity: architecture-agent",
    incoming: str = "Incoming activity: architecture-review-agent",
) -> Path:
    handoff = repo / "handoff.md"
    handoff.write_text(
        f"""{title}

## Boundary

{outgoing}
{incoming}
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

Review the architecture against proposal.md.

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


def test_activity_handoff_between_agents_is_accepted(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head))

    assert result.returncode == 0, result.stderr
    assert "structurally valid" in result.stdout


def test_unicode_arrow_and_case_in_boundary_are_accepted(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(
        repo, _handoff(repo, head, "Architecture-Agent → architecture-review-agent")
    )

    assert result.returncode == 0, result.stderr


def test_boundary_that_differs_from_declared_activities_is_rejected(
    tmp_path: Path,
) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head, "architecture-agent -> planning-agent"))

    assert result.returncode == 1
    assert "HO-BOUNDARY" in result.stderr


def test_boundary_without_arrow_is_rejected(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head, "architecture-agent to reviewer"))

    assert result.returncode == 1
    assert "HO-BOUNDARY" in result.stderr


def test_phase_handoff_title_is_rejected(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    result = _run(repo, _handoff(repo, head, title="# Phase Handoff"))

    assert result.returncode == 1
    assert "HO-TITLE" in result.stderr


def test_phase_fields_are_rejected(tmp_path: Path) -> None:
    repo, head = _repository(tmp_path)
    handoff = _handoff(
        repo,
        head,
        "proposal intake -> requirements",
        outgoing="Outgoing phase: proposal intake",
        incoming="Incoming phase: requirements",
    )
    result = _run(repo, handoff)

    assert result.returncode == 1
    assert "missing declared field in Boundary: Outgoing activity" in result.stderr
    assert "missing declared field in Boundary: Incoming activity" in result.stderr
