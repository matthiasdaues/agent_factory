"""Integration tests for the step-guard script.

Each test runs the executable as a subprocess against a temporary working
tree and step manifest.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

STEP_GUARD = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "step-guard"
)


def _guard_env(tmp_path: Path) -> dict[str, str]:
    """Return a subprocess environment isolated from host hooks/config."""
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(tmp_path),
    }


def _run_guard(
    guard_type: str,
    cwd: Path,
    *,
    event: dict[str, object] | None = None,
    tool: str = "Read",
    path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke step-guard with one JSON tool event on stdin."""
    payload: dict[str, object] = {"tool": tool}
    if event is not None:
        payload.update(event)
    elif path is not None:
        payload["path"] = path
    return subprocess.run(
        [str(STEP_GUARD), "--guard-type", guard_type],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=_guard_env(cwd),
        check=False,
    )


def _write_manifest(cwd: Path, text: str) -> None:
    """Write the active step manifest for a test repo."""
    manifest = cwd / ".current-work" / "current-step.yml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text)


def test_read_allows_declared_input(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo,
        """inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n""",
    )

    result = _run_guard("read", repo, path="docs/spec/prd.md")

    assert result.returncode == 0, result.stderr


def test_read_allows_factory_prefix(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("read", repo, path="factory/rulebooks/rules.md")

    assert result.returncode == 0, result.stderr


def test_read_denies_out_of_scope_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("read", repo, path="src/main.py")

    assert result.returncode == 1


def test_read_allows_when_manifest_absent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = _run_guard("read", repo, path="src/main.py")

    assert result.returncode == 0, result.stderr


def test_write_allows_declared_output(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("write", repo, tool="Write", path="src/module_a/handler.py")

    assert result.returncode == 0, result.stderr


def test_write_allows_findings(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("write", repo, tool="Write", path="docs/findings/IMPL-0001.md")

    assert result.returncode == 0, result.stderr


def test_write_allows_gate_marker(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard(
        "write", repo, tool="Write", path=".current-work/verify-base-ok"
    )

    assert result.returncode == 0, result.stderr


def test_write_denies_ledger(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "write", repo, tool="Write", path=".current-work/dispatch-ledger.yaml"
    )

    assert result.returncode == 1


def test_write_denies_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "write", repo, tool="Write", path=".current-work/current-step.yml"
    )

    assert result.returncode == 1


def test_write_denies_out_of_scope_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("write", repo, tool="Write", path="docs/spec/prd.md")

    assert result.returncode == 1


def test_write_allows_when_manifest_absent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = _run_guard("write", repo, tool="Write", path="docs/spec/prd.md")

    assert result.returncode == 0, result.stderr


def test_security_denies_ledger_even_if_output_glob_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "write", repo, tool="Write", path=".current-work/dispatch-ledger.yaml"
    )

    assert result.returncode == 1


def test_security_denies_manifest_even_if_output_glob_matches(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "write", repo, tool="Write", path=".current-work/current-step.yml"
    )

    assert result.returncode == 1


def test_bash_allows_declared_read_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard(
        "bash",
        repo,
        tool="Bash",
        event={"command": "cat docs/spec/prd.md"},
    )

    assert result.returncode == 0, result.stderr


def test_bash_allows_declared_write_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard(
        "bash",
        repo,
        tool="Bash",
        event={"command": "echo x > src/module_a/new.py"},
    )

    assert result.returncode == 0, result.stderr


def test_bash_denies_out_of_scope_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard(
        "bash",
        repo,
        tool="Bash",
        event={"command": "echo x > docs/spec/prd.md"},
    )

    assert result.returncode == 1


def test_bash_denies_manifest_write(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "bash",
        repo,
        tool="Bash",
        event={"command": "tee .current-work/current-step.yml"},
    )

    assert result.returncode == 1


def test_bash_denies_ledger_write(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(
        repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - .current-work/**\n"
    )

    result = _run_guard(
        "bash",
        repo,
        tool="Bash",
        event={"command": "echo x > .current-work/dispatch-ledger.yaml"},
    )

    assert result.returncode == 1


def test_bash_allows_opaque_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_manifest(repo, "inputs:\n  - docs/spec/prd.md\noutputs:\n  - src/**/*.py\n")

    result = _run_guard("bash", repo, tool="Bash", event={"command": "git status"})

    assert result.returncode == 0, result.stderr
