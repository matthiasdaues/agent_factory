"""Dispatch can run a fix wave (BUG-0082 to BUG-0085, BUG-0087).

Each test builds a scratch repository with an invocation branch in its own
worktree and drives dispatch the way the implementation agent does.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from test_dispatch_merge_safety import STORY, _dispatch, _git

DEPENDENT_STORY = STORY.replace("deps: []", "deps: [ST-0001]")
TOUCHES_ONLY_STORY = STORY.replace('outputs: ["src/{id}.txt"]\n', "")
TESTING_YAML = '# comment\ntest_all: "false"\ntest_command: "true"\n'


def _repo(
    tmp_path: Path,
    *,
    testing_yaml: str | None = None,
    project_json: bool = True,
    first_story: str = STORY,
) -> dict[str, Path]:
    """A repo with ST-0001 and ST-0002 (which depends on ST-0001).

    *testing_yaml* is committed as docs/testing.yaml when given. Without it,
    config/project.json carries the test command, unless *project_json* is
    False. *first_story* is the backlog template for ST-0001.
    """
    repo = tmp_path / "repo"
    (repo / "backlog").mkdir(parents=True)
    (repo / "src").mkdir()
    _git(repo.parent, "init", "-q", "-b", "dev", str(repo))
    (repo / "backlog" / "ST-0001.md").write_text(first_story.format(id="ST-0001"))
    (repo / "backlog" / "ST-0002.md").write_text(
        DEPENDENT_STORY.format(id="ST-0002")
    )
    if testing_yaml is not None:
        (repo / "docs").mkdir()
        (repo / "docs" / "testing.yaml").write_text(testing_yaml)
    elif project_json:
        (repo / "config").mkdir()
        (repo / "config" / "project.json").write_text('{"test_command": "true"}')
    (repo / ".gitignore").write_text(".current-work/\n")
    (repo / "src" / ".keep").write_text("")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "init")
    inv = repo / ".current-work" / "feat" / "x" / "inv"
    _git(repo, "worktree", "add", "-q", "-b", "feat/x", str(inv))
    ledger = repo / ".current-work" / "feat" / "x" / "dispatch-ledger.yaml"
    return {"repo": repo, "inv": inv, "ledger": ledger}


def _init(r: dict[str, Path], stories: str = "ST-0001,ST-0002"):
    base = _git(r["repo"], "rev-parse", "HEAD")
    return _dispatch(
        r["repo"], r["ledger"], "init", "--base", base, "--stories", stories,
        "--feature-branch", "feat/x", "--yes",
    )


def _ledger(r: dict[str, Path]) -> dict:
    return yaml.safe_load(r["ledger"].read_text())


def _story(ledger: dict, story_id: str) -> dict:
    stories = ledger["stories"]
    if isinstance(stories, dict):
        return stories[story_id]
    return next(entry for entry in stories if entry["id"] == story_id)


def _story_worktree(r: dict[str, Path], story_id: str) -> Path:
    return r["repo"] / ".current-work" / "feat" / "x" / "story" / story_id


def _contract_test_command(r: dict[str, Path], story_id: str) -> str:
    """Return the test command that prepare-wave wrote into the contract."""
    contract = (
        _story_worktree(r, story_id) / ".current-work" / "feat" / "x" / "story"
        / story_id / "handoff-contract.md"
    )
    for line in contract.read_text().splitlines():
        if line.startswith("- test_command: "):
            return line[len("- test_command: "):]
    raise AssertionError(f"no test_command line in {contract}")


def _prepare_wave_one(r: dict[str, Path], cwd: Path | None = None):
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    return _dispatch(cwd or r["repo"], r["ledger"], "prepare-wave", "1")


# -- BUG-0085: the test command lives in docs/testing.yaml ------------------


@pytest.mark.parametrize(
    ("testing_yaml", "expected"),
    [
        (TESTING_YAML, "true"),
        ('test_all: "true && echo x"   # composite command\n', "true && echo x"),
        ("test_command: null\ntest_all: 'true'\n", "true"),
        ("test_command: \"\"\ntest_all: true-cmd\n", "true-cmd"),
        ("test_all: >-\n  true &&\n  echo folded\nsuites: []\n", "true && echo folded"),
        (
            'test_command: "true && echo x"\nsuites: []\nnotes: >-\n  prose\n\n  more\n',
            "true && echo x",
        ),
    ],
)
def test_prepare_wave_takes_the_test_command_from_testing_yaml(
    tmp_path, testing_yaml, expected
):
    r = _repo(tmp_path, testing_yaml=testing_yaml)

    result = _prepare_wave_one(r)

    assert result.returncode == 0, result.stderr
    assert _contract_test_command(r, "ST-0001") == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ('key: "make test && make frontend_test"   # composite', "make test && make frontend_test"),
        ("key: 'it''s'  # quoted", "it's"),
        ("key: plain value # comment", "plain value"),
        ("key: null", None),
        ("key: ~", None),
        ("key: a#b", "a#b"),
    ],
)
def test_stdlib_yaml_loader_reads_quotes_comments_and_null(line, expected):
    """dispatch runs without PyYAML, so its fallback loader reads testing.yaml."""
    import dispatch_lib as lib

    assert lib._stdlib_load(line)["key"] == expected


@pytest.mark.parametrize(
    "value",
    [
        "123", "null", "true", "see #12", '"quoted"', "'single'", "", " pad", "a\nb", "[]",
        ">", "|", ">-", "|+", "|2", "|-+",
    ],
)
def test_stdlib_yaml_dump_round_trips_strings(value):
    import dispatch_lib as lib

    assert lib._stdlib_load(lib._stdlib_dump({"key": value})) == {"key": value}


def test_an_unreadable_testing_yaml_still_yields_its_test_command(tmp_path):
    r = _repo(
        tmp_path,
        testing_yaml='test_command: "true && echo x"  # c\nnotes: |2\n   indented\n',
    )

    result = _prepare_wave_one(r)

    assert result.returncode == 0, result.stderr
    assert _contract_test_command(r, "ST-0001") == "true && echo x"
    assert "warning: cannot parse" in result.stderr
    assert str(r["repo"] / "docs" / "testing.yaml") in result.stderr
    assert "explicit indentation indicator" in result.stderr


def test_a_null_testing_yaml_command_falls_back_to_project_json(tmp_path):
    r = _repo(tmp_path, testing_yaml="test_command: null\ntest_all: null\n")
    (r["repo"] / "config").mkdir()
    (r["repo"] / "config" / "project.json").write_text(
        '{"test_command": "from-project-json"}'
    )

    result = _prepare_wave_one(r)

    assert result.returncode == 0, result.stderr
    assert _contract_test_command(r, "ST-0001") == "from-project-json"


def test_project_json_is_the_fallback_without_testing_yaml(tmp_path):
    r = _repo(tmp_path)

    result = _prepare_wave_one(r)

    assert result.returncode == 0, result.stderr
    assert _contract_test_command(r, "ST-0001") == "true"


def test_testing_yaml_is_read_from_the_main_checkout(tmp_path):
    r = _repo(tmp_path, project_json=False)
    # Untracked in the main checkout, so the invocation worktree lacks it.
    (r["repo"] / "docs").mkdir()
    (r["repo"] / "docs" / "testing.yaml").write_text("test_command: main-cmd\n")
    assert not (r["inv"] / "docs" / "testing.yaml").exists()

    result = _prepare_wave_one(r, cwd=r["inv"])

    assert result.returncode == 0, result.stderr
    assert _contract_test_command(r, "ST-0001") == "main-cmd"


# -- BUG-0082: dependencies reach the ledger and gate the next story --------


def test_init_records_story_dependencies(tmp_path):
    r = _repo(tmp_path)

    assert _init(r).returncode == 0
    assert _story(_ledger(r), "ST-0002")["deps"] == ["ST-0001"]


def test_plan_refreshes_story_dependencies(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    data = _ledger(r)
    _story(data, "ST-0002")["deps"] = []
    r["ledger"].write_text(yaml.safe_dump(data))

    result = _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog")

    assert result.returncode == 0, result.stderr
    assert _story(_ledger(r), "ST-0002")["deps"] == ["ST-0001"]


def _block_story(r: dict[str, Path], story_id: str) -> None:
    result = _dispatch(
        r["repo"], r["ledger"], "mark-blocked", story_id, "--reason", "red suite",
    )
    assert result.returncode == 0, (result.stdout, result.stderr)


def test_close_wave_does_not_list_a_story_whose_dependency_is_blocked(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")

    result = _dispatch(r["inv"], r["ledger"], "close-wave", "1")

    assert result.returncode == 0, result.stderr
    assert _ledger(r)["waves"][0]["next_ready"] == []


def test_close_wave_does_not_list_a_story_whose_dependency_failed(tmp_path):
    import dispatch_lib as lib

    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    ledger = lib.Ledger.load(r["ledger"])
    ledger.stories["ST-0001"].status = lib.StoryState.FAILED

    record, _ = ledger.close_wave(1, "a" * 40)

    assert record.next_ready == []


def test_prepare_wave_skips_a_story_whose_dependency_is_blocked(tmp_path):
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "2")

    assert result.returncode == 0, result.stderr
    assert "ST-0001" in result.stdout + result.stderr
    assert _story(_ledger(r), "ST-0002")["status"] == "pending"
    branches = _git(r["repo"], "branch", "--list", "story/ST-0002")
    assert branches == ""


# -- BUG-0083: the ledger is runtime state, close-wave commits nothing ------


@pytest.mark.parametrize("where", ["repo", "inv"])
def test_close_wave_saves_the_ledger_without_a_commit(tmp_path, where):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _block_story(r, "ST-0001")
    heads = {b: _git(r["repo"], "rev-parse", b) for b in ("dev", "feat/x")}

    result = _dispatch(r[where], r["ledger"], "close-wave", "1")

    assert result.returncode == 0, result.stderr
    assert [w["number"] for w in _ledger(r)["waves"]] == [1]
    assert {b: _git(r["repo"], "rev-parse", b) for b in heads} == heads


# -- BUG-0084: a failed prepare-wave leaves nothing that blocks a retry -----


def test_prepare_wave_retry_succeeds_after_verify_base_fails(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0

    # Make verify-base fail once: move the invocation branch ahead of the
    # ledger's base, so the story worktree would start behind its target.
    (r["inv"] / "src" / "ahead.txt").write_text("ahead\n")
    _git(r["inv"], "add", "-A")
    _git(r["inv"], "commit", "-qm", "ahead")
    failed = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")
    assert failed.returncode != 0
    assert _git(r["repo"], "branch", "--list", "story/ST-0001") == ""

    # Bring the ledger's base up to the branch, then retry.
    data = _ledger(r)
    data["branch_head"] = _git(r["repo"], "rev-parse", "feat/x")
    r["ledger"].write_text(yaml.safe_dump(data))
    retry = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert retry.returncode == 0, retry.stderr
    assert _story(_ledger(r), "ST-0001")["status"] == "prepared"


def test_prepare_wave_reuses_a_leftover_branch_without_work(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    base = _git(r["repo"], "rev-parse", "feat/x")
    # A leftover from an older dispatch version that died between the two
    # git calls.
    _git(r["repo"], "branch", "story/ST-0001", base)

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode == 0, result.stderr
    assert _story(_ledger(r), "ST-0001")["status"] == "prepared"


def test_prepare_wave_refuses_a_leftover_branch_with_work(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    scratch = r["repo"] / ".current-work" / "scratch"
    _git(r["repo"], "worktree", "add", "-q", "-b", "story/ST-0001", str(scratch))
    (scratch / "src" / "work.txt").write_text("work\n")
    _git(scratch, "add", "-A")
    _git(scratch, "commit", "-qm", "work")
    _story_worktree(r, "ST-0001").parent.mkdir(parents=True)
    _git(r["repo"], "worktree", "move", str(scratch), str(_story_worktree(r, "ST-0001")))
    draft = _story_worktree(r, "ST-0001") / "src" / "draft.txt"
    draft.write_text("uncommitted\n")
    tip = _git(r["repo"], "rev-parse", "story/ST-0001")

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode != 0
    assert "story/ST-0001" in result.stderr
    assert _git(r["repo"], "rev-parse", "story/ST-0001") == tip
    assert draft.read_text() == "uncommitted\n"


def _assert_no_story_workspace(r: dict[str, Path], story_id: str) -> None:
    assert _git(r["repo"], "branch", "--list", f"story/{story_id}") == ""
    assert not _story_worktree(r, story_id).exists()
    assert str(_story_worktree(r, story_id)) not in _git(
        r["repo"], "worktree", "list", "--porcelain"
    )


def test_prepare_wave_rolls_back_when_the_manifest_step_fails(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    # Without a test command the handoff contract, and so the manifest
    # step, fails after the workspace exists.
    (r["repo"] / "config" / "project.json").unlink()

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode != 0
    assert "test command" in result.stderr
    _assert_no_story_workspace(r, "ST-0001")
    assert _story(_ledger(r), "ST-0001")["status"] == "pending"


def test_prepare_wave_rolls_back_when_git_creates_both_and_fails(tmp_path):
    """A failing post-checkout hook makes git worktree add exit 1 after it
    created the branch and the worktree."""
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    hook = r["repo"] / ".git" / "hooks" / "post-checkout"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode != 0
    _assert_no_story_workspace(r, "ST-0001")


# -- D1: a second prepare-wave or prepare-story keeps a live worktree -------


def test_prepare_wave_again_keeps_the_worktree_of_a_dispatching_story(tmp_path):
    r = _repo(tmp_path)
    assert _init(r, "ST-0001").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "mark-dispatching", "ST-0001").returncode == 0
    work = _story_worktree(r, "ST-0001") / "src" / "ST-0001.txt"
    work.write_text("uncommitted agent work\n")

    result = _dispatch(r["repo"], r["ledger"], "prepare-wave", "1")

    assert result.returncode == 0, result.stderr
    assert work.read_text() == "uncommitted agent work\n"
    assert _story(_ledger(r), "ST-0001")["status"] == "dispatching"


def _commit_story_work(
    r: dict[str, Path], story_id: str, extra_paths: tuple[str, ...] = ()
) -> None:
    """Dispatch *story_id*, commit its work plus *extra_paths*, and verify it."""
    for args in (("mark-dispatching", story_id), ("mark-dispatched", story_id)):
        result = _dispatch(r["repo"], r["ledger"], *args)
        assert result.returncode == 0, (args, result.stderr)
    story = _story_worktree(r, story_id)
    for rel in (f"src/{story_id}.txt", *extra_paths):
        (story / rel).parent.mkdir(parents=True, exist_ok=True)
        (story / rel).write_text("work\n")
    _git(story, "add", "-A")
    _git(story, "commit", "-qm", "story work")
    sha = _git(story, "rev-parse", "HEAD")
    result = _dispatch(r["repo"], r["ledger"], "verify-story", story_id, "--sha", sha)
    assert result.returncode == 0, result.stderr


def _finish_story(r: dict[str, Path], story_id: str) -> None:
    """Dispatch, commit, verify, and merge *story_id* into feat/x."""
    _commit_story_work(r, story_id)
    result = _dispatch(r["inv"], r["ledger"], "merge-story", story_id)
    assert result.returncode == 0, result.stderr


@pytest.fixture()
def chain(tmp_path: Path) -> dict[str, Path]:
    """ST-0001 merged into feat/x; ST-0002 waits on it as a chain link."""
    r = _repo(tmp_path)
    assert _init(r).returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "plan", "--backlog-dir", "backlog").returncode == 0
    assert _dispatch(r["repo"], r["ledger"], "prepare-wave", "1").returncode == 0
    _finish_story(r, "ST-0001")
    return r


def test_prepare_story_creates_the_chain_link_workspace(chain):
    merge_sha = _story(_ledger(chain), "ST-0001")["commit_sha"]

    result = _dispatch(chain["repo"], chain["ledger"], "prepare-story", "ST-0002")

    assert result.returncode == 0, result.stderr
    assert _story(_ledger(chain), "ST-0002")["status"] == "prepared"
    assert _git(chain["repo"], "rev-parse", "story/ST-0002") == merge_sha
    assert _story_worktree(chain, "ST-0002").is_dir()


def test_prepare_story_again_keeps_the_worktree_of_a_dispatching_story(chain):
    assert _dispatch(chain["repo"], chain["ledger"], "prepare-story", "ST-0002").returncode == 0
    assert _dispatch(chain["repo"], chain["ledger"], "mark-dispatching", "ST-0002").returncode == 0
    work = _story_worktree(chain, "ST-0002") / "src" / "ST-0002.txt"
    work.write_text("uncommitted agent work\n")

    result = _dispatch(chain["repo"], chain["ledger"], "prepare-story", "ST-0002")

    assert result.returncode != 0
    assert "dispatching" in result.stderr
    assert work.read_text() == "uncommitted agent work\n"
    assert _story(_ledger(chain), "ST-0002")["status"] == "dispatching"


def test_prepare_story_points_a_failed_story_to_re_dispatch(chain):
    data = _ledger(chain)
    _story(data, "ST-0002")["status"] = "failed"
    chain["ledger"].write_text(yaml.safe_dump(data))

    result = _dispatch(chain["repo"], chain["ledger"], "prepare-story", "ST-0002")

    assert result.returncode != 0
    assert "dispatch re-dispatch ST-0002" in result.stderr
    assert _git(chain["repo"], "branch", "--list", "story/ST-0002") == ""


def test_prepare_story_rolls_back_when_the_manifest_step_fails(chain):
    (chain["repo"] / "config" / "project.json").unlink()

    result = _dispatch(chain["repo"], chain["ledger"], "prepare-story", "ST-0002")

    assert result.returncode != 0
    _assert_no_story_workspace(chain, "ST-0002")
    assert _story(_ledger(chain), "ST-0002")["status"] == "pending"


# -- BUG-0087: merge-story reads touches when outputs is absent -------------


@pytest.fixture()
def touches_only(tmp_path: Path) -> dict[str, Path]:
    """ST-0001 declares only touches and waits, dispatched, in wave 1."""
    r = _repo(tmp_path, first_story=TOUCHES_ONLY_STORY)
    assert _prepare_wave_one(r).returncode == 0
    return r


def test_merge_story_scopes_a_story_by_its_touches(touches_only):
    _commit_story_work(touches_only, "ST-0001")

    result = _dispatch(touches_only["inv"], touches_only["ledger"], "merge-story", "ST-0001")

    assert result.returncode == 0, result.stdout + result.stderr
    assert _story(_ledger(touches_only), "ST-0001")["status"] == "done"


def test_merge_story_allows_the_index_yaml_a_hook_rewrites(touches_only):
    _commit_story_work(touches_only, "ST-0001", ("packages/factory/INDEX.yaml",))

    result = _dispatch(touches_only["inv"], touches_only["ledger"], "merge-story", "ST-0001")

    assert result.returncode == 0, result.stdout + result.stderr


def test_merge_story_blocks_a_file_outside_touches(touches_only):
    _commit_story_work(touches_only, "ST-0001", ("src/stray.txt",))

    result = _dispatch(touches_only["inv"], touches_only["ledger"], "merge-story", "ST-0001")

    assert result.returncode != 0
    assert "src/stray.txt" in result.stdout + result.stderr
    assert _story(_ledger(touches_only), "ST-0001")["status"] == "dispatched"
