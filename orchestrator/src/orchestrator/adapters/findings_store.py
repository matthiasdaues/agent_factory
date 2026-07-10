from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, List
from uuid import uuid4

from jsonschema import Draft202012Validator

from orchestrator.entities import Finding, FindingSource, FindingStatus, Severity

_FINDING_ID_RE = re.compile(r"^FND-(\d{4,})$")
_FINDING_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Finding",
    "type": "object",
    "required": [
        "id",
        "phase",
        "iteration",
        "source",
        "code",
        "severity",
        "artifact",
        "message",
        "status",
    ],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "string", "pattern": r"^FND-[0-9]{4,}$"},
        "phase": {"type": "string"},
        "iteration": {"type": "integer", "minimum": 1},
        "source": {"enum": ["spec-lint", "semantic"]},
        "code": {"type": "string"},
        "severity": {"enum": ["error", "warning", "info"]},
        "artifact": {"type": "string"},
        "message": {"type": "string"},
        "status": {"enum": ["open", "superseded", "resolved"]},
        "created_by": {"type": "string"},
        "resolved_by": {"type": ["string", "null"]},
    },
}
_VALIDATOR = Draft202012Validator(_FINDING_SCHEMA)


class FilesystemFindingsStore:
    def __init__(self, findings_dir: Path) -> None:
        self.findings_dir = findings_dir
        self.findings_dir.mkdir(parents=True, exist_ok=True)

    def ingest(self, findings: List[Finding]) -> None:
        for finding in findings:
            self._save(finding)

    def supersede_prior(self, phase: str, current_iteration: int) -> int:
        superseded = 0
        for finding in self._all_findings():
            if (
                finding.phase == phase
                and finding.iteration < current_iteration
                and finding.status == FindingStatus.OPEN
            ):
                finding.status = FindingStatus.SUPERSEDED
                self._save(finding)
                superseded += 1
        return superseded

    def open_count(self, phase: str, iteration: int) -> int:
        return len(self.list_open(phase, iteration))

    def list_open(self, phase: str, iteration: int) -> List[Finding]:
        return [
            finding
            for finding in self._all_findings()
            if finding.phase == phase
            and finding.iteration == iteration
            and finding.status == FindingStatus.OPEN
        ]

    def next_id(self) -> str:
        max_id = 0
        for path in self.findings_dir.glob("FND-*.json"):
            match = _FINDING_ID_RE.match(path.stem)
            if match:
                max_id = max(max_id, int(match.group(1)))
        return f"FND-{max_id + 1:04d}"

    def _load(self, path: Path) -> Finding:
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._validate_payload(payload)
        return Finding(
            id=payload["id"],
            phase=payload["phase"],
            iteration=payload["iteration"],
            source=FindingSource(payload["source"]),
            code=payload["code"],
            severity=Severity(payload["severity"]),
            artifact=payload["artifact"],
            message=payload["message"],
            status=FindingStatus(payload["status"]),
            created_by=payload.get("created_by", ""),
            resolved_by=payload.get("resolved_by"),
        )

    def _save(self, finding: Finding) -> None:
        payload = self._serialize(finding)
        self._validate_payload(payload)
        target = self.findings_dir / f"{finding.id}.json"
        temp = self.findings_dir / f".{finding.id}.{uuid4().hex}.tmp"
        temp.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.replace(temp, target)

    def _all_findings(self) -> List[Finding]:
        return [
            self._load(path) for path in sorted(self.findings_dir.glob("FND-*.json"))
        ]

    def _serialize(self, finding: Finding) -> dict[str, Any]:
        return {
            "id": finding.id,
            "phase": finding.phase,
            "iteration": finding.iteration,
            "source": finding.source.value,
            "code": finding.code,
            "severity": finding.severity.value,
            "artifact": finding.artifact,
            "message": finding.message,
            "status": finding.status.value,
            "created_by": finding.created_by,
            "resolved_by": finding.resolved_by,
        }

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        errors = sorted(
            _VALIDATOR.iter_errors(payload), key=lambda error: list(error.path)
        )
        if errors:
            raise ValueError(errors[0].message)
