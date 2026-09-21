"""Unit tests for usage.views.capture_health view function."""

from __future__ import annotations

from pathlib import Path

from usage.preflight import run_preflight
from usage.views.capture_health import capture_health


class TestCaptureHealthNone:
    """capture_health with no preflight result (empty dir)."""

    def test_returns_view_name(self) -> None:
        result = capture_health(None)
        assert result["view"] == "capture_health"

    def test_all_counts_zero(self) -> None:
        result = capture_health(None)
        assert result["total_lines"] == 0
        assert result["valid_count"] == 0
        assert result["failure_count"] == 0

    def test_no_failures(self) -> None:
        result = capture_health(None)
        assert result["has_failures"] is False

    def test_empty_failure_lists(self) -> None:
        result = capture_health(None)
        assert result["failures_by_code"] == []
        assert result["failures_by_file"] == []

    def test_diagnostic_false_by_default(self) -> None:
        result = capture_health(None)
        assert result["diagnostic"] is False

    def test_diagnostic_true_when_set(self) -> None:
        result = capture_health(None, diagnostic=True)
        assert result["diagnostic"] is True

    def test_diagnostic_label_present_when_diagnostic(self) -> None:
        result = capture_health(None, diagnostic=True)
        assert result["diagnostic_label"] == "incomplete"

    def test_diagnostic_label_absent_when_not_diagnostic(self) -> None:
        result = capture_health(None)
        assert "diagnostic_label" not in result


class TestCaptureHealthValidOnly:
    """capture_health with valid-only input (no failures)."""

    def test_counts_match_valid_records(self, ancestry_dir: Path) -> None:
        # valid_tree.jsonl is a self-contained tree with no failures.
        paths = [ancestry_dir / "valid_tree.jsonl"]
        pr = run_preflight(paths)
        result = capture_health(pr)
        assert result["valid_count"] == pr.valid_count
        assert result["failure_count"] == 0
        assert result["total_lines"] == pr.valid_count
        assert result["has_failures"] is False

    def test_empty_failure_lists(self, ancestry_dir: Path) -> None:
        paths = [ancestry_dir / "valid_tree.jsonl"]
        pr = run_preflight(paths)
        result = capture_health(pr)
        assert result["failures_by_code"] == []
        assert result["failures_by_file"] == []


class TestCaptureHealthWithFailures:
    """capture_health with ancestry failures present."""

    def test_has_failures_true(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        assert result["has_failures"] is True

    def test_failure_count_matches(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        assert result["failure_count"] == pr.failure_count
        assert result["valid_count"] == pr.valid_count
        assert result["total_lines"] == pr.valid_count + pr.failure_count

    def test_failures_by_code_populated(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        codes = result["failures_by_code"]
        assert len(codes) > 0
        # Each entry has code and count
        for entry in codes:
            assert "code" in entry
            assert "count" in entry
            assert isinstance(entry["count"], int)
            assert entry["count"] > 0

    def test_failures_by_code_sum_matches_total(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        code_sum = sum(e["count"] for e in result["failures_by_code"])
        assert code_sum == result["failure_count"]

    def test_failures_by_file_populated(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        files = result["failures_by_file"]
        assert len(files) > 0
        for entry in files:
            assert "file" in entry
            assert "count" in entry
            assert isinstance(entry["count"], int)
            assert entry["count"] > 0

    def test_failures_by_file_sum_matches_total(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        file_sum = sum(e["count"] for e in result["failures_by_file"])
        assert file_sum == result["failure_count"]

    def test_failures_by_code_ordered_desc(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        counts = [e["count"] for e in result["failures_by_code"]]
        assert counts == sorted(counts, reverse=True)

    def test_failures_by_file_ordered_by_name(self, ancestry_dir: Path) -> None:
        paths = sorted(ancestry_dir.glob("*.jsonl"))
        pr = run_preflight(paths)
        result = capture_health(pr)
        names = [e["file"] for e in result["failures_by_file"]]
        assert names == sorted(names)
