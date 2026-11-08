"""finding-lint reads git (ST-0392, FC-10-IT-02; ST-0393, FC-11).

Each test builds its own repository in tmp_path. The ST-0392 tests commit the
findings and then change, stage, or remove them; the lint compares the working
tree, or the index with --staged, with HEAD (BR-109, BR-110). The ST-0393
tests commit a script on main and dev and change it on a feature branch; the
lint checks in_use against the line identities of git blame (BR-088). The
ST-0395 tests commit a finding first and check when the git check is due, and
which version of the artifact it blames.
"""

from __future__ import annotations

import json
import subprocess

import pytest
from test_finding_lint import (
    BUG_PATH,
    CONFIRMED,
    FAGAN_PATH,
    OVERRIDE,
    PLAYBOOK,
    REGISTER_PATH,
    _bar,
    _clean_set,
    _commit,
    _critical_fields,
    _finding_fields,
    _finding_text,
    _git,
    _major_bug,
    _matrix,
    _register,
    _register_path,
    _repo,
    _run_in,
    _tree,
    _write,
)

HEAD_RULES = pytest.mark.spec("FC-10-IT-02")


@pytest.fixture
def committed(tmp_path):
    """A repository whose HEAD holds the Demo Data of ST-0391."""
    root, env = _repo(tmp_path)
    _clean_set(root)
    _commit(root, env)
    return root, env


def _lower_fagan(root) -> None:
    _write(root, FAGAN_PATH, _finding_text(_finding_fields(severity="minor")))


@HEAD_RULES
def test_st_0392_a_lowering_in_the_working_tree_fails_without_staged(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout


@HEAD_RULES
def test_st_0392_an_unstaged_lowering_is_not_seen_with_staged(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


@HEAD_RULES
def test_st_0392_a_staged_lowering_fails_with_staged(committed):
    root, env = committed
    _lower_fagan(root)
    _git(root, env, "add", FAGAN_PATH)
    _write(root, FAGAN_PATH, _finding_text(_finding_fields()))
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout
    assert _run_in(root, env).returncode == 0


@HEAD_RULES
@pytest.mark.parametrize(
    ("override", "code"), [({}, 1), (OVERRIDE, 0)], ids=["no-keys", "keys"]
)
def test_st_0392_a_staged_move_of_fagan_0042_into_the_register(
    committed, override, code
):
    root, env = committed
    _git(root, env, "rm", "-q", FAGAN_PATH)
    _write(
        root,
        _register_path(name="FAGAN-0042"),
        _register(id="FAGAN-0042", **override),
    )
    _git(root, env, "add", "docs/findings/register")
    result = _run_in(root, env, "--staged")
    assert result.returncode == code, result.stdout
    if code:
        assert f"{FAGAN_PATH}: BR-109 removal" in result.stdout
        assert "FAGAN-0042" in result.stdout


@HEAD_RULES
def test_st_0392_a_staged_removal_of_a_register_file_fails(committed):
    root, env = committed
    _git(root, env, "rm", "-q", REGISTER_PATH)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{REGISTER_PATH}: BR-110 removal" in result.stdout
    assert "FAGAN-0032" in result.stdout


@HEAD_RULES
def test_st_0392_the_staged_migration_of_bug_0067_passes(tmp_path):
    root, env = _repo(tmp_path)
    _write(
        root,
        "docs/findings/BUG-0067.md",
        "---\nid: BUG-0067\nseverity: Minor\nstatus: open\n---\n",
    )
    _commit(root, env)
    _git(root, env, "rm", "-q", "docs/findings/BUG-0067.md")
    _write(root, _register_path(name="BUG-0067"), _register(id="BUG-0067"))
    _git(root, env, "add", "docs/findings/register")
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


@HEAD_RULES
def test_st_0392_a_critical_lowering_passes_once_head_holds_the_confirmation(
    tmp_path,
):
    root, env = _repo(tmp_path)
    _write(root, BUG_PATH, _finding_text(_critical_fields(), damage=True))
    _commit(root, env)
    _write(root, BUG_PATH, _finding_text(_major_bug(**OVERRIDE)))
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{BUG_PATH}: BR-109 lowering" in result.stdout

    _write(root, BUG_PATH, _finding_text(_critical_fields(**CONFIRMED), damage=True))
    _commit(root, env, "confirm the stop")
    _write(root, BUG_PATH, _finding_text(_major_bug(**OVERRIDE)))
    result = _run_in(root, env)
    assert (result.returncode, result.stdout) == (0, "")


@HEAD_RULES
def test_st_0392_a_repository_without_a_commit_checks_every_file_as_new(tmp_path):
    root, env = _repo(tmp_path)
    _clean_set(root)
    assert _run_in(root, env).returncode == 0
    _git(root, env, "add", "-A")
    result = _run_in(root, env, "--staged")
    assert (result.returncode, result.stdout) == (0, "")


@HEAD_RULES
def test_st_0392_staged_outside_a_repository_exits_2(tmp_path):
    root = tmp_path / "plain"
    root.mkdir()
    _clean_set(root)
    _, env = _repo(tmp_path)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 2
    assert "finding-lint" in result.stderr


@HEAD_RULES
def test_st_0392_a_failed_git_call_exits_2(committed):
    root, env = committed
    blob = subprocess.run(
        ["git", "rev-parse", f"HEAD:{FAGAN_PATH}"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (root / ".git" / "objects" / blob[:2] / blob[2:]).unlink()
    result = _run_in(root, env)
    assert result.returncode == 2
    assert "finding-lint" in result.stderr


@HEAD_RULES
def test_st_0392_the_demo_scenario_of_the_story(committed):
    root, env = committed
    _lower_fagan(root)
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout

    _git(root, env, "add", FAGAN_PATH)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1
    assert f"{FAGAN_PATH}: BR-109 lowering" in result.stdout

    _git(root, env, "checkout", "HEAD", "--", FAGAN_PATH)
    (root / REGISTER_PATH).unlink()
    _write(
        root,
        "docs/findings/FAGAN-0032.md",
        _finding_text(_finding_fields(id="FAGAN-0032")),
    )
    result = _run_in(root, env)
    assert (result.returncode, result.stdout) == (0, "")


# --- The git check for in use (ST-0393) ---------------------------------------

SCRIPT = "packages/factory/scripts/premerge-check"
DISPATCH = "packages/factory/scripts/dispatch"
PLAYBOOK_PATH = "packages/factory/playbooks/feature-addition.md"
INSTALLED = ".agent-factory/factory/scripts/premerge-check"
SETTINGS = "docs/factory-settings.yaml"
ON_DEV = f"{FAGAN_PATH}: BR-088 in use: artifact lines exist unchanged on dev"
IN_USE_FALSE = {
    "document": _tree(False, False, True, False),
    "code": _tree(False, False, True, False),
    "runtime": _tree(False, False, True, False),
    "security": _bar("execution", 1, "proven", False),
    "architecture": _matrix("high", "fails"),
}


def _script(inserted: int = 0) -> str:
    """The script of the Demo Data: the defect at lines 100 to 114 on dev."""
    lines = [f"setup step {number} of the gate" for number in range(1, 100)]
    lines += [f"inserted check {number} above the defect" for number in range(inserted)]
    lines += [f"defect line {number} accepts an empty story" for number in range(15)]
    lines += [f"tail step {number} of the gate" for number in range(26)]
    return "\n".join(lines) + "\n"


def _dispatch() -> str:
    return "".join(
        f"dispatch line {number} merges a wave\n" for number in range(1, 1601)
    )


def _file_finding(root, review_class: str, artifact: str, **overrides) -> None:
    fields = _finding_fields(
        review_class, basis=dict(IN_USE_FALSE[review_class]), artifact=artifact
    )
    fields.update(overrides)
    _write(root, FAGAN_PATH, _finding_text(fields))
    if not (root / SETTINGS).exists():
        _write(root, SETTINGS, "release_tag_patterns: []\n")


def _base(tmp_path):
    """Commit the script, dispatch, and the playbook on main, and branch dev off."""
    root, env = _repo(tmp_path)
    _write(root, ".gitignore", "/.agent-factory/\n")
    _write(root, SCRIPT, _script())
    _write(root, DISPATCH, _dispatch())
    _write(root, PLAYBOOK_PATH, PLAYBOOK)
    _commit(root, env, "the gate")
    _git(root, env, "branch", "dev")
    return root, env


def _feature(root, env, start: str = "main") -> None:
    """Branch feature/demo off *start* and insert 20 lines above the defect."""
    _git(root, env, "checkout", "-q", "-b", "feature/demo", start)
    _write(root, SCRIPT, _script(inserted=20))
    _commit(root, env, "insert 20 checks")


@pytest.fixture
def demo(tmp_path):
    """The Demo Data of ST-0393 without the installed copy."""
    root, env = _base(tmp_path)
    _feature(root, env)
    return root, env


def _install(root, text: str | None = None) -> None:
    """Write the untracked installed copy, by default of the checked-out script."""
    _write(root, INSTALLED, (root / SCRIPT).read_text() if text is None else text)


def _violations(result) -> list[str]:
    """Return the output lines that are not a skipped branch."""
    return [
        line for line in result.stdout.splitlines() if not line.startswith("skipped ")
    ]


def _assert_found(result, where: str) -> None:
    assert result.returncode == 1, result.stdout + result.stderr
    message = f"{FAGAN_PATH}: BR-088 in use: artifact lines exist unchanged {where}"
    assert _violations(result) == [message]


def _assert_passes(result) -> None:
    assert result.returncode == 0, result.stdout + result.stderr
    assert (_violations(result), result.stderr) == ([], "")


@pytest.mark.spec("FC-11-IT-01")
def test_st_0393_a_code_finding_on_lines_unchanged_on_dev_fails(demo):
    root, env = demo
    _file_finding(root, "code", f"{DISPATCH}:1383-1390")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-01")
def test_st_0393_a_range_with_one_line_the_story_changed_passes(demo):
    root, env = demo
    _file_finding(root, "code", f"{SCRIPT}:119-134")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-02")
def test_st_0393_a_security_finding_on_lines_unchanged_on_dev_fails(demo):
    root, env = demo
    _file_finding(root, "security", f"{SCRIPT}:120-134")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-03")
def test_st_0393_a_runtime_finding_on_dispatch_1588_fails(demo):
    root, env = demo
    _file_finding(root, "runtime", f"{DISPATCH}:1588")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-04")
def test_st_0393_lines_unchanged_in_the_installed_copy_fail(demo):
    root, env = demo
    _file_finding(root, "code", f"{SCRIPT}:100-119")
    _assert_passes(_run_in(root, env))
    _install(root)
    _assert_found(_run_in(root, env), "in the installed copy")


@pytest.mark.spec("FC-11-IT-05")
def test_st_0393_shifted_lines_match_their_identity_on_dev(demo):
    root, env = demo
    assert (root / SCRIPT).read_text().splitlines()[119] == (
        "defect line 0 accepts an empty story"
    )
    _file_finding(root, "code", f"{SCRIPT}:120-134")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-06")
def test_st_0393_lines_moved_to_another_file_are_found_in_their_old_file(tmp_path):
    root, env = _repo(tmp_path)
    lines = [f"dispatch step {number} merges the wave" for number in range(1, 31)]
    _write(root, DISPATCH, "\n".join(lines) + "\n")
    _commit(root, env, "dispatch")
    _git(root, env, "branch", "dev")
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    _write(root, DISPATCH, "\n".join(lines[:5]) + "\n")
    _write(
        root, "packages/factory/scripts/dispatch_lib.py", "\n".join(lines[5:]) + "\n"
    )
    _commit(root, env, "move the merge steps")
    _file_finding(root, "code", "packages/factory/scripts/dispatch_lib.py:2-10")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-07")
def test_st_0393_lines_introduced_under_a_renamed_path_are_found(tmp_path):
    root, env = _repo(tmp_path)
    _write(root, "factory/scripts/dispatch", _dispatch())
    _commit(root, env, "dispatch")
    (root / "packages").mkdir()
    _git(root, env, "mv", "factory", "packages/factory")
    _commit(root, env, "move the factory")
    _git(root, env, "branch", "dev")
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    blame = subprocess.run(
        ["git", "blame", "-M", "-C", "--porcelain", "-L", "5,5", "dev", "--", DISPATCH],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "filename factory/scripts/dispatch" in blame.splitlines()
    _file_finding(root, "code", f"{DISPATCH}:5-10")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-08")
def test_st_0393_installed_lines_that_git_has_no_record_of_do_not_count(demo):
    root, env = demo
    with (root / SCRIPT).open("a") as script:
        script.write("an uncommitted check\n")
    _install(root)
    _file_finding(root, "code", f"{SCRIPT}:161")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-09")
@pytest.mark.parametrize(("line", "code"), [(12, 1), (23, 0)], ids=["dev", "new"])
def test_st_0393_a_single_brace_matches_only_the_same_line(tmp_path, line, code):
    root, env = _repo(tmp_path)
    braces = "packages/factory/scripts/braces.js"
    text = ""
    for number in range(10):
        text += f"function step{number}() {{\n}}\n"
        _write(root, braces, text)
        _commit(root, env, f"step {number}")
    _git(root, env, "branch", "dev")
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    _write(root, braces, text + "function review() {\n  return 1;\n}\n")
    _commit(root, env, "review")
    assert (root / braces).read_text().splitlines()[line - 1] == "}"
    blame = subprocess.run(
        ["git", "blame", "-M", "-C", "--porcelain", "-L", "23,23", "--", braces],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "summary review" in blame
    _file_finding(root, "code", f"{braces}:{line}")
    result = _run_in(root, env)
    assert result.returncode == code, result.stdout


@pytest.mark.spec("FC-11-IT-10")
def test_st_0393_in_use_true_passes_without_a_match(demo):
    root, env = demo
    why = "**Why this severity:** The orchestrator project already reads the checks, and the gate fails its purpose."
    fields = _finding_fields(
        "code", basis=_tree(True, False, True, False), artifact=f"{SCRIPT}:100-119"
    )
    _write(root, FAGAN_PATH, _finding_text(fields, why=why))
    _write(root, SETTINGS, "release_tag_patterns: []\n")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-11")
def test_st_0393_a_consumer_project_skips_the_installed_copy(tmp_path):
    root, env = _repo(tmp_path)
    _write(root, ".gitignore", "/.agent-factory/\n")
    _write(root, "src/app.py", "def main():\n    return 0\n")
    _commit(root, env, "app")
    _git(root, env, "branch", "dev")
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    _write(
        root,
        "src/app.py",
        "def main():\n    return 0\n\n\ndef review():\n    return 1\n",
    )
    _commit(root, env, "review")
    _write(root, ".agent-factory/factory/src/app.py", (root / "src/app.py").read_text())
    _file_finding(root, "code", "src/app.py:5-6")
    _assert_passes(_run_in(root, env))
    _file_finding(root, "code", "src/app.py:1-2")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-19")
@pytest.mark.parametrize("review_class", ["document", "architecture"])
def test_st_0393_document_and_architecture_findings_skip_the_git_check(
    demo, review_class
):
    root, env = demo
    _file_finding(root, review_class, f"{SCRIPT}:120-134")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-20")
def test_st_0393_a_linked_worktree_finds_the_installed_copy_of_the_main_checkout(
    tmp_path,
):
    root, env = _base(tmp_path)
    _feature(root, env)
    feature_script = (root / SCRIPT).read_text()
    _git(root, env, "checkout", "-q", "main")
    _install(root, feature_script)
    worktree = tmp_path / "story"
    _git(root, env, "worktree", "add", "-q", str(worktree), "feature/demo")
    assert not (worktree / ".agent-factory").exists()
    _file_finding(worktree, "code", f"{SCRIPT}:100-119")
    _assert_found(_run_in(worktree, env), "in the installed copy")


@pytest.mark.spec("FC-11-IT-22")
@pytest.mark.parametrize(
    ("changed", "code"),
    [("Review it.", 1), ("Check it.", 0), ("Update the spec.", 0)],
    ids=["after-the-section", "nested-heading", "section"],
)
def test_st_0393_a_heading_artifact_is_checked_as_its_section(demo, changed, code):
    root, env = demo
    _write(root, PLAYBOOK_PATH, PLAYBOOK.replace(changed, changed + " Again."))
    _commit(root, env, "change the playbook")
    _file_finding(root, "code", f"{PLAYBOOK_PATH}#step-11--update-specification")
    result = _run_in(root, env)
    assert result.returncode == code, result.stdout
    if code:
        _assert_found(result, "on dev")


@pytest.mark.spec("FC-11-IT-23")
def test_st_0393_lines_on_origin_dev_count_when_dev_lags_behind(tmp_path):
    root, env = _base(tmp_path)
    _feature(root, env, "dev")
    _git(root, env, "update-ref", "refs/remotes/origin/dev", "feature/demo")
    _git(root, env, "checkout", "-q", "-b", "feature/next")
    _file_finding(root, "code", f"{SCRIPT}:100-119")
    _assert_found(_run_in(root, env), "on origin/dev")


@pytest.mark.spec("FC-11-IT-24")
def test_st_0393_a_branch_the_clone_lacks_is_skipped_and_named(tmp_path):
    root, env = _base(tmp_path)
    _git(root, env, "branch", "-q", "-D", "dev")
    _git(root, env, "branch", "-q", "-m", "main", "dev")
    _feature(root, env, "dev")
    _file_finding(root, "code", f"{SCRIPT}:100-119")
    result = _run_in(root, env)
    assert result.returncode == 0, result.stdout
    assert result.stdout.splitlines() == [
        "skipped main: no such branch",
        "skipped origin/dev: no such branch",
        "skipped origin/main: no such branch",
    ]


@pytest.mark.spec("FC-11-IT-25")
@pytest.mark.parametrize(
    ("places", "where"),
    [
        (("dev", "main", "installed"), "on dev"),
        (("main", "installed"), "on main"),
        (("origin/main", "installed"), "on origin/main"),
    ],
)
def test_st_0393_the_message_names_the_first_place(tmp_path, places, where):
    root, env = _base(tmp_path)
    _git(root, env, "branch", "-q", "-f", "dev", "main")
    _feature(root, env)
    _git(
        root,
        env,
        "branch",
        "-q",
        "-f",
        "dev",
        "main" if "dev" not in places else "feature/demo",
    )
    if "main" in places:
        _git(root, env, "branch", "-q", "-f", "main", "feature/demo")
    if "origin/main" in places:
        _git(root, env, "update-ref", "refs/remotes/origin/main", "feature/demo")
    _git(root, env, "checkout", "-q", "-b", "feature/next")
    if "installed" in places:
        _install(root)
    _file_finding(root, "code", f"{SCRIPT}:100-119")
    _assert_found(_run_in(root, env), where)


@pytest.mark.spec("FC-11-IT-05")
def test_st_0393_the_demo_scenario_of_the_story(demo):
    root, env = demo
    _install(root, _script())
    _file_finding(root, "code", f"{SCRIPT}:120-134")
    result = _run_in(root, env)
    assert result.returncode == 1
    assert ON_DEV in result.stdout

    _file_finding(root, "document", f"{SCRIPT}:120-134")
    _assert_passes(_run_in(root, env))

    _file_finding(root, "code", f"{SCRIPT}:120-134")
    _commit(root, env, "file the finding")
    _git(root, env, "checkout", "-q", "main")
    worktree = root.parent / "story"
    _git(root, env, "worktree", "add", "-q", str(worktree), "feature/demo")
    _file_finding(worktree, "code", f"{SCRIPT}:100-119")
    assert not (worktree / ".agent-factory").exists()
    _install(root, (worktree / SCRIPT).read_text())
    _assert_found(_run_in(worktree, env), "in the installed copy")


# --- The release tags and the setting (ST-0394) --------------------------------

MISSING_KEY = (
    "docs/factory-settings.yaml: key release_tag_patterns is missing. Add the "
    "list of git tag patterns that count as releases, such as "
    '["v[0-9]*"], or [] for none.'
)
V_PATTERN = 'release_tag_patterns: ["v[0-9]*"]\n'
RELEASE_LINES = f"{SCRIPT}:100-119"


def _tagged(tmp_path, tag: str):
    """The Demo Data of ST-0393 plus *tag* on the commit that introduced the lines.

    The 20 inserted checks exist on the feature branch and at the tag only,
    because dev and main do not hold them.
    """
    root, env = _base(tmp_path)
    _feature(root, env)
    _git(root, env, "tag", tag)
    with (root / SCRIPT).open("a") as script:
        script.write("a later step\n")
    _commit(root, env, "a later step")
    return root, env


@pytest.mark.spec("FC-11-IT-12")
@pytest.mark.parametrize(
    ("tag", "code"),
    [("v1.0.0", 1), ("v1.1.0-rc", 1), ("1.1.0", 0), ("orchestrator-v0.1.0", 0)],
)
def test_st_0394_only_a_tag_that_matches_a_pattern_counts(tmp_path, tag, code):
    root, env = _tagged(tmp_path, tag)
    _file_finding(root, "code", RELEASE_LINES)
    _write(root, SETTINGS, V_PATTERN)
    result = _run_in(root, env)
    if code:
        _assert_found(result, f"at tag {tag}")
    else:
        _assert_passes(result)


@pytest.mark.spec("FC-11-IT-12")
def test_st_0394_a_block_list_counts_the_same_tags(tmp_path):
    root, env = _tagged(tmp_path, "v1.0.0")
    _file_finding(root, "code", RELEASE_LINES)
    _write(root, SETTINGS, 'release_tag_patterns:\n  - "v[0-9]*"\n')
    _assert_found(_run_in(root, env), "at tag v1.0.0")


@pytest.mark.spec("FC-11-IT-13")
@pytest.mark.parametrize(
    "settings", [None, "other_key: 1\n"], ids=["no-file", "no-key"]
)
def test_st_0394_a_due_git_check_fails_closed_without_the_setting(
    tmp_path, settings
):
    root, env = _tagged(tmp_path, "v1.0.0")
    _file_finding(root, "code", RELEASE_LINES)
    (root / SETTINGS).unlink()
    if settings:
        _write(root, SETTINGS, settings)
    result = _run_in(root, env)
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [MISSING_KEY]


@pytest.mark.spec("FC-11-IT-13")
def test_st_0394_a_value_that_is_no_list_of_strings_fails_naming_file_and_key(
    tmp_path,
):
    root, env = _tagged(tmp_path, "v1.0.0")
    _file_finding(root, "code", RELEASE_LINES)
    _write(root, SETTINGS, "release_tag_patterns: 3\n")
    result = _run_in(root, env)
    assert result.returncode == 1
    assert result.stdout.startswith("docs/factory-settings.yaml: key release_tag_patterns")


@pytest.mark.spec("FC-11-IT-14")
def test_st_0394_an_empty_list_counts_no_tag_but_branches_still_count(tmp_path):
    root, env = _tagged(tmp_path, "v1.0.0")
    _file_finding(root, "code", RELEASE_LINES)
    _write(root, SETTINGS, "release_tag_patterns: []\n")
    _assert_passes(_run_in(root, env))
    _file_finding(root, "code", f"{SCRIPT}:1-20")
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-15")
def test_st_0394_a_document_finding_needs_no_setting(tmp_path):
    root, env = _tagged(tmp_path, "v1.0.0")
    _file_finding(root, "document", RELEASE_LINES)
    (root / SETTINGS).unlink()
    result = _run_in(root, env)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
    assert not (root / SETTINGS).exists()


# --- When the git check is due (ST-0395) ---------------------------------------

NEW_LINES = f"{SCRIPT}:100-119"
OLD_LINES = f"{DISPATCH}:1383-1390"
CHANGED_BASIS = {"basis": _tree(False, False, True, True)}
NEW_REGISTER = _register_path(name="FAGAN-0050")
OLD_REGISTER = "docs/findings/register/code.jsonl"
MOVED_ARTIFACT = f"{DISPATCH}:1384-1390"
REGISTERED = {"basis": _tree(False, False, False, True), "artifact": OLD_LINES}
REGISTER_ON_DEV = (
    f"{REGISTER_PATH}: BR-088 in use: artifact lines exist unchanged on dev"
)


def _assert_no_check_ran(result) -> None:
    """Exit 0 and no output: a due check would print the branches the clone lacks."""
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def _assert_register_on_dev(result) -> None:
    assert result.returncode == 1, result.stdout + result.stderr
    assert _violations(result) == [REGISTER_ON_DEV]


def _settings(root) -> None:
    if not (root / SETTINGS).exists():
        _write(root, SETTINGS, "release_tag_patterns: []\n")


def _merge_into_dev(root, env) -> None:
    _git(root, env, "checkout", "-q", "dev")
    _git(root, env, "merge", "-q", "--no-edit", "feature/demo")


@pytest.fixture
def filed(demo):
    """The demo repository whose HEAD holds FAGAN-0042 on lines unchanged on dev."""
    root, env = demo
    _file_finding(root, "code", OLD_LINES)
    _commit(root, env, "file the finding")
    return root, env


@pytest.mark.spec("FC-11-IT-16")
def test_st_0395_a_waived_finding_whose_branch_merged_into_dev_passes(demo):
    root, env = demo
    _file_finding(root, "code", NEW_LINES)
    _commit(root, env, "file the finding")
    _merge_into_dev(root, env)
    _file_finding(root, "code", NEW_LINES, status="waived", **OVERRIDE)
    _assert_no_check_ran(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-17")
def test_st_0395_a_new_uncommitted_finding_gets_the_check_without_staged(demo):
    root, env = demo
    _file_finding(root, "code", OLD_LINES)
    _assert_found(_run_in(root, env), "on dev")
    _assert_no_check_ran(_run_in(root, env, "--staged"))


@pytest.mark.spec("FC-11-IT-18")
def test_st_0395_a_staged_basis_gets_the_check_while_the_working_tree_equals_head(
    filed,
):
    root, env = filed
    _file_finding(root, "code", OLD_LINES, **CHANGED_BASIS)
    _git(root, env, "add", FAGAN_PATH)
    _file_finding(root, "code", OLD_LINES)
    _assert_found(_run_in(root, env, "--staged"), "on dev")
    _assert_no_check_ran(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-18")
def test_st_0395_a_basis_change_that_is_not_staged_gets_no_check_with_staged(filed):
    root, env = filed
    _file_finding(root, "code", OLD_LINES, **CHANGED_BASIS)
    _assert_no_check_ran(_run_in(root, env, "--staged"))
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-18")
def test_st_0395_a_changed_artifact_gets_the_check(filed):
    root, env = filed
    _file_finding(root, "code", MOVED_ARTIFACT)
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-26")
def test_st_0395_a_new_register_file_gets_the_check(demo):
    root, env = demo
    _settings(root)
    _write(root, NEW_REGISTER, _register(id="FAGAN-0050", **REGISTERED))
    result = _run_in(root, env)
    assert result.returncode == 1, result.stdout + result.stderr
    assert _violations(result) == [
        f"{NEW_REGISTER}: BR-088 in use: artifact lines exist unchanged on dev"
    ]


@pytest.fixture
def registered(demo):
    """The demo repository whose HEAD holds FAGAN-0032 as a register file."""
    root, env = demo
    _settings(root)
    _write(root, REGISTER_PATH, _register(**REGISTERED))
    _commit(root, env, "register the finding")
    return root, env


@pytest.mark.spec("FC-11-IT-27")
def test_st_0395_a_committed_register_file_with_a_new_status_gets_no_check(registered):
    root, env = registered
    _write(root, REGISTER_PATH, _register(status="resolved", **REGISTERED))
    _git(root, env, "add", REGISTER_PATH)
    _assert_no_check_ran(_run_in(root, env, "--staged"))


@pytest.mark.spec("FC-11-IT-27")
def test_st_0395_a_committed_register_file_with_a_new_basis_gets_the_check(registered):
    root, env = registered
    _write(
        root,
        REGISTER_PATH,
        _register(artifact=OLD_LINES, basis=_tree(False, False, False, False)),
    )
    _git(root, env, "add", REGISTER_PATH)
    result = _run_in(root, env, "--staged")
    assert result.returncode == 1, result.stdout + result.stderr
    assert REGISTER_ON_DEV in result.stdout


def _old_register(root, env) -> None:
    """Commit the line of FAGAN-0032 in the old register, as the Demo Data holds it."""
    _settings(root)
    _write(root, OLD_REGISTER, json.dumps(_register(**REGISTERED)) + "\n")
    _commit(root, env, "the old register")


def _stage_move(root, env, **overrides) -> None:
    """Stage the removal of the old register and the register file of FAGAN-0032."""
    _git(root, env, "rm", "-q", OLD_REGISTER)
    data = _register(**{**REGISTERED, **overrides})
    _write(root, REGISTER_PATH, json.dumps(dict(reversed(list(data.items())))))
    _git(root, env, "add", REGISTER_PATH)


@pytest.mark.spec("FC-20-IT-02")
def test_st_0395_a_moved_line_keeps_its_earlier_check(demo):
    root, env = demo
    _old_register(root, env)
    _stage_move(root, env)
    _assert_no_check_ran(_run_in(root, env, "--staged"))


@pytest.mark.spec("FC-20-IT-02")
def test_st_0395_a_moved_line_with_a_changed_artifact_gets_the_check(demo):
    root, env = demo
    _old_register(root, env)
    _stage_move(root, env, artifact=MOVED_ARTIFACT)
    _assert_register_on_dev(_run_in(root, env, "--staged"))


@pytest.mark.spec("FC-20-IT-02")
def test_st_0395_the_demo_scenario_of_the_story(demo):
    root, env = demo
    _write(root, SETTINGS, V_PATTERN)
    _file_finding(root, "code", NEW_LINES)
    _commit(root, env, "file the finding")
    _merge_into_dev(root, env)
    _file_finding(root, "code", NEW_LINES, status="waived", **OVERRIDE)
    _assert_no_check_ran(_run_in(root, env))
    _commit(root, env, "waive the finding")

    other = "docs/findings/FAGAN-0043.md"
    fields = _finding_fields(
        "code", id="FAGAN-0043", basis=dict(IN_USE_FALSE["code"]), artifact=OLD_LINES
    )
    _write(root, other, _finding_text(fields))
    result = _run_in(root, env)
    assert result.returncode == 1
    assert f"{other}: BR-088 in use: artifact lines exist unchanged on dev" in (
        result.stdout
    )
    (root / other).unlink()

    _old_register(root, env)
    _stage_move(root, env)
    _assert_no_check_ran(_run_in(root, env, "--staged"))
    _commit(root, env, "move the line")
    _git(root, env, "checkout", "-q", "HEAD~1", "--", OLD_REGISTER)
    _git(root, env, "rm", "-q", "-f", REGISTER_PATH)
    _commit(root, env, "restore the line")
    _stage_move(root, env, artifact=MOVED_ARTIFACT)
    _assert_register_on_dev(_run_in(root, env, "--staged"))


# --- The version the git check blames with --staged (BUG-0121) -----------------


def _edit_line(root, line: int, text: str) -> None:
    lines = (root / SCRIPT).read_text().splitlines()
    lines[line - 1] = text
    (root / SCRIPT).write_text("\n".join(lines) + "\n")


@pytest.fixture
def staged_finding(tmp_path):
    """A branch that leaves the script as on dev, with a staged finding on its lines."""
    root, env = _base(tmp_path)
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    _file_finding(root, "code", f"{SCRIPT}:10-20")
    _git(root, env, "add", FAGAN_PATH, SETTINGS)
    return root, env


@pytest.mark.spec("FC-11-IT-18")
def test_bug_0121_an_unstaged_edit_does_not_hide_lines_unchanged_in_the_index(
    staged_finding,
):
    root, env = staged_finding
    _edit_line(root, 15, "an unstaged edit inside the range")
    _assert_found(_run_in(root, env, "--staged"), "on dev")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-18")
def test_bug_0121_an_unstaged_revert_causes_no_false_rejection(staged_finding):
    root, env = staged_finding
    original = (root / SCRIPT).read_text()
    _edit_line(root, 15, "a staged edit inside the range")
    _git(root, env, "add", SCRIPT)
    (root / SCRIPT).write_text(original)
    _assert_passes(_run_in(root, env, "--staged"))
    _assert_found(_run_in(root, env), "on dev")


@pytest.mark.spec("FC-11-IT-18")
def test_bug_0121_the_range_comes_from_the_index(staged_finding):
    root, env = staged_finding
    lines = (root / SCRIPT).read_text().splitlines()
    (root / SCRIPT).write_text("\n".join(lines[:5]) + "\n")
    _assert_found(_run_in(root, env, "--staged"), "on dev")
    _assert_passes(_run_in(root, env))


@pytest.mark.spec("FC-11-IT-18")
def test_bug_0121_a_rename_counts_from_the_index_when_the_file_is_gone(tmp_path):
    root, env = _repo(tmp_path)
    _write(root, "factory/scripts/dispatch", _dispatch())
    _commit(root, env, "dispatch")
    _git(root, env, "branch", "dev")
    _git(root, env, "checkout", "-q", "-b", "feature/demo")
    (root / "packages").mkdir()
    _git(root, env, "mv", "factory", "packages/factory")
    _commit(root, env, "move the factory")
    _file_finding(root, "code", f"{DISPATCH}:5-10")
    _git(root, env, "add", FAGAN_PATH, SETTINGS)
    (root / DISPATCH).unlink()
    _assert_found(_run_in(root, env, "--staged"), "on dev")
    _assert_passes(_run_in(root, env))
