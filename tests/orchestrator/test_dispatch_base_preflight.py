"""Direct UC-12 assurance tests for the verify-base process boundary."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_VERIFY_BASE = _ROOT / "factory" / "scripts" / "verify-base"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, path: str, text: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    _git(repo, "add", path)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    base = _commit(repo, "base.txt", "base\n", "base")
    return repo, base


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(_VERIFY_BASE), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _marker(repo: Path) -> Path:
    return repo / ".current-work" / "verify-base-ok"


def test_UC_12_BR_044_abbreviated_declared_base_is_usage_error(tmp_path):
    repo, base = _repo(tmp_path)
    marker = _marker(repo)
    marker.parent.mkdir()
    marker.write_text("previous success\n", encoding="utf-8")

    result = _run(repo, "dev", "--expect-base", base[:12])

    assert result.returncode == 2
    assert "exact lowercase 40-character" in result.stderr
    assert not marker.exists()


def test_UC_12_BR_044_unknown_full_object_name_is_invocation_error(tmp_path):
    repo, _ = _repo(tmp_path)

    result = _run(repo, "dev", "--expect-base", "0" * 40)

    assert result.returncode == 2
    assert "BASE_ERROR" in result.stderr
    assert not _marker(repo).exists()


@pytest.mark.parametrize("invalid", ["uppercase", "short", "long", "nonhex"])
def test_UC_12_BR_044_noncanonical_declared_bases_are_usage_errors(tmp_path, invalid):
    repo, base = _repo(tmp_path)
    values = {
        "uppercase": base.upper(),
        "short": base[:-1],
        "long": f"{base}0",
        "nonhex": "g" * 40,
    }

    result = _run(repo, "dev", "--expect-base", values[invalid])

    assert result.returncode == 2
    assert not _marker(repo).exists()


def test_UC_12_BR_045_stale_target_blocks_and_clears_old_marker(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature")
    _git(repo, "switch", "-q", "dev")
    _commit(repo, "target.txt", "new target work\n", "advance target")
    _git(repo, "switch", "-q", "feature")
    marker = _marker(repo)
    marker.parent.mkdir()
    marker.write_text("previous success\n", encoding="utf-8")

    result = _run(repo, "dev", "--expect-base", base)

    assert result.returncode == 1
    assert "BASE_STALE" in result.stdout
    assert not marker.exists()


def test_UC_12_BR_045_wrong_declared_base_blocks_and_clears_old_marker(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "wrong", base)
    wrong = _commit(repo, "wrong.txt", "wrong branch\n", "wrong base")
    _git(repo, "switch", "-q", "-c", "feature", base)
    _commit(repo, "feature.txt", "feature work\n", "feature")
    marker = _marker(repo)
    marker.parent.mkdir()
    marker.write_text("previous success\n", encoding="utf-8")

    result = _run(repo, "dev", "--expect-base", wrong)

    assert result.returncode == 1
    assert "BASE_WRONG" in result.stdout
    assert not marker.exists()


def test_UC_12_BR_044_valid_exact_base_writes_matching_marker(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature")
    head = _commit(repo, "feature.txt", "feature work\n", "feature")

    result = _run(repo, "dev", "--expect-base", base)

    assert result.returncode == 0, result.stderr
    assert _marker(repo).read_text(encoding="utf-8") == (
        f"target=dev\nexpect_base={base}\nhead={head}\n"
    )


def test_UC_12_BR_045_unknown_target_is_invocation_error(tmp_path):
    repo, _ = _repo(tmp_path)

    result = _run(repo, "missing-target")

    assert result.returncode == 2
    assert "BASE_ERROR" in result.stderr
    assert not _marker(repo).exists()
