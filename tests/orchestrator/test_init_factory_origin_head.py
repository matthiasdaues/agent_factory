"""Tests for `fix_origin_head()` in `factory/scripts/init-factory` (ST-0159).

`origin/HEAD` is a local symref that should point at the remote's default
branch. It goes dangling — most often left pointing at `origin/master` after
a remote's default branch moved to `main` — whenever a clone predates that
rename, and tools that resolve `origin/HEAD` then fail silently. The retro
that spawned this story recorded 25 minutes lost to exactly that failure
across three QA agent runs.

`init-factory` is an extensionless script, loaded here the same way
test_init_factory_guardrail.py loads it: via importlib against the real
file. Each test builds a throwaway pair of real git repos (a bare "origin"
and a clone of it) with `subprocess` calls, exercising `fix_origin_head`
against real git state rather than mocked subprocess calls — the same
Chicago-school approach test_commit_safe.py takes for its git plumbing.

Three repair paths are covered, per the acceptance criteria:
  - valid symref: no-op
  - dangling symref, remote reachable: repaired via `git remote set-head
    origin --auto`
  - dangling symref, remote unreachable ("network unavailable"): repaired
    from local `refs/remotes/origin/*`, preferring `main` over `master`
Plus the "tolerates all failures gracefully" requirement: no `origin`
remote at all must not raise.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_origin_head", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("init_factory_origin_head", _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules["init_factory_origin_head"] = init_factory
_loader.exec_module(init_factory)


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )


def _make_bare_origin(tmp_path: Path, name: str, branch: str) -> Path:
    """Build a bare repo with one commit on `branch`, usable as a clone source."""
    work = tmp_path / f"{name}-work"
    work.mkdir()
    _git(work, "init", "-q", "-b", branch)
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    (work / "f.txt").write_text("x\n", encoding="utf-8")
    _git(work, "add", "f.txt")
    _git(work, "commit", "-q", "-m", "init")

    bare = tmp_path / f"{name}.git"
    _git(tmp_path, "clone", "-q", "--bare", str(work), str(bare))
    return bare


def _clone(tmp_path: Path, origin: Path, name: str) -> Path:
    repo = tmp_path / name
    _git(tmp_path, "clone", "-q", str(origin), str(repo))
    return repo


def _symref_target(repo: Path) -> str:
    return _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD").stdout.strip()


def _break_symref(
    repo: Path, bogus_target: str = "refs/remotes/origin/does-not-exist"
) -> None:
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", bogus_target)


def _make_unreachable(repo: Path, tmp_path: Path) -> None:
    """Point `origin` at a path with no repo — simulates network unavailable."""
    _git(repo, "remote", "set-url", "origin", str(tmp_path / "nonexistent.git"))


def test_valid_symref_is_noop(tmp_path):
    origin = _make_bare_origin(tmp_path, "origin", "main")
    repo = _clone(tmp_path, origin, "repo")
    before = _symref_target(repo)
    assert before == "refs/remotes/origin/main"

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)

    assert _symref_target(repo) == before
    assert any("no repair needed" in line for line in report)


def test_dangling_symref_repaired_via_network(tmp_path):
    origin = _make_bare_origin(tmp_path, "origin", "main")
    repo = _clone(tmp_path, origin, "repo")
    _break_symref(repo)
    assert _symref_target(repo) != "refs/remotes/origin/main"

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)

    assert _symref_target(repo) == "refs/remotes/origin/main"
    assert any("git remote set-head --auto" in line for line in report)


def test_offline_fallback_prefers_main_when_both_present(tmp_path):
    origin = _make_bare_origin(tmp_path, "origin", "main")
    repo = _clone(tmp_path, origin, "repo")

    # Give the repo a local origin/master tracking ref too, so both main and
    # master are known locally — main must still win.
    head_sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "update-ref", "refs/remotes/origin/master", head_sha)

    _break_symref(repo)
    _make_unreachable(repo, tmp_path)

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)

    assert _symref_target(repo) == "refs/remotes/origin/main"
    assert any("offline fallback" in line for line in report)


def test_offline_fallback_uses_master_when_main_absent(tmp_path):
    origin = _make_bare_origin(tmp_path, "origin", "master")
    repo = _clone(tmp_path, origin, "repo")
    assert _symref_target(repo) == "refs/remotes/origin/master"

    _break_symref(repo)
    _make_unreachable(repo, tmp_path)

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)

    assert _symref_target(repo) == "refs/remotes/origin/master"
    assert any("offline fallback" in line for line in report)


def test_no_origin_remote_does_not_raise(tmp_path):
    repo = tmp_path / "solo"
    repo.mkdir()
    _git(repo, "init", "-q")

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)  # must not raise

    assert any("repair skipped" in line for line in report)


def test_no_local_fallback_candidate_does_not_raise(tmp_path):
    origin = _make_bare_origin(tmp_path, "origin", "main")
    repo = _clone(tmp_path, origin, "repo")

    # Drop the only local tracking ref, so the offline fallback has nothing
    # to work with once the network path also fails.
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    _break_symref(repo)
    _make_unreachable(repo, tmp_path)

    report: list[str] = []
    init_factory.fix_origin_head(repo, report)  # must not raise

    assert any("no local origin/main or origin/master" in line for line in report)
