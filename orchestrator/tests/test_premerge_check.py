"""Real-history UC-12 assurance tests for the shipped premerge-check gate."""

from __future__ import annotations

import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_PREMERGE_CHECK = _ROOT / "factory" / "scripts" / "premerge-check"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _commit(repo: Path, files: dict[str, str], message: str) -> str:
    for relative_path, text in files.items():
        target = repo / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        _git(repo, "add", relative_path)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "target")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    base = _commit(repo, {"base.txt": "base\n"}, "base")
    return repo, base


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(_PREMERGE_CHECK), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _marker(repo: Path) -> Path:
    return repo / ".agent-factory" / "premerge-check-ok"


def test_UC_12_BR_046_stale_target_reverting_branch_blocks(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature", base)
    _commit(repo, {"feature.txt": "feature\n"}, "feature")
    _git(repo, "switch", "-q", "target")
    _commit(repo, {"target.txt": "target advance\n"}, "advance target")

    result = _run(repo, "target", "feature")

    assert result.returncode == 1
    assert "BLOCK stale-base-signature" in result.stdout
    assert not _marker(repo).exists()


def test_UC_12_BR_046_out_of_scope_diff_blocks(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature", base)
    _commit(repo, {"outside.txt": "outside\n"}, "outside scope")

    result = _run(repo, "target", "feature", "--scope", "allowed")

    assert result.returncode == 1
    assert "BLOCK out-of-scope-paths: outside.txt" in result.stdout
    assert not _marker(repo).exists()


def test_UC_12_BR_046_file_count_blowout_blocks(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature", base)
    _commit(
        repo,
        {"one.txt": "1\n", "two.txt": "2\n", "three.txt": "3\n"},
        "three files",
    )

    result = _run(repo, "target", "feature", "--max-files", "2")

    assert result.returncode == 1
    assert "BLOCK file-count-blowout: 3 files changed" in result.stdout
    assert not _marker(repo).exists()


def test_UC_12_BR_046_clean_in_scope_diff_writes_matching_marker(tmp_path):
    repo, base = _repo(tmp_path)
    _git(repo, "switch", "-q", "-c", "feature", base)
    head = _commit(repo, {"allowed/change.txt": "allowed\n"}, "allowed change")

    result = _run(
        repo,
        "target",
        "feature",
        "--scope",
        "allowed",
        "--max-files",
        "2",
    )

    assert result.returncode == 0, result.stderr
    assert "premerge-check: PASS" in result.stdout
    assert _marker(repo).read_text(encoding="utf-8") == (
        f"branch=feature\nhead={head}\n"
    )


def test_UC_12_BR_046_unknown_branch_is_invocation_error(tmp_path):
    repo, _ = _repo(tmp_path)

    result = _run(repo, "target", "missing-branch")

    assert result.returncode == 2
    assert "unknown revision" in result.stderr.lower()
    assert not _marker(repo).exists()
