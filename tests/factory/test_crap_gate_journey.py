"""The journey of a story blocked by a CRAP gate that cannot measure (QS-31, DEC-45).

One run by hand on a temporary repository: the gate fails a changed function,
the developer commit fixes it, a stopped stack makes the gate exit 2 and the
story blocked, resume-gates returns it with its attempts, and merge-story
merges it with the real premerge-check and the real crap-score.
"""

from __future__ import annotations

import stat
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SOURCE_SCRIPTS_DIR
from test_run_lifecycle_dispatch import (
    AU,
    _dispatch,
    _dispatched_by_hand,
    _entry,
    _env,
    _git,
)

GATE_REASON = "gate cannot measure: crap-score"
STORY_CODE = "def tree_severity(x):\n    return x\n\n"

# The measuring command fails while the stack is stopped, and plants one row
# of tree_severity: 0 % coverage until the developer commit marks it covered.
MEASURE_STUB = """#!/bin/sh
if [ -e "{stopped}" ]; then echo "the Compose stack is stopped" >&2; exit 1; fi
if grep -q covered src/ST-0350.py; then cov=100; else cov=0; fi
printf '[{{"file": "src/ST-0350.py", "function": "tree_severity", "start_line": 1, \
"end_line": 3, "complexity": 5, "coverage_pct": %s}}]' "$cov" > "$GATE_OUTPUT"
"""
GATED = """\
test_command: "true"
gates:
  crap-score:
    enabled: true
    threshold: 8
    timeout_minutes: 10
    measures:
      - name: python
        files: "src/*"
        command: "{stub}"
"""
REAL_CRAP_SCORE = '#!/bin/sh\nexec "{python}" "{script}" "$@"\n'


def _executable(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def _gate_check(run: dict[str, Path]) -> subprocess.CompletedProcess:
    """The gate-check step: crap-score against the feature branch in the primary checkout."""
    repo = run["repo"]
    return subprocess.run(
        [
            str(repo / ".agent-factory" / "factory" / "scripts" / "crap-score"),
            "--base", "feature/login",
            "--story-id", "ST-0350",
            "--report-dir", str(repo / ".current-work" / "crap-score"),
        ],
        cwd=repo, env=_env(), capture_output=True, text=True, check=False,
    )


def _step(run: dict[str, Path], *args: str) -> subprocess.CompletedProcess:
    result = _dispatch(run["repo"], run["ledger"], *args)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result


@pytest.mark.spec("CG-08-E2-01")
def test_cg_08_a_blocked_story_resumes_and_merges_with_its_attempts(tmp_path):
    """Scenario Outline: Exit 2 in the gate-check step blocks the story,
    Scenario: resume-gates returns the story to the gate-check step, and
    Scenario Outline: A gate that cannot measure at the merge blocks the story on both ways."""
    stopped = tmp_path / "stack-stopped"
    stub = _executable(tmp_path / "crap-measure-stub", MEASURE_STUB.format(stopped=stopped))
    run = _dispatched_by_hand(
        tmp_path, code=STORY_CODE, rules=False, testing=GATED.format(stub=stub)
    )
    repo = run["repo"]
    _executable(
        repo / ".agent-factory" / "factory" / "scripts" / "crap-score",
        REAL_CRAP_SCORE.format(python=sys.executable, script=SOURCE_SCRIPTS_DIR / "crap-score"),
    )

    # The gate fails the changed function, and the attempt fails.
    failing = _gate_check(run)
    assert failing.returncode == 1, failing.stdout + failing.stderr
    assert "tree_severity" in failing.stdout
    _step(run, "mark-failed", "ST-0350", "--class", AU)
    for step in ("re-dispatch", "mark-dispatching"):
        _step(run, step, "ST-0350")

    # The developer commit fixes the function.
    (repo / "src" / "ST-0350.py").write_text(STORY_CODE + "# covered\n")
    _git(repo, "add", "src")
    _git(repo, "commit", "-qm", "fix: cover tree_severity (ST-0350)")
    sha = _git(repo, "rev-parse", "HEAD")
    _step(run, "mark-dispatched", "ST-0350")
    _step(run, "verify-story", "ST-0350", "--sha", sha)
    attempts = _entry(run).attempts
    assert len(attempts) == 1

    # The stack stops, the gate cannot measure, and the story is blocked.
    stopped.write_text("")
    cannot = _gate_check(run)
    assert cannot.returncode == 2, cannot.stdout + cannot.stderr
    _step(run, "mark-blocked", "ST-0350", "--reason", GATE_REASON)
    assert _entry(run).status.value == "blocked"

    # The User starts the stack, and resume-gates returns the story.
    stopped.unlink()
    _step(run, "resume-gates", "ST-0350")
    entry = _entry(run)
    assert entry.status.value == "dispatched"
    assert entry.attempts == attempts
    assert _git(repo, "rev-parse", "story/ST-0350") == sha

    passing = _gate_check(run)
    assert passing.returncode == 0, passing.stdout + passing.stderr
    merged = _step(run, "merge-story", "ST-0350")

    entry = _entry(run)
    assert entry.status.value == "done", merged.stdout + merged.stderr
    assert entry.attempts == attempts
    assert _git(repo, "merge-base", "--is-ancestor", sha, "feature/login") == ""
