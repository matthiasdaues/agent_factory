"""Acceptance tests for CLI-neutral research dispatch (ST-0063).

These tests observe the public Markdown contracts consumed directly through
Factory's canonical and installed CLI surfaces.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_INIT_SCRIPT = _ROOT / "factory" / "scripts" / "init-factory"
_loader = SourceFileLoader("init_factory_research_portability", str(_INIT_SCRIPT))
_spec = importlib.util.spec_from_loader(_loader.name, _loader)
init_factory = importlib.util.module_from_spec(_spec)
sys.modules[_loader.name] = init_factory
_loader.exec_module(init_factory)

_DISPATCH_CONTRACT = (
    _ROOT / "factory" / "rulebooks" / "conventions" / "dispatch-contract.md"
)
_RESEARCH_TOPIC = _ROOT / "factory" / "playbooks" / "research-topic.md"
_RESEARCH_SURVEY = _ROOT / "factory" / "playbooks" / "research-survey.md"
_ORCHESTRATOR = _ROOT / "factory" / "agents" / "research-orchestrator.md"
_CANONICAL_RESEARCH_ARTIFACTS = (
    _DISPATCH_CONTRACT,
    _RESEARCH_TOPIC,
    _RESEARCH_SURVEY,
    _ORCHESTRATOR,
)


@pytest.fixture
def installed_factory(tmp_path, monkeypatch):
    """Install Factory without exercising unrelated runtime/hook provisioning."""
    monkeypatch.setattr(
        init_factory, "provision_usage_runtime", lambda _target, _report: False
    )
    monkeypatch.setattr(
        init_factory, "pre_commit_install", lambda _target, _report: None
    )

    assert init_factory.main(["--target", str(tmp_path), "--source", str(_ROOT)]) == 0
    return tmp_path


@pytest.mark.parametrize(
    "field",
    ("agent", "tier", "task", "output", "independent_session"),
)
def test_Dispatch_Contract_research_assignment_declares_required_fields(field):
    """A logical research assignment exposes every portable dispatch field."""
    contract = _DISPATCH_CONTRACT.read_text()

    assert f"`{field}`" in contract


def test_Dispatch_Contract_requires_unique_output_paths():
    """Concurrent assignments cannot race on a shared output artifact."""
    contract = _DISPATCH_CONTRACT.read_text().lower()

    assert "unique output path" in contract


def test_CLI_Portability_preflight_blocks_without_required_capabilities():
    """Source access always blocks; falsification also needs independence."""
    contract = _DISPATCH_CONTRACT.read_text().lower()

    assert "source access" in contract
    assert "block" in contract
    assert "falsification" in contract
    assert "independent" in contract


def test_Role_Separation_falsification_playbook_blocks_without_independence():
    """The strict workflow cannot silently weaken role separation."""
    playbook = _RESEARCH_TOPIC.read_text().lower()

    assert "source access" in playbook
    assert "independent agent identities" in playbook
    assert "block" in playbook
    assert "dispatch-contract.md" in playbook


def test_CLI_Portability_survey_source_gathering_falls_back_to_sequential():
    """Survey retains assignments when bounded fan-out is unavailable."""
    playbook = _RESEARCH_SURVEY.read_text().lower()

    assert "source access" in playbook
    assert "sequential" in playbook
    assert "unique output" in playbook
    assert "dispatch-contract.md" in playbook


def test_Dispatch_Contract_orchestrator_owns_portable_preflight_and_dispatch():
    """The role entry point applies the same contract as both playbooks."""
    orchestrator = _ORCHESTRATOR.read_text().lower()

    assert "source access" in orchestrator
    assert "independent agent identities" in orchestrator
    assert "sequential" in orchestrator
    assert "dispatch-contract.md" in orchestrator


@pytest.mark.parametrize("cli_dir", (".claude", ".github", ".pi", ".codex"))
def test_CLI_Portability_installed_surfaces_expose_research_contract(
    installed_factory, cli_dir
):
    """Every supported CLI discovers the canonical portable contract."""
    installed = installed_factory / cli_dir

    assert (installed / "playbooks" / "research-topic.md").exists()
    assert (installed / "playbooks" / "research-survey.md").exists()
    assert (installed / "rulebooks" / "conventions" / "dispatch-contract.md").exists()


def test_CLI_Portability_installed_agent_surfaces_preserve_invocation_guidance(
    installed_factory,
):
    """Installed role adapters retain the logical dispatch responsibility."""
    markdown_agent = "agents/research-orchestrator.md"
    for cli_dir in (".claude", ".github", ".pi"):
        text = (installed_factory / cli_dir / markdown_agent).read_text().lower()
        assert "dispatch logical assignments" in text

    codex_agent = (
        installed_factory / ".codex/agents/research-orchestrator.toml"
    ).read_text()
    assert "Dispatch logical assignments" in codex_agent


def test_CLI_Portability_canonical_artifacts_avoid_vendor_model_names():
    """Factory tiers, not vendor model labels, define research dispatch."""
    text = "\n".join(path.read_text().lower() for path in _CANONICAL_RESEARCH_ARTIFACTS)

    for vendor_model in ("opus", "sonnet", "haiku"):
        assert vendor_model not in text
    assert "agent tool" not in text
