"""Contract tests for the seven-part subagent handoff prompt."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

DISPATCH_SCRIPT = Path(__file__).resolve().parent.parent / "factory" / "scripts" / "dispatch"
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "factory" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
dispatch_lib = importlib.import_module("dispatch_lib")

Ledger = dispatch_lib.Ledger
StoryEntry = dispatch_lib.StoryEntry
StoryState = dispatch_lib.StoryState
ensure_handoff_contract_budget = dispatch_lib.ensure_handoff_contract_budget
handoff_contract_path = dispatch_lib.handoff_contract_path
normalized_token_count = dispatch_lib.normalized_token_count


def _git_env(tmp_path: Path) -> dict[str, str]:
    """Return a git environment isolated from user-level configuration."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _git(repo: Path, tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command inside the temporary repository."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=repo,
        check=False,
        env=_git_env(tmp_path),
    )


def _run_dispatch(*args: str, cwd: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the dispatch CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, str(DISPATCH_SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=False,
        env=_git_env(tmp_path),
    )


def _init_repo(tmp_path: Path) -> Path:
    """Create a minimal git repository for handoff-contract tests."""
    repo = tmp_path / "repo"
    repo.mkdir()

    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
    ):
        result = _git(repo, tmp_path, *args)
        assert result.returncode == 0, result.stderr

    config_dir = repo / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps({"project_name": "test", "test_command": "pytest -q"})
    )

    result = _git(repo, tmp_path, "add", "-A")
    assert result.returncode == 0, result.stderr
    result = _git(repo, tmp_path, "commit", "--no-verify", "-m", "initial")
    assert result.returncode == 0, result.stderr
    return repo


def _write_story(
    repo: Path,
    story_id: str,
    *,
    title: str,
    strategy: str,
    outputs: list[str],
    body_marker: str,
    seam_outputs: list[str] | None = None,
    impl_outputs: list[str] | None = None,
) -> None:
    """Write a backlog story with enough metadata for prompt rendering."""
    lines = [
        "---",
        f"id: {story_id}",
        f"title: {title}",
        "status: pending",
        "tier: economy",
        f"strategy: {strategy}",
        "traces:",
        "  - Feature: Subagent Handoff Contract",
        "outputs:",
    ]
    lines.extend(f"  - {item}" for item in outputs)
    if seam_outputs is not None:
        lines.append("seam_outputs:")
        lines.extend(f"  - {item}" for item in seam_outputs)
    if impl_outputs is not None:
        lines.append("impl_outputs:")
        lines.extend(f"  - {item}" for item in impl_outputs)
    lines.extend(["---", "", f"Acceptance criteria marker: {body_marker}"])
    story_path = repo / "backlog" / f"{story_id}.md"
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text("\n".join(lines) + "\n")


def _write_ledger(repo: Path, *entries: StoryEntry) -> Path:
    """Persist a dispatch ledger containing the provided entries."""
    ledger = Ledger()
    for entry in entries:
        ledger.stories[entry.id] = entry
    ledger_path = repo / ".agent-factory" / "dispatch-ledger.yaml"
    ledger.save(ledger_path)
    return ledger_path


def _load_ledger(repo: Path) -> Ledger:
    """Load the repository's default dispatch ledger."""
    return Ledger.load(repo / ".agent-factory" / "dispatch-ledger.yaml")


def _assert_seven_parts(text: str) -> None:
    """Assert the rendered contract contains all seven required parts."""
    assert "Part 1 — Outcome" in text
    assert "Part 2 — Workspace" in text
    assert "Part 3 — Allowed writes" in text
    assert "Part 4 — Forbidden actions" in text
    assert "Part 5 — Required checks" in text
    assert "Part 6 — Stop conditions" in text
    assert "Part 7 — Return envelope" in text


def test_prepare_wave_writes_seven_part_contracts_for_direct_and_seams_first(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    _write_story(
        repo,
        "ST-001",
        title="Direct handoff contract",
        strategy="direct",
        outputs=["factory/scripts/dispatch", "tests/test_handoff_contract.py"],
        body_marker="DIRECT-STORY-BODY",
    )
    _write_story(
        repo,
        "ST-002",
        title="Seams-first handoff contract",
        strategy="seams-first",
        outputs=["factory/scripts/dispatch_lib.py", "tests/test_handoff_contract.py"],
        seam_outputs=["tests/test_handoff_contract.py"],
        impl_outputs=["factory/scripts/dispatch_lib.py"],
        body_marker="SEAMS-FIRST-STORY-BODY",
    )
    _write_ledger(
        repo,
        StoryEntry(id="ST-001", wave=1, status=StoryState.PENDING),
        StoryEntry(id="ST-002", wave=1, status=StoryState.PENDING),
    )

    result = _run_dispatch("prepare-wave", "1", cwd=repo, tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr

    ledger = _load_ledger(repo)
    cases = [
        ("ST-001", "Direct handoff contract", "DIRECT-STORY-BODY"),
        ("ST-002", "Seams-first handoff contract", "SEAMS-FIRST-STORY-BODY"),
    ]
    for story_id, title, marker in cases:
        entry = ledger.stories[story_id]
        prompt_path = handoff_contract_path(
            Path(entry.worktree), entry.feature_branch, entry.branch
        )
        assert prompt_path.exists()
        text = prompt_path.read_text()

        _assert_seven_parts(text)
        assert f"- Story ID: {story_id}" in text
        assert f"- Title: {title}" in text
        assert f"backlog/{story_id}.md" in text
        assert marker not in text
        assert "Before any other work" not in text
        assert "sub-agent" not in text
        assert "workflow" not in text.lower()
        assert "- test_command: pytest -q" in text
        assert normalized_token_count(text) <= 800


def test_handoff_budget_gate_accepts_exactly_3200_bytes_and_rejects_3201() -> None:
    """The normalized-token budget uses a 3200-byte ceiling."""
    exact = "x" * 3200
    ensure_handoff_contract_budget(exact)
    assert normalized_token_count(exact) == 800

    with pytest.raises(ValueError):
        ensure_handoff_contract_budget(exact + "x")
