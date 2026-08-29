"""Integration tests for the step-guard shell adapter.

Verifies that the adapter correctly extracts paths from apply_patch-style
tool events (patch text with embedded file headers) and passes them to the
core step-guard script.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ADAPTER = (
    Path(__file__).resolve().parent.parent.parent
    / "factory"
    / "config"
    / "hooks"
    / "step-guard.sh"
)
STEP_GUARD = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "step-guard"
)


def _make_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo with factory/scripts/step-guard available."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    scripts = repo / "factory" / "scripts"
    scripts.mkdir(parents=True)
    guard_link = scripts / "step-guard"
    guard_link.symlink_to(STEP_GUARD)
    return repo


def _write_manifest(repo: Path, text: str) -> None:
    manifest = repo / ".current-work" / "current-step.yml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(text)


def _adapter_env(repo: Path) -> dict[str, str]:
    return {
        **os.environ,
        "GIT_CONFIG_NOSYSTEM": "1",
        "HOME": str(repo),
    }


def _run_adapter(
    repo: Path,
    guard_type: str,
    event: dict,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(ADAPTER)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=repo,
        env={**_adapter_env(repo), "GUARD_TYPE": guard_type},
        check=False,
    )


def test_adapter_allows_apply_patch_in_scope(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {
        "tool_input": {
            "patch": "*** Add File: src/handler.py\n+print('hello')\n",
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 0, result.stderr


def test_adapter_denies_apply_patch_out_of_scope(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {
        "tool_input": {
            "patch": "*** Add File: docs/spec/epics1.md\n+# Epic 1\n",
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 1


def test_adapter_denies_if_any_patch_path_out_of_scope(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {
        "tool_input": {
            "patch": (
                "*** Add File: src/ok.py\n+pass\n"
                "*** Add File: config/bad.yaml\n+key: val\n"
            ),
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 1


def test_adapter_allows_multiple_in_scope_patch_paths(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {
        "tool_input": {
            "patch": (
                "*** Add File: src/a.py\n+pass\n"
                "*** Update File: src/b.py\n@@ 1,1 @@\n-old\n+new\n"
            ),
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 0, result.stderr


def test_adapter_allows_when_no_manifest(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)

    event = {
        "tool_input": {
            "patch": "*** Add File: anywhere/file.txt\n+content\n",
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 0, result.stderr


def test_adapter_still_works_with_direct_path_field(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {"tool_input": {"file_path": "src/handler.py"}}
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 0, result.stderr


def test_adapter_handles_delete_file_header(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    _write_manifest(repo, "inputs:\n  - docs/**\noutputs:\n  - src/**/*.py\n")

    event = {
        "tool_input": {
            "patch": "*** Delete File: src/old.py\n",
        },
    }
    result = _run_adapter(repo, "write", event)

    assert result.returncode == 0, result.stderr
