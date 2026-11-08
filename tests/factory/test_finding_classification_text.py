"""Text checks of the finding-classification rulebook (ST-0386).

The rulebook packages/factory/rulebooks/conventions/finding-classification.md
holds the one set of classification rules. These tests read it, the older
rulebooks that link it, and the envelope examples.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT

RULEBOOKS = REPO_ROOT / "packages" / "factory" / "rulebooks"
RULEBOOK = RULEBOOKS / "conventions" / "finding-classification.md"
REPORT_FORMAT = RULEBOOKS / "conventions" / "report-format.md"
FINDING_FORMAT = RULEBOOKS / "conventions" / "finding-format.md"
OWASP = RULEBOOKS / "principles" / "owasp-top-10.md"
RULES = RULEBOOKS / "rules.md"
INTERFACE_CONTRACTS = REPO_ROOT / "docs" / "spec" / "interface-contracts.md"
FINDINGS = REPO_ROOT / "docs" / "findings"

CLASSES = ("document", "code", "security", "architecture", "runtime")
LEVELS = ("critical", "major", "minor", "note")
# The agreement check of ST-0390 uses these three, so no example may name them.
AGREEMENT_SET = ("FAGAN-0021", "SEC-0005", "SEC-0006")
FINDING_ID = re.compile(r"\b[A-Z]+-\d{4}\b")
PATH_SPAN = re.compile(r"`((?:packages|docs)/[^`\s:#]+)")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    """Join wrapped lines so a phrase can be found across a line break."""
    return re.sub(r"\s+", " ", text)


def _section(text: str, heading: str) -> str:
    """Return the body under a heading, up to the next heading of its level."""
    match = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"heading {heading!r} is missing"
    level = len(match.group(1))
    rest = text[match.end() :]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


def _register_ids() -> set[str]:
    ids: set[str] = set()
    register = FINDINGS / "register"
    for path in register.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                ids.add(json.loads(line)["id"])
    ids.update(path.stem for path in register.glob("*/*.json"))
    return ids


def _example_rows(class_name: str) -> list[list[str]]:
    """Return the cells of each row of the calibration table of a class."""
    body = _section(_text(RULEBOOK), f"Class: {class_name}")
    table = _section(body, "Calibration examples")
    rows = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0].strip("`") in LEVELS:
            rows.append(cells)
    return rows


@pytest.mark.spec("FC-01-LN-01")
def test_st_0386_rulebook_holds_values_scale_tree_and_class_sections():
    text = _text(RULEBOOK)
    for heading in (
        "The values of a finding",
        "Shared severity scale and blocking rule",
        "In use",
        "The consequence tree",
        "Type from the fix",
    ):
        _section(text, heading)
    for class_name in CLASSES:
        _section(text, f"Class: {class_name}")
    values = _flat(_section(text, "The values of a finding"))
    for value in ("Category", "Type", "Severity", "Blocking"):
        assert f"| {value} " in values
    scale = _section(text, "Shared severity scale and blocking rule")
    for level in LEVELS:
        assert f"`{level}`" in scale
    tree = _flat(_section(text, "The consequence tree"))
    order = [
        tree.index(f"`{q}`")
        for q in ("harms_downstream", "fails_purpose", "raises_cost")
    ]
    assert order == sorted(order)


@pytest.mark.spec("FC-01-LN-02")
@pytest.mark.parametrize("class_name", CLASSES)
def test_st_0386_each_level_has_two_or_three_real_examples_or_one_invented(class_name):
    known = {path.stem for path in FINDINGS.glob("*.md")} | _register_ids()
    rows = _example_rows(class_name)
    for level in LEVELS:
        level_rows = [row for row in rows if row[0].strip("`") == level]
        real = [row for row in level_rows if "Invented" not in row[1]]
        invented = [row for row in level_rows if "Invented" in row[1]]
        if real:
            assert 2 <= len(real) <= 3, (
                f"{class_name}/{level}: {len(real)} real examples"
            )
            assert not invented, (
                f"{class_name}/{level} mixes real and invented examples"
            )
        else:
            assert len(invented) == 1, (
                f"{class_name}/{level}: needs one invented example"
            )
        for row in real:
            ids = FINDING_ID.findall(row[1])
            assert ids, f"{class_name}/{level}: a real example names no ID"
            for finding_id in ids:
                assert finding_id in known, f"{finding_id} is not in docs/findings/"
            assert row[2], f"{class_name}/{level}: {ids[0]} has no basis"
        for row in invented:
            paths = PATH_SPAN.findall(" ".join(row))
            assert paths, f"{class_name}/{level}: the invented example names no file"
            for path in paths:
                assert (REPO_ROOT / path).exists(), f"{path} does not exist"


@pytest.mark.spec("FC-01-LN-02")
def test_st_0386_no_example_names_a_finding_of_the_agreement_check():
    text = _text(RULEBOOK)
    for finding_id in AGREEMENT_SET:
        assert finding_id not in text


@pytest.mark.spec("FC-02-LN-01")
def test_st_0386_rulebook_states_the_class_and_filing_rules():
    text = _flat(_text(RULEBOOK))
    for phrase in (
        "The reviewed material decides the class",
        "playbooks, skills, agent definitions, rulebooks, and hook configuration",
        "the change that the `**Fix:**` line demands",
        "`docs/spec/work/todo.md`",
        "An observation that names no artifact is not a finding",
        "A `suggestion` of the document, code, or runtime class describes material that works",
        "`nitpick` always gives `note`",
        "its category is `defect` or `risk` and its severity is `critical` or `major`",
    ):
        assert phrase in text, phrase


@pytest.mark.spec("FC-04-LN-01")
def test_st_0386_an_attack_that_needs_the_capability_it_gains_is_not_a_finding():
    security = _flat(_section(_text(RULEBOOK), "Class: security"))
    assert "An attack that needs the capability it gains is not a finding" in security


@pytest.mark.spec("FC-09-LN-01")
@pytest.mark.parametrize(
    "path",
    [REPORT_FORMAT, INTERFACE_CONTRACTS],
    ids=["report-format", "interface-contracts"],
)
def test_st_0386_envelope_example_carries_four_keys(path):
    counts = re.findall(r'"finding_counts":\s*(\{[^}]*\})', _text(path))
    assert counts, f"{path.name} has no finding_counts example"
    for raw in counts:
        assert set(json.loads(raw)) == set(LEVELS)


@pytest.mark.spec("FC-09-LN-01")
def test_st_0386_claim_review_counts_a_blocker_under_major():
    text = _flat(_text(RULEBOOK))
    assert "A BLOCKER counts under `major`" in text
    assert "nothing under `critical`" in text


@pytest.mark.spec("FC-17-LN-01")
def test_st_0386_rulebook_states_the_waiver_rules():
    waiver = _flat(_section(_text(RULEBOOK), "Waiver and confirmation"))
    for phrase in (
        "keeps its computed severity",
        "only after the stakeholder has confirmed its stop",
        "No override raises a `minor` finding",
        "never with `deferred`",
        "never by a lowering to a `note`",
        "the register file stays",
        "`override_by` and `override_reason`",
        "`stop_confirmed_by` and `stop_confirmed_reason`",
    ):
        assert phrase in waiver, phrase


LEVEL_DEFINITION = re.compile(
    r"\*\*(Critical|Major|Minor|High|Medium|Low)\*\*\s*[—:-]"
    r"|Critical\s*/\s*High"
    r"|Medium or higher"
    r"|blocking severity is",
)


@pytest.mark.parametrize(
    ("path", "heading"),
    [
        (REPORT_FORMAT, "Category rules"),
        (REPORT_FORMAT, "Severity"),
        (FINDING_FORMAT, "When to file"),
        (OWASP, None),
        (RULES, "Findings"),
    ],
    ids=[
        "report-format-category",
        "report-format-severity",
        "finding-format",
        "owasp",
        "rules",
    ],
)
def test_st_0386_older_rulebooks_link_the_rulebook_and_define_no_level(path, heading):
    text = _text(path)
    body = _section(text, heading) if heading else text
    assert "finding-classification.md" in body
    assert not LEVEL_DEFINITION.search(body), LEVEL_DEFINITION.search(body)


# ST-0387: the twelve review files, the finding template, and the register rule.

FACTORY = REPO_ROOT / "packages" / "factory"
TEMPLATE = RULEBOOKS / "templates" / "finding.md"
RULEBOOK_LINK = "finding-classification.md#class-"
# The rows of the Scenario Outline in FC-01: the file and the classes it links.
REVIEW_FILES = {
    "skills/inspect-spec/SKILL.md": ("document",),
    "skills/reconcile-spec/SKILL.md": ("document",),
    "agents/proposal-review-agent.md": ("document",),
    "agents/spec-review-agent.md": ("document",),
    "agents/reconciliation-agent.md": ("document",),
    "skills/fagan-review/SKILL.md": ("code",),
    "agents/code-review-agent.md": ("code",),
    "skills/security-review/SKILL.md": ("security",),
    "skills/atam-review/SKILL.md": ("architecture",),
    "agents/architecture-review-agent.md": ("architecture",),
    "skills/bug-hunt/SKILL.md": ("runtime",),
    "agents/qa-agent.md": ("code", "security", "runtime"),
}
REVIEW_SKILLS = {
    path: classes[0]
    for path, classes in REVIEW_FILES.items()
    if path.startswith("skills/")
}
# A table row that starts with a level names that level and gives its meaning.
LEVEL_ROW = re.compile(
    r"^\|\s*`?(critical|major|minor|note|high|medium|low)`?\s*\|",
    re.IGNORECASE | re.MULTILINE,
)
HUMAN_FIELDS = (
    "override_by",
    "override_reason",
    "stop_confirmed_by",
    "stop_confirmed_reason",
)
TEMPLATE_FIELDS = (
    "id",
    "source",
    "review_class",
    "category",
    "type",
    "severity",
    "basis",
    "rating",
    *HUMAN_FIELDS,
    "artifact",
    "status",
    "owner",
    "traces",
)


@pytest.mark.spec("FC-01-LN-03")
@pytest.mark.parametrize("relative", sorted(REVIEW_FILES))
def test_st_0387_review_file_links_its_class_section_and_defines_no_severity(relative):
    text = _text(FACTORY / relative)
    for class_name in REVIEW_FILES[relative]:
        assert f"{RULEBOOK_LINK}{class_name})" in text, (
            f"{relative} lacks the link to Class: {class_name}"
        )
    assert not LEVEL_DEFINITION.search(text), LEVEL_DEFINITION.search(text)
    assert not LEVEL_ROW.search(text), LEVEL_ROW.search(text)


@pytest.mark.spec("FC-01-LN-03")
def test_st_0387_fagan_review_names_the_class_code():
    text = _text(FACTORY / "skills" / "fagan-review" / "SKILL.md")
    assert "review class `code`" in text
    assert "[Class: code]" in text


@pytest.mark.spec("FC-05-LN-01")
def test_st_0387_a_non_risk_names_its_assumptions():
    architecture = _flat(_section(_text(RULEBOOK), "Class: architecture"))
    assert "each non-risk names its assumptions" in architecture
    for relative in (
        "skills/atam-review/SKILL.md",
        "agents/architecture-review-agent.md",
    ):
        assert "A non-risk names the assumptions it rests on" in _flat(
            _text(FACTORY / relative)
        )


def _template_frontmatter_keys() -> list[str]:
    block = _section(_text(TEMPLATE), "Frontmatter")
    code = re.search(r"```markdown\n---\n(.*?)\n---\n```", block, re.DOTALL)
    assert code, "the Frontmatter section holds no frontmatter block"
    return re.findall(r"^([a-z_]+):(?:[ \t]|$)", code.group(1), re.MULTILINE)


@pytest.mark.spec("FC-06-LN-01")
def test_st_0387_template_holds_the_sixteen_frontmatter_fields():
    assert _template_frontmatter_keys() == list(TEMPLATE_FIELDS)


@pytest.mark.spec("FC-06-LN-01")
def test_st_0387_template_leaves_the_human_fields_null():
    block = _section(_text(TEMPLATE), "Frontmatter")
    for field in HUMAN_FIELDS:
        assert re.search(rf"^{field}:[ \t]*(#.*)?$", block, re.MULTILINE), (
            f"{field} must carry no value"
        )


@pytest.mark.spec("FC-06-LN-01")
def test_st_0387_template_holds_the_body_lines_and_the_possible_damage_section():
    text = _text(TEMPLATE)
    for line in ("**What is wrong:**", "**Why this severity:**", "**Fix:**"):
        assert line in text
    assert (
        text.index("**What is wrong:**")
        < text.index("**Why this severity:**")
        < text.index("**Fix:**")
    )
    assert "## Possible damage" in text
    assert (
        "A `critical` finding ends with this section. No other severity holds it."
        in _flat(text)
    )
    assert "— check:" in text


@pytest.mark.spec("FC-06-LN-01")
def test_st_0387_template_lists_the_status_values_and_who_sets_them():
    status = _flat(_section(_text(TEMPLATE), "Frontmatter"))
    for phrase in (
        "`open` and `resolved`: set by an agent",
        "`waived`: set by the stakeholder only",
        "`deferred`: set by the migration only",
    ):
        assert phrase in status, phrase


@pytest.mark.spec("FC-07-LN-01")
@pytest.mark.parametrize(("relative", "class_name"), sorted(REVIEW_SKILLS.items()))
def test_st_0387_review_skill_writes_a_minor_finding_as_a_register_file(
    relative, class_name
):
    text = _flat(_text(FACTORY / relative))
    assert f"`docs/findings/register/{class_name}/<ID>.json`" in text
    assert "`status: open`" in text
    assert "no finding file" in text
    assert re.search(
        r"sets (?:`status` of the register file|its `status`) to `resolved`", text
    )


@pytest.mark.spec("FC-07-LN-01")
def test_st_0387_finding_format_resolves_a_register_file_and_names_two_removals():
    text = _flat(_text(FINDING_FORMAT))
    assert (
        "The commit that fixes a `minor` finding sets `status` of its register file to `resolved`."
        " The register file stays." in text
    )
    removal = _flat(_section(_text(FINDING_FORMAT), "Removal of a finding file"))
    assert "The migration moves a `minor` finding" in removal
    assert "The stakeholder lowers a blocking finding" in removal
    assert "Each one leaves a register file under the same ID" in removal


# ST-0389: the QA triage table states the consequence, not a severity.

QA_TEMPLATE = RULEBOOKS / "templates" / "qa-strategy.md"
TRIAGE_CONSEQUENCES = ("harm if in use", "fails purpose", "raises cost")


def _table_header_and_rows(section: str) -> tuple[list[str], list[list[str]]]:
    """Return the header cells and the body rows of the first table in a section."""
    lines = [line for line in section.splitlines() if line.startswith("|")]
    assert len(lines) >= 3, "the section holds no table"

    def cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    return cells(lines[0]), [cells(line) for line in lines[2:]]


@pytest.mark.spec("FC-19-LN-01")
def test_st_0389_triage_table_has_a_consequence_column_and_no_severity_column():
    header, rows = _table_header_and_rows(
        _section(_text(QA_TEMPLATE), "Defect Severity Triage")
    )
    assert "Consequence" in header
    assert not [cell for cell in header if cell.lower().startswith("severity")], header
    column = header.index("Consequence")
    consequences = [row[column].strip('"') for row in rows]
    assert consequences == list(TRIAGE_CONSEQUENCES)


# ST-0388: the proposal-review agent rates each Appendix row with two questions.

PROPOSAL_AGENT = FACTORY / "agents" / "proposal-review-agent.md"
PROPOSAL_TEMPLATE = RULEBOOKS / "templates" / "proposal.md"


@pytest.mark.spec("FC-08-LN-01")
def test_st_0388_agent_asks_two_questions_and_writes_the_severity_sentence():
    text = _flat(_text(PROPOSAL_AGENT))
    order = [text.index(f"`{q}`") for q in ("fails_purpose", "raises_cost")]
    assert order == sorted(order)
    assert "A yes gives `major`" in text
    assert "A yes gives `minor`" in text
    assert "Two no answers give `note`" in text
    assert "A row is never `critical`" in text
    assert "`Severity:`" in text


@pytest.mark.spec("FC-08-LN-01")
def test_st_0388_agent_never_sets_waived():
    text = _flat(_text(PROPOSAL_AGENT))
    assert "The agent never sets `waived`" in text


@pytest.mark.spec("FC-08-LN-01")
def test_st_0388_template_lists_waived_as_stakeholder_only_on_a_major_row():
    section = _flat(_section(_text(PROPOSAL_TEMPLATE), "Review findings"))
    assert "Only the stakeholder sets `waived`, and only on a `major` row" in section
    assert "with the reason in Resolution" in section
    assert "never `critical`" in section


# ST-0398: the loop, the stop notice, the confirmation, and the waiver.
PLAYBOOKS = REPO_ROOT / "packages" / "factory" / "playbooks"
SKILLS = REPO_ROOT / "packages" / "factory" / "skills"
LOOP_PLAYBOOKS = (
    "feature-addition",
    "refactoring",
    "documentation-update",
    "architecture-review",
    "bug-fix",
    "greenfield-development",
)


@pytest.mark.spec("FC-13-LN-01")
def test_st_0398_confirmed_critical_finding_loops_back_and_keeps_severity():
    text = _flat(_text(FINDING_FORMAT))
    assert (
        "A confirmed `critical` finding loops back to its owner like a `major` one"
        in text
    )
    assert "it keeps severity `critical`" in text


@pytest.mark.spec("FC-14-LN-01")
@pytest.mark.parametrize("name", LOOP_PLAYBOOKS)
def test_st_0398_playbook_explains_the_stop_and_ends_a_headless_run(name):
    text = _flat(_text(PLAYBOOKS / f"{name}.md"))
    assert "`dispatch` or `premerge-check` exits `1`" in text
    assert "explain each stopping finding with `explain-review-finding`" in text
    assert (
        "A headless run does not wait. It ends with the notice in its final summary"
        in text
    )


@pytest.mark.spec("FC-14-LN-01")
@pytest.mark.parametrize("skill", ("explain-review-finding", "run-step"))
def test_st_0398_skill_names_the_stop_notice_as_an_input(skill):
    assert "stop notice" in _flat(_text(SKILLS / skill / "SKILL.md"))


@pytest.mark.spec("FC-16-LN-01")
def test_st_0398_finding_format_holds_the_confirmation_step():
    section = _flat(_section(_text(FINDING_FORMAT), "Confirming a stop"))
    assert "Run each check under `## Possible damage`" in section
    assert "Write `stop_confirmed_by` and `stop_confirmed_reason`" in section
    assert "says what was checked and found" in section


@pytest.mark.spec("FC-18-LN-01")
def test_st_0398_finding_format_names_the_editor_and_bang_command():
    text = _flat(_text(FINDING_FORMAT))
    assert (
        "in an editor or with a `!` command, which runs outside the tool hooks" in text
    )


def test_st_0398_finding_format_holds_the_waiver():
    section = _flat(_section(_text(FINDING_FORMAT), "Waiving a finding"))
    assert "`status: waived` with `override_by` and `override_reason`" in section
