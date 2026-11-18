"""Text checks of the run lifecycle (docs/spec/features/run-lifecycle.feature).

These tests read files of this repository and check their text.
"""

from __future__ import annotations

import re
from dataclasses import fields
from pathlib import Path

import pytest
import yaml

from conftest import REPO_ROOT

TEST_ROOTS = (REPO_ROOT / "tests", REPO_ROOT / "packages" / "usage" / "tests")
LAYOUT_GATES = REPO_ROOT / "tests" / "factory" / "test_core_layout_gates.py"

# A path expression that starts at this repository's root and names
# .agent-factory, such as REPO_ROOT / ".agent-factory" / "factory".
REPO_PATH = re.compile(
    r"\b(?:REPO_ROOT|PROJECT_ROOT|ROOT)\s*/\s*"
    r"""["']\.agent-factory(?P<rest>[^"']*)["'](?P<next>\s*/\s*["'][^"']*["'])?"""
)
# The link of this repository's .agent-factory that scope-lint reads
# .agent-factory/workstreams through (OI-08).
SCOPE_LINT_LINK = re.compile(r"""symlink_to\(\s*REPO_ROOT\s*/\s*["']\.agent-factory["']\s*\)""")


def installed_copy_reads(text: str) -> list[str]:
    """Return each expression of text that reads this repository's installed copy."""
    links = {match.start() for match in SCOPE_LINT_LINK.finditer(text)}
    reads = []
    for match in REPO_PATH.finditer(text):
        link_start = text.rfind("symlink_to(", 0, match.start())
        is_link = link_start in links and not match["rest"] and not match["next"]
        if not is_link:
            reads.append(match.group(0))
    return reads


def _test_files() -> list[Path]:
    """Every test file but this one, whose samples name the forms the check finds."""
    return sorted(
        path
        for root in TEST_ROOTS
        if root.is_dir()
        for path in root.rglob("*.py")
        if path != Path(__file__).resolve()
    )


@pytest.mark.spec("RL-18-LN-01")
def test_RL_18_LN_01_no_test_reads_the_installed_copy_of_this_repository() -> None:
    """Scenario: The test suite of this repository reads no installed copy of its own."""
    files = _test_files()
    assert LAYOUT_GATES in files
    reads = {
        str(path.relative_to(REPO_ROOT)): found
        for path in files
        if (found := installed_copy_reads(path.read_text(encoding="utf-8")))
    }
    assert reads == {}


@pytest.mark.spec("RL-18-LN-01")
def test_RL_18_LN_01_a_read_of_the_installed_copy_counts() -> None:
    """The check finds each form of a path under this repository's .agent-factory/factory,
    and leaves a path under a temporary project alone."""
    assert installed_copy_reads('x = REPO_ROOT / ".agent-factory" / "factory"')
    assert installed_copy_reads("x = REPO_ROOT / '.agent-factory/factory/scripts'")
    assert installed_copy_reads('x = PROJECT_ROOT / ".agent-factory"')
    assert installed_copy_reads('p.symlink_to(REPO_ROOT / ".agent-factory" / "factory")')
    assert installed_copy_reads('x = tmp_path / ".agent-factory" / "factory"') == []
    assert installed_copy_reads('x = target / ".agent-factory/factory"') == []


@pytest.mark.spec("RL-18-LN-02")
def test_RL_18_LN_02_the_scope_lint_link_is_no_read_of_the_installed_copy() -> None:
    """Scenario: A link to this repository's .agent-factory for scope-lint is no read
    of the installed copy."""
    text = LAYOUT_GATES.read_text(encoding="utf-8")
    assert SCOPE_LINT_LINK.search(text), "the scope-lint link moved or changed its form"
    assert installed_copy_reads(text) == []
    line = '(baseline / ".agent-factory").symlink_to(REPO_ROOT / ".agent-factory")'
    assert installed_copy_reads(line) == []


# --- RL-04: reviews and findings name their story or run (ST-0412) ------------

FACTORY = REPO_ROOT / "packages" / "factory"
CODE_REVIEW_AGENT = FACTORY / "agents" / "code-review-agent.md"
QA_AGENT = FACTORY / "agents" / "qa-agent.md"
REPORT_FORMAT = FACTORY / "rulebooks" / "conventions" / "report-format.md"
FINDING_FORMAT = FACTORY / "rulebooks" / "conventions" / "finding-format.md"
FINDING_TEMPLATE = FACTORY / "rulebooks" / "templates" / "finding.md"


def _text(path: Path) -> str:
    """Return the text of *path* with its line breaks folded into spaces."""
    return " ".join(path.read_text(encoding="utf-8").split())


def _section(path: Path, heading: str) -> str:
    """Return the folded text of the section under *heading*, up to the next one."""
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^(#+) {re.escape(heading)}\n(?P<body>.*?)(?=^#{{1,2}} |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"{path.name} has no section {heading!r}"
    return " ".join(match["body"].split())


def _template_keys() -> list[str]:
    """Return the frontmatter keys of the YAML block in the finding template."""
    block = re.search(
        r"```markdown\n---\n(?P<body>.*?)\n---\n```",
        FINDING_TEMPLATE.read_text(encoding="utf-8"),
        re.DOTALL,
    )
    assert block, "the finding template has no frontmatter block"
    return re.findall(r"^([a-z_]+):", block["body"], re.MULTILINE)


@pytest.mark.spec("RL-04-LN-01")
def test_RL_04_LN_01_the_story_report_carries_the_story_id_and_a_day_number() -> None:
    """Scenarios: The review report carries the story ID in its name; A second
    review on the same day adds a number to the name."""
    agent = _text(CODE_REVIEW_AGENT)
    assert "docs/reviews/code-review-<story-id>-YYYY-MM-DD.md" in agent
    assert "docs/reviews/code-review-YYYY-MM-DD.md" not in agent
    assert "add `-2` to the name, and `-3` for a third review that day" in agent
    assert "You add the number yourself; no script does." in agent
    assert "sets `story` to the story ID and `branch_head` to the head of the story branch" in agent
    story_and_run = _section(REPORT_FORMAT, "Story and run")
    assert "`docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`" in story_and_run
    assert "`code-review-ST-0350-2026-11-24-2.md`" in story_and_run
    assert "a third adds `-3`" in story_and_run
    frontmatter = _section(REPORT_FORMAT, "Report frontmatter")
    assert "story:" in frontmatter and "branch_head:" in frontmatter


@pytest.mark.spec("RL-04-LN-02")
def test_RL_04_LN_02_a_finding_names_its_story_or_its_run() -> None:
    """Scenarios: A story finding names its story; A feature-level finding names
    its run; A finding from a review outside any run names neither."""
    keys = _template_keys()
    assert {"story", "run"} <= set(keys)
    assert keys.index("story") < keys.index("run") < keys.index("traces")
    fields = _section(FINDING_FORMAT, "Format")
    assert "`owner`, `story`, `run`, and `traces`" in fields
    rule = _section(FINDING_FORMAT, "Story and run")
    for row in (
        "| The review of a story, such as the code review | the story ID: `ST-0350` | empty |",
        "| empty | the feature branch: `feature/login` |",
        "| A review outside any run | empty | empty |",
    ):
        assert row in rule
    assert "`finding-lint` refuses a finding file that sets both" in rule
    template = _text(FINDING_TEMPLATE)
    assert "A finding of a review outside any run leaves both empty." in template
    for agent in (CODE_REVIEW_AGENT, QA_AGENT):
        text = _text(agent)
        assert "finding-format.md#story-and-run" in text, agent.name
        assert "leaves both empty" in text, agent.name
    review = _text(CODE_REVIEW_AGENT)
    assert "A finding of a story's review sets `story` to the story ID and leaves `run` empty." in review
    qa = _text(QA_AGENT)
    assert "Each finding it files leaves `story` empty and sets `run` to the feature branch." in qa


@pytest.mark.spec("RL-04-LN-03")
def test_RL_04_LN_03_a_review_without_findings_still_commits_its_report() -> None:
    """Scenario: A review without findings still commits its report."""
    sentence = "The developer agent commits the report of a story's review on the story branch, also when the review {} no finding."
    assert sentence.format("files") in _text(CODE_REVIEW_AGENT)
    assert sentence.format("filed") in _section(REPORT_FORMAT, "Story and run")


@pytest.mark.spec("RL-04-LN-04")
@pytest.mark.parametrize(
    ("agent", "report"),
    [
        (CODE_REVIEW_AGENT, "code-review report"),
        (QA_AGENT, "Fagan report"),
        (QA_AGENT, "security report"),
        (QA_AGENT, "bug-hunt report"),
    ],
    ids=["code-review", "fagan", "security", "bug-hunt"],
)
def test_RL_04_LN_04_a_feature_level_report_names_its_run(agent: Path, report: str) -> None:
    """Scenario Outline: A feature-level report names its run."""
    text = _text(agent)
    run = "sets `run` to the feature branch and `branch_head` to the head of the feature branch"
    assert run in text, agent.name
    if agent == QA_AGENT:
        assert f"the {report}" in text
    else:
        assert "`docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md` with the slash of the branch name replaced by a hyphen" in text
    table = _section(REPORT_FORMAT, "Story and run")
    for row in (
        "| Code review of the whole feature | `docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`, with the slash of the branch name replaced by a hyphen | empty | feature branch | head of the feature branch reviewed |",
        "| Fagan, security, and bug-hunt reports of QA | the name the skill gives | empty | feature branch | head of the feature branch reviewed |",
    ):
        assert row in table
    assert "run:" in _section(REPORT_FORMAT, "Report frontmatter")


# --- RL-17: the dispatch contract lists the fields of the ledger (ST-0408) ----

DISPATCH_CONTRACT = FACTORY / "rulebooks" / "conventions" / "dispatch-contract.md"


def _contract_ledger_blocks() -> list[dict]:
    """Return the YAML blocks of the sections Dispatch Ledger and Wave Closeout Record."""
    text = DISPATCH_CONTRACT.read_text(encoding="utf-8")
    start = text.index("### Dispatch Ledger")
    end = text.index("\n## Close\n", start)
    return [
        yaml.safe_load(block)
        for block in re.findall(r"```yaml\n(.*?)```", text[start:end], re.DOTALL)
    ]


def _story_keys(ledger: dict) -> set[str]:
    return {key for entry in ledger["stories"].values() for key in entry}


@pytest.mark.spec("RL-17-LN-01")
def test_RL_17_LN_01_the_dispatch_contract_lists_exactly_the_written_fields(tmp_path) -> None:
    """Scenario: The dispatch contract lists exactly the fields the code writes."""
    import dispatch_lib as lib
    from test_run_lifecycle_ledger import full_ledger, written

    code = written(full_ledger(), tmp_path / "dispatch-ledger.yaml")
    # The sample ledger sets every field, so the check sees each written name.
    assert _story_keys(code) == {f.name for f in fields(lib.StoryEntry)}
    schema, closeout = _contract_ledger_blocks()

    assert set(schema) == set(code)
    assert _story_keys(schema) == _story_keys(code)
    assert set(closeout["waves"][0]) == set(code["waves"][0])


# --- ST-0415: the test-strategy agent writes gate keys with hyphens --------

FACTORY = REPO_ROOT / "packages" / "factory"
GATE_KEY_TEXTS = (
    FACTORY / "agents" / "test-strategy-agent.md",
    FACTORY / "skills" / "detect-test-regime" / "SKILL.md",
    FACTORY / "skills" / "crap-score" / "SKILL.md",
    FACTORY / "skills" / "mutation-testing" / "SKILL.md",
)
# The old gate keys of BR-055. A field key keeps its underscores, so
# gates.attempts_escalated and gates.mutation-testing.timeout_minutes do not count.
OLD_GATE_KEY = re.compile(r"\bgates\.(?:crap_score|mutation_testing|test_design_verify)\b")


@pytest.mark.spec("RL-09-LN-01")
@pytest.mark.parametrize("path", GATE_KEY_TEXTS, ids=lambda p: p.parent.name)
def test_RL_09_LN_01_the_gate_texts_name_only_keys_with_hyphens(path: Path) -> None:
    """Scenario: The test-strategy agent writes gate keys with hyphens."""
    assert OLD_GATE_KEY.findall(path.read_text(encoding="utf-8")) == []


@pytest.mark.spec("RL-09-LN-01")
def test_RL_09_LN_01_the_test_strategy_agent_names_the_key_with_hyphens() -> None:
    text = GATE_KEY_TEXTS[0].read_text(encoding="utf-8")
    assert "`gates.crap-score.threshold`" in text


@pytest.mark.spec("RL-09-LN-01")
def test_RL_09_LN_01_the_check_finds_an_old_gate_key() -> None:
    assert OLD_GATE_KEY.findall("set gates.crap_score.threshold") == ["gates.crap_score"]
    assert OLD_GATE_KEY.findall("set gates.mutation-testing.timeout_minutes") == []
    assert OLD_GATE_KEY.findall("gates.attempts_escalated") == []
    assert OLD_GATE_KEY.findall("gates.test_design_verify") == ["gates.test_design_verify"]
