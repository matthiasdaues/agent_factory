from __future__ import annotations

import json
from pathlib import Path

from orchestrator.adapters.findings_store import FilesystemFindingsStore
from orchestrator.entities import Finding, FindingSource, FindingStatus, Severity
from orchestrator.ports import FindingsStore


def _finding(
    *,
    finding_id: str,
    phase: str = "reviewing",
    iteration: int = 1,
    source: FindingSource = FindingSource.SPEC_LINT,
    code: str = "SPEC-001",
    severity: Severity = Severity.ERROR,
    artifact: str = "docs/spec.md",
    message: str = "Problem found",
    status: FindingStatus = FindingStatus.OPEN,
    created_by: str = "spec-lint",
    resolved_by: str | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        phase=phase,
        iteration=iteration,
        source=source,
        code=code,
        severity=severity,
        artifact=artifact,
        message=message,
        status=status,
        created_by=created_by,
        resolved_by=resolved_by,
    )


def test_store_satisfies_port(tmp_path: Path):
    assert isinstance(FilesystemFindingsStore(tmp_path / "findings"), FindingsStore)


def test_ingest_writes_files(tmp_path: Path):
    findings_dir = tmp_path / "findings"
    store = FilesystemFindingsStore(findings_dir)

    store.ingest([_finding(finding_id="FND-0001"), _finding(finding_id="FND-0002")])

    assert (findings_dir / "FND-0001.json").is_file()
    assert (findings_dir / "FND-0002.json").is_file()


def test_load_accepts_payload_without_created_by_or_resolved_by(tmp_path: Path):
    findings_dir = tmp_path / "findings"
    findings_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": "FND-0001",
        "phase": "reviewing",
        "iteration": 1,
        "source": "semantic",
        "code": "SEM-001",
        "severity": "error",
        "artifact": "docs/spec.md",
        "message": "Problem found",
        "status": "open",
    }
    (findings_dir / "FND-0001.json").write_text(json.dumps(payload), encoding="utf-8")

    finding = FilesystemFindingsStore(findings_dir)._load(
        findings_dir / "FND-0001.json"
    )

    assert finding == _finding(
        finding_id="FND-0001",
        source=FindingSource.SEMANTIC,
        code="SEM-001",
        created_by="",
        resolved_by=None,
    )


def test_ingest_writes_valid_json_fields(tmp_path: Path):
    findings_dir = tmp_path / "findings"
    store = FilesystemFindingsStore(findings_dir)
    finding = _finding(
        finding_id="FND-0420",
        phase="gating",
        iteration=3,
        source=FindingSource.SEMANTIC,
        code="SEM-004",
        severity=Severity.WARNING,
        artifact="src/orchestrator/core.py",
        message="Please clarify branch condition.",
        status=FindingStatus.RESOLVED,
        created_by="reviewer",
        resolved_by="operator",
    )

    store.ingest([finding])

    payload = json.loads((findings_dir / "FND-0420.json").read_text(encoding="utf-8"))
    assert payload == {
        "id": "FND-0420",
        "phase": "gating",
        "iteration": 3,
        "source": "semantic",
        "code": "SEM-004",
        "severity": "warning",
        "artifact": "src/orchestrator/core.py",
        "message": "Please clarify branch condition.",
        "status": "resolved",
        "created_by": "reviewer",
        "resolved_by": "operator",
    }


def test_next_id_returns_monotonically_increasing_ids(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")

    assert store.next_id() == "FND-0001"
    store.ingest([_finding(finding_id="FND-0007"), _finding(finding_id="FND-0042")])

    assert store.next_id() == "FND-0043"
    store.ingest([_finding(finding_id=store.next_id())])
    assert store.next_id() == "FND-0044"


def test_supersede_prior_marks_only_prior_open_findings(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    store.ingest(
        [
            _finding(finding_id="FND-0001", phase="reviewing", iteration=1),
            _finding(finding_id="FND-0002", phase="reviewing", iteration=2),
            _finding(
                finding_id="FND-0003",
                phase="reviewing",
                iteration=2,
                status=FindingStatus.RESOLVED,
            ),
            _finding(finding_id="FND-0004", phase="reviewing", iteration=3),
            _finding(finding_id="FND-0005", phase="gating", iteration=1),
        ]
    )

    superseded = store.supersede_prior("reviewing", current_iteration=3)

    assert superseded == 2
    assert (
        store._load(tmp_path / "findings" / "FND-0001.json").status
        == FindingStatus.SUPERSEDED
    )
    assert (
        store._load(tmp_path / "findings" / "FND-0002.json").status
        == FindingStatus.SUPERSEDED
    )
    assert (
        store._load(tmp_path / "findings" / "FND-0003.json").status
        == FindingStatus.RESOLVED
    )
    assert (
        store._load(tmp_path / "findings" / "FND-0004.json").status
        == FindingStatus.OPEN
    )
    assert (
        store._load(tmp_path / "findings" / "FND-0005.json").status
        == FindingStatus.OPEN
    )


def test_open_count_returns_matching_open_findings(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    store.ingest(
        [
            _finding(finding_id="FND-0001", phase="reviewing", iteration=2),
            _finding(finding_id="FND-0002", phase="reviewing", iteration=2),
            _finding(
                finding_id="FND-0003",
                phase="reviewing",
                iteration=2,
                status=FindingStatus.SUPERSEDED,
            ),
            _finding(finding_id="FND-0004", phase="reviewing", iteration=3),
            _finding(finding_id="FND-0005", phase="gating", iteration=2),
        ]
    )

    assert store.open_count("reviewing", 2) == 2


def test_list_open_returns_matching_open_findings(tmp_path: Path):
    store = FilesystemFindingsStore(tmp_path / "findings")
    expected = [
        _finding(finding_id="FND-0002", phase="reviewing", iteration=4),
        _finding(
            finding_id="FND-0001",
            phase="reviewing",
            iteration=4,
            source=FindingSource.SEMANTIC,
            code="SEM-101",
            severity=Severity.INFO,
        ),
    ]
    store.ingest(
        expected
        + [
            _finding(
                finding_id="FND-0003",
                phase="reviewing",
                iteration=4,
                status=FindingStatus.RESOLVED,
            ),
            _finding(finding_id="FND-0004", phase="reviewing", iteration=3),
            _finding(finding_id="FND-0005", phase="gating", iteration=4),
        ]
    )

    findings = store.list_open("reviewing", 4)

    assert [finding.id for finding in findings] == ["FND-0001", "FND-0002"]
    assert findings == sorted(expected, key=lambda finding: finding.id)


def test_round_trip_load_matches_ingested_finding(tmp_path: Path):
    findings_dir = tmp_path / "findings"
    store = FilesystemFindingsStore(findings_dir)
    finding = _finding(
        finding_id="FND-0099",
        phase="implementation",
        iteration=6,
        source=FindingSource.SEMANTIC,
        code="SEM-009",
        severity=Severity.INFO,
        artifact="src/orchestrator/adapters/findings_store.py",
        message="Looks good now.",
        created_by="reviewer",
        resolved_by=None,
    )

    store.ingest([finding])

    assert store._load(findings_dir / "FND-0099.json") == finding
