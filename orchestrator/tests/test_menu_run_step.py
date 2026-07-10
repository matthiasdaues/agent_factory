"""Tests for the `run-step` menu flow: agent -> skill scope -> adapter ->
model (ST-0053).

Traces: UC-11, FR-S4, BR-055, cli_specification.md §Run-step. Covers
`build_run_step_menu`'s four runtime-populated levels (agent listing with
tier, `all skills` default plus declared skills, adapter default `★`, model
default `★` via `ModelResolver.resolve_agent_tier`) and
`build_run_step_dispatch`'s leaf, which must reach the exact same
`_handle_run_step` direct mode uses (FR-V3).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

from orchestrator import cli
from orchestrator.adapters.adapter_registry import TomlAdapterRegistry
from orchestrator.adapters.config_store import TomlConfigStore
from orchestrator.cli import (
    build_run_step_dispatch,
    build_run_step_menu,
)
from orchestrator.entities import Config, MenuNode, MenuNodeType
from orchestrator.menu_controller import DispatchOutcome


def _write_agent(
    agents_dir: Path,
    name: str,
    *,
    tier: str | None = None,
    skills: list[str] | None = None,
) -> None:
    agents_dir.mkdir(parents=True, exist_ok=True)
    skills = skills or []
    lines = ["---"]
    if tier is not None:
        lines.append(f"tier: {tier}")
    lines.append("skills:")
    for skill in skills:
        lines.append(f"  - {skill}")
    lines.append("outputs:")
    lines.append("  - docs/out.md")
    lines.append("---")
    lines.append(f"# {name}\n")
    (agents_dir / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")


def _orch_dir(tmp_path: Path) -> Path:
    return tmp_path / ".orchestrator"


def _registry_with_copilot(tmp_path: Path) -> TomlAdapterRegistry:
    registry = TomlAdapterRegistry(_orch_dir(tmp_path))
    registry.register("copilot", sys.executable)
    return registry


def _find(children: list[MenuNode], node_id: str) -> MenuNode:
    for child in children:
        if child.id == node_id:
            return child
    raise AssertionError(
        f"no child with id {node_id!r} among {[c.id for c in children]}"
    )


# ---------------------------------------------------------------------------
# Level 1: agent listing with tier (cli_specification.md example rendering)
# ---------------------------------------------------------------------------


class TestAgentListing:
    def test_lists_agents_with_declared_tier(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong", skills=["fagan-review"])
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)

        assert root.id == "run-step"
        assert len(root.children) == 1
        agent_node = root.children[0]
        assert agent_node.id == "run-step.qa-agent"
        assert agent_node.label == "qa-agent [strong]"
        assert agent_node.type == MenuNodeType.MENU

    def test_agent_without_declared_tier_shows_standard(self, tmp_path: Path) -> None:
        """VR-041: a null tier resolves as standard — reflected in the label too."""
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "planning-agent", tier=None)
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)

        assert root.children[0].label == "planning-agent [standard]"

    def test_no_agent_is_marked_default(self, tmp_path: Path) -> None:
        """Spec's example rendering carries no ★ at the agent-selection depth —
        the operator must actively choose an agent (the first, non-★, Enter
        press of the "three Enter presses on ★ defaults" happy path)."""
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        _write_agent(agents_dir, "architecture-agent", tier="strong")
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)

        assert all(not child.is_default for child in root.children)

    def test_agents_listed_in_filename_order(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "zzz-agent", tier="standard")
        _write_agent(agents_dir, "aaa-agent", tier="standard")
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)

        assert [c.id for c in root.children] == [
            "run-step.aaa-agent",
            "run-step.zzz-agent",
        ]


# ---------------------------------------------------------------------------
# Level 2: skill scope — "all skills" default plus declared skills (FR-S4)
# ---------------------------------------------------------------------------


class TestSkillScope:
    def test_all_skills_is_first_and_default(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(
            agents_dir,
            "qa-agent",
            tier="strong",
            skills=["fagan-review", "security-review", "bug-hunt"],
        )
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)
        agent_node = root.children[0]

        assert [c.id for c in agent_node.children] == [
            "run-step.qa-agent.all-skills",
            "run-step.qa-agent.fagan-review",
            "run-step.qa-agent.security-review",
            "run-step.qa-agent.bug-hunt",
        ]
        assert agent_node.children[0].label == "all skills"
        assert agent_node.children[0].is_default is True
        assert all(not c.is_default for c in agent_node.children[1:])

    def test_agent_with_no_declared_skills_shows_only_all_skills(
        self, tmp_path: Path
    ) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "coaching-agent", tier="standard", skills=[])
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)
        agent_node = root.children[0]

        assert [c.id for c in agent_node.children] == [
            "run-step.coaching-agent.all-skills"
        ]


# ---------------------------------------------------------------------------
# Level 3: adapter selection — default marked ★
# ---------------------------------------------------------------------------


class TestAdapterSelection:
    def test_configured_default_adapter_is_marked(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        registry = TomlAdapterRegistry(_orch_dir(tmp_path))
        registry.register("copilot", sys.executable)
        registry.register("codex", shutil.which("sh") or "/bin/sh")
        config_store = TomlConfigStore(_orch_dir(tmp_path))
        config_store.save(Config(adapter="codex"))

        root = build_run_step_menu(agents_dir, registry, config_store)
        skill_node = root.children[0].children[0]  # all skills

        codex_node = _find(skill_node.children, "run-step.qa-agent.all-skills.codex")
        copilot_node = _find(
            skill_node.children, "run-step.qa-agent.all-skills.copilot"
        )
        assert codex_node.is_default is True
        assert copilot_node.is_default is False

    def test_builtin_default_adapter_used_when_unconfigured(
        self, tmp_path: Path
    ) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        registry = _registry_with_copilot(tmp_path)
        config_store = TomlConfigStore(_orch_dir(tmp_path))  # no config.toml written

        root = build_run_step_menu(agents_dir, registry, config_store)
        skill_node = root.children[0].children[0]

        copilot_node = _find(
            skill_node.children, "run-step.qa-agent.all-skills.copilot"
        )
        assert (
            copilot_node.is_default is True
        )  # "copilot" is BUILTIN_DEFAULTS["adapter"]


# ---------------------------------------------------------------------------
# Level 4: model selection — tier-resolved default ★ (BR-055)
# ---------------------------------------------------------------------------


class TestModelSelection:
    def test_tier_resolved_default_model_is_marked(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "economy", "gpt-5-mini")
        registry.set_model("copilot", "standard", "gpt-5.4")
        registry.set_model("copilot", "strong", "gpt-5.4-strong")
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)
        adapter_node = _find(
            root.children[0].children[0].children,
            "run-step.qa-agent.all-skills.copilot",
        )

        assert [c.id for c in adapter_node.children] == [
            "run-step.qa-agent.all-skills.copilot.economy",
            "run-step.qa-agent.all-skills.copilot.standard",
            "run-step.qa-agent.all-skills.copilot.strong",
        ]
        strong_node = _find(
            adapter_node.children, "run-step.qa-agent.all-skills.copilot.strong"
        )
        assert strong_node.label == "gpt-5.4-strong [strong]"
        assert strong_node.is_default is True
        assert sum(1 for c in adapter_node.children if c.is_default) == 1

    def test_null_tier_agent_resolves_as_standard(self, tmp_path: Path) -> None:
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "planning-agent", tier=None)
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "standard", "gpt-5.4")
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)
        adapter_node = _find(
            root.children[0].children[0].children,
            "run-step.planning-agent.all-skills.copilot",
        )

        standard_node = _find(
            adapter_node.children, "run-step.planning-agent.all-skills.copilot.standard"
        )
        assert standard_node.is_default is True

    def test_incomplete_dictionary_marks_no_default_without_crashing(
        self, tmp_path: Path
    ) -> None:
        """BR-055/ADR-0016: an unresolvable tier degrades to "no ★", it must
        never raise out of menu-tree construction."""
        agents_dir = tmp_path / "agents"
        _write_agent(agents_dir, "qa-agent", tier="strong")
        registry = _registry_with_copilot(tmp_path)  # empty dictionary
        config_store = TomlConfigStore(_orch_dir(tmp_path))

        root = build_run_step_menu(agents_dir, registry, config_store)
        adapter_node = _find(
            root.children[0].children[0].children,
            "run-step.qa-agent.all-skills.copilot",
        )

        assert adapter_node.children == []


# ---------------------------------------------------------------------------
# Dispatch: the leaf reaches the exact same handler as direct mode (FR-V3)
# ---------------------------------------------------------------------------


class TestRunStepDispatch:
    def _capture(self, monkeypatch):
        calls: dict = {}

        def _fake_build_runtime(args, classification=None):
            calls["build_runtime_args"] = SimpleNamespace(
                adapter=args.adapter,
                model=args.model,
                agent=args.agent,
                skill=args.skill,
                timeout=args.timeout,
                interactive=args.interactive,
                command=args.command,
            )
            # ST-0058: real `_build_runtime` now exposes the *resolved*
            # effective timeout as `runtime.timeout_s` (BR-040/QS-20) —
            # dispatch reads that, not the raw (possibly-`None`)
            # `args.timeout`. Mirror that shape here so this fake stays a
            # faithful stand-in for the real return value.
            return SimpleNamespace(marker="fake-runtime", timeout_s=args.timeout)

        def _fake_handle_run_step(runtime, agent_name, timeout_s, skill=None):
            calls["handle_run_step"] = (runtime, agent_name, timeout_s, skill)
            return 0

        monkeypatch.setattr(cli, "_build_runtime", _fake_build_runtime)
        monkeypatch.setattr(cli, "_handle_run_step", _fake_handle_run_step)
        monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)
        return calls

    def test_specific_skill_leaf_matches_direct_mode_args(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        # copilot/strong -> gpt-5.4-strong, resolved via the registry.
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")
        calls = self._capture(monkeypatch)
        dispatch = build_run_step_dispatch()
        node = MenuNode(
            id="run-step.qa-agent.fagan-review.copilot.strong",
            label="gpt-5.4-strong [strong]",
            type=MenuNodeType.FUNCTION,
        )

        outcome = dispatch(node)

        assert outcome == DispatchOutcome(long_running=True)
        built = calls["build_runtime_args"]
        assert built.adapter == "copilot"
        assert built.agent == "qa-agent"
        assert built.skill == "fagan-review"
        assert built.command == "run-step"

        expected = cli.build_parser().parse_args(
            [
                "--adapter",
                "copilot",
                "--model",
                built.model,
                "run-step",
                "qa-agent",
                "--skill",
                "fagan-review",
            ]
        )
        assert built.model == expected.model
        assert built.timeout == expected.timeout

        runtime, agent_name, timeout_s, skill = calls["handle_run_step"]
        assert runtime.marker == "fake-runtime"
        assert agent_name == "qa-agent"
        assert skill == "fagan-review"

    def test_all_skills_leaf_omits_skill_flag_like_direct_mode(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")
        calls = self._capture(monkeypatch)
        dispatch = build_run_step_dispatch()
        node = MenuNode(
            id="run-step.qa-agent.all-skills.copilot.strong",
            label="gpt-5.4-strong [strong]",
            type=MenuNodeType.FUNCTION,
        )

        outcome = dispatch(node)

        assert outcome.long_running is True
        built = calls["build_runtime_args"]
        assert built.skill is None  # matches direct mode's --skill-omitted default
        _, agent_name, _, skill = calls["handle_run_step"]
        assert agent_name == "qa-agent"
        assert skill is None

    def test_model_id_is_resolved_from_the_registry_by_tier(
        self, monkeypatch, tmp_path
    ) -> None:
        monkeypatch.chdir(tmp_path)
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")
        calls = self._capture(monkeypatch)
        dispatch = build_run_step_dispatch()
        node = MenuNode(
            id="run-step.qa-agent.all-skills.copilot.strong",
            label="gpt-5.4-strong [strong]",
            type=MenuNodeType.FUNCTION,
        )

        dispatch(node)

        assert calls["build_runtime_args"].model == "gpt-5.4-strong"

    def test_dispatch_equivalent_to_direct_mode_invocation(
        self, monkeypatch, tmp_path
    ) -> None:
        """FR-V3: the menu leaf must feed `_build_runtime`/`_handle_run_step`
        the same effective arguments the direct-mode command line would."""
        monkeypatch.chdir(tmp_path)
        registry = _registry_with_copilot(tmp_path)
        registry.set_model("copilot", "strong", "gpt-5.4-strong")

        menu_calls = self._capture(monkeypatch)
        build_run_step_dispatch()(
            MenuNode(
                id="run-step.qa-agent.fagan-review.copilot.strong",
                label="x",
                type=MenuNodeType.FUNCTION,
            )
        )
        from_menu = menu_calls["build_runtime_args"]

        direct_calls = self._capture(monkeypatch)
        args = cli.build_parser().parse_args(
            [
                "--adapter",
                "copilot",
                "--model",
                "gpt-5.4-strong",
                "run-step",
                "qa-agent",
                "--skill",
                "fagan-review",
            ]
        )
        cli._resolve_interactive(args)
        runtime = cli._build_runtime(args, classification=None)
        cli._handle_run_step(runtime, args.agent, args.timeout, args.skill)
        from_direct = direct_calls["build_runtime_args"]

        assert from_menu.adapter == from_direct.adapter
        assert from_menu.model == from_direct.model
        assert from_menu.agent == from_direct.agent
        assert from_menu.skill == from_direct.skill
        assert from_menu.timeout == from_direct.timeout


# ---------------------------------------------------------------------------
# build_root_dispatch wiring
# ---------------------------------------------------------------------------


class TestRootDispatchWiring:
    def test_run_step_prefixed_nodes_route_to_run_step_dispatch(
        self, monkeypatch
    ) -> None:
        seen = []
        monkeypatch.setattr(
            cli, "build_status_dispatch", lambda svc: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli, "build_backlog_dispatch", lambda store: lambda node: DispatchOutcome()
        )
        monkeypatch.setattr(
            cli,
            "build_manage_run_dispatch",
            lambda build_runtime: lambda node: DispatchOutcome(),
        )
        monkeypatch.setattr(
            cli,
            "build_run_step_dispatch",
            lambda: (
                lambda node: seen.append(node) or DispatchOutcome(long_running=True)
            ),
        )
        hook = cli.build_root_dispatch(
            status_service=object(),
            backlog_store=object(),
            build_runtime=lambda: (_ for _ in ()).throw(AssertionError("unused")),
            config_store=object(),
            adapter_registry=object(),
            matrix_path=Path("unused-model-matrix.conf"),
        )
        node = MenuNode(
            id="run-step.qa-agent.all-skills.copilot.strong",
            label="x",
            type=MenuNodeType.FUNCTION,
        )

        outcome = hook(node)

        assert seen == [node]
        assert outcome.long_running is True
