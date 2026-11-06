"""Text tests for the counter-ids rules (ST-0373, counter-ids.feature)."""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script

RULES = REPO_ROOT / "packages/factory/rulebooks/rules.md"
BRANCHING_POLICY = REPO_ROOT / "packages/factory/rulebooks/conventions/branching-policy.md"
PLANNING_AGENT = REPO_ROOT / "packages/factory/agents/planning-agent.md"

# A sentence that tells the reader to commit indexed artifacts to dev, or to
# keep them off other branches.
DEV_ONLY = re.compile(
    r"(commit[^.\n]*(indexed artifacts|backlog stories)[^.\n]*to `dev`"
    r"|(indexed artifacts|backlog stories)[^.\n]*(are )?(always )?committed to `dev`"
    r"|never commit indexed artifacts to a feature"
    r"|`dev`[^.\n]*(single )?canonical index)",
    re.IGNORECASE,
)


def _branching_section(text: str) -> str:
    start = text.index("## Branching")
    following = re.search(r"^## ", text[start + 3 :], re.MULTILINE)
    return text[start : start + 3 + following.start()] if following else text[start:]


def _indexed_text(path) -> str:
    text = path.read_text()
    return _branching_section(text) if path == RULES else text


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", [RULES, BRANCHING_POLICY, PLANNING_AGENT], ids=lambda p: p.name)
def test_st_0373_file_allows_indexed_artifacts_on_any_branch(path):
    text = _indexed_text(path)
    assert re.search(r"indexed artifacts?[^.\n]*any branch", text, re.IGNORECASE)
    assert "next-id" in text


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", [RULES, BRANCHING_POLICY, PLANNING_AGENT], ids=lambda p: p.name)
def test_st_0373_file_requires_no_indexed_artifact_on_dev(path):
    assert DEV_ONLY.search(_indexed_text(path)) is None


@pytest.mark.spec("CID-08-LN-01")
def test_st_0373_branching_policy_drops_the_dev_only_heading():
    assert "Indexed Artifacts On Dev" not in BRANCHING_POLICY.read_text()


def _section(text: str, heading: str) -> str:
    start = text.index(f"## {heading}")
    following = re.search(r"^## ", text[start + 3 :], re.MULTILINE)
    return text[start : start + 3 + following.start()] if following else text[start:]


# A bullet that names the claim push by next-id as an exception to the
# human's pushes.
CLAIM_PUSH_EXCEPTION = re.compile(
    r"^- .*`next-id`[^\n]*\bpush[^\n]*\bexception\b|^- .*\bexception\b[^\n]*`next-id`[^\n]*\bpush",
    re.IGNORECASE | re.MULTILINE,
)


@pytest.mark.spec("CID-09-LN-01")
def test_st_0374_dispatch_states_claim_push_exception_for_manual_mode():
    section = _section(RULES.read_text(), "Dispatch")
    match = CLAIM_PUSH_EXCEPTION.search(section)
    assert match is not None
    assert "manual" in match.group(0).lower()


@pytest.mark.spec("CID-09-LN-01")
def test_st_0374_git_workflow_states_claim_push_exception_for_both_modes():
    section = _section(RULES.read_text(), "Git workflow")
    match = CLAIM_PUSH_EXCEPTION.search(section)
    assert match is not None
    line = match.group(0).lower()
    assert "manual" in line and "automated" in line


@pytest.mark.spec("CID-09-LN-01")
def test_st_0374_rules_never_say_an_outside_push_only_leaves_a_gap():
    text = RULES.read_text()
    assert not re.search(r"only leave a gap|only leaves a gap", text, re.IGNORECASE)


# ST-0372: the four producer files number a new artifact with next-id.
SKILLS = REPO_ROOT / "packages/factory/skills"
CREATE_BACKLOG = SKILLS / "create-backlog/SKILL.md"
FINDING_FORMAT = REPO_ROOT / "packages/factory/rulebooks/conventions/finding-format.md"
BUG_FIX = REPO_ROOT / "packages/factory/playbooks/bug-fix.md"
TODO_FORMAT = REPO_ROOT / "packages/factory/rulebooks/conventions/todo-format.md"
WRITE_ADR = SKILLS / "write-adr/SKILL.md"
SLICE_STORY = SKILLS / "create-backlog-slice-story/SKILL.md"

NEXT_ID_PATH = ".agent-factory/factory/scripts/next-id"

PRODUCERS = {
    CREATE_BACKLOG: ["ST"],
    BUG_FIX: ["BUG"],
    TODO_FORMAT: ["T"],
    WRITE_ADR: ["ADR"],
}

# A sentence that tells the reader to find the highest number by scanning.
SCAN_FOR_HIGHEST = re.compile(
    r"(scan(ning)?[^.\n]*(highest|existing|next)|(highest|next available)[^.\n]*scan"
    r"|increment the highest numeric)",
    re.IGNORECASE,
)


def _without_split_rule(path, text: str) -> str:
    # The create-backlog id rule keeps the letter scan for a split.
    if path == CREATE_BACKLOG:
        return re.sub(r"[^.\n]*split[^.\n]*letter[^.\n]*\.?", "", text, flags=re.IGNORECASE)
    return text


@pytest.mark.spec("CID-07-LN-01")
@pytest.mark.parametrize("path", list(PRODUCERS), ids=lambda p: p.parent.name + "/" + p.name)
def test_st_0372_producer_calls_next_id_with_its_prefixes(path):
    text = path.read_text()
    assert NEXT_ID_PATH in text
    for prefix in PRODUCERS[path]:
        assert re.search(rf"next-id[` ]+{prefix}\b|next-id <TAG>", text), prefix
    assert "standard output" in text
    assert re.search(r"stop[^.\n]*report|report[^.\n]*stop", text, re.IGNORECASE)
    assert re.search(r"never[^.\n]*(by hand|pick)", text, re.IGNORECASE)


@pytest.mark.spec("CID-07-LN-01")
@pytest.mark.parametrize("path", list(PRODUCERS), ids=lambda p: p.parent.name + "/" + p.name)
def test_st_0372_producer_has_no_scan_for_the_highest_number(path):
    text = _without_split_rule(path, path.read_text())
    assert SCAN_FOR_HIGHEST.search(text) is None


@pytest.mark.spec("CID-07-LN-02")
def test_st_0372_write_adr_numbers_with_next_id_adr_and_keeps_the_file_form():
    text = WRITE_ADR.read_text()
    assert "next-id ADR" in text
    assert "docs/adr/NNNN-short-title.md" in text


@pytest.mark.spec("CID-07-LN-03")
def test_st_0372_slice_story_keeps_the_letter_scan_and_runs_no_next_id():
    text = SLICE_STORY.read_text()
    assert re.search(r"scanning existing `backlog/ST-NNNN\*\.md`", text)
    assert "next-id" not in text


# IMPL-0005: next-id serves the prefixes of BR-068 only.
NEXT_ID_TEXT_FILES = [RULES, BRANCHING_POLICY, PLANNING_AGENT]


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", NEXT_ID_TEXT_FILES, ids=lambda p: p.name)
def test_impl_0005_no_file_says_next_id_hands_out_prop(path):
    text = path.read_text()
    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        if "next-id" in sentence:
            assert "PROP" not in sentence, sentence
    assert not re.search(r"\(`?[^)]*PROP-NN", text), "PROP-NN in an example list"


@pytest.mark.spec("CID-08-LN-01")
def test_impl_0005_rules_limit_the_claim_to_prefixes_next_id_serves():
    text = RULES.read_text()
    assert "every ID of a prefix that `next-id` serves" in text
    assert "claim every ID through `next-id`" not in text


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", NEXT_ID_TEXT_FILES, ids=lambda p: p.name)
def test_impl_0005_file_links_the_prefix_list_and_names_ids_outside_the_counter(path):
    text = path.read_text()
    assert "id-prefixes.md" in text or "finding-format.md" in text
    assert re.search(r"\bPROP\b[^.\n]*(own numbering|outside)", text)


# ST-0383: id-prefixes.md holds one row per prefix of next-id (BR-108).
ID_PREFIXES = REPO_ROOT / "packages/factory/rulebooks/conventions/id-prefixes.md"
FACTORY_ROOT = REPO_ROOT / "packages/factory"
NEXT_ID = SOURCE_SCRIPTS_DIR / "next-id"


def check_id_prefix_table(table_path, next_id_path, factory_root) -> list[str]:
    """Return one problem per drift between the table, next-id, and the producer files."""
    import importlib.util
    from importlib.machinery import SourceFileLoader

    loader = SourceFileLoader("next_id_under_check", str(next_id_path))
    spec = importlib.util.spec_from_loader("next_id_under_check", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    wanted = set(module.PREFIXES)

    rows: dict[str, tuple[str, str]] = {}
    problems: list[str] = []
    for line in table_path.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        match = re.fullmatch(r"`([A-Z]+)`", cells[0]) if len(cells) == 3 else None
        if match:
            rows[match.group(1)] = (cells[1], cells[2])
    for prefix in sorted(wanted - rows.keys()):
        problems.append(f"prefix {prefix} is in next-id and not in the table")
    for prefix in sorted(rows.keys() - wanted):
        problems.append(f"prefix {prefix} is in the table and not in next-id")
    for prefix, (artifact, producers) in rows.items():
        if not artifact:
            problems.append(f"prefix {prefix} has no artifact")
        files = re.findall(r"`([^`]+\.md)`", producers)
        if not files:
            problems.append(f"prefix {prefix} names no ID producer file")
        for name in files:
            if not (factory_root / name).is_file():
                problems.append(f"prefix {prefix} names {name}, which does not exist")
    return problems


@pytest.mark.spec("CIF-16-LN-01")
def test_st_0383_id_prefixes_holds_one_row_per_prefix_with_existing_producers():
    assert check_id_prefix_table(ID_PREFIXES, NEXT_ID, FACTORY_ROOT) == []
    assert len(load_script("next-id").PREFIXES) == 12
    text = ID_PREFIXES.read_text()
    recon = next(line for line in text.splitlines() if line.startswith("| `RECON`"))
    assert "skills/reconcile-spec/SKILL.md" in recon
    assert "agents/reconciliation-agent.md" in recon


@pytest.mark.spec("CIF-16-LN-02")
@pytest.mark.parametrize("path", [RULES, BRANCHING_POLICY, FINDING_FORMAT], ids=lambda p: p.name)
def test_st_0383_file_points_to_id_prefixes(path):
    assert re.search(r"\]\((conventions/|\./)?id-prefixes\.md", path.read_text())


@pytest.mark.spec("CIF-16-LN-03")
def test_st_0383_finding_format_table_keeps_one_review_per_tag_and_recon():
    text = FINDING_FORMAT.read_text()
    assert "next-id <TAG>" not in text
    rows = [
        [c.strip() for c in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if re.match(r"\| [^|]+ \| `[A-Z]+` +\|", line)
    ]
    tags = [r[1].strip("`") for r in rows]
    assert len(rows) == 9 and len(set(tags)) == 9
    recon = next(r for r in rows if r[1] == "`RECON`")
    assert "reconciliation" in recon[0].lower()


@pytest.mark.spec("CIF-17-CT-01")
def test_st_0383_checker_names_a_prefix_the_table_has_and_next_id_lacks(tmp_path):
    broken = tmp_path / "id-prefixes.md"
    broken.write_text(
        ID_PREFIXES.read_text() + "\n| `PROP` | Proposal row | `skills/write-adr/SKILL.md` |\n"
    )
    problems = check_id_prefix_table(broken, NEXT_ID, FACTORY_ROOT)
    assert any("PROP" in p for p in problems)


@pytest.mark.spec("CIF-17-CT-01")
def test_st_0383_checker_names_a_missing_prefix_and_a_missing_producer_file(tmp_path):
    lines = [
        line.replace("skills/write-adr/SKILL.md", "skills/no-such/SKILL.md")
        for line in ID_PREFIXES.read_text().splitlines()
        if not line.startswith("| `QA`")
    ]
    broken = tmp_path / "id-prefixes.md"
    broken.write_text("\n".join(lines))
    problems = check_id_prefix_table(broken, NEXT_ID, FACTORY_ROOT)
    assert any("QA" in p for p in problems)
    assert any("skills/no-such/SKILL.md" in p for p in problems)
