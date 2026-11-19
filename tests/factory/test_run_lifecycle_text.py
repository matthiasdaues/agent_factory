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
    links = [match.span() for match in SCOPE_LINT_LINK.finditer(text)]
    reads = []
    for match in REPO_PATH.finditer(text):
        # Only a match that starts inside the span of a scope-lint link is that
        # link; a later read in the same file still counts (IMPL-0020).
        in_link = any(start <= match.start() < end for start, end in links)
        is_link = in_link and not match["rest"] and not match["next"]
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
    # A read below the scope-lint link counts, although a link call comes first (IMPL-0020).
    below_the_link = (
        '(baseline / ".agent-factory").symlink_to(REPO_ROOT / ".agent-factory")\n'
        'installed = REPO_ROOT / ".agent-factory"'
    )
    assert installed_copy_reads(below_the_link) == ['REPO_ROOT / ".agent-factory"']


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
    FACTORY / "agents" / "implementation-agent.md",
    FACTORY / "skills" / "detect-test-regime" / "SKILL.md",
    FACTORY / "skills" / "crap-score" / "SKILL.md",
    FACTORY / "skills" / "mutation-testing" / "SKILL.md",
)
# The old gate keys of BR-055. A field key keeps its underscores, so
# gates.attempts_escalated and gates.mutation-testing.timeout_minutes do not count.
OLD_GATE_KEY = re.compile(r"\bgates\.(?:crap_score|mutation_testing|test_design_verify)\b")


@pytest.mark.spec("RL-09-LN-01")
@pytest.mark.parametrize(
    "path", GATE_KEY_TEXTS, ids=lambda p: p.parent.name if p.name == "SKILL.md" else p.stem
)
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


# --- RL-05: the gate-check step retries within the attempt limits (ST-0418) ---

IMPLEMENTATION_AGENT = FACTORY / "agents" / "implementation-agent.md"


def _gate_check_loop() -> str:
    return _section(IMPLEMENTATION_AGENT, "Gate-Check Loop")


@pytest.mark.spec("RL-05-LN-01")
def test_RL_05_LN_01_a_failing_gate_records_acceptance_unmet() -> None:
    """Scenario: A failing gate records the failure class acceptance_unmet."""
    loop = _section(IMPLEMENTATION_AGENT, "Fix-iteration loop")
    assert "When a gate fails, the attempt has failed." in loop
    assert "dispatch mark-failed <story-id> --class acceptance_unmet`" in loop
    assert "A failing gate always records the failure class `acceptance_unmet` (BR-114)." in loop


@pytest.mark.spec("RL-05-LN-02")
def test_RL_05_LN_02_each_retry_gets_a_fresh_developer_agent_with_the_gate_output() -> None:
    """Scenario: Each retry gets a fresh developer agent with the gate output."""
    loop = _section(IMPLEMENTATION_AGENT, "Fix-iteration loop")
    assert "Spawn a **fresh** developer agent for the retry" in loop
    assert (
        "The brief of the fresh developer agent holds the gate output: the report "
        "of each failing gate and the affected files"
    ) in loop
    template = _gate_check_loop().split("**Fix-iteration prompt template:**")[1]
    assert "**Gate reports:**" in template
    assert "This is attempt `<N>` on the tier `<tier>`." in template


@pytest.mark.spec("RL-05-LN-03")
def test_RL_05_LN_03_dispatch_counts_the_attempts_on_both_ways() -> None:
    """Scenario: With the defaults, a failing story gets three attempts on each tier and is then failed.
    Scenario: The same counts apply in a run by hand."""
    loop = _gate_check_loop()
    attempts = _section(IMPLEMENTATION_AGENT, "Attempts and escalation")
    assert "The implementation agent does not count attempts itself" in attempts
    assert "it runs `dispatch re-dispatch` and `dispatch escalate`" in attempts
    assert "A story gets `gates.attempts` counted attempts on its tier, the first attempt included." in attempts
    assert "the story gets `gates.attempts_escalated` counted attempts" in attempts
    assert "`gates.attempts_escalated: 0` turns escalation off" in attempts
    assert "then stays `failed`" in attempts
    assert "The same counts apply in an orchestrated run and in a run by hand." in attempts
    assert "dispatch re-dispatch <story-id>`" in loop
    assert "dispatch escalate <story-id>`" in loop
    assert "runs in an orchestrated run and in a run by hand" in loop
    for old in ("Maximum fix iterations per tier", "wave escalation slot", "**6** developer spawns",
                "applies to **automated mode only**"):
        assert old not in loop


# --- RL-02 and RL-03: the story workflow and the stops by hand (ST-0411) -----

DEVELOPER_AGENT = FACTORY / "agents" / "developer-agent.md"
GATE_SCRIPTS = ("crap-score", "mutation-testing", "test-design-verify", "dependency-check")


def _raw_block(path: Path, heading: str) -> str:
    """Return the raw text under *heading*, up to the next heading of level 1 to 3."""
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"^#+ {re.escape(heading)}\n(?P<body>.*?)(?=^#{{1,3}} |\Z)", text, re.M | re.S
    )
    assert match, f"{path.name} has no section {heading!r}"
    return match["body"]


def _block(path: Path, heading: str) -> str:
    """Return the folded text under *heading*, up to the next heading of level 1 to 3."""
    return " ".join(_raw_block(path, heading).split())


def _table_rows(path: Path, heading: str) -> list[list[str]]:
    """Return the cells of each body row of the tables under *heading*."""
    lines = [line for line in _raw_block(path, heading).splitlines() if line.startswith("|")]
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    return [
        cells for index, cells in enumerate(rows)
        if not set("".join(cells)) <= {"-", " "}
        and not (index + 1 < len(rows) and set("".join(rows[index + 1])) <= {"-", " "})
    ]


def _numbered_steps(path: Path, heading: str) -> list[str]:
    """Return the folded text of each numbered step under *heading*."""
    steps = re.split(r"^\d+\. ", _raw_block(path, heading), flags=re.M)[1:]
    return [" ".join(step.split()) for step in steps]


STORY_WORKFLOW_STEPS = ("**Implement.**", "**Review.**", "**Fix.**", "**Gate-check step.**", "**Merge.**")


@pytest.mark.spec("RL-02-LN-03")
def test_RL_02_LN_03_the_story_workflow_runs_its_five_steps_in_order() -> None:
    """Scenario: The story workflow runs its steps in order on the story branch."""
    assert "in an orchestrated run and in a run by hand" in _block(IMPLEMENTATION_AGENT, "Story workflow")
    steps = _numbered_steps(IMPLEMENTATION_AGENT, "Story workflow")
    assert len(steps) == len(STORY_WORKFLOW_STEPS)
    for step, title in zip(steps, STORY_WORKFLOW_STEPS):
        assert step.startswith(title), step
    implement, review, fix, gates, merge = steps
    assert "implements the story with TDD and commits" in implement
    assert "`docs/reviews/code-review-<story-id>-YYYY-MM-DD.md`" in review
    assert "also when the review files no finding" in review
    assert "[Gate-Check Loop](#gate-check-loop)" in gates
    assert "`dispatch merge-story <story-id>`" in merge
    assert "sets `status: done` in the merge commit" in merge
    for heading in ("Workflow — Automated Mode", "Workflow — Run By Hand"):
        assert "steps 2 and 3 of the [story workflow](#story-workflow)" in _block(IMPLEMENTATION_AGENT, heading)
    place = _block(DEVELOPER_AGENT, "Place in the story workflow")
    order = ["implement and commit", "review", "fix each open blocking finding",
             "gate-check step", "`dispatch merge-story`"]
    positions = [place.index(step) for step in order]
    assert positions == sorted(positions)
    assert "implementation-agent.md#story-workflow" in place


@pytest.mark.spec("RL-02-LN-01")
def test_RL_02_LN_01_a_repeat_review_follows_each_fix_of_a_blocking_finding() -> None:
    """Scenario: A repeat review follows each fix of a blocking finding."""
    fix = _numbered_steps(IMPLEMENTATION_AGENT, "Story workflow")[2]
    assert "A fresh developer agent fixes each open blocking finding of the story and commits." in fix
    assert "The code-review agent then reviews the story branch again." in fix
    assert "until no blocking finding with the story's ID is open" in fix
    assert "finding-classification.md#shared-severity-scale-and-blocking-rule" in fix


@pytest.mark.spec("RL-02-LN-02")
def test_RL_02_LN_02_the_developer_agent_runs_no_gate_and_sets_no_done() -> None:
    """Scenarios: The developer agent runs no gate script; Only dispatch merge-story
    sets a story to done."""
    text = _text(DEVELOPER_AGENT)
    assert "**Run the gates**" not in text
    for gate in GATE_SCRIPTS:
        assert f"scripts/{gate}" not in text, gate
    assert "You never run a gate script" in text
    commit = _numbered_steps(DEVELOPER_AGENT, "Workflow")[3]
    assert commit.startswith("**Commit**")
    assert "Do not set `status: done`; `dispatch merge-story` sets it in the merge commit (BR-118)." in commit
    assert "set `status: done`." not in text.replace("Do not set `status: done`", "")
    criteria = _block(DEVELOPER_AGENT, "Completion Criteria")
    assert "`status` unchanged" in criteria
    assert "every gate of the gate list has run" not in criteria
    loop = _gate_check_loop()
    assert "The developer agent runs no gate script." in loop
    assert "the developer agent runs the same gates" not in loop


STOPS = [
    ("Before a story starts", "`dispatch prepare-story <story-id>`"),
    ("Before a finding becomes a unit of work", "`dispatch add <finding-id>`"),
    ("Before a story merges", "`dispatch merge-story <story-id>`"),
    ("A story stops as `blocked`", "`dispatch re-dispatch <story-id>`"),
    (
        "A story stops as `failed` when its counted attempts are used up and `dispatch escalate` refuses it",
        "`dispatch re-dispatch <story-id>`",
    ),
    (
        "A story stops as `failed` after its second `contract_violation` attempt",
        "`dispatch re-dispatch <story-id>`",
    ),
    ("Before the merge into `dev`", "`premerge-check dev <feature-branch>`"),
]


@pytest.mark.spec("RL-03-LN-01")
@pytest.mark.parametrize(("point", "command"), STOPS, ids=[s[0][:30] for s in STOPS])
def test_RL_03_LN_01_the_agent_stops_before_each_decision_point(point: str, command: str) -> None:
    """Scenario Outline: The implementation agent stops and waits before a decision point."""
    rows = {cells[0]: cells[1] for cells in _table_rows(IMPLEMENTATION_AGENT, "Stops by hand")}
    assert point in rows
    assert command in rows[point]


@pytest.mark.spec("RL-03-LN-01")
def test_RL_03_LN_01_each_stop_shows_the_decision_and_waits_for_the_go() -> None:
    """Scenario: A failed attempt with a retry left is no decision point."""
    stops = _block(IMPLEMENTATION_AGENT, "Stops by hand")
    assert len(_table_rows(IMPLEMENTATION_AGENT, "Stops by hand")) == len(STOPS)
    assert (
        "show the story and the head of its branch, the findings of the story with "
        "their status, and the output of `premerge-check` where it applies"
    ) in stops
    assert "Then name the command you run after the go, and wait." in stops
    assert "Run no command of the stop before the User's go." in stops
    assert "`dispatch merge-story <story-id> --dry-run`" in stops
    assert (
        "A failed attempt with a retry left is no stop: run `dispatch re-dispatch` "
        "or `dispatch escalate` without the User (BR-116)."
    ) in stops
    assert "The wave close is no stop" in stops
    workflow = _block(IMPLEMENTATION_AGENT, "Workflow — Run By Hand")
    assert "[Stops by hand](#stops-by-hand)" in workflow
    order = [workflow.index(command) for command in (
        "dispatch init --mode by-hand", "dispatch prepare-story <story-id>",
        "dispatch mark-dispatching <story-id>", "dispatch mark-dispatched <story-id>",
        "dispatch merge-story <story-id>", "dispatch close-wave <wave>",
    )]
    assert order == sorted(order)
    assert "--no-stage --no-commit" not in workflow


@pytest.mark.spec("RL-03-LN-02")
def test_RL_03_LN_02_the_user_runs_only_three_commands() -> None:
    """Scenarios: The User runs only three commands in a run by hand; A run by hand
    needs no refresh of the story branch."""
    section = _block(IMPLEMENTATION_AGENT, "Who runs each dispatch command")
    rows = {cells[0]: cells[1:] for cells in _table_rows(IMPLEMENTATION_AGENT, "Who runs each dispatch command")}
    users = [name for name, cells in rows.items() if "The User." in cells]
    assert users == ["`return-story`, `close --drop`, `close`"]
    assert rows[users[0]] == ["The User.", "The User."]
    assert rows["`init`"] == ["The implementation agent.", "The implementation agent."]
    assert rows["`refresh-story`"] == ["The implementation agent.", "Not used."]
    for name, (orchestrated, by_hand) in rows.items():
        if name != users[0]:
            assert orchestrated == "The implementation agent.", name
            assert by_hand.startswith(("The implementation agent", "Not used.")), name
    assert "with `!` in Claude Code or in a terminal of their own" in section
    workflow = _block(IMPLEMENTATION_AGENT, "Workflow — Run By Hand")
    assert "refresh-story" not in workflow


# --- RL-08: a refused premerge-check returns to the gate-check step (ST-0416) ---


def _orchestrated_merge_step() -> str:
    workflow = _section(IMPLEMENTATION_AGENT, "Workflow — Automated Mode")
    return workflow.split("d. **Merge**")[1].split("e. **Failed/blocked stories**")[0]


@pytest.mark.spec("RL-08-LN-01")
def test_RL_08_LN_01_a_refused_premerge_check_returns_to_the_gate_check_step() -> None:
    """Scenario: A refused premerge-check sends a story in an orchestrated run
    back to the gate-check step."""
    merge = _orchestrated_merge_step()
    assert "When `premerge-check` refuses, `merge-story` exits `1`, merges nothing" in merge
    assert "Send the story back to the gate-check step" in merge
    assert "[fix-iteration loop](#fix-iteration-loop) on the story branch" in merge
    assert "gets the `premerge-check` output as its gate output" in merge


@pytest.mark.spec("RL-08-LN-01")
def test_RL_08_LN_01_a_dirty_feature_worktree_goes_to_the_user_unchanged() -> None:
    """Scenario: An uncommitted change in the worktree of the feature branch
    stops merge-story in an orchestrated run."""
    merge = _orchestrated_merge_step()
    assert "`merge-story` also refuses when the worktree of the feature branch holds" in merge
    assert "Report its message to the User unchanged" in merge
    assert "do not change that worktree" in merge
    assert "`dispatch.refuse_dirty_feature_worktree: false`" in merge


@pytest.mark.spec("RL-08-LN-01")
def test_RL_08_LN_01_step_4d_runs_again_after_the_user_has_acted() -> None:
    """IMPL-0038: after a refusal for an uncommitted change, and after a refused
    amend, the agent runs step 4d again once the User has acted."""
    merge = " ".join(_orchestrated_merge_step().split())
    dirty = merge.index("`dispatch.refuse_dirty_feature_worktree: false`")
    assert merge.index("After the User has acted, run step 4d again.") > dirty
    amend = merge.index("When a hook refuses the amend")
    assert "the story stays `dispatched`" in merge[amend:]
    assert "Report its message to the User, and run step 4d again after the User has fixed the cause." in merge[amend:]


@pytest.mark.spec("RL-08-LN-01")
def test_RL_08_LN_01_a_refused_merge_by_hand_waits_for_the_user() -> None:
    """IMPL-0035: by hand, a merge-story that exits 1 and keeps the story
    dispatched goes to the User unchanged, and the agent touches no file."""
    steps = _numbered_steps(IMPLEMENTATION_AGENT, "Workflow — Run By Hand")
    merge = next(step for step in steps if step.startswith("**Merge**"))
    assert (
        "When `merge-story` exits `1` and the story stays `dispatched`, show its "
        "message unchanged, change no file in the primary checkout, and wait for "
        "the User before the next `merge-story`." in merge
    )


# --- RL-11: the next wave starts only after the wave close (ST-0421) ----------


@pytest.mark.spec("RL-11-LN-01")
def test_RL_11_LN_01_the_drift_sessions_run_at_the_wave_close_without_a_stop() -> None:
    """Scenarios: The implementation agent runs the drift sessions and closes the
    wave; The wave close does not wait for the User's go."""
    steps = _numbered_steps(IMPLEMENTATION_AGENT, "Workflow — Automated Mode")
    close = next(step for step in steps if step.startswith("**Close the wave**"))
    marks = (
        "dispatch close-wave <wave-number>",
        "dispatches the owner of each `open` row",
        "dispatches the owner's reviewer for each `fixed` row",
        "run `close-wave` again until it passes",
        "The next wave starts only after the wave record exists",
    )
    found = _positions(close, marks)
    assert found == sorted(found), dict(zip(marks, found))
    assert "without a stop for the User" in close
    assert "never after a merge" in close
    merge_step = next(step for step in steps if step.startswith("**Verify, review"))
    assert "spec-feedback" not in merge_step

    by_hand = _numbered_steps(IMPLEMENTATION_AGENT, "Workflow — Run By Hand")
    by_hand_close = next(step for step in by_hand if step.startswith("**Close the wave**"))
    assert by_hand_close.index("dispatch close-wave") < by_hand_close.index("drift rows")
    assert "without a stop" in by_hand_close
    assert "The wave close is no stop" in _block(IMPLEMENTATION_AGENT, "Stops by hand")

    rule = _block(DISPATCH_CONTRACT, "Drift Rows At The Wave Close")
    marks = (
        "runs `dispatch close-wave <wave>`",
        "lists each such row with its owner",
        "dispatches the owner of each `open` row",
        "dispatches the owner's reviewer for each `fixed` row",
        "runs `close-wave` again",
    )
    found = _positions(rule, marks)
    assert found == sorted(found), dict(zip(marks, found))
    assert "It does not wait for the User's go" in rule
    assert "Drift Rows After A Merge" not in DISPATCH_CONTRACT.read_text(encoding="utf-8")


# --- RL-13: the feature checks and the merge into dev (ST-0424) ---------------

PLAYBOOKS = FACTORY / "playbooks"
FEATURE_PLAYBOOKS = (PLAYBOOKS / "feature-addition.md", PLAYBOOKS / "greenfield-development.md")
BRANCHING_POLICY = FACTORY / "rulebooks" / "conventions" / "branching-policy.md"
RULES = FACTORY / "rulebooks" / "rules.md"
BUG_HUNT = FACTORY / "skills" / "bug-hunt" / "SKILL.md"
FEATURE_CHECKS = "Feature checks and the merge into `dev`"


def _positions(text: str, marks: tuple[str, ...]) -> list[int]:
    found = [text.find(mark) for mark in marks]
    assert -1 not in found, dict(zip(marks, found))
    return found


@pytest.mark.spec("RL-13-LN-01")
@pytest.mark.parametrize("path", FEATURE_PLAYBOOKS, ids=lambda p: p.name)
def test_RL_13_LN_01_the_playbook_orders_review_qa_merge_reconciliation(path: Path) -> None:
    """Scenario: The feature checks run after the last wave closes."""
    text = _text(path)
    assert (
        "The feature checks start after the last wave closes: code review of the whole "
        "feature, then QA, then the merge into `dev`, then reconciliation on `dev`." in text
    )
    marks = (
        "activate code-review-agent",
        "`docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`",
        "activate qa-agent",
        "`docs/reviews/bug-hunt-*.md`",
        "premerge-check dev <feature-branch>",
        "activate reconciliation-agent",
    )
    positions = _positions(text, marks)
    assert positions == sorted(positions)


@pytest.mark.spec("RL-13-LN-01")
def test_RL_13_LN_01_the_agent_and_the_policy_order_the_feature_checks() -> None:
    """The implementation agent and the branching policy name the same order."""
    steps = _numbered_steps(IMPLEMENTATION_AGENT, FEATURE_CHECKS)
    assert [step.split(".**")[0] for step in steps] == [
        "**Code review of the whole feature", "**QA", "**Merge", "**Reconciliation",
    ]
    assert "`docs/reviews/code-review-<feature-branch>-YYYY-MM-DD.md`" in steps[0]
    assert "on `dev`" in steps[3]
    policy = _numbered_steps(BRANCHING_POLICY, "Merge Into Dev")
    assert "reviews the whole feature" in policy[0]
    assert "QA agent" in policy[1]
    assert "premerge-check dev <feature-branch>`" in policy[2]
    assert "on `dev`" in policy[3]
    handoff = _section(IMPLEMENTATION_AGENT, "Handoff")
    assert "Run reconciliation-agent, then QA" not in handoff
    assert "Reconciliation runs on `dev` after the merge" in handoff


RECONCILIATION_AGENT = FACTORY / "agents" / "reconciliation-agent.md"
DOCUMENTATION_UPDATE = PLAYBOOKS / "documentation-update.md"


@pytest.mark.spec("RL-13-LN-01")
def test_RL_13_LN_01_the_handoffs_order_review_qa_merge_reconciliation() -> None:
    """IMPL-0051: the handoffs of the code-review, QA and reconciliation agents
    follow code review, QA, merge, then reconciliation on `dev`."""
    review = _section(CODE_REVIEW_AGENT, "Handoff")
    assert "Run reconciliation" not in review
    assert "the QA Agent" in review
    qa = _section(QA_AGENT, "Handoff")
    assert "PR ready to merge" not in qa
    assert "premerge-check dev <feature-branch>" in qa
    reconciliation = _text(RECONCILIATION_AGENT)
    assert "pre-merge to dev" not in reconciliation
    assert "Run QA agent" not in reconciliation
    assert "on `dev` after the User merges the feature branch into `dev`" in reconciliation
    backfeed = _text(DOCUMENTATION_UPDATE)
    assert "before its merge into `dev`" not in backfeed
    assert "the owners of reconciliation rows commit on `dev`" in backfeed


@pytest.mark.spec("RL-13-LN-02")
def test_RL_13_LN_02_the_agent_shows_the_result_and_leaves_the_merge_to_the_user() -> None:
    """Scenario: The User merges after the implementation agent shows the result."""
    merge = _numbered_steps(IMPLEMENTATION_AGENT, FEATURE_CHECKS)[2]
    assert "Run `.agent-factory/factory/scripts/premerge-check dev <feature-branch>`" in merge
    assert "show its full output to the User" in merge
    assert "When it passes, the User merges the feature branch into `dev`" in merge
    assert "The implementation agent never merges into `dev`" in merge
    for step in ("7. **Repeat or finish**", "8. **Merge into `dev`**"):
        assert step in IMPLEMENTATION_AGENT.read_text(encoding="utf-8")
    assert _text(IMPLEMENTATION_AGENT).count("(#feature-checks-and-the-merge-into-dev)") == 2
    assert "No agent merges into `dev`" in _text(BRANCHING_POLICY)


@pytest.mark.spec("RL-13-LN-02")
def test_RL_13_LN_02_rules_run_premerge_check_on_both_ways() -> None:
    """IMPL-0034: the rule that runs premerge-check before git merge holds on both
    ways, and the worktree rule names the temporary worktree of premerge-check."""
    lines = RULES.read_text(encoding="utf-8").splitlines()
    premerge = [line for line in lines if "premerge-check <target> <branch>` before `git merge" in line]
    assert len(premerge) == 1
    assert "(automated only)" not in premerge[0]
    assert "This holds on both ways" in premerge[0]
    worktree = [line for line in lines if "git worktree add -b <branch> .current-work" in line]
    assert len(worktree) == 1
    assert "no worktrees are created" not in worktree[0]
    assert "A run by hand checks out each story branch in the primary checkout" in worktree[0]
    assert "Only `premerge-check` adds a worktree there" in worktree[0]


@pytest.mark.spec("RL-04-LN-04")
def test_RL_04_LN_04_the_bug_hunt_skill_writes_its_report() -> None:
    """BUG-0130: the bug-hunt skill names its report with `run` and `branch_head`,
    and the QA agent declares it as an output."""
    report = _section(BUG_HUNT, "Phase: Report")
    assert "save the report as `docs/reviews/bug-hunt-YYYY-MM-DD.md`" in report
    assert "sets `run` to the feature branch and `branch_head` to the full SHA" in report
    front = yaml.safe_load(QA_AGENT.read_text(encoding="utf-8").split("---")[1])
    patterns = [d["path_pattern"] for d in front["outputs"]["declarations"]]
    assert "docs/reviews/bug-hunt-*.md" in patterns
