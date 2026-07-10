"""Unit + smoke tests for the Copilot adapter.

Unit tests fake subprocess.run — deterministic, no network. The live smoke
test hits the real copilot CLI and is skipped unless RUN_LIVE=1.
"""

from __future__ import annotations

import os
import subprocess

import pytest

from orchestrator.adapters.copilot import CopilotAdapter
from orchestrator.ports import CLIAdapter, InvocationResult


class _FakeCompleted:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_adapter_satisfies_port():
    assert isinstance(CopilotAdapter(), CLIAdapter)


def test_command_is_non_interactive():
    cmd = CopilotAdapter()._command("say hi")
    assert cmd[0] == "copilot"
    assert "-p" in cmd and "say hi" in cmd
    # required for headless mode, else copilot prompts and hangs
    assert "--allow-all-tools" in cmd


def test_model_flag_added_when_set():
    assert "--model" not in CopilotAdapter()._command("x")
    cmd = CopilotAdapter(model="auto")._command("x")
    assert cmd[cmd.index("--model") + 1] == "auto"


def test_command_forces_clean_session():
    # ATAM-R11/T-? isolation: never resume a persisted session.
    cmd = CopilotAdapter()._command("x")
    assert not {"--continue", "--resume", "-r", "-c"} & set(cmd)


def test_success_maps_to_result(monkeypatch, tmp_path):
    def fake_run(cmd, **kw):
        assert kw["cwd"] == str(tmp_path)
        assert kw["timeout"] == 30
        return _FakeCompleted(0, stdout="PONG\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter().invoke("ping", tmp_path, 30)
    assert isinstance(r, InvocationResult)
    assert (r.exit_code, r.timed_out, r.auth_error) == (0, False, False)
    assert "PONG" in r.stdout


def test_timeout_maps_to_timed_out(monkeypatch, tmp_path):
    def fake_run(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, kw["timeout"], output="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter().invoke("hang", tmp_path, 5)
    assert r.timed_out and r.exit_code == 124 and not r.auth_error


def test_auth_failure_detected(monkeypatch, tmp_path):
    # ATAM-R03/T-13 drift-pin: this exact wording must keep mapping to auth_error.
    def fake_run(cmd, **kw):
        return _FakeCompleted(1, stderr="Error: not logged in. Run `copilot login`.")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter().invoke("x", tmp_path, 30)
    assert r.exit_code == 1 and r.auth_error and not r.config_error


def test_config_error_detected(monkeypatch, tmp_path):
    # ATAM-R01/T-11: bad --model id is operator-fixable -> halt, not loop.
    def fake_run(cmd, **kw):
        return _FakeCompleted(
            1, stderr='Error: Model "x" from --model flag is not available.'
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(model="x").invoke("x", tmp_path, 30)
    assert r.config_error and not r.auth_error


def test_auth_takes_precedence_over_config(monkeypatch, tmp_path):
    def fake_run(cmd, **kw):
        return _FakeCompleted(1, stderr="not logged in; model not available")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter().invoke("x", tmp_path, 30)
    assert r.auth_error and not r.config_error


def test_generic_failure_is_neither_auth_nor_config(monkeypatch, tmp_path):
    # An author-fixable failure loops; it must set neither halt flag.
    def fake_run(cmd, **kw):
        return _FakeCompleted(2, stderr="some other failure")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter().invoke("x", tmp_path, 30)
    assert r.exit_code == 2 and not r.auth_error and not r.config_error


# --- Interactive mode ---


def test_interactive_inherits_stdio(monkeypatch, tmp_path):
    """Interactive mode must NOT capture output — let the user interact.
    No -p flag: copilot enters live chat, agent reads instruction file."""
    captured_cmd = []
    captured_kwargs = {}

    def fake_run(cmd, **kw):
        captured_cmd.extend(cmd)
        captured_kwargs.update(kw)
        return _FakeCompleted(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("x", tmp_path, 30)
    assert (
        "capture_output" not in captured_kwargs or not captured_kwargs["capture_output"]
    )
    assert "-p" not in captured_cmd
    assert "--no-color" not in captured_cmd
    assert "--allow-all-tools" in captured_cmd
    assert r.exit_code == 0
    assert not r.timed_out


def test_interactive_omits_prompt_flag(monkeypatch, tmp_path):
    """Interactive mode drops -p: prompt delivered via instruction file, not CLI arg."""
    captured_cmd = []

    def fake_run(cmd, **kw):
        captured_cmd.extend(cmd)
        return _FakeCompleted(0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("initial context", tmp_path, 30)
    assert "-p" not in captured_cmd
    assert "initial context" not in captured_cmd
    assert r.exit_code == 0


def test_interactive_timeout_still_works(monkeypatch, tmp_path):
    """Interactive mode still respects the timeout."""

    def fake_run(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, kw["timeout"], output="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("hang", tmp_path, 5)
    assert r.timed_out and r.exit_code == 124


def test_interactive_captures_stderr(monkeypatch, tmp_path):
    """FAGAN-0036: Interactive mode captures stderr for auth/config classification."""

    def fake_run(cmd, **kw):
        return _FakeCompleted(0, stdout="ignored", stderr="some output")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = CopilotAdapter(interactive=True).invoke("x", tmp_path, 30)
    assert r.stdout == ""
    assert r.stderr == "some output"
    assert not r.auth_error and not r.config_error


def test_per_call_model_overrides_constructor(monkeypatch, tmp_path):
    """FAGAN-0001: per-call model from resolver overrides adapter default."""
    captured_cmd = []

    def fake_run(cmd, **kw):
        captured_cmd.extend(cmd)
        return _FakeCompleted(0, stdout="ok")

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = CopilotAdapter(model="default-model")
    adapter.invoke("x", tmp_path, 30, model="per-call-model")
    assert "--model" in captured_cmd
    idx = captured_cmd.index("--model")
    assert captured_cmd[idx + 1] == "per-call-model"


def test_per_call_model_none_uses_constructor(monkeypatch, tmp_path):
    """When per-call model is None, adapter constructor model is used."""
    captured_cmd = []

    def fake_run(cmd, **kw):
        captured_cmd.extend(cmd)
        return _FakeCompleted(0, stdout="ok")

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = CopilotAdapter(model="constructor-model")
    adapter.invoke("x", tmp_path, 30, model=None)
    assert "--model" in captured_cmd
    idx = captured_cmd.index("--model")
    assert captured_cmd[idx + 1] == "constructor-model"


@pytest.mark.live
@pytest.mark.skipif(
    os.environ.get("RUN_LIVE") != "1", reason="set RUN_LIVE=1 to hit copilot"
)
def test_live_smoke(tmp_path):
    r = CopilotAdapter().invoke(
        "Reply with exactly the single word: PONG", tmp_path, timeout_s=120
    )
    assert not r.timed_out, "copilot timed out"
    assert not r.auth_error, f"auth error: {r.stderr[:200]}"
    assert r.exit_code == 0, f"exit {r.exit_code}: {r.stderr[:200]}"
    assert "PONG" in r.stdout.upper(), f"unexpected stdout: {r.stdout[:200]}"
