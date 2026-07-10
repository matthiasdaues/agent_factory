"""Copilot CLI adapter — the first concrete CLIAdapter (FR-C2).

Non-interactive invocation (resolves T-01):
    copilot -p "<prompt>" --allow-all-tools --no-color --log-level none [-C <cwd>]

`--allow-all-tools` is required for non-interactive mode; without it copilot
prompts for permission and would hang a headless run.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..ports import InvocationResult

# copilot signals an unauthenticated / unavailable session on stderr; used to
# set auth_error so the core halts (BR-018) rather than looping the author.
# NOTE (ATAM-R03/T-13): stderr matching is a fallback, not a first-class
# signal. If copilot reworded these messages the flags would silently flip to
# loop-instead-of-halt, so the pinning tests in test_copilot_adapter.py assert
# the current wording and must fail loudly on drift.
_AUTH_RE = re.compile(
    r"(not logged in|please log ?in|log ?in to|authenticat|unauthorized|\b401\b)",
    re.IGNORECASE,
)

# Operator-fixable, deterministically-repeating failures (bad model id, unknown
# flag/option). Looping the author on these just burns the cap (ATAM-R01/T-11),
# so they set config_error and the core halts instead.
_CONFIG_RE = re.compile(
    r"(from --\S+ flag is not available|not available|unknown option|"
    r"invalid (model|value|argument)|unrecognized)",
    re.IGNORECASE,
)


class CopilotAdapter:
    """Runs GitHub Copilot CLI in a fresh subprocess per invocation (ADR-0002)."""

    def __init__(
        self,
        binary: str = "copilot",
        model: str | None = None,
        interactive: bool = False,
    ) -> None:
        self.binary = binary
        self.model = model
        self.interactive = interactive

    def _command(self, prompt: str, model: str | None = None) -> list[str]:
        effective_model = model if model is not None else self.model
        cmd = [
            self.binary,
            "-p",
            prompt,
            "--allow-all-tools",
            "--no-color",
            "--log-level",
            "none",
        ]
        if effective_model:
            cmd += ["--model", effective_model]
        return cmd

    def invoke(
        self, prompt: str, cwd: Path, timeout_s: int, model: str | None = None
    ) -> InvocationResult:
        effective_model = model if model is not None else self.model
        if self.interactive:
            return self._invoke_interactive(prompt, cwd, timeout_s, effective_model)
        cmd = self._command(prompt, effective_model)
        return self._invoke_captured(cmd, cwd, timeout_s)

    def _interactive_command(self, model: str | None = None) -> list[str]:
        """Build command for interactive mode — no -p flag, agent reads instruction file."""
        cmd = [
            self.binary,
            "--allow-all-tools",
        ]
        if model:
            cmd += ["--model", model]
        return cmd

    def _invoke_interactive(
        self, prompt: str, cwd: Path, timeout_s: int, model: str | None = None
    ) -> InvocationResult:
        cmd = self._interactive_command(model)
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                timeout=timeout_s,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.TimeoutExpired:
            return InvocationResult(
                exit_code=124,
                stdout="",
                stderr="",
                timed_out=True,
                auth_error=False,
                config_error=False,
            )
        stderr = proc.stderr or ""
        failed = proc.returncode != 0
        auth_error = failed and bool(_AUTH_RE.search(stderr))
        config_error = failed and not auth_error and bool(_CONFIG_RE.search(stderr))
        return InvocationResult(
            exit_code=proc.returncode,
            stdout="",
            stderr=stderr,
            timed_out=False,
            auth_error=auth_error,
            config_error=config_error,
        )

    def _invoke_captured(
        self, cmd: list[str], cwd: Path, timeout_s: int
    ) -> InvocationResult:
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            return InvocationResult(
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
                auth_error=False,
            )
        failed = proc.returncode != 0
        stderr = proc.stderr or ""
        auth_error = failed and bool(_AUTH_RE.search(stderr))
        # auth takes precedence; a config error is a non-auth, deterministic failure.
        config_error = failed and not auth_error and bool(_CONFIG_RE.search(stderr))
        return InvocationResult(
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            timed_out=False,
            auth_error=auth_error,
            config_error=config_error,
        )
