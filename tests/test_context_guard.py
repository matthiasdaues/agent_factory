"""Contract tests for the step-guard context budget check."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

STEP_GUARD = (
    Path(__file__).resolve().parent.parent / "factory" / "scripts" / "step-guard"
)


def _guard_env(tmp_path: Path) -> dict[str, str]:
    """Return a subprocess environment isolated from host hooks/config."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _write_file(path: Path, size: int) -> None:
    """Write a file with a fixed byte size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def _write_manifest(cwd: Path, text: str) -> None:
    """Write the active step manifest for a test repo."""
    manifest = cwd / ".current_work" / "current-step.yml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text)


def _run_context(
    cwd: Path, event: dict[str, object]
) -> subprocess.CompletedProcess[str]:
    """Invoke step-guard in context mode with one JSON event on stdin."""
    return subprocess.run(
        [str(STEP_GUARD), "--guard-type", "context"],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=_guard_env(cwd),
        check=False,
    )


def test_context_allows_exact_budget_with_explicit_inputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_file(repo / "src" / "foo.py", 8)
    _write_file(repo / "src" / "bar.py", 4)

    result = _run_context(
        repo,
        {
            "tool": "Spawn",
            "inputs": ["src/foo.py", "src/bar.py"],
            "max_input_tokens": 3,
        },
    )

    assert result.returncode == 0, result.stderr


def test_context_denies_over_budget_and_reports_estimate(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_file(repo / "src" / "foo.py", 8)
    _write_file(repo / "src" / "bar.py", 8)

    result = _run_context(
        repo,
        {
            "tool": "Spawn",
            "inputs": ["src/foo.py", "src/bar.py"],
            "max_input_tokens": 3,
        },
    )

    assert result.returncode == 1
    assert "estimated 4 tokens" in result.stderr
    assert "budget 3" in result.stderr


def test_context_allows_zero_byte_files_and_empty_inputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_file(repo / "src" / "empty.py", 0)

    result = _run_context(
        repo,
        {
            "tool": "Spawn",
            "inputs": [],
            "max_input_tokens": 0,
        },
    )

    assert result.returncode == 0, result.stderr


def test_context_reads_inputs_and_budget_from_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_file(repo / "src" / "package" / "module.py", 8)
    _write_manifest(
        repo,
        "inputs:\n  - src/**/*.py\nmax_input_tokens: 2\n",
    )

    result = _run_context(repo, {"tool": "Spawn"})

    assert result.returncode == 0, result.stderr
