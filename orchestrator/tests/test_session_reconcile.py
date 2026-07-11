"""Tests for session-reconcile — the session-log vs. git-state gate.

session-reconcile is a script without a .py extension; it is loaded via
SourceFileLoader, matching the test_matrix_lint / test_backlog_lint precedent.
Each test builds a temp git repo, chdir's into it (git commands run in cwd),
writes a session log, and runs check_session() directly.

Proves acceptance test 2 of the proposal (§5): a file changed on disk that no
logged run's files_changed accounts for and that isn't staged or committed is
flagged as an unexplained change.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[2] / "factory" / "scripts" / "session-reconcile"
)
_loader = SourceFileLoader("session_reconcile", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("session_reconcile", _loader)
session_reconcile = importlib.util.module_from_spec(_spec)
sys.modules["session_reconcile"] = session_reconcile
_loader.exec_module(session_reconcile)

check_session = session_reconcile.check_session
Finding = session_reconcile.Finding


# --- Helpers ------------------------------------------------------------------


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    # The session log lives gitignored under .agent-factory/, as in a real repo,
    # so it never appears as an unexplained change in git status.
    (root / ".gitignore").write_text(".agent-factory/\n", encoding="utf-8")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)


def _write_log(path: Path, runs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in runs), encoding="utf-8")


def _edit_tracked_spec(root: Path) -> None:
    """Commit a docs/spec/ file, then modify it, so git reports the individual
    path (a wholly-untracked docs/ collapses to one porcelain entry)."""
    spec = root / "docs" / "spec"
    spec.mkdir(parents=True)
    (spec / "prd.md").write_text("# PRD\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "spec"], cwd=root, check=True)
    (spec / "prd.md").write_text("# PRD edited\n", encoding="utf-8")


def _run(script: str, files_changed: list[dict], **extra) -> dict:
    return {
        "ts": "2026-07-11T14:32:07Z",
        "script": script,
        "argv": [],
        "exit_code": 0,
        "files_changed": files_changed,
        **extra,
    }


# --- Unexplained change (acceptance test 2) -----------------------------------


class TestUnexplained:
    def test_worktree_change_no_logged_run_is_flagged(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        # A file changed on disk that no logged run accounts for.
        (tmp_path / "rogue.txt").write_text("hand-edited\n", encoding="utf-8")
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(
            log, [_run("spec-lint", [{"path": "docs/spec/x.md", "status": "M"}])]
        )

        findings = check_session(log, base=None, head="HEAD")
        unexplained = [f for f in findings if f.code == "RECON-UNEXPLAINED"]
        assert len(unexplained) == 1
        assert unexplained[0].artifact == "rogue.txt"
        assert unexplained[0].severity == "error"

    def test_logged_worktree_change_is_explained(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        (tmp_path / "tracked.txt").write_text("logged edit\n", encoding="utf-8")
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [_run("spec-lint", [{"path": "tracked.txt", "status": "??"}])])

        findings = check_session(log, base=None, head="HEAD")
        assert not any(f.code == "RECON-UNEXPLAINED" for f in findings)

    def test_committed_change_is_explained(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        subprocess.run(["git", "checkout", "-qb", "feature"], cwd=tmp_path, check=True)
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True
        ).stdout.strip()
        (tmp_path / "committed.txt").write_text("c\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "add committed"], cwd=tmp_path, check=True
        )
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [])

        findings = check_session(log, base=base, head="HEAD")
        assert not any(f.code == "RECON-UNEXPLAINED" for f in findings)


# --- Silent drift -------------------------------------------------------------


class TestDrift:
    def test_logged_change_that_vanished_is_flagged(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        # Log claims a change, but nothing on disk or committed reflects it.
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [_run("spec-lint", [{"path": "ghost.md", "status": "M"}])])

        findings = check_session(log, base=None, head="HEAD")
        drift = [f for f in findings if f.code == "RECON-DRIFT"]
        assert len(drift) == 1
        assert drift[0].artifact == "ghost.md"


# --- Stale gate ---------------------------------------------------------------


class TestStaleGate:
    def test_spec_change_without_spec_lint_run(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _edit_tracked_spec(tmp_path)
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [_run("backlog-lint", [])])

        findings = check_session(log, base=None, head="HEAD")
        assert any(f.code == "RECON-STALE" for f in findings)

    def test_spec_change_with_spec_lint_run_is_quiet(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _edit_tracked_spec(tmp_path)
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(
            log,
            [_run("spec-lint", [{"path": "docs/spec/prd.md", "status": "??"}])],
        )

        findings = check_session(log, base=None, head="HEAD")
        assert not any(f.code == "RECON-STALE" for f in findings)


# --- Log handling & driver ----------------------------------------------------


class TestLogHandling:
    def test_missing_log_is_info(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        findings = check_session(tmp_path / "nope.jsonl", base=None, head="HEAD")
        assert any(f.code == "RECON-NOLOG" for f in findings)

    def test_malformed_line_warns(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        log = tmp_path / ".agent-factory" / "log.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("{not json}\n", encoding="utf-8")
        findings = check_session(log, base=None, head="HEAD")
        assert any(f.code == "RECON-LOG" for f in findings)

    def test_clean_session_exits_zero(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [])
        rc = session_reconcile.main(["--log", str(log)])
        assert rc == 0

    def test_unexplained_gates_nonzero(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        (tmp_path / "rogue.txt").write_text("x\n", encoding="utf-8")
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [])
        rc = session_reconcile.main(["--log", str(log)])
        assert rc == 1

    def test_report_only_exits_zero(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        (tmp_path / "rogue.txt").write_text("x\n", encoding="utf-8")
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [])
        rc = session_reconcile.main(["--log", str(log), "--report-only"])
        assert rc == 0

    def test_json_format(self, tmp_path, monkeypatch, capsys):
        _init_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        (tmp_path / "rogue.txt").write_text("x\n", encoding="utf-8")
        log = tmp_path / ".agent-factory" / "log.jsonl"
        _write_log(log, [])
        session_reconcile.main(["--log", str(log), "--format", "json"])
        out = json.loads(capsys.readouterr().out)
        assert out["summary"]["error"] == 1
