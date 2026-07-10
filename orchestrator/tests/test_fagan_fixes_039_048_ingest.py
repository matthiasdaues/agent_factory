from __future__ import annotations

import json

from pathlib import Path

from orchestrator.adapters.finding_ingest import DefaultFindingIngestor
from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.entities import FindingSource, FindingStatus, Severity


# FAGAN-0045: DefaultFindingIngestor.ingest_gate_output() must tolerate mixed
# pre-commit stdout (banner text plus an embedded JSON findings block), not
# just a pure JSON document, while still tagging findings as gate findings
# (source=SPEC_LINT, created_by="spec-lint").


def test_ingest_gate_output_pure_json_still_ingests(tmp_path: Path):
    """No regression: a pure JSON gate payload keeps working."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    payload = {
        "findings": [
            {
                "code": "STRUCT001",
                "severity": "error",
                "artifact": "docs/spec/use_cases/UC-01.md",
                "message": "missing required section",
            }
        ],
        "summary": {"error": 1, "warning": 0, "info": 0},
    }

    count = ingestor.ingest_gate_output(json.dumps(payload), "reviewing", 1)

    assert count == 1
    open_findings = store.list_open("reviewing", 1)
    assert len(open_findings) == 1
    finding = open_findings[0]
    assert finding.code == "STRUCT001"
    assert finding.severity == Severity.ERROR
    assert finding.status == FindingStatus.OPEN
    assert finding.source == FindingSource.SPEC_LINT
    assert finding.created_by == "spec-lint"


def test_ingest_gate_output_mixed_text_with_banner_lines_ingests_findings(
    tmp_path: Path,
):
    """The bug: real pre-commit stdout wraps the JSON block in hook banner text.
    Deterministic findings must still be ingested — not silently dropped."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    gate_output = (
        """spec-lint..............................................................Failed
- hook id: spec-lint
- exit code: 1

Running spec-lint over docs/spec/**/*.md
"""
        + json.dumps(
            {
                "findings": [
                    {
                        "code": "STRUCT001",
                        "severity": "error",
                        "artifact": "docs/spec/use_cases/UC-01.md",
                        "message": "missing required section",
                    },
                    {
                        "code": "TRACE002",
                        "severity": "warning",
                        "artifact": "docs/spec/use_cases/UC-02.md",
                        "message": "traceability link missing",
                    },
                ]
            }
        )
        + "\n\nspec-lint hook failed, see findings above.\n"
    )

    count = ingestor.ingest_gate_output(gate_output, "reviewing", 2)

    assert count == 2
    open_findings = sorted(store.list_open("reviewing", 2), key=lambda f: f.code)
    assert [f.code for f in open_findings] == ["STRUCT001", "TRACE002"]
    assert [f.severity for f in open_findings] == [Severity.ERROR, Severity.WARNING]
    assert all(f.source == FindingSource.SPEC_LINT for f in open_findings)
    assert all(f.created_by == "spec-lint" for f in open_findings)
    assert all(f.status == FindingStatus.OPEN for f in open_findings)


# FAGAN-0045 regression: the tolerant scanner used by map_spec_lint can visit
# the same logical finding twice — once because a dict is both finding-shaped
# and nests a findings/finding key, and again because two separate top-level
# JSON blocks in the same stdout repeat it. map_spec_lint must de-dupe by
# content (code, severity, artifact, message).


def test_ingest_gate_output_dict_both_bare_and_nested_counts_once(tmp_path: Path):
    """A single dict that is itself finding-shaped AND carries a nested
    findings list containing the same finding must be counted once, not
    twice."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    payload = {
        "code": "STRUCT001",
        "severity": "error",
        "artifact": "docs/spec/use_cases/UC-01.md",
        "message": "missing required section",
        "findings": [
            {
                "code": "STRUCT001",
                "severity": "error",
                "artifact": "docs/spec/use_cases/UC-01.md",
                "message": "missing required section",
            }
        ],
    }

    count = ingestor.ingest_gate_output(json.dumps(payload), "reviewing", 1)

    assert count == 1
    open_findings = store.list_open("reviewing", 1)
    assert len(open_findings) == 1
    assert open_findings[0].code == "STRUCT001"
    assert open_findings[0].source == FindingSource.SPEC_LINT
    assert open_findings[0].created_by == "spec-lint"


def test_ingest_gate_output_repeated_top_level_json_blocks_count_once(tmp_path: Path):
    """A tool that echoes a finding as inline text-JSON and again in a final
    summary block must not double-count it."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    one_finding = {
        "code": "TRACE002",
        "severity": "warning",
        "artifact": "docs/spec/use_cases/UC-02.md",
        "message": "traceability link missing",
    }
    gate_output = (
        "echoing finding: " + json.dumps(one_finding) + "\n"
        "final summary:\n" + json.dumps({"findings": [one_finding]}) + "\n"
    )

    count = ingestor.ingest_gate_output(gate_output, "reviewing", 1)

    assert count == 1
    open_findings = store.list_open("reviewing", 1)
    assert len(open_findings) == 1
    assert open_findings[0].code == "TRACE002"
    assert open_findings[0].source == FindingSource.SPEC_LINT
    assert open_findings[0].created_by == "spec-lint"


def test_ingest_gate_output_distinct_findings_are_not_over_collapsed(tmp_path: Path):
    """Dedup must key on full content, not just presence — two genuinely
    different findings (differing code/artifact/message) must both survive,
    even when nested and bare representations of each are both present."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    payload = {
        "code": "STRUCT001",
        "severity": "error",
        "artifact": "docs/spec/use_cases/UC-01.md",
        "message": "missing required section",
        "findings": [
            {
                "code": "TRACE002",
                "severity": "warning",
                "artifact": "docs/spec/use_cases/UC-02.md",
                "message": "traceability link missing",
            }
        ],
    }

    count = ingestor.ingest_gate_output(json.dumps(payload), "reviewing", 1)

    assert count == 2
    open_findings = sorted(store.list_open("reviewing", 1), key=lambda f: f.code)
    assert [f.code for f in open_findings] == ["STRUCT001", "TRACE002"]
    assert all(f.source == FindingSource.SPEC_LINT for f in open_findings)
    assert all(f.created_by == "spec-lint" for f in open_findings)


def test_ingest_gate_output_no_findings_ingests_nothing(tmp_path: Path):
    """A clean gate run (or output with no embedded JSON at all) must not
    fabricate findings."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")

    # Genuinely empty stdout.
    assert ingestor.ingest_gate_output("", "reviewing", 1) == 0

    # Banner text only, no embedded JSON.
    assert (
        ingestor.ingest_gate_output(
            "spec-lint...........................................................Passed\n",
            "reviewing",
            1,
        )
        == 0
    )

    # Embedded JSON with an explicitly empty findings list.
    clean_payload = json.dumps(
        {"findings": [], "summary": {"error": 0, "warning": 0, "info": 0}}
    )
    assert (
        ingestor.ingest_gate_output(
            f"spec-lint passed.\n{clean_payload}\n", "reviewing", 1
        )
        == 0
    )

    assert store.list_open("reviewing", 1) == []
