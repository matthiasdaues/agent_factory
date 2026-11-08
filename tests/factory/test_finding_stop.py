"""A critical finding stops dispatch and premerge-check (ST-0397, BR-091).

The contract tests (FC-14-CT-01 to FC-14-CT-03) call the stop functions of
dispatch_lib directly. The integration tests (FC-14-IT-01 to FC-14-IT-09)
build scratch repositories in tmp_path and run the scripts as subprocesses.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT, SOURCE_SCRIPTS_DIR, load_script
from test_dispatch_merge_safety import _dispatch, _env, _git
from test_dispatch_run_blockers import _init, _repo, _story_worktree

import dispatch_lib as lib

PREMERGE_CHECK = SOURCE_SCRIPTS_DIR / "premerge-check"
HOOK = REPO_ROOT / "packages" / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
CONTRACTS = REPO_ROOT / "docs" / "spec" / "interface-contracts.md"

STOP_SUBCOMMANDS = [
    "init", "prepare-wave", "prepare-story", "mark-dispatching", "mark-dispatched",
    "re-dispatch", "escalate", "refresh-story", "merge-story", "close-wave",
]
READ_SUBCOMMANDS = [
    "status", "plan", "suggest-merge-args", "verify-story", "mark-done",
    "mark-blocked", "mark-failed", "clear-manifest",
]

BUG_0037 = """\
---
id: BUG-0037
source: bug-hunt
review_class: code
category: defect
type: checking
severity: critical
basis:
  in_use: true
  harms_downstream: true
  fails_purpose: true
  raises_cost: true
rating: null
override_by: null
override_reason: null
stop_confirmed_by: {by}
stop_confirmed_reason: {reason}
artifact: packages/factory/scripts/dispatch:1383
status: {status}
owner: developer-agent
---

# An empty story passes verify-story, and a red suite then resets earlier merges away

**What is wrong:** `merge-story` resets the branch hard to a guessed state.

**Why this severity:** The lines exist unchanged in .agent-factory/factory/scripts/dispatch, which every dispatch run executes. The reset removes merges that later stories build on.

**Fix:** Treat a story as merged only when `HEAD` is its merge commit.

## Possible damage

- merges on `dev` from dispatch runs since the installed copy was last updated — check: compare `git log --merges dev` with the merges the dispatch log records
"""


def finding(
    *, by: str = "null", reason: str = "null", status: str = "open",
    severity: str = "critical", review_class: bool = True,
) -> str:
    text = BUG_0037.format(by=by, reason=reason, status=status)
    text = text.replace("severity: critical", f"severity: {severity}")
    if not review_class:
        text = text.replace("review_class: code\n", "")
    return text


def contract_example() -> str:
    """Return the BUG-0037 notice from the stop contract in interface-contracts.md."""
    text = CONTRACTS.read_text()
    section = text.split("### The stop in `dispatch` and `premerge-check`", 1)[1]
    match = re.search(r"```text\n(.*?)```", section, re.S)
    assert match, "no text block in the stop contract"
    return match.group(1)


# -- FC-14-CT-01: the stop condition on both versions ------------------------


@pytest.mark.parametrize(
    ("worktree", "head", "stops"),
    [
        pytest.param(finding(), None, True, id="uncommitted-critical-open"),
        pytest.param(finding(), finding(), True, id="both-critical-open"),
        pytest.param(finding(by="human"), finding(), True, id="by-without-reason"),
        pytest.param(finding(by="human", reason='""'), finding(), True, id="empty-reason"),
        pytest.param(finding(reason="checked"), finding(), True, id="reason-without-by"),
        pytest.param(
            finding(by="human", reason="compared 14 merges, none lost"), finding(),
            False, id="worktree-confirmed",
        ),
        pytest.param(
            finding(status="resolved"),
            finding(by="human", reason="compared 14 merges, none lost"),
            False, id="head-confirmed",
        ),
        pytest.param(finding(status="deferred"), finding(), True, id="worktree-deferred"),
        pytest.param(finding(status="resolved"), finding(), True, id="worktree-resolved"),
        pytest.param(finding(severity="major"), finding(), True, id="worktree-lowered"),
        pytest.param(None, finding(), True, id="worktree-removed"),
        pytest.param(None, finding(status="deferred"), True, id="head-deferred"),
        pytest.param(finding(status="waived"), finding(), True, id="worktree-waived"),
        pytest.param(
            finding(status="resolved", review_class=False),
            finding(status="resolved", review_class=False),
            False, id="old-resolved-without-class",
        ),
        pytest.param(
            finding(status="open", review_class=False), None, True,
            id="old-open-without-class",
        ),
        pytest.param(finding(severity="major"), finding(severity="major"), False, id="major"),
        pytest.param(None, None, False, id="no-file"),
    ],
)
def test_st_0397_stop_condition_reads_both_versions(worktree, head, stops):
    assert lib.finding_stops(worktree, head) is stops


def test_st_0397_stop_parts_come_from_the_version_that_is_critical():
    head = finding()
    lowered = finding(severity="major").replace(
        "every dispatch run executes", "nothing executes"
    )

    entry = lib.stop_entry("BUG-0037", lowered, head)

    assert entry is not None
    assert "every dispatch run executes" in entry.in_use


# -- FC-14-CT-02: the stop notice --------------------------------------------


def test_st_0397_notice_equals_the_example_of_the_stop_contract():
    entry = lib.stop_entry("BUG-0037", finding(), None)

    notice = lib.render_stop_notice([entry])

    assert notice.splitlines() == contract_example().splitlines()
    assert notice == contract_example()


# -- FC-14-CT-03: every parser subcommand is in exactly one list --------------


def test_st_0397_every_dispatch_subcommand_is_in_exactly_one_list():
    dispatch = load_script("dispatch")
    parser = dispatch.build_parser()
    action = next(a for a in parser._actions if a.dest == "subcommand")
    names = set(action.choices)

    assert lib.STOP_SUBCOMMANDS.isdisjoint(lib.READ_SUBCOMMANDS)
    assert names == lib.STOP_SUBCOMMANDS | lib.READ_SUBCOMMANDS
    assert lib.STOP_SUBCOMMANDS == set(STOP_SUBCOMMANDS)
    assert lib.READ_SUBCOMMANDS == set(READ_SUBCOMMANDS)


# -- Integration helpers -----------------------------------------------------


def write_finding(root: Path, text: str, name: str = "BUG-0037") -> Path:
    path = root / "docs" / "findings" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def commit_finding(root: Path, text: str, name: str = "BUG-0037") -> Path:
    path = write_finding(root, text, name)
    _git(root, "add", str(path))
    _git(root, "commit", "-qm", f"add {name}")
    return path


def premerge(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(PREMERGE_CHECK), *args], cwd=cwd, env=_env(),
        capture_output=True, text=True, check=False,
    )


def merge_repo(tmp_path: Path) -> Path:
    """A repo on dev with branch feature/core-artifact-ownership one commit ahead."""
    repo = tmp_path / "merge-repo"
    _git(tmp_path, "init", "-q", "-b", "dev", str(repo))
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "README.md").write_text("init\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "checkout", "-q", "-b", "feature/core-artifact-ownership")
    (repo / "feature.txt").write_text("feature\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "feature")
    _git(repo, "checkout", "-q", "dev")
    return repo


def state(r: dict[str, Path]) -> tuple[str, str, str]:
    """The ledger text, the branch heads, and the worktree list."""
    ledger = r["ledger"].read_text() if r["ledger"].exists() else ""
    refs = _git(r["repo"], "for-each-ref", "--format=%(refname) %(objectname)")
    worktrees = _git(r["repo"], "worktree", "list", "--porcelain")
    return ledger, refs, worktrees


@pytest.fixture(scope="module")
def stopped_run(tmp_path_factory) -> dict[str, Path]:
    """A dispatch run with ST-0001 prepared, then stopped by an uncommitted BUG-0037."""
    r = _repo(tmp_path_factory.mktemp("stop"))
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    write_finding(r["repo"], finding())
    return r


def stop_args(r: dict[str, Path], subcommand: str) -> list[str]:
    base = _git(r["repo"], "rev-parse", "HEAD")
    return {
        "init": ["init", "--base", base, "--stories", "ST-0001", "--yes"],
        "prepare-wave": ["prepare-wave", "1"],
        "prepare-story": ["prepare-story", "ST-0002"],
        "close-wave": ["close-wave", "1"],
    }.get(subcommand, [subcommand, "ST-0001"])


# -- FC-14-IT-01: dispatch refuses each start or merge subcommand -------------


@pytest.mark.parametrize("subcommand", STOP_SUBCOMMANDS)
def test_st_0397_dispatch_refuses_work_during_a_stop(stopped_run, subcommand):
    r = stopped_run
    before = state(r)

    result = _dispatch(r["repo"], r["ledger"], *stop_args(r, subcommand))

    assert result.returncode == 1, result.stderr
    assert result.stdout == contract_example()
    assert state(r) == before


# -- FC-14-IT-02: dispatch answers reads during a stop ------------------------


def _read_run(tmp_path: Path, subcommand: str, *, stop: bool):
    """Run *subcommand* on a prepared run, with or without BUG-0037."""
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    for step in ("mark-dispatching", "mark-dispatched"):
        assert _dispatch(r["repo"], r["ledger"], step, "ST-0001").returncode == 0
    story = _story_worktree(r, "ST-0001")
    (story / "src" / "ST-0001.txt").write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "work")
    sha = _git(story, "rev-parse", "HEAD")
    if stop:
        write_finding(r["repo"], finding())
    args = {
        "plan": ["plan", "--backlog-dir", "backlog", "--dry-run"],
        "suggest-merge-args": ["suggest-merge-args"],
        "status": ["status"],
        "verify-story": ["verify-story", "ST-0001", "--sha", sha],
        "mark-blocked": ["mark-blocked", "ST-0001", "--reason", "waits"],
        "clear-manifest": ["clear-manifest", "--force", "--worktree", str(story)],
    }.get(subcommand, [subcommand, "ST-0001"])
    result = _dispatch(r["repo"], r["ledger"], *args)
    return result.returncode, _normal(result.stdout, tmp_path), _normal(
        r["ledger"].read_text(), tmp_path
    )


def _normal(text: str, root: Path) -> str:
    """Mask the paths and commit SHAs that differ between two scratch repositories."""
    return re.sub(r"\b[0-9a-f]{40}\b", "<sha>", text.replace(str(root), "<tmp>"))


@pytest.mark.parametrize("subcommand", READ_SUBCOMMANDS)
def test_st_0397_dispatch_answers_reads_during_a_stop(tmp_path, subcommand):
    without = _read_run(tmp_path / "plain", subcommand, stop=False)
    during = _read_run(tmp_path / "stopped", subcommand, stop=True)

    assert "STOP:" not in during[1]
    assert during == without


# -- FC-14-IT-03 and FC-14-IT-04: premerge-check refuses, the merge is denied --


def test_st_0397_premerge_check_refuses_and_writes_no_marker(tmp_path):
    repo = merge_repo(tmp_path)
    write_finding(repo, finding())

    result = premerge(repo, "dev", "feature/core-artifact-ownership")

    assert result.returncode == 1
    assert result.stdout == contract_example()
    assert not (repo / ".current-work" / "premerge-check-ok").exists()


def test_st_0397_merge_is_denied_after_the_refused_premerge_check(tmp_path):
    repo = merge_repo(tmp_path)
    write_finding(repo, finding())
    assert premerge(repo, "dev", "feature/core-artifact-ownership").returncode == 1

    payload = json.dumps(
        {"tool_input": {"command": "git merge feature/core-artifact-ownership"}}
    )
    result = subprocess.run(
        ["bash", str(HOOK)], input=payload, cwd=repo, env=_env(),
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 2
    assert "premerge-check-ok" in result.stderr


# -- FC-14-IT-05: the stop reads the worktree it runs in ----------------------


def test_st_0397_stop_reads_only_the_worktree_it_runs_in(tmp_path):
    repo = merge_repo(tmp_path)
    feature = repo / ".current-work" / "feature"
    _git(repo, "worktree", "add", "-q", str(feature), "feature/core-artifact-ownership")
    write_finding(feature, finding())

    in_feature = premerge(feature, "dev", "feature/core-artifact-ownership")
    in_main = premerge(repo, "dev", "feature/core-artifact-ownership")

    assert in_feature.returncode == 1
    assert in_feature.stdout == contract_example()
    assert "STOP:" not in in_main.stdout
    assert in_main.returncode == 0, in_main.stdout


# -- FC-14-IT-06: both scripts print the same notice ---------------------------


def test_st_0397_both_scripts_print_the_same_notice(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    write_finding(r["repo"], finding())

    from_dispatch = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")
    from_premerge = premerge(r["repo"], "dev", "feat/x")

    assert from_dispatch.stdout == from_premerge.stdout == contract_example()
    assert "STOP" not in from_dispatch.stderr
    assert "STOP" not in from_premerge.stderr


# -- FC-14-IT-07 and FC-14-IT-08: the confirmation lifts the stop --------------


def test_st_0397_an_uncommitted_confirmation_lifts_the_stop(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    commit_finding(r["repo"], finding())
    write_finding(
        r["repo"], finding(by="human", reason="compared 14 merges, none lost")
    )

    from_dispatch = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")
    from_premerge = premerge(r["repo"], "dev", "feat/x")

    assert from_dispatch.returncode == 0, from_dispatch.stdout + from_dispatch.stderr
    assert "STOP:" not in from_premerge.stdout
    assert "premerge-check:" in from_premerge.stdout


def test_st_0397_an_empty_reason_holds_the_stop(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    write_finding(r["repo"], finding(by="human", reason='""'))

    from_dispatch = _dispatch(r["repo"], r["ledger"], "prepare-wave", "3")
    from_premerge = premerge(r["repo"], "dev", "feat/x")

    assert from_dispatch.returncode == 1
    assert from_dispatch.stdout == contract_example()
    assert from_premerge.returncode == 1
    assert from_premerge.stdout == contract_example()


# -- FC-14-IT-09: only the confirmation lifts the stop -------------------------


@pytest.mark.parametrize(
    "change",
    ["status: deferred", "status: resolved", "severity: major", "removed"],
)
def test_st_0397_an_uncommitted_change_never_lifts_the_stop(tmp_path, change):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    path = commit_finding(r["repo"], finding())
    before = r["ledger"].read_text()
    if change == "removed":
        path.unlink()
    else:
        key = change.split(":")[0]
        text = re.sub(rf"^{key}: .*$", change, path.read_text(), count=1, flags=re.M)
        path.write_text(text)

    from_dispatch = _dispatch(r["repo"], r["ledger"], "prepare-wave", "3")
    from_premerge = premerge(r["repo"], "dev", "feat/x")

    assert from_dispatch.returncode == 1
    assert from_dispatch.stdout == contract_example()
    assert from_premerge.returncode == 1
    assert from_premerge.stdout == contract_example()
    assert r["ledger"].read_text() == before
    assert yaml.safe_load(before)


def test_st_0397_a_committed_deferred_status_still_stops(tmp_path):
    r = _repo(tmp_path)
    commit_finding(r["repo"], finding(status="deferred"))

    result = premerge(r["repo"], "dev", "feat/x")

    assert result.returncode == 1
    assert result.stdout == contract_example()


def test_st_0397_an_old_resolved_critical_finding_stops_no_run(tmp_path):
    r = _repo(tmp_path)
    commit_finding(r["repo"], finding(status="resolved", review_class=False))

    result = premerge(r["repo"], "dev", "feat/x")

    assert "STOP:" not in result.stdout
    assert "stale-base" in result.stdout


# -- FC-14-IT-10: a committed lowering fails at the hook, and the stop holds ---


@pytest.mark.spec("FC-14-IT-10")
def test_st_0396_hook_rejects_the_lowering_and_the_stop_holds(tmp_path):
    from test_precommit_config_contract import install_finding_lint_hook, run_git

    repo = merge_repo(tmp_path)
    commit_finding(repo, finding())
    install_finding_lint_hook(repo)
    path = write_finding(repo, finding(severity="major"))
    run_git(repo, "add", str(path))

    lowered = run_git(repo, "commit", "-qm", "lower BUG-0037")

    assert lowered.returncode == 1, lowered.stdout + lowered.stderr
    assert "BUG-0037" in lowered.stdout + lowered.stderr
    held = premerge(repo, "dev", "feature/core-artifact-ownership")
    assert held.returncode == 1
    assert held.stdout == contract_example()
