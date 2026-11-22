"""Text checks of the CRAP gate setup (docs/spec/features/crap-gate-setup.feature).

These tests read files of this repository and check their text.
"""

from __future__ import annotations

import re
import subprocess
import sys

import pytest
import yaml

from conftest import REPO_ROOT

TEMPLATE = REPO_ROOT / "packages" / "factory" / "rulebooks" / "templates" / "charter-testing.yaml"
VALIDATION_RULES = REPO_ROOT / "docs" / "spec" / "validation-rules.md"


def _rule_text(rule: str) -> str:
    """Return the bullet of *rule* in docs/spec/validation-rules.md."""
    match = re.search(
        rf"^- \*\*{re.escape(rule)}\*\*:(.*)$", VALIDATION_RULES.read_text(), re.MULTILINE
    )
    assert match, f"{rule} is missing from {VALIDATION_RULES}"
    return match.group(1)


@pytest.mark.spec("CG-11-LN-02")
def test_cg_11_the_charter_template_has_a_mutation_entry_and_no_crap_entry() -> None:
    """Scenario: Template includes gates section without a CRAP gate."""
    gates = yaml.safe_load(TEMPLATE.read_text())["gates"]
    assert isinstance(gates, dict)
    assert "mutation_testing" in gates
    assert "crap_score" not in gates
    assert "crap-score" not in gates


@pytest.mark.spec("CG-12-LN-05")
@pytest.mark.parametrize(
    ("rule", "statements"),
    [
        # premerge-check runs no gate by default
        ("BR-066", ["No default picks a gate.", "`premerge-check` runs none"]),
        # crap-score reads the report of the measuring command
        ("BR-027", ["`crap-score` reads the rows that the project's measuring commands write"]),
        # only the stakeholder writes docs/findings/exceptions.md
        (
            "BR-092",
            ["Only the stakeholder writes the exceptions register `docs/findings/exceptions.md`"],
        ),
        # a gate that cannot measure is a fourth cause of blocked
        (
            "BR-116",
            [
                "stops as `blocked` when a gate cannot measure",
                "`crap-score` exits `2` in the gate-check step",
                "`premerge-check` exits `3` at the merge",
            ],
        ),
        # merge-story turns exit 3 of premerge-check into blocked
        ("BR-124", ["When `premerge-check` exits `3`", "it sets the entry `blocked`"]),
    ],
)
def test_cg_12_the_business_rules_state_the_gates_behaviour(rule, statements) -> None:
    """Scenario Outline: The business rules state the gate's behaviour."""
    text = _rule_text(rule)
    for statement in statements:
        assert statement in text, f"{rule} does not state: {statement}"


SETUP_SKILL_DIR = REPO_ROOT / "packages" / "factory" / "skills" / "setup-crap-score"
PYTHON_TEMPLATE = SETUP_SKILL_DIR / "crap-measure-python"


@pytest.mark.spec("CG-03-LN-01")
def test_cg_03_the_python_template_holds_the_tool_code_and_names_its_duty() -> None:
    """Scenario: The Python measuring command starts from the Factory template."""
    text = PYTHON_TEMPLATE.read_text()
    header = re.search(r"^# /// script\n(.*?)^# ///$", text, re.MULTILINE | re.DOTALL)
    assert header, "the template has no `uv run --script` header"
    assert text.startswith("#!/usr/bin/env -S uv run --script\n")
    assert '"radon' in header.group(1)
    assert '"coverage' in header.group(1)
    assert "from radon.complexity import cc_visit" in text
    assert re.search(r"^import coverage$", text, re.MULTILINE)
    assert re.search(r"^TEST_COMMAND: list\[str\] = \[\]$", text, re.MULTILINE)
    docstring = " ".join(text.split('"""')[1].split())
    assert "it exits non-zero, names the cause, and writes no rows" in docstring
    assert "never reports such a file as 0 % covered" in docstring


@pytest.mark.spec("CG-03-LN-02")
def test_cg_03_no_file_of_the_setup_skill_names_the_factory_folder() -> None:
    """Scenario: The project's commands refer to nothing under .agent-factory/.

    SKILL.md stays in the Factory, so only the files that the skill copies count."""
    files = sorted(
        p for p in SETUP_SKILL_DIR.rglob("*") if p.is_file() and p.name != "SKILL.md"
    )
    assert PYTHON_TEMPLATE in files
    for path in files:
        assert ".agent-factory/" not in path.read_text(), f"{path} names .agent-factory/"


CRAP_SCORE = REPO_ROOT / "packages" / "factory" / "scripts" / "crap-score"
CRAP_SKILL = REPO_ROOT / "packages" / "factory" / "skills" / "crap-score" / "SKILL.md"
ADR_0003 = REPO_ROOT / "docs" / "adr" / "0003-test-execution-via-hooks.md"
ARC42_5 = REPO_ROOT / "docs" / "arc42" / "05_building_block_view.md"
# A file ending of a language, such as `.py` or `*.ts`; `.json` is no language.
LANGUAGE_ENDING = re.compile(r"\.(?:py|pyi|ts|tsx|js|jsx|mjs|go|rs|java|kt|rb|php|cs|c|cpp|h)\b")
TOOLS = ("radon", "lizard", "coverage.py", "ESLint", "Vitest", "Jest")


@pytest.mark.spec("CG-03-LN-03")
def test_cg_03_crap_score_holds_no_language_specific_code() -> None:
    """Scenario: crap-score holds no language-specific code."""
    text = CRAP_SCORE.read_text()
    assert not re.search(r"^\s*(?:import|from)\s+(?:radon|coverage)\b", text, re.MULTILINE)
    assert "radon" not in text
    assert LANGUAGE_ENDING.findall(text) == []


@pytest.mark.spec("CG-03-LN-03")
def test_cg_03_the_check_finds_a_language_ending() -> None:
    assert LANGUAGE_ENDING.findall('rglob("*.py") and main.ts') == [".py", ".ts"]
    assert LANGUAGE_ENDING.findall("report.json") == []


@pytest.mark.spec("CG-12-LN-01")
def test_cg_12_the_crap_score_skill_describes_the_gate_without_a_tool_or_threshold() -> None:
    """Scenario: The skill crap-score describes the gate and names no tool and no threshold."""
    text = CRAP_SKILL.read_text()
    flat = " ".join(text.split())
    for content in (
        "GATE_OUTPUT",
        "`start_line`",
        "`end_line`",
        "`coverage_pct`",
        "`parse_error`",
        "complexity² × (1 − coverage_pct/100)³ + complexity",
        "half up",
        "docs/findings/exceptions.md",
        "`gates.crap-score.threshold`",
    ):
        assert content in flat, f"crap-score/SKILL.md does not describe {content}"
    for code in ("`0`", "`1`", "`2`"):
        assert code in flat
    for folder in ("worktree of the story", "primary checkout", "premerge-check", "gate-setup-proof"):
        assert folder in flat, f"crap-score/SKILL.md does not name the folder of {folder}"
    for tool in TOOLS:
        assert tool.lower() not in text.lower(), f"crap-score/SKILL.md names {tool}"
    assert not re.search(r"default threshold|threshold[^.\n]*default", text, re.IGNORECASE)


@pytest.mark.spec("CG-12-LN-04")
def test_cg_12_the_architecture_names_exit_code_2_of_crap_score() -> None:
    """Scenario: The architecture names exit code 2 of crap-score."""
    adr = " ".join(ADR_0003.read_text().split())
    assert "Decision 5 of the amendment of 2026-08-28 gains one exception: the CRAP gate `crap-score`." in adr
    assert "It exits `2` when it cannot measure" in adr
    rows = [line for line in ARC42_5.read_text().splitlines() if line.startswith("| **crap-score**")]
    assert any("2 (cannot measure)" in row for row in rows)


IMPLEMENTATION_AGENT = REPO_ROOT / "packages" / "factory" / "agents" / "implementation-agent.md"
STORY_TEMPLATE = REPO_ROOT / "packages" / "factory" / "rulebooks" / "templates" / "story.md"
DEFAULT_OF_CRAP_SCORE = re.compile(
    r"default[^.\n]*crap-score[^.\n]*alone|crap-score` alone|crap-score alone", re.IGNORECASE
)


def _section(text: str, heading: str) -> str:
    """Return the body of the Markdown section *heading* up to the next heading of its level."""
    match = re.search(rf"^(#+) {re.escape(heading)}\s*$", text, re.MULTILINE)
    assert match, f"{heading} is missing"
    level = len(match.group(1))
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


@pytest.mark.spec("CG-11-LN-01")
def test_cg_11_the_gate_check_step_refuses_crap_score_without_an_entry() -> None:
    """Scenario Outline: A story that names crap-score before the setup is refused,
    row the gate-check step."""
    step = _section(IMPLEMENTATION_AGENT.read_text(), "Gate-Check Step")
    paragraphs = [p for p in step.split("\n\n") if "setup-crap-score" in p]
    assert paragraphs, "the gate-check step does not name setup-crap-score"
    assert any(
        "refuse the story" in p
        and "`gates.crap-score`" in p
        and "`crap_score`" in p
        and "BR-055" in p
        for p in paragraphs
    ), paragraphs


@pytest.mark.spec("CG-11-LN-01")
@pytest.mark.parametrize("path", [IMPLEMENTATION_AGENT, STORY_TEMPLATE], ids=["agent", "template"])
def test_cg_11_no_file_names_a_default_that_runs_crap_score_alone(path) -> None:
    """Scenario: The story template and the implementation agent name no default gate."""
    assert not DEFAULT_OF_CRAP_SCORE.search(path.read_text()), path


@pytest.mark.spec("CG-04-LN-01")
def test_cg_04_the_gate_check_step_runs_crap_score_as_a_background_job() -> None:
    """Scenario: The implementation agent runs crap-score as a background job, and
    Scenario Outline: The gate-check step runs crap-score in the folder of the story."""
    step = _section(IMPLEMENTATION_AGENT.read_text(), "Gate-Check Step")
    calls = [line for line in step.splitlines() if "scripts/crap-score " in line]
    assert len(calls) == 1, calls
    assert "--base <feature-branch>" in calls[0]
    assert "--report-dir" in calls[0]
    assert ".current-work/crap-score" in calls[0]
    assert "--threshold" not in calls[0]
    paragraphs = [p for p in step.split("\n\n") if "`crap-score`" in p and "background job" in p]
    assert any(
        "exit code" in p and "only" in p and "BR-134" in p for p in paragraphs
    ), paragraphs
    assert "hardcoded default" not in step


@pytest.mark.spec("CG-07-LN-01")
def test_cg_07_the_gate_check_step_blocks_a_story_when_crap_score_exits_two() -> None:
    """Scenario Outline: Exit 2 in the gate-check step blocks the story."""
    section = _section(IMPLEMENTATION_AGENT.read_text(), "Gate that cannot measure")
    flat = " ".join(section.split())
    assert (
        'dispatch mark-blocked <story-id> --reason "gate cannot measure: crap-score"' in section
    ), section
    assert "exits `2`" in flat
    assert "BR-134" in flat
    assert "spawn no developer agent" in flat
    assert "no attempt" in flat
    assert "Do not run `mark-failed`" in flat
    assert "gate `crap-score`" in flat
    assert "quote the message that `crap-score` printed" in flat
    assert "Quote it unchanged" in flat
    assert "keeps its attempts" in flat
    assert "branch" in flat


def _flat_section(heading: str) -> str:
    return " ".join(_section(IMPLEMENTATION_AGENT.read_text(), heading).split())


@pytest.mark.spec("CG-09-LN-01")
def test_cg_09_the_agent_runs_resume_gates_and_then_the_gate_check_step() -> None:
    """Scenario: resume-gates returns the story to the gate-check step, and
    Scenario: re-dispatch stays the way back for a story whose code must change."""
    flat = _flat_section("Gate that cannot measure")
    resume = "run `.agent-factory/factory/scripts/dispatch resume-gates <story-id>`, then the gate-check step again"
    assert resume in flat
    assert "so spawn no developer agent (BR-135, DEC-07)" in flat
    assert "the code must change" in flat
    assert "`.agent-factory/factory/scripts/dispatch re-dispatch <story-id>` instead" in flat


@pytest.mark.spec("CG-04-LN-02")
def test_cg_04_a_crap_score_stopped_by_a_signal_gives_no_verdict() -> None:
    """Scenario Outline: A run stopped by a signal stops its command first and gives no verdict."""
    flat = _flat_section("Gate that cannot measure")
    paragraphs = [p for p in flat.split("A `crap-score` that exits 128")[1:]]
    assert paragraphs, "the step names no exit of 128 plus a signal number"
    text = paragraphs[0]
    assert text.startswith(" plus a signal number")
    assert "gives no verdict" in text
    assert "Record no attempt" in text
    assert "Run `crap-score` again in the gate-check step (DEC-56)" in text


@pytest.mark.spec("CG-11-LN-03")
def test_cg_11_the_refusal_before_any_gate_records_no_attempt() -> None:
    """Scenario Outline: A story that names crap-score before the setup is refused, row the gate-check step."""
    step = _section(IMPLEMENTATION_AGENT.read_text(), "Gate-Check Step")
    paragraphs = [" ".join(p.split()) for p in step.split("\n\n") if "setup-crap-score" in p]
    assert any(
        "Record no attempt and do not run `mark-failed` (DEC-58)" in p for p in paragraphs
    ), paragraphs


@pytest.mark.spec("CG-08-LN-01")
def test_cg_08_step_4d_sends_a_story_blocked_after_exit_3_to_resume_gates() -> None:
    """Scenario Outline: A gate that cannot measure at the merge blocks the story on both ways."""
    lines = [line for line in IMPLEMENTATION_AGENT.read_text().splitlines()
             if line.lstrip().startswith("d. **Merge**")]
    assert len(lines) == 1, lines
    step = lines[0]
    sign = "holds the line `GATE CANNOT MEASURE: crap-score`, `premerge-check` exited `3`"
    exit_3 = step.split(sign, 1)
    assert len(exit_3) == 2, "step 4d names no exit 3 of premerge-check"
    text = exit_3[1].split("(BR-124, BR-136)", 1)[0]
    # IMPL-0085: the exit-3 case comes before the rule that leads to the fix-iteration loop.
    assert step.index(sign) < step.index("When `premerge-check` refuses, `merge-story` exits `1`")
    assert step.index(sign) < step.index("[fix-iteration loop](#fix-iteration-loop)")
    assert "`blocked` with the reason `gate cannot measure: crap-score`" in text
    assert "Never send that story to the fix-iteration loop" in text
    assert "dispatch resume-gates <story-id>" in text
    assert "fixed the setup" in text


SETUP_SKILL = SETUP_SKILL_DIR / "SKILL.md"
TEST_STRATEGY_AGENT = REPO_ROOT / "packages" / "factory" / "agents" / "test-strategy-agent.md"
PRE_COMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"
INDEX = REPO_ROOT / "packages" / "factory" / "INDEX.yaml"
INDEX_LINT = REPO_ROOT / "packages" / "factory" / "scripts" / "index-lint"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _step(number: int) -> str:
    """Return the flat body of `## Step <number>` of setup-crap-score/SKILL.md."""
    text = SETUP_SKILL.read_text()
    match = re.search(rf"^## Step {number} — .*$", text, re.MULTILINE)
    assert match, f"setup-crap-score/SKILL.md has no step {number}"
    rest = text[match.end():]
    end = re.search(r"^## ", rest, re.MULTILINE)
    return _flat(rest[: end.start()] if end else rest)


@pytest.mark.spec("CG-01-LN-01")
def test_cg_01_the_setup_reads_the_project_tries_each_tool_and_gives_each_exclusion_a_reason() -> None:
    """Scenarios: The agent reads the languages and the suites from docs/testing.yaml;
    The agent tries a candidate tool on a real file before it proposes the tool;
    A language outside the candidate table gets tools the agent looked up and tried;
    The agent proposes each exclusion with a reason."""
    step_1 = _step(1)
    assert "`docs/testing.yaml`" in step_1
    for item in ("languages", "test commands", "suites"):
        assert item in step_1, f"step 1 does not read the {item}"
    assert "one measure per language" in step_1
    step_2 = _step(2)
    assert "on a real file of the project before" in step_2
    assert "outside the candidate table" in step_2
    assert "looks up" in step_2 and "tries each" in step_2
    step_3 = _step(3)
    assert "each with a reason" in step_3
    assert '"**/db/alembic/versions/**"' in step_3


@pytest.mark.spec("CG-01-LN-02")
def test_cg_01_the_candidate_table_names_the_tools_of_br_139() -> None:
    """Scenario: The agent tries a candidate tool on a real file before it proposes the tool."""
    rows = [_flat(line) for line in SETUP_SKILL.read_text().splitlines() if line.startswith("|")]
    assert "| Python | `radon`, `lizard` | coverage.py |" in rows, rows
    assert (
        "| TypeScript/JavaScript | ESLint `complexity`, `lizard` | Vitest or Jest with v8; "
        "`node --test --experimental-test-coverage` |" in rows
    ), rows


@pytest.mark.spec("CG-01-LN-03")
def test_cg_01_the_user_confirms_each_write_and_the_gate_starts_last() -> None:
    """Scenarios: The User enables the gate after the proof passes; The agent writes
    docs/testing.yaml only after the User confirms; The agent measures the whole project and
    reports the failures and the run time; Step 6 keeps the measured run time next to the time
    limit; A threshold changed in step 6 runs the proof again before the gate is enabled;
    A failed proof leaves the gate disabled."""
    step_4 = _step(4)
    assert "shows the change" in step_4
    assert "only after the User confirms" in step_4
    assert "`enabled: false`" in step_4
    assert "`TEST_COMMAND`" in step_4
    step_5 = _step(5)
    assert (
        ".agent-factory/factory/scripts/gate-setup-proof --measure <name> "
        "--plant .current-work/gate-setup-proof/plant/<name>/" in step_5
    )
    assert "A failed proof keeps `enabled: false`" in step_5
    step_6 = _step(6)
    assert ".agent-factory/factory/scripts/crap-score --all" in step_6
    assert "Exit `1` is the normal result of this step" in step_6
    assert "writes no report" in step_6
    assert "propose a higher `timeout_minutes`" in step_6
    assert "number of functions that would fail" in step_6
    assert "run time" in step_6
    assert "`measured_minutes` next to `timeout_minutes`" in step_6
    step_7 = _step(7)
    assert "runs `gate-setup-proof` again" in step_7
    assert "`enabled: true` only after the proof passes with the final threshold and the User confirms" in step_7


@pytest.mark.spec("CG-01-LN-04")
def test_cg_01_the_setup_writes_no_exception_and_no_commit_hook() -> None:
    """Scenario: The setup writes no exception and no commit hook."""
    text = _flat(SETUP_SKILL.read_text())
    assert "writes no row of the exceptions register" in text
    assert "writes no commit hook" in text
    config = yaml.safe_load(PRE_COMMIT_CONFIG.read_text())
    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            assert "crap-score" not in str(hook.get("id", "")), hook
            assert "crap-score" not in str(hook.get("entry", "")), hook


@pytest.mark.spec("CG-01-LN-05")
def test_cg_01_the_setup_commits_once_after_step_7() -> None:
    """Scenario: The setup commits once, after the User confirms the start of the gate."""
    for number in range(1, 7):
        assert "git commit" not in _step(number), f"step {number} commits"
    step_7 = _step(7)
    assert "one commit" in step_7
    assert "git commit" in step_7
    for item in ("`docs/testing.yaml`", "measuring commands", "`ready` commands"):
        assert item in step_7, f"the commit of step 7 does not hold the {item}"
    assert "No earlier step commits" in _flat(SETUP_SKILL.read_text())


@pytest.mark.spec("CG-02-LN-01")
def test_cg_02_the_planted_functions_are_decided_by_coverage_alone() -> None:
    """Scenario: The planted functions are decided by coverage alone."""
    step_5 = _step(5)
    for content in (
        "`base/`",
        "`gap/`",
        "layout of the project",
        "`proof_untested`",
        "`proof_tested`",
        "the same complexity, at or below the threshold",
        "above the threshold at 0 % coverage",
        "complexity 3",
        "scores 12",
        "threshold 8",
    ):
        assert content in step_5, f"step 5 does not name {content}"


@pytest.mark.spec("CG-12-LN-02")
def test_cg_12_the_generated_index_lists_the_setup_skill() -> None:
    """Scenario: The setup skill is in the generated index."""
    skills = yaml.safe_load(INDEX.read_text())["skills"]
    names = [entry["name"] for entry in skills]
    assert "setup-crap-score" in names
    result = subprocess.run(
        [sys.executable, str(INDEX_LINT), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.spec("CG-12-LN-03")
def test_cg_12_the_test_strategy_agent_runs_the_setup_and_no_gate_on_a_story() -> None:
    """Scenario: The test-strategy agent runs the setup and no gate on a story."""
    text = TEST_STRATEGY_AGENT.read_text()
    flat = _flat(text)
    assert "setup-crap-score" in yaml.safe_load(text.split("---")[1])["skills"]
    assert "Invoke `setup-crap-score`" in flat
    assert "runs `gate-setup-proof` and `crap-score --all` during the setup" in flat
    assert "runs no gate on a story" in flat
    assert "The diff leaves out the entry `gates.crap-score`" in flat
    completion = _flat(_section(text, "Completion Criteria"))
    assert "gate ran" not in completion
