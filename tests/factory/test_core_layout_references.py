"""Deterministic text checks for the core artifact layout.

Each block below owns one contract row of
docs/spec/core-artifact-layout-qa-strategy.md and carries its Rule's scope
identifier in a ``spec`` marker. Add a new contract as its own block with its
own test functions; share only the helpers in this header.

Owned contracts:
  - CAL-15-LN-01: feature-addition.md and brownfield-onboarding.md name the
    four anchor files, report each missing one, and do not name
    docs/CONTEXT.md as an anchor (structural)
  - CAL-12-LN-01: domain-modeling writes terms as Term/Definition/Avoid rows
    of docs/spec/glossary.md, the term readers look terms up there, and no
    owned file names a CONTEXT.md as a term store (structural)
"""

from __future__ import annotations

import re
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


# --- CAL-12-LN-01: glossary table rows, not CONTEXT.md ----------------------

GLOSSARY = "docs/spec/glossary.md"
GLOSSARY_HEADER = re.compile(r"^\| Term +\| Definition +\| Avoid +\|$", re.MULTILINE)
OLD_ROUTING_FILE = re.compile(r"CONTEXT(-MAP)?\.md")

GLOSSARY_READERS = (
    "skills/grilling/SKILL.md",
    "skills/write-adr/SKILL.md",
    "skills/process-transcript/SKILL.md",
    "skills/inspect-spec/SKILL.md",
    "skills/fagan-review/SKILL.md",
    "skills/reconcile-spec/SKILL.md",
    "skills/scratchpad/SKILL.md",
    "agents/proposal-review-agent.md",
)

GLOSSARY_FILES = (
    "skills/domain-modeling/SKILL.md",
    *GLOSSARY_READERS,
    "rulebooks/conventions/context-format.md",
    "rulebooks/conventions/markdown-formatting.md",
    "rulebooks/templates/glossary.md",
)


def _domain_modeling_writer() -> str:
    return section(
        read_factory_file("skills/domain-modeling/SKILL.md"),
        f"### Update {GLOSSARY} inline",
    )


@pytest.mark.spec("CAL-12")
def test_domain_modeling_writes_term_rows_into_the_glossary() -> None:
    text = _domain_modeling_writer()
    assert f"`{GLOSSARY}`" in text
    assert "Term, Definition, and Avoid" in text
    assert "row" in text


@pytest.mark.spec("CAL-12")
def test_domain_modeling_creates_a_missing_section_for_the_context() -> None:
    assert "creates the section" in _domain_modeling_writer()


@pytest.mark.spec("CAL-12")
def test_domain_modeling_updates_an_existing_row_instead_of_a_second_one() -> None:
    assert "updates the existing row" in _domain_modeling_writer()


@pytest.mark.spec("CAL-12")
def test_domain_modeling_names_no_context_md_as_term_store() -> None:
    text = read_factory_file("skills/domain-modeling/SKILL.md")
    assert not OLD_ROUTING_FILE.search(text)


@pytest.mark.spec("CAL-12")
def test_glossary_template_replaces_the_context_template() -> None:
    assert not (FACTORY / "rulebooks/templates/context.md").exists()
    assert GLOSSARY_HEADER.search(read_factory_file("rulebooks/templates/glossary.md"))


@pytest.mark.spec("CAL-12")
def test_no_factory_file_links_the_old_context_template() -> None:
    offenders = [
        str(path.relative_to(FACTORY))
        for path in FACTORY.rglob("*.md")
        if "templates/context.md" in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


@pytest.mark.spec("CAL-12")
@pytest.mark.parametrize("path", GLOSSARY_READERS)
def test_term_reader_looks_terms_up_in_the_glossary(path: str) -> None:
    assert GLOSSARY in read_factory_file(path)


@pytest.mark.spec("CAL-12")
@pytest.mark.parametrize("path", GLOSSARY_FILES)
def test_glossary_file_names_no_context_md(path: str) -> None:
    assert not OLD_ROUTING_FILE.search(read_factory_file(path))
