"""Integration tests for dispatch status subcommand.

QA strategy Layer 3 — subprocess boundary, no internal imports.
Owner of: dispatch status acceptance criteria 11-12.
"""

import subprocess
import textwrap
from pathlib import Path

DISPATCH = (
    Path(__file__).resolve().parent.parent.parent / "factory" / "scripts" / "dispatch"
)


def run_dispatch(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Invoke the dispatch script as a subprocess."""
    return subprocess.run(
        [str(DISPATCH), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        check=False,
    )


def test_status_valid_ledger(tmp_path):
    ledger = tmp_path / ".current-work" / "dispatch-ledger.yaml"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        textwrap.dedent(
            """\
        stories:
          ST-001:
            id: ST-001
            wave: 1
            status: prepared
            branch: feat/ST-001
            worktree: null
            base_sha: """
            + "a" * 40
            + """
            gate_results: {}
    """
        )
    )
    result = run_dispatch("--ledger", str(ledger), "status", cwd=tmp_path)
    assert result.returncode == 0
    assert "ST-001" in result.stdout
    assert "prepared" in result.stdout


def test_status_missing_ledger(tmp_path):
    result = run_dispatch(
        "--ledger",
        str(tmp_path / "nope.yaml"),
        "status",
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_status_syntactically_malformed(tmp_path):
    ledger = tmp_path / "bad.yaml"
    ledger.write_text("this is not yaml\n")
    result = run_dispatch("--ledger", str(ledger), "status", cwd=tmp_path)
    assert result.returncode == 1
    assert "malformed" in result.stderr.lower()


def test_status_structurally_invalid(tmp_path):
    ledger = tmp_path / "bad.yaml"
    ledger.write_text("stories: not_a_mapping\n")
    result = run_dispatch("--ledger", str(ledger), "status", cwd=tmp_path)
    assert result.returncode == 1
