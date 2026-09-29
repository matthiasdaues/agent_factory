"""Integration tests for ST-0250 — capture works without the analysis component."""

from __future__ import annotations

import json
import subprocess
import uuid
from pathlib import Path

import pytest

CAPTURE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "factory"
    / "scripts"
    / "usage-capture"
)


@pytest.fixture()
def capture_project(tmp_path: Path) -> Path:
    """Project directory with capture prerequisites but no analysis component."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "project.json").write_text(
        json.dumps(
            {
                "project_id": str(uuid.uuid4()),
                "project_name": "capture-independence-test",
            }
        )
    )

    usage_dir = tmp_path / ".agent-factory" / "usage"
    usage_dir.mkdir(parents=True)

    assert not (tmp_path / ".agent-factory" / "usage" / "analysis").exists()
    return tmp_path


@pytest.fixture()
def transcript(tmp_path: Path) -> Path:
    """Minimal Claude Code transcript JSONL."""
    path = tmp_path / "transcript.jsonl"
    path.write_text(
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Test response."}],
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                },
            }
        )
        + "\n"
    )
    return path


class TestCaptureIndependence:
    def test_capture_without_analysis_component(
        self, capture_project: Path, transcript: Path
    ) -> None:
        """Capture appends a JSONL record when usage-analysis is absent (LU-09)."""
        assert not (capture_project / ".agent-factory" / "usage" / "analysis").exists()

        result = subprocess.run(
            [
                "uv",
                "run",
                "--script",
                str(CAPTURE_SCRIPT),
                "--cli",
                "claude-code",
                "--transcript",
                str(transcript),
                "--session",
                "test-session-001",
                "--transcript-retention",
                "omit",
            ],
            capture_output=True,
            text=True,
            cwd=str(capture_project),
            timeout=120,
        )
        assert result.returncode == 0, f"capture failed: {result.stderr}"

        usage_dir = capture_project / ".agent-factory" / "usage"
        jsonl_files = list(usage_dir.glob("*.jsonl"))
        assert jsonl_files, "no JSONL files found in usage spool"

        records = []
        for f in jsonl_files:
            for line in f.read_text().splitlines():
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) >= 1, "no records found in JSONL files"
        record = records[0]
        assert record["cli"] == "claude-code"
        assert record["session_id"] == "test-session-001"
        assert isinstance(record["normalized_input"], int)
        assert isinstance(record["normalized_output"], int)


class TestDependencyBoundary:
    def test_dependency_check_passes(self) -> None:
        """dependency-check exits zero with factory/usage boundary rules (LU-11)."""
        script = (
            Path(__file__).resolve().parents[2]
            / "packages"
            / "factory"
            / "scripts"
            / "dependency-check"
        )
        result = subprocess.run(
            [
                "python3",
                str(script),
                "--source-root",
                "packages/",
                "--story-id",
                "ST-0250-test",
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            timeout=30,
        )
        assert result.returncode == 0, f"dependency-check failed: {result.stdout}"
        report = json.loads(result.stdout)
        rule_names = {r["rule_name"] for r in report}
        assert "factory must_not_depend_on usage" in rule_names
        assert "usage must_not_depend_on factory" in rule_names
        assert all(r["pass_fail"] == "pass" for r in report)

    def test_dependency_check_detects_violation(self, tmp_path: Path) -> None:
        """dependency-check exits non-zero when a boundary is violated (LU-11)."""
        script = (
            Path(__file__).resolve().parents[2]
            / "packages"
            / "factory"
            / "scripts"
            / "dependency-check"
        )
        source = tmp_path / "source"
        pkg_a = source / "alpha"
        pkg_a.mkdir(parents=True)
        (pkg_a / "__init__.py").write_text("")
        (pkg_a / "leaky.py").write_text("import beta\n")
        pkg_b = source / "beta"
        pkg_b.mkdir(parents=True)
        (pkg_b / "__init__.py").write_text("")

        dsl = tmp_path / "test.dsl"
        dsl.write_text(
            'workspace "test" {\n  model {\n    alpha must_not_depend_on beta\n  }\n}\n'
        )

        result = subprocess.run(
            [
                "python3",
                str(script),
                "--dsl-path",
                str(dsl),
                "--source-root",
                str(source),
                "--story-id",
                "violation-test",
                "--report-dir",
                str(tmp_path / "reports"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        report = json.loads(result.stdout)
        violations = [r for r in report if r["pass_fail"] == "fail"]
        assert violations
        assert violations[0]["rule_name"] == "alpha must_not_depend_on beta"
