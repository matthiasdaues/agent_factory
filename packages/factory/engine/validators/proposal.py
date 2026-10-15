"""Proposal readiness validator.

Checks file existence, format (markdown with frontmatter), and required
fields. Returns the shared validator result shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class ValidatorResult:
    artifact_type: str
    artifact_ref: str
    assessed_commit: str
    checks: tuple[Check, ...]
    warnings: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


REQUIRED_SECTIONS = ("Problem", "Solution", "Scope")
REQUIRED_FRONTMATTER = ("title", "status")


def _parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return None


def validate_proposal(path: Path, assessed_commit: str = "unknown") -> ValidatorResult:
    """Validate a proposal file for readiness evidence."""
    path = Path(path)
    checks: list[Check] = []
    warnings: list[str] = []
    commit = assessed_commit

    checks.append(
        Check(
            name="file_exists",
            passed=path.exists(),
            detail=str(path),
        )
    )
    if not path.exists():
        warnings.append(f"proposal not found: {path}")
        return ValidatorResult(
            artifact_type="proposal",
            artifact_ref=str(path),
            assessed_commit=commit,
            checks=tuple(checks),
            warnings=tuple(warnings),
        )

    text = path.read_text()

    fm = _parse_frontmatter(text)
    checks.append(
        Check(
            name="frontmatter_present",
            passed=fm is not None,
            detail="YAML frontmatter block" if fm else "no frontmatter found",
        )
    )

    if fm is not None:
        for field_name in REQUIRED_FRONTMATTER:
            present = field_name in fm and fm[field_name]
            checks.append(
                Check(
                    name=f"frontmatter_{field_name}",
                    passed=present,
                    detail=fm.get(field_name, "missing"),
                )
            )
            if not present:
                warnings.append(f"missing frontmatter field: {field_name}")

        status = fm.get("status", "")
        checks.append(
            Check(
                name="status_accepted",
                passed=status == "accepted",
                detail=f"status is '{status}'",
            )
        )
        if status != "accepted":
            warnings.append(f"proposal status is '{status}', expected 'accepted'")

    for section in REQUIRED_SECTIONS:
        found = f"## {section}" in text or f"# {section}" in text
        checks.append(
            Check(
                name=f"section_{section.lower()}",
                passed=found,
                detail=f"section '{section}' {'found' if found else 'missing'}",
            )
        )
        if not found:
            warnings.append(f"missing required section: {section}")

    return ValidatorResult(
        artifact_type="proposal",
        artifact_ref=str(path),
        assessed_commit=commit,
        checks=tuple(checks),
        warnings=tuple(warnings),
    )
