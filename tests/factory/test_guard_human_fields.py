"""Integration tests for the hook guard-human-fields.

Each test sends one tool call to the hook on standard input, inside a
temporary git repository, and reads the exit code. A call comes in the format
of its CLI: a Claude Code or Codex PreToolUse payload, a Copilot CLI
preToolUse payload, or the payload of the Pi extension. The payloads follow
the guard contract in docs/spec/interface-contracts.md; none was recorded
from a real CLI session (FC-QG23).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT

GUARD = REPO_ROOT / "packages" / "factory" / "config" / "hooks" / "guard-human-fields"

BUG_0037 = """\
---
id: BUG-0037
source: bug-hunt
review_class: code
category: defect
type: function
severity: critical
override_by: null
override_reason: null
stop_confirmed_by: null
stop_confirmed_reason: null
artifact: .agent-factory/factory/scripts/premerge-check:120-134
status: open
owner: developer-agent
---

# premerge-check merges without the base check

**What is wrong:** The script skips the base check.

## Possible damage

- merges on `dev` from dispatch runs since the installed copy was last updated — check: compare `git log --merges dev` with the merges the dispatch log records
"""

FAGAN_0042 = """\
---
id: FAGAN-0042
source: fagan-review
review_class: code
category: defect
type: checking
severity: major
override_by: null
override_reason: null
stop_confirmed_by: null
stop_confirmed_reason: null
artifact: packages/factory/scripts/dispatch:40
status: open
owner: developer-agent
---

# dispatch reads the ledger twice

**What is wrong:** The ledger is read twice.
"""

WAIVED = """\
---
id: FAGAN-0043
source: fagan-review
review_class: code
category: defect
type: checking
severity: major
override_by: stakeholder
override_reason: accepted for this release
stop_confirmed_by: null
stop_confirmed_reason: null
artifact: packages/factory/scripts/dispatch:41
status: waived
owner: developer-agent
---

# dispatch logs teh wrong path

**What is wrong:** The log line names the wrong path.
"""

FAGAN_0032 = {
    "id": "FAGAN-0032",
    "source": "fagan-review",
    "review_class": "code",
    "category": "defect",
    "type": "documentation",
    "severity": "minor",
    "artifact": "packages/factory/scripts/dispatch:12",
    "story": "ST-0370",
    "finding": "The docstring names an old flag.",
    "basis": {"in_use": True, "harms_downstream": False, "fails_purpose": False, "raises_cost": True},
    "why_this_severity": "A reader can still act (no to fails_purpose).",
    "commit": "d0a78a5c40327c1f7e4c9a204ab5e766a7e0c44b",
    "status": "open",
}

PROPOSAL = """\
# Review loop cap

## Design

The Status column of a review table holds `open` or `waived`.

# Appendix

## Review findings

| ID  | Pass | Severity | Check   | Status | Finding                     | Resolution |
| --- | ---- | -------- | ------- | ------ | --------------------------- | ---------- |
| R1  | 1    | major    | clarity | open   | The cap is unclear. Severity: fails_purpose. |            |
| R2  | 1    | minor    | wording | fixed  | A typo. Severity: raises_cost. | Fixed.   |
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A git repository with BUG-0037, FAGAN-0042, a waived finding, the
    register file FAGAN-0032, and a proposal with an Appendix table."""
    root = tmp_path / "project"
    findings = root / "docs" / "findings"
    (findings / "register" / "code").mkdir(parents=True)
    (findings / "BUG-0037.md").write_text(BUG_0037)
    (findings / "FAGAN-0042.md").write_text(FAGAN_0042)
    (findings / "FAGAN-0043.md").write_text(WAIVED)
    (findings / "register" / "code" / "FAGAN-0032.json").write_text(
        json.dumps(FAGAN_0032, indent=2) + "\n"
    )
    (root / "docs" / "proposals").mkdir(parents=True)
    (root / "docs" / "proposals" / "review-loop-cap.md").write_text(PROPOSAL)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    return root


def run_guard(project: Path, tool_name: str, tool_input: dict) -> subprocess.CompletedProcess:
    payload = {
        "session_id": "test",
        "hook_event_name": "PreToolUse",
        "cwd": str(project),
        "tool_name": tool_name,
        "tool_input": tool_input,
    }
    return subprocess.run(
        [str(GUARD)],
        input=json.dumps(payload),
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def path_of(project: Path, rel: str) -> str:
    return str(project / rel)


class TestEditRefused:
    @pytest.mark.spec("FC-18-IT-01")
    def test_st_0400_edit_that_sets_stop_confirmed_by_is_refused(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/BUG-0037.md"),
            "old_string": "stop_confirmed_by: null",
            "new_string": "stop_confirmed_by: human",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/BUG-0037.md" in result.stderr
        assert "stop_confirmed_by" in result.stderr
        assert "stakeholder" in result.stderr
        assert "editor" in result.stderr
        assert "`!` command" in result.stderr


class TestBashRefused:
    @pytest.mark.spec("FC-18-IT-02")
    def test_st_0400_sed_that_sets_status_waived_is_refused(self, project):
        result = run_guard(project, "Bash", {
            "command": "sed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr
        assert "status" in result.stderr

    @pytest.mark.spec("FC-18-IT-03")
    def test_st_0400_sed_that_writes_waived_into_a_proposal_row_is_refused(self, project):
        result = run_guard(project, "Bash", {
            "command": "sed -i 's/| R1  | 1    | major    | clarity | open   |"
            "/| R1  | 1    | major    | clarity | waived |/' docs/proposals/review-loop-cap.md",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/proposals/review-loop-cap.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-03")
    def test_st_0400_edit_that_writes_waived_into_a_proposal_row_is_refused(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/proposals/review-loop-cap.md"),
            "old_string": "| clarity | open   |",
            "new_string": "| clarity | waived |",
        })

        assert result.returncode == 2, result.stderr
        assert "Status" in result.stderr


    @pytest.mark.spec("FC-18-IT-02")
    @pytest.mark.parametrize("command", [
        "git status\nsed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md",
        "printf 'stop_confirmed_by: human\\n' | tee -a docs/findings/BUG-0037.md",
        "echo 'override_by: human' >> docs/findings/BUG-0037.md",
        (
            "python3 -c \"import pathlib; p = pathlib.Path('docs/findings/BUG-0037.md'); "
            "p.write_text(p.read_text().replace('override_by: null', 'override_by: human'))\""
        ),
        "bash -c \"sed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md\"",
    ])
    def test_st_0400_other_shell_writes_that_set_a_field_are_refused(self, project, command):
        result = run_guard(project, "Bash", {"command": command})

        assert result.returncode == 2, result.stderr


class TestShellFormsRefused:
    """IMPL-0015: a heredoc script, a keyword, or a wrapper does not hide the write."""

    SED = "sed -i 's/status: open/status: waived/' docs/findings/IMPL-0004.md"

    @pytest.mark.spec("FC-18-IT-02")
    @pytest.mark.parametrize("command", [
        (
            "python3 - <<'PY'\n"
            "open('docs/findings/IMPL-0004.md','w').write('status: waived')\n"
            "PY"
        ),
        f"bash <<'EOF'\n{SED}\nEOF",
        f"if true; then {SED}; fi",
        f"{{ {SED}; }}",
        f"env X=1 {SED}",
        f"cat <<< 'x'\n{SED}",
        f"command {SED}",
        f"sudo {SED}",
        f"time {SED}",
        f"for f in a; do {SED}; done",
        f"! {SED}",
    ], ids=[
        "python-heredoc", "bash-heredoc", "then", "brace", "env",
        "here-string", "command", "sudo", "time", "do", "bang",
    ])
    def test_impl_0015_hidden_shell_write_is_refused(self, project, command):
        result = run_guard(project, "Bash", {"command": command})

        assert result.returncode == 2, result.stderr
        assert "docs/findings/IMPL-0004.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_impl_0015_python_heredoc_that_writes_a_fixture_passes(self, project):
        command = (
            "python3 - <<'PY'\n"
            "open('tests/fixtures/waived.md','w').write('status: waived')\n"
            "PY"
        )

        result = run_guard(project, "Bash", {"command": command})

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_impl_0015_here_string_to_read_only_command_passes(self, project):
        result = run_guard(project, "Bash", {"command": "grep waived <<< 'status: waived'"})

        assert result.returncode == 0, result.stderr


class TestWriteRefused:
    @pytest.mark.spec("FC-18-IT-04")
    def test_st_0400_write_of_an_existing_finding_that_confirms_the_stop_is_refused(self, project):
        content = BUG_0037.replace("stop_confirmed_by: null", "stop_confirmed_by: human")

        result = run_guard(project, "Write", {
            "file_path": path_of(project, "docs/findings/BUG-0037.md"),
            "content": content,
        })

        assert result.returncode == 2, result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-04")
    def test_st_0400_write_of_a_new_finding_that_sets_override_by_is_refused(self, project):
        content = FAGAN_0042.replace("FAGAN-0042", "FAGAN-0044").replace(
            "override_by: null", "override_by: human"
        )

        result = run_guard(project, "Write", {
            "file_path": path_of(project, "docs/findings/FAGAN-0044.md"),
            "content": content,
        })

        assert result.returncode == 2, result.stderr
        assert "override_by" in result.stderr


class TestLegitimateCallsPass:
    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_write_of_a_new_finding_from_the_template_passes(self, project):
        content = FAGAN_0042.replace("FAGAN-0042", "FAGAN-0045")

        result = run_guard(project, "Write", {
            "file_path": path_of(project, "docs/findings/FAGAN-0045.md"),
            "content": content,
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_typo_fix_in_a_waived_finding_passes(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/FAGAN-0043.md"),
            "old_string": "# dispatch logs teh wrong path",
            "new_string": "# dispatch logs the wrong path",
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_typo_fix_that_quotes_the_waived_status_line_passes(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/FAGAN-0043.md"),
            "old_string": "status: waived\nowner: developer-agent\n---\n\n# dispatch logs teh",
            "new_string": "status: waived\nowner: developer-agent\n---\n\n# dispatch logs the",
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_edit_of_the_finding_template_passes(self, project):
        template = project / "packages" / "factory" / "rulebooks" / "templates" / "finding.md"
        template.parent.mkdir(parents=True)
        template.write_text("status: open\nstop_confirmed_by: null\n")

        result = run_guard(project, "Edit", {
            "file_path": str(template),
            "old_string": "stop_confirmed_by: null",
            "new_string": "stop_confirmed_by: human",
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_read_only_grep_passes(self, project):
        result = run_guard(project, "Bash", {
            "command": 'grep "status: waived" docs/findings/*.md',
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_heredoc_that_writes_a_fixture_under_tests_passes(self, project):
        command = (
            "mkdir -p tests/fixtures/waived/docs/findings && "
            "cat > tests/fixtures/waived/docs/findings/FAGAN-0099.md <<'EOF'\n"
            "---\nid: FAGAN-0099\noverride_by: human\nstatus: waived\n---\n"
            "EOF"
        )

        result = run_guard(project, "Bash", {"command": command})

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-05")
    def test_st_0400_bug_fix_playbook_sed_that_resolves_a_finding_passes(self, project):
        result = run_guard(project, "Bash", {
            "command": "sed -i 's/status: open/status: resolved/' docs/findings/FAGAN-0042.md",
        })

        assert result.returncode == 0, result.stderr


class TestRegisterFile:
    @pytest.mark.spec("FC-18-IT-11")
    def test_st_0400_edit_that_adds_override_by_to_a_register_file_is_refused(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/register/code/FAGAN-0032.json"),
            "old_string": '"status": "open"',
            "new_string": '"status": "open",\n  "override_by": "human"',
        })

        assert result.returncode == 2, result.stderr
        assert "override_by" in result.stderr
        assert "docs/findings/register/code/FAGAN-0032.json" in result.stderr

    @pytest.mark.spec("FC-18-IT-11")
    def test_st_0400_write_of_a_new_register_file_without_override_keys_passes(self, project):
        content = json.dumps({**FAGAN_0032, "id": "FAGAN-0050"}, indent=2) + "\n"

        result = run_guard(project, "Write", {
            "file_path": path_of(project, "docs/findings/register/code/FAGAN-0050.json"),
            "content": content,
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-11")
    def test_st_0400_edit_of_the_finding_text_beside_an_existing_override_passes(self, project):
        register = project / "docs" / "findings" / "register" / "code" / "FAGAN-0032.json"
        register.write_text(json.dumps(
            {**FAGAN_0032, "override_by": "stakeholder", "override_reason": "lowered"}, indent=2
        ) + "\n")

        result = run_guard(project, "Edit", {
            "file_path": str(register),
            "old_string": "The docstring names an old flag.",
            "new_string": "The docstring names the old flag --force.",
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-12")
    def test_st_0400_edit_that_sets_status_waived_in_a_register_file_is_refused(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/register/code/FAGAN-0032.json"),
            "old_string": '"status": "open"',
            "new_string": '"status": "waived"',
        })

        assert result.returncode == 2, result.stderr
        assert "status" in result.stderr

    @pytest.mark.spec("FC-18-IT-12")
    def test_st_0400_edit_that_sets_status_resolved_in_a_register_file_passes(self, project):
        result = run_guard(project, "Edit", {
            "file_path": path_of(project, "docs/findings/register/code/FAGAN-0032.json"),
            "old_string": '"status": "open"',
            "new_string": '"status": "resolved"',
        })

        assert result.returncode == 0, result.stderr


class TestMultiEditAndNotebookEdit:
    @pytest.mark.spec("FC-18-IT-14")
    def test_st_0400_multiedit_whose_second_edit_sets_a_field_is_refused(self, project):
        result = run_guard(project, "MultiEdit", {
            "file_path": path_of(project, "docs/findings/BUG-0037.md"),
            "edits": [
                {"old_string": "skips the base check", "new_string": "skips the base-SHA check"},
                {"old_string": "stop_confirmed_by: null", "new_string": "stop_confirmed_by: human"},
            ],
        })

        assert result.returncode == 2, result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-14")
    def test_st_0400_multiedit_that_fixes_two_typos_in_a_waived_finding_passes(self, project):
        result = run_guard(project, "MultiEdit", {
            "file_path": path_of(project, "docs/findings/FAGAN-0043.md"),
            "edits": [
                {"old_string": "logs teh wrong", "new_string": "logs the wrong"},
                {"old_string": "names the wrong path.", "new_string": "names a wrong path."},
            ],
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-14")
    def test_st_0400_notebookedit_outside_the_guarded_paths_passes(self, project):
        result = run_guard(project, "NotebookEdit", {
            "notebook_path": path_of(project, "notebooks/analysis.ipynb"),
            "cell_id": "cell-1",
            "new_source": "status = 'waived'\noverride_by: human",
            "edit_mode": "replace",
        })

        assert result.returncode == 0, result.stderr


def run_payload(project: Path, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(GUARD)],
        input=json.dumps(payload),
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def codex_patch(project: Path, patch: str) -> subprocess.CompletedProcess:
    """A Codex PreToolUse payload of an apply_patch call."""
    return run_payload(project, {
        "session_id": "test",
        "hook_event_name": "PreToolUse",
        "cwd": str(project),
        "tool_name": "apply_patch",
        "tool_input": {"command": patch},
    })


def copilot_call(project: Path, tool_name: str, tool_args: dict) -> subprocess.CompletedProcess:
    """A Copilot CLI preToolUse payload; toolArgs arrives as a JSON string."""
    return run_payload(project, {
        "timestamp": 1762500000000,
        "cwd": str(project),
        "toolName": tool_name,
        "toolArgs": json.dumps(tool_args),
    })


def copilot_patch(project: Path, patch: str) -> subprocess.CompletedProcess:
    return copilot_call(project, "apply_patch", {"patch": patch})


def pi_patch(project: Path, patch: str) -> subprocess.CompletedProcess:
    """The payload the Pi extension passes for an apply_patch tool_call event."""
    return run_payload(project, {
        "cwd": str(project),
        "toolName": "apply_patch",
        "input": {"patch": patch},
    })


class TestCodexApplyPatch:
    @pytest.mark.spec("FC-18-IT-09")
    def test_st_0401_patch_that_adds_stop_confirmed_by_is_refused(self, project):
        result = codex_patch(project, """\
*** Begin Patch
*** Update File: docs/findings/BUG-0037.md
@@
 override_reason: null
-stop_confirmed_by: null
+stop_confirmed_by: human
 stop_confirmed_reason: null
*** End Patch
""")

        assert result.returncode == 2, result.stderr
        assert "docs/findings/BUG-0037.md" in result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-09")
    def test_st_0401_patch_that_fixes_a_typo_in_a_waived_finding_passes(self, project):
        result = codex_patch(project, """\
*** Begin Patch
*** Update File: docs/findings/FAGAN-0043.md
@@
-# dispatch logs teh wrong path
+# dispatch logs the wrong path
*** End Patch
""")

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-09")
    def test_st_0401_patch_whose_second_file_sets_a_field_is_refused(self, project):
        result = codex_patch(project, """\
*** Begin Patch
*** Add File: notes/todo.md
+Check the base SHA.
*** Update File: docs/findings/FAGAN-0042.md
@@
-status: open
+status: waived
*** End Patch
""")

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-09")
    def test_st_0401_patch_that_adds_a_waived_finding_file_is_refused(self, project):
        result = codex_patch(project, """\
*** Begin Patch
*** Add File: docs/findings/FAGAN-0050.md
+---
+id: FAGAN-0050
+status: waived
+---
*** End Patch
""")

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0050.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-09")
    def test_st_0401_patch_and_shell_call_as_argument_lists_are_refused(self, project):
        patch = "*** Begin Patch\n*** Update File: docs/findings/FAGAN-0042.md\n" \
                "@@\n-status: open\n+status: waived\n*** End Patch\n"
        shell = "sed -i 's/status: open/status: waived/' docs/findings/FAGAN-0042.md"

        for tool_name, command in (("apply_patch", ["apply_patch", patch]),
                                   ("Bash", ["bash", "-lc", shell])):
            result = run_payload(project, {
                "cwd": str(project),
                "tool_name": tool_name,
                "tool_input": {"command": command},
            })

            assert result.returncode == 2, (tool_name, result.stderr)


class TestCopilotCalls:
    @pytest.mark.spec("FC-18-IT-10")
    def test_st_0401_edit_that_sets_status_waived_is_refused(self, project):
        result = copilot_call(project, "edit", {
            "path": path_of(project, "docs/findings/FAGAN-0042.md"),
            "old_str": "status: open",
            "new_str": "status: waived",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr
        assert "status" in result.stderr

    @pytest.mark.spec("FC-18-IT-10")
    def test_st_0401_write_file_that_sets_status_waived_is_refused(self, project):
        result = copilot_call(project, "write_file", {
            "path": path_of(project, "docs/findings/FAGAN-0042.md"),
            "content": FAGAN_0042.replace("status: open", "status: waived"),
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-10")
    @pytest.mark.parametrize("tool_name, tool_args", [
        ("edit", {"old_str": "status: open", "new_str": "status: waived"}),
        ("write_file", {"content": "status: waived\n"}),
    ])
    def test_st_0401_same_calls_on_the_finding_template_pass(self, project, tool_name, tool_args):
        template = project / "packages" / "factory" / "rulebooks" / "templates" / "finding.md"
        template.parent.mkdir(parents=True)
        template.write_text("status: open\n")

        result = copilot_call(project, tool_name, {"path": str(template), **tool_args})

        assert result.returncode == 0, result.stderr


UNPARSABLE_PATCH = """\
*** Begin Patch
*** Update File: docs/findings/FAGAN-0042.md
status: open
=> status: waived
"""


class TestUnparsablePatch:
    @pytest.mark.spec("FC-18-IT-13")
    @pytest.mark.parametrize("send", [codex_patch, copilot_patch, pi_patch],
                             ids=["codex", "copilot", "pi"])
    def test_st_0401_unparsable_patch_that_names_a_guarded_path_is_refused(self, project, send):
        result = send(project, UNPARSABLE_PATCH)

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-13")
    @pytest.mark.parametrize("send", [codex_patch, copilot_patch, pi_patch],
                             ids=["codex", "copilot", "pi"])
    def test_st_0401_unparsable_patch_that_names_no_guarded_path_passes(self, project, send):
        patch = UNPARSABLE_PATCH.replace("docs/findings/FAGAN-0042.md", "notes/todo.md")

        result = send(project, patch)

        assert result.returncode == 0, result.stderr


def opencode_call(project: Path, tool_name: str, args: dict) -> subprocess.CompletedProcess:
    """The payload the guard-only OpenCode plugin hands to the guard (ST-0403)."""
    return run_payload(project, {
        "cwd": str(project),
        "toolName": tool_name,
        "input": args,
    })


class TestOpenCodeCalls:
    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_edit_that_sets_stop_confirmed_by_is_refused(self, project):
        result = opencode_call(project, "edit", {
            "filePath": path_of(project, "docs/findings/BUG-0037.md"),
            "oldString": "stop_confirmed_by: null",
            "newString": "stop_confirmed_by: human",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/BUG-0037.md" in result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_write_that_sets_stop_confirmed_by_is_refused(self, project):
        result = opencode_call(project, "write", {
            "filePath": path_of(project, "docs/findings/BUG-0037.md"),
            "content": BUG_0037.replace("stop_confirmed_by: null", "stop_confirmed_by: human"),
        })

        assert result.returncode == 2, result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_patch_that_sets_stop_confirmed_by_is_refused(self, project):
        result = opencode_call(project, "patch", {"patchText": """\
*** Begin Patch
*** Update File: docs/findings/BUG-0037.md
@@
 override_reason: null
-stop_confirmed_by: null
+stop_confirmed_by: human
 stop_confirmed_reason: null
*** End Patch
"""})

        assert result.returncode == 2, result.stderr
        assert "docs/findings/BUG-0037.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_shell_that_sets_stop_confirmed_by_is_refused(self, project):
        result = opencode_call(project, "shell", {
            "command": "sed -i 's/stop_confirmed_by: null/stop_confirmed_by: human/' "
            "docs/findings/BUG-0037.md",
        })

        assert result.returncode == 2, result.stderr
        assert "stop_confirmed_by" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_execute_with_javascript_that_writes_a_human_field_is_refused(self, project):
        result = opencode_call(project, "execute", {
            "code": "await Bun.write('docs/findings/BUG-0037.md', 'stop_confirmed_by: human\\n')",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/BUG-0037.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_execute_with_javascript_outside_the_guarded_paths_passes(self, project):
        result = opencode_call(project, "execute", {
            "code": "await Bun.write('notes/todo.md', 'stop_confirmed_by: human\\n')",
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_unparsable_patch_that_names_a_guarded_path_is_refused(self, project):
        result = opencode_call(project, "patch", {"patchText": UNPARSABLE_PATCH})

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_unparsable_patch_that_names_no_guarded_path_passes(self, project):
        result = opencode_call(project, "patch", {
            "patchText": UNPARSABLE_PATCH.replace("docs/findings/FAGAN-0042.md", "notes/todo.md"),
        })

        assert result.returncode == 0, result.stderr

    @pytest.mark.spec("FC-18-IT-17")
    def test_st_0403_edit_that_sets_no_human_field_passes(self, project):
        result = opencode_call(project, "edit", {
            "filePath": path_of(project, "docs/findings/BUG-0037.md"),
            "oldString": "The script skips the base check.",
            "newString": "The script skips the base check on dev.",
        })

        assert result.returncode == 0, result.stderr


class TestShellChangesDirectory:
    """BUG-0120: the guard follows a literal `cd` of the command line."""

    def test_bug_0120_cd_before_sed_into_a_finding_is_refused(self, project):
        result = run_guard(project, "Bash", {
            "command": "cd docs && sed -i 's/status: open/status: waived/' findings/FAGAN-0042.md",
        })

        assert result.returncode == 2, result.stderr
        assert "docs/findings/FAGAN-0042.md" in result.stderr

    def test_bug_0120_cd_before_sed_outside_the_guarded_paths_passes(self, project):
        (project / "docs" / "notes.md").write_text("status: open\n")

        result = run_guard(project, "Bash", {
            "command": "cd docs && sed -i 's/status: open/status: waived/' notes.md",
        })

        assert result.returncode == 0, result.stderr

    def test_bug_0120_cd_inside_a_subshell_ends_with_the_subshell(self, project):
        result = run_guard(project, "Bash", {
            "command": "(cd notes) && sed -i 's/status: open/status: waived/' "
            "docs/findings/FAGAN-0042.md",
        })

        assert result.returncode == 2, result.stderr


class TestHelp:
    def test_st_0400_help_names_the_blind_spot(self):
        result = subprocess.run([str(GUARD), "--help"], capture_output=True, text=True, check=False)

        assert result.returncode == 0
        assert "DEC-42" in result.stdout
        assert "hides the field name" in result.stdout
