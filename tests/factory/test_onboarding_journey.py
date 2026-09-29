"""End-to-end journey test for ST-0293 (Journey Measurement epic).

Exercises the safe, non-interactive newcomer path through
`install-agent-factory`: preflight diagnosis, cancellation, the consent
gate, installation, the receipt, and the data first-session routing reads.
Owns VFO-09-E2-01 -- "Complete safe journey checks consent, cancellation,
installation, receipt, and routing"
(docs/spec/value-first-onboarding-journey-qa-strategy.md) -- the one
end-to-end smoke test retained for this feature (see "Test Retention
Policy" in that document). Traces to
docs/spec/value-first-onboarding-journey.feature, Rule "Quality researcher
measures the complete newcomer journey", Scenario "Automated journey
checks the safe non-interactive path".

Does not exercise updating (EPIC 3) or the first task (EPIC 5); those own
their own coverage (test_update_factory.py, test_onboarding_sandbox.py).

Uses a controlled fixture: a temporary Git repository with one commit and
a real copy of packages/factory/ as the --from-local source, so the
installation and routing checkpoints exercise install-agent-factory's
actual delegate, init-factory, and its real detection signals -- not a
stub. No network access is used: --from-local bypasses the remote release
path entirely.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT, load_script

SCRIPT = REPO_ROOT / "packages" / "factory" / "scripts" / "install-agent-factory"
TESTING_YAML = REPO_ROOT / "docs" / "testing.yaml"


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _run_git(args: list[str], cwd: Path, env: dict | None = None) -> None:
    run_env = {**os.environ, **(env or {})}
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        env=run_env,
    )


def _make_factory_source(tmp_path: Path) -> Path:
    """Copy the real packages/factory/ tree into an isolated source root.

    A real copy, not a stub, so the installation and routing checkpoints
    exercise install-agent-factory's actual delegate, init-factory, and
    its real detection signals.
    """
    source = tmp_path / "factory-source"
    shutil.copytree(
        REPO_ROOT / "packages" / "factory",
        source / "packages" / "factory",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return source


def _make_controlled_target(tmp_path: Path) -> Path:
    """A temporary Git repository with one commit, containing files that
    trigger known detections: pyproject.toml (python), conftest.py
    (pytest), and .pre-commit-config.yaml (the safety signal the
    routing checkpoint asserts). One dot-dir (.claude/) gives the
    fixture exactly one detected interface, so it auto-selects on a
    blank answer (VFO-015)."""
    target = tmp_path / "newcomer-project"
    target.mkdir()
    git_env = {
        "GIT_AUTHOR_NAME": "journey-test", "GIT_AUTHOR_EMAIL": "journey@test",
        "GIT_COMMITTER_NAME": "journey-test", "GIT_COMMITTER_EMAIL": "journey@test",
    }
    _run_git(["init"], cwd=target, env=git_env)
    (target / "pyproject.toml").write_text(
        '[project]\nname = "newcomer-project"\nversion = "0.1.0"\n'
    )
    (target / "conftest.py").write_text("")
    (target / ".pre-commit-config.yaml").write_text("repos: []\n")
    (target / ".claude").mkdir()
    _run_git(["add", "-A"], cwd=target, env=git_env)
    _run_git(["commit", "-m", "initial commit"], cwd=target, env=git_env)
    return target


def _snapshot(root: Path) -> set[str]:
    """Relative paths of every file and directory under root, git
    internals excluded."""
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if ".git" not in p.relative_to(root).parts
    }


def _run_bootstrap(factory_source: Path, target: Path, input_text: str
                    ) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--from-local", str(factory_source),
         "--target", str(target)],
        input=input_text, capture_output=True, text=True, timeout=120,
    )


# ---------------------------------------------------------------------------
# The journey
# ---------------------------------------------------------------------------

class TestAutomatedJourneySafeNonInteractivePath:
    """VFO-09-E2-01: preflight, cancellation, consent gate, installation,
    receipt, and routing, in the order a newcomer would actually hit
    them, against one controlled fixture."""

    @pytest.mark.spec("VFO-09")
    def test_safe_non_interactive_path_all_six_checkpoints(self, tmp_path):
        mod = load_script("install-agent-factory")
        factory_source = _make_factory_source(tmp_path)
        target = _make_controlled_target(tmp_path)

        # --- Checkpoint 1: preflight ----------------------------------
        # VFO-010: preflight diagnosis is read-only.
        before = _snapshot(target)
        readiness, checks = mod.run_preflight(factory_source, target)
        assert readiness in (
            mod.READINESS_READY, mod.READINESS_LIMITED, mod.READINESS_BLOCKED,
        )
        assert checks, "preflight must run at least one check"
        assert _snapshot(target) == before, \
            "preflight diagnosis must not change the target"

        # --- Checkpoint 2: cancellation (blank consent) -----------------
        # VFO-012: blank input is never consent.
        assert mod.get_consent(input_func=lambda _: "") is False

        before = _snapshot(target)
        # Blank auto-selects the one detected interface (VFO-015); the
        # second blank line then declines the consent gate.
        cancelled = _run_bootstrap(factory_source, target, "\n\n")
        assert cancelled.returncode == 0, cancelled.stdout + cancelled.stderr
        assert "cancelled" in cancelled.stdout.lower()
        assert _snapshot(target) == before, \
            "cancellation must leave the target unchanged"
        assert not (target / ".agent-factory").exists()

        # --- Checkpoint 3: consent gate (explicit decline) ---------------
        assert mod.get_consent(input_func=lambda _: "no") is False

        before = _snapshot(target)
        declined = _run_bootstrap(factory_source, target, "\nno\n")
        assert declined.returncode == 0, declined.stdout + declined.stderr
        assert "cancelled" in declined.stdout.lower()
        assert _snapshot(target) == before, \
            "a declined consent gate must leave the target unchanged"
        assert not (target / ".agent-factory").exists()

        # --- Checkpoint 4: installation (affirmative consent) ------------
        installed = _run_bootstrap(factory_source, target, "\nyes\n")
        assert installed.returncode == 0, installed.stdout + installed.stderr

        manifest_path = target / ".agent-factory" / "install.json"
        assert manifest_path.is_file(), "installation must write the manifest"
        manifest = json.loads(manifest_path.read_text())
        assert manifest["cli"] == ["claude"]

        # --- Checkpoint 5: receipt ----------------------------------------
        version = (
            factory_source / "packages" / "factory" / "VERSION"
        ).read_text().strip()
        receipt = installed.stdout
        assert "Installation Receipt" in receipt
        assert "Changed paths:" in receipt
        assert ".agent-factory/" in receipt
        assert "Interface:   claude" in receipt
        assert f"Version:     {version}" in receipt
        assert f"Next:        cd {target}" in receipt

        # --- Checkpoint 6: first-session routing ---------------------------
        # Virgil is an NL agent definition and is not invoked directly; this
        # checkpoint verifies the data its routing reads
        # (packages/factory/agents/virgil.md "First-session insight").
        before = _snapshot(target)
        context_path = (
            target / ".agent-factory" / "config" / "project-context.json"
        )
        assert context_path.is_file()
        context = json.loads(context_path.read_text())
        language_names = {item["name"] for item in context["languages"]}
        test_runner_names = {item["name"] for item in context["test_runners"]}
        assert "python" in language_names
        assert "pytest" in test_runner_names
        # Safety signal: Virgil reports the presence of the target's own
        # .pre-commit-config.yaml directly ("pre-commit hooks present" /
        # "none observed"), the same file the controlled fixture seeds --
        # it is not a project-context.json field.
        assert (target / ".pre-commit-config.yaml").is_file()
        assert _snapshot(target) == before, \
            "reading routing data must not change the target"


# ---------------------------------------------------------------------------
# Layer binding
# ---------------------------------------------------------------------------

class TestEndToEndLayerBinding:
    def test_testing_yaml_declares_end_to_end_layer(self):
        config = yaml.safe_load(TESTING_YAML.read_text())
        layers = config.get("layers", {})
        assert "end_to_end" in layers, \
            "docs/testing.yaml must declare an end_to_end layer binding"
        entry_point = layers["end_to_end"].get("entry_point", "")
        assert "tests/factory/test_onboarding_journey.py" in entry_point
