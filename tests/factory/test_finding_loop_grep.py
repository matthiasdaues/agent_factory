"""Loop greps of the playbooks run on a fixture (ST-0398, FC-13-IT-01).

Each playbook with a review loop names a `grep -l "^status: open"` command.
The test reads the command from the playbook text and runs it in a fixture
`docs/findings/`, so a rewritten grep that lists a waived finding fails here.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT

PLAYBOOKS = REPO_ROOT / "packages" / "factory" / "playbooks"
LOOP_GREP = re.compile(r'^grep -l "\^status: open" (\S+)(?: \| .*)?$', re.MULTILINE)


def _frontmatter(finding_id: str, severity: str, status: str, body: str) -> str:
    return f"---\nid: {finding_id}\nseverity: {severity}\nstatus: {status}\n---\n\n{body}\n"


@pytest.fixture
def findings_repo(tmp_path: Path) -> Path:
    findings = tmp_path / "docs" / "findings"
    (findings / "register" / "code").mkdir(parents=True)
    files = {
        "FAGAN-0042": ("major", "open", "A fixture finding."),
        "FAGAN-0043": ("major", "waived", 'The body quotes "status: open" once.'),
        "BUG-0037": ("critical", "open", "A confirmed critical finding."),
        "SPEC-0001": ("major", "open", "A spec finding."),
        "ATAM-0001": ("major", "open", "An architecture finding."),
        "IMPL-0001": ("major", "open", "An implementation finding."),
        "SEC-0001": ("major", "open", "A security finding."),
    }
    for name, (severity, status, body) in files.items():
        (findings / f"{name}.md").write_text(_frontmatter(name, severity, status, body))
    (findings / "register" / "code" / "FAGAN-0032.json").write_text(
        '{"id": "FAGAN-0032", "status": "open"}\n'
    )
    return tmp_path


def _greps() -> list[tuple[str, str]]:
    found = []
    for path in sorted(PLAYBOOKS.glob("*.md")):
        for match in LOOP_GREP.finditer(path.read_text(encoding="utf-8")):
            found.append((path.name, match.group(0).split(" | ")[0]))
    return found


def _run(command: str, cwd: Path) -> set[str]:
    result = subprocess.run(
        ["bash", "-c", command],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return {Path(line).name for line in result.stdout.splitlines() if line}


def test_st_0398_every_review_loop_playbook_names_an_anchored_grep() -> None:
    names = {name for name, _ in _greps()}
    for expected in (
        "feature-addition.md",
        "refactoring.md",
        "documentation-update.md",
        "architecture-review.md",
        "bug-fix.md",
        "greenfield-development.md",
    ):
        assert expected in names, f"{expected} names no anchored loop grep"


def test_st_0398_no_playbook_keeps_an_unanchored_loop_grep() -> None:
    for path in PLAYBOOKS.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'grep (-\w+ )?"status: open"', text), path.name


@pytest.mark.parametrize(("playbook", "command"), _greps())
def test_st_0398_fc_13_it_01_loop_grep_lists_open_findings_not_waived_ones(
    playbook: str, command: str, findings_repo: Path
) -> None:
    listed = _run(command, findings_repo)
    assert "FAGAN-0043.md" not in listed, f"{playbook} lists a waived finding"
    assert "FAGAN-0032.json" not in listed, f"{playbook} lists a register file"
    assert listed, f"{playbook} lists no open finding"


def test_st_0398_demo_grep_lists_the_open_finding_only(findings_repo: Path) -> None:
    command = 'grep -l "^status: open" docs/findings/*.md'
    listed = _run(command, findings_repo)
    assert "FAGAN-0042.md" in listed
    assert "BUG-0037.md" in listed
    assert "FAGAN-0043.md" not in listed
