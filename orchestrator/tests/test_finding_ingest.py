from __future__ import annotations

import json

import pytest
from pathlib import Path

from orchestrator.adapters.finding_ingest import (
    DefaultFindingIngestor,
    map_spec_lint,
)
from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.entities import Finding, FindingSource, FindingStatus, Severity


def _finding(finding_id: str) -> Finding:
    return Finding(
        id=finding_id,
        phase="reviewing",
        iteration=1,
        source=FindingSource.SPEC_LINT,
        code="SPEC-001",
        severity=Severity.ERROR,
        artifact="docs/spec.md",
        message="Existing finding",
        status=FindingStatus.OPEN,
        created_by="spec-lint",
    )


def test_map_spec_lint_with_valid_json_returns_correct_findings(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    payload = {
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
        ],
        "summary": {"error": 1, "warning": 1, "info": 0},
    }

    findings = map_spec_lint(json.dumps(payload), "reviewing", 2, store)

    assert findings == [
        Finding(
            id="FND-0001",
            phase="reviewing",
            iteration=2,
            source=FindingSource.SPEC_LINT,
            code="STRUCT001",
            severity=Severity.ERROR,
            artifact="docs/spec/use_cases/UC-01.md",
            message="missing required section",
            status=FindingStatus.OPEN,
            created_by="spec-lint",
        ),
        Finding(
            id="FND-0002",
            phase="reviewing",
            iteration=2,
            source=FindingSource.SPEC_LINT,
            code="TRACE002",
            severity=Severity.WARNING,
            artifact="docs/spec/use_cases/UC-02.md",
            message="traceability link missing",
            status=FindingStatus.OPEN,
            created_by="spec-lint",
        ),
    ]


def test_map_spec_lint_with_empty_findings_list_returns_empty(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")

    findings = map_spec_lint(
        json.dumps({"findings": [], "summary": {"error": 0, "warning": 0, "info": 0}}),
        "reviewing",
        1,
        store,
    )

    assert findings == []


def test_map_spec_lint_with_malformed_json_returns_empty(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")

    assert map_spec_lint("{not json", "reviewing", 1, store) == []


def test_map_spec_lint_assigns_monotonic_ids_via_store(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    store.ingest([_finding("FND-0007")])
    payload = {
        "findings": [
            {
                "code": "STRUCT001",
                "severity": "error",
                "artifact": "docs/spec/use_cases/UC-01.md",
                "message": "missing required section",
            },
            {
                "code": "STRUCT002",
                "severity": "info",
                "artifact": "docs/spec/use_cases/UC-02.md",
                "message": "consider adding rationale",
            },
        ],
        "summary": {"error": 1, "warning": 0, "info": 1},
    }

    findings = map_spec_lint(json.dumps(payload), "reviewing", 3, store)

    assert [finding.id for finding in findings] == ["FND-0008", "FND-0009"]


def test_all_returned_findings_have_status_open(tmp_path: Path):
    """Both ingestion paths — the deterministic gate scanner and the markdown
    reader — must only ever produce ``open`` findings (ADR-0012, ADR-0019)."""
    store = FilesystemFindingsStore(tmp_path / "findings")
    spec_findings = map_spec_lint(
        json.dumps(
            {
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
        ),
        "reviewing",
        1,
        store,
    )
    docs = tmp_path / "docs" / "findings"
    _write_finding(
        docs,
        "SEM-0201.md",
        id_="SEM-0201",
        severity="error",
        status="open",
        artifact="src/orchestrator/loop.py",
        title="guard missing on empty queue",
    )
    ingestor = DefaultFindingIngestor(store, docs)
    ingestor.ingest_open_findings("reviewing", 1)
    semantic_findings = store.list_open("reviewing", 1)

    assert all(
        finding.status == FindingStatus.OPEN
        for finding in spec_findings + semantic_findings
    )


# --- DefaultFindingIngestor: read open findings from docs/findings/*.md
# (ADR-0012 ingestion source; ADR-0019 confirms the store it writes to is the
# loop's sole source of truth) ---


def _write_finding(
    dir_: Path,
    name: str,
    *,
    id_: str,
    severity: str,
    status: str,
    artifact: str,
    title: str,
) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / name).write_text(
        f"---\nid: {id_}\nsource: spec-review\nseverity: {severity}\n"
        f"category: defect\nartifact: {artifact}\nstatus: {status}\n"
        f"traces: [NFR-01]\n---\n\n# {title}\n\n**What is wrong:** ...\n",
        encoding="utf-8",
    )


def test_ingest_open_findings_raises_for_malformed_open_finding(tmp_path: Path):
    docs = tmp_path / "docs" / "findings"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "SPEC-0001.md").write_text(
        """---
id: SPEC-0001
source: spec-review
severity: sev1
category: defect
status: open
traces: [NFR-01]
---

# NFR-01 not verifiable
""",
        encoding="utf-8",
    )
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, docs)

    with pytest.raises(ValueError, match=r"SPEC-0001\.md.*severity='sev1'.*artifact"):
        ingestor.ingest_open_findings("requirements", 1)


def test_ingest_open_findings_reads_open_files_and_maps_severity(tmp_path: Path):
    docs = tmp_path / "docs" / "findings"
    _write_finding(
        docs,
        "SPEC-0001.md",
        id_="SPEC-0001",
        severity="major",
        status="open",
        artifact="docs/spec/prd.md#NFR-01",
        title="NFR-01 not verifiable",
    )
    # resolved → must be skipped
    _write_finding(
        docs,
        "SPEC-0002.md",
        id_="SPEC-0002",
        severity="critical",
        status="resolved",
        artifact="docs/spec/vr.md#VR-001",
        title="fixed already",
    )
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, docs)

    count = ingestor.ingest_open_findings("requirements", 1)

    assert count == 1
    open_findings = store.list_open("requirements", 1)
    assert len(open_findings) == 1
    finding = open_findings[0]
    assert finding.code == "SPEC-0001"
    assert finding.severity == Severity.ERROR  # major → error
    assert finding.artifact == "docs/spec/prd.md#NFR-01"
    assert finding.message == "NFR-01 not verifiable"
    assert finding.source == FindingSource.SEMANTIC


def test_ingest_open_findings_missing_dir_returns_zero(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    ingestor = DefaultFindingIngestor(store, tmp_path / "docs" / "findings")
    assert ingestor.ingest_open_findings("requirements", 1) == 0
