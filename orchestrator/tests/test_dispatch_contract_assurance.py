"""Contract evidence for nested addressing and bounded dispatch (ST-0071)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_DISPATCH_CONTRACT = _ROOT / "factory/rulebooks/conventions/dispatch-contract.md"
_RULES = _ROOT / "factory/rulebooks/rules.md"
_IMPLEMENTATION_AGENT = _ROOT / "factory/agents/implementation-agent.md"
_RECONCILIATION_AGENT = _ROOT / "factory/agents/reconciliation-agent.md"
_DISPATCH_WAVE = _ROOT / "factory/config/extensions/dispatch-wave.ts"
_RUN_AGENT = _ROOT / "factory/config/extensions/run-agent.ts"

_NESTED_DISPATCH_SURFACES = (_DISPATCH_CONTRACT, _RECONCILIATION_AGENT)
_LIVE_BUDGET_IDENTIFIERS = (
    r"\btoken_?budget\b",
    r"\bremaining_?tokens\b",
    r"\bbudget_?remaining\b",
    r"\bmax_?tokens\b",
)


def _text(path: Path) -> str:
    """Read one canonical evidence surface as authored."""
    return path.read_text(encoding="utf-8")


def _plain(path: Path) -> str:
    """Normalize Markdown emphasis for wording-level contract assertions."""
    text = _text(path).lower().replace("`", "").replace("*", "")
    return re.sub(r"[-\s]+", " ", text)


@pytest.mark.parametrize(
    "surface", _NESTED_DISPATCH_SURFACES, ids=lambda path: path.name
)
def test_UC_12_BR_047_nested_dispatch_requires_resolvable_parent_instance(
    surface: Path,
):
    """Every recursive-dispatch surface rejects a role name as a reply address."""
    text = _plain(surface)
    assert "resolvable instance id" in text
    assert re.search(r"never (?:its own |the )?agent type name", text)


def test_UC_12_BR_047_nested_dispatch_has_explicit_local_fallback():
    """An unreachable or declining child cannot strand its parent indefinitely."""
    contract = _plain(_DISPATCH_CONTRACT)
    reconciliation = _plain(_RECONCILIATION_AGENT)

    assert "report your result to instance" in contract
    assert "<parent_instance_id>" in contract
    assert "declines out of scope work or does not respond" in contract
    assert "do the work yourself rather than waiting" in contract
    assert "do not block indefinitely" in contract
    assert "dispatch contract.md#sub agent addressing" in reconciliation
    assert "never block indefinitely" in reconciliation


def test_UC_12_BR_048_whole_codebase_work_is_split_or_checkpointed():
    """Large dispatches have independently verifiable scopes or round checkpoints."""
    contract = _plain(_DISPATCH_CONTRACT)
    rules = _plain(_RULES)
    implementation = _plain(_IMPLEMENTATION_AGENT)

    assert (
        "split a whole codebase task into per module or per directory dispatches"
        in contract
    )
    assert "each independently verifiable and mergeable" in contract
    assert "checkpoint long tasks with commits between rounds" in contract
    assert (
        "split a whole codebase dispatch into smaller, independently mergeable dispatches"
        in rules
    )
    assert "checkpoint a long running dispatch with commits between rounds" in rules
    assert "dispatch contract.md" in implementation
    assert "smaller, independently mergeable dispatches" in implementation
    assert "output file overlap" in implementation


def test_UC_12_BR_048_dispatch_wave_preserves_mechanical_scope_evidence():
    """Pi waves still pass every declared output scope to premerge-check."""
    source = _text(_DISPATCH_WAVE)

    assert 'description: "Output path prefixes for `premerge-check --scope`."' in source
    assert 'for (const s of item.scope ?? []) pmArgs.push("--scope", s);' in source
    assert 'runScript(cwd, "premerge-check", pmArgs)' in source


@pytest.mark.parametrize(
    "runtime", (_DISPATCH_WAVE, _RUN_AGENT), ids=lambda path: path.name
)
def test_UC_12_BR_048_dispatch_runtime_has_no_live_token_budget_control(
    runtime: Path,
):
    """Accepted scope/checkpoint evidence must not grow a live budget runtime."""
    source = _text(runtime)
    for pattern in _LIVE_BUDGET_IDENTIFIERS:
        assert re.search(pattern, source, flags=re.IGNORECASE) is None
