"""Contract tests for block-dangerous-git.sh hook — dispatch-ledger gate.

The hook denies `git commit` on story/* branches when no dispatch ledger
exists in the main checkout. Non-story branches and story branches with
a ledger present are unaffected.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_SOURCE = (
    REPO_ROOT / "packages" / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
)
_INSTALLED = REPO_ROOT / "factory" / "config" / "hooks" / "block-dangerous-git.sh"
HOOK_PATH = _SOURCE if _SOURCE.exists() else _INSTALLED


def _run_hook(
    command: str, cwd: str | Path | None = None, env: dict | None = None
) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"command": command}})
    run_env = {k: v for k, v in os.environ.items()}
    run_env.pop("GIT_DIR", None)
    run_env.pop("GIT_WORK_TREE", None)
    run_env.pop("GIT_INDEX_FILE", None)
    if env:
        run_env.update(env)
    return subprocess.run(
        ["bash", str(HOOK_PATH)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=run_env,
    )


def _init_repo(path: Path, branch: str = "main") -> None:
    subprocess.run(
        ["git", "init", "-b", branch, str(path)], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "commit.gpgsign", "false"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.email", "test@test"],
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(path), "config", "user.name", "Test"],
        capture_output=True,
        check=True,
    )
    (path / "README.md").write_text("init\n")
    subprocess.run(
        ["git", "-C", str(path), "add", "."], capture_output=True, check=True
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-m", "init", "--no-verify"],
        capture_output=True,
        check=True,
    )


def _create_worktree(main: Path, branch: str, wt_path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-b", branch, str(wt_path), "HEAD"],
        capture_output=True,
        check=True,
    )


def _place_verify_base_marker(wt_path: Path) -> None:
    marker_dir = wt_path / ".current-work"
    marker_dir.mkdir(parents=True, exist_ok=True)
    head_sha = subprocess.run(
        ["git", "-C", str(wt_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    (marker_dir / "verify-base-ok").write_text(f"head={head_sha}\n")


def _place_ledger(
    main: Path,
    feature_name: str = "feature-test",
    branches: list[str] | None = None,
    mode: str = "orchestrated",
) -> Path:
    """Write a ledger whose entries name the given story branches."""
    ledger_dir = main / ".current-work" / feature_name
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger = ledger_dir / "dispatch-ledger.yaml"
    lines = ["---", f"mode: {mode}", f"feature_branch: {feature_name}"]
    if branches:
        lines.append("stories:")
    else:
        lines.append("stories: {}")
    for branch in branches or []:
        story_id = branch.rsplit("/", 1)[-1]
        lines += [
            f"  {story_id}:",
            f"    id: {story_id}",
            "    status: dispatched",
            f"    branch: {branch}",
            f"    feature_branch: {feature_name}",
        ]
    ledger.write_text("\n".join(lines) + "\n")
    return ledger


class TestLedgerGateOnStoryBranch:
    """Commits on story/* branches require a dispatch ledger in the main checkout."""

    def test_story_branch_without_ledger_is_denied(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-9999", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 2
        assert (
            "dispatch ledger" in result.stderr.lower()
            or "dispatch" in result.stderr.lower()
        )

    @pytest.mark.spec("RL-16-IT-05")
    def test_story_branch_with_ledger_is_allowed(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-9999", wt)
        _place_verify_base_marker(wt)
        _place_ledger(main, branches=["story/ST-9999"])

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 0

    def test_non_story_branch_without_ledger_is_allowed(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "feature/something", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 0

    def test_denial_message_suggests_dispatch_init(self, tmp_path):
        main = tmp_path / "main"
        wt = tmp_path / "wt"
        _init_repo(main)
        _create_worktree(main, "story/ST-0001", wt)
        _place_verify_base_marker(wt)

        result = _run_hook("git commit -m test", cwd=wt)
        assert result.returncode == 2
        assert "dispatch init" in result.stderr


class TestTestingYamlResolution:
    """resolve_testing_yaml finds docs/testing.yaml at the canonical path."""

    def test_docs_testing_yaml_allows_declared_command(self, tmp_path):
        """test_changed_command declared in docs/testing.yaml is allowed."""
        main = tmp_path / "main"
        _init_repo(main)
        testing_yaml = main / "docs" / "testing.yaml"
        testing_yaml.parent.mkdir(parents=True, exist_ok=True)
        testing_yaml.write_text('test_changed_command: "uv run pytest -q"\n')

        result = _run_hook("uv run pytest -q", cwd=main)
        assert result.returncode == 0, result.stderr

    def test_docs_testing_yaml_takes_precedence(self, tmp_path):
        """docs/testing.yaml is preferred over docs/agent-context/testing.yaml."""
        main = tmp_path / "main"
        _init_repo(main)
        canonical = main / "docs" / "testing.yaml"
        canonical.parent.mkdir(parents=True, exist_ok=True)
        canonical.write_text('test_changed_command: "uv run pytest -q"\n')
        legacy = main / "docs" / "agent-context" / "testing.yaml"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text('test_changed_command: "uv run pytest -x"\n')

        assert _run_hook("uv run pytest -q", cwd=main).returncode == 0
        assert _run_hook("uv run pytest -x", cwd=main).returncode == 2


class TestChangedFilesCommand:
    """BR-024: an agent may run test_changed_command with changed paths, and
    never test_command or test_staged_command."""

    TESTING_YAML = (
        'test_command: "uv run pytest"\n'
        'test_staged_command: "uv run pytest --tb=short"\n'
        'test_changed_command: "uv run pytest -q"\n'
    )

    def _repo(self, tmp_path: Path) -> Path:
        main = tmp_path / "main"
        _init_repo(main)
        (main / "docs").mkdir()
        (main / "docs" / "testing.yaml").write_text(self.TESTING_YAML)
        return main

    @pytest.mark.parametrize(
        "command",
        [
            "uv run pytest -q",
            "uv run pytest -q packages/factory/scripts/dispatch",
            "uv run pytest -q src/a.py docs/b-c.md tests/x_y.py",
        ],
    )
    def test_the_changed_files_command_with_paths_is_allowed(self, tmp_path, command):
        result = _run_hook(command, cwd=self._repo(tmp_path))
        assert result.returncode == 0, result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            "uv run pytest",
            "uv run pytest --tb=short",
            "uv run pytest -qq",
            "uv run pytest -q ../x.py",
            "uv run pytest -q src/a.py; rm -rf /tmp/y",
            "uv run pytest -q src/a.py && uv run pytest",
            "uv run pytest -q $(echo x)",
            "uv run pytest -q 'a b'",
            "uv run pytest -q --lf",
        ],
    )
    def test_the_full_suite_and_other_arguments_are_blocked(self, tmp_path, command):
        result = _run_hook(command, cwd=self._repo(tmp_path))
        assert result.returncode == 2


class TestScopedTestRuns:
    """BR-024: an agent may run named test files, never the whole suite."""

    @pytest.mark.parametrize(
        "command",
        [
            "uv run pytest tests/factory/test_crap_gate_score.py",
            "uv run pytest -q tests/factory/test_crap_gate_score.py",
            "uv run pytest tests/a/test_x.py tests/b/test_y.py --tb=short",
            "uv run pytest tests/factory/test_x.py::test_one",
            "uv run pytest tests/factory/test_x.py::TestA::test_b[case-1]",
            "uv run pytest -n auto -m spec tests/factory/test_x.py",
            "uv run --directory /home/u/repo/.current-work/f/story/ST-1 pytest tests/x.py",
            'grep -n "uv run pytest" docs/spec/validation-rules.md',
            'git commit -m "fix: run pytest; cargo test after cd x && uv run pytest"',
            "git commit -q -F - <<'EOF'\nfix: the gate\n\npytest tests/ now passes; npm test too\nuv run pytest\nEOF",
            "git commit -m 'docs: (uv run pytest) is blocked'",
        ],
    )
    def test_named_test_files_are_allowed(self, tmp_path, command):
        main = tmp_path / "main"
        _init_repo(main)
        result = _run_hook(command, cwd=main)
        assert result.returncode == 0, result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            "uv run pytest",
            "uv run pytest -q",
            "uv run pytest tests/",
            "uv run pytest packages/factory/scripts/x.py",
            "uv run pytest tests/x.py; rm -rf /tmp/y",
            "uv run pytest tests/x.py && git push",
            "uv run pytest tests/x.py | tee log",
            "uv run pytest tests/../etc/x.py",
            "uv run pytest -k 'a or b' tests/x.py",
            "uv run pytest tests/x.py $(echo z)",
            "cd /tmp && uv run pytest",
            "cd /tmp && uv run pytest tests/x.py",
            "cd /tmp; pytest",
            "uv run --directory /x pytest",
            "uv run --quiet pytest",
            "uv run python -m pytest",
            "FOO=1 uv run pytest",
            "(uv run pytest)",
            "echo a | python3 -m pytest -q",
            "env CI=1 pytest tests/",
            "uvx pytest",
            "cd /tmp && go test ./...",
            "true && cargo test",
            'echo "$(uv run pytest)"',
            "cat <<'EOF'\nx\nEOF\nuv run pytest",
            'git commit -m "x"; uv run pytest',
        ],
    )
    def test_the_whole_suite_and_compound_commands_stay_blocked(
        self, tmp_path, command
    ):
        main = tmp_path / "main"
        _init_repo(main)
        result = _run_hook(command, cwd=main)
        assert result.returncode == 2


class TestLedgerGateDoesNotAffectMainCheckout:
    """Commits in the main checkout (not a worktree) skip the ledger check."""

    def test_commit_in_main_checkout_without_ledger_passes(self, tmp_path):
        main = tmp_path / "main"
        _init_repo(main)
        subprocess.run(
            ["git", "-C", str(main), "checkout", "-b", "story/ST-0002"],
            capture_output=True,
            check=True,
        )

        result = _run_hook("git commit -m test", cwd=main)
        assert result.returncode == 0


class TestNextIdPasses:
    """The claim push belongs to next-id; the hook lets the script pass (CID-09-CT-01)."""

    @pytest.mark.spec("CID-09-CT-01")
    @pytest.mark.parametrize(
        "command",
        [
            "next-id ST",
            "next-id ST --remote /tmp/remote.git",
            ".agent-factory/factory/scripts/next-id ST",
        ],
    )
    def test_st_0374_next_id_command_exits_zero(self, command, tmp_path):
        main = tmp_path / "main"
        _init_repo(main)

        result = _run_hook(command, cwd=main)

        assert result.returncode == 0


class TestMoveToOriginPasses:
    """The move is a push through next-id; the hook lets the script pass (CIF-09-IT-01)."""

    @pytest.mark.spec("CIF-09-IT-01")
    @pytest.mark.parametrize(
        "command",
        [
            ".agent-factory/factory/scripts/next-id --move-to-origin",
            "next-id --move-to-origin",
        ],
    )
    def test_st_0382_move_to_origin_command_exits_zero(self, command, tmp_path):
        main = tmp_path / "main"
        _init_repo(main)

        result = _run_hook(command, cwd=main)

        assert result.returncode == 0


class TestNoVerifyForms:
    """ST-0396, FC-12-IT-03: an agent cannot skip the pre-commit hook."""

    @pytest.mark.spec("FC-12-IT-03")
    @pytest.mark.parametrize(
        "command",
        [
            "git commit -m fix " + "--no-" + "verify",
            "git commit " + "-" + "n -m fix",
            "git commit -m fix " + "-" + "n",
        ],
    )
    def test_st_0396_both_forms_are_denied(self, command):
        result = _run_hook(command)

        assert result.returncode == 2, result.stderr

    @pytest.mark.spec("FC-12-IT-03")
    @pytest.mark.parametrize(
        "command",
        [
            "grep -rn " + "--no-" + "verify packages/",
            "grep -n " + "-" + "n docs/",
        ],
    )
    def test_st_0396_a_harmless_grep_for_the_flag_passes(self, command):
        result = _run_hook(command)

        assert result.returncode == 0, result.stderr


# --- ST-0427: the two refusals of the run lifecycle and the run lookup by branch ---

RETURN_STORY = "dispatch return-story ST-0350"
CLOSE_DROP = "dispatch close --drop"
REFUSED = [RETURN_STORY, CLOSE_DROP]


@pytest.fixture
def isolated_git(tmp_path, monkeypatch):
    """An empty HOME and no system config, so no user setting reaches git."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    return tmp_path


def _run_payload(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    run_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    run_env["GIT_CONFIG_NOSYSTEM"] = "1"
    return subprocess.run(
        ["bash", str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=run_env,
    )


def _claude_code(command: str, cwd: Path) -> dict:
    return {
        "session_id": "test",
        "hook_event_name": "PreToolUse",
        "cwd": str(cwd),
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


def _codex(command: str, cwd: Path) -> dict:
    return {
        "session_id": "test",
        "hook_event_name": "PreToolUse",
        "cwd": str(cwd),
        "tool_name": "exec_command",
        "tool_input": {"cmd": command},
    }


def _copilot(command: str, cwd: Path) -> dict:
    """Copilot CLI sends toolArgs as a JSON string."""
    return {
        "timestamp": 1762500000000,
        "cwd": str(cwd),
        "toolName": "bash",
        "toolArgs": json.dumps({"command": command}),
    }


def _pi(command: str, cwd: Path) -> dict:
    """The payload that pi's block-dangerous-git.ts passes for a bash tool_call."""
    return {"toolName": "bash", "input": {"command": command}}


PAYLOADS = {"Claude Code": _claude_code, "Codex": _codex, "Copilot": _copilot, "pi": _pi}


def _assert_refused(result: subprocess.CompletedProcess, names: str) -> None:
    assert result.returncode == 2, result.stderr
    assert names in result.stderr
    assert json.loads(result.stdout)["permissionDecision"] == "deny"


def _head(path: Path, rev: str = "HEAD") -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", rev],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], capture_output=True, check=True)


class TestTheTwoCommandsAreRefusedInEverySession:
    """RL-16-IT-01: both commands are refused with or without a run."""

    @pytest.mark.spec("RL-16-IT-01")
    @pytest.mark.parametrize("command", REFUSED)
    def test_st_0427_refused_in_a_repository_without_a_ledger(self, command, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")

        _assert_refused(_run_hook(command, cwd=main), command)

    @pytest.mark.spec("RL-16-IT-01")
    @pytest.mark.parametrize("command", REFUSED)
    def test_st_0427_refused_on_dev_beside_the_ledger_of_a_run(self, command, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")
        _place_ledger(main, "feature/login", ["story/ST-0350"])

        _assert_refused(_run_hook(command, cwd=main), command)

    @pytest.mark.spec("RL-16-IT-01")
    @pytest.mark.parametrize("command", REFUSED)
    def test_st_0427_refused_in_the_worktree_of_a_story(self, command, isolated_git):
        main = isolated_git / "main"
        wt = isolated_git / "wt"
        _init_repo(main, "dev")
        _create_worktree(main, "story/ST-0350", wt)
        _place_verify_base_marker(wt)
        _place_ledger(main, "feature/login", ["story/ST-0350"])

        _assert_refused(_run_hook(command, cwd=wt), command)


class TestEveryToolPayloadReachesTheRefusal:
    """RL-16-IT-02: the payloads of Claude Code, Codex, Copilot and pi."""

    @pytest.mark.spec("RL-16-IT-02")
    @pytest.mark.parametrize("command", REFUSED)
    @pytest.mark.parametrize("tool", sorted(PAYLOADS))
    def test_st_0427_each_tool_payload_is_refused(self, tool, command, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")

        result = _run_payload(PAYLOADS[tool](command, main), main)

        _assert_refused(result, command)

    @pytest.mark.spec("RL-16-IT-02")
    @pytest.mark.parametrize("tool", sorted(PAYLOADS))
    def test_st_0427_each_tool_payload_passes_a_harmless_command(self, tool, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")

        result = _run_payload(PAYLOADS[tool]("git status", main), main)

        assert result.returncode == 0, result.stderr


class TestEveryFormIsRefused:
    """RL-16-IT-07: every form that puts dispatch at a command position (OI-11)."""

    @pytest.mark.spec("RL-16-IT-07")
    @pytest.mark.parametrize(
        ("form", "names"),
        [
            (".agent-factory/factory/scripts/dispatch return-story ST-0350", "dispatch return-story"),
            ("./.agent-factory/factory/scripts/dispatch close --drop", "dispatch close --drop"),
            ("packages/factory/scripts/dispatch close --drop", "dispatch close --drop"),
            ("git status && dispatch close --drop", "dispatch close --drop"),
            ("git status; dispatch return-story ST-0350", "dispatch return-story"),
            ('bash -c "dispatch close --drop"', "dispatch close --drop"),
            ('bash -c "git status && dispatch return-story ST-0350"', "dispatch return-story"),
            # IMPL-0021: an option of dispatch before the subcommand.
            (
                "dispatch --ledger .current-work/feature/x/dispatch-ledger.yaml return-story ST-0350",
                "dispatch return-story",
            ),
            (
                "dispatch --ledger=.current-work/feature/x/dispatch-ledger.yaml close --drop",
                "dispatch close --drop",
            ),
            # IMPL-0021: a shell word that leads the command.
            ("env dispatch return-story ST-0350", "dispatch return-story"),
            ("FOO=1 dispatch return-story ST-0350", "dispatch return-story"),
            ("{ dispatch return-story ST-0350; }", "dispatch return-story"),
            ("if true; then dispatch return-story ST-0350; fi", "dispatch return-story"),
            # IMPL-0021: an interpreter in front of dispatch.
            ("uv run .agent-factory/factory/scripts/dispatch close --drop", "dispatch close --drop"),
            (
                "python3 .agent-factory/factory/scripts/dispatch return-story ST-0350",
                "dispatch return-story",
            ),
            # IMPL-0021: a quoted word, which the shell unquotes.
            ('dispatch close "--drop"', "dispatch close --drop"),
            ('dispatch "return-story" ST-0350', "dispatch return-story"),
        ],
    )
    def test_st_0427_every_form_is_refused(self, form, names, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")

        _assert_refused(_run_hook(form, cwd=main), names)

    @pytest.mark.spec("RL-16-IT-07")
    @pytest.mark.parametrize(
        "mention",
        [
            'grep -n "dispatch return-story" docs/spec/interface-contracts.md',
            'grep -c "dispatch close --drop" docs/spec/interface-contracts.md',
            "rg 'dispatch return-story' docs/",
            'git commit -m "docs: refuse dispatch close --drop and dispatch return-story"',
            "echo dispatch return-story",
        ],
    )
    def test_st_0427_a_quoted_mention_in_another_command_passes(self, mention, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")

        result = _run_hook(mention, cwd=main)

        assert result.returncode == 0, result.stderr


class TestNoOtherDispatchCommandIsRefused:
    """RL-16-IT-03: merge-story and the other subcommands pass in both ways."""

    @pytest.mark.spec("RL-16-IT-03")
    @pytest.mark.parametrize("mode", ["by-hand", "orchestrated"])
    @pytest.mark.parametrize(
        "command",
        [
            "dispatch merge-story ST-0350",
            ".agent-factory/factory/scripts/dispatch merge-story ST-0350",
            "dispatch status",
            "dispatch close",
            "dispatch close --orphans",
        ],
    )
    def test_st_0427_other_dispatch_commands_pass(self, command, mode, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")
        _git(main, "branch", "story/ST-0350")
        _place_ledger(main, "feature/login", ["story/ST-0350"], mode=mode)
        marker = main / ".current-work" / "premerge-check-ok"
        marker.write_text(f"branch=story/ST-0350\nhead={_head(main, 'story/ST-0350')}\n")

        result = _run_hook(command, cwd=main)

        assert result.returncode == 0, result.stderr


class TestMergeNeedsAMarkerForTheCurrentHead:
    """RL-16-IT-04: the marker names the branch at its current head."""

    def _repo(self, root: Path) -> Path:
        main = root / "main"
        _init_repo(main, "dev")
        _git(main, "branch", "story/ST-0350")
        (main / ".current-work").mkdir()
        return main

    def _marker(self, main: Path, branch: str, head: str) -> None:
        (main / ".current-work" / "premerge-check-ok").write_text(
            f"branch={branch}\nhead={head}\n"
        )

    @pytest.mark.spec("RL-16-IT-04")
    def test_st_0427_marker_for_the_current_head_passes(self, isolated_git):
        main = self._repo(isolated_git)
        self._marker(main, "story/ST-0350", _head(main, "story/ST-0350"))

        result = _run_hook("git merge story/ST-0350", cwd=main)

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("RL-16-IT-04")
    def test_st_0427_marker_for_an_older_head_is_refused(self, isolated_git):
        main = self._repo(isolated_git)
        old_head = _head(main, "story/ST-0350")
        new_head = subprocess.run(
            ["git", "-C", str(main), "commit-tree", "-m", "change", "-p", old_head, "HEAD^{tree}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        _git(main, "update-ref", "refs/heads/story/ST-0350", new_head)
        self._marker(main, "story/ST-0350", old_head)

        _assert_refused(_run_hook("git merge story/ST-0350", cwd=main), "premerge-check-ok")

    @pytest.mark.spec("RL-16-IT-04")
    def test_st_0427_marker_for_another_branch_is_refused(self, isolated_git):
        main = self._repo(isolated_git)
        self._marker(main, "story/ST-0351", _head(main, "story/ST-0350"))

        _assert_refused(_run_hook("git merge story/ST-0350", cwd=main), "premerge-check-ok")


class TestTheRunIsFoundFromTheBranch:
    """RL-16-IT-05: a story branch belongs to the run whose ledger lists it."""

    @pytest.mark.spec("RL-16-IT-05")
    def test_st_0427_ledger_of_another_run_does_not_count(self, isolated_git):
        main = isolated_git / "main"
        wt = isolated_git / "wt"
        _init_repo(main, "dev")
        _create_worktree(main, "story/ST-0350", wt)
        _place_verify_base_marker(wt)
        _place_ledger(main, "feature/search", ["story/ST-0351"])

        result = _run_hook("git commit -m test", cwd=wt)

        _assert_refused(result, "story/ST-0350")
        assert "ledger" in result.stderr

    @pytest.mark.spec("RL-16-IT-05")
    def test_st_0427_ledger_that_lists_the_branch_counts(self, isolated_git):
        main = isolated_git / "main"
        wt = isolated_git / "wt"
        _init_repo(main, "dev")
        _create_worktree(main, "story/ST-0350", wt)
        _place_verify_base_marker(wt)
        _place_ledger(main, "feature/search", ["story/ST-0351"])
        _place_ledger(main, "feature/login", ["story/ST-0350"])

        result = _run_hook("git commit -m test", cwd=wt)

        assert result.returncode == 0, result.stderr


class TestALedgerOfAnotherBranchDoesNotCountOnDev:
    """RL-16-IT-06: a commit in the primary checkout on dev passes."""

    @pytest.mark.spec("RL-16-IT-06")
    def test_st_0427_commit_on_dev_passes_beside_a_ledger(self, isolated_git):
        main = isolated_git / "main"
        _init_repo(main, "dev")
        _place_ledger(main, "feature/login", ["story/ST-0350"])

        result = _run_hook("git commit -m test", cwd=main)

        assert result.returncode == 0, result.stderr
