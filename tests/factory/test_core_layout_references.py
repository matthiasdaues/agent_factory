"""Deterministic text checks for the core artifact layout.

Each block below owns one contract row of
docs/spec/core-artifact-layout-qa-strategy.md and carries its Rule's scope
identifier in a ``spec`` marker. Add a new contract as its own block with its
own test functions; share only the helpers in this header.

Owned contracts:
  - CAL-15-LN-01: feature-addition.md and brownfield-onboarding.md name the
    four anchor files, report each missing one, and do not name
    docs/CONTEXT.md as an anchor (structural)
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY = REPO_ROOT / "packages" / "factory"


def read_factory_file(relative: str) -> str:
    """Return the text of one file under packages/factory/."""
    return (FACTORY / relative).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """Return the section that starts at ``heading`` and ends before the next
    heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading)
    end = len(text)
    for marker in ("\n" + "#" * n + " " for n in range(1, level + 1)):
        found = text.find(marker, start + len(heading))
        if found != -1:
            end = min(end, found)
    return text[start:end]


# --- CAL-15-LN-01: anchor-file check in both playbooks -----------------------

ANCHOR_FILE_SET = (
    "docs/spec/architecture.dsl",
    "docs/spec/scope-map.md",
    "docs/spec/glossary.md",
    "docs/agent-context.md",
)

ANCHOR_CHECKS = {
    "feature-addition": ("playbooks/feature-addition.md", "## Prerequisites"),
    "brownfield-stage-1-exit": (
        "playbooks/brownfield-onboarding.md",
        "### Step 2.6 — Validate Stage 1 Exit",
    ),
}


def _anchor_check(name: str) -> str:
    path, heading = ANCHOR_CHECKS[name]
    return section(read_factory_file(path), heading)


@pytest.mark.spec("CAL-15")
@pytest.mark.parametrize("check", ANCHOR_CHECKS)
@pytest.mark.parametrize("anchor_file", ANCHOR_FILE_SET)
def test_anchor_check_names_each_anchor_file(check: str, anchor_file: str) -> None:
    assert f"`{anchor_file}`" in _anchor_check(check)


@pytest.mark.spec("CAL-15")
@pytest.mark.parametrize("check", ANCHOR_CHECKS)
def test_anchor_check_names_each_missing_file(check: str) -> None:
    assert "names each missing file" in _anchor_check(check)


@pytest.mark.spec("CAL-15")
def test_feature_addition_suggests_brownfield_onboarding_on_a_missing_file() -> None:
    text = _anchor_check("feature-addition")
    assert "suggest running `brownfield-onboarding`" in text


@pytest.mark.spec("CAL-15")
@pytest.mark.parametrize("check", ANCHOR_CHECKS)
def test_anchor_check_counts_four_anchor_files(check: str) -> None:
    text = _anchor_check(check)
    assert "four anchor files" in text
    assert "three anchor files" not in text


@pytest.mark.spec("CAL-15")
@pytest.mark.parametrize("path", sorted({path for path, _ in ANCHOR_CHECKS.values()}))
def test_playbook_names_no_context_md(path: str) -> None:
    assert "CONTEXT.md" not in read_factory_file(path)
