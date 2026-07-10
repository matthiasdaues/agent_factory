from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, List

from orchestrator.entities import Finding, FindingSource, FindingStatus, Severity
from orchestrator.ports import FindingsStore

# The findings store uses a three-level machine severity (error|warning|info).
# Reviewers report on the human review scales — critical/major/minor for most
# reviews (REPORT-FORMAT.md), high/medium/low for the security and ATAM reviews.
# Map every scale onto the store taxonomy so semantic findings are ingested and
# counted rather than silently dropped (which would make the review loop treat a
# phase with open Major defects as clean).
_SEVERITY_ALIASES = {
    "error": Severity.ERROR,
    "warning": Severity.WARNING,
    "info": Severity.INFO,
    "critical": Severity.ERROR,
    "major": Severity.ERROR,
    "high": Severity.ERROR,
    "medium": Severity.WARNING,
    "minor": Severity.WARNING,
    "low": Severity.INFO,
}
_FINDING_ID_RE = re.compile(r"^FND-(?P<number>\d+)$")


class DefaultFindingIngestor:
    """Reads the review agent's filed findings and writes them to the store.

    Implements the ``FindingIngestor`` port. The review agents file each
    finding as ``docs/findings/<TAG>-NNNN.md`` (strict frontmatter); this reads
    the ones still ``open``, maps them onto the finding DTO, and writes them to
    the store, which stamps the monotonic IDs (BR-019). Reading the filed files
    — rather than the reviewer's stdout — works whether the reviewer ran
    headless or in an interactive session where stdout is not captured
    (ADR-0012). The store this writes to remains the loop's sole source of
    truth; the filed markdown is the ingestion input it is projected from, not
    a second store (ADR-0019).
    """

    def __init__(self, store: FindingsStore, docs_findings_dir: Path) -> None:
        self._store = store
        self._docs_findings_dir = Path(docs_findings_dir)

    def ingest_open_findings(self, phase: str, iteration: int) -> int:
        raw = _read_open_findings(self._docs_findings_dir)
        findings = _build_findings(
            raw,
            phase=phase,
            iteration=iteration,
            source=FindingSource.SEMANTIC,
            created_by="reviewer",
            store=self._store,
        )
        self._store.ingest(findings)
        return len(findings)

    def ingest_gate_output(self, gate_output: str, phase: str, iteration: int) -> int:
        """Parse deterministic gate findings from pre-commit stdout and ingest."""
        findings = map_spec_lint(gate_output, phase, iteration, self._store)
        if findings:
            self._store.ingest(findings)
        return len(findings)


def _read_open_findings(docs_findings_dir: Path) -> list[dict[str, Any]]:
    """Return the normalized raw findings from every ``open`` finding file."""
    out: list[dict[str, Any]] = []
    if not docs_findings_dir.is_dir():
        return out
    for path in sorted(docs_findings_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        frontmatter, body = _split_frontmatter(text)
        if frontmatter is None:
            continue
        if str(frontmatter.get("status", "")).strip().lower() != "open":
            continue
        severity = _parse_severity(frontmatter.get("severity"))
        code = str(frontmatter.get("id", "")).strip()
        artifact = str(frontmatter.get("artifact", "")).strip().strip("`")
        message = _finding_title(body) or artifact
        missing: list[str] = []
        if severity is None:
            missing.append(f"severity={frontmatter.get('severity')!r}")
        if not code:
            missing.append("id")
        if not artifact:
            missing.append("artifact")
        if missing:
            raise ValueError(
                f"open finding {path.name} is missing or has invalid fields: "
                + ", ".join(missing)
            )
        out.append(
            {
                "code": code,
                "severity": severity,
                "artifact": artifact,
                "message": message,
            }
        )
    return out


def _split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Split a ``---`` YAML frontmatter block from the body (scalar fields only)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    fields: dict[str, str] = {}
    body_start = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body_start = index + 1
            break
        match = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", lines[index])
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("'\"")
    if body_start is None:
        return None, text
    return fields, "\n".join(lines[body_start:])


def _finding_title(body: str) -> str:
    for line in body.splitlines():
        match = re.match(r"^#\s+(.*\S)\s*$", line)
        if match:
            return match.group(1).strip()
    return ""


def map_spec_lint(
    json_output: str,
    phase: str,
    iteration: int,
    store: FindingsStore,
) -> List[Finding]:
    """Parse gate findings out of pre-commit stdout.

    Pre-commit stdout is commonly mixed text: hook banner lines wrapped around
    an embedded JSON ``{"findings": [...]}`` block, not a pure JSON document.
    ``_extract_json_findings`` tolerates that mixed shape, so a banner-plus-JSON
    gate transcript still yields its deterministic findings instead of being
    silently dropped.
    """
    if not json_output.strip():
        return []

    candidates = _extract_json_findings(json_output)
    if not candidates:
        return []

    normalized = _normalize_and_dedup(candidates)
    return _build_findings(
        normalized,
        phase=phase,
        iteration=iteration,
        source=FindingSource.SPEC_LINT,
        created_by="spec-lint",
        store=store,
    )


def _extract_json_findings(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    decoder = json.JSONDecoder()
    index = 0

    while index < len(text):
        match = re.search(r"[\[{]", text[index:])
        if not match:
            break

        start = index + match.start()
        try:
            payload, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            index = start + 1
            continue

        findings.extend(_walk_json_payload(payload))
        index = end

    return findings


def _walk_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        findings: list[dict[str, Any]] = []
        if _looks_like_finding(payload):
            findings.append(payload)

        nested = payload.get("findings")
        if isinstance(nested, list):
            for item in nested:
                findings.extend(_walk_json_payload(item))

        finding = payload.get("finding")
        if finding is not None:
            findings.extend(_walk_json_payload(finding))
        return findings

    if isinstance(payload, list):
        findings: list[dict[str, Any]] = []
        for item in payload:
            findings.extend(_walk_json_payload(item))
        return findings

    return []


def _normalize_and_dedup(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize raw candidates and drop content-duplicates.

    The deterministic gate scanner (``map_spec_lint``) walks JSON payloads that
    can legitimately yield the same logical finding more than once — e.g. a
    dict that is both finding-shaped and also nests a ``findings``/``finding``
    key, or repeated top-level JSON blocks in the same stdout (FAGAN-0045). Key
    on the finding's content, not identity, so re-ingesting duplicate stdout
    does not inflate ``open_count``.
    """
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for candidate in candidates:
        finding = _normalize_raw_finding(candidate)
        if not finding:
            continue
        key = (
            finding["code"],
            finding["severity"].value,
            finding["artifact"],
            finding["message"],
        )
        if key in seen:
            continue
        seen.add(key)
        normalized.append(finding)
    return normalized


def _normalize_raw_finding(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    code = raw.get("code")
    artifact = raw.get("artifact")
    message = raw.get("message")
    severity = _parse_severity(raw.get("severity"))

    if not all(
        isinstance(value, str) and value.strip() for value in (code, artifact, message)
    ):
        return None
    if severity is None:
        return None

    return {
        "code": code.strip(),
        "severity": severity,
        "artifact": artifact.strip().strip("`"),
        "message": message.strip(),
    }


def _parse_severity(value: Any) -> Severity | None:
    if not isinstance(value, str):
        return None
    return _SEVERITY_ALIASES.get(value.strip().lower())


def _looks_like_finding(payload: dict[str, Any]) -> bool:
    return {"code", "severity", "artifact", "message"}.issubset(payload)


def _build_findings(
    raw_findings: list[dict[str, Any]],
    *,
    phase: str,
    iteration: int,
    source: FindingSource,
    created_by: str,
    store: FindingsStore,
) -> List[Finding]:
    if not raw_findings:
        return []

    ids = list(_allocate_ids(store, len(raw_findings)))
    return [
        Finding(
            id=finding_id,
            phase=phase,
            iteration=iteration,
            source=source,
            code=raw_finding["code"],
            severity=raw_finding["severity"],
            artifact=raw_finding["artifact"],
            message=raw_finding["message"],
            status=FindingStatus.OPEN,
            created_by=created_by,
        )
        for finding_id, raw_finding in zip(ids, raw_findings)
    ]


def _allocate_ids(store: FindingsStore, count: int) -> Iterable[str]:
    match = _FINDING_ID_RE.match(store.next_id())
    start = int(match.group("number")) if match else 1
    for offset in range(count):
        yield f"FND-{start + offset:04d}"
