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
from conftest import SOURCE_SCRIPTS_DIR
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
    ledger.invocation_branch = "feat/x"
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


# -- merge-story accepts the story's own spec-feedback report ----------------


def _commit_report_only(story: Path, story_id: str) -> str:
    path = story / _report_path(story_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_report((CORE, "open")))
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
