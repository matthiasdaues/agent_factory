"""close-wave refuses to close a wave while a drift row is unhandled (ST-0361).

Each test builds a scratch repository with an invocation branch, writes a
ledger whose wave 2 holds ST-0318, ST-0319, and ST-0320, commits the
spec-feedback reports on the invocation branch, and runs dispatch the way
the implementation agent does. The fixture is the `wave-2` Demo Data of
backlog/ST-0361.md (BR-062, BR-063, ADR-0029, ATAM-0008).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import SOURCE_SCRIPTS_DIR, write_review_report
from test_dispatch_merge_safety import _dispatch, _git, dispatched  # noqa: F401

import dispatch_lib as lib

WAVE = ("ST-0318", "ST-0319", "ST-0320")
CORE = "docs/spec/validation-rules.md"
QA_STRATEGY = "docs/spec/work/payments-qa-strategy.md"
ADR = "docs/adr/0012-dispatcher-owned-gate-loop.md"
HEADER = (
    "| Artifact | Drift | Evidence | Owner | Status |\n"
    "| -------- | ----- | -------- | ----- | ------ |\n"
)


def _report(*rows: tuple[str, str]) -> str:
    body = "".join(
        f"| `{artifact}` | The rule differs. | `src/x.py:1` | owner-agent | `{status}` |\n"
        for artifact, status in rows
    )
    return "# Spec feedback\n\n" + HEADER + body


def _report_path(story_id: str) -> str:
    return f"docs/spec/work/spec-feedback-{story_id}.md"


@pytest.fixture()
def wave_two(tmp_path: Path) -> dict[str, Path]:
    """A repo whose ledger records wave 2 with three merged stories."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / ".gitignore").write_text(".current-work/\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    inv = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(inv))
    ledger_path = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    ledger = lib.Ledger()
    ledger.feature_branch = "feat/x"
    ledger.waves.append(lib.WaveCloseout(number=1, branch_head="a" * 40))
    for story_id in WAVE:
        ledger.stories[story_id] = lib.StoryEntry(
            id=story_id, wave=2, status=lib.StoryState.DONE, commit_sha="b" * 40,
        )
    ledger.save(ledger_path)
    return {"repo": repo, "inv": inv, "ledger": ledger_path}


def _commit_reports(r: dict[str, Path], reports: dict[str, str]) -> None:
    """Commit *reports* (story id to text) on the invocation branch."""
    for story_id, text in reports.items():
        path = r["inv"] / _report_path(story_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    _git(r["inv"], "add", "-A")
    _git(r["inv"], "commit", "-qm", "reports")


def _closed_waves(r: dict[str, Path]) -> list[int]:
    data = yaml.safe_load(r["ledger"].read_text())
    return [w["number"] for w in data.get("waves") or []]


def _close(r: dict[str, Path], dispatch: Path | None = None):
    if dispatch is None:
        return _dispatch(r["repo"], r["ledger"], "close-wave", "2")
    return subprocess.run(
        [str(dispatch), "--ledger", str(r["ledger"]), "close-wave", "2"],
        cwd=r["repo"], capture_output=True, text=True, check=False,
    )


# -- CAO-14-IT-01: the status of each row decides the close ------------------


@pytest.mark.spec("CAO-14-IT-01")
def test_st_0361_wave_two_fails_on_the_open_core_row(wave_two):
    _commit_reports(wave_two, {
        "ST-0318": _report((CORE, "open")),
        "ST-0319": _report((QA_STRATEGY, "fixed")),
    })

    result = _close(wave_two)

    assert result.returncode != 0
    assert "spec-feedback-ST-0318.md" in result.stderr
    assert CORE in result.stderr
    assert "open" in result.stderr
    assert "ST-0319" not in result.stderr
    assert _closed_waves(wave_two) == [1]


@pytest.mark.spec("CAO-14-IT-01")
@pytest.mark.parametrize(
    ("artifact", "status", "passes"),
    [
        (CORE, "open", False),
        (CORE, "fixed", False),
        (CORE, "confirmed", True),
        (QA_STRATEGY, "open", False),
        (QA_STRATEGY, "fixed", True),
        (ADR, "fixed", True),
        (CORE, "rejected", True),
    ],
)
def test_st_0361_close_wave_checks_the_status_of_each_row(
    wave_two, artifact, status, passes,
):
    _commit_reports(wave_two, {"ST-0318": _report((artifact, status))})

    result = _close(wave_two)

    if passes:
        assert result.returncode == 0, result.stderr
        assert _closed_waves(wave_two) == [1, 2]
    else:
        assert result.returncode != 0
        assert "spec-feedback-ST-0318.md" in result.stderr
        assert artifact in result.stderr
        assert status in result.stderr
        assert _closed_waves(wave_two) == [1]


@pytest.mark.spec("CAO-14-IT-01")
def test_st_0361_names_every_unhandled_row(wave_two):
    _commit_reports(wave_two, {
        "ST-0318": _report((CORE, "fixed"), ("docs/spec/glossary.md", "open")),
        "ST-0320": _report((QA_STRATEGY, "open")),
    })

    result = _close(wave_two)

    assert result.returncode != 0
    for name in (CORE, "docs/spec/glossary.md", QA_STRATEGY):
        assert name in result.stderr
    assert "spec-feedback-ST-0320.md" in result.stderr


@pytest.mark.spec("CAO-14-IT-01")
def test_st_0361_the_demo_closes_after_the_row_is_confirmed(wave_two):
    """Demo Scenario steps 1 to 4: open, then fixed, then confirmed."""
    for status, passes in (("open", False), ("fixed", False), ("confirmed", True)):
        _commit_reports(wave_two, {
            "ST-0318": _report((CORE, status)),
            "ST-0319": _report((QA_STRATEGY, "fixed")),
        })
        result = _close(wave_two)
        assert (result.returncode == 0) is passes, (status, result.stderr)
    assert _closed_waves(wave_two) == [1, 2]


@pytest.mark.spec("CAO-14-IT-01")
def test_st_0361_a_wave_without_reports_closes(wave_two):
    """CAO-G13: a story without a report counts as a story without rows."""
    result = _close(wave_two)

    assert result.returncode == 0, result.stderr
    assert _closed_waves(wave_two) == [1, 2]


@pytest.mark.spec("CAO-14-IT-01")
def test_st_0361_an_uncommitted_status_change_does_not_count(wave_two):
    """Sessions commit the row status on the invocation branch (ADR-0029)."""
    _commit_reports(wave_two, {"ST-0318": _report((CORE, "open"))})
    (wave_two["inv"] / _report_path("ST-0318")).write_text(
        _report((CORE, "confirmed"))
    )

    result = _close(wave_two)

    assert result.returncode != 0
    assert "open" in result.stderr


# -- ATAM-0008: close-wave fails closed on input it cannot read --------------


@pytest.mark.spec("CAO-14-IT-01")
@pytest.mark.parametrize(
    ("text", "names"),
    [
        (_report((CORE, "done")), "done"),
        (_report(("", "fixed")), "Artifact"),
        ("# Spec feedback\n\nNo drift found.\n", "Artifact"),
        (
            "| Artifact | Mismatch | Evidence | Owner | Status |\n"
            "| --- | --- | --- | --- | --- |\n"
            f"| {CORE} | x | y | z | open |\n",
            "Drift",
        ),
    ],
    ids=["unknown-status", "empty-artifact", "no-table", "wrong-header"],
)
def test_st_0361_an_unreadable_report_fails_and_names_the_file(
    wave_two, text, names,
):
    _commit_reports(wave_two, {"ST-0319": text})

    result = _close(wave_two)

    assert result.returncode != 0
    assert "spec-feedback-ST-0319.md" in result.stderr
    assert names in result.stderr
    assert _closed_waves(wave_two) == [1]


# -- CAO-14-IT-02: the installed core list classifies a row ------------------


def _installed_dispatch(tmp_path: Path, core_list: str | None) -> Path:
    """Copy the scripts into an installed layout with its own core list."""
    factory = tmp_path / "installed" / ".agent-factory" / "factory"
    shutil.copytree(SOURCE_SCRIPTS_DIR, factory / "scripts")
    (factory / "rulebooks").mkdir()
    if core_list is not None:
        (factory / "rulebooks" / "core-artifacts.yaml").write_text(core_list)
    return factory / "scripts" / "dispatch"


@pytest.mark.spec("CAO-14-IT-02")
def test_st_0361_the_installed_core_list_classifies_a_fixed_row(wave_two, tmp_path):
    _commit_reports(wave_two, {"ST-0319": _report((QA_STRATEGY, "fixed"))})
    source = _installed_dispatch(tmp_path / "a", (
        SOURCE_SCRIPTS_DIR.parent / "rulebooks" / "core-artifacts.yaml"
    ).read_text())
    changed = _installed_dispatch(tmp_path / "b", (
        "entries:\n"
        "  - path_pattern: docs/spec/work/{name}-qa-strategy.md\n"
        "    sample_path: docs/spec/work/example-qa-strategy.md\n"
        "    family: seam\n"
        "    optional: true\n"
    ))

    blocked = _close(wave_two, changed)
    assert blocked.returncode != 0
    assert QA_STRATEGY in blocked.stderr

    passed = _close(wave_two, source)
    assert passed.returncode == 0, passed.stderr


@pytest.mark.spec("CAO-14-IT-02")
@pytest.mark.parametrize("core_list", [None, "entries: [\n", "entries: []\n"])
def test_st_0361_a_missing_core_list_fails_and_names_the_path(
    wave_two, tmp_path, core_list,
):
    dispatch = _installed_dispatch(tmp_path, core_list)

    result = _close(wave_two, dispatch)

    assert result.returncode != 0
    assert ".agent-factory/factory/rulebooks/core-artifacts.yaml" in result.stderr
    assert _closed_waves(wave_two) == [1]


# -- RL-11-IT: the next wave starts only after the wave close (ST-0421) -----

GLOSSARY = "docs/spec/glossary.md"
RUNTIME_VIEW = "docs/arc42/06_runtime_view.md"
STORY = """---
id: {id}
title: {id}
tier: economy
status: open
deps: []
touches: ["src/{id}.txt"]
quality-gates: []
---
# {id}
"""


def _owned_report(*rows: tuple[str, str, str]) -> str:
    """A report whose rows are (artifact, owner, status)."""
    body = "".join(
        f"| `{artifact}` | The rule differs. | `src/x.py:1` | `{owner}` | `{status}` |\n"
        for artifact, owner, status in rows
    )
    return "# Spec feedback\n\n" + HEADER + body


@pytest.fixture()
def run_on_login(tmp_path: Path):
    """A repository with backlog stories and the feature branch feature/login.

    Call the returned builder with ledger entries to write the ledger of an
    orchestrated run, or of a run by hand in the primary checkout."""
    repo = tmp_path / "repo"
    for folder in ("backlog", "docs", "src"):
        (repo / folder).mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    for story_id in ("ST-0350", "ST-0351", "ST-0352"):
        (repo / "backlog" / f"{story_id}.md").write_text(STORY.format(id=story_id))
    (repo / "docs" / "testing.yaml").write_text('test_command: "true"\n')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    ledger_path = repo / ".current-work" / "feature" / "login" / "dispatch-ledger.yaml"

    def build(*entries: lib.StoryEntry, mode: str = "orchestrated") -> dict[str, Path]:
        if mode == "by-hand":
            _git(repo, "checkout", "-q", "-b", "feature/login")
            feature = repo
        else:
            feature = repo / ".current-work" / "feature" / "login" / "inv"
            _git(repo, "worktree", "add", "-q", "-b", "feature/login", str(feature))
        ledger = lib.Ledger()
        ledger.mode = mode
        ledger.feature_branch = "feature/login"
        ledger.branch_root = _git(repo, "rev-parse", "feature/login")
        for entry in entries:
            ledger.stories[entry.id] = entry
        ledger.save(ledger_path)
        return {"repo": repo, "inv": feature, "ledger": ledger_path}

    return build


def _entry(story_id: str, wave: int | None, status=lib.StoryState.PENDING, **fields):
    if status == lib.StoryState.DONE:
        fields.setdefault("commit_sha", "b" * 40)
    return lib.StoryEntry(
        id=story_id, wave=wave, status=status, feature_branch="feature/login",
        deps=fields.pop("deps", []), **fields,
    )


def _status(r: dict[str, Path], story_id: str) -> str:
    return yaml.safe_load(r["ledger"].read_text())["stories"][story_id]["status"]


def _branch_exists(r: dict[str, Path], branch: str) -> bool:
    return bool(_git(r["repo"], "branch", "--list", branch))


@pytest.mark.spec("RL-11-IT-01")
def test_RL_11_IT_01_close_wave_lists_each_unhandled_row_with_its_owner(run_on_login):
    """Scenario: close-wave refuses while a drift row is not handled."""
    r = run_on_login(
        _entry("ST-0350", 1, lib.StoryState.DONE),
        _entry("ST-0351", 1, lib.StoryState.BLOCKED, reason="red suite"),
    )
    _commit_reports(r, {
        "ST-0350": _owned_report((RUNTIME_VIEW, "architecture-agent", "open")),
        "ST-0351": _owned_report((GLOSSARY, "domain-modeling-agent", "fixed")),
    })

    result = _dispatch(r["repo"], r["ledger"], "close-wave", "1")

    assert result.returncode != 0
    lines = result.stderr.splitlines()
    open_row = next(line for line in lines if RUNTIME_VIEW in line)
    fixed_row = next(line for line in lines if GLOSSARY in line)
    assert "spec-feedback-ST-0350.md" in open_row
    assert "architecture-agent" in open_row and "open" in open_row
    assert "spec-feedback-ST-0351.md" in fixed_row
    assert "domain-modeling-agent" in fixed_row and "fixed" in fixed_row
    assert _closed_waves(r) == []


@pytest.mark.spec("RL-11-IT-02")
def test_RL_11_IT_02_the_next_wave_waits_for_the_wave_record(run_on_login):
    """Scenario: The next wave waits for the wave record. Demo Scenario steps
    1 to 3: the drift sessions handle the row, close-wave passes, and only
    then prepare-wave 2 prepares ST-0352."""
    r = run_on_login(
        _entry("ST-0350", 1, lib.StoryState.DONE),
        _entry("ST-0352", 2),
    )
    _commit_reports(r, {
        "ST-0350": _owned_report((RUNTIME_VIEW, "architecture-agent", "open")),
    })

    before = _dispatch(r["repo"], r["ledger"], "prepare-wave", "2")

    assert before.returncode != 0
    assert "wave 1 has no wave record" in before.stderr
    assert _status(r, "ST-0352") == "pending"
    assert not _branch_exists(r, "story/ST-0352")

    refused = _dispatch(r["repo"], r["ledger"], "close-wave", "1")
    assert refused.returncode != 0
    assert "architecture-agent" in refused.stderr
    # The owner fixes the row and the architecture is no core artifact.
    _commit_reports(r, {
        "ST-0350": _owned_report((RUNTIME_VIEW, "architecture-agent", "fixed")),
    })
    closed = _dispatch(r["repo"], r["ledger"], "close-wave", "1")
    assert closed.returncode == 0, closed.stderr
    after = _dispatch(r["repo"], r["ledger"], "prepare-wave", "2")

    assert after.returncode == 0, after.stderr
    assert _status(r, "ST-0352") == "prepared"


@pytest.mark.spec("RL-11-IT-03")
def test_RL_11_IT_03_by_hand_each_story_is_a_wave_of_its_own(run_on_login):
    """Scenario: In a run by hand, each story is a wave of its own."""
    r = run_on_login(
        _entry("ST-0350", 1, lib.StoryState.DONE),
        _entry("ST-0351", None),
        mode="by-hand",
    )
    _commit_reports(r, {
        "ST-0350": _owned_report((GLOSSARY, "domain-modeling-agent", "open")),
    })

    refused = _dispatch(r["repo"], r["ledger"], "prepare-story", "ST-0351")
    still_open = _dispatch(r["repo"], r["ledger"], "close-wave", "1")

    assert refused.returncode != 0
    assert "wave 1 has no wave record" in refused.stderr
    assert _status(r, "ST-0351") == "pending"
    assert not _branch_exists(r, "story/ST-0351")
    assert still_open.returncode != 0
    assert "domain-modeling-agent" in still_open.stderr
    assert _closed_waves(r) == []

    _commit_reports(r, {
        "ST-0350": _owned_report((GLOSSARY, "domain-modeling-agent", "confirmed")),
    })
    closed = _dispatch(r["repo"], r["ledger"], "close-wave", "1")
    started = _dispatch(r["repo"], r["ledger"], "prepare-story", "ST-0351")

    assert closed.returncode == 0, closed.stderr
    assert _closed_waves(r) == [1]
    assert started.returncode == 0, started.stderr
    entry = yaml.safe_load(r["ledger"].read_text())["stories"]["ST-0351"]
    assert (entry["status"], entry["wave"]) == ("prepared", 2)


@pytest.mark.spec("RL-11-IT-04")
def test_RL_11_IT_04_a_wave_with_a_returned_story_closes_and_the_next_story_starts(
    run_on_login,
):
    """Scenario: A wave that holds a returned story closes, and the next
    independent story starts."""
    r = run_on_login(
        _entry("ST-0350", 1, lib.StoryState.DONE),
        _entry("ST-0351", 1, returned=True),
        _entry("ST-0352", 2),
    )

    closed = _dispatch(r["repo"], r["ledger"], "close-wave", "1")
    started = _dispatch(r["repo"], r["ledger"], "prepare-wave", "2")

    assert closed.returncode == 0, closed.stderr
    assert _closed_waves(r) == [1]
    entry = yaml.safe_load(r["ledger"].read_text())["stories"]["ST-0351"]
    assert (entry["status"], entry["wave"], entry["returned"]) == ("pending", 1, True)
    assert started.returncode == 0, started.stderr
    assert _status(r, "ST-0352") == "prepared"


# -- merge-story accepts the story's own spec-feedback report ----------------


def _commit_report_only(story: Path, story_id: str) -> str:
    path = story / _report_path(story_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_report((CORE, "open")))
    write_review_report(story, "ST-0001")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "spec feedback")
    return _git(story, "rev-parse", "HEAD")


@pytest.mark.parametrize(("report_of", "passes"), [("ST-0001", True), ("ST-0002", False)])
def test_st_0361_merge_scope_accepts_only_the_storys_own_report(
    dispatched, report_of, passes,  # noqa: F811
):
    repo, inv, ledger = dispatched["repo"], dispatched["inv"], dispatched["ledger"]
    sha = _commit_report_only(dispatched["story"], report_of)
    assert _dispatch(repo, ledger, "verify-story", "ST-0001", "--sha", sha).returncode == 0

    result = _dispatch(inv, ledger, "merge-story", "ST-0001")

    output = result.stdout + result.stderr
    if passes:
        assert result.returncode == 0, output
        assert (inv / _report_path("ST-0001")).is_file()
    else:
        assert result.returncode != 0
        assert "premerge-check failed" in output
        assert _report_path("ST-0002") in output
