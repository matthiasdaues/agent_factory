"""Text tests for the fitting rules of the counter (ST-0377, counter-ids-fitting.feature)."""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT

VIRGIL = REPO_ROOT / "packages/factory/agents/virgil.md"
CONFIG = REPO_ROOT / "packages/factory/config"
AGENTS_FILES = [CONFIG / f"AGENTS.{cli}.md" for cli in ("claude", "codex", "copilot", "pi")]
SESSION_MENU = CONFIG / "session-menu.md"

KEYS = (
    "model_matrix_configured",
    "fingerprint_confirmed",
    "agent_context_populated",
    "test_regime_detected",
    "hooks_decided",
    "counter_seeded",
)


def _fitting_section() -> str:
    text = VIRGIL.read_text()
    start = text.index("\n## Fitting")
    following = re.search(r"^## ", text[start + 4 :], re.MULTILINE)
    return text[start : start + 4 + following.start()] if following else text[start:]


def _step(heading: str) -> str:
    section = _fitting_section()
    match = re.search(rf"^### {re.escape(heading)}.*$", section, re.MULTILINE)
    assert match, f"no step headed {heading!r}"
    following = re.search(r"^###? ", section[match.end() :], re.MULTILINE)
    end = match.end() + following.start() if following else len(section)
    return section[match.start() : end]


@pytest.mark.spec("CIF-01-LN-01")
def test_st_0377_seed_step_follows_hooks_step_and_sets_sixth_key():
    headings = re.findall(r"^### (.+)$", _fitting_section(), re.MULTILINE)
    hooks = next(i for i, h in enumerate(headings) if h.startswith("3. Decide on hooks"))
    assert headings[hooks + 1].startswith("4. Seed the ID counter")
    assert "fitting.counter_seeded" in _step("4. Seed the ID counter")


@pytest.mark.spec("CIF-01-LN-02")
def test_st_0377_seed_step_confirms_before_seeding_and_has_three_ends():
    step = _step("4. Seed the ID counter")
    assert "next-id --plan-seed" in step
    assert re.search(r"only after the (user|newcomer) confirms", step, re.IGNORECASE)
    assert "refs/ids/counters" in step
    assert re.search(r"every later ID continues", step)
    assert re.search(r"declin", step, re.IGNORECASE)
    assert re.search(r"unreachable|does not answer", step, re.IGNORECASE)
    assert re.search(r"in use", step, re.IGNORECASE)
    assert re.search(r"no plain `git push`", step, re.IGNORECASE)


@pytest.mark.spec("CIF-03-LN-01")
def test_st_0377_greenfield_walks_step_zero_and_step_four():
    section = _fitting_section()
    match = re.search(r"Greenfield projects[^\n]*(?:\n[^\n]+)*", section)
    assert match
    paragraph = match.group(0)
    assert re.search(r"step 0", paragraph)
    assert re.search(r"step 4", paragraph)


@pytest.mark.spec("CIF-04-LN-01")
@pytest.mark.parametrize("path", AGENTS_FILES, ids=lambda p: p.name)
def test_st_0377_agents_file_lists_six_keys_with_counter_seeded_sixth(path):
    text = path.read_text()
    rows = re.findall(r"^\| `(\w+)`\s+\| (.+?)\s+\|$", text, re.MULTILINE)
    assert tuple(key for key, _ in rows) == KEYS
    assert rows[-1][1] == "ID counter seed"
    assert "X/6" in text
    assert "six fitting keys" in text


@pytest.mark.spec("CIF-04-LN-01")
def test_st_0377_session_menu_counts_six_steps():
    text = SESSION_MENU.read_text()
    assert "X/6" in text
    assert re.search(r"all six fitting steps[^\n]*seed", text)


def test_st_0377_no_five_key_wording_remains():
    stale = re.compile(r"X/5|five fitting steps|all five keys|five fitting keys", re.IGNORECASE)
    paths = [p for p in CONFIG.glob("*.md")] + [VIRGIL]
    hits = [p.name for p in paths if stale.search(p.read_text())]
    assert hits == []


@pytest.mark.spec("CIF-02-LN-01")
def test_st_0379_missing_origin_sets_the_setting_before_plan_seed():
    step = _step("4. Seed the ID counter")
    setting = step.index("agent-factory.counterRemote")
    assert "git rev-parse --git-common-dir" in step
    assert re.search(r"parent of the directory", step)
    assert setting < step.index("next-id --plan-seed")


def _before_menu() -> str:
    text = SESSION_MENU.read_text()
    return text[: text.index("What do you want to do?")]


@pytest.mark.spec("CIF-09-LN-01")
def test_st_0382_check_before_menu_names_both_conditions():
    check = _before_menu()
    assert "git config agent-factory.counterRemote" in check
    assert "git remote get-url origin" in check


@pytest.mark.spec("CIF-09-LN-01")
def test_st_0382_offer_runs_the_move_only_after_confirmation():
    check = _before_menu()
    assert "next-id --move-to-origin" in check
    assert re.search(r"only after the (user|developer) confirms", check, re.IGNORECASE)


@pytest.mark.spec("CIF-09-LN-01")
def test_st_0382_collision_report_names_both_counters_and_changes_nothing_else():
    check = _before_menu()
    assert re.search(r"two counters", check)
    assert re.search(r"names both", check)
    assert re.search(r"lines[^\n]*next-id[^\n]*printed", check)
    assert re.search(r"changes nothing else", check)


@pytest.mark.spec("CIF-09-LN-01")
def test_st_0382_no_offer_without_origin_or_setting():
    check = _before_menu()
    assert re.search(r"without `origin`[^\n]*no move", check, re.IGNORECASE)
    assert re.search(r"without the setting", check, re.IGNORECASE)


@pytest.mark.spec("CIF-09-LN-01")
def test_st_0382_other_failure_names_next_session_start():
    check = _before_menu()
    assert re.search(r"next session start", check)
