"""Tests for _session_log.py and the spec-lint wrap.

_session_log.py is a real importable module (leading underscore, .py extension),
so it is imported directly after putting factory/scripts/ on sys.path. The
spec-lint wrap is exercised end-to-end as a subprocess inside a temp git repo —
the faithful path, including the script-dir-on-sys.path import.

Proves acceptance test 1 of the proposal (§5): with AF_SESSION_LOG set, one
well-formed JSONL line lands with the correct script, argv, exit_code, and a
real recent UTC ts.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "factory" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import _session_log  # noqa: E402

SPEC_LINT = _SCRIPTS / "spec-lint"


# --- Helpers ------------------------------------------------------------------


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    # The session log lives gitignored under .agent-factory/, as in a real repo.
    (root / ".gitignore").write_text(".agent-factory/\n", encoding="utf-8")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)


def _assert_recent_utc(ts: str) -> None:
    parsed = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    assert now - timedelta(minutes=5) <= parsed <= now + timedelta(seconds=5), ts


# --- record() transparency ----------------------------------------------------


class TestTransparency:
    def test_noop_when_env_unset(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv("AF_SESSION_LOG", raising=False)
        log = tmp_path / "log.jsonl"
        with _session_log.record("spec-lint", ["--graph"]) as rec:
            rec.exit_code = 0
        assert not log.exists()

    def test_yields_recorder_either_way(self, monkeypatch):
        monkeypatch.delenv("AF_SESSION_LOG", raising=False)
        with _session_log.record("x", []) as rec:
            assert isinstance(rec, _session_log.Recorder)


# --- record() writes a well-formed line ---------------------------------------


class TestRecordWrites:
    def test_one_line_with_files_changed_and_exit_code(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        log = tmp_path / "log.jsonl"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("AF_SESSION_LOG", str(log))

        with _session_log.record("spec-lint", ["docs/spec", "--graph"]) as rec:
            (tmp_path / "new.txt").write_text("hi\n", encoding="utf-8")
            rec.exit_code = 0

        lines = log.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["script"] == "spec-lint"
        assert entry["argv"] == ["docs/spec", "--graph"]
        assert entry["exit_code"] == 0
        _assert_recent_utc(entry["ts"])
        paths = {fc["path"] for fc in entry["files_changed"]}
        assert "new.txt" in paths
        assert "summary" not in entry  # no set_summary call

    def test_set_summary_folded_in(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        log = tmp_path / "log.jsonl"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("AF_SESSION_LOG", str(log))

        with _session_log.record("spec-lint", []) as rec:
            _session_log.set_summary({"error": 0, "warning": 2, "info": 1})
            rec.exit_code = 0

        entry = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
        assert entry["summary"] == {"error": 0, "warning": 2, "info": 1}

    def test_set_summary_noop_when_inactive(self, monkeypatch):
        monkeypatch.delenv("AF_SESSION_LOG", raising=False)
        # No active record: must not raise.
        _session_log.set_summary({"error": 1})

    def test_exception_still_records(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        log = tmp_path / "log.jsonl"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("AF_SESSION_LOG", str(log))

        try:
            with _session_log.record("spec-lint", []):
                raise RuntimeError("boom")
        except RuntimeError:
            pass

        entry = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
        assert entry["exit_code"] is None

    def test_appends_not_overwrites(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        log = tmp_path / "log.jsonl"
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("AF_SESSION_LOG", str(log))
        for i in range(3):
            with _session_log.record("spec-lint", [str(i)]) as rec:
                rec.exit_code = i
        lines = log.read_text(encoding="utf-8").splitlines()
        assert [json.loads(ln)["exit_code"] for ln in lines] == [0, 1, 2]


# --- spec-lint end-to-end (acceptance test 1) ---------------------------------


class TestSpecLintWrap:
    def _minimal_spec(self, root: Path) -> Path:
        spec = root / "docs" / "spec"
        (spec / "use_cases").mkdir(parents=True)
        (spec / "supplementary_specs").mkdir(parents=True)
        (spec / "prd.md").write_text("# PRD\n", encoding="utf-8")
        (spec / "actor-goal-list.md").write_text("# Goals\n", encoding="utf-8")
        (spec / "supplementary_specs" / "entity-model.md").write_text(
            "# Entities\n", encoding="utf-8"
        )
        (spec / "supplementary_specs" / "validation-rules.md").write_text(
            "# Rules\n", encoding="utf-8"
        )
        # Commit the scaffolding so a git-tracked dir exists: git collapses a
        # wholly-untracked docs/ into one porcelain entry, which would hide the
        # new traceability.json inside it.
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "spec"], cwd=root, check=True)
        return spec

    def test_spec_lint_graph_logs_one_line(self, tmp_path, monkeypatch):
        _init_repo(tmp_path)
        spec = self._minimal_spec(tmp_path)
        log = tmp_path / ".agent-factory" / "session-log.jsonl"

        env = {**os.environ, "AF_SESSION_LOG": str(log)}
        result = subprocess.run(
            [
                sys.executable,
                str(SPEC_LINT),
                "--spec-dir",
                str(spec),
                "--graph",
                str(spec / "traceability.json"),
                "--report-only",
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

        lines = log.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["script"] == "spec-lint"
        assert "--graph" in entry["argv"]
        assert isinstance(entry["exit_code"], int)
        _assert_recent_utc(entry["ts"])
        # --graph wrote traceability.json -> the git-diff path captured it.
        paths = {fc["path"] for fc in entry["files_changed"]}
        assert any("traceability.json" in p for p in paths)
        # spec-lint has --format json, so its summary counts are folded in.
        assert set(entry["summary"]) == {"error", "warning", "info"}
